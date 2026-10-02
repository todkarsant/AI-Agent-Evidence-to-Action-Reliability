# P2-C1.2 confirmatory analysis (M0 vs M1): implementation

This implements the frozen protocol `P2_C1_4_CONFIRMATORY_PROTOCOL_FREEZE_V1_2026-09-21.md` §4–13 and
`P2_C1_4_MISSINGNESS_AND_ELIGIBILITY_AMENDMENT_2026-10-01.md` §4 (S1/S2) and §5 (missingness audit).
It has been exercised only on SYNTHETIC data. **The implementation choices listed below need author
approval before unblinding.**

## Files
- `run_P2_C1_2_confirmatory_analysis.py`: the analysis.
- `make_synthetic_cohort.py`: SYNTHETIC inputs for tests only. Outputs carry `"SYNTHETIC": true`, use `SYN-` ids, and set `xw_construction_version` to `SYNTHETIC-...`.
- `../../tests/test_P2_C1_2_confirmatory_analysis.py`: pytest suite (synthetic only, about 35 s).

## Inputs
| flag | content |
|---|---|
| `--cohort` | locked aligned cohort `{"protocol_version":"P2-C1.4-ALIGNED-V2","records":[...]}` |
| `--xw` | `{"xw_construction_version":..., "records":[{"decision_id", "x_w": float in [0,1] or null}]}`, with exactly one entry per cohort decision_id |
| `--out` | output directory |
| `--reference-features` (optional) | CSV `decision_id,hardness,nesting_depth` for the §5 audit. If it is absent, the audit records `NOT_COMPUTED_INPUT_MISSING` |
| `--sha-check COHORT_SHA256 XW_SHA256` (optional) | the run fails closed on a hash mismatch. SHA-256 of every input is recorded either way |
| `--test-mode`, `--repeats N` | **tests only**. `--repeats` is refused unless `--test-mode` is also given, and `test_mode` is recorded in the outputs |

The run fails closed (exit 2, no results written) when decision_id sets differ, decision_ids are duplicated, x_w is out of range or non-numeric, protocol_version is wrong, an E1/E2 record has a non-null x_w, or E3E4 outcome fields are inconsistent.

## Outputs
- `results.json`: every number, input hashes, package versions, seeds, status and population counts, feasibility, Riley quantities, missingness audit, verdicts and the list of implementation choices. It is written with sorted keys and contains no timestamp, so two runs give byte-identical files.
- `per_case_logloss_differences_<primary|S1|S2_low|S2_high>.csv`: `repeat, fold, decision_id, y, p0, p1, d`.
- `summary.md`: a short human-readable summary.
- `run_metadata.json`: run timestamp, argv, absolute paths and the SHA-256 of results.json. This file is not part of the deterministic output.

Exit codes: 0 = completed, 2 = input invalid, 3 = `FEASIBILITY_STOP`.

## How to run
```bash
# real confirmatory run: no overrides are possible
python3 research/P2-C1.2/analysis/run_P2_C1_2_confirmatory_analysis.py \
  --cohort <locked_cohort.json> --xw <locked_xw.json> --out <dir> \
  [--reference-features <ref.csv>] [--sha-check <cohort_sha> <xw_sha>]

# tests
python3 -m pytest research/tests/test_P2_C1_2_confirmatory_analysis.py -q
```
Runtime is about 90 s for 600 synthetic records at the frozen 20 repeats with four populations. It scales roughly linearly in N.

