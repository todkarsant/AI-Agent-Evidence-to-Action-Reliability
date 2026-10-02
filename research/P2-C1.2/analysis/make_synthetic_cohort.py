#!/usr/bin/env python3
"""Generate a SYNTHETIC aligned cohort + X_W file + reference-features CSV for TESTS ONLY.

Every output is marked SYNTHETIC (top-level "SYNTHETIC": true, decision_ids prefixed "SYN-",
xw_construction_version "SYNTHETIC-..."). No real data is read or produced.

--signal none : Y_H independent of X_W (null case)
--signal xw   : logit P(Y_H=1) increases strongly with X_W (signal case)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from typing import Optional

import numpy as np

E = "EVALUABLE"
E1 = "EXCLUDED_E1_REFERENCE_NOT_SCOREABLE"
E2 = "NON_EVALUABLE_E2_RUNTIME_FAILURE_PRE_EVIDENCE"
E34 = "NON_EVALUABLE_E3E4_RUNTIME_FAILURE_POST_EVIDENCE"


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def make(n: int = 600, seed: int = 1, signal: str = "none", base_rate: float = 0.08, max_events: Optional[int] = None,
         p_e1: float = 0.02, p_e2: float = 0.03, p_e34: float = 0.06, p_no_evidence: float = 0.06, p_dup_group: float = 0.05):
    rng = np.random.default_rng(seed)
    statuses = rng.choice([E, E1, E2, E34], size=n, p=[1 - p_e1 - p_e2 - p_e34, p_e1, p_e2, p_e34])
    dbs = [f"syn_db_{k:02d}" for k in range(25)]
    records, xw_records, ref_rows = [], [], []
    questions = []
    events = 0
    for i in range(n):
        did = f"SYN-{i:06d}"
        st = str(statuses[i])
        db = dbs[int(rng.integers(len(dbs)))]
        q = "SYNTHETIC question %d about %s %s" % (i, db, "x" * int(rng.integers(0, 60)))
        if questions and rng.random() < p_dup_group:  # repeated benchmark case -> shared group
            db, q = questions[int(rng.integers(len(questions)))]
        questions.append((db, q))
        exec_ok = bool(rng.random() < 0.85)
        rc = int(rng.geometric(0.15)) - 1 if exec_ok else None
        cc = int(rng.integers(1, 6)) if exec_ok else None
        xw = float(rng.integers(0, 8)) / 7.0
        has_ev = st in (E, E34) and rng.random() >= p_no_evidence
        io = {"replacement_occurred": None, "p0_correct": None, "final_correct": None, "y_h": None,
              "y_h_implied_by_definition": None, "locked_after_evidence": True}
        if st == E:
            z = np.log(base_rate / (1 - base_rate)) + 0.3 * (0 if exec_ok else 1)
            if signal == "xw":
                z += 5.0 * (xw - 0.5)
            y = int(rng.random() < _sigmoid(z))
            if max_events is not None and has_ev and y == 1:
                if events >= max_events:
                    y = 0
                else:
                    events += 1
            p0 = bool(y == 1 or rng.random() < 0.5)
            repl = bool(y == 1 or rng.random() < 0.3)
            io.update({"p0_correct": p0, "replacement_occurred": repl, "final_correct": (False if y == 1 else bool(rng.random() < 0.6)), "y_h": y})
        elif st == E34:
            p0 = bool(rng.random() < 0.5)
            io.update({"p0_correct": p0, "y_h_implied_by_definition": (0 if not p0 else None)})
        if st in (E1, E2):
            exec_ok_b, rc_b, cc_b = False, None, None
        else:
            exec_ok_b, rc_b, cc_b = exec_ok, rc, cc
        ev = {"question": q, "database_id": db, "schema": "SYNTHETIC SCHEMA", "returned_columns": None, "returned_rows": None,
              "row_count": rc_b, "column_count": cc_b,
              "evidence_hash": hashlib.sha256(did.encode()).hexdigest() if st in (E, E34) else None,
              "captured_before_intervention": True}
        records.append({"decision_id": did, "protocol_version": "P2-C1.4-ALIGNED-V2", "record_status": st,
                        "baseline": {"execution_ok": exec_ok_b, "row_count": rc_b, "column_count": cc_b},
                        "decision_time_evidence": ev, "intervention_outcome": io,
                        "provenance": {"manifest_hash": "SYNTHETIC", "code_version": "SYNTHETIC", "runtime_manifest_hash": "SYNTHETIC",
                                       "baseline_hash": "SYNTHETIC", "outcome_record_hash": "SYNTHETIC"}})
        xw_records.append({"decision_id": did, "x_w": (xw if has_ev else None)})
        ref_rows.append({"decision_id": did, "hardness": str(rng.choice(["easy", "medium", "hard", "extra"])), "nesting_depth": int(rng.integers(0, 3))})
    cohort = {"SYNTHETIC": True, "protocol_version": "P2-C1.4-ALIGNED-V2", "records": records}
    xwf = {"SYNTHETIC": True, "xw_construction_version": f"SYNTHETIC-signal-{signal}-seed-{seed}", "records": xw_records}
    return cohort, xwf, ref_rows


def write(out_dir: str, cohort: dict, xwf: dict, ref_rows: list) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    paths = {"cohort": os.path.join(out_dir, "SYNTHETIC_cohort.json"), "xw": os.path.join(out_dir, "SYNTHETIC_xw.json"),
             "ref": os.path.join(out_dir, "SYNTHETIC_reference_features.csv")}
    for k in ("cohort", "xw"):
        with open(paths[k], "w", encoding="utf-8") as fh:
            json.dump(cohort if k == "cohort" else xwf, fh, sort_keys=True, indent=1)
    with open(paths["ref"], "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["decision_id", "hardness", "nesting_depth"], lineterminator="\n")
        w.writeheader()
        w.writerows(ref_rows)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--signal", choices=["none", "xw"], default="none")
    ap.add_argument("--max-events", type=int, default=None)
    a = ap.parse_args()
    paths = write(a.out, *make(a.n, a.seed, a.signal, max_events=a.max_events))
    print(json.dumps(paths, indent=1))


if __name__ == "__main__":
    main()
