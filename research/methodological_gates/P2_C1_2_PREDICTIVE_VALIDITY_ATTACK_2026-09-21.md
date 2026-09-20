# P2-C1.2 — Predictive / Incremental Validity Methodological Attack

**Date:** 2026-09-21  
**Status:** ATTACK COMPLETED — CONFIRMATORY MODELING NOT YET AUTHORIZED

## 1. Frozen starting point

### Outcome

The current P2-C1.2 target is:

Y_H = I(P0 correct AND replacement occurs AND final answer incorrect)

The intended comparison is:

M0 = f(B)

M1 = f(B, X_W)

where B is the frozen prospective baseline and X_W is the frozen observable evidence-witness construct.

### Frozen baseline

The repository's prospective baseline specification freezes execution_ok, row_count, and column_count and excludes generated SQL, gold SQL/answer, P0 correctness, intervention/replacement outcome, final-answer correctness, post-hoc labels, X_W, and outcome-selected features.

This baseline freeze is valid as a methodological starting point. It does not establish that these variables were historically preregistered for the earlier Project 1 experiment.

## 2. Attack A — Unit-of-analysis alignment

### Finding: FAIL

The frozen human X_W cohort contains 12 cases.

A forensic recount of the actual frozen packet shows:
- 12 total cases
- 7 SUCCESS
- 5 NO_USABLE_EVIDENCE

The 49 populated applicability judgments therefore equal exactly 7 × 7. The earlier human-reliability audit wording that said '8 SUCCESS cases' was a documentation error and has been corrected. The reliability denominators themselves remain consistent with 7 SUCCESS cases.

The historical P1/P6 outcome summary, by contrast, describes 330 eligible development cases with 21 harmful replacements and 91 heldout cases with 5 harms.

The 12 X_W cases were explicitly described as a fresh qualification subset with no overlap with the historical P1/P6 schemas/questions.

Therefore the current artifacts do **not** provide a row-level dataset in which both X_W is measured and Y_H is observed for the same units.

Without that alignment, an M0 versus M1 predictive-validity comparison cannot be performed. Any attempt to regress the 21 historical harms on the 12-case X_W values would be an invalid unit mismatch.

### Disposition

**Hard stop.** A confirmatory predictive-validity model must not be fitted until a common outcome-bearing/X_W-bearing cohort exists.

## 3. Attack B — Outcome leakage

### PASS, subject to implementation audit

The frozen human protocol excludes P0 correctness, intervention/replacement, downstream outcome, generated SQL, reference SQL/answer, and post-hoc labels from annotation.

The baseline specification independently excludes the same outcome-bearing variables.

The principal remaining implementation requirement is to verify that the eventual model-building code receives only decision-time B and X_W fields plus the frozen outcome Y_H for training/evaluation, with no derived post-outcome fields.

No such confirmatory model has been run.

## 4. Attack C — Construct timing

### PASS in principle; cohort reconstruction required

X_W is defined from decision-time displayed evidence and an outcome-blinded human annotation process. This is temporally compatible with prediction of a later replacement-harm outcome.

However, the predictor must be attached to the exact decision instance whose later Y_H is being predicted. The current 12-case qualification cohort does not satisfy that requirement for the historical P1/P6 harm outcomes.

## 5. Attack D — Missing X_W / NO_USABLE_EVIDENCE

### FAIL / unresolved

The frozen codebook explicitly says that NO_USABLE_EVIDENCE does not become a substantive X_W zero.

Therefore the eventual predictive dataset cannot silently encode execution failure as X_W = 0.

The analysis must predefine one of the following before outcome-bearing modeling:

1. collect usable decision-time evidence and X_W for every eligible outcome-bearing decision instance;
2. explicitly restrict the estimand to a prespecified population in which X_W is defined, with a scientific justification and corresponding change in target claim; or
3. specify a formally justified missing-predictor strategy that is frozen before outcome modeling and is valid for the actual deployment/measurement process.