## Frozen parameters (not configurable)
- **Models.** B = execution_ok (0/1), z(log1p(row_count)), z(log1p(column_count)). M0 = logistic(B). M1 = logistic(B + X_W).
- **X_W enters raw.** It is neither transformed nor standardized, because the protocol specifies transforms only for the counts.
- **Regression settings.** scikit-learn `LogisticRegression(solver="lbfgs", l1_ratio=0.0, C, fit_intercept=True, max_iter=2000, tol=1e-8, class_weight=None)`. `l1_ratio=0.0` is the L2 penalty; `penalty="l2"` is deprecated in sklearn 1.8. The lbfgs objective penalizes only the coefficients and **does not penalize the intercept**: `LinearModelLoss.l2_penalty` is applied to the weights without the intercept.
- **C grid.** {0.01, 0.1, 1, 10, 100}, tuned by inner 5-fold StratifiedGroupKFold on mean inner-validation log loss. M0 and M1 use the same criterion. Ties go to the smaller C.
- **Cross-validation.** Outer: 5-fold StratifiedGroupKFold(shuffle=True) × 20 repeats, seeds 20261001..20261020. Inner seed = `outer_seed*10 + outer_fold_index`. Groups = (database_id, question). Within a repeat, M0 and M1 use identical partitions.
- **Primary population.** EVALUABLE ∧ x_w non-null ∧ y_h non-null.
- **Estimand.** d_i = LL(y,p0) − LL(y,p1), with p clipped to [1e-15, 1−1e-15]. Delta = mean d_i, and positive means M1 is better. The interval is the 2.5/97.5 percentile (linear) of the 20 repeat-level Deltas.
- **Sensitivity analyses.** S1 = primary + E3 (y = `y_h_implied_by_definition` = 0). S2_low and S2_high = S1 + E4 (p0_correct true) with y = 0 and y = 1. The result is flagged robust only if the sign of Delta agrees across all four analyses.
- **Riley et al. 2020 planning values.** 4 parameters, shrinkage 0.90, R²_CS = 15% of the maximum at the observed prevalence. Criteria (i) and (iii) are reported, with δ = 0.05 for (iii).

## Implementation choices needing author confirmation (the protocol does not state these)
The full list (IC01–IC21) is in `IMPLEMENTATION_CHOICES` in the script and is copied into `results.json`. The main ones:
1. **Feasibility rule.** The run stops with `FEASIBILITY_STOP` if StratifiedGroupKFold raises, or if any outer or inner training or validation fold, in any of the 20 repeats, lacks events or non-events. This is checked on all partitions before any fit.
2. **Riley shortfall.** A shortfall gives `FEASIBILITY_WARNING_RILEY` and the analysis still runs. This is an implementation reading of §4 ("inadequate for a stable penalized model"), and **the author must confirm it before unblinding.**
3. **Missing counts.** Null row/column counts are allowed only when execution_ok is false. They are coded 0 before log1p, so execution_ok absorbs the structural-missingness level.
4. **Standardization.** Uses ddof=0; an SD of 0 is replaced by 1. After C is chosen, the model is refit on the full outer training fold.
5. **Tuning loss.** The unweighted mean of the per-fold mean log losses (the GridSearchCV convention). Ties are exact float ties.
6. **Secondary metrics.** Computed per repeat on the pooled outer predictions and summarized as the mean and 2.5/97.5 percentiles over repeats. Calibration uses statsmodels GLM: the slope from y ~ 1 + logit(p), and the intercept from y ~ 1 with offset logit(p). Without statsmodels it falls back to an unpenalized sklearn slope plus a Newton offset intercept, and the method used is recorded.
7. **Missingness audit.** Compares E2, E3E4 (combined) and EVALUABLE. E3 vs E4 is not split because that would require p0_correct, an outcome field. The audit is descriptive only.
8. **Infeasible sensitivity population.** Reported as `FEASIBILITY_STOP` and makes the robustness flag `NOT_ASSESSABLE`. No inferential decision rule on Delta is applied, because none is frozen.
9. **Robustness flag is sign-only.** It can read `ROBUST` when Delta is negligible: on a null synthetic cohort, all four Deltas came out slightly negative.

## Package versions tested
Python 3.11.15, numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0, statsmodels 0.15.0, pytest 9.0.3.
pandas is not used.
