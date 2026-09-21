# P2-C1.4 — Confirmatory Statistical and Collection Protocol Freeze V1

**Freeze date:** 2026-09-21  
**Protocol ID:** P2-C1.4-CONFIRMATORY-V1-2026-09-21  
**Status:** **FROZEN BEFORE CONFIRMATORY OUTCOME COLLECTION**

## 1. Confirmatory question
Does adding the independently measured decision-time evidence-witness score X_W improve out-of-sample prediction of harmful incumbent replacement beyond the frozen baseline B?

M0 = f(B)

M1 = f(B, X_W)

Y_H = I(P0 correct AND replacement occurs AND final answer incorrect).

The claim is restricted to incremental predictive validity in the newly collected evaluation population and protocol. No causal protection, universal reliability, or deployment-safety claim is authorized.

## 2. Prediction unit
One immutable decision instance is one question/database case executed once under the pinned P6-IP decision pathway in the confirmatory run.

Each record is linked by decision_id to the question/database, frozen baseline B, exact pre-intervention evidence, later intervention/replacement state, final correctness, Y_H, and independent X_W annotations.

Benchmark case identity is retained as the dependence cluster. Historical outcomes are never joined to the new decision instances.

## 3. Confirmatory source population and freshness
The primary acquisition frame is the Spider 1.0 training-side source used by the qualified collector: train_spider.json plus train_others.json, downloaded from the pinned Spider archive and cryptographically verified.

The historical P1 cohort was based on the Spider development set (1,034 questions). The confirmatory source is therefore a different official Spider split. The frozen 12-case C4.2.3-B/C4.2.4 measurement pilot is explicitly excluded.

Selection rule: include every unique (db_id, question) available in the pinned training-side source after exclusion of the frozen 12-case pilot, in deterministic SHA-256 order only for stable manifest ordering. No outcome, X_W label, P0 correctness, replacement, or final correctness is used for selection.

The full eligible frame is collected rather than choosing an arbitrary fixed N. This avoids an unsupported single-point sample-size target while using all available cases in the prespecified source frame.

## 4. Sample-size rationale and feasibility gate
No arbitrary events-per-variable rule is used as the primary justification.

Before collection, the following are frozen:
- candidate predictor parameters: 3 baseline parameters + 1 X_W parameter = 4 slopes;
- shrinkage target: 0.90;
- anticipated planning prevalence: approximately 6.36%, taken only from the historical P1 development discovery cohort (21/330) and explicitly treated as a planning assumption, not as a known future rate;
- anticipated model performance: conservative low-signal planning assumption corresponding to 15% of the maximum Cox-Snell R² for the planning prevalence, because no validated external C-statistic/R² for X_W exists;
- all available eligible source-frame units will be collected;
- if the realized outcome count is inadequate for a stable penalized model, the result is reported as a feasibility/measurement outcome and confirmatory model fitting is stopped rather than rescued by changing the protocol.

This follows context-specific prediction-model sample-size guidance rather than a fixed EPV-only rule.

## 5. Baseline B — frozen
Exactly three fields: execution_ok, row_count, column_count.

For modeling only, row_count and column_count are transformed as log1p and standardized using training-fold mean/SD. execution_ok remains binary. Transformation and standardization are fitted inside each training fold and then applied unchanged to its validation fold.

No evidence-derived feature may be added after outcome inspection.

## 6. X_W — frozen
X_W is the frozen W1-W7 witness construct and the frozen UNCLEAR operational rule already established in C4.2.4-A.

For each usable evidence-bearing decision instance, two independent outcome-blinded raters annotate the same frozen evidence. Raw responses are immutable and retained separately. No rater sees outcomes, intervention/replacement, correctness, SQL, reference answers, or post-hoc labels.

X_W is the mean of applicable W1-W7 witness indicators. NO_USABLE_EVIDENCE is missing X_W, never zero.

## 7. Primary analysis population
The acquisition population includes every eligible source-frame decision instance.

The primary M0-vs-M1 analysis population is restricted to decision instances for which usable decision-time evidence permits an X_W annotation. This restriction is frozen before outcome analysis and is not outcome-dependent.

All acquired cases, including NO_USABLE_EVIDENCE cases, remain in the cohort flow and are reported. No post-hoc complete-case rule may be introduced.

## 8. Model family — frozen
Both models use penalized binary logistic regression with L2 (ridge) regularization.

- intercept included and not intentionally penalized;
- no interactions;
- no nonlinear terms beyond the frozen log1p transformation of row_count and column_count;
- no class weighting;
- no outcome resampling;
- no feature selection;
- solver: deterministic L-BFGS implementation available in the pinned analysis environment;
- maximum iterations: 2000;
- convergence tolerance: 1e-8.

Regularization strength is selected only inside training data from the prespecified grid:

C in {0.01, 0.1, 1, 10, 100}

where smaller C means stronger regularization. M0 and M1 use the same candidate grid, folds, and tuning criterion.

## 9. Out-of-sample evaluation — frozen
Primary evaluation uses repeated nested group-stratified cross-validation:

