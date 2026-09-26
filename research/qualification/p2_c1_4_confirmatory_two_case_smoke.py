#!/usr/bin/env python3
"""Two-case Runtime3 smoke for the explicit P2-C1.4 wording amendment.

This is qualification only. It runs the actual Project1 P6-IP path for the two
frozen diagnostic cases and writes no cohort artifacts.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


CASES = ("P2C14-CONF-000001", "P2C14-CONF-000046")
PROTOCOL = "P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--project1-root", type=Path, required=True)
    args = ap.parse_args()

    if os.getenv("LLM_PROVIDER", "").lower() != "ollama":
        raise SystemExit("REFUSED: LLM_PROVIDER must be ollama")
    if os.getenv("OLLAMA_MODEL") != "llama3.2:1b":
        raise SystemExit("REFUSED: OLLAMA_MODEL must be llama3.2:1b")
    if os.getenv("P2_C1_4_PROTOCOL_FROZEN") != PROTOCOL:
        raise SystemExit("REFUSED: frozen protocol authorization mismatch")

    sys.path.insert(0, str(args.project1_root.resolve()))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from research.p6_ip_runner import run_case
    from research.spider_benchmark import (
        BenchmarkEnvironment,
        SecondaryExecutionEvaluator,
        SpiderDataset,
    )
    from research.deterministic_solver import RuleBasedDeterministicSolver
    from research.runtime3_confirmatory_prompt_amendment import (
        AMENDMENT_ID,
        ConfirmatoryRuntime3OllamaProvider,
    )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    by_id = {c["decision_id"]: c for c in manifest["cases"]}
    missing = [x for x in CASES if x not in by_id]
    if missing:
        raise SystemExit(f"FAIL: frozen cases missing from manifest: {missing}")

    dataset = SpiderDataset(args.questions, args.database_dir)
    lookup = {(x.db_id, x.question): x for x in dataset.examples}

    print("=" * 72)
    print("P2-C1.4 AMENDED RUNTIME3 TWO-CASE QUALIFICATION SMOKE")
    print("=" * 72)
    print("Protocol:", PROTOCOL)
    print("Amendment:", AMENDMENT_ID)
    print("Model:", os.getenv("OLLAMA_MODEL"))
    print("Cases:", ", ".join(CASES))
    print("NO cohort artifacts will be written.")
    print()

    failures = []

    for decision_id in CASES:
        case = by_id[decision_id]
        example = lookup.get((case["db_id"], case["question"]))
        if example is None:
            raise SystemExit(f"FAIL: case not found in questions: {decision_id}")

        provider = ConfirmatoryRuntime3OllamaProvider(
            os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
        )
        evaluator = SecondaryExecutionEvaluator(dataset)
        env = BenchmarkEnvironment(
            dataset,
            evaluator,
            provider,
            RuleBasedDeterministicSolver(args.database_dir),
        )

        started = time.monotonic()
        print("-" * 72)
        print(decision_id)
        print("db_id:", case["db_id"])
        print("question:", case["question"])

        try:
            selected, defensibility = run_case(env, example)
            elapsed = time.monotonic() - started
            print("run_case: PASS")
            print("selected policy:", getattr(selected, "policy", "<unknown>"))
            print("elapsed_seconds:", round(elapsed, 3))
            print("defensibility:", json.dumps(defensibility, sort_keys=True))
        except Exception as exc:
            elapsed = time.monotonic() - started
            failures.append(decision_id)
            print("run_case: FAIL")
            print(type(exc).__name__ + ":", str(exc))
            print("elapsed_seconds:", round(elapsed, 3))

    print()
    print("=" * 72)
    if failures:
        print("QUALIFICATION STATUS: FAIL")
        print("Failed cases:", ", ".join(failures))
        print("Confirmatory acquisition remains blocked.")
        return 2

    print("QUALIFICATION STATUS: PASS")
    print("Both amended frozen-path cases completed.")
    print("This is qualification only; it is not confirmatory acquisition.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
