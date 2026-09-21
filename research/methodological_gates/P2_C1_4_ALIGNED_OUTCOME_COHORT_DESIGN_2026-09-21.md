# P2-C1.4 — Aligned Outcome-Bearing Cohort Design and Evidence-Preservation Protocol

**Date:** 2026-09-21  
**Status:** DESIGN DRAFT — NOT YET FROZEN FOR OUTCOME COLLECTION  
**Depends on:** P2-C1.3 historical reconstruction failure; frozen W1-W7 codebook; frozen UNCLEAR operational rule.

## 1. Purpose

P2-C1.4 defines the minimum scientific architecture for a new cohort in which the predictor and outcome are measured on the same decision instances.

The target structure is:

[
D_i=(B_i,E_i^{decision-time},X_{W,i},I_i,Y_i,Y_{H,i})
]

where B is the frozen baseline; E is exact decision-time evidence; X_W is independently annotated W1-W7 evidence-witness score; I is intervention/replacement; Y is final-answer correctness; and Y_H is harmful incumbent replacement.

The confirmatory outcome is:

[
Y_{H,i}=I(P0_i\ correct \land I_i=replacement \land final_i\ incorrect).
]

The predictor must contain no outcome-derived information.

## 2. Prediction unit

One eligible decision instance is one unique agent question/database decision for which the system produces an incumbent P0 result and a candidate intervention/replacement decision.

Each decision instance receives a stable immutable decision_id linking question/schema, baseline B, exact decision-time evidence, intervention state, final correctness, Y_H, and X_W annotations.

Before collection is frozen, the cohort generator must identify whether multiple decision instances share a database/schema, question, model run, perturbation, execution trace, or other common generation unit. The actual dependence structure must be recorded before outcome analysis.

## 3. Eligible population

The primary population should be defined prospectively as all fresh benchmark decision instances that enter the P2 replacement-policy pathway and for which the frozen baseline B and decision-time evidence can be captured before downstream intervention/outcome information is available.

Eligibility must not depend on X_W or Y_H.

Exclusions must be mechanical and recorded before outcome analysis. No case may be excluded because of its outcome or because X_W is difficult to annotate.

## 4. Freshness and historical separation

The confirmatory cohort must use a newly versioned and cryptographically hashed case manifest.

Historical P1/P6 cases must not be silently mixed into the primary confirmatory cohort. Any overlap must be detected mechanically and handled under a pre-frozen rule.

Historical P1/P6 remains discovery/mechanism evidence.

## 5. Decision-time evidence capture

For each decision instance, capture the evidence at the exact point at which the replacement policy could make its decision.

At minimum preserve: question, schema/database identifier, baseline fields, execution status, returned column names, returned rows, row count, and column count, plus any information actually displayed to the intervention policy.

Do not augment the annotator-facing evidence with gold SQL, reference answer, P0 correctness, challenger correctness, replacement decision, final correctness, Y_H, or post-hoc evaluator outputs.

Additional machine telemetry may be retained in a separate provenance artifact.

## 6. Temporal ordering

The pipeline must enforce and record:

[
E^{decision-time} ightarrow B ightarrow replacement\ decision ightarrow final\ outcome
]

X_W annotation may occur after evidence capture but must be outcome-blinded and must never alter the original decision/evidence artifact.

## 7. Baseline B

The current frozen baseline contains execution_ok, row_count, and column_count.

B remains frozen for the confirmatory comparison. No additional evidence-derived feature may be introduced after outcome inspection. Any baseline change requires a new versioned specification and methodological amendment.

## 8. X_W measurement

The current W1-W7 codebook remains controlling.

For each eligible evidence-bearing decision instance, rater A and rater B independently annotate the frozen evidence packet while blinded to P0 correctness, intervention/replacement, final correctness, Y_H, generated/reference SQL, and post-hoc labels.

Raw annotations remain immutable. The frozen UNCLEAR normalization rule is then applied deterministically.

## 9. NO_USABLE_EVIDENCE and missing X_W

NO_USABLE_EVIDENCE means X_W is missing, not zero.

The preferred design is to capture usable decision-time evidence for every eligible outcome-bearing decision instance. If unavoidable missingness remains, its treatment must be frozen before outcome analysis and applied consistently to M0 and M1. Post-hoc convenient complete-case deletion is not acceptable.

## 10. Outcome construction

Only after decision-time predictor/evidence artifacts are immutable should P0 correctness, replacement occurrence, final-answer correctness, and Y_H be derived.

The outcome derivation must be deterministic and separately versioned. The annotator-facing packet must never expose these fields.

## 11. Leakage barrier

Forbidden from X_W construction: generated SQL, reference SQL, reference answer, P0 correctness, challenger correctness, replacement/intervention decision, final correctness, Y_H, post-hoc evaluator labels, and any field created after the replacement decision.

