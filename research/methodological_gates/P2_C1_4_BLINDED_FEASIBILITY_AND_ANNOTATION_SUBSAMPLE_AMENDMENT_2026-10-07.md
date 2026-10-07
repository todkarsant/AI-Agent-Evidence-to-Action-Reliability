# P2-C1.4 Blinded Feasibility and Annotation Subsample Amendment

**Amendment ID:** `P2-C1.4-BLINDED-FEASIBILITY-AND-ANNOTATION-SUBSAMPLE-AMENDMENT-2026-10-07`
**Date:** 2026-10-07
**Status:** APPROVED by the author (approach chosen 2026-10-07) and FROZEN before execution. No X_W exists yet, no annotation has been locked, and no outcome has been inspected.
**Amends:** frozen protocol `P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21` §6 and §15 (the scope of the human annotation). Nothing else is amended.

## 1. Why

The protocol asks two independent human raters to annotate every usable decision, about 8,600 cases each. At an estimated 20–40 seconds per case, that is about 50–100 hours per rater. The author judged this infeasible.

Under the frozen Riley hard stop (amendment `…-2026-10-02`, A4), annotation is also pointless if the outcome count cannot support the model even with the full cohort.

## 2. What changes

### 2.1 Blinded feasibility check (runs once, before annotation)

`research/cohort/p2_c1_4_blinded_feasibility_and_subsample.py`, run by the workflow `p2-c1-4-blinded-feasibility.yml`, does the following:

1. **Eligible primary decisions.** It takes `record_status = EVALUABLE`, packet `execution_status = SUCCESS` (usable decision-time evidence) and `y_h` not null. This is the frozen protocol §7 population before X_W exists.
2. **Riley calculation.** It computes Riley et al. (2020) criteria (i) and (iii) at the frozen planning values on N_eligible and the pooled event count.
3. **If the full eligible population fails either criterion:** the verdict is `FULL_COHORT_FAILS_RILEY`.
   - No annotation is requested.
   - The confirmatory result is a feasibility stop, reported as such.
4. **Otherwise, a subsample is drawn.**
   - Size: `n_sub = min(N_eligible, max(ceil(1.5 × n_Riley), ceil(50 / prevalence)))`, where `n_Riley` is the larger of the two criteria's minimum N.
   - Draw: simple random sampling without replacement from the sorted eligible IDs, using `random.Random(20261007)`.
   - All E3/E4 decisions with usable evidence are added for the frozen S1/S2 analyses.

**What it outputs.** The verdict, N_eligible, n_sub and the subsample packets. The event count and the prevalence are never printed or stored. n_sub does reveal the prevalence approximately; this is disclosed here.

**What it does not see.** It cannot look at the X_W–outcome relation, because X_W does not exist yet. The selection is invariant to which decisions are events; a test checks this by shuffling the outcomes.

### 2.2 Annotation scope

- **Who annotates what.** Both raters annotate the same subsample, each in their own original random order. The packets, codebook, UNCLEAR rule, tool, validator, construction and combination rule are unchanged.
- **NO_USABLE_EVIDENCE cases are not annotated.** Their X_W is missing by definition. This drops the applicability-on-NUE reliability item (implementation amendment X5). Reliability is reported on the annotated subsample.

### 2.3 Analysis

The analysis is unchanged.

- **Decisions that were not sampled** get X_W = null, filled in mechanically from the sampling record, with the hash recorded. They leave the primary population as "not sampled", which is missing completely at random by design. The cohort flow reports them separately from NO_USABLE_EVIDENCE.
- **Riley hard stop.** It still applies, to the realized primary population. The 1.5 inflation is there to make a stop caused by sampling noise unlikely.
- **Everything else is unchanged:** the missingness audit, S1/S2 and the single run.

## 3. What is not changed

The question, B, Y_H, the W1–W7 construct, two independent human raters, outcome blinding of the raters, the model family, the C grid, folds, repeats, seeds and the estimand are all unchanged.

## 4. Limitations to report

- **Precision.** A subsample gives less precision than the full cohort.
- **Outcome-rate look.** The outcome rate (not its association) informed the annotation sample size, through a pre-specified blinded rule run once.
- **Approval scope.** The author approved the approach. The inflation factor 1.5, the minimum of 50 expected events and the seed 20261007 were set by the implementer, before execution.

## 5. Verification (synthetic data only)

`research/tests/test_P2_C1_4_blinded_feasibility_subsample.py` covers:

- the verdict that the full cohort fails Riley;
- the subsample being drawn without the event count being disclosed;
- the rater order being preserved;
- the selection being invariant to outcome assignment;
- refusal of the wrong cohort;
- the full gate chain with a subsample (Stage 1 → Stage 2 with the sampling record).