Complete-case deletion must not be adopted merely because it is convenient. Missing-data handling must be part of the prediction protocol and must be applicable consistently to model development and evaluation.

## 6. Attack E — Baseline model dimensionality and rare outcome

The historical development summary contains 21 harmful outcomes among 330 eligible cases, approximately 6.36%.

That is a sparse binary outcome for predictive-model development. The baseline contains three signal fields, but the final model specification still has to freeze transformations, missingness representation, model family, regularization/penalization, interaction policy, and tuning policy.

Standard unpenalized logistic regression should not be assumed safe merely because the predictor count is small. Rare/sparse binary outcomes can produce separation and unstable maximum-likelihood estimates; penalized approaches such as Firth-type logistic regression are established responses to this problem.

Riley et al. also emphasize that binary prediction-model sample requirements depend on outcome prevalence, number of predictor parameters, expected model performance, and overfitting—not merely a fixed events-per-variable rule.

## 7. Attack F — In-sample incremental validity

### REJECTED

A statistically significant X_W coefficient, likelihood-ratio test, apparent R² increase, or apparent AUC increase would not by itself establish incremental predictive validity.

The research question is explicitly **out-of-sample prediction**.

The primary comparison therefore has to use predictions generated for observations that were not used to fit or tune the corresponding model.

For a single available cohort, repeated/nested cross-validation can be used only if the full model-selection procedure is contained inside the training folds. Any preprocessing, imputation, scaling, feature transformation, tuning, or threshold selection must be fit within training data.

## 8. Attack G — Metric choice

### Required freeze

AUC alone is insufficient for the stated claim because the claim concerns prediction of a consequential binary outcome, not only ranking.

The primary incremental estimand should be a paired out-of-sample proper scoring-loss difference between M0 and M1, with secondary reporting of discrimination and calibration.

Candidate reporting set:
- primary: out-of-sample log loss or another prespecified strictly proper scoring rule;
- secondary: Brier score;
- secondary: AUROC;
- secondary: calibration intercept/slope or a suitably constrained calibration assessment;
- descriptive: precision-recall curve/AUPRC because the outcome is sparse;
- optional decision-utility analysis only if an explicit harm-action threshold is prespecified independently.

The exact primary metric must be frozen before outcome-bearing modeling.

Brier score is a proper scoring rule and useful for comparing probabilistic predictions on the same population, but its value is prevalence-dependent; it should therefore not be the sole reported measure.

## 9. Attack H — Cross-validation optimism

If hyperparameters or model specifications are selected using the same resamples used to estimate final performance, the performance estimate can be optimistic.

The clean confirmatory design is:
- outer folds estimate out-of-sample performance;
- all preprocessing/model tuning occurs inside each outer training fold;
- M0 and M1 are evaluated on exactly the same outer test observations;
- the per-case loss difference is retained so the comparison is paired.

If no tuning is allowed and a completely fixed low-dimensional model is specified in advance, a simpler repeated cross-fitting scheme may be sufficient. The choice must be frozen before inspecting Y_H.

## 10. Attack I — Incremental-validity estimand

The estimand should be:

Delta_L = E[L(Y, p0)] - E[L(Y, p1)]

where lower L is better and p0/p1 are strictly out-of-sample predictions from M0/M1 on the same evaluation observations.

Positive Delta_L means M1 has lower expected loss than M0.

The sign convention and primary metric must be frozen before analysis.

A coefficient for X_W is not the primary estimand.

## 11. Attack J — Cluster / dependence structure

The unit of prediction must be explicitly frozen.

If the final dataset contains multiple decisions from the same original case, model run, schema, user/session, or repeated perturbation, ordinary row-wise resampling would overstate effective sample size.

The outer split must therefore keep any scientifically defined dependent units together.

No cluster structure may be invented after inspection; the actual data-generation unit must be audited first.

## 12. Attack K — Historical holdout

The historical 91-case heldout subset contains 5 harms in the current project summary.

It cannot automatically serve as an external validation set for P2-C1.2 because X_W was not measured on those same cases and the historical traces did not preserve the required raw evidence.

