# P2-C1.4 Runtime Amendment 5 — Long-request Ollama transport ceiling

Date: 2026-09-21

Status: INFRASTRUCTURE / RUNTIME AMENDMENT — REQUALIFICATION REQUIRED

## Trigger

Runtime3 confirmatory acquisition run 35636675220 produced a concrete transport failure in shard 0:

- `httpx.ReadTimeout`
- failure occurred during the pinned Project 1 `OllamaProvider.generate_sql()` call
- the request exceeded the Runtime3 900-second HTTP timeout
- the scientific collector, model identity, prompt, temperature, source population, manifest, outcome definition, and X_W definition were not changed by the failure.

## Correction

The Runtime3 transport ceiling is increased:

- `OLLAMA_TIMEOUT_SECONDS: 900 -> 1800` seconds.
- acquisition job timeout: `180 -> 240` minutes.

Shard concurrency remains `max-parallel: 2`; no scientific workload is added or removed.

## Scientific invariants

Unchanged:

- Project 1 commit
- Spider commit
- Spider archive SHA-256
- confirmatory manifest
- shard size
- model: `llama3.2:1b`
- Ollama version: `0.33.3`
- prompt/model semantics
- temperature
- decision-time evidence boundary
- P6-IP decision path
- outcome definition
- X_W definition and codebook
- statistical estimand/model family
- annotation rules
- acceptance criteria

A timeout remains a runtime failure. It is never converted into a synthetic observation.

## Requalification requirement

The next fresh Runtime3 acquisition must again satisfy:

`Runtime3 smoke PASS -> fresh confirmatory acquisition -> exact 44-shard reconciliation -> 8,638 records -> exact manifest order/uniqueness -> forensic audit -> immutable lock`.

This amendment is transport-only and does not authorize confirmatory modeling before the forensic lock and same-unit X_W/Y_H alignment.
