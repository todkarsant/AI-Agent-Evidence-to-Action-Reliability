# P2-C1.2 — Baseline Signal Specification v1

**Status:** FROZEN PROSPECTIVE BASELINE
**Freeze date:** 2026-09-19

## Purpose

Freeze the baseline before any human labels, intervention outcomes, or predictive-model fitting from the new cohort are inspected. The baseline must be independent of X_W construction.

## Baseline signal set B

B contains only decision-time signals preserved in the audited P0 evidence trace:

1. **execution_ok** — whether the candidate query executed successfully.
2. **row_count** — number of returned rows when execution succeeds; missing on execution failure.
3. **column_count** — number of returned columns when execution succeeds; missing on execution failure.

Missing row_count/column_count are represented as structurally missing because execution failed; no imputation may use outcome information.

## Exclusions

The baseline does not use generated SQL text, gold SQL, gold answer, P0 correctness, intervention/replacement outcome, final-answer correctness, post-hoc evaluator labels, X_W labels, or any feature derived from them.

The historical P0 selector assess_strict_evidence(question, sql, row_count) is not reused as a baseline feature because it depends on generated SQL and would create a direct construct/intervention entanglement risk.

## Model rule

Baseline model M0 = f(B). Expanded model M1 = f(B, X_W).

Model family, regularization, preprocessing, randomization, missingness handling, and out-of-sample split must be frozen before outcome-bearing analysis. No outcome-dependent feature selection is permitted.

## Scope limitation

This is a **prospective freeze**, not evidence that B was historically preregistered before the earlier Project 1 experiment. The confirmatory claim must therefore be phrased as a prospective P2-C1.2 analysis on the new measurement cohort.

## Scientific rationale

B captures the coarse decision-time execution/evidence signals that were actually preserved in the historical trace while avoiding reuse of the historical SQL-dependent selector. X_W contributes field-level, obligation-specific observable witness information that is not mechanically equivalent to row_count or column_count.
