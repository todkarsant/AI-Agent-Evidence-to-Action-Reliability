"""P2-C1.4 evidence-availability audit (outcome-blind, descriptive, NOT prespecified).

Compares decisions whose decision-time evidence is usable (packet execution_status SUCCESS) with
NO_USABLE_EVIDENCE decisions. The primary population requires usable evidence (protocol section 13),
so this shows which kinds of decisions the primary analysis cannot see.

Reads only:
  * a blinded rater packet (case_id, database_id, question, execution_status), which holds no outcomes;
  * optionally the reference-SQL features CSV (decision_id, hardness, nesting_depth).
It never reads the cohort file and so cannot touch outcomes. No hypothesis test is run.

  python p2_c1_4_evidence_availability_audit.py --packet P2_C1_4_XW_RATER_A.json \
      [--reference-features P2_C1_4_REFERENCE_SQL_FEATURES.csv] --out EVIDENCE_AVAILABILITY_AUDIT.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

GROUPS = ("SUCCESS", "NO_USABLE_EVIDENCE")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dist(values) -> dict:
    c = Counter(values)
    n = sum(c.values())
    return {"n": n, "proportions": {str(k): round(v / n, 4) for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))}}


def summary(xs: list) -> dict:
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4) if len(xs) > 1 else [xs[0]] * 3
    return {"n": len(xs), "mean": round(statistics.fmean(xs), 2), "q25": q[0], "median": q[1], "q75": q[2]}


def audit(packet: Path, features: Path | None) -> dict:
    cases = json.loads(packet.read_text(encoding="utf-8"))["cases"]
    status = {c["case_id"]: c["execution_status"] for c in cases}
    bad = set(status.values()) - set(GROUPS)
    if bad:
        raise SystemExit(f"REFUSED: unexpected execution_status values {sorted(bad)}")
    by = {g: [c for c in cases if c["execution_status"] == g] for g in GROUPS}
    per_db = defaultdict(Counter)
    for c in cases:
        per_db[c["database_id"]][c["execution_status"]] += 1
    rates = sorted(v["NO_USABLE_EVIDENCE"] / sum(v.values()) for v in per_db.values())
    out = {
        "audit": "P2-C1.4 evidence availability (outcome-blind; descriptive; not prespecified)",
        "inputs": {"packet_sha256": sha(packet), "reference_features_sha256": sha(features) if features else None},
        "outcome_fields_used": [],
        "n_decisions": len(cases),
        "counts": {g: len(by[g]) for g in GROUPS},
        "no_usable_evidence_fraction": round(len(by["NO_USABLE_EVIDENCE"]) / len(cases), 4),
        "question_length_chars": {g: summary([len(c["question"]) for c in by[g]]) for g in GROUPS},
        "per_database_no_usable_evidence_rate": {
            "n_databases": len(per_db), "min": round(rates[0], 4), "median": round(statistics.median(rates), 4),
            "max": round(rates[-1], 4)},
        "test": "descriptive only; no hypothesis test",
    }
    if features:
        rows = list(csv.DictReader(features.open(encoding="utf-8")))
        feat = {r["decision_id"]: r for r in rows}
        for name in ("hardness", "nesting_depth"):
            out[f"reference_sql_{name}"] = {
                g: dist(feat[c["case_id"]][name] for c in by[g] if c["case_id"] in feat) for g in GROUPS}
        out["reference_features_missing"] = sorted(set(status) - set(feat))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--packet", type=Path, required=True, help="a FULL blinded rater packet (A or B)")
    ap.add_argument("--reference-features", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    res = audit(a.packet, a.reference_features)
    a.out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("n_decisions", "counts", "no_usable_evidence_fraction")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
