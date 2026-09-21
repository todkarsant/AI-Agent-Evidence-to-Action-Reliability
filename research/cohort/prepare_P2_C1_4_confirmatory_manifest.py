#!/usr/bin/env python3
"""Freeze the P2-C1.4 confirmatory source-frame manifest.

Selection is outcome-blind:
- concatenate the pinned Spider training-side files;
- deduplicate by (db_id, question);
- exclude the frozen 12-case C4.2.3-B pilot;
- rank deterministically by SHA-256(P2-C1.4-CONF-{db_id}\n{question});
- retain every remaining candidate.

No outcome, correctness, intervention, or X_W field is read.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

PROTOCOL = "P2-C1.4-CONFIRMATORY-V1-RUNTIME2-2026-09-21"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--train",nargs="+",type=Path,required=True)
    ap.add_argument("--pilot-manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    pilot=json.loads(args.pilot_manifest.read_text(encoding="utf-8"))
    excluded={(x["db_id"],x["question"]) for x in pilot["cases"]}

    seen=set()
    candidates=[]
    for p in args.train:
        rows=json.loads(p.read_text(encoding="utf-8"))
        for x in rows:
            key=(x["db_id"],x["question"])
            if key in excluded or key in seen:
                continue
            seen.add(key)
            rank=hashlib.sha256(
                f"P2-C1.4-CONF-{x['db_id']}\n{x['question']}".encode("utf-8")
            ).hexdigest()
            candidates.append((rank,x))

    candidates.sort(key=lambda z:z[0])
    cases=[
        {
            "decision_id":f"P2C14-CONF-{i:06d}",
            "db_id":x["db_id"],
            "question":x["question"],
            "source_rank_sha256":rank,
            "dependence_group":f"{x['db_id']}::{x['question']}",
        }
        for i,(rank,x) in enumerate(candidates,1)
    ]

    manifest={
        "protocol_version":PROTOCOL,
        "confirmatory":True,
        "selection_rule":"all unique training-side (db_id,question) cases after frozen pilot exclusion; deterministic SHA-256 ordering",
        "source_files":[str(p) for p in args.train],
        "excluded_source_manifest_sha256":sha256_bytes(args.pilot_manifest.read_bytes()),
        "case_count":len(cases),
        "cases":cases,
    }
    if not cases:
        raise SystemExit("FAIL: no confirmatory candidates")
    if len({c["decision_id"] for c in cases}) != len(cases):
        raise SystemExit("FAIL: duplicate decision_id")
    if len({(c["db_id"],c["question"]) for c in cases}) != len(cases):
        raise SystemExit("FAIL: duplicate (db_id,question)")

    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(manifest,indent=2,ensure_ascii=False)+"\n"
    args.output.write_text(raw,encoding="utf-8")
    print(json.dumps({
        "protocol_version":PROTOCOL,
        "case_count":len(cases),
        "manifest_sha256":sha256_bytes(raw.encode("utf-8")),
        "excluded_pilot_cases":len(excluded)
    },indent=2))

if __name__=="__main__":
    main()
