#!/usr/bin/env python3
"""Mechanical validator for P2-C1.4 X_W rater response files.

Outcome-blind. Reads only the rater's own blinded packet and the response export.
Performs no adjudication and no reliability statistics; labels are never changed.

Fails closed (exit 1) unless:
  * the response references this exact packet (SHA-256 of the packet file) and rater label;
  * case IDs match the packet exactly, once each, in packet order;
  * case_status equals the packet execution_status (mechanical, not rater-judged);
  * every W1-W7 entry uses the frozen vocabulary and the frozen pairing rules;
  * UNCLEAR carries a non-empty reason (frozen UNCLEAR rule, rule 5);
  * independence is attested and the export is marked complete (unless --allow-partial);
  * no forbidden outcome/SQL/provenance keys appear anywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RESPONSE_VERSION = "P2_C1_4_XW_RATER_RESPONSE_V1_2026-10-02"
PACKET_VERSION = "P2-C1.4_XW_ANNOTATION_PACKET_V1_2026-09-21"
CODEBOOK = "C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19"
DIMENSIONS = ("W1", "W2", "W3", "W4", "W5", "W6", "W7")
APPLICABLE = {"YES", "NO", "UNCLEAR"}
WITNESS = {"PRESENT", "ABSENT_OR_AMBIGUOUS"}
FORBIDDEN_KEYS = {
    "generated_sql", "gold_sql", "gold_answer", "reference_sql", "reference_answer",
    "p0_correct", "p0_correctness", "challenger_correct", "final_correct", "y_h",
    "intervention", "replacement", "replacement_occurred", "downstream_outcome",
    "posthoc_evaluator_labels", "post_hoc", "evidence_hash", "evidence_sha256",
    "source_artifact_sha256", "latency_ms", "llm_calls", "cost", "record_status",
}


def all_keys(x):
    out = set()
    if isinstance(x, dict):
        for k, v in x.items():
            out.add(k)
            out |= all_keys(v)
    elif isinstance(x, list):
        for v in x:
            out |= all_keys(v)
    return out


def validate(packet_path: Path, response_path: Path, allow_partial: bool = False) -> dict:
    problems: list[str] = []
    packet_bytes = packet_path.read_bytes()
    packet = json.loads(packet_bytes)
    resp = json.loads(response_path.read_text(encoding="utf-8"))

    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet: wrong packet_version")
    if resp.get("response_schema_version") != RESPONSE_VERSION:
        problems.append("response: wrong response_schema_version")
    if resp.get("construct_codebook") != CODEBOOK:
        problems.append("response: wrong construct_codebook")
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    if resp.get("packet_sha256") != packet_sha:
        problems.append("response: packet_sha256 does not match this packet file")
    if resp.get("rater_packet") != packet.get("rater_packet"):
        problems.append("response: rater_packet does not match packet")
    if not str(resp.get("rater_id") or "").strip():
        problems.append("response: rater_id missing")
    if resp.get("independence_attested") is not True:
        problems.append("response: independence not attested")
    if not allow_partial and resp.get("complete") is not True:
        problems.append("response: export is not marked complete")
    forbidden = FORBIDDEN_KEYS & all_keys(resp)
    if forbidden:
        problems.append(f"response: forbidden keys present: {sorted(forbidden)}")

    pcases = packet["cases"]
    rcases = resp.get("cases") or []
    if [c["case_id"] for c in rcases] != [c["case_id"] for c in pcases]:
        problems.append("response: case IDs do not match the packet exactly (set and order)")
    pstatus = {c["case_id"]: c["execution_status"] for c in pcases}
    incomplete = 0
    for c in rcases:
        cid = c.get("case_id")
        st = c.get("case_status")
        if st != pstatus.get(cid):
            problems.append(f"{cid}: case_status {st!r} differs from packet execution_status")
            continue
        dims = c.get("dimensions")
        if not isinstance(dims, dict) or set(dims) != set(DIMENSIONS):
            problems.append(f"{cid}: dimensions must be exactly W1-W7")
            continue
        case_ok = True
        for w in DIMENSIONS:
            d = dims[w]
            app, wit, note = d.get("applicable"), d.get("witness"), str(d.get("notes") or "")
            if app is None and allow_partial:
                case_ok = False
                continue
            if app not in APPLICABLE:
                problems.append(f"{cid}:{w}: invalid applicability {app!r}")
                continue
            if st == "NO_USABLE_EVIDENCE" or app == "NO":
                if wit is not None:
                    problems.append(f"{cid}:{w}: witness must be null here")
            elif wit not in WITNESS:
                if allow_partial and wit is None:
                    case_ok = False
                else:
                    problems.append(f"{cid}:{w}: applicable={app} requires a witness label")
            if app == "UNCLEAR" and not note.strip():
                problems.append(f"{cid}:{w}: UNCLEAR requires a reason in notes")
        if not case_ok:
            incomplete += 1
    return {
        "response_file": response_path.name,
        "response_sha256": hashlib.sha256(response_path.read_bytes()).hexdigest(),
        "packet_file": packet_path.name,
        "packet_sha256": packet_sha,
        "rater_packet": packet.get("rater_packet"),
        "cases": len(rcases),
        "incomplete_cases": incomplete,
        "status": "PASS" if not problems else "FAIL",
        "problems": problems[:100],
        "problem_count": len(problems),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--response", type=Path, required=True)
    ap.add_argument("--allow-partial", action="store_true",
                    help="progress check only; never valid for the annotation lock")
    ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    v = validate(a.packet, a.response, a.allow_partial)
    v["allow_partial"] = a.allow_partial
    if a.output:
        a.output.write_text(json.dumps(v, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v[k] for k in ("rater_packet", "cases", "incomplete_cases", "status", "problem_count")}))
    for p in v["problems"][:20]:
        print("  -", p)
    sys.exit(0 if v["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
