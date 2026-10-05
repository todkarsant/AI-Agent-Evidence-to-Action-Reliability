"""Tests for research/cohort/reference_sql_features_P2_C1_4.py.

Requires the pinned official Spider evaluator (taoyds/spider @ b7b5b8c) and NLTK punkt_tab, as in
the acquisition workflow. Set SPIDER_EVAL_DIR to the evaluator checkout; skipped if it is absent.
"""
from __future__ import annotations

import csv
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO / "research" / "cohort" / "reference_sql_features_P2_C1_4.py"
SPIDER = Path(os.environ.get("SPIDER_EVAL_DIR", REPO / "external" / "spider"))

pytestmark = pytest.mark.skipif(not (SPIDER / "evaluation.py").is_file(), reason="pinned Spider evaluator not available")

CASES = [
    # (question, gold SQL, expected hardness, expected nesting depth)
    ("q easy", "SELECT name FROM singer", "easy", 0),
    ("q medium", "SELECT name, age FROM singer WHERE age > 20", "medium", 0),
    ("q extra", "SELECT name FROM singer WHERE age > 20 AND name LIKE 'a%' GROUP BY name HAVING count(*) > 1 ORDER BY name LIMIT 3", "extra", 0),
    ("q nested", "SELECT name FROM singer WHERE age > (SELECT avg(age) FROM singer)", "hard", 1),
    ("q double nested", "SELECT name FROM singer WHERE singer_id IN (SELECT singer_id FROM concert WHERE year > (SELECT avg(year) FROM concert))", None, 2),
    ("q union", "SELECT name FROM singer WHERE age > 30 UNION SELECT name FROM singer WHERE age < 20", None, 1),
    ("q from-subquery", "SELECT count(*) FROM (SELECT singer_id FROM concert GROUP BY singer_id)", None, 1),
    ("q unparseable", "SELECT nosuchcolumn FROM singer", None, None),
]


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    d = tmp_path_factory.mktemp("feat")
    db = d / "database" / "toy" / "toy.sqlite"
    db.parent.mkdir(parents=True)
    con = sqlite3.connect(db)
    con.executescript("CREATE TABLE singer(singer_id int primary key, name text, age int);"
                      "CREATE TABLE concert(concert_id int primary key, singer_id int, year int,"
                      " FOREIGN KEY(singer_id) REFERENCES singer(singer_id));")
    con.close()
    manifest = {"case_count": len(CASES), "cases": [
        {"decision_id": f"P2C14-CONF-{i:06d}", "db_id": "toy", "question": q} for i, (q, *_rest) in enumerate(CASES, 1)]}
    (d / "manifest.json").write_text(json.dumps(manifest))
    (d / "questions.json").write_text(json.dumps([{"db_id": "toy", "question": q, "query": s} for q, s, *_r in CASES]))
    r = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(d / "manifest.json"),
                        "--questions", str(d / "questions.json"), "--database-dir", str(d / "database"),
                        "--spider-eval-dir", str(SPIDER), "--output", str(d / "f.csv"), "--summary", str(d / "s.json")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rows = {row["decision_id"]: row for row in csv.DictReader(open(d / "f.csv"))}
    return rows, json.loads((d / "s.json").read_text())


def test_hardness_and_depth(run):
    rows, _ = run
    for i, (q, _s, hard, depth) in enumerate(CASES, 1):
        did = f"P2C14-CONF-{i:06d}"
        if depth is None:
            assert did not in rows
            continue
        assert int(rows[did]["nesting_depth"]) == depth, q
        assert rows[did]["hardness"] in ("easy", "medium", "hard", "extra")
        if hard is not None:
            assert rows[did]["hardness"] == hard, q


def test_summary_and_unparseable(run):
    rows, s = run
    assert s["features_written"] == len(rows) == len(CASES) - 1
    assert s["unparseable_count"] == 1 and s["unparseable"][0]["decision_id"] == f"P2C14-CONF-{len(CASES):06d}"
    assert s["outcomes_accessed"] is False


def test_csv_is_readable_by_the_frozen_analysis(run, tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("p2c12_a_feat", REPO / "research" / "P2-C1.2" / "analysis" / "run_P2_C1_2_confirmatory_analysis.py")
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    rows, _ = run
    p = tmp_path / "f.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["decision_id", "hardness", "nesting_depth"])
        for r in rows.values():
            w.writerow([r["decision_id"], r["hardness"], r["nesting_depth"]])
    feats = A.load_reference_features(str(p))
    assert len(feats) == len(rows)
