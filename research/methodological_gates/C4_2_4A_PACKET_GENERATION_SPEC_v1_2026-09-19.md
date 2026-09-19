# C.4.2.4-A — Blinded Packet Generation Specification v1

**Status:** FROZEN
**Freeze date:** 2026-09-19

## Inputs

- Frozen 12-case manifest: data/manifests/C4_2_3B_PILOT12_CASES.json
- Audited evidence-capture JSON from C.4.2.3-D
- Official Spider tables.json from the pinned Spider archive
- Frozen witness codebook v2

## Packet contents

Each packet contains only:
- case identifier;
- database identifier;
- natural-language question;
- database schema;
- execution status;
- returned column names;
- returned rows;
- row count;
- column count;
- blank W1-W7 annotation fields and a notes field.

No generated query text, reference query/answer, correctness labels, intervention/outcome fields, post-hoc labels, execution provenance hashes, or model/runtime telemetry are included.

## Randomization

Rater A: seed 424241.
Rater B: seed 424242.

The randomization changes case order only. Human independence comes from separate raters annotating separately; different seeds are not themselves evidence of rater independence.

## Integrity checks

The generator must:
1. verify the source evidence hash;
2. verify all 12 manifest cases are present exactly once;
3. construct schemas only from the pinned Spider tables artifact;
4. exclude forbidden fields before serialization;
5. scan serialized packets for SQL statement text and forbidden metadata;
6. verify both packet SHA-256 hashes;
7. emit a manifest containing source, generator, codebook, and packet hashes.

## Provenance rule

These packets are a **new versioned cohort**. They are not represented as reconstruction of the unrecoverable 2026-09-18 historical packet bytes.


## Activation record

The deterministic packet-generation workflow is installed on 2026-09-19; activation is intentionally separate from historical packet reconstruction.
