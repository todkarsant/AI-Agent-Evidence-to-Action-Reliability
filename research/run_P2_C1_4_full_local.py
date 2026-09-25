#!/usr/bin/env python3
"""
P2-C1.4 Confirmatory V1 Runtime3 full local acquisition orchestrator.

- Uses the frozen 8,638-case / 44-shard manifest.
- Reuses an already completed shard when aligned_records.json exists
  and passes validation.
- Uses the actual validator CLI:
      validate_P2_C1_4_aligned_records.py <records>
- Performs exact shard/manifest reconciliation before consolidation.
- Performs final consolidated validation.
- Runs the forensic immutable cohort lock.
- Fails closed on count/order/duplicate/provenance mismatches.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path


PROTOCOL = "P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21"
EXPECTED_RECORDS = 8638
EXPECTED_SHARDS = 44
SHARD_SIZE = 200

PARENT_MANIFEST_SHA256 = (
    "f17c30d7aa7c46220febfbbd81b6ac8c0e5b9546e6fc2693eac4c953e04e1894"
)

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT.parent / ".venv312" / "Scripts" / "python.exe"

QUESTIONS = ROOT / "data" / "confirmatory_questions_source.json"
DATABASE_DIR = ROOT / "data" / "database"
TABLES_FILE = ROOT / "data" / "tables.json"
SPIDER_DIR = ROOT / "external" / "spider"

PARENT_MANIFEST = (
    ROOT / "data" / "manifests" / "P2_C1_4_CONFIRMATORY_MANIFEST.json"
)

COLLECTOR = ROOT / "research" / "cohort" / "collect_P2_C1_4_aligned_cohort.py"
VALIDATOR = ROOT / "research" / "cohort" / "validate_P2_C1_4_aligned_records.py"
FORENSIC_LOCK = ROOT / "research" / "cohort" / "forensic_lock_audit_P2_C1_4.py"

ARTIFACT_ROOT = ROOT / "artifacts" / "cohort_confirmatory_runtime3_full"
SHARD_MANIFEST_DIR = ARTIFACT_ROOT / "shards"
CONSOLIDATED_DIR = ARTIFACT_ROOT / "consolidated"
LOCK_DIR = ARTIFACT_ROOT / "forensic_lock"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def run_command(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("COMMAND:")
    print(" ".join(str(x) for x in cmd))
    print()
    result = subprocess.run(cmd, cwd=str(ROOT), env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}")


def verify_file(path: Path, label: str) -> None:
    if not path.exists():
        raise RuntimeError(f"{label} missing: {path}")
    if path.stat().st_size == 0:
        raise RuntimeError(f"{label} is empty: {path}")


def verify_environment() -> dict[str, str]:
    required = {
        "PROJECT1_ROOT": os.environ.get("PROJECT1_ROOT"),
        "PYTHONPATH": os.environ.get("PYTHONPATH"),
        "LLM_PROVIDER": os.environ.get("LLM_PROVIDER"),
        "OLLAMA_BASE_URL": os.environ.get("OLLAMA_BASE_URL"),
        "OLLAMA_MODEL": os.environ.get("OLLAMA_MODEL"),
        "P2_C1_4_PROTOCOL_FROZEN": os.environ.get("P2_C1_4_PROTOCOL_FROZEN"),
    }

    for key, value in required.items():
        if not value:
            raise RuntimeError(f"Required environment variable missing: {key}")

    if required["LLM_PROVIDER"].lower() != "ollama":
        raise RuntimeError("REFUSED: LLM_PROVIDER must be 'ollama'.")

    if required["OLLAMA_MODEL"] != "llama3.2:1b":
        raise RuntimeError(
            "REFUSED: unexpected Ollama model: "
            + required["OLLAMA_MODEL"]
        )

    if required["P2_C1_4_PROTOCOL_FROZEN"] != PROTOCOL:
        raise RuntimeError("REFUSED: frozen protocol environment mismatch.")

    return dict(os.environ)


def verify_parent_manifest() -> dict:
    verify_file(PARENT_MANIFEST, "Parent manifest")
    actual_sha = sha256_file(PARENT_MANIFEST)

    if actual_sha != PARENT_MANIFEST_SHA256:
        raise RuntimeError(
            "FATAL: frozen parent manifest SHA256 mismatch.\n"
            f"Expected: {PARENT_MANIFEST_SHA256}\n"
            f"Actual:   {actual_sha}"
        )

    manifest = load_json(PARENT_MANIFEST)

    if manifest.get("confirmatory") is not True:
        raise RuntimeError("FATAL: parent manifest is not confirmatory.")

    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise RuntimeError("FATAL: parent manifest cases is not a list.")

    if len(cases) != EXPECTED_RECORDS:
        raise RuntimeError(
            f"FATAL: expected {EXPECTED_RECORDS} cases, found {len(cases)}."
        )

    decision_ids = [c.get("decision_id") for c in cases]

    if any(not x for x in decision_ids):
        raise RuntimeError("FATAL: missing decision_id in parent manifest.")

    if len(decision_ids) != len(set(decision_ids)):
        raise RuntimeError("FATAL: duplicate decision_id in parent manifest.")

    if decision_ids[0] != "P2C14-CONF-000001":
        raise RuntimeError("FATAL: unexpected first decision_id.")

    if decision_ids[-1] != "P2C14-CONF-008638":
        raise RuntimeError("FATAL: unexpected last decision_id.")

    print(f"PASS: {len(cases)} frozen cases")
    print(f"PASS: manifest SHA256 {actual_sha}")
    print(f"FIRST: {decision_ids[0]}")
    print(f"LAST : {decision_ids[-1]}")
    return manifest


def create_shard_manifests(manifest: dict) -> list[Path]:
    SHARD_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    cases = manifest["cases"]
    paths: list[Path] = []

    for shard_index in range(EXPECTED_SHARDS):
        start = shard_index * SHARD_SIZE
        end = min(start + SHARD_SIZE, len(cases))
        shard_cases = cases[start:end]

        if not shard_cases:
            raise RuntimeError(f"FATAL: shard {shard_index:02d} is empty.")

        shard_manifest = {
            "protocol_version": manifest.get("protocol_version", PROTOCOL),
            "confirmatory": True,
            "selection_rule": manifest.get("selection_rule"),
            "source_manifest_sha256": PARENT_MANIFEST_SHA256,
            "shard_index": shard_index,
            "shard_count": EXPECTED_SHARDS,
            "cases": shard_cases,
        }

        path = SHARD_MANIFEST_DIR / f"shard_{shard_index:02d}.json"
        save_json(path, shard_manifest)

        if path.read_bytes().startswith(b"\xef\xbb\xbf"):
            raise RuntimeError(f"FATAL: BOM detected in {path}")

        paths.append(path)

        print(
            f"SHARD {shard_index:02d}: "
            f"{len(shard_cases):3d} cases "
            f"{shard_cases[0]['decision_id']} -> "
            f"{shard_cases[-1]['decision_id']}"
        )

    if len(paths) != EXPECTED_SHARDS:
        raise RuntimeError("FATAL: wrong number of shard manifests.")

    print(f"PASS: {len(paths)} BOM-free shard manifests created")
    return paths


def extract_records(aligned_path: Path) -> list[dict]:
    data = load_json(aligned_path)
    records = data if isinstance(data, list) else data.get("records")

    if not isinstance(records, list):
        raise RuntimeError(f"Invalid aligned-records structure: {aligned_path}")

    return records


def validate_shard(
    shard_index: int,
    shard_manifest_path: Path,
    shard_output_dir: Path,
) -> list[dict]:

    aligned_path = shard_output_dir / "aligned_records.json"
    verify_file(aligned_path, "aligned_records.json")

    # CRITICAL CLI CONTRACT:
    # validate_P2_C1_4_aligned_records.py accepts positional \`records\`.
    cmd = [
        str(PYTHON),
        str(VALIDATOR),
        str(aligned_path),
    ]

    print()
    print("=" * 70)
    print(f"VALIDATE shard_{shard_index:02d}")
    print("=" * 70)
    run_command(cmd)

    records = extract_records(aligned_path)
    shard_manifest = load_json(shard_manifest_path)
    expected_cases = shard_manifest["cases"]

    expected_ids = [c["decision_id"] for c in expected_cases]
    actual_ids = [r.get("decision_id") for r in records]

    if len(records) != len(expected_ids):
        raise RuntimeError(
            f"shard_{shard_index:02d}: count mismatch: "
            f"expected {len(expected_ids)}, got {len(records)}"
        )

    if actual_ids != expected_ids:
        raise RuntimeError(
            f"shard_{shard_index:02d}: decision_id order mismatch."
        )

    if len(actual_ids) != len(set(actual_ids)):
        raise RuntimeError(f"shard_{shard_index:02d}: duplicate decision_id.")

    expected_manifest_hash = sha256_file(shard_manifest_path)

    for record in records:
        if record.get("protocol_version") != "P2-C1.4-ALIGNED-V2":
            raise RuntimeError(
                f"{record.get('decision_id')}: unexpected aligned protocol."
            )

        if record.get("provenance", {}).get("manifest_hash") != expected_manifest_hash:
            raise RuntimeError(
                f"{record.get('decision_id')}: shard manifest provenance hash mismatch."
            )

    print(
        f"PASS: shard_{shard_index:02d} "
        f"{len(records)} records; exact shard order verified"
    )
    return records


def acquire_shard(
    shard_index: int,
    shard_manifest_path: Path,
    shard_output_dir: Path,
    env: dict[str, str],
) -> list[dict]:

    aligned_path = shard_output_dir / "aligned_records.json"

    # Resume: never rerun successful Ollama acquisition unnecessarily.
    if aligned_path.exists():
        print()
        print("#" * 70)
        print(
            f"SHARD {shard_index + 1}/{EXPECTED_SHARDS}: "
            f"shard_{shard_index:02d} [RESUME]"
        )
        print("#" * 70)
        print("Existing aligned_records.json found.")
        print("Skipping Ollama acquisition; validating existing artifact.")

        return validate_shard(
            shard_index,
            shard_manifest_path,
            shard_output_dir,
        )

    print()
    print("#" * 70)
    print(
        f"SHARD {shard_index + 1}/{EXPECTED_SHARDS}: "
        f"shard_{shard_index:02d}"
    )
    print("#" * 70)

    shard_output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(PYTHON),
        str(COLLECTOR),
        "--questions",
        str(QUESTIONS),
        "--database-dir",
        str(DATABASE_DIR),
        "--manifest",
        str(shard_manifest_path),
        "--spider-eval-dir",
        str(SPIDER_DIR),
        "--tables-file",
        str(TABLES_FILE),
        "--outdir",
        str(shard_output_dir),
        "--confirmatory",
    ]

    print()
    print("=" * 70)
    print(f"ACQUIRE shard_{shard_index:02d}")
    print("=" * 70)
    run_command(cmd, env=env)

    verify_file(aligned_path, f"shard_{shard_index:02d} aligned records")

    return validate_shard(
        shard_index,
        shard_manifest_path,
        shard_output_dir,
    )


def consolidate(
    parent_manifest: dict,
    shard_records: list[list[dict]],
) -> Path:

    print()
    print("=" * 70)
    print("4. EXACT SHARD RECONCILIATION")
    print("=" * 70)

    if len(shard_records) != EXPECTED_SHARDS:
        raise RuntimeError(
            f"FATAL: expected {EXPECTED_SHARDS} shard result sets."
        )

    flattened: list[dict] = []

    for index, records in enumerate(shard_records):
        expected_count = (
            SHARD_SIZE
            if index < EXPECTED_SHARDS - 1
            else EXPECTED_RECORDS - SHARD_SIZE * (EXPECTED_SHARDS - 1)
        )

        if len(records) != expected_count:
            raise RuntimeError(
                f"FATAL: shard_{index:02d} expected "
                f"{expected_count}, got {len(records)}."
            )

        flattened.extend(records)

    if len(flattened) != EXPECTED_RECORDS:
        raise RuntimeError(
            f"FATAL: flattened count {len(flattened)} != {EXPECTED_RECORDS}."
        )

    expected_ids = [c["decision_id"] for c in parent_manifest["cases"]]
    actual_ids = [r["decision_id"] for r in flattened]

    if actual_ids != expected_ids:
        raise RuntimeError(
            "FATAL: consolidated decision_id order does not exactly "
            "match the frozen parent manifest."
        )

    if len(actual_ids) != len(set(actual_ids)):
        raise RuntimeError(
            "FATAL: duplicate decision_id in consolidated cohort."
        )

    cohort = {
        "protocol_version": "P2-C1.4-ALIGNED-V2",
        "source_manifest_sha256": PARENT_MANIFEST_SHA256,
        "record_count": len(flattened),
        "records": flattened,
    }

    CONSOLIDATED_DIR.mkdir(parents=True, exist_ok=True)
    consolidated_path = (
        CONSOLIDATED_DIR
        / "P2_C1_4_CONFIRMATORY_ALIGNED_RECORDS.json"
    )

    save_json(consolidated_path, cohort)

    print(f"PASS: {EXPECTED_SHARDS}/{EXPECTED_SHARDS} shards")
    print(f"PASS: {EXPECTED_RECORDS}/{EXPECTED_RECORDS} records")
    print("PASS: exact frozen decision_id ordering")
    print("PASS: no duplicate decision_id")
    print("CONSOLIDATED SHA256:", sha256_file(consolidated_path))

    return consolidated_path


def final_validate(consolidated_path: Path) -> None:
    print()
    print("=" * 70)
    print("5. FINAL CONSOLIDATED VALIDATION")
    print("=" * 70)

    cmd = [
        str(PYTHON),
        str(VALIDATOR),
        str(consolidated_path),
    ]

    run_command(cmd)

    records = extract_records(consolidated_path)

    if len(records) != EXPECTED_RECORDS:
        raise RuntimeError(
            "FATAL: final validator passed but record count is wrong."
        )

    print(
        f"PASS: final consolidated validation {len(records)} records"
    )


def forensic_lock(consolidated_path: Path) -> None:
    print()
    print("=" * 70)
    print("6. FORENSIC IMMUTABLE COHORT LOCK")
    print("=" * 70)

    LOCK_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(PYTHON),
        str(FORENSIC_LOCK),
        "--manifest",
        str(PARENT_MANIFEST),
        "--cohort",
        str(consolidated_path),
        "--outdir",
        str(LOCK_DIR),
    ]

    run_command(cmd)

    lock_path = LOCK_DIR / "P2_C1_4_CONFIRMATORY_COHORT_LOCK.json"
    verify_file(lock_path, "Forensic lock artifact")

    lock = load_json(lock_path)

    if lock.get("status") != "PASS_IMMUTABLE_COHORT_LOCK":
        raise RuntimeError(
            "FATAL: forensic audit did not produce "
            "PASS_IMMUTABLE_COHORT_LOCK."
        )

    if lock.get("record_count") != EXPECTED_RECORDS:
        raise RuntimeError("FATAL: forensic lock record count mismatch.")

    if lock.get("source_manifest_sha256") != PARENT_MANIFEST_SHA256:
        raise RuntimeError("FATAL: forensic lock manifest hash mismatch.")

    print()
    print("==============================================")
    print("P2-C1.4 FORENSIC LOCK: PASS")
    print("==============================================")
    print(f"Records : {lock['record_count']}")
    print(f"Status  : {lock['status']}")
    print(f"Lock SHA: {sha256_file(lock_path)}")


def main() -> int:
    print("=" * 70)
    print("P2-C1.4 CONFIRMATORY V1 RUNTIME3")
    print("FULL LOCAL ACQUISITION")
    print("=" * 70)
    print(f"Protocol : {PROTOCOL}")
    print(f"Records  : {EXPECTED_RECORDS}")
    print(f"Shards   : {EXPECTED_SHARDS}")
    print(f"Python   : {PYTHON}")
    print()

    if not PYTHON.exists():
        raise RuntimeError(f"Python executable missing: {PYTHON}")

    for path, label in [
        (QUESTIONS, "Questions file"),
        (DATABASE_DIR, "Database directory"),
        (TABLES_FILE, "Tables file"),
        (SPIDER_DIR, "Spider evaluator directory"),
        (COLLECTOR, "Collector"),
        (VALIDATOR, "Validator"),
        (FORENSIC_LOCK, "Forensic lock auditor"),
    ]:
        verify_file(path, label)

    print("=" * 70)
    print("1. VERIFY FROZEN PARENT MANIFEST")
    print("=" * 70)
    parent_manifest = verify_parent_manifest()

    print()
    print("=" * 70)
    print("2. CREATE BOM-FREE SHARD MANIFESTS")
    print("=" * 70)
    shard_manifests = create_shard_manifests(parent_manifest)

    print()
    print("=" * 70)
    print("3. CONFIRMATORY ACQUISITION")
    print("=" * 70)
    env = verify_environment()

    all_shard_records: list[list[dict]] = []

    for shard_index, shard_manifest_path in enumerate(shard_manifests):
        shard_output_dir = ARTIFACT_ROOT / f"shard_{shard_index:02d}"

        records = acquire_shard(
            shard_index,
            shard_manifest_path,
            shard_output_dir,
            env,
        )

        all_shard_records.append(records)

    consolidated_path = consolidate(parent_manifest, all_shard_records)
    final_validate(consolidated_path)
    forensic_lock(consolidated_path)

    print()
    print("=" * 70)
    print("P2-C1.4 FULL LOCAL ACQUISITION COMPLETE")
    print("=" * 70)
    print()
    print("8,638 / 8,638 records acquired and reconciled.")
    print("44 / 44 shards validated.")
    print("Forensic immutable cohort lock: PASS.")
    print()
    print("NO X_W annotation was performed by this collector.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nSTOP: interrupted by user.")
        raise SystemExit(130)
    except Exception as exc:
        print()
        print("=" * 70)
        print("FATAL: P2-C1.4 ORCHESTRATOR STOPPED")
        print("=" * 70)
        print(str(exc))
        raise SystemExit(1)
