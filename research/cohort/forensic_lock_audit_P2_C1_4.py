#!/usr/bin/env python3
"""Forensic lock auditor for the P2-C1.4 aligned confirmatory cohort.

This is a mechanical integrity audit. It does not fit models, adjudicate X_W,
or make scientific judgments beyond explicit protocol invariants.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

FORBIDDEN_EVIDENCE = {
    "p0_correct","challenger_correct","replacement_occurred","final_correct",
    "y_h","generated_sql","gold_sql","reference_sql","reference_answer",
    "posthoc_evaluator_labels","intervention","replacement","downstream_outcome",
}

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_json(x) -> str:
    return sha256_bytes(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode())

def fail(msg: str) -> None:
    raise SystemExit("FAIL: " + msg)

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--cohort",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    args=ap.parse_args()

    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    cohort=json.loads(args.cohort.read_text(encoding="utf-8"))
    manifest_hash=sha256_bytes(args.manifest.read_bytes())
    cohort_hash=sha256_bytes(args.cohort.read_bytes())

    if manifest.get("confirmatory") is not True:
        fail("source manifest is not confirmatory")
    expected_ids=[c["decision_id"] for c in manifest["cases"]]
    records=cohort.get("records")
    if cohort.get("protocol_version")!="P2-C1.4-ALIGNED-V2":
        fail("wrong aligned cohort protocol version")
    if not isinstance(records,list) or len(records)!=len(expected_ids):
        fail("cohort record count does not match source manifest")
    ids=[r.get("decision_id") for r in records]
    if ids!=expected_ids:
        fail("decision_id order does not exactly match frozen source manifest")
    if len(ids)!=len(set(ids)):
        fail("duplicate decision_id")

    no_evidence=0
    harms=0
    replacements=0
    p0_correct=0
    final_correct=0

    for r in records:
        did=r["decision_id"]
        if r["protocol_version"]!="P2-C1.4-ALIGNED-V2":
            fail(f"{did}: protocol mismatch")
        e=r["decision_time_evidence"]
        b=r["baseline"]
        o=r["intervention_outcome"]
        p=r["provenance"]
        if p["manifest_hash"]!=manifest_hash:
            fail(f"{did}: manifest hash mismatch")
        if not e["captured_before_intervention"]:
            fail(f"{did}: evidence not pre-intervention")
        if not isinstance(e.get("schema"),str) or not e["schema"]:
            fail(f"{did}: missing decision-time schema")
        if b["execution_ok"] != (e["row_count"] is not None):
            fail(f"{did}: baseline execution_ok mismatch")
        for k in FORBIDDEN_EVIDENCE:
            if k in e:
                fail(f"{did}: forbidden evidence key {k}")
        if e["row_count"] is None:
            no_evidence+=1
            if any(e.get(k) is not None for k in ("returned_columns","returned_rows","column_count","evidence_hash")):
                fail(f"{did}: NO_USABLE_EVIDENCE contains non-null result evidence")
        else:
            if e["row_count"] != len(e["returned_rows"]):
                fail(f"{did}: row_count mismatch")
            if e["column_count"] != len(e["returned_columns"]):
                fail(f"{did}: column_count mismatch")
            expected_evidence_hash=sha256_json({
                "question":e["question"],
                "database_id":e["database_id"],
                "schema":e["schema"],
                "returned_columns":e["returned_columns"],
                "returned_rows":e["returned_rows"],
                "row_count":e["row_count"],
                "column_count":e["column_count"],
            })
            if e["evidence_hash"]!=expected_evidence_hash:
                fail(f"{did}: evidence hash mismatch")
        expected_yh=int(o["p0_correct"] and o["replacement_occurred"] and not o["final_correct"])
        if o["y_h"]!=expected_yh:
            fail(f"{did}: Y_H formula mismatch")
        if not o["locked_after_evidence"]:
            fail(f"{did}: outcome was not marked post-evidence lock")
        harms+=o["y_h"]
        replacements+=int(o["replacement_occurred"])
        p0_correct+=int(o["p0_correct"])
        final_correct+=int(o["final_correct"])

    args.outdir.mkdir(parents=True,exist_ok=True)
    lock={
        "lock_protocol":"P2-C1.4-CONFIRMATORY-COHORT-LOCK-V1",
        "status":"PASS_IMMUTABLE_COHORT_LOCK",
        "source_manifest_sha256":manifest_hash,
        "consolidated_cohort_sha256":cohort_hash,
        "record_count":len(records),
        "no_usable_evidence_count":no_evidence,
        "replacement_count":replacements,
        "p0_correct_count":p0_correct,
        "final_correct_count":final_correct,
        "harm_count":harms,
        "aligned_record_protocol":"P2-C1.4-ALIGNED-V2",
        "runtime_protocol":"P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21",
        "annotation_status":"NOT_ANNOTATED",
    }
    p=args.outdir/"P2_C1_4_CONFIRMATORY_COHORT_LOCK.json"
    p.write_text(json.dumps(lock,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    digest=sha256_bytes(p.read_bytes())
    (args.outdir/"SHA256SUM.txt").write_text(digest+"  "+p.name+"\n",encoding="utf-8")
    print(json.dumps(lock,indent=2))
    print({"lock_sha256":digest})

if __name__=="__main__":
    main()
