#!/usr/bin/env python3
"""Mechanical validator for C4.2.4-A human response files.

This script intentionally performs no scientific adjudication and no reliability
statistics. It checks structural correspondence, response vocabulary, and the
absence of obvious forbidden fields. Human labels remain untouched.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPECTED_CASES = {
    "C423_0091","C423_0021","C423_0061","C423_0071","C423_0041","C423_0081",
    "C423_0001","C423_0031","C423_0011","C423_0111","C423_0051","C423_0101",
}
DIMENSIONS = {"W1","W2","W3","W4","W5","W6","W7"}
CASE_STATUS = {"SUCCESS","NO_USABLE_EVIDENCE"}
APPLICABLE = {"YES","NO","UNCLEAR"}
WITNESS = {"PRESENT","ABSENT_OR_AMBIGUOUS"}
FORBIDDEN_KEYS = {
    "generated_sql","gold_sql","gold_answer","reference_sql","reference_answer",
    "p0_correctness","intervention","replacement","downstream_outcome",
    "post_hoc","sql_sha256","evidence_sha256","source_artifact_sha256",
    "source_evidence_sha256","latency_ms","llm_calls","cost",
}

def all_keys(x):
    out=set()
    if isinstance(x, dict):
        for k,v in x.items():
            out.add(k)
            out |= all_keys(v)
    elif isinstance(x, list):
        for v in x:
            out |= all_keys(v)
    return out

def fail(msg):
    print("FAIL:", msg)
    raise SystemExit(1)

def validate(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or "cases" not in obj:
        fail(f"{path}: missing top-level cases")
    cases=obj["cases"]
    if len(cases) != 12:
        fail(f"{path}: expected 12 cases, found {len(cases)}")
    ids={c.get("case_id") for c in cases}
    if ids != EXPECTED_CASES:
        fail(f"{path}: case IDs do not exactly match frozen cohort")
    forbidden=FORBIDDEN_KEYS & all_keys(obj)
    if forbidden:
        fail(f"{path}: forbidden keys present: {sorted(forbidden)}")

    for c in cases:
        cid=c["case_id"]
        if c.get("case_status") not in CASE_STATUS:
            fail(f"{path}:{cid}: invalid case_status")
        dims=c.get("dimensions")
        if not isinstance(dims, dict) or set(dims) != DIMENSIONS:
            fail(f"{path}:{cid}: dimensions must be exactly W1-W7")
        for w in DIMENSIONS:
            d=dims[w]
            if not isinstance(d, dict):
                fail(f"{path}:{cid}:{w}: dimension must be an object")
            app=d.get("applicable")
            wit=d.get("witness")
            if app not in APPLICABLE:
                fail(f"{path}:{cid}:{w}: invalid applicability {app!r}")
            if c["case_status"] == "NO_USABLE_EVIDENCE":
                if wit is not None:
                    fail(f"{path}:{cid}:{w}: NO_USABLE_EVIDENCE requires witness=null")
            else:
                if app == "NO":
                    if wit is not None:
                        fail(f"{path}:{cid}:{w}: applicable=NO requires witness=null")
                elif app in {"YES","UNCLEAR"}:
                    if wit not in WITNESS:
                        fail(f"{path}:{cid}:{w}: applicable={app} requires witness PRESENT or ABSENT_OR_AMBIGUOUS")
    print(f"PASS: {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: validate_C4_2_4A_human_responses.py RESPONSE.json [...]")
        raise SystemExit(2)
    for p in sys.argv[1:]:
        validate(p)
