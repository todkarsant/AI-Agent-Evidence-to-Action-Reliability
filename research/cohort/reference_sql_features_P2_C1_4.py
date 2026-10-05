#!/usr/bin/env python3
"""Outcome-blind reference-SQL complexity features for the P2-C1.4 systematic-missingness audit.

Amendments:
  * P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01, section 5 (audit features);
  * P2-C1.4-XW-CONSTRUCTION-AND-ANALYSIS-IMPLEMENTATION-AMENDMENT-2026-10-02, item A7.

Inputs are only the frozen manifest, the Spider question files, the Spider databases (for schemas)
and the pinned official Spider evaluator. The aligned cohort, model output, predicted SQL,
correctness labels and outcomes are never read.

For every frozen decision the reference (gold) SQL is parsed with the pinned evaluator
(evaluation.get_sql(Schema(get_schema(db)), gold_sql)), exactly as the E1 census does. Two features
are then derived:

  hardness       Evaluator().eval_hardness(parsed) -> easy | medium | hard | extra
                 (the official Spider difficulty level).
  nesting_depth  The maximum depth of nested query blocks in the parsed reference SQL; 0 means no
                 nested block. One level is counted for each SQL dict found in:
                   - a condition operand in WHERE, HAVING or FROM ... ON;
                   - a FROM-clause subquery (table_unit of type "sql");
                   - an INTERSECT / UNION / EXCEPT branch.
                 Depth is recursive: a subquery inside a subquery counts 2.

Decisions whose reference SQL cannot be parsed by the pinned evaluator (all of them are E1 by the
census definition) are not written to the CSV. They are listed in the summary JSON, and the audit
reports them as missing features.

Outputs:
  --output   CSV with columns decision_id,hardness,nesting_depth, in frozen manifest order.
  --summary  JSON with input hashes, overall counts by hardness and depth, and unparseable IDs.
             These are overall counts only; they are not broken down by record status or outcome.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

FEATURES_VERSION = "P2-C1.4-REFERENCE-SQL-FEATURES-V1-2026-10-05"
HARDNESS_LEVELS = ("easy", "medium", "hard", "extra")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def child_blocks(sql: dict) -> list[dict]:
    """Directly nested SQL dicts of one parsed query block (see module docstring)."""
    out: list[dict] = []
    conds = sql["from"]["conds"][::2] + sql["where"][::2] + sql["having"][::2]
    for cond_unit in conds:
        for operand in (cond_unit[3], cond_unit[4]):
            if isinstance(operand, dict):
                out.append(operand)
    for table_unit in sql["from"]["table_units"]:
        if table_unit[0] == "sql" and isinstance(table_unit[1], dict):
            out.append(table_unit[1])
    for key in ("intersect", "union", "except"):
        if sql.get(key) is not None:
            out.append(sql[key])
    return out


def nesting_depth(sql: dict) -> int:
    kids = child_blocks(sql)
    return 0 if not kids else 1 + max(nesting_depth(k) for k in kids)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--spider-eval-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    sys.path.insert(0, str(args.spider_eval_dir))
    try:
        _load("process_sql", args.spider_eval_dir / "process_sql.py")
        evaluation = _load("official_spider_evaluation_features", args.spider_eval_dir / "evaluation.py")
    finally:
        sys.path.pop(0)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("case_count") != len(manifest.get("cases", [])):
        raise SystemExit("FAIL: manifest case_count does not match its cases")
    gold = {(r["question"], r["db_id"]): r["query"] for r in json.loads(args.questions.read_text(encoding="utf-8"))}

    evaluator = evaluation.Evaluator()
    schemas: dict[str, object] = {}
    rows, unparseable = [], []
    for c in manifest["cases"]:
        key = (c["question"], c["db_id"])
        if key not in gold:
            raise SystemExit(f"FAIL: no reference SQL for {c['decision_id']}")
        db_path = args.database_dir / c["db_id"] / f"{c['db_id']}.sqlite"
        if not db_path.exists():
            raise SystemExit(f"FAIL: database missing for {c['decision_id']} ({c['db_id']})")
        try:
            if c["db_id"] not in schemas:
                schemas[c["db_id"]] = evaluation.Schema(evaluation.get_schema(str(db_path)))
            parsed = evaluation.get_sql(schemas[c["db_id"]], gold[key])
            hard = evaluator.eval_hardness(parsed)
            depth = nesting_depth(parsed)
        except Exception as exc:  # parse failure: E1 by the census definition
            unparseable.append({"decision_id": c["decision_id"], "error": f"{type(exc).__name__}: {exc}"[:300]})
            continue
        if hard not in HARDNESS_LEVELS:
            raise SystemExit(f"FAIL: unexpected hardness {hard!r} for {c['decision_id']}")
        rows.append((c["decision_id"], hard, depth))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["decision_id", "hardness", "nesting_depth"])
        w.writerows(rows)
    summary = {
        "features_version": FEATURES_VERSION,
        "manifest_sha256": sha(args.manifest),
        "questions_sha256": sha(args.questions),
        "evaluator_sha256": {"evaluation.py": sha(args.spider_eval_dir / "evaluation.py"),
                             "process_sql.py": sha(args.spider_eval_dir / "process_sql.py")},
        "manifest_case_count": manifest["case_count"],
        "features_written": len(rows),
        "unparseable_count": len(unparseable),
        "unparseable": unparseable,
        "hardness_counts_overall": dict(sorted(Counter(r[1] for r in rows).items())),
        "nesting_depth_counts_overall": {str(k): v for k, v in sorted(Counter(r[2] for r in rows).items())},
        "csv_sha256": sha(args.output),
        "outcomes_accessed": False,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("manifest_case_count", "features_written", "unparseable_count",
                                              "hardness_counts_overall", "nesting_depth_counts_overall")}))


if __name__ == "__main__":
    main()