- outer: 5 folds;
- repeats: 20;
- inner tuning: 5-fold group-stratified cross-validation;
- random seeds: outer repeats 20261001 through 20261020;
- identical outer partitions are used for M0 and M1 within every repeat;
- groups are (db_id, question), so no repeated benchmark case can cross an outer fold;
- tuning, preprocessing, and C selection occur only inside the training portion of each outer fold.

The outer evaluation observations are never used to select C.

If the realized number of groups/events makes 5-fold stratification impossible, collection does not change. The analysis must report the failure and stop confirmatory fitting rather than altering the fold count after seeing outcomes.

## 10. Primary estimand and metric — frozen
For each outer prediction:

d_i = LogLoss(Y_H,i, p0,i) - LogLoss(Y_H,i, p1,i)

Primary incremental-validity estimand:

Delta_logloss = mean(d_i)

Positive values mean M1 has lower predictive log loss than M0.

The primary estimate is the mean paired out-of-sample loss difference, with repeat-level estimates retained for uncertainty assessment.

No in-sample coefficient, delta-R², training AUC, or thresholded accuracy is the primary estimand.

## 11. Secondary performance measures — frozen
Report for M0 and M1:
- Brier score;
- AUROC when both classes occur;
- AUPRC when both classes occur;
- calibration intercept and slope, with sparse-event limitations explicitly reported;
- distribution of predicted probabilities;
- paired per-case log-loss differences.

## 12. Uncertainty — frozen
Retain every outer-fold/repeat prediction and paired loss.

Primary uncertainty summary: 95% percentile interval over the 20 repeat-level Delta_logloss estimates.

A repeat-level interval is not treated as if the 20 repeats were independent participants; it quantifies resampling instability. The manuscript will distinguish this from a population-level confidence interval.

If a cluster bootstrap is used as a sensitivity analysis, it must resample (db_id, question) groups and refit the complete nested procedure within each bootstrap replicate. It cannot replace the frozen primary estimate.

## 13. Missing X_W — frozen
NO_USABLE_EVIDENCE is not recoded as zero and is not imputed from SQL, row counts, correctness, outcomes, or other hidden fields.

Primary analysis excludes these records from the M0/M1 comparison because X_W is undefined. The exclusion count and reasons are reported from the frozen acquisition flow.

M0 is evaluated on the same primary analysis observations as M1 to preserve a paired incremental comparison.

## 14. Outcome construction — frozen
The decision-time evidence artifact is serialized, hashed, and leakage-scanned before official outcome evaluation.

Only afterward are P0 correctness, replacement, final correctness and Y_H derived.

Annotation packets are generated from the locked evidence artifact and contain no outcome fields.

## 15. Reliability gate — frozen
Before X_W is used in the confirmatory model:
- both independent raters must complete the same frozen cohort;
- mechanical validation must pass;
- raw annotations must be hash-locked;
- packet-to-decision_id reconciliation must pass;
- raw applicability and witness agreement must be reported;
- Cohen kappa and Gwet AC1 are descriptive/sensitivity reliability measures;
- UNCLEAR normalization is applied deterministically under the already frozen rule.

No outcome-bearing model selection may occur before annotation lock.

## 16. Leakage and stopping rules — frozen
Stop confirmatory analysis if evidence is captured after intervention, evidence mutates after lock, outcome/correctness/SQL leaks into annotator packets, decision_id duplicates occur, decision-to-outcome linkage is unresolved, historical outcome values are joined to new decision instances, X_W is generated from hidden SQL or outcome information, undocumented manual outcome adjudication occurs, missingness handling differs from this protocol, group identity cannot be preserved, runtime nondeterminism prevents identifying decision instances, or outcome variation is insufficient for the prespecified model/resampling design.

No scientific parameter, model family, seed, cohort definition, or exclusion rule may be changed to rescue a failed confirmatory run.

## 17. Reporting standard
The manuscript will report cohort construction, source split, eligibility/exclusions, prediction unit, dependence structure, temporal ordering, evidence preservation, rater blinding/independence, missingness, outcome prevalence, predictor transformations, model family, regularization grid, nested resampling, discrimination, calibration, proper scoring loss, paired incremental loss, uncertainty and limitations.

## 18. External methodological basis
- Riley et al., BMJ 2020: context-specific sample-size planning for binary prediction models and avoidance of arbitrary EPV-only justification.
- Pratiwi et al., Behaviormetrika 2024: out-of-sample incremental predictive validity and nested cross-validation when tuning penalties.
- TRIPOD+AI, BMJ 2024: separation of evaluation from tuning/model selection, explicit predictor/missing-data/model specification, and reporting of discrimination/calibration and uncertainty.
- scikit-learn documentation: StratifiedGroupKFold keeps groups in a single fold while attempting class-balance preservation; LogisticRegression documents L2 regularization and C semantics.

## 19. Confirmatory authorization
This document is the statistical/protocol freeze.

**Authorized next step:** generate and hash the confirmatory source-frame manifest, then acquire the aligned outcome-bearing cohort under the pinned runtime.

**Not authorized:** X_W annotation before evidence lock; model fitting before X_W lock; any retrospective attachment to P1/P6 outcomes.

## 20. Status
**P2-C1.4-S: FROZEN.**  
**P2-C1.4-M: FROZEN.**  
**P2-C1.4 collection protocol: FROZEN.**  
**Next: actual aligned outcome-bearing cohort acquisition.**