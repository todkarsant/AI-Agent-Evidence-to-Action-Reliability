"""Tests for the findings renderer and the evidence-availability audit (SYNTHETIC data only)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
RENDER = REPO / "research" / "cohort" / "render_P2_C1_4_findings.py"
AUDIT = REPO / "research" / "cohort" / "p2_c1_4_evidence_availability_audit.py"
_fspec = importlib.util.spec_from_file_location("p2c14_feas_tests_mod", REPO / "research" / "tests" / "test_P2_C1_4_blinded_feasibility_subsample.py")


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


@pytest.fixture(scope="module")
def chain(tmp_path_factory):
    t = importlib.util.module_from_spec(_fspec)
    _fspec.loader.exec_module(t)
    g = importlib.util.module_from_spec(t._gspec)
    t._gspec.loader.exec_module(g)
    d = tmp_path_factory.mktemp("chain")
    cdir, cfile, pdir = t.build(d, 1500, 8, 0.25)
    assert t.feas(cfile, pdir, d / "f").returncode == 0
    spk = d / "f" / "packets"
    rdir = d / "responses"
    rdir.mkdir()
    for k, s in (("A", 1), ("B", 2)):
        exp = g.simulate_export(spk / f"P2_C1_4_XW_RATER_{k}.json", f"Synthetic rater {k}", s)
        (rdir / f"P2_C1_4_XW_RESPONSES_RATER_{k}_FINAL.json").write_text(json.dumps(exp), encoding="utf-8")
    assert run(t.GATE, "stage1", "--packets", spk, "--responses", rdir, "--out", d / "s1").returncode == 0
    r = run(t.GATE, "stage2", "--cohort-dir", cdir, "--construction", d / "s1" / "construction", "--out", d / "s2",
            "--expected-cohort-sha256", t.sha(cfile), "--test-mode-repeats", "1",
            "--sampling-record", d / "s1" / "SAMPLING_RECORD.json")
    assert r.returncode == 0, r.stderr
    return d, pdir


def test_audit_reads_packet_only(chain, tmp_path):
    _, pdir = chain
    out = tmp_path / "a.json"
    r = run(AUDIT, "--packet", pdir / "P2_C1_4_XW_RATER_A.json", "--out", out)
    assert r.returncode == 0, r.stderr
    a = json.loads(out.read_text())
    assert a["outcome_fields_used"] == []
    assert sum(a["counts"].values()) == a["n_decisions"] == 1500


def test_render_marks_synthetic_and_fills_sections(chain, tmp_path):
    d, pdir = chain
    aud = tmp_path / "a.json"
    assert run(AUDIT, "--packet", pdir / "P2_C1_4_XW_RATER_A.json", "--out", aud).returncode == 0
    r = run(RENDER, "--stage1", d / "s1", "--stage2", d / "s2", "--out", tmp_path / "fd", "--evidence-availability", aud)
    assert r.returncode == 0, r.stderr
    md = (tmp_path / "fd" / "P2_C1_4_FINDINGS.md").read_text()
    assert "NOT A FINDING" in md
    for sec in ("9.3.1", "9.3.2", "9.3.3", "9.3.4", "9.3.5", "9.3.6", "Claim boundary", "Evidence availability"):
        assert sec in md
    s = json.loads((tmp_path / "fd" / "P2_C1_4_FINDINGS.json").read_text())
    res = json.loads((d / "s2" / "analysis" / "results.json").read_text())
    assert s["delta_logloss"]["primary"] == res["analyses"]["primary"]["delta_logloss"]
    assert s["test_or_synthetic"] is True


def test_render_refuses_tampered_results(chain, tmp_path):
    d, _ = chain
    import shutil
    s2 = tmp_path / "s2"
    shutil.copytree(d / "s2", s2)
    p = s2 / "analysis" / "results.json"
    res = json.loads(p.read_text())
    res["analyses"]["primary"]["delta_logloss"] = 0.5
    p.write_text(json.dumps(res))
    r = run(RENDER, "--stage1", d / "s1", "--stage2", s2, "--out", tmp_path / "fd")
    assert r.returncode != 0 and "REFUSED" in r.stderr


def test_render_riley_hard_stop(tmp_path):
    t = importlib.util.module_from_spec(_fspec)
    _fspec.loader.exec_module(t)
    g = importlib.util.module_from_spec(t._gspec)
    t._gspec.loader.exec_module(g)
    cdir, cfile, pdir = t.build(tmp_path, 300, 7, 0.06)
    rdir = tmp_path / "responses"
    rdir.mkdir()
    for k, s in (("A", 1), ("B", 2)):
        exp = g.simulate_export(pdir / f"P2_C1_4_XW_RATER_{k}.json", f"Synthetic rater {k}", s)
        (rdir / f"P2_C1_4_XW_RESPONSES_RATER_{k}_FINAL.json").write_text(json.dumps(exp), encoding="utf-8")
    assert run(t.GATE, "stage1", "--packets", pdir, "--responses", rdir, "--out", tmp_path / "s1").returncode == 0
    assert run(t.GATE, "stage2", "--cohort-dir", cdir, "--construction", tmp_path / "s1" / "construction",
               "--out", tmp_path / "s2", "--expected-cohort-sha256", t.sha(cfile), "--test-mode-repeats", "1").returncode == 0
    r = run(RENDER, "--stage1", tmp_path / "s1", "--stage2", tmp_path / "s2", "--out", tmp_path / "fd")
    assert r.returncode == 0, r.stderr
    md = (tmp_path / "fd" / "P2_C1_4_FINDINGS.md").read_text()
    assert "FEASIBILITY_STOP_RILEY" in md and "Not estimated" in md
    assert json.loads((tmp_path / "fd" / "P2_C1_4_FINDINGS.json").read_text())["delta_logloss"]["primary"] is None
