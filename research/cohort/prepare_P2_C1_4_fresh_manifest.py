#!/usr/bin/env python3
"""Prepare a non-confirmatory fresh manifest from Spider development questions.

Freshness rule for this dry-run utility:
- exclude every (db_id, question) in the frozen C4.2.3-B pilot manifest;
- rank remaining questions by SHA-256(decision_id seed);
- select the requested count;
- write the resulting manifest and hash externally.

This utility does not establish the confirmatory sample size or freeze the
future scientific cohort. A future confirmatory manifest must be separately
versioned and frozen.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--train",nargs="+",type=Path,required=True)
    ap.add_argument("--pilot-manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--count",type=int,default=4)
    args=ap.parse_args()
    pilot=json.loads(args.pilot_manifest.read_text())
    excluded={(x["db_id"],x["question"]) for x in pilot["cases"]}
    rows=[]
    for p in args.train:
        rows.extend(json.loads(p.read_text(encoding="utf-8")))
    seen=set(); candidates=[]
    for x in rows:
        key=(x["db_id"],x["question"])
        if key in excluded or key in seen: continue
        seen.add(key)
        seed=f"P2-C1.4-DRY-{x['db_id']}\n{x['question']}".encode()
        rank=hashlib.sha256(seed).hexdigest()
        candidates.append((rank,x))
    candidates.sort(key=lambda z:z[0])
    chosen=candidates[:args.count]
    if len(chosen)<args.count: raise SystemExit("not enough fresh candidates")
    manifest={
        "protocol_version":"P2-C1.4-FRESH-MANIFEST-DRY-V1",
        "confirmatory":False,
        "excluded_source_manifest_sha256":hashlib.sha256(args.pilot_manifest.read_bytes()).hexdigest(),
        "selection_rule":"exclude pilot (db_id,question), then ascending SHA256(P2-C1.4-DRY-{db_id}\\n{question})",
        "case_count":len(chosen),
        "cases":[{"decision_id":f"P2C14-DRY-{i:03d}","db_id":x["db_id"],"question":x["question"]} for i,(_,x) in enumerate(chosen,1)]
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"cases":len(chosen),"manifest_sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),"excluded":len(excluded)},indent=2))
if __name__=="__main__": main()
