# P2-C1.3 — Aligned Outcome-Bearing Cohort Reconstruction Audit

**Date:** 2026-09-21  
**Status:** **COMPLETED — HISTORICAL RECONSTRUCTION BLOCKED; NEW ALIGNED COHORT REQUIRED**

## 1. Audit question

Can the historical Project 1 / P6 decision instances be reconstructed so that the same decision units simultaneously carry:

\[
(B_i, E_i^{decision-time}, X_{W,i}, Y_{H,i})
\]

where:

- \(B_i\) = frozen prospective baseline decision-time signals;
- \(E_i^{decision-time}\) = the evidence visible at the decision time;
- \(X_{W,i}\) = the independently measured W1-W7 witness construct;
- \(Y_{H,i}\) = harmful incumbent replacement outcome.

The purpose of this gate is to determine whether the existing historical material can support P2-C1.2 without retrospective unit-level data fusion.

## 2. Sources inspected

### Project 2 repository

The current canonical repository was inspected at main, including:

- `research/methodological_gates/P2_C1_2_PREDICTIVE_VALIDITY_ATTACK_2026-09-21.md`
- `research/methodological_gates/C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19.md`
- `research/methodological_gates/C4_2_4A_PACKET_GENERATION_SPEC_v1_2026-09-19.md`
- `research/annotation_packets/C4_2_4A_WITNESS_V2_PACKET_MANIFEST.json`
- `research/annotation_packets/C4_2_4A_WITNESS_V2_PROVENANCE.md`
- `research/status/CURRENT_RESEARCH_STATE.md`

The Project 2 main tree contains the fresh C4.2.3/C4.2.4 measurement artifacts, but it does not contain the historical 330/91 outcome-bearing raw evidence cohort.

### Project 1 repository

The historical Project 1 repository and the recorded benchmark/P6 commits were inspected, including:

- historical benchmark commit `1765680283df63232018bf7b827d1576c81c3a61`;
- P6-IP controlled run `34252265013`;
- P6-IP results record;
- P6-IP design and runner;
- P6-IP analysis code;
- the frozen benchmark protocol and experiment data model;
- the P6 workflow definition.

The Project 1 repository contains the experimental code, protocol, analysis logic, and provenance references. It does **not** contain a committed historical table linking every P6 decision instance to preserved decision-time raw evidence suitable for independent W1-W7 annotation.

## 3. Historical outcome cohort is real, but is not an X_W cohort

The historical P6-IP result record reports:

### Development

- 1,034 total Spider cases.
- 330 intervention-eligible cases.
- 62 P0-correct eligible cases.
- 268 P0-wrong eligible cases.
- 157 challenger replacements.
- 21 harms.
- 2 rescues.

### Held-out schemas

- 254 total cases.
- 91 intervention-eligible cases.
- 16 P0-correct eligible cases.
- 75 P0-wrong eligible cases.
- 39 challenger replacements.
- 5 harms.
- 1 rescue.

These are valid historical P6 outcome summaries for their stated experiment, but they do not by themselves provide the decision-time evidence required to construct the new X_W predictor.

## 4. Historical raw-trace preservation audit

The historical P6 runner shows that P6 development/holdout chunks were uploaded as GitHub Actions artifacts containing `p6_dev.json` / `p6_unseen.json` traces and defensibility records.

The controlled P6 run `34252265013` currently has non-expired chunk artifacts and a final-analysis artifact. This establishes that historical machine artifacts existed and remain referenced by GitHub Actions metadata.

However, the preserved Project 2 research record explicitly documents the scientific limitation that the historical P6 traces did **not preserve the raw decision-time evidence or intervention identifiers needed by the new construct**. The P6 result/analysis artifacts therefore cannot be treated as a validated W1-W7 annotation substrate merely because benchmark traces existed.

The P6 runner itself records only the evidence fields needed by its original policy, such as incumbent row/column counts and execution status, while the new X_W construct requires independently inspectable witness content at decision time.

**Important distinction:** existence of a historical P6 trace is not equivalent to preservation of the evidence representation required for independent X_W annotation.