Forbidden from B unless explicitly frozen in a new version: X_W, witness counts, evidence length, lexical overlap, row-value uniqueness/count features, or any evidence-derived feature selected after outcome inspection.

## 12. Provenance architecture

Each decision instance should produce a provenance bundle containing at least:

[
{decision_id,manifest_hash,code_version,runtime_manifest,evidence_hash,B_hash,annotation_packet_hash,rater_response_hash,outcome_record_hash}
]

Hashes must be recorded without exposing forbidden fields to annotators. Raw artifacts are immutable after lock. Corrections create new versions rather than overwriting scientific artifacts.

## 13. Rater blinding and independence

Raters receive separate packet streams and cannot see each other's labels, outcomes, correctness, intervention state, generated/reference SQL, or post-hoc evaluation.

Randomized packet order is not evidence of independence. Independence must be documented by explicit rater attestation and operational separation.

## 14. Reliability analysis

Primary descriptive reliability: raw obligation-level agreement, Cohen's kappa, contingency tables, Gwet AC1 sensitivity analysis, prevalence/marginal distributions, and uncertainty intervals where appropriate.

Reliability analysis must be outcome-blind. No coefficient threshold automatically establishes construct validity.

## 15. Statistical analysis is deliberately not yet frozen

Before the first confirmatory outcome analysis, separately freeze: predictor parameterization, model family, regularization/penalization, missing-X_W treatment, primary proper scoring rule, secondary metrics, outer resampling design, dependence/cluster unit, model tuning procedure, and uncertainty procedure.

## 16. Primary incremental-validity target

The comparison remains:

[
M_0=f(B)
]

versus

[
M_1=f(B,X_W).
]

The intended primary estimand is:

[
Delta_L=E[L(Y_H,p_0)]-E[L(Y_H,p_1)]
]

where both predictions are out of sample on the same evaluation observations.

Positive Delta_L means M1 has lower predictive loss.

The exact scoring rule is not frozen by this document.

## 17. Evaluation design

The final protocol should ensure identical outer evaluation observations for M0 and M1; preprocessing fit only inside training folds; no tuning using outer test outcomes; paired per-case loss differences retained; and dependence units kept together where required.

If tuning is required, nested resampling is preferred. The final choice must be frozen before outcome-bearing model selection.

## 18. Sample-size gate

No arbitrary participant/event target is frozen here.

Historical development data contained 21 harms among 330 eligible cases (approximately 6.36%), but this historical discovery rate must not automatically be treated as the future cohort event rate.

Prediction-model sample size should be justified using anticipated outcome proportion, candidate predictor parameter count, expected predictive performance, and overfitting/precision considerations rather than a fixed events-per-variable rule alone. Riley et al. recommend a context-specific approach for binary prediction models. citeturn0search0turn0search2

Therefore a separate P2-C1.4-S sample-size analysis must be completed before outcome collection is declared confirmatory. It must state the target population, anticipated Y_H prevalence and source, candidate predictor parameters, anticipated performance assumptions, acceptable optimism/shrinkage/precision criteria, required eligible units/events, feasibility, and stopping rule.

## 19. Why a new cohort is scientifically preferable

P2-C1.3 established that historical reconstruction cannot provide the required X_W/Y_H alignment.

A new cohort directly creates:

[
oxed{same\ decision ightarrow same\ evidence ightarrow X_W ightarrow later\ Y_H}
]

rather than attempting retrospective recovery.

## 20. Stopping rules

Stop and audit if decision-time evidence is missing systematically; intervention decisions cannot be linked to immutable IDs; outcome derivation requires undocumented manual judgment; X_W packets expose forbidden outcome information; historical overlap cannot be determined; evidence artifacts change after annotation; or runtime nondeterminism prevents reproducible decision-instance identification.

No scientific parameter may be altered automatically to make the cohort pass.

## 21. Reporting requirements

The eventual manuscript should report cohort construction, exclusions, prediction unit, temporal ordering, evidence preservation, X_W annotation/blinding, rater independence, missingness, outcome prevalence, model specification, resampling, discrimination, calibration, proper scoring loss, paired incremental loss, uncertainty intervals, and limitations.

This is consistent with TRIPOD+AI guidance distinguishing training/tuning from evaluation data and recommending reporting of discrimination and calibration. citeturn0search3

## 22. Gate disposition

**P2-C1.4 design: READY FOR PRE-COLLECTION AUDIT, NOT YET FROZEN.**

Next required gates:

1. P2-C1.4-S — sample-size/event-rate feasibility attack;
2. P2-C1.4-M — model-family and primary scoring-rule freeze;
3. P2-C1.4-R — runtime/evidence-preservation qualification;
4. fresh aligned outcome-bearing cohort collection.

No confirmatory outcome analysis is authorized by this document.
