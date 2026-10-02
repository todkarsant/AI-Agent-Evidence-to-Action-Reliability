"""Tests for research/P2-C1.2/analysis/run_P2_C1_2_confirmatory_analysis.py (SYNTHETIC data only)."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.join(os.path.dirname(HERE), "P2-C1.2", "analysis")


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ANALYSIS_DIR, fname))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


A = _load("p2c12_analysis", "run_P2_C1_2_confirmatory_analysis.py")
SYN = _load("p2c12_synthetic", "make_synthetic_cohort.py")

REPEATS = 2  # test-mode override only


def _write(tmp, cohort, xw, ref=None):
    paths = SYN.write(str(tmp), cohort, xw, ref or [])
    if ref is None:
        paths["ref"] = None
    return paths


def _run(paths, out, repeats=REPEATS, extra=()):
    argv = ["--cohort", paths["cohort"], "--xw", paths["xw"], "--out", str(out), "--test-mode", "--repeats", str(repeats)]
    if paths.get("ref"):
        argv += ["--reference-features", paths["ref"]]
    return A.main(argv + list(extra))


@pytest.fixture(scope="module")
def null_runs(tmp_path_factory):
    d = tmp_path_factory.mktemp("null")
    paths = _write(d / "in", *SYN.make(600, seed=11, signal="none", base_rate=0.25))
    c1 = _run(paths, d / "out1")
    c2 = _run(paths, d / "out2")
    return paths, d / "out1", d / "out2", c1, c2


@pytest.fixture(scope="module")
def signal_run(tmp_path_factory):
    d = tmp_path_factory.mktemp("signal")
    paths = _write(d / "in", *SYN.make(600, seed=12, signal="xw", base_rate=0.25))
    code = _run(paths, d / "out")
    return paths, d / "out", code


def _results(out):
    with open(os.path.join(out, "results.json"), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- determinism
def test_determinism_byte_identical(null_runs):
    _, o1, o2, c1, c2 = null_runs
    assert c1 == c2 == 0
    for f in ["results.json", "summary.md"] + [f"per_case_logloss_differences_{p}.csv" for p in ("primary", "S1", "S2_low", "S2_high")]:
        with open(os.path.join(o1, f), "rb") as a, open(os.path.join(o2, f), "rb") as b:
            assert a.read() == b.read(), f
    assert os.path.exists(os.path.join(o1, "run_metadata.json"))
    assert "run_timestamp_utc" not in open(os.path.join(o1, "results.json")).read()


def test_outputs_record_hashes_versions_seeds_testmode(null_runs):
    paths, o1, *_ = null_runs
    r = _results(o1)
    assert r["inputs"]["cohort_sha256"] == A.sha256_file(paths["cohort"])
    assert r["inputs"]["xw_sha256"] == A.sha256_file(paths["xw"])
    assert r["test_mode"] is True and r["input_marked_synthetic"] is True
    assert r["frozen_parameters"]["outer_seeds"] == [20261001, 20261002]
    assert r["frozen_parameters"]["C_grid"] == [0.01, 0.1, 1.0, 10.0, 100.0]
    assert r["package_versions"]["scikit-learn"]
    a = r["analyses"]["primary"]
    assert a["n_outer_predictions"] == REPEATS * r["population_counts"]["primary"]["n"]
    assert np.isclose(a["delta_logloss"], np.mean(a["delta_logloss_by_repeat"]))
    lo, hi = a["delta_logloss_repeat_percentile_interval_95"]
    assert lo <= hi


def test_per_case_csv_consistent(null_runs):
    _, o1, *_ = null_runs
    import csv
    rows = list(csv.DictReader(open(os.path.join(o1, "per_case_logloss_differences_primary.csv"))))
    r = _results(o1)
    assert len(rows) == r["analyses"]["primary"]["n_outer_predictions"]
    for row in rows[:50]:
        y, p0, p1 = int(row["y"]), float(row["p0"]), float(row["p1"])
        ll = lambda p: -(y * np.log(p) + (1 - y) * np.log(1 - p))
        assert np.isclose(ll(p0) - ll(p1), float(row["d"]))
    d = np.array([float(x["d"]) for x in rows])
    assert np.isclose(d.mean(), r["analyses"]["primary"]["delta_logloss"])


# ---------------------------------------------------------------- CLI guard
def test_repeats_override_refused_without_test_mode(tmp_path):
    paths = _write(tmp_path / "in", *SYN.make(60, seed=3))
    code = A.main(["--cohort", paths["cohort"], "--xw", paths["xw"], "--out", str(tmp_path / "o"), "--repeats", "2"])
    assert code == A.EXIT_INPUT_INVALID
    code = A.main(["--cohort", paths["cohort"], "--xw", paths["xw"], "--out", str(tmp_path / "o"), "--repeats", "20"])
    assert code == A.EXIT_INPUT_INVALID
    assert not os.path.exists(tmp_path / "o" / "results.json")


# ---------------------------------------------------------------- fail closed
def _expect_fail(tmp_path, cohort, xw, extra=()):
    paths = _write(tmp_path / "in", cohort, xw)
    code = _run(paths, tmp_path / "out", repeats=1, extra=extra)
    assert code == A.EXIT_INPUT_INVALID
    assert not os.path.exists(tmp_path / "out" / "results.json")


def test_fail_closed_mismatched_decision_ids(tmp_path):
    c, x, _ = SYN.make(80, seed=4)
    x2 = copy.deepcopy(x)
    x2["records"][0]["decision_id"] = "SYN-NOT-IN-COHORT"
    _expect_fail(tmp_path / "a", c, x2)
    x3 = copy.deepcopy(x)
    x3["records"].pop()
    _expect_fail(tmp_path / "b", c, x3)
    x4 = copy.deepcopy(x)
    x4["records"].append(dict(x4["records"][0]))
    _expect_fail(tmp_path / "c", c, x4)


@pytest.mark.parametrize("bad", [1.0000001, -0.01, float("nan"), "0.5", True])
def test_fail_closed_out_of_range_xw(tmp_path, bad):
    c, x, _ = SYN.make(80, seed=5)
    i = next(k for k, r in enumerate(c["records"]) if r["record_status"] == "EVALUABLE")
    x["records"][i]["x_w"] = bad
    _expect_fail(tmp_path, c, x)


def test_fail_closed_sha_check(tmp_path):
    c, x, _ = SYN.make(80, seed=6)
    _expect_fail(tmp_path, c, x, extra=["--sha-check", "0" * 64, "0" * 64])


def test_fail_closed_other_integrity(tmp_path):
    c, x, _ = SYN.make(80, seed=7)
    c2 = copy.deepcopy(c)
    c2["protocol_version"] = "P2-C1.4-ALIGNED-V1"
    _expect_fail(tmp_path / "a", c2, x)
    c3 = copy.deepcopy(c)
    e34 = next(r for r in c3["records"] if r["record_status"] == A.STATUS_E3E4)
    e34["intervention_outcome"]["y_h"] = 1
    _expect_fail(tmp_path / "b", c3, x)


# ---------------------------------------------------------------- null / signal behaviour
def test_null_xw_gives_delta_near_zero():
    deltas = []
    for seed in (21, 22, 23):
        c, x, _ = SYN.make(600, seed=seed, signal="none")
        recs, xm = A.validate_inputs(c, x)
        pops, _ = A.build_populations(recs, xm)
        plan, why = A.build_partitions(pops["primary"], 1)
        assert why is None
        res, _ = A.analyze_population(pops["primary"], plan)
        deltas.append(res["delta_logloss"])
    assert all(abs(d) < 0.01 for d in deltas), deltas
    assert np.mean(deltas) < 0.003, deltas  # not systematically positive


def test_null_run_primary_small(null_runs):
    r = _results(null_runs[1])
    assert abs(r["analyses"]["primary"]["delta_logloss"]) < 0.01


def test_signal_xw_gives_positive_delta(signal_run):
    _, out, code = signal_run
    assert code == 0
    r = _results(out)
    a = r["analyses"]["primary"]
    assert a["delta_logloss"] > 0.02
    assert a["delta_logloss_repeat_percentile_interval_95"][0] > 0
    assert r["verdicts"]["robustness"]["flag"] == "ROBUST"
    assert a["models"]["M1"]["auroc"]["mean"] > a["models"]["M0"]["auroc"]["mean"]


# ---------------------------------------------------------------- populations
def test_s1_s2_population_counts(signal_run):
    paths, out, _ = signal_run
    c = json.load(open(paths["cohort"]))
    x = {e["decision_id"]: e["x_w"] for e in json.load(open(paths["xw"]))["records"]}
    recs = c["records"]
    prim = [r for r in recs if r["record_status"] == "EVALUABLE" and x[r["decision_id"]] is not None and r["intervention_outcome"]["y_h"] is not None]
    e3 = [r for r in recs if r["record_status"] == A.STATUS_E3E4 and x[r["decision_id"]] is not None and r["intervention_outcome"]["y_h_implied_by_definition"] == 0]
    e4 = [r for r in recs if r["record_status"] == A.STATUS_E3E4 and x[r["decision_id"]] is not None and r["intervention_outcome"]["p0_correct"] is True]
    ev = sum(r["intervention_outcome"]["y_h"] for r in prim)
    assert len(e3) > 0 and len(e4) > 0
    pc = _results(out)["population_counts"]
    assert (pc["primary"]["n"], pc["primary"]["events"]) == (len(prim), ev)
    assert (pc["S1"]["n"], pc["S1"]["events"]) == (len(prim) + len(e3), ev)
    assert (pc["S2_low"]["n"], pc["S2_low"]["events"]) == (len(prim) + len(e3) + len(e4), ev)
    assert (pc["S2_high"]["n"], pc["S2_high"]["events"]) == (len(prim) + len(e3) + len(e4), ev + len(e4))
    flow = _results(out)["cohort_flow"]
    assert sum(flow["status_counts"].values()) == len(recs)


def test_groups_never_cross_outer_folds():
    c, x, _ = SYN.make(600, seed=31, p_dup_group=0.3)
    recs, xm = A.validate_inputs(c, x)
    pops, _ = A.build_populations(recs, xm)
    p = pops["primary"]
    assert len(set(p.groups.tolist())) < p.n  # duplicates present
    plan, why = A.build_partitions(p, 3)
    assert why is None
    for rep in plan:
        for f in rep["folds"]:
            assert not set(p.groups[f["train"]].tolist()) & set(p.groups[f["test"]].tolist())
            for itr, ite in f["inner"]:
                assert not set(p.groups[itr].tolist()) & set(p.groups[ite].tolist())
                assert set(itr.tolist()) | set(ite.tolist()) == set(f["train"].tolist())


# ---------------------------------------------------------------- feasibility
def test_feasibility_stop_when_too_few_events(tmp_path):
    paths = _write(tmp_path / "in", *SYN.make(300, seed=41, max_events=3))
    code = _run(paths, tmp_path / "out")
    assert code == A.EXIT_FEASIBILITY_STOP
    r = _results(tmp_path / "out")
    assert r["population_counts"]["primary"]["events"] == 3
    assert r["verdicts"]["primary"] == "FEASIBILITY_STOP"
    assert r["feasibility"]["per_population"]["primary"] == "FEASIBILITY_STOP"
    assert all(v["status"] == "NOT_RUN_PRIMARY_FEASIBILITY_STOP" for v in r["analyses"].values())
    assert not any(f.startswith("per_case") for f in os.listdir(tmp_path / "out"))
    assert r["riley_2020"]["verdict"] == "RILEY_CRITERIA_NOT_MET"


def test_riley_quantities():
    q = A.riley_quantities(1000, 500)
    assert q["criterion_iii_min_n"] == 385  # (1.96/0.05)^2 * 0.25 = 384.16
    phi = 0.0636
    mx = 1 - (phi ** phi * (1 - phi) ** (1 - phi)) ** 2
    r2 = 0.15 * mx
    exp_i = 4 / ((0.9 - 1) * np.log(1 - r2 / 0.9))
    q = A.riley_quantities(10000, 636)
    assert np.isclose(q["criterion_i_min_n_unrounded"], exp_i)
    assert q["criterion_i_met"] == (10000 >= q["criterion_i_min_n"])
    assert A.riley_quantities(50, 5)["verdict"] == "RILEY_CRITERIA_NOT_MET"
    assert A.riley_quantities(100, 0)["verdict"] == "RILEY_CRITERIA_NOT_MET"


def test_riley_hard_stop_fits_nothing(tmp_path):
    # folds are mechanically feasible, but the primary population is below Riley criterion (i)
    c, x, ref = SYN.make(600, seed=12, signal="none", base_rate=0.08)
    recs, xm = A.validate_inputs(c, x)
    pops, _ = A.build_populations(recs, xm)
    p = pops["primary"]
    assert A.build_partitions(p, REPEATS)[1] is None
    q = A.riley_quantities(p.n, int(p.y.sum()))
    assert q["verdict"] == "RILEY_CRITERIA_NOT_MET"
    paths = _write(tmp_path / "in", c, x, ref)
    code = _run(paths, tmp_path / "out")
    assert code == A.EXIT_FEASIBILITY_STOP
    r = _results(tmp_path / "out")
    assert r["verdicts"]["primary"] == "FEASIBILITY_STOP_RILEY"
    assert r["verdicts"]["robustness"]["flag"] == "NOT_ASSESSABLE"
    assert r["feasibility"]["per_population"]["primary"] == "FEASIBLE"
    assert all(v["status"] == "NOT_RUN_RILEY_STOP" for v in r["analyses"].values())
    assert not any(f.startswith("per_case") for f in os.listdir(tmp_path / "out"))


def test_riley_met_in_completed_runs(null_runs, signal_run):
    for out in (null_runs[1], signal_run[1]):
        r = _results(out)
        assert r["riley_2020"]["verdict"] == "RILEY_CRITERIA_MET"
        assert r["verdicts"]["primary"] == "ANALYSIS_COMPLETED"


# ---------------------------------------------------------------- missingness audit
class _Poison(dict):
    def __getitem__(self, k):
        raise AssertionError("audit touched an outcome field")

    def get(self, *a, **k):
        raise AssertionError("audit touched an outcome field")

    def __iter__(self):
        raise AssertionError("audit touched an outcome field")


def test_missingness_audit_never_reads_outcome_fields(tmp_path):
    c, x, ref = SYN.make(200, seed=51)
    poisoned = copy.deepcopy(c["records"])
    for r in poisoned:
        r["intervention_outcome"] = _Poison()
        r["baseline"] = _Poison()
    proj = A.pre_outcome_projection(poisoned)
    assert all(set(p) == {"decision_id", "record_status", "database_id", "question"} for p in proj)
    refmap = {row["decision_id"]: {"hardness": row["hardness"], "nesting_depth": row["nesting_depth"]} for row in ref}
    audit_poison = A.missingness_audit(proj, refmap)
    audit_clean = A.missingness_audit(A.pre_outcome_projection(c["records"]), refmap)
    assert audit_poison == audit_clean
    # changing every outcome leaves the audit unchanged
    flipped = copy.deepcopy(c["records"])
    for r in flipped:
        r["intervention_outcome"] = {"y_h": 1, "p0_correct": True}
    assert A.missingness_audit(A.pre_outcome_projection(flipped), refmap) == audit_clean
    assert audit_clean["outcome_fields_used"] == []
    assert set(audit_clean["groups_compared"]) == {"EVALUABLE", "E2", "E3E4"}


def test_missingness_audit_without_reference_features(null_runs):
    r = _results(null_runs[1])
    a = r["missingness_audit"]
    assert a["reference_sql_hardness"] != "NOT_COMPUTED_INPUT_MISSING"
    audit = A.missingness_audit(A.pre_outcome_projection(SYN.make(50, seed=52)[0]["records"]), None)
    assert audit["reference_sql_hardness"] == "NOT_COMPUTED_INPUT_MISSING"
    assert audit["reference_sql_nesting_depth"] == "NOT_COMPUTED_INPUT_MISSING"


# ---------------------------------------------------------------- calibration cross-check
def test_calibration_matches_closed_form_on_perfect_calibration():
    rng = np.random.default_rng(0)
    p = rng.uniform(0.02, 0.6, 20000)
    y = (rng.uniform(size=p.size) < p).astype(int)
    cal = A.calibration(y, p)
    assert cal["error"] is None
    assert abs(cal["slope"] - 1) < 0.1 and abs(cal["intercept"]) < 0.05
