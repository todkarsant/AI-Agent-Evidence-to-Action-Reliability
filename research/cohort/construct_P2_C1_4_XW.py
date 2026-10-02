#!/usr/bin/env python3
"""Lock raw rater annotations, report reliability, and construct X_W for P2-C1.4.

Outcome-blind: reads only the two blinded rater packets, their packet manifest
and the two validated response exports. It never opens the aligned cohort,
outcomes, SQL or provenance hashes.

Rules applied (frozen; see the X_W construction amendment for the combination rule):
  * per-rater, per-case X_W (UNCLEAR rule freeze 2026-09-21, section 2):
        YES + PRESENT              -> 1, in denominator
        YES + ABSENT_OR_AMBIGUOUS  -> 0, in denominator
        UNCLEAR (genuine semantic) -> 0, in denominator (rule 5)
        NO                         -> excluded
    X_W = sum / |denominator|; NO_USABLE_EVIDENCE -> missing; empty denominator -> missing.
  * combined X_W = mean of the raters' X_W that are defined; missing if neither is defined.
  * raw labels are never modified; no adjudication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_P2_C1_4_XW_responses import DIMENSIONS, validate  # noqa: E402

VERSION = "P2-C1.4-XW-CONSTRUCTION-V1-2026-10-02"
BOOT_REPS = 2000
BOOT_SEED = 20261002


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rater_xw(case: dict) -> tuple[float | None, dict]:
    if case["case_status"] == "NO_USABLE_EVIDENCE":
        return None, {w: None for w in DIMENSIONS}
    ind = {}
    for w in DIMENSIONS:
        d = case["dimensions"][w]
        if d["applicable"] == "NO":
            ind[w] = None
        elif d["applicable"] == "UNCLEAR":
            ind[w] = 0
        else:
            ind[w] = 1 if d["witness"] == "PRESENT" else 0
    vals = [v for v in ind.values() if v is not None]
    return (sum(vals) / len(vals) if vals else None), ind


def kappa_ac1(pairs: list[tuple[str, str]], cats: list[str]) -> dict:
    n = len(pairs)
    if n == 0:
        return {"n": 0, "agreement": None, "cohen_kappa": None, "gwet_ac1": None, "table": {}}
    table = {a: {b: 0 for b in cats} for a in cats}
    for a, b in pairs:
        table[a][b] += 1
    po = sum(table[c][c] for c in cats) / n
    pa = {c: sum(table[c].values()) / n for c in cats}
    pb = {c: sum(table[a][c] for a in cats) / n for c in cats}
    pe_k = sum(pa[c] * pb[c] for c in cats)
    kappa = None if pe_k >= 1 else (po - pe_k) / (1 - pe_k)
    q = len(cats)
    pi = {c: (pa[c] + pb[c]) / 2 for c in cats}
    pe_g = sum(pi[c] * (1 - pi[c]) for c in cats) / (q - 1)
    ac1 = None if pe_g >= 1 else (po - pe_g) / (1 - pe_g)
    return {"n": n, "agreement": po, "cohen_kappa": kappa, "gwet_ac1": ac1, "table": table,
            "marginals_A": pa, "marginals_B": pb}


def boot_ci(pairs, cats, key):
    if len(pairs) < 2:
        return None
    rng = random.Random(BOOT_SEED)
    vals = []
    for _ in range(BOOT_REPS):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        v = kappa_ac1(s, cats)[key]
        if v is not None:
            vals.append(v)
    if not vals:
        return None
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return [lo, hi]


def stat_block(pairs, cats):
    s = kappa_ac1(pairs, cats)
    s["cohen_kappa_ci95_case_bootstrap"] = boot_ci(pairs, cats, "cohen_kappa")
    s["gwet_ac1_ci95_case_bootstrap"] = boot_ci(pairs, cats, "gwet_ac1")
    return s


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return None if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet-a", type=Path, required=True)
    ap.add_argument("--packet-b", type=Path, required=True)
    ap.add_argument("--packet-manifest", type=Path, required=True)
    ap.add_argument("--response-a", type=Path, required=True)
    ap.add_argument("--response-b", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    man = json.loads(a.packet_manifest.read_text(encoding="utf-8"))
    for lab, p in (("A", a.packet_a), ("B", a.packet_b)):
        if man["packet_sha256"][lab] != sha(p):
            raise SystemExit(f"FAIL: packet {lab} does not match the packet manifest")
    va = validate(a.packet_a, a.response_a)
    vb = validate(a.packet_b, a.response_b)
    for lab, v in (("A", va), ("B", vb)):
        if v["status"] != "PASS" or v["rater_packet"] != lab:
            raise SystemExit(f"FAIL: response {lab} did not validate: {v['problems'][:5]}")
    ra = json.loads(a.response_a.read_text(encoding="utf-8"))
    rb = json.loads(a.response_b.read_text(encoding="utf-8"))
    if ra["rater_id"].strip().lower() == rb["rater_id"].strip().lower():
        raise SystemExit("FAIL: both responses carry the same rater_id")
    A = {c["case_id"]: c for c in ra["cases"]}
    B = {c["case_id"]: c for c in rb["cases"]}
    if set(A) != set(B):
        raise SystemExit("FAIL: raters annotated different case sets")
    order = sorted(A)

    a.out.mkdir(parents=True, exist_ok=True)
    lock = {
        "construction_version": VERSION,
        "packet_manifest_sha256": sha(a.packet_manifest),
        "source_cohort_sha256": man["source_cohort_sha256"],
        "packet_sha256": man["packet_sha256"],
        "response_sha256": {"A": va["response_sha256"], "B": vb["response_sha256"]},
        "rater_ids": {"A": ra["rater_id"], "B": rb["rater_id"]},
        "independence_attested": {"A": ra["independence_attested"], "B": rb["independence_attested"]},
        "case_count": len(order),
        "status": "RAW_ANNOTATIONS_LOCKED",
    }
    (a.out / "P2_C1_4_XW_RAW_ANNOTATION_LOCK.json").write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")

    rel = {"construction_version": VERSION, "applicability": {}, "witness_where_both_applicable": {},
           "normalized_indicator": {}}
    per = []
    xa_list, xb_list = [], []
    for cid in order:
        xa, ia = rater_xw(A[cid])
        xb, ib = rater_xw(B[cid])
        defined = [x for x in (xa, xb) if x is not None]
        per.append({"decision_id": cid, "x_w_A": xa, "x_w_B": xb,
                    "x_w": (sum(defined) / len(defined)) if defined else None,
                    "case_status": A[cid]["case_status"]})
        if xa is not None and xb is not None:
            xa_list.append(xa)
            xb_list.append(xb)
    for w in DIMENSIONS:
        app = [(A[c]["dimensions"][w]["applicable"], B[c]["dimensions"][w]["applicable"]) for c in order]
        rel["applicability"][w] = stat_block(app, ["YES", "NO", "UNCLEAR"])
        wit = [(A[c]["dimensions"][w]["witness"], B[c]["dimensions"][w]["witness"]) for c in order
               if A[c]["case_status"] == "SUCCESS"
               and A[c]["dimensions"][w]["applicable"] == "YES" and B[c]["dimensions"][w]["applicable"] == "YES"]
        rel["witness_where_both_applicable"][w] = stat_block(wit, ["PRESENT", "ABSENT_OR_AMBIGUOUS"])
        norm = []
        for c in order:
            if A[c]["case_status"] != "SUCCESS":
                continue
            _, ia = rater_xw(A[c])
            _, ib = rater_xw(B[c])
            m = lambda v: "EXCLUDED" if v is None else str(v)  # noqa: E731
            norm.append((m(ia[w]), m(ib[w])))
        rel["normalized_indicator"][w] = stat_block(norm, ["1", "0", "EXCLUDED"])
    rel["x_w_between_raters"] = {
        "n_both_defined": len(xa_list),
        "pearson_r": corr(xa_list, xb_list),
        "mean_abs_diff": (sum(abs(x - y) for x, y in zip(xa_list, xb_list)) / len(xa_list)) if xa_list else None,
        "exact_equal_fraction": (sum(1 for x, y in zip(xa_list, xb_list) if x == y) / len(xa_list)) if xa_list else None,
    }
    rel["x_w_missing"] = {
        "no_usable_evidence": sum(1 for r in per if r["case_status"] == "NO_USABLE_EVIDENCE"),
        "empty_denominator_or_undefined_combined": sum(1 for r in per if r["case_status"] == "SUCCESS" and r["x_w"] is None),
        "one_rater_undefined": sum(1 for r in per if r["case_status"] == "SUCCESS" and (r["x_w_A"] is None) != (r["x_w_B"] is None)),
    }
    rel["note"] = "Descriptive reliability only; no coefficient threshold constitutes a PASS (codebook v2)."
    (a.out / "P2_C1_4_XW_RELIABILITY.json").write_text(json.dumps(rel, indent=2, sort_keys=True) + "\n")
    xw = {"xw_construction_version": VERSION,
          "raw_annotation_lock_sha256": sha(a.out / "P2_C1_4_XW_RAW_ANNOTATION_LOCK.json"),
          "records": [{"decision_id": r["decision_id"], "x_w": r["x_w"]} for r in per]}
    (a.out / "P2_C1_4_XW.json").write_text(json.dumps(xw, indent=2, sort_keys=True) + "\n")
    (a.out / "P2_C1_4_XW_PER_RATER.json").write_text(json.dumps({"construction_version": VERSION, "records": per}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"cases": len(order), "x_w_defined": sum(1 for r in per if r["x_w"] is not None),
                      **rel["x_w_missing"], "status": "XW_CONSTRUCTED"}))


if __name__ == "__main__":
    main()
