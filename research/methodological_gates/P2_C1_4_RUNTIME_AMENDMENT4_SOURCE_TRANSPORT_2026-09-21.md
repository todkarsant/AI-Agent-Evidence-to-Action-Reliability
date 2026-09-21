# P2-C1.4 Runtime Amendment 4 — Source transport and bounded Ollama concurrency

Date: 2026-09-21

Status: INFRASTRUCTURE / RUNTIME AMENDMENT — REQUALIFICATION REQUIRED

## Trigger

Runtime3 acquisition run 35614795768 demonstrated two independent execution bottlenecks:

1. repeated shard-level retrieval of the pinned Spider 1.0 archive from the canonical Google Drive distribution exhausted the shared-download quota;
2. multiple confirmatory shards reached the pinned Ollama runtime but encountered `httpx.ReadTimeout` during SQL generation despite the Runtime3 900-second transport ceiling.

The frozen source manifest and scientific protocol are not being changed.

## Corrections

Runtime3 is requalified with the following transport-only changes:

- Spider 1.0 source archive is retrieved once from a public re-host whose published archive SHA-256 exactly matches the frozen `SPIDER_ARCHIVE_SHA256` value:
  `00636695dabed6b5f4b8328a16b13e069a2f16591d5efcce57660669c85b121b`.
- The verified archive and extracted source data are passed from the manifest-freeze job to acquisition shards as an immutable GitHub Actions artifact.
- Acquisition shards therefore perform zero direct Google Drive downloads.
- Confirmatory shard `max-parallel` is reduced from 6 to 2 to reduce concurrent local Ollama inference contention.
- `OLLAMA_TIMEOUT_SECONDS` remains 900 seconds.
- Shard job timeout remains 180 minutes.
- Model, model version, prompt, temperature, source population, manifest order, P6-IP logic, evidence definition, outcome definition, X_W definition, statistical model, and scoring rules are unchanged.

## Source provenance

The re-hosted archive is documented as a re-host of the canonical Spider 1.0 distribution and publishes the same SHA-256 used by the frozen protocol. The runtime must still verify the archive bytes against the frozen SHA before using them.

## Scientific safety

These changes affect only data transport and runner scheduling. They do not alter the bytes accepted as the Spider 1.0 source archive after SHA-256 verification, and they do not alter the scientific execution path.

Failed or timed-out cases remain failed; they are never converted to synthetic observations.

## Qualification requirement

Required transition:

`Runtime3 targeted dry-run PASS → fresh confirmatory acquisition → exact 44-shard reconciliation → forensic integrity gate`.

No confirmatory cohort is accepted unless all 8,638 manifest records are present exactly once and in frozen manifest order.
