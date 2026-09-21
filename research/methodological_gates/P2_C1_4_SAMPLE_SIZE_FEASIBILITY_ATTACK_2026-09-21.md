# P2-C1.4-S — Sample-Size and Event-Rate Feasibility Attack
**Date:** 2026-09-21
**Status:** ATTACK COMPLETED — NO CONFIRMATORY COHORT SIZE FROZEN

## Question
Can the proposed aligned cohort support an incremental binary prediction comparison of M0=f(B) versus M1=f(B,X_W) without relying on an arbitrary events-per-variable rule?

## Design inputs
The future unit is one eligible decision instance with B, decision-time evidence, X_W, intervention/replacement, final correctness, and Y_H. The current historical rate of 21 harms among 330 eligible development cases (approximately 6.36%) is discovery context only and is not treated as the future prevalence.

The confirmatory predictor is intentionally low-dimensional: the frozen baseline currently has three fields (execution_ok, row_count, column_count), while X_W is one scalar derived from W1-W7. The effective parameter count is nevertheless not assumed to equal the raw feature count because preprocessing, transformations, penalization, intercept handling, tuning, clustering, and missingness rules can change effective complexity.

## Attack 1 — arbitrary EPV target
A fixed rule such as “10 events per variable” is rejected as the sole sample-size justification. Prediction-model sample size depends on outcome prevalence, candidate parameter count, anticipated predictive performance, shrinkage/optimism, and precision.

## Attack 2 — historical prevalence treated as known
Using 21/330 (approximately 6.36%) as if it were the future Y_H rate would be an unsupported assumption. The new cohort must report the observed prevalence and distinguish planning assumptions from observed results.

## Attack 3 — single-point N
A single N cannot be responsibly frozen before a defensible prevalence range and model-complexity specification exist. A scenario analysis is required.

## Scenario planning
Let p be the anticipated harm prevalence and E the required number of events under a specified modeling criterion. Then N is approximately E/p. For illustration only, if p=0.05, 0.10, or 0.20, every 100 required events would correspond to approximately 2,000, 1,000, or 500 eligible units respectively. These are planning conversions, not evidence-based sample-size requirements.

## Attack 4 — random train/test split
A small rare-outcome cohort split into training/test subsets can leave too few harms in either partition and inflate uncertainty. The primary protocol should therefore use repeated/nested out-of-sample resampling with all preprocessing/tuning confined to training data, provided the dependence structure permits it.

## Attack 5 — dependence inflation
If multiple decision instances share database, question template, model run, perturbation, or trace, the nominal row count overstates independent information. Dependence groups must be identified before analysis and kept together in outer evaluation.

## Required pre-collection decision
Before confirmatory collection, freeze:
1. anticipated prevalence range and its empirical source;
2. exact predictor parameterization;
3. maximum model complexity;
4. acceptable optimism/shrinkage or precision criterion;
5. dependence unit;
6. resampling design;
7. stopping/feasibility rule.

## Disposition
**PASS WITH CONDITIONS for design progression.** No confirmatory N is frozen by this attack. The cohort is not authorized to be called confirmatory until the above planning inputs are frozen and feasibility is demonstrated.

## Scientific safety
No outcome-bearing model was fit and no future outcome rate was inferred from the current 12-case measurement cohort.
