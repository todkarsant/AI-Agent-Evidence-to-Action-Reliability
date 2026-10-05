"""End-to-end tests for research/cohort/p2_c1_4_post_annotation_gate.py (SYNTHETIC data only).

Chain exercised: synthetic locked cohort -> real packet generator -> simulated rater exports
-> stage1 (validate, raw lock, X_W) -> stage2 (hash chain checks, frozen analysis in test mode).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GATE = REPO / "research" / "cohort" / "p2_c1_4_post_annotation_gate.py"
GEN = REPO / "research" / "cohort" / "generate_P2_C1_4_XW_annotation_packets.py"

_spec = importlib.util.spec_from_file_location("p2c12_synthetic_gate", REPO / "research" / "P2-C1.2" / "analysis" / "make_synthetic_cohort.py")
SYN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SYN)

N = 600
DIMS = ("W1", "W2", "W3", "W4", "W5", "W6", "W7")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


def simulate_export(packet_path: Path, rater_id: str, seed: int) -> dict:
    packet = json.loads(packet_path.read_bytes())
    rng = random.Random(seed)
    cases = []
    for c in packet["cases"]:
        st = c["execution_status"]
        dims = {}
        for w in DIMS:
            if st == "NO_USABLE_EVIDENCE":
                dims[w] = {"applicable": "NO", "witness": None, "notes": ""}
                continue
            u = rng.random()
            if u < 0.45:
                dims[w] = {"applicable": "NO", "witness": None, "notes": ""}
            elif u < 0.5:
                dims[w] = {"applicable": "UNCLEAR", "witness": "ABSENT_OR_AMBIGUOUS", "notes": "question wording ambiguous"}
            else:
                dims[w] = {"applicable": "YES", "witness": rng.choice(["PRESENT", "ABSENT_OR_AMBIGUOUS"]), "notes": ""}
        cases.append({"case_id": c["case_id"], "case_status": st, "dimensions": dims, "case_notes": ""})
    return {
        "response_schema_version": "P2_C1_4_XW_RATER_RESPONSE_V1_2026-10-02",
        "tool_version": "P2_C1_4_XW_ANNOTATOR_V1_2026-10-02",
        "construct_codebook": "C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19",
        "unclear_rule": "C4_2_4A_UNCLEAR_XW_OPERATIONAL_RULE_FREEZE_2026-09-21",
        "packet_version": packet["packet_version"],
        "packet_sha256": sha(packet_path),
        "rater_packet": packet["rater_packet"],
        "rater_id": rater_id,
        "independence_attested": True,
        "complete": True,
        "completed_cases": len(cases),
        "total_cases": len(cases),
        "cases": cases,
    }


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    d = tmp_path_factory.mktemp("gate")
    cohort, _, ref = SYN.make(N, seed=12, signal="xw", base_rate=0.25)
    cdir = d / "cohort"
    (cdir / "lock").mkdir(parents=True)
    cfile = cdir / "P2_C1_4_CONFIRMATORY_ALIGNED_RECORDS.json"
    cfile.write_text(json.dumps(cohort), encoding="utf-8")
    (cdir / "lock" / "P2_C1_4_CONFIRMATORY_COHORT_LOCK.json").write_text(json.dumps({"status": "PASS_IMMUTABLE_COHORT_LOCK", "record_count": N}))
    pdir = d / "packets"
    r = run(GEN, "--cohort", cfile, "--out", pdir, "--expected-count", N)
    assert r.returncode == 0, r.stderr
    rdir = d / "responses"
    rdir.mkdir()
    for k, s in (("A", 1), ("B", 2)):
        exp = simulate_export(pdir / f"P2_C1_4_XW_RATER_{k}.json", f"Synthetic rater {k}", s)
        (rdir / f"P2_C1_4_XW_RESPONSES_RATER_{k}_FINAL.json").write_text(json.dumps(exp, indent=1), encoding="utf-8")
    ffile = d / "P2_C1_4_REFERENCE_SQL_FEATURES.csv"
    with open(ffile, "w", encoding="utf-8") as fh:
        fh.write("decision_id,hardness,nesting_depth\n")
        for row in ref:
            fh.write(f"{row['decision_id']},{row['hardness']},{row['nesting_depth']}\n")
    return {"d": d, "cdir": cdir, "cfile": cfile, "pdir": pdir, "rdir": rdir, "ffile": ffile}


def stage1(w, out, rdir=None, pdir=None):
    return run(GATE, "stage1", "--packets", pdir or w["pdir"], "--responses", rdir or w["rdir"], "--out", out)


def verdict(out, stage):
    return json.loads((Path(out) / f"{stage.upper()}_VERDICT.json").read_text())


def test_full_chain_passes(world, tmp_path):
    out1 = tmp_path / "s1"
    r = stage1(world, out1)
    assert r.returncode == 0, r.stderr + r.stdout
    v1 = verdict(out1, "stage1")
    assert v1["status"] == "PASS_RAW_ANNOTATIONS_LOCKED_XW_CONSTRUCTED"
    assert v1["outcomes_accessed"] is False and v1["case_count"] == N
    assert v1["source_cohort_sha256_from_packets"] == sha(world["cfile"])
    out2 = tmp_path / "s2"
    r = run(GATE, "stage2", "--cohort-dir", world["cdir"], "--construction", out1 / "construction", "--out", out2,
            "--expected-cohort-sha256", sha(world["cfile"]), "--test-mode-repeats", "2")
    assert r.returncode == 0, r.stderr + r.stdout
    v2 = verdict(out2, "stage2")
    assert v2["status"] == "ANALYSIS_EXECUTED"
    assert v2["analysis_exit_code"] in (0, 3)
    assert v2["primary_verdict"] in ("ANALYSIS_COMPLETED", "FEASIBILITY_STOP_RILEY", "FEASIBILITY_STOP")
    assert v2["xw_sha256"] == v1["xw_sha256"]
    assert (out2 / "analysis" / "results.json").is_file()


def test_refuses_when_only_one_export_committed(world, tmp_path):
    rdir = tmp_path / "only_a"
    rdir.mkdir()
    shutil.copy(world["rdir"] / "P2_C1_4_XW_RESPONSES_RATER_A_FINAL.json", rdir)
    r = stage1(world, tmp_path / "s1", rdir=rdir)
    assert r.returncode == 1
    assert verdict(tmp_path / "s1", "stage1")["status"] == "REFUSED"
    assert not (tmp_path / "s1" / "construction").exists()


def test_refuses_incomplete_or_invalid_export(world, tmp_path):
    rdir = tmp_path / "bad"
    shutil.copytree(world["rdir"], rdir)
    p = rdir / "P2_C1_4_XW_RESPONSES_RATER_B_FINAL.json"
    exp = json.loads(p.read_text())
    exp["complete"] = False
    p.write_text(json.dumps(exp))
    r = stage1(world, tmp_path / "s1", rdir=rdir)
    assert r.returncode == 1
    v = verdict(tmp_path / "s1", "stage1")
    assert "rater B" in v["reason"] and not (tmp_path / "s1" / "construction").exists()


def test_refuses_tampered_packet(world, tmp_path):
    pdir = tmp_path / "packets"
    shutil.copytree(world["pdir"], pdir)
    with open(pdir / "P2_C1_4_XW_RATER_A.json", "a") as fh:
        fh.write(" ")
    r = stage1(world, tmp_path / "s1", pdir=pdir)
    assert r.returncode == 1
    assert "manifest" in verdict(tmp_path / "s1", "stage1")["reason"]


def test_stage2_refuses_wrong_or_unlinked_cohort(world, tmp_path):
    out1 = tmp_path / "s1"
    assert stage1(world, out1).returncode == 0
    r = run(GATE, "stage2", "--cohort-dir", world["cdir"], "--construction", out1 / "construction", "--out", tmp_path / "s2a",
            "--expected-cohort-sha256", "0" * 64, "--test-mode-repeats", "1")
    assert r.returncode == 1 and "expected locked cohort" in verdict(tmp_path / "s2a", "stage2")["reason"]
    other = tmp_path / "other"
    shutil.copytree(world["cdir"], other)
    f = other / "P2_C1_4_CONFIRMATORY_ALIGNED_RECORDS.json"
    f.write_text(f.read_text() + " ")
    r = run(GATE, "stage2", "--cohort-dir", other, "--construction", out1 / "construction", "--out", tmp_path / "s2b",
            "--expected-cohort-sha256", sha(f), "--test-mode-repeats", "1")
    assert r.returncode == 1 and "annotation packets" in verdict(tmp_path / "s2b", "stage2")["reason"]
    assert not (tmp_path / "s2b" / "analysis").exists()


def test_stage2_passes_reference_features_and_checks_their_hash(world, tmp_path):
    out1 = tmp_path / "s1"
    assert stage1(world, out1).returncode == 0
    r = run(GATE, "stage2", "--cohort-dir", world["cdir"], "--construction", out1 / "construction", "--out", tmp_path / "s2",
            "--expected-cohort-sha256", sha(world["cfile"]), "--test-mode-repeats", "1",
            "--reference-features", world["ffile"], "--expected-reference-features-sha256", sha(world["ffile"]))
    assert r.returncode == 0, r.stderr + r.stdout
    v = verdict(tmp_path / "s2", "stage2")
    assert v["reference_features_sha256"] == sha(world["ffile"])
    res = json.loads((tmp_path / "s2" / "analysis" / "results.json").read_text())
    assert isinstance(res["missingness_audit"]["reference_sql_hardness"], dict)
    assert res["inputs"]["reference_features_sha256"] == sha(world["ffile"])
    r = run(GATE, "stage2", "--cohort-dir", world["cdir"], "--construction", out1 / "construction", "--out", tmp_path / "s2x",
            "--expected-cohort-sha256", sha(world["cfile"]), "--test-mode-repeats", "1",
            "--reference-features", world["ffile"], "--expected-reference-features-sha256", "0" * 64)
    assert r.returncode == 1 and "reference-features" in verdict(tmp_path / "s2x", "stage2")["reason"]
