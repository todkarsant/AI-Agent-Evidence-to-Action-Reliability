# C4.2.4-A — Human Annotation Handoff Protocol v1

**Status:** OPERATIONAL HANDOFF — DOES NOT CLOSE THE GATE  
**Date:** 2026-09-21  
**Cohort:** C4_2_4A_WITNESS_V2_2026-09-19  
**Construct:** frozen W1-W7 observable evidence-witness construct

## Purpose

The computational preparation for C.4.2.4-A is complete. The remaining requirement is two genuinely independent, outcome-blinded human annotation passes over the same frozen 12-case cohort.

This document is an execution protocol, not a scientific result.

## Required human boundary

Two real human raters are required.

- Rater A and Rater B must work independently.
- They must not see each other's annotations before both raw annotation files are locked.
- They must not consult generated SQL, reference SQL, reference answers, P0 correctness, intervention/replacement outcomes, downstream outcomes, or post-hoc evaluator labels.
- They must not reconcile disagreements during primary annotation.
- A later adjudication, if needed, is a separate artifact and never replaces the two raw annotation sets.

Different packet randomization seeds do **not** establish human independence.

## Frozen inputs

Rater A packet:

- research/annotation_packets/C4_2_4A_WITNESS_V2_RATER_A.json
- SHA-256: 50391c44acc58ab9b9e11f7a3999cc6f8247e0a37451929b57ddc9d0392fd9ee
- seed: 424241

Rater B packet:

- research/annotation_packets/C4_2_4A_WITNESS_V2_RATER_B.json
- SHA-256: 804d633c1ff8382adc8343f41fd6035afb3e044d228d420519f5baea186a9c3e
- seed: 424242

Frozen codebook:

- research/methodological_gates/C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19.md
- blob SHA-1: fc33316b172915244e127d050142bb3bac0534b5

Response schema:

- research/annotation_packets/C4_2_4A_RATER_RESPONSE_SCHEMA_V1_2026-09-20.json

## Annotation procedure

For each case:

1. Read only the natural-language question, schema, execution status, returned columns, and returned rows.
2. Determine whether each W1-W7 dimension is applicable.
3. If applicable, decide whether the observable witness is PRESENT or ABSENT_OR_AMBIGUOUS.
4. If applicability is genuinely unclear, use UNCLEAR and record the reason.
5. For NO_USABLE_EVIDENCE, keep witness values null; do not convert execution failure into zeros.
6. Record a concise evidence-based note where useful.
7. Do not inspect hidden or downstream information.

### Critical distinction

Applicability is not witness presence.

Example: if a question asks for male students and the result displays only student IDs, the selection obligation is applicable but its witness is absent. It is not N/A.

## C423_0001 caution

The question asks for papers on VLDB after 2000 without explicitly enumerating output attributes. The pre-annotation audit identified this as an output-scope ambiguity.

Do not silently resolve this ambiguity using hidden information. If the interpretation remains materially unclear, use the response schema's UNCLEAR applicability state and explain the reason. The two raw annotations will then be audited separately for applicability agreement before any confirmatory denominator is fixed.

## Submission protocol

To preserve independence:

1. Each rater receives only their assigned packet and the frozen codebook/schema.
2. Each rater completes their response file independently.
3. Neither rater sends their completed labels to the other.
4. Do not publish completed labels in a shared issue, pull request, chat, or repository location visible to the other rater.
5. Once both are independently complete, the two raw files can be supplied to the research owner for mechanical validation and statistical analysis.
6. Raw files must remain immutable after receipt. Any correction requires preserving the original and recording the reason.

## Gate after submission

Only after both raw files are locked:

1. mechanically validate schema and packet correspondence;
2. verify no forbidden information was introduced;
3. separately assess applicability agreement;
4. construct the predefined binary witness denominator from jointly applicable dimensions according to the frozen operational rule;
5. calculate obligation-level percent agreement, Cohen's kappa, Gwet AC1 sensitivity analysis, contingency tables, prevalence/mix, and appropriate uncertainty intervals;
6. perform the predefined disagreement/codebook-failure audit;
7. preserve weak or null reliability findings;
8. if the codebook must change, create a new version and cohort rather than editing this cohort retrospectively.

## Prohibited shortcuts

The following do not satisfy C.4.2.4-A:

- two LLM passes;
- two passes by the same human;
- model + human treated as two independent humans;
- adjudication replacing raw ratings;
- reconstructing the historical 2026-09-18 packets;
- using correctness/outcome information to resolve an annotation;
- changing the W1-W7 codebook after seeing the human labels without creating a new version/cohort.

## Current gate status

**OPEN — HUMAN ANNOTATION REQUIRED.**

No confirmatory P2-C1.2 predictive/incremental-validity analysis may begin before this gate is resolved.
