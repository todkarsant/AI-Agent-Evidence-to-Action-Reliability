#!/usr/bin/env python3
"""P2-C1.4 blinded feasibility check and annotation subsample.

Amendment: P2-C1.4-BLINDED-FEASIBILITY-AND-ANNOTATION-SUBSAMPLE-AMENDMENT-2026-10-07.

Runs ONCE, before any X_W exists. It uses the outcome only through the pooled event count of the
eligible primary population, which feeds the frozen Riley et al. (2020) calculation. The
X_W-outcome relation cannot be looked at, because no X_W exists yet. The script never prints or
writes the event count or the prevalence. It outputs only:

  * verdict FULL_COHORT_FAILS_RILEY: even every eligible decision cannot meet Riley criteria (i) and
    (iii) at the frozen planning values. Under the frozen hard stop, the confirmatory model cannot
    be fitted, so no annotation is requested. No packets are written.
  * verdict SUBSAMPLE_DRAWN: the annotation sample size n_sub and two subsample packets.
    n_sub = min(N_eligible, max(ceil(1.5 * n_riley), ceil(50 / prevalence))), where
    n_riley = max(criterion (i) min N, criterion (iii) min N). Decisions are drawn by simple random
    sampling without replacement from the eligible decisions (sorted IDs, random.Random(seed)).
    The draw does not depend on outcomes. All E3/E4 decisions with usable evidence are added for
    the frozen S1/S2 sensitivity analyses.

Eligible primary decision (mechanical, as in the frozen protocol section 7 and the missingness
amendment): record_status EVALUABLE, packet execution_status SUCCESS (usable decision-time
evidence), and y_h not null.

Subsample packets keep each rater's original random order and every field, so the existing tool,
validator and construction code work unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

AMENDMENT_ID = "P2-C1.4-BLINDED-FEASIBILITY-AND-ANNOTATION-SUBSAMPLE-AMENDMENT-2026-10-07"
DEFAULT_SEED = 20261007
INFLATION = 1.5
MIN_EXPECTED_EVENTS = 50
STATUS_EVALUABLE = "EVALUABLE"
STATUS_E3E4 = "NON_EVALUABLE_E3E4_RUNTIME_FAILURE_POST_EVIDENCE"
PACKET_NAMES = {"A": "P2_C1_4_XW_RATER_A.json", "B": "P2_C1_4_XW_RATER_B.json"}
MANIFEST = "P2_C1_4_XW_PACKET_MANIFEST.json"

REPO = Path(__file__).resolve().parent.parent.parent
ANALYSIS = REPO / "research" / "P2-C1.2" / "analysis" / "run_P2_C1_2_confirmatory_analysis.py"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _riley():
    spec = importlib.util.spec_from_file_location("p2c12_riley_only", ANALYSIS)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["p2c12_riley_only"] = mod
    spec.loader.exec_module(mod)
    return mod.riley_quantities


def fail(msg: str) -> None:
    raise SystemExit(f"REFUSED: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cohort", type=Path, required=True)
    ap.add_argument("--packets", type=Path, required=True, help="directory with the full blinded packets and their manifest")
    ap.add_argument("--expected-cohort-sha256", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    a = ap.parse_args()

    csha = sha(a.cohort)
    if csha != a.expected_cohort_sha256.lower():
        fail("cohort SHA-256 differs from the locked cohort")
    man_p = a.packets / MANIFEST
    man = json.loads(man_p.read_text(encoding="utf-8"))
    if man.get("source_cohort_sha256") != csha:
        fail("packets were not generated from this cohort")
    packets = {}
    for k, n in PACKET_NAMES.items():
        p = a.packets / n
        if sha(p) != man["packet_sha256"][k]:
            fail(f"packet {k} does not match its manifest")
        packets[k] = json.loads(p.read_text(encoding="utf-8"))

    status = {c["case_id"]: c["execution_status"] for c in packets["A"]["cases"]}
    if status != {c["case_id"]: c["execution_status"] for c in packets["B"]["cases"]}:
        fail("packets A and B disagree on cases or execution status")

    cohort = json.loads(a.cohort.read_text(encoding="utf-8"))
    recs = cohort["records"]
    if set(status) != {r["decision_id"] for r in recs}:
        fail("packet case IDs differ from cohort decision IDs")

    eligible, events, e3e4 = [], 0, []
    for r in recs:
        did, st = r["decision_id"], r["record_status"]
        if st == STATUS_EVALUABLE and status[did] == "SUCCESS":
            y = r["intervention_outcome"].get("y_h")
            if y is not None:
                eligible.append(did)
                events += int(y)
        elif st == STATUS_E3E4 and status[did] == "SUCCESS":
            e3e4.append(did)
    n_elig = len(eligible)

    riley = _riley()(n_elig, events)
    a.out.mkdir(parents=True, exist_ok=True)
    verdict = {
        "amendment_id": AMENDMENT_ID,
        "cohort_sha256": csha,
        "parent_packet_manifest_sha256": sha(man_p),
        "n_eligible_primary": n_elig,
        "seed": a.seed,
        "inflation": INFLATION,
        "min_expected_events": MIN_EXPECTED_EVENTS,
        "event_count_disclosed": False,
    }
    if riley["verdict"] != "RILEY_CRITERIA_MET":
        verdict.update({"verdict": "FULL_COHORT_FAILS_RILEY",
                        "meaning": "Even the full eligible population cannot meet Riley criteria (i) and (iii); under the frozen hard stop the confirmatory model is not fitted. No annotation is requested."})
        (a.out / "FEASIBILITY_VERDICT.json").write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({k: verdict[k] for k in ("verdict", "n_eligible_primary")}))
        return 0

    phi = events / n_elig
    n_riley = max(riley["criterion_i_min_n"], riley["criterion_iii_min_n"])
    n_sub = min(n_elig, max(math.ceil(INFLATION * n_riley), math.ceil(MIN_EXPECTED_EVENTS / phi)))
    sampled = sorted(random.Random(a.seed).sample(sorted(eligible), n_sub))
    selected = set(sampled) | set(e3e4)

    pdir = a.out / "packets"
    pdir.mkdir(exist_ok=True)
    new_sha = {}
    for k, pk in packets.items():
        sub = dict(pk)
        sub["cases"] = [c for c in pk["cases"] if c["case_id"] in selected]
        sub["source_record_count"] = len(sub["cases"])
        sub["subsample"] = {"amendment_id": AMENDMENT_ID, "seed": a.seed,
                            "parent_packet_sha256": man["packet_sha256"][k],
                            "n_sampled_primary": n_sub, "n_e3e4_added": len(e3e4)}
        p = pdir / PACKET_NAMES[k]
        p.write_text(json.dumps(sub, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        new_sha[k] = sha(p)
    sub_man = {
        "packet_version": man["packet_version"],
        "source_cohort_sha256": csha,
        "source_record_count": len(selected),
        "rater_A_seed": man["rater_A_seed"],
        "rater_B_seed": man["rater_B_seed"],
        "packet_sha256": new_sha,
        "parent_packet_manifest_sha256": sha(man_p),
        "subsample_amendment_id": AMENDMENT_ID,
    }
    (pdir / MANIFEST).write_text(json.dumps(sub_man, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    record = {
        "amendment_id": AMENDMENT_ID,
        "seed": a.seed,
        "rule": "simple random sample without replacement of sorted eligible primary decision IDs; all E3/E4 decisions with usable evidence added",
        "n_eligible_primary": n_elig,
        "n_sampled_primary": n_sub,
        "n_e3e4_added": len(e3e4),
        "sampled_decision_ids": sorted(selected),
        "cohort_sha256": csha,
        "parent_packet_manifest_sha256": sha(man_p),
        "subsample_packet_sha256": new_sha,
    }
    (pdir / "SAMPLING_RECORD.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verdict.update({"verdict": "SUBSAMPLE_DRAWN", "n_sampled_primary": n_sub, "n_e3e4_added": len(e3e4),
                    "n_cases_per_rater": len(selected), "sampling_record_sha256": sha(pdir / "SAMPLING_RECORD.json"),
                    "subsample_packet_sha256": new_sha})
    (a.out / "FEASIBILITY_VERDICT.json").write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: verdict[k] for k in ("verdict", "n_eligible_primary", "n_sampled_primary", "n_e3e4_added", "n_cases_per_rater")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
