# P2-C1.4 — Runtime Timeout Amendment and Acquisition Forensic Finding

**Date:** 2026-09-21  
**Status:** **VERSIONED RUNTIME AMENDMENT — PRE-OUTCOME**  
**Previous protocol authorization:** `P2-C1.4-CONFIRMATORY-V1-2026-09-21`  
**New authorization:** `P2-C1.4-CONFIRMATORY-V1-RUNTIME1-2026-09-21`

## 1. Trigger

Confirmatory acquisition run `35596992786` was inspected while still in progress. Multiple matrix shards reached the frozen collector but failed during the pinned Ollama execution path with `httpx.ReadTimeout`.

The failures occurred before a complete aligned outcome-bearing cohort could be produced. No X_W annotations or M0/M1 analysis were performed.

## 2. Concrete evidence

The observed failure path was:

`collect_P2_C1_4_aligned_cohort.py`
→ `p6_ip_runner.run_case`
→ `BenchmarkEnvironment._run_p5`
→ `OllamaProvider.generate_sql`
→ `OllamaProvider._chat`
→ `httpx.Client(timeout=120)`
→ `httpx.ReadTimeout`

Observed examples include:
- shard 7: timeout during challenger/P5 SQL generation;
- shard 4: timeout during P5 SQL generation.

The failure is a transport/runtime timeout, not a scientific outcome and not a model-performance result.

## 3. Why this requires an explicit amendment

The existing pinned Project 1 implementation hard-coded a 120-second Ollama HTTP timeout. The confirmatory cohort contains thousands of fresh benchmark cases and includes P5 challenger generation, which can exceed that transport limit on some GitHub-hosted runners.

Silently changing the timeout would be inappropriate because the runtime provenance would no longer match the recorded protocol.

Therefore the change is versioned explicitly before accepting any new confirmatory data.

## 4. Exact amendment

The Project 1 Ollama provider was changed from a hard-coded transport timeout to an explicitly configurable timeout while preserving the existing default:

- previous default: 120 seconds;
- new configurable variable: `OLLAMA_TIMEOUT_SECONDS`;
- default remains 120 seconds outside this research workflow;
- confirmatory acquisition sets `OLLAMA_TIMEOUT_SECONDS=300`.

No prompt text, model name, model temperature, SQL rules, intervention policy, outcome definition, X_W codebook, manifest population, or statistical analysis specification is changed by this amendment.

Project 1 amended commit:

`7bef895846f2ac89d885827be16b30e69986b013`

The acquisition workflow now pins that exact commit.

## 5. Scientific boundary

This amendment is a transport/runtime qualification change only.

It does **not**:
- retry completed LLM calls;
- change prompts;
- change model;
- change temperature;
- change candidate selection;
- change P0/P6-IP logic;
- change evidence capture;
- change Y_H;
- change X_W;
- inspect outcomes to choose a timeout;
- modify the source-frame population.

No confirmatory scientific record from the failed runs is retained as usable outcome data.

## 6. Treatment of prior runs

Runs `35595401984`, `35595461664`, and `35596426619` remain forensic infrastructure failures.

Run `35596992786` is also **not** an accepted confirmatory cohort because it contains runtime timeout failures and therefore cannot satisfy complete source-frame coverage.

All artifacts from these runs remain useful as audit evidence and are excluded from the scientific cohort.

## 7. New acquisition authorization

A subsequent acquisition run using:

- the same 8,638-case frozen source frame;
- the same 12-case pilot exclusion;
- the same Spider fixture;
- the same `llama3.2:1b`;
- the same temperature 0 setting;
- the same X_W/evidence protocol;
- the amended Project 1 runtime commit;
- 300-second Ollama transport timeout;

may be treated as the next confirmatory acquisition attempt under the versioned runtime authorization.

The source-frame population is unchanged.

## 8. Completion gate remains unchanged

The cohort remains blocked until:
1. every expected shard is present;
2. exact decision-ID coverage matches the frozen manifest;
3. duplicate IDs are absent;
4. decision-time evidence is locked before outcome derivation;
5. genuine `NO_USABLE_EVIDENCE` is represented as missing;
6. Y_H is derived only after evidence lock;
7. consolidated hashes are recorded;
8. forensic audit passes.

Only then may the cohort be locked and transferred to independent blinded X_W annotation.

## 9. Current disposition

**P2-C1.4 confirmatory acquisition: NOT YET COMPLETE.**

The timeout amendment is explicitly versioned and pre-outcome. The next acquisition attempt must use the amended runtime provenance. No scientific result has been claimed.