A genuine external validation claim requires X_W and B to be available for the same heldout decision instances, with the outcome observed independently.

## 13. Attack L — 12-case human cohort as a predictive dataset

### REJECTED

The 12-case C4.2.4-A cohort is a **measurement/reliability qualification cohort**, not a predictive-validity sample.

Its purpose was to validate the witness measurement process.

Using its agreement statistics or X_W values to claim predictive validity would be a category error.

The cohort should remain identified as measurement validation evidence.

## 14. Attack M — Baseline contamination by raw evidence

The frozen B is intentionally coarse.

A future analyst must not add raw-evidence-derived variables such as row-value counts, unique-value counts, evidence length, lexical overlap, or other evidence summaries merely because they correlate with Y_H or improve M0.

Doing so after inspecting X_W/outcomes would redefine the baseline and weaken the incremental-validity claim.

Any baseline expansion requires a new versioned specification and a new confirmatory protocol.

## 15. Attack N — Claim interpretation

Even if M1 improves out-of-sample prediction, the result would establish **incremental predictive validity in the tested population and protocol**.

It would not establish causal protection from harm, that X_W causes harm reduction, correctness of the underlying SQL, global evidence completeness, universal agent reliability, deployment safety, or generalization to unrelated agent tasks.

The paper claim must remain bounded to the tested decision-time evidence and replacement-harm setting.

## 16. Current verdict

| Attack | Status |
|---|---|
| Frozen baseline independence | PASS |
| Outcome leakage controls | PASS in design; implementation audit pending |
| Decision-time timing | PASS in principle |
| X_W / Y_H row-level alignment | **FAIL** |
| NO_USABLE_EVIDENCE handling | **UNRESOLVED** |
| Rare-outcome model specification | **UNRESOLVED** |
| Out-of-sample requirement | PASS as target; implementation not yet frozen |
| Primary metric | **NOT YET FROZEN** |
| Cross-validation protocol | **NOT YET FROZEN** |
| Dependency/cluster unit | **NOT YET FROZEN** |
| Historical holdout as external validation | REJECTED under current artifacts |
| 12-case cohort as predictive sample | REJECTED |

## 17. Scientific gate

**P2-C1.2 CONFIRMATORY MODELING: BLOCKED.**

This is not an infrastructure block.

The current blocker is a **scientific data-design requirement**:

> construct a single, outcome-bearing cohort in which B, X_W, and Y_H are defined for the same decision units under the frozen timing/blinding rules.

The 12-case measurement cohort cannot be retrofitted into the historical 330/91 outcome cohorts.

## 18. Minimum valid next design

Before fitting M0/M1:

1. freeze the exact prediction unit and eligible population;
2. determine whether every eligible decision instance has preserved decision-time evidence sufficient for independent X_W annotation;
3. create a new outcome-bearing evidence cohort with B + decision-time evidence + Y_H linkage;
4. independently annotate X_W without outcome access;
5. lock raw annotations;
6. predefine the missing-X_W rule;
7. freeze the model family/regularization and preprocessing;
8. freeze the primary out-of-sample scoring metric;
9. freeze the outer resampling/split and dependence handling;
10. only then execute M0/M1.

This sequence preserves the novelty seam while preventing a retrospective merge of incompatible datasets.

## 19. External methodological support

The attack follows established prediction-model principles: evaluation data should be distinct from training/model-selection data; prediction-model performance should consider discrimination and calibration; binary prediction sample requirements depend on outcome prevalence and model complexity; and out-of-sample incremental predictive validity should be assessed out of sample rather than by relying only on apparent R² or coefficient significance.

Supporting sources checked on 2026-09-21 include Collins et al., TRIPOD+AI (BMJ 2024); Riley et al. (BMJ 2020); and recent work specifically examining out-of-sample incremental predictive validity.

## 20. No confirmatory result

No P2-C1.2 predictive model, p-value, effect estimate, AUC, Brier score, log-loss difference, or incremental-validity result has been generated.
