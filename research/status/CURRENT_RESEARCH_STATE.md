# Current Research State — P2-C1.3

**State:** `BLOCKED_SCIENTIFIC_COHORT_ALIGNMENT`

**As of:** 2026-09-21

## Current gate status

- **C.4.2.3-C:** global P0 determinism remains unestablished; targeted exact-path qualification is not a global guarantee.
- **C.4.2.3-D:** fresh observational evidence capture was qualified under the documented targeted scope.
- **C.4.2.4-A:** **RESOLVED** after independent-rater attestation, mechanical validation, packet reconciliation, and frozen UNCLEAR operational rule.
- **P2-C1.2 methodological attack:** **COMPLETED**.
- **P2-C1.3 aligned outcome-bearing cohort reconstruction:** **COMPLETED — historical reconstruction rejected**.
- **P2-C1.2 confirmatory modeling:** **BLOCKED** pending an aligned outcome-bearing cohort.

## Decisive scientific blocker

The current W1-W7 X_W measurement cohort contains 12 fresh cases, while the historical P1/P6 outcome summaries contain 330 eligible development cases and 91 held-out cases.

The current 12-case X_W cohort was intentionally non-overlapping with the historical P1/P6 schemas/questions.

The historical Project 1 repository preserves experiment code, protocol, analysis logic, and GitHub Actions provenance. Historical P6 runs also produced machine trace artifacts. However, the preserved scientific record does not establish preservation of the decision-time evidence in a form that supports independent W1-W7 annotation across the historical outcome-bearing units.

Therefore the required row-level structure:

[
(B_i,E_i^{decision-time},X_{W,i},Y_{H,i})
]

does not currently exist for the same decision units.

## What is now established

### Measurement

- W1-W7 witness construct is frozen.
- Human response artifacts are preserved.
- Applicability: 49/49 descriptive agreement; Cohen kappa 1.00.
- Binary witness labels: 27/27 descriptive agreement; Cohen kappa 1.00; Gwet AC1 1.00.
- Independent-rater provenance is supported by explicit attestation.
- UNCLEAR handling is frozen as a pre-outcome methodological amendment.

### Predictive-validity design

The following requirements remain before confirmatory modeling:

1. common decision unit;
2. preserved decision-time evidence;
3. B/X_W/Y_H linkage;
4. predefined missing-X_W handling;
5. frozen model family/regularization/preprocessing;
6. frozen primary proper scoring metric;
7. frozen outer resampling and dependence structure.

## Prohibited shortcuts

Do not:

- retrofit 12 X_W values onto the historical 330/91 outcome units;
- infer X_W from row/column counts or hidden SQL;
- convert NO_USABLE_EVIDENCE to X_W=0;
- call the historical 91-case holdout external validation for X_W;
- fit M0/M1 before aligned data exist.

## Next gate

**P2-C1.4 — Aligned Outcome-Bearing Cohort Design and Evidence-Preservation Protocol**

The new cohort must preserve, for each eligible decision instance:

[
(id,B,E_{decision-time},intervention,final correctness,Y_H)
]

and permit independent outcome-blinded W1-W7 annotation.

## Publication record

The complete methodological development path is now documented in:

- `research/P2_RESEARCH_DEVELOPMENT_JOURNEY.md`
- `research/methodological_gates/P2_C1_3_ALIGNED_COHORT_RECONSTRUCTION_AUDIT_2026-09-21.md`
- `paper/PROJECT2_LIVING_RESEARCH_DRAFT.md`

No confirmatory predictive model, p-value, AUC, Brier score, log-loss difference, or incremental-validity result exists.
