# P2-C1.4 Runtime Amendment 3 — Confirmatory shard LLM transport timeout

Date: 2026-09-21

Status: INFRASTRUCTURE / RUNTIME AMENDMENT — CURRENT CONFIRMATORY RUN INVALIDATED; REQUALIFICATION REQUIRED

## Trigger

Confirmatory Runtime2 run 35602663614 reached the pinned collector successfully but multiple acquisition shards failed inside the already-qualified Ollama provider with `httpx.ReadTimeout` while generating SQL. The timeout occurred in Project 1 `app/services/llm.py` during the P6-IP/P5 SQL-generation path.

The failing jobs had already completed checkout, source-data installation, NLTK qualification, Ollama startup, and model fingerprinting. The failure therefore occurs at the transport/inference-duration boundary rather than at schema, evidence, outcome, or statistical logic.

## Observed boundary

The confirmatory workflow currently sets `OLLAMA_TIMEOUT_SECONDS=300` and gives each 200-case shard a 60-minute job timeout. The first failed shards demonstrate that the 300-second per-request ceiling is insufficient for at least some confirmatory cases under the current pinned runner/runtime.

## Correction

Advance the runtime authorization to:

`P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21`

Runtime3 changes only transport/runtime ceilings:

- `OLLAMA_TIMEOUT_SECONDS`: 300 → 900 seconds;
- shard job timeout: 60 → 180 minutes;
- no change to model, prompt, temperature, source population, manifest order, P6-IP logic, evidence definition, Y_H definition, X_W, statistical model, or scoring rule.

The current Runtime2 confirmatory run is not accepted as confirmatory data because incomplete/failed shards cannot satisfy the complete-cohort lock requirement.

## Qualification requirement

A fresh non-confirmatory Runtime3 dry-run must first exercise the same timeout configuration. Only after Runtime3 runtime qualification may a fresh confirmatory acquisition be accepted.

## Scientific safety

Timeout expansion is a transport-level correction. It does not create, remove, reorder, relabel, or impute observations. Any shard that still fails remains ineligible; failed shards are not converted into empty or missing scientific records.

## Provenance

- Confirmatory run exposing blocker: 35602663614
- Pinned Project 1 commit: 7c1864a5619af7118c690f8de72eab57dc0cdc93
- Pinned Spider commit: b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c
- Ollama: 0.33.3
- Model: llama3.2:1b
- Runtime2 timeout: 300 seconds

## Gate consequence

Current state: P2-C1.4 confirmatory acquisition BLOCKED pending Runtime3 qualification.

Required transition:

`Runtime3 dry-run PASS → forensic runtime audit → fresh confirmatory acquisition → complete 8,638-case reconciliation → immutable lock → blinded X_W annotation`.
