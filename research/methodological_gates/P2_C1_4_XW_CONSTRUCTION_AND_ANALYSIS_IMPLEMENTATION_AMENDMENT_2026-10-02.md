# P2-C1.4 X_W Construction and Analysis Implementation Amendment

**Amendment ID:** `P2-C1.4-XW-CONSTRUCTION-AND-ANALYSIS-IMPLEMENTATION-AMENDMENT-2026-10-02`
**Date:** 2026-10-02
**Status:** DRAFT for author approval. It must be approved and frozen **before** the raw annotations are locked and before anyone sees an outcome.
**Frozen protocol:** `P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21` (unchanged)
**Related:** Codebook v2 (2026-09-19), UNCLEAR rule (2026-09-21), Missingness amendment (2026-10-01), G3 amendment (2026-10-01)

## 1. Why

The cohort was locked on 2026-10-02 (acquisition run `36853456589`), and blinded packets were generated (run `37017913823`). Before annotation and analysis can run mechanically, several points the frozen documents do not state have to be fixed. Nobody has seen any outcome. The outcome summaries in the lock artifact have not been opened.

## 2. Gaps closed (X_W)

| # | Gap in frozen documents | Proposed rule |
|---|---|---|
| X1 | How the two raters' labels become one X_W (protocol §6 defines X_W only per rater) | Compute X_W for each rater under the frozen UNCLEAR rule. **Combined X_W = mean of the two raters' X_W** where both are defined; if only one is defined, use that one; if neither, missing. No adjudication; raw labels are never changed. |
| X2 | Who applies UNCLEAR rule step 2 (implementation-only uncertainty → YES/NO) at 8,638-case scale. In the 12-case pilot the researcher applied it afterwards. | Raters apply it while annotating. The tool states it on every screen: UNCLEAR is only for ambiguity in the question's wording, never for how a hidden query might have been written. Any UNCLEAR that remains is treated as genuine semantic ambiguity (rule 5): w = 0, kept in the denominator. A reason is mandatory. |
| X3 | Whether case status is judged by the rater | No. Status is mechanical and comes from the packet (`SUCCESS` / `NO_USABLE_EVIDENCE`); the tool and validator enforce this. |
| X4 | A SUCCESS case where a rater marks every dimension NO (empty denominator) | That rater's X_W is undefined (not 0, not 1). This is reported as a count. |
| X5 | Applicability on NO_USABLE_EVIDENCE cases | Judged from the question for reliability reporting; witness stays null; X_W is missing. |
| X6 | Reliability uncertainty "where appropriate" | 95% case-level bootstrap intervals for Cohen's kappa and Gwet's AC1 (2,000 replicates, seed 20261002). Descriptive only; no threshold constitutes a pass. |

## 3. Gaps closed (analysis implementation)

The frozen analysis is implemented in `research/P2-C1.2/analysis/run_P2_C1_2_confirmatory_analysis.py`. The full list of 23 implementation choices (IC01–IC21 in the script plus the CLI choices) is in that file and in its README. Those needing an explicit decision:

| # | Choice | Proposed |
|---|---|---|
| A1 | C tuning criterion (protocol: "same tuning criterion") | Mean inner-fold log loss; ties go to the smaller C. |
| A2 | Inner-fold seeds (not stated) | `outer_seed × 10 + outer_fold_index`. |
| A3 | X_W scaling | Used raw (0–1); only the two count features are log1p-standardized, as frozen. |
| A4 | Protocol §4 "inadequate outcome count" | The run stops (`FEASIBILITY_STOP`) only if the frozen 5-fold group-stratified partitions cannot be built or any fold lacks events or non-events. A shortfall against Riley et al. (2020) criteria (i) and (iii) at the frozen planning values is reported as `FEASIBILITY_WARNING_RILEY`, and the analysis still runs and is reported with that warning. |
| A5 | Robustness flag (missingness amendment §4) | The sign of Δlog-loss must agree across primary, S1, S2-low and S2-high. Note: sign agreement can occur for a negligible effect; intervals are always reported alongside it. |
| A6 | Systematic-missingness audit E3 vs E4 split | Not separated, because the split needs `p0_correct`, an outcome field. E2 and E3/E4 combined are compared with EVALUABLE. This is a deviation from amendment §5 wording, in favour of blinding. |
| A7 | Reference-SQL hardness and nesting depth for the audit | Computed from the frozen source questions by a separate outcome-blind script (to be added). Until then the audit reports `NOT_COMPUTED_INPUT_MISSING` for those two features. |
| A8 | Pinned analysis environment (protocol: "pinned analysis environment") | Python 3.11, numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0, statsmodels 0.15.0. These are recorded in the outputs. |

## 4. Sequence (frozen once approved)

1. Rater A and rater B annotate their own packets with `research/annotation_ui/P2_C1_4_XW_ANNOTATOR.html`, independently, with an independence attestation.
2. `validate_P2_C1_4_XW_responses.py` must pass for both final exports.
3. `construct_P2_C1_4_XW.py` hash-locks the raw annotations, writes the reliability report and constructs X_W. It never opens the cohort or outcomes.
4. Only then is the analysis run once on the locked cohort and locked X_W, with the frozen settings (no test mode).

## 5. What is not changed

The question, B, the X_W construct and codebook, the UNCLEAR rule, Y_H, the model family, the C grid, folds, repeats, outer seeds, estimand, cohort and every amendment already adopted remain as they are.

## 6. Verification so far (synthetic data only)

- Annotator: driven in headless Chromium with a full-size synthetic packet (8,638 cases, 32.5 MB). It loaded and hashed in about 2 s, rendered about 16 ms per click and about 25 ms per case with 500 rows, kept 0.37 MB of autosave, survived a reload, and its export passed the validator.
- Validator and construction: 18 tests, covering 11 rejection cases, the X_W rules, end-to-end construction, refusal of identical rater IDs and swapped files, and no access to the cohort.
- Analysis: 22 tests (determinism, fail-closed inputs, a null X_W giving Δ ≈ 0, a signal X_W giving Δ > 0, S1/S2 counts, group separation, feasibility stop, Riley formulas, an outcome-blind audit, calibration).
