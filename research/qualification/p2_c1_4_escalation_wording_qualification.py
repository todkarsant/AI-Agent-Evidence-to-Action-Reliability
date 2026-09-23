#!/usr/bin/env python3
"""Non-confirmatory P2-C1.4 qualification of Runtime3 escalation wording.

This experiment exercises the actual pinned Project1 P6-IP path. It does not
modify Project1, the frozen confirmatory collector, or the confirmatory
protocol. The only experimental manipulation is replacement of the exact
post-evidence escalation sentence at the Runtime3 provider boundary.

Conditions:
  baseline: Project1's frozen escalation sentence unchanged
  candidate: same prompt with only the escalation sentence replaced by a
             schema/question-oriented sentence

Each case/condition gets a fresh Runtime3 provider and BenchmarkEnvironment.
The provider's _chat method is wrapped only to record the exact prompt and,
for the candidate condition, replace the exact sentence before the inherited
OllamaProvider.generate_sql() call. Thus prompt construction remains the
pinned Project1 implementation.

The pilot manifest is an input; no cases are selected based on model output.
The script records completion/limit/runtime behavior and prompt hashes.
It is NOT confirmatory evidence and must not be merged into the frozen
confirmatory acquisition path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

CURRENT_SENTENCE = (
    "This is a post-evidence escalation. Re-check joins, filters, grouping, "
    "ordering and nested-query semantics before answering."
)
CANDIDATE_SENTENCE = (
    "This is a post-evidence escalation. Re-check the SQL against the schema "
    "and question before answering."
)
CONDITIONS = ("baseline", "candidate")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cases(manifest_path: Path, limit: int | None) -> list[dict[str, Any]]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit("FAIL: pilot manifest has no cases[]")
    required = ("decision_id", "db_id", "question")
    for i, case in enumerate(cases):
        missing = [k for k in required if k not in case]
        if missing:
            raise SystemExit(f"FAIL: pilot case {i} missing keys: {missing}")
    selected = cases[:limit] if limit is not None else cases
    if not selected:
        raise SystemExit("FAIL: empty selected pilot cohort")
    ids = [c["decision_id"] for c in selected]
    if len(ids) != len(set(ids)):
        raise SystemExit("FAIL: duplicate decision_id in selected pilot cohort")
    return selected


def build_provider(Runtime3OllamaProvider):
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    return Runtime3OllamaProvider(base_url, model)


def run_condition(
    *,
    condition: str,
    cases: list[dict[str, Any]],
    questions: Path,
    database_dir: Path,
    project1_root: Path,
) -> list[dict[str, Any]]:
    sys.path.insert(0, str(project1_root))
    from research.p6_ip_runner import run_case
    from research.spider_benchmark import (
        BenchmarkEnvironment,
        SecondaryExecutionEvaluator,
        SpiderDataset,
    )
    from research.deterministic_solver import RuleBasedDeterministicSolver
    from runtime3_ollama import Runtime3OllamaProvider

    dataset = SpiderDataset(questions, database_dir)
    lookup = {(x.db_id, x.question): x for x in dataset.examples}
    results: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        key = (case["db_id"], case["question"])
        example = lookup.get(key)
        if example is None:
            raise SystemExit(
                f"FAIL: pilot case not found in questions: {case['decision_id']} "
                f"{case['db_id']}"
            )

        provider = build_provider(Runtime3OllamaProvider)
        original_chat = provider._chat
        prompt_records: list[dict[str, Any]] = []

        def wrapped_chat(prompt: str, _original=original_chat):
            actual_prompt = prompt
            replacement_applied = False
            if condition == "candidate":
                occurrences = actual_prompt.count(CURRENT_SENTENCE)
                if occurrences != 1:
                    raise RuntimeError(
                        "candidate condition refused prompt because the exact "
                        f"frozen sentence occurred {occurrences} times"
                    )
                actual_prompt = actual_prompt.replace(
                    CURRENT_SENTENCE, CANDIDATE_SENTENCE
                )
                replacement_applied = True

            record = {
                "call_index": len(prompt_records) + 1,
                "original_prompt_chars": len(prompt),
                "original_prompt_sha256": sha256_text(prompt),
                "actual_prompt_chars": len(actual_prompt),
                "actual_prompt_sha256": sha256_text(actual_prompt),
                "replacement_applied": replacement_applied,
                "current_sentence_occurrences": prompt.count(CURRENT_SENTENCE),
            }
            prompt_records.append(record)
            return _original(actual_prompt)

        provider._chat = wrapped_chat

        evaluator = SecondaryExecutionEvaluator(dataset)
        env = BenchmarkEnvironment(
            dataset,
            evaluator,
            provider,
            RuleBasedDeterministicSolver(database_dir),
        )

        started = time.perf_counter()
        error: str | None = None
        trace = None
        defensibility: dict[str, Any] | None = None
        try:
            trace, defensibility = run_case(env, example)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        elapsed_ms = (time.perf_counter() - started) * 1000

        trace_dict = asdict(trace) if trace is not None else None
        result = {
            "decision_id": case["decision_id"],
            "db_id": case["db_id"],
            "question": case["question"],
            "condition": condition,
            "case_index": index,
            "elapsed_ms": elapsed_ms,
            "trace": trace_dict,
            "defensibility": defensibility,
            "prompt_records": prompt_records,
            "exception": error,
        }
        results.append(result)

        status = (
            "EXCEPTION"
            if error
            else (
                "OUTPUT_LIMIT"
                if trace_dict and "output-token limit" in str(trace_dict.get("error"))
                else "COMPLETED"
            )
        )
        print(
            json.dumps(
                {
                    "condition": condition,
                    "case": f"{index}/{len(cases)}",
                    "decision_id": case["decision_id"],
                    "status": status,
                    "llm_calls": trace_dict.get("llm_calls") if trace_dict else None,
                    "output_tokens": trace_dict.get("output_tokens") if trace_dict else None,
                    "latency_ms": round(elapsed_ms, 1),
                },
                separators=(",", ":"),
            ),
            flush=True,
        )

    return results


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    exceptions = sum(bool(r["exception"]) for r in rows)
    traces = [r["trace"] for r in rows if r["trace"] is not None]
    output_limit = sum(
        "output-token limit" in str(t.get("error"))
        for t in traces
    )
    escalated = sum(bool(t.get("evidence_escalated")) for t in traces)
    return {
        "n_cases": total,
        "exceptions": exceptions,
        "runtime_output_limit_failures": output_limit,
        "cases_with_p6_escalation": escalated,
        "completed_without_exception": total - exceptions,
        "mean_llm_calls": (
            sum(int(t.get("llm_calls", 0)) for t in traces) / len(traces)
            if traces else None
        ),
        "total_prompt_calls": sum(len(r["prompt_records"]) for r in rows),
        "candidate_replacements_applied": sum(
            sum(bool(p["replacement_applied"]) for p in r["prompt_records"])
            for r in rows
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--pilot-manifest", type=Path, required=True)
    ap.add_argument("--project1-root", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    if args.limit != 12:
        raise SystemExit(
            "REFUSED: this qualification harness is frozen to the 12-case pilot; "
            "use --limit 12"
        )

    if os.getenv("LLM_PROVIDER", "").lower() != "ollama":
        raise SystemExit("REFUSED: qualification requires LLM_PROVIDER=ollama")

    cases = load_cases(args.pilot_manifest, args.limit)
    results: dict[str, list[dict[str, Any]]] = {}
    for condition in CONDITIONS:
        results[condition] = run_condition(
            condition=condition,
            cases=cases,
            questions=args.questions,
            database_dir=args.database_dir,
            project1_root=args.project1_root,
        )

    output = {
        "experiment": "P2-C1.4-RUNTIME3-ESCALATION-WORDING-QUALIFICATION",
        "status": "NON_CONFIRMATORY_QUALIFICATION",
        "pilot_case_count": len(cases),
        "conditions": {
            "baseline": {
                "sentence": CURRENT_SENTENCE,
                "manipulation": "none",
            },
            "candidate": {
                "sentence": CANDIDATE_SENTENCE,
                "manipulation": "exact single-sentence replacement at provider boundary",
            },
        },
        "scientific_controls": {
            "project1_path": str(args.project1_root.resolve()),
            "questions_sha256": sha256_text(
                args.questions.read_text(encoding="utf-8")
            ),
            "pilot_manifest_sha256": sha256_text(
                args.pilot_manifest.read_text(encoding="utf-8")
            ),
            "ollama_base_url": os.getenv("OLLAMA_BASE_URL"),
            "ollama_model": os.getenv("OLLAMA_MODEL"),
            "runtime3_max_output_tokens": os.getenv(
                "RUNTIME3_OLLAMA_MAX_OUTPUT_TOKENS"
            ),
            "runtime3_max_attempts": os.getenv("RUNTIME3_OLLAMA_MAX_ATTEMPTS"),
        },
        "results": results,
        "summary": {
            condition: summarize(results[condition])
            for condition in CONDITIONS
        },
        "interpretation_rule": (
            "Descriptive qualification only. This artifact does not select a "
            "confirmatory protocol, alter frozen P2-C1.4 data, or establish a "
            "scientific claim."
        ),
    }

    args.outdir.mkdir(parents=True, exist_ok=True)
    out = args.outdir / "p2_c1_4_escalation_wording_qualification.json"
    out.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output["summary"], indent=2))


if __name__ == "__main__":
    main()
