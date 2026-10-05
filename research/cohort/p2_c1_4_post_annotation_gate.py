#!/usr/bin/env python3
"""P2-C1.4 post-annotation gate: validate exports -> lock raw labels -> construct X_W -> run analysis once.

Two stages, run as separate CI jobs so that stage 1 never has the outcome-bearing cohort on disk.

stage1 (outcome-blind)
  * both FINAL rater exports must be present (A and B, committed together);
  * both packet files must match the packet manifest SHA-256;
  * each export must pass validate_P2_C1_4_XW_responses.py (no partial exports);
  * construct_P2_C1_4_XW.py writes the raw-annotation lock, reliability report and X_W.
stage2 (uses the locked cohort; runs only after stage 1 passed)
  * the cohort file SHA-256 must equal the expected locked-cohort hash AND the packet manifest's
    source_cohort_sha256 recorded in the raw-annotation lock (chain cohort -> packets -> labels -> X_W);
  * the forensic cohort lock must read PASS_IMMUTABLE_COHORT_LOCK;
  * the frozen analysis runs once, without test mode, with --sha-check on both inputs.
    Exit 0 (completed) and exit 3 (FEASIBILITY_STOP / FEASIBILITY_STOP_RILEY) are both valid
    confirmatory outcomes and are reported; exit 2 (input invalid) fails the gate.

Every stage writes a machine-readable verdict JSON. Labels and parameters are never changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
VALIDATOR = HERE / "validate_P2_C1_4_XW_responses.py"
CONSTRUCT = HERE / "construct_P2_C1_4_XW.py"
ANALYSIS = REPO / "research" / "P2-C1.2" / "analysis" / "run_P2_C1_2_confirmatory_analysis.py"

RESPONSE_NAMES = {"A": "P2_C1_4_XW_RESPONSES_RATER_A_FINAL.json", "B": "P2_C1_4_XW_RESPONSES_RATER_B_FINAL.json"}
PACKET_NAMES = {"A": "P2_C1_4_XW_RATER_A.json", "B": "P2_C1_4_XW_RATER_B.json"}
PACKET_MANIFEST = "P2_C1_4_XW_PACKET_MANIFEST.json"
COHORT_FILE = "P2_C1_4_CONFIRMATORY_ALIGNED_RECORDS.json"
COHORT_LOCK = Path("lock") / "P2_C1_4_CONFIRMATORY_COHORT_LOCK.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def refuse(out: Path, stage: str, reason: str, **extra) -> None:
    write(out / f"{stage.upper()}_VERDICT.json", {"stage": stage, "status": "REFUSED", "reason": reason, **extra})
    print(f"REFUSED ({stage}): {reason}", file=sys.stderr)
    sys.exit(1)


def stage1(packets: Path, responses: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    present = {k: (responses / n).is_file() for k, n in RESPONSE_NAMES.items()}
    if not all(present.values()):
        refuse(out, "stage1", "both FINAL rater exports must be committed together", present=present,
               expected=RESPONSE_NAMES)
    man_p = packets / PACKET_MANIFEST
    if not man_p.is_file():
        refuse(out, "stage1", f"packet manifest missing: {man_p}")
    man = json.loads(man_p.read_text(encoding="utf-8"))
    for k, n in PACKET_NAMES.items():
        p = packets / n
        if not p.is_file():
            refuse(out, "stage1", f"packet {k} missing: {p}")
        if sha(p) != man["packet_sha256"][k]:
            refuse(out, "stage1", f"packet {k} does not match the packet manifest")
    reports = {}
    for k in ("A", "B"):
        rp = out / f"P2_C1_4_XW_VALIDATION_{k}.json"
        r = subprocess.run([sys.executable, str(VALIDATOR), "--packet", str(packets / PACKET_NAMES[k]),
                            "--response", str(responses / RESPONSE_NAMES[k]), "--output", str(rp)],
                           capture_output=True, text=True)
        print(r.stdout[-2000:], r.stderr[-2000:])
        rep = json.loads(rp.read_text(encoding="utf-8")) if rp.is_file() else {"status": "FAIL", "problems": [r.stderr[-500:]]}
        reports[k] = {"status": rep.get("status"), "cases": rep.get("cases"), "problem_count": rep.get("problem_count"),
                      "first_problems": (rep.get("problems") or [])[:10]}
        if r.returncode != 0 or rep.get("status") != "PASS":
            refuse(out, "stage1", f"rater {k} export failed validation", validation=reports)
    cdir = out / "construction"
    r = subprocess.run([sys.executable, str(CONSTRUCT),
                        "--packet-a", str(packets / PACKET_NAMES["A"]), "--packet-b", str(packets / PACKET_NAMES["B"]),
                        "--packet-manifest", str(man_p),
                        "--response-a", str(responses / RESPONSE_NAMES["A"]),
                        "--response-b", str(responses / RESPONSE_NAMES["B"]),
                        "--out", str(cdir)], capture_output=True, text=True)
    print(r.stdout[-2000:], r.stderr[-2000:])
    if r.returncode != 0:
        refuse(out, "stage1", "X_W construction failed", detail=r.stderr[-1000:] or r.stdout[-1000:])
    lock = json.loads((cdir / "P2_C1_4_XW_RAW_ANNOTATION_LOCK.json").read_text(encoding="utf-8"))
    write(out / "STAGE1_VERDICT.json", {
        "stage": "stage1",
        "status": "PASS_RAW_ANNOTATIONS_LOCKED_XW_CONSTRUCTED",
        "validation": reports,
        "packet_manifest_sha256": sha(man_p),
        "source_cohort_sha256_from_packets": man["source_cohort_sha256"],
        "raw_annotation_lock_sha256": sha(cdir / "P2_C1_4_XW_RAW_ANNOTATION_LOCK.json"),
        "xw_sha256": sha(cdir / "P2_C1_4_XW.json"),
        "reliability_sha256": sha(cdir / "P2_C1_4_XW_RELIABILITY.json"),
        "case_count": lock["case_count"],
        "outcomes_accessed": False,
    })
    print("STAGE1 PASS")


def stage2(cohort_dir: Path, construction: Path, out: Path, expected_cohort_sha: str, test_mode_repeats: int | None = None,
           reference_features: Path | None = None, expected_features_sha: str | None = None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    cohort = cohort_dir / COHORT_FILE
    lockf = cohort_dir / COHORT_LOCK
    xw = construction / "P2_C1_4_XW.json"
    rawlock = construction / "P2_C1_4_XW_RAW_ANNOTATION_LOCK.json"
    for p in (cohort, xw, rawlock):
        if not p.is_file():
            refuse(out, "stage2", f"required input missing: {p}")
    csha = sha(cohort)
    raw = json.loads(rawlock.read_text(encoding="utf-8"))
    if raw.get("status") != "RAW_ANNOTATIONS_LOCKED":
        refuse(out, "stage2", "raw annotations are not locked")
    if csha != expected_cohort_sha.lower():
        refuse(out, "stage2", "cohort SHA-256 differs from the expected locked cohort", got=csha, expected=expected_cohort_sha)
    if csha != raw.get("source_cohort_sha256"):
        refuse(out, "stage2", "cohort SHA-256 differs from the cohort the annotation packets were generated from",
               got=csha, packets_source=raw.get("source_cohort_sha256"))
    if lockf.is_file():
        lk = json.loads(lockf.read_text(encoding="utf-8"))
        if lk.get("status") != "PASS_IMMUTABLE_COHORT_LOCK":
            refuse(out, "stage2", "forensic cohort lock is not PASS_IMMUTABLE_COHORT_LOCK")
    elif test_mode_repeats is None:
        refuse(out, "stage2", f"forensic cohort lock file missing: {lockf}")
    fsha = None
    if reference_features is not None:
        if not reference_features.is_file():
            refuse(out, "stage2", f"reference-features file missing: {reference_features}")
        fsha = sha(reference_features)
        if expected_features_sha and fsha != expected_features_sha.lower():
            refuse(out, "stage2", "reference-features CSV differs from the expected file", got=fsha, expected=expected_features_sha)
    xsha = sha(xw)
    adir = out / "analysis"
    cmd = [sys.executable, str(ANALYSIS), "--cohort", str(cohort), "--xw", str(xw), "--out", str(adir),
           "--sha-check", csha, xsha]
    if reference_features is not None:
        cmd += ["--reference-features", str(reference_features)]
    if test_mode_repeats is not None:  # local pipeline tests only; recorded in results.json
        cmd += ["--test-mode", "--repeats", str(test_mode_repeats)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-3000:])
    if r.returncode not in (0, 3):
        refuse(out, "stage2", f"analysis refused its inputs (exit {r.returncode})", detail=r.stderr[-1500:])
    res = json.loads((adir / "results.json").read_text(encoding="utf-8"))
    write(out / "STAGE2_VERDICT.json", {
        "stage": "stage2",
        "status": "ANALYSIS_EXECUTED",
        "analysis_exit_code": r.returncode,
        "primary_verdict": res["verdicts"]["primary"],
        "riley_verdict": res["verdicts"]["riley"],
        "robustness_flag": res["verdicts"]["robustness"]["flag"],
        "test_mode": res["test_mode"],
        "cohort_sha256": csha,
        "xw_sha256": xsha,
        "reference_features_sha256": fsha,
        "raw_annotation_lock_sha256": sha(rawlock),
        "results_json_sha256": sha(adir / "results.json"),
    })
    print(f"STAGE2 DONE: {res['verdicts']['primary']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="stage", required=True)
    s1 = sub.add_parser("stage1")
    s1.add_argument("--packets", type=Path, required=True)
    s1.add_argument("--responses", type=Path, required=True)
    s1.add_argument("--out", type=Path, required=True)
    s2 = sub.add_parser("stage2")
    s2.add_argument("--cohort-dir", type=Path, required=True)
    s2.add_argument("--construction", type=Path, required=True)
    s2.add_argument("--out", type=Path, required=True)
    s2.add_argument("--expected-cohort-sha256", required=True)
    s2.add_argument("--test-mode-repeats", type=int, default=None, help="LOCAL TESTS ONLY")
    s2.add_argument("--reference-features", type=Path, default=None, help="CSV from reference_sql_features_P2_C1_4.py")
    s2.add_argument("--expected-reference-features-sha256", default=None)
    a = ap.parse_args()
    if a.stage == "stage1":
        stage1(a.packets, a.responses, a.out)
    else:
        stage2(a.cohort_dir, a.construction, a.out, a.expected_cohort_sha256, a.test_mode_repeats,
               a.reference_features, a.expected_reference_features_sha256)


if __name__ == "__main__":
    main()
