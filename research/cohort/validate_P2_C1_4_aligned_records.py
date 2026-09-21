#!/usr/bin/env python3
"""Mechanical validator for P2-C1.4 aligned outcome-bearing records.

Scientific policy is intentionally not inferred here. This script checks only
structural/linkage/leakage invariants that can be verified mechanically.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

FORBIDDEN_ANNOTATOR_KEYS = {
    "p0_correct", "challenger_correct", "replacement_occurred",
    "final_correct", "y_h", "generated_sql", "reference_sql",
    "reference_answer", "posthoc_evaluator_labels",
}

def sha256_json(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def fail(msg):
    raise SystemExit("FAIL: " + msg)

def validate_record(r, seen):
    required = {"decision_id","protocol_version","baseline","decision_time_evidence",
                "intervention_outcome","provenance"}
    missing = required - r.keys()
    if missing:
        fail(f"{r.get('decision_id','<unknown>')}: missing {sorted(missing)}")
    did = r["decision_id"]
    if did in seen:
        fail(f"duplicate decision_id: {did}")
    seen.add(did)
    if r["protocol_version"] != "P2-C1.4-ALIGNED-V1":
        fail(f"{did}: wrong protocol_version")

    b = r["baseline"]
    if set(b) != {"execution_ok","row_count","column_count"}:
        fail(f"{did}: baseline schema mismatch")
    e = r["decision_time_evidence"]
    for k in ("question","database_id","returned_columns","returned_rows","row_count","column_count","evidence_hash","captured_before_intervention"):
        if k not in e:
            fail(f"{did}: missing evidence field {k}")
    if e["captured_before_intervention"] is not True:
        fail(f"{did}: evidence was not marked pre-intervention")
    if e["row_count"] is None or e["column_count"] is None:
        if e["row_count"] is not None or e["column_count"] is not None:
            fail(f"{did}: partially missing evidence counts")
        if e["returned_rows"] is not None or e["returned_columns"] is not None:
            fail(f"{did}: NO_USABLE_EVIDENCE must preserve null rows/columns")
        if e["evidence_hash"] is not None:
            fail(f"{did}: NO_USABLE_EVIDENCE must have null evidence_hash")
    else:
        if e["row_count"] != len(e["returned_rows"]):
            fail(f"{did}: evidence row_count mismatch")
        if e["column_count"] != len(e["returned_columns"]):
            fail(f"{did}: evidence column_count mismatch")
        expected_hash=sha256_json({
            "question": e["question"],
            "database_id": e["database_id"],
            "returned_columns": e["returned_columns"],
            "returned_rows": e["returned_rows"],
            "row_count": e["row_count"],
            "column_count": e["column_count"],
        })
        if e["evidence_hash"] != expected_hash:
            fail(f"{did}: evidence_hash mismatch")

    o = r["intervention_outcome"]
    for k in ("replacement_occurred","p0_correct","final_correct","y_h","locked_after_evidence"):
        if k not in o:
            fail(f"{did}: missing outcome field {k}")
    expected_yh = int(o["p0_correct"] and o["replacement_occurred"] and not o["final_correct"])
    if o["y_h"] != expected_yh:
        fail(f"{did}: y_h formula mismatch")
    if o["locked_after_evidence"] is not True:
        fail(f"{did}: outcome not marked post-evidence lock")

def validate_annotation_packet(packet):
    def walk(x, path=""):
        if isinstance(x, dict):
            for k,v in x.items():
                if k in FORBIDDEN_ANNOTATOR_KEYS:
                    fail(f"annotation packet forbidden key {k} at {path or '<root>'}")
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(x, list):
            for i,v in enumerate(x):
                walk(v, f"{path}[{i}]")
    walk(packet)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("records", type=Path)
    ap.add_argument("--annotation-packet", type=Path)
    args=ap.parse_args()
    data=json.loads(args.records.read_text(encoding="utf-8"))
    records=data if isinstance(data,list) else data.get("records")
    if not isinstance(records,list) or not records:
        fail("records must be a non-empty JSON list or {'records':[...]}")
    seen=set()
    for r in records:
        validate_record(r, seen)
    if args.annotation_packet:
        validate_annotation_packet(json.loads(args.annotation_packet.read_text(encoding="utf-8")))
    print(f"PASS: {len(records)} aligned records; unique decision_id; evidence/outcome linkage and Y_H formula valid.")

if __name__ == "__main__":
    main()
