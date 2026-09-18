# GitHub Actions Automation Strategy

## Can Project 1 Actions be reused?

Yes, as a **reference and implementation pattern**, but not copied unchanged.

The Project 1 workflow `.github/workflows/spider-benchmark.yml` establishes a useful end-to-end pattern:

1. checkout code;
2. install a controlled Python environment;
3. start local Ollama;
4. perform a provider smoke test;
5. acquire Spider data;
6. pin the official Spider evaluator;
7. run tests;
8. execute benchmark;
9. analyze results;
10. upload artifacts.

## Why it must not be copied unchanged

The existing workflow installs Ollama through the unpinned current installer:

`curl -fsSL https://ollama.com/install.sh | sh`

That is insufficient for Project 2 reproducibility because it does not guarantee Ollama 0.33.3.

The historical model name `llama3.2:1b` is also not sufficient to establish byte-identical model provenance because a model name is not a cryptographic artifact identity.

The Project 2 standard therefore requires:

- pinned Ollama version;
- recorded Ollama executable/archive SHA-256 where available;
- recorded model manifest digest;
- recorded underlying model blob digest where available;
- pinned benchmark code commit;
- pinned Spider evaluator commit;
- pinned dataset/archive hashes;
- explicit fresh-corpus manifest;
- artifact retention;
- no silent substitution of a different model/runtime.

## Recommended Project 2 automation layers

### Layer 1 — Runtime qualification

Purpose: establish that the requested execution runtime is operational.

Must perform:

- Ollama version check;
- server health check;
- model presence;
- model digest capture;
- exact historical provider smoke test;
- runtime manifest generation.

### Layer 2 — Fresh P0 pilot

Purpose: execute only the frozen 120-case fresh P0 pilot.

Must preserve:

- exact input manifest;
- model/runtime provenance;
- one trace per case;
- failures/timeouts;
- generated SQL;
- token counts if exposed;
- latency;
- raw provider response metadata needed for audit.

### Layer 3 — Measurement annotation

Purpose: support C.4.2.2 independent reliability assessment.

This should be separate from the benchmark execution workflow so annotation cannot become contaminated by benchmark outcomes.

### Layer 4 — Confirmatory predictive-validity workflow

Purpose: only after measurement reliability and preregistration gates pass.

It must operate from a frozen specification and produce machine-readable analysis artifacts.

## Critical architectural rule

Do **not** make Project 2 depend on mutable Project 1 workflows at runtime.

The Project 1 workflow is evidence about how the earlier benchmark was run. Project 2 should copy the relevant methodological pattern into its own repository and then harden it for the new protocol.

This creates a clean provenance boundary:

`Project 1 workflow -> historical reference`

`Project 2 workflow -> frozen current protocol`

## Current recommendation

The first Project 2 workflow should be a small, manually triggered qualification/pilot workflow rather than the full 120-case experiment.

No automatic full benchmark should run on every push. Research datasets and model artifacts are expensive and outcome-bearing; execution should require an explicit manual trigger and record the exact source commit.

## Current status

The Project 1 workflow has been audited as a reusable **reference pattern**.

It has **not** been declared suitable for direct reuse without hardening.
