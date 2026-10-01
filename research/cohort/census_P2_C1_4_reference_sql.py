#!/usr/bin/env python3
"""E1 reference-SQL scoreability census for the P2-C1.4 frozen manifest.

Amendment: P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01 (E1).

Model-independent and outcome-blind. For every frozen decision it checks only
whether the pinned official Spider evaluator could score ANY prediction against
the reference (gold) SQL, using the same two operations that evaluator applies
to the gold query:

  1. evaluation.get_sql(Schema(get_schema(db)), gold_sql)   (parse)
  2. sqlite3 cursor.execute(gold_sql).fetchall()            (execute, raw string)

No model is called, no predicted SQL is read, and no outcome is computed.
A decision failing either check is EXCLUDED_E1_REFERENCE_NOT_SCOREABLE.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sqlite3
import sys
import time
from pathlib import Path

CENSUS_PROTOCOL = "P2-C1.4-E1-REFERENCE-SQL-CENSUS-V1"
AMENDMENT_ID = "P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01"
EXECUTE_TIMEOUT_SECONDS = 120


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def execute_reference(db_path: Path, gold_sql: str) -> str | None:
    """Return None if the raw gold SQL executes, else the error text."""
    conn = sqlite3.connect(str(db_path))
    deadline = time.monotonic() + EXECUTE_TIMEOUT_SECONDS
    conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10000)
    try:
        conn.cursor().execute(gold_sql).fetchall()
        return None
    except Exception as exc:  # the pinned evaluator does not catch this
        return f"{type(exc).__name__}: {exc}"
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--spider-eval-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    sys.path.insert(0, str(args.spider_eval_dir))
    try:
        _load("process_sql", args.spider_eval_dir / "process_sql.py")
        evaluation = _load("official_spider_evaluation_census", args.spider_eval_dir / "evaluation.py")
    finally:
        sys.path.pop(0)

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    gold = {(r["question"], r["db_id"]): r["query"]
            for r in json.loads(args.questions.read_text(encoding="utf-8"))}

    excluded = []
    for c in manifest["cases"]:
        key = (c["question"], c["db_id"])
        if key not in gold:
            raise SystemExit(f"FAIL: no reference SQL for {c['decision_id']}")
        gold_sql = gold[key]
        db_path = args.database_dir / c["db_id"] / f"{c['db_id']}.sqlite"
        if not db_path.exists():
            raise SystemExit(f"FAIL: database missing for {c['decision_id']} ({c['db_id']})")
        reason = None
        try:
            schema = evaluation.Schema(evaluation.get_schema(str(db_path)))
            evaluation.get_sql(schema, gold_sql)
        except Exception as exc:
            reason = ("REFERENCE_SQL_NOT_PARSEABLE", f"{type(exc).__name__}: {exc}")
        if reason is None:
            err = execute_reference(db_path, gold_sql)
            if err is not None:
                reason = ("REFERENCE_SQL_NOT_EXECUTABLE", err)
        if reason is not None:
            excluded.append({
                "decision_id": c["decision_id"],
                "db_id": c["db_id"],
                "reason": reason[0],
                "error": reason[1][:500],
                "reference_sql_sha256": hashlib.sha256(gold_sql.encode("utf-8")).hexdigest(),
            })

    out = {
        "census_protocol": CENSUS_PROTOCOL,
        "amendment_id": AMENDMENT_ID,
        "source_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "checked_count": len(manifest["cases"]),
        "excluded_count": len(excluded),
        "excluded": excluded,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("checked_count", "excluded_count")}))


if __name__ == "__main__":
    main()
