#!/usr/bin/env python3
"""Forensic audit of a completed P2-C1.4 aligned cohort.

This audit is intentionally mechanical. It does not fit models, derive X_W,
or alter records. It verifies cohort identity, uniqueness, protocol fields,
evidence-before-outcome claims, hash integrity, outcome construction
consistency, and absence of forbidden annotator leakage.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

FORBIDDEN_EVIDENCE_KEYS={
    "p0_correct","challenger_correct","replacement_occurred","final_correct",
    "y_h","generated_sql","gold_sql","reference_sql","reference_answer",
    "posthoc_evaluator_labels","intervention","replacement","downstream_outcome"
}

def canon(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def sha(x): return hashlib.sha256(x).hexdigest()

def scan_forbidden(x,path=""):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in FORBIDDEN_EVIDENCE_KEYS:
                raise AssertionError(f"forbidden key {k} at {path or '<root>'}")
            scan_forbidden(v,f"{path}.{k}" if path else k)
    elif isinstance(x,list):
        for i,v in enumerate(x): scan_forbidden(v,f"{path}[{i}]")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cohort",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--pilot-manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    cohort=json.loads(args.cohort.read_text(encoding="utf-8"))
    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    pilot=json.loads(args.pilot_manifest.read_text(encoding="utf-8"))

    assert cohort["protocol_version"]=="P2-C1.4-ALIGNED-V1"
    assert manifest["confirmatory"] is True
    assert manifest["protocol_version"]=="P2-C1.4-CONFIRMATORY-V1-2026-09-21"

    expected={(x["decision_id"],x["db_id"],x["question"]) for x in manifest["cases"]}
    pilot_keys={(x["db_id"],x["question"]) for x in pilot["cases"]}
    records=cohort["records"]
    actual={(r["decision_id"],r["decision_time_evidence"]["database_id"],r["decision_time_evidence"]["question"]) for r in records}

    assert actual==expected, f"manifest/record mismatch: expected {len(expected)}, actual {len(actual)}"
    assert not (actual & {(d,f,q) for d,f,q in []})
    assert len(records)==len(expected)==manifest["case_count"]
    assert len({r["decision_id"] for r in records})==len(records)
    assert all((r["decision_time_evidence"]["database_id"],r["decision_time_evidence"]["question"]) not in pilot_keys for r in records)

    evidence_ok=0
    harm_count=0
    replacement_count=0
    missing_evidence=0
    for r in records:
        e=r["decision_time_evidence"]
        b=r["baseline"]
        o=r["intervention_outcome"]
        assert e["captured_before_intervention"] is True
        assert o["locked_after_evidence"] is True
        assert b["execution_ok"] == (b["row_count"] is not None)
        assert b["row_count"] == e["row_count"]
        assert b["column_count"] == e["column_count"]

        if e["row_count"] is None:
            missing_evidence += 1
            assert e["returned_rows"] is None and e["returned_columns"] is None and e["evidence_hash"] is None
        else:
            payload={
                "question":e["question"],"database_id":e["database_id"],
                "returned_columns":e["returned_columns"],
                "returned_rows":e["returned_rows"],
                "row_count":e["row_count"],
                "column_count":e["column_count"]
            }
            assert e["evidence_hash"]==sha(canon(payload))
            evidence_ok += 1

        assert o["y_h"] == int(o["p0_correct"] and o["replacement_occurred"] and not o["final_correct"])
        replacement_count += int(o["replacement_occurred"])
        harm_count += int(o["y_h"])

        # Evidence subobject must contain no outcome-derived material.
        scan_forbidden(e)

    result={
        "status":"PASS",
        "protocol_version":cohort["protocol_version"],
        "record_count":len(records),
        "manifest_case_count":manifest["case_count"],
        "evidence_ok_count":evidence_ok,
        "no_usable_evidence_count":missing_evidence,
        "replacement_count":replacement_count,
        "harm_count":harm_count,
        "pilot_exclusion_verified":True,
        "same_unit_alignment_verified":True,
        "evidence_hashes_verified":True,
        "outcome_formula_verified":True,
        "forbidden_evidence_leakage_scan":"PASS"
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