## 5. X_W cohort audit

The current C4.2.4-A cohort contains exactly:

- 12 fresh cases;
- 7 SUCCESS;
- 5 NO_USABLE_EVIDENCE;
- 49 populated applicability judgments;
- 27 populated binary witness judgments.

The cohort was intentionally created from a fresh, non-overlapping 12-case subset. The Project 2 handoff records that the 12 cases have no overlap with the historical P1/P6 schemas/questions.

Therefore the current X_W values cannot be attached to the historical 330 development or 91 held-out intervention units.

## 6. Unit-of-analysis result

The required alignment is:

\[
\boxed{B_i \leftrightarrow E_i^{decision-time} \leftrightarrow X_{W,i} \leftrightarrow Y_{H,i}}
\]

for the **same decision instance \(i\)**.

Current state:

| Component | Historical P1/P6 cohort | Current X_W cohort |
|---|---|---|
| Decision instances | Yes | Yes |
| Historical P0/P6 outcome | Yes | No |
| Y_H | Yes for eligible units | No |
| Decision-time evidence sufficient for W1-W7 | **Not preserved in the required form** | Yes |
| Independently annotated X_W | No | Yes |
| Same-unit B + X_W + Y_H | **No** | No |

**Verdict: FAIL.**

No scientifically defensible row-level fusion exists between the current 12-case X_W cohort and the historical 330/91 outcome cohorts.

## 7. Can the historical 91-case holdout be rescued as external validation?

No.

A validation set must contain the predictor and outcome for the same evaluation units. The historical holdout has Y_H-related outcomes, but X_W was not measured on those units and the required decision-time evidence was not preserved as an annotation substrate.

Therefore the historical 91-case holdout may remain a historical P6 corroboration set, but it cannot be called an external validation set for P2-C1.2.

## 8. Can the historical 12-case X_W cohort be used as a predictive sample?

No.

Its scientific purpose was measurement/reliability qualification. It has no corresponding Y_H outcome-bearing intervention cohort.

Using its X_W distribution or agreement statistics to infer predictive validity would be a category error.

## 9. Missing-X_W consequence

The historical outcome cohort also contains a second problem: the frozen X_W definition explicitly treats `NO_USABLE_EVIDENCE` as missing X_W, not as seven zeros.

Therefore even after unit alignment is solved, the confirmatory dataset must predefine how X_W is available across all eligible outcome-bearing units.

The preferred design is to preserve enough decision-time evidence for independent annotation on every eligible unit, rather than introducing a convenient post-hoc complete-case rule.

## 10. Scientific decision

### Historical reconstruction

**BLOCKED.**

The existing repository and documented historical provenance do not establish a reconstructable, independently annotatable X_W for the same historical decision units carrying Y_H.

### Required next design

Create a new aligned outcome-bearing cohort in which each decision unit preserves:

1. frozen baseline \(B\);
2. exact decision-time displayed evidence \(E\);
3. sufficient provenance to establish temporal ordering;
4. later replacement/intervention decision;
5. final correctness needed to derive \(Y_H\);
6. independent outcome-blinded X_W annotation;
7. raw annotation provenance and hashes.

The historical P1/P6 results remain in the paper as **discovery/mechanism evidence and methodological motivation**, not as confirmatory P2-C1.2 predictor-outcome data.

## 11. Stopping rule

No attempt will be made to:

- assign the 12 X_W values to the 330/91 historical units;
- infer X_W from historical row counts;
- reconstruct witness content from hidden/generated SQL;
- set missing X_W to zero;
- use historical P6 intervention records as a proxy for X_W;
- call the 91-case holdout external validation;
- fit M0/M1 before aligned data exist.

## 12. Gate disposition

**P2-C1.3: COMPLETE — HISTORICAL RECONSTRUCTION FAILED SCIENTIFICALLY.**

This is a productive negative result: the audit establishes exactly why the historical P1/P6 dataset cannot answer the new incremental-validity question.

**Next gate:** P2-C1.4 — Aligned outcome-bearing cohort design and evidence-preservation protocol.

No confirmatory predictive model has been run.
