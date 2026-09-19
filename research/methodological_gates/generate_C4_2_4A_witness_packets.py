#!/usr/bin/env python3
"""Generate the frozen C4.2.4-A W1-W7 blinded annotation cohort.

Inputs:
  --evidence audited C.4.2.3-D evidence_capture_pilot12.json
  --spider-zip pinned Spider archive
  --manifest frozen 12-case manifest

The generator intentionally never reads or serializes generated SQL, reference SQL,
reference answers, correctness labels, intervention/outcome labels, or runtime telemetry.
"""
import argparse, hashlib, json, random, zipfile
from pathlib import Path

SEEDS = {"A": 424241, "B": 424242}
VERSION = "C4_2_4A_WITNESS_V2_2026-09-19"
FORBIDDEN_KEYS = {
    "generated_sql", "gold_sql", "gold_answer", "p0_correctness",
    "intervention", "replacement", "downstream_outcome", "post_hoc",
    "sql_sha256", "evidence_sha256", "latency_ms", "llm_calls", "cost",
}
SQL_PATTERNS = ("SELECT ", "INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ", "CREATE ")

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def schema_map(spider_zip, wanted):
    with zipfile.ZipFile(spider_zip) as z:
        tables = json.loads(z.read("spider_data/tables.json"))
    out = {}
    for db in tables:
        if db["db_id"] not in wanted:
            continue
        lines = []
        for ti, table in enumerate(db["table_names_original"]):
            cols = [c[1] for c in db["column_names_original"] if c[0] == ti]
            lines.append("TABLE " + table + ": " + ", ".join(cols))
        out[db["db_id"]] = "\n".join(lines)
    if set(out) != set(wanted):
        raise AssertionError("Schema coverage mismatch")
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--spider-zip", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    evidence = json.loads(Path(args.evidence).read_text())
    manifest = json.loads(Path(args.manifest).read_text())
    manifest_cases = {c["db_id"]: c for c in manifest["cases"]}
    first = {x["trace"]["db_id"]: x for x in evidence["first"]}
    if set(manifest_cases) != set(first) or len(first) != 12:
        raise AssertionError("Manifest/evidence coverage mismatch")

    schemas = schema_map(args.spider_zip, set(manifest_cases))
    source_hash = sha256(args.evidence)
    base = []

    for db_id, case in manifest_cases.items():
        captured = first[db_id]["captured_evidence"]
        row_count = captured["row_count"]
        usable = row_count is not None
        item = {
            "case_id": case["pilot_case_id"],
            "db_id": db_id,
            "question": case["question"],
            "schema": schemas[db_id],
            "execution_status": "SUCCESS" if usable else "NO_USABLE_EVIDENCE",
            "columns": captured["columns"] if usable else [],
            "rows": captured["rows"] if usable else [],
            "row_count": row_count,
            "column_count": captured["column_count"],
            "annotations": {"W1": None, "W2": None, "W3": None, "W4": None,
                            "W5": None, "W6": None, "W7": None, "notes": None},
        }
        base.append(item)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    packet_hashes = {}

    for label, seed in SEEDS.items():
        cases = json.loads(json.dumps(base))
        random.Random(seed).shuffle(cases)
        packet = {
            "packet_version": VERSION,
            "rater_packet": label,
            "randomization_seed": seed,
            "source_artifact_sha256": source_hash,
            "source_case_count": 12,
            "blinding": {
                "excluded_information":
                    "No generated query text, reference query/answer, correctness labels, "
                    "intervention/outcome variables, post-hoc labels, execution provenance "
                    "hashes, or model/runtime telemetry are exposed."
            },
            "cases": cases,
        }
        raw = json.dumps(packet, indent=2, sort_keys=True) + "\n"
        upper = raw.upper()
        if any(p in upper for p in SQL_PATTERNS):
            raise AssertionError("SQL statement text detected")
        for forbidden in FORBIDDEN_KEYS:
            if forbidden in raw:
                raise AssertionError("Forbidden metadata detected: " + forbidden)
        if len(cases) != 12 or len({c["case_id"] for c in cases}) != 12:
            raise AssertionError("Case uniqueness failure")
        target = out / f"C4_2_4A_WITNESS_V2_RATER_{label}.json"
        target.write_text(raw)
        packet_hashes[label] = sha256(target)

    record = {
        "packet_version": VERSION,
        "source_evidence_sha256": source_hash,
        "rater_A_seed": SEEDS["A"],
        "rater_B_seed": SEEDS["B"],
        "packet_sha256": packet_hashes,
    }
    (out / "C4_2_4A_WITNESS_V2_PACKET_MANIFEST.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(record, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
