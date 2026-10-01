#!/usr/bin/env python3
"""Runtime-failure gate for P2-C1.4 (amended G3 / G4 lock condition).

Amendment: P2-C1.4-QUALIFICATION-GATE-G3-AMENDMENT-2026-10-01.

Outcome-blind. Reads only record_status, decision_id order and the E1 census.
It never reads outcome fields. Fails closed (exit 1) when:

  * the record count or decision_id order differs from what is expected;
  * any record carries an unknown or missing record_status;
  * E1 status disagrees with the pre-acquisition census;
  * runtime failures (E2 + E3/E4) exceed floor(MAX_FRACTION * record_count).

The ceiling is fixed at 5% of all frozen records in the checked set
(10 of 200 for qualification; 431 of 8,638 for the confirmatory cohort).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

AMENDMENT_ID = "P2-C1.4-QUALIFICATION-GATE-G3-AMENDMENT-2026-10-01"
MAX_FRACTION = 0.05
STATUSES = {
    "EVALUABLE",
    "EXCLUDED_E1_REFERENCE_NOT_SCOREABLE",
    "NON_EVALUABLE_E2_RUNTIME_FAILURE_PRE_EVIDENCE",
    "NON_EVALUABLE_E3E4_RUNTIME_FAILURE_POST_EVIDENCE",
}
RUNTIME_FAILURE = {
    "NON_EVALUABLE_E2_RUNTIME_FAILURE_PRE_EVIDENCE",
    "NON_EVALUABLE_E3E4_RUNTIME_FAILURE_POST_EVIDENCE",
}
E1 = "EXCLUDED_E1_REFERENCE_NOT_SCOREABLE"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", type=Path, required=True)
    ap.add_argument("--expected-ids", type=Path, required=True,
                    help="manifest JSON whose cases[].decision_id give the expected order")
    ap.add_argument("--e1-census", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    records = json.loads(args.records.read_text(encoding="utf-8"))["records"]
    expected = [c["decision_id"] for c in json.loads(args.expected_ids.read_text(encoding="utf-8"))["cases"]]
    census = json.loads(args.e1_census.read_text(encoding="utf-8"))
    e1_ids = {x["decision_id"] for x in census["excluded"]}

    problems = []
    ids = [r["decision_id"] for r in records]
    if ids != expected:
        problems.append(f"decision_id set/order mismatch ({len(ids)} records, {len(expected)} expected)")
    counts = {}
    failed = []
    for r in records:
        st = r.get("record_status")
        if st not in STATUSES:
            problems.append(f"{r['decision_id']}: missing or unknown record_status {st!r}")
            continue
        counts[st] = counts.get(st, 0) + 1
        if (st == E1) != (r["decision_id"] in e1_ids):
            problems.append(f"{r['decision_id']}: E1 status disagrees with census")
        if st in RUNTIME_FAILURE:
            failed.append(r["decision_id"])

    ceiling = math.floor(MAX_FRACTION * len(expected))
    if len(failed) > ceiling:
        problems.append(f"runtime failures {len(failed)} exceed ceiling {ceiling} "
                        f"({MAX_FRACTION:.0%} of {len(expected)})")

    verdict = {
        "gate": args.label,
        "amendment_id": AMENDMENT_ID,
        "record_count": len(records),
        "expected_count": len(expected),
        "record_status_counts": counts,
        "runtime_failure_count": len(failed),
        "runtime_failure_ceiling": ceiling,
        "runtime_failure_decision_ids": failed,
        "status": "PASS" if not problems else "FAIL",
        "problems": problems[:50],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: verdict[k] for k in ("gate", "status", "record_status_counts",
                                              "runtime_failure_count", "runtime_failure_ceiling", "problems")}))
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
