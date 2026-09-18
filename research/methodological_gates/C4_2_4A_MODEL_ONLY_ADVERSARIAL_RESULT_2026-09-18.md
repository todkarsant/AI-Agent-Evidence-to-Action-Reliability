# C.4.2.4-A — Model-only adversarial feasibility result

**Date:** 2026-09-18  
**Status:** NON-CONFIRMATORY — HUMAN RELIABILITY GATE REMAINS OPEN

## Purpose

Two separately specified model annotation passes were performed against the blinded 12-case packet. This is an adversarial feasibility test only. It is **not** evidence of independent human-rater reliability.

## Cases

- Total cases: 12
- Available evidence: 7
- NO_USABLE_EVIDENCE: 5
- Obligation-level binary comparisons: 23

The five failed-execution cases were retained at case level and did not receive substantive obligation labels.

## Results

- Raw obligation-level agreement: **86.96%** (20/23)
- Cohen's kappa: **0.721**
- Gwet's AC1: **0.756**

Contingency table:

| | Pass B = 0 | Pass B = 1 |
|---|---:|---:|
| Pass A = 0 | 13 | 1 |
| Pass A = 1 | 2 | 7 |

These are model-only exploratory statistics and must not be presented as empirical inter-rater reliability.

## Disagreements

Three obligation-level disagreements occurred:

1. **C4_2_4A_01 / O2 — Projection**
   - Pass A: supported
   - Pass B: not supported
   - Issue: empty result contains requested output columns but no returned paper rows. This exposes an unresolved distinction between structural availability of requested attributes and substantive evidentiary support for the requested output.

2. **C4_2_4A_03 / O6 — Extremum**
   - Pass A: supported
   - Pass B: not supported
   - Issue: result columns explicitly identify maximum/minimum values, but displayed evidence alone does not independently establish the population-level extremum unless the labeling itself is accepted as sufficient evidence.

3. **C4_2_4A_08 / O7 — Cardinality/completeness**
   - Pass A: not supported
   - Pass B: supported
   - Issue: exactly three rows are displayed for a “top 3” request, but three rows do not necessarily demonstrate that they are the complete top-three population.

## Adversarial interpretation

The model-only agreement is reasonably high in this small pilot, but the disagreements are concentrated exactly where the construct is most vulnerable:

- structural evidence versus substantive evidence;
- output labels versus independently demonstrated semantics;
- returned cardinality versus completeness.

Therefore the pilot **does not justify declaring the codebook validated**.

The disagreement pattern instead provides a concrete falsification target for the human annotation stage.

## Gate decision

**C.4.2.4-A: OPEN / HUMAN VALIDATION REQUIRED**

The construct is not failed by this model-only pilot, but it is also not passed.

Required next step remains two genuinely independent human annotations. The human study must preserve the three disagreement classes as explicit adversarial cases rather than resolving them in advance.

## Reproducibility

Model-pass A CSV SHA-256:
`ecbc2defefdab450cdae36914ceb916a3c93d846c9be541f88ee91815ca910d9`

Model-pass B CSV SHA-256:
`afa776cc7cbc156b703d764a9b053a3c2941271502e793f1848e14b64589f040`

REPORT.json SHA-256:
`e1f3547bf9e256eb34f6b12c256857263f50dce1705655909eeafbb74dbe9640`
