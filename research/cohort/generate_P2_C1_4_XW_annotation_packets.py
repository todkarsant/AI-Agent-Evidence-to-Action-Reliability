#!/usr/bin/env python3
"""Generate blinded P2-C1.4 X_W annotation packets from a forensic-locked cohort.

This script performs no annotation and no outcome access. It exposes only the
decision-time evidence permitted by the frozen W1-W7 codebook, then creates two
independently randomized packets for outcome-blinded human raters.
"""
from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path

SEEDS={"A":424241,"B":424242}
VERSION="P2-C1.4_XW_ANNOTATION_PACKET_V1_2026-09-21"
FORBIDDEN_KEYS={
    "p0_correct","challenger_correct","replacement_occurred","final_correct",
    "y_h","generated_sql","gold_sql","reference_sql","reference_answer",
    "posthoc_evaluator_labels","intervention","replacement","downstream_outcome",
    "outcome","outcomes","official_spider_execution","model","runtime",
    "latency_ms","llm_calls","cost","evidence_hash","source_artifact_sha256",
    "manifest_hash","runtime_manifest_hash","code_version"
}

def sha256_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(p:Path)->str:
    return sha256_bytes(p.read_bytes())

def collect_keys(x):
    out=set()
    if isinstance(x,dict):
        for k,v in x.items():
            out.add(k); out |= collect_keys(v)
    elif isinstance(x,list):
        for v in x: out |= collect_keys(v)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cohort",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--expected-count",type=int,default=8638)
    args=ap.parse_args()

    cohort=json.loads(args.cohort.read_text(encoding="utf-8"))
    records=cohort.get("records")
    if cohort.get("protocol_version")!="P2-C1.4-ALIGNED-V2":
        raise SystemExit("REFUSED: wrong aligned cohort protocol")
    if not isinstance(records,list) or len(records)!=args.expected_count:
        raise SystemExit(f"REFUSED: expected {args.expected_count} locked records, found {len(records) if isinstance(records,list) else 'non-list'}")

    ids=[r.get("decision_id") for r in records]
    if len(ids)!=len(set(ids)):
        raise SystemExit("REFUSED: duplicate decision_id")
    base=[]
    for r in records:
        e=r["decision_time_evidence"]
        # Only decision-time evidence permitted to W1-W7 raters.
        item={
            "case_id":r["decision_id"],
            "database_id":e["database_id"],
            "question":e["question"],
            "schema":e["schema"],
            "execution_status":"SUCCESS" if e["row_count"] is not None else "NO_USABLE_EVIDENCE",
            "returned_columns":e["returned_columns"] if e["row_count"] is not None else [],
            "returned_rows":e["returned_rows"] if e["row_count"] is not None else [],
            "row_count":e["row_count"],
            "column_count":e["column_count"],
            "annotations":{
                "W1":None,"W2":None,"W3":None,"W4":None,
                "W5":None,"W6":None,"W7":None,"notes":None
            }
        }
        forbidden=collect_keys(item) & FORBIDDEN_KEYS
        if forbidden: raise SystemExit(f"REFUSED: forbidden annotation fields {sorted(forbidden)}")
        raw=json.dumps(item,ensure_ascii=False,sort_keys=True)
        if any(marker in raw.upper() for marker in SQL_MARKERS):
            # Natural-language questions may legitimately contain SQL-like text;
            # this is a conservative packet audit, not a content transformation.
            raise SystemExit(f"REFUSED: SQL marker detected in annotation packet source for {r['decision_id']}")
        base.append(item)

    args.out.mkdir(parents=True,exist_ok=True)
    source_hash=sha256_file(args.cohort)
    packet_hashes={}
    for label,seed in SEEDS.items():
        arr=json.loads(json.dumps(base))
        random.Random(seed).shuffle(arr)
        packet={
            "packet_version":VERSION,
            "rater_packet":label,
            "randomization_seed":seed,
            "source_record_count":len(arr),
            "blinding":{
                "excluded_information":[
                    "generated SQL/reference SQL/reference answer",
                    "correctness labels",
                    "replacement/intervention/outcome labels",
                    "post-hoc evaluator labels",
                    "runtime/model telemetry",
                    "evidence/provenance hashes"
                ]
            },
            "cases":arr
        }
        forbidden=collect_keys(packet) & FORBIDDEN_KEYS
        if forbidden: raise SystemExit(f"REFUSED: forbidden keys in packet {label}: {sorted(forbidden)}")
        p=args.out/f"P2_C1_4_XW_RATER_{label}.json"
        p.write_text(json.dumps(packet,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
        packet_hashes[label]=sha256_file(p)

    manifest={
        "packet_version":VERSION,
        "source_cohort_sha256":source_hash,
        "source_record_count":len(records),
        "rater_A_seed":SEEDS["A"],
        "rater_B_seed":SEEDS["B"],
        "packet_sha256":packet_hashes
    }
    (args.out/"P2_C1_4_XW_PACKET_MANIFEST.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
