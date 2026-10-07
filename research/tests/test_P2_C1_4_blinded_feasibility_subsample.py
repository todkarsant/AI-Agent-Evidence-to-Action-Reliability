"""Tests for the blinded feasibility check / annotation subsample, and the gate's subsample path (SYNTHETIC only)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
FEAS = REPO / "research" / "cohort" / "p2_c1_4_blinded_feasibility_and_subsample.py"
GEN = REPO / "research" / "cohort" / "generate_P2_C1_4_XW_annotation_packets.py"
GATE = REPO / "research" / "cohort" / "p2_c1_4_post_annotation_gate.py"

_spec = importlib.util.spec_from_file_location("p2c12_syn_feas", REPO / "research" / "P2-C1.2" / "analysis" / "make_synthetic_cohort.py")
SYN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SYN)
_gspec = importlib.util.spec_from_file_location("p2c14_gate_tests_mod", REPO / "research" / "tests" / "test_P2_C1_4_post_annotation_gate.py")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


def build(d: Path, n: int, seed: int, base_rate: float, mutate=None):
    cohort, _, _ = SYN.make(n, seed=seed, signal="xw", base_rate=base_rate)
    if mutate:
        mutate(cohort)
    cdir = d / "cohort"
    (cdir / "lock").mkdir(parents=True)
    cfile = cdir / "P2_C1_4_CONFIRMATORY_ALIGNED_RECORDS.json"
    cfile.write_text(json.dumps(cohort), encoding="utf-8")
    (cdir / "lock" / "P2_C1_4_CONFIRMATORY_COHORT_LOCK.json").write_text(json.dumps({"status": "PASS_IMMUTABLE_COHORT_LOCK"}))
    pdir = d / "packets"
    r = run(GEN, "--cohort", cfile, "--out", pdir, "--expected-count", n)
    assert r.returncode == 0, r.stderr
    return cdir, cfile, pdir


def feas(cfile, pdir, out, expected=None, seed=None):
    args = [FEAS, "--cohort", cfile, "--packets", pdir, "--out", out, "--expected-cohort-sha256", expected or sha(cfile)]
    if seed is not None:
        args += ["--seed", seed]
    return run(*args)


def test_fails_riley_on_small_low_prevalence_cohort(tmp_path):
    cdir, cfile, pdir = build(tmp_path, 300, 7, 0.06)
    r = feas(cfile, pdir, tmp_path / "out")
    assert r.returncode == 0, r.stderr
    v = json.loads((tmp_path / "out" / "FEASIBILITY_VERDICT.json").read_text())
    assert v["verdict"] == "FULL_COHORT_FAILS_RILEY"
    assert not (tmp_path / "out" / "packets").exists()


def test_subsample_drawn_and_no_event_count_disclosed(tmp_path):
    cdir, cfile, pdir = build(tmp_path, 1500, 8, 0.25)
    r = feas(cfile, pdir, tmp_path / "out")
    assert r.returncode == 0, r.stderr
    v = json.loads((tmp_path / "out" / "FEASIBILITY_VERDICT.json").read_text())
    assert v["verdict"] == "SUBSAMPLE_DRAWN"
    assert v["n_sampled_primary"] < v["n_eligible_primary"]
    text = (tmp_path / "out" / "FEASIBILITY_VERDICT.json").read_text() + r.stdout
    for forbidden in ("events", "prevalence", "y_h", "phi"):
        assert f'"{forbidden}' not in text
    rec = json.loads((tmp_path / "out" / "packets" / "SAMPLING_RECORD.json").read_text())
    assert len(rec["sampled_decision_ids"]) == v["n_cases_per_rater"] == rec["n_sampled_primary"] + rec["n_e3e4_added"]
    man = json.loads((tmp_path / "out" / "packets" / "P2_C1_4_XW_PACKET_MANIFEST.json").read_text())
    for k in ("A", "B"):
        p = tmp_path / "out" / "packets" / f"P2_C1_4_XW_RATER_{k}.json"
        assert sha(p) == man["packet_sha256"][k]
        sub = json.loads(p.read_text())
        full = json.loads((pdir / f"P2_C1_4_XW_RATER_{k}.json").read_text())
        order_full = [c["case_id"] for c in full["cases"] if c["case_id"] in set(rec["sampled_decision_ids"])]
        assert [c["case_id"] for c in sub["cases"]] == order_full  # rater's random order preserved
        assert all(c["execution_status"] == "SUCCESS" for c in sub["cases"])


def test_selection_does_not_depend_on_which_cases_have_events(tmp_path):
    def shuffle_outcomes(cohort):
        ev = [r for r in cohort["records"] if r["record_status"] == "EVALUABLE" and r["intervention_outcome"]["y_h"] is not None]
        ys = [r["intervention_outcome"]["y_h"] for r in ev]
        random.Random(99).shuffle(ys)
        for r, y in zip(ev, ys):
            r["intervention_outcome"]["y_h"] = y
    out = {}
    for name, mut in (("orig", None), ("shuffled", shuffle_outcomes)):
        d = tmp_path / name
        cdir, cfile, pdir = build(d, 1500, 8, 0.25, mutate=mut)
        assert feas(cfile, pdir, d / "out").returncode == 0
        out[name] = json.loads((d / "out" / "packets" / "SAMPLING_RECORD.json").read_text())["sampled_decision_ids"]
    assert out["orig"] == out["shuffled"]


def test_refuses_wrong_cohort_hash(tmp_path):
    cdir, cfile, pdir = build(tmp_path, 300, 9, 0.25)
    r = feas(cfile, pdir, tmp_path / "out", expected="0" * 64)
    assert r.returncode != 0 and "REFUSED" in r.stderr


def test_gate_chain_with_subsample(tmp_path):
    gate_tests = importlib.util.module_from_spec(_gspec)
    _gspec.loader.exec_module(gate_tests)
    cdir, cfile, pdir = build(tmp_path, 1500, 8, 0.25)
    assert feas(cfile, pdir, tmp_path / "f").returncode == 0
    spk = tmp_path / "f" / "packets"
    rdir = tmp_path / "responses"
    rdir.mkdir()
    for k, s in (("A", 1), ("B", 2)):
        exp = gate_tests.simulate_export(spk / f"P2_C1_4_XW_RATER_{k}.json", f"Synthetic rater {k}", s)
        (rdir / f"P2_C1_4_XW_RESPONSES_RATER_{k}_FINAL.json").write_text(json.dumps(exp), encoding="utf-8")
    r = run(GATE, "stage1", "--packets", spk, "--responses", rdir, "--out", tmp_path / "s1")
    assert r.returncode == 0, r.stderr + r.stdout
    v1 = json.loads((tmp_path / "s1" / "STAGE1_VERDICT.json").read_text())
    assert v1["sampling_record_sha256"] == sha(spk / "SAMPLING_RECORD.json")
    assert (tmp_path / "s1" / "SAMPLING_RECORD.json").is_file()
    r = run(GATE, "stage2", "--cohort-dir", cdir, "--construction", tmp_path / "s1" / "construction", "--out", tmp_path / "s2",
            "--expected-cohort-sha256", sha(cfile), "--test-mode-repeats", "1",
            "--sampling-record", tmp_path / "s1" / "SAMPLING_RECORD.json")
    assert r.returncode == 0, r.stderr + r.stdout
    v2 = json.loads((tmp_path / "s2" / "STAGE2_VERDICT.json").read_text())
    assert v2["status"] == "ANALYSIS_EXECUTED"
    full = json.loads((tmp_path / "s2" / "P2_C1_4_XW_FULL_COHORT.json").read_text())
    rec = json.loads((spk / "SAMPLING_RECORD.json").read_text())
    assert len(full["records"]) == 1500
    assert sum(1 for x in full["records"] if x["decision_id"] not in set(rec["sampled_decision_ids"]) and x["x_w"] is not None) == 0
    res = json.loads((tmp_path / "s2" / "analysis" / "results.json").read_text())
    assert res["population_counts"]["primary"]["n"] <= rec["n_sampled_primary"]
