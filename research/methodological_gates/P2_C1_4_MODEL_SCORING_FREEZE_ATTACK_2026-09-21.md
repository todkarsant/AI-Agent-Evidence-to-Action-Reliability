# P2-C1.4-M — Model-Family and Primary Scoring-Rule Freeze Attack
**Date:** 2026-09-21
**Status:** ATTACK COMPLETED — PROTOCOL CANDIDATE IDENTIFIED, CONFIRMATORY FREEZE STILL REQUIRES PRE-COLLECTION LOCK

## Target
Compare:
- M0 = f(B)
- M1 = f(B, X_W)

with the same out-of-sample observations and paired per-case losses.

## Attack 1 — model complexity
The outcome is rare in historical discovery data and the predictor set is intentionally small. Flexible learners, automated feature search, boosting, unrestricted interaction search, and outcome-driven model selection would create an avoidable overfitting risk. They are therefore outside the current candidate confirmatory protocol.

## Attack 2 — model family
A penalized logistic model is a natural candidate because Y_H is binary and the intended inference is incremental prediction from a small prespecified feature set. However, this document does not silently convert that candidate into a frozen confirmatory choice. The exact penalty, regularization selection, intercept treatment, and any transformation of row/column counts must be frozen before outcome-bearing modeling.

## Attack 3 — primary scoring rule
The primary estimand is a paired difference in out-of-sample predictive loss:
Delta_L = E[L(Y_H,p0)] - E[L(Y_H,p1)].

For binary probabilistic prediction, log loss is a candidate primary proper scoring rule because it evaluates the full predicted probability and penalizes confident incorrect predictions. Brier score is retained as a secondary proper scoring measure. Discrimination metrics such as AUROC/AUPRC cannot replace a proper scoring-loss comparison because they do not evaluate probability calibration in the same way.

This is a methodological candidate, not a post-hoc result.

## Attack 4 — calibration
Calibration must be reported because an incremental model can change predicted probabilities without materially changing ranking. At minimum report a calibration assessment appropriate to the final sample size and event count; avoid over-interpreting calibration plots in a sparse sample.

## Attack 5 — tuning leakage
Any regularization selection, preprocessing, transformation, threshold selection, or hyperparameter tuning must occur inside training folds. Outer evaluation outcomes must remain untouched until prediction is generated.

## Attack 6 — paired comparison
M0 and M1 must generate predictions for the identical outer evaluation observations. Retain per-case loss differences:
d_i = L(Y_i,p0_i) - L(Y_i,p1_i).
The primary incremental estimate is the mean of d_i over the prespecified outer evaluation observations, with uncertainty estimated under the same dependence/resampling structure.

## Attack 7 — threshold metrics
A thresholded accuracy/F1/sensitivity/specificity comparison is not suitable as the primary incremental-validity estimand because it discards probability information and introduces a threshold decision. Thresholded metrics may be secondary only if a threshold is frozen independently of test outcomes.

## Candidate protocol emerging from the attack
- Model family: low-dimensional penalized logistic regression.
- Candidate primary loss: log loss.
- Secondary: Brier score, AUROC, AUPRC, calibration assessment.
- Evaluation: paired out-of-sample predictions for M0 and M1.
- Tuning: training folds only.
- Dependence: cluster-aware outer resampling if dependence audit identifies clusters.
- No outcome-driven feature engineering.
- No model-family search after viewing outcome results.

## Disposition
**PASS WITH CONDITIONS for protocol progression.** The attack narrows the candidate confirmatory protocol but does not itself constitute prospective freezing. A versioned protocol must be frozen before outcome-bearing model fitting.

## Scientific safety
No M0/M1 outcome model was fit during this gate.
