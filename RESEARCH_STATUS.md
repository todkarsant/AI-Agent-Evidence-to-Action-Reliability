# Research Status

Last updated: 2026-09-18

## Overall status

**Project 2 is in methodological validation.**

The repository has now been established as the canonical source of truth. No fresh P0 experiment should be treated as part of the scientific record until its runtime and provenance are recorded here.

## Gate ledger

| Gate | Status | Record |
|---|---|---|
| P1/P6 discovery evidence | Complete | Discovery/mechanism evidence only |
| P2-C1.1 novelty/falsification work | Complete to current stage | Broad perturbation/robustness novelty seam rejected |
| C.4.1-A Construct Identifiability | **FAIL** | Historical P6 decision path cannot observe representation-level evidence perturbations |
| C.4.1-B Alternative Construct Attack | **PARTIAL / REDESIGN** | Evidence sufficiency is the surviving candidate seam |
| C.4.1-C Construct Separation | **CONDITIONAL PASS** | Requires fresh isolated pilot |
| C.4.2.1 Deterministic Obligation Extraction | **PROVISIONAL PASS** | Requires fresh measurement pilot |
| C.4.2.2 Measurement Reliability | **CONDITIONAL PASS** | Requires genuine independent double annotation |
| C.4.2.3-A Fresh Corpus Acquisition/Freedom From Historical Overlap | **PASS** | 120 fresh cases / 12 non-overlapping schemas |
| C.4.2.3-B Clean Execution Input | **PASS** | Gold-derived fields excluded from annotator-facing input |
| C.4.2.3-C Fresh P0 Execution | **REOPENED / FAIL** | Later repeat exposed 1/12 SQL and execution-status nondeterminism |
| P2-C1.2 Predictive / Incremental Validity | **PENDING** | Must follow validated measurement procedure |

## Important negative findings

### P6

The earlier P6 intervention policy reduced official Spider accuracy on both development and heldout-schema evaluation and increased cost. These results are discovery evidence and a mechanism signal, not confirmatory evidence for P2.

### Construct identifiability

The historical P6 implementation did not expose the raw execution result to the eligibility selector. Therefore representation-level semantic perturbation stability could not have been measured as a non-tautological construct on the historical trace.

This is a methodological failure that motivated the redesign toward independently measured evidence sufficiency.

## Immediate execution boundary

Before the 120-case fresh P0 execution:

1. capture the recovered runtime manifest;
2. verify the historical `OllamaProvider` implementation;
3. perform a small P0 smoke test using the historical request format;
4. preserve all runtime/model digests;
5. only then execute the fresh pilot corpus.

## Reproducibility caveat

The historical benchmark recorded Ollama 0.33.3 and model `llama3.2:1b`, but did not record the original model artifact digest. Therefore byte-identical reproduction of the historical model artifact is not currently proven.

The current recovered runtime and model artifact are fully identified in the reproducibility records, but they must not be described as byte-identically historical without matching historical provenance.

## Requalification update — 2026-09-18

A later rerun of the 12-case fresh P0 pilot under the same declared historical benchmark commit and pinned Ollama runtime produced 11/12 exact SQL matches and 11/12 execution-status matches. The sole mismatch occurred on `behavior_monitoring`. Consequently, the earlier determinism PASS is not sufficient for qualification.

**Current boundary:** no fresh P0 corpus run, human reliability analysis, or P2-C1.2 predictive analysis should treat C.4.2.3-C/D as qualified until this nondeterminism is characterized.

The P0 and evidence-capture workflows have been changed to `workflow_dispatch` only so documentation commits cannot silently trigger experimental runs.
