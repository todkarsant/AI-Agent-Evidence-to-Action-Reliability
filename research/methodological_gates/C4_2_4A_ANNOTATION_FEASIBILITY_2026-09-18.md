# C.4.2.4-A — Double-blind annotation feasibility/adversarial pilot

**Date:** 2026-09-18  
**Status:** READY FOR INDEPENDENT ANNOTATION — NOT YET A RELIABILITY PASS

## Purpose

Test whether the frozen C4.2.4 evidence-obligation codebook can be applied independently and outcome-blind to decision-time evidence, before any confirmatory P2-C1.2 measurement or predictive-validity analysis.

## Pilot material

- Fresh isolated Spider pilot: 12 cases across 12 schemas.
- Source evidence-capture artifact: `evidence_capture_pilot12.json`.
- Source artifact SHA-256: `__SOURCE__`
- Two independently randomized rater packets were generated from the same frozen source:
  - Rater A packet SHA-256: `92a1c456ab501c9f2ce1823bd110884f64649c0a97f8c9af134ad4357c4b5732`
  - Rater B packet SHA-256: `04d51ad99a194721fd9bf87cdaafd988396cb86a46f97425612e640c9a69143f`
- Rater A randomization seed: 424241.
- Rater B randomization seed: 424242.

## Blinding controls

The case material exposes only:
1. case identifier;
2. database identifier;
3. natural-language question;
4. database schema;
5. execution status;
6. returned column names;
7. returned rows;
8. row/column counts.

The packets exclude generated SQL, gold SQL, gold answers, P0 correctness, intervention/replacement decisions, downstream outcomes, post-hoc evaluator labels, and features derived from those variables.

A programmatic inspection found no SQL statement text in either packet.

## Important pilot characteristic

Of the 12 cases, 7 have interpretable execution evidence and 5 have execution failure/no usable evidence. The five NO_USABLE_EVIDENCE cases are retained rather than discarded because this is an adversarial feasibility test. Their frequency is itself relevant to measurement usability.

## Required independent procedure

Two genuinely independent raters must annotate the packets separately. The same model or the same person producing both label sets does **not** constitute independent replication.

For each case, raters identify only obligations explicitly entailed by the question and then rate applicable obligations as SUPPORTED or NOT_SUPPORTED. Failed execution/no interpretable result is recorded as NO_USABLE_EVIDENCE. Original labels must remain unchanged; any adjudication is a separate artifact.

## Primary analysis after raw labels are locked

1. Obligation-level percent agreement.
2. Cohen's kappa.
3. Gwet's AC1 sensitivity analysis.
4. Obligation-level contingency tables.
5. Aggregate X_E agreement descriptively.
6. Intra-rater subset if collected.

Interpretation must include denominators, obligation prevalence/mix, and uncertainty. No automatic coefficient threshold is declared a success criterion.

## Adversarial falsification checks

The pilot is intended to discover:
- obligations that cannot be judged from result evidence alone;
- ambiguity caused by schema/evidence presentation;
- inadvertent inference of hidden SQL;
- excessive NO_USABLE_EVIDENCE frequency;
- obligation classes that are not operationally separable;
- agreement that is dominated by prevalence rather than substantive interpretability.

## Gate boundary

**No reliability PASS is claimed here.** C.4.2.4-A remains open until two independent raw annotation sets exist and the disagreement/codebook audit is completed.

If the codebook requires revision after outcome-bearing annotation starts, the revision must create a new version and a new measurement cohort; the current frozen codebook must not be silently edited.
