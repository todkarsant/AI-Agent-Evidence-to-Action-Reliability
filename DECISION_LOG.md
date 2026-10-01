# Decision Log

This file records material methodological and research decisions. Decisions should be appended rather than rewritten.

## 2026-09-18 — Project 2 canonical repository established

**Decision:** Establish `AI-Agent-Evidence-to-Action-Reliability` as the canonical source of truth for Project 2.

**Reason:** Separate the research program from Project 1 implementation and from the existing LLM evaluation/observability platform.

**Effect:** Future methodological decisions, runtime provenance, experiments, failures, and publication records are versioned here.

## 2026-09-18 — Working project identity

**Decision:** `AI Agent Evidence-to-Action Reliability`

**Repository:** `AI-Agent-Evidence-to-Action-Reliability`

**Scope note:** The project is about AI agents; current experiments are LLM-mediated, but the repository name is intentionally not tied to a single model family.

## Methodological policy — preserve falsification

**Decision:** Failed constructs, negative results, and rejected novelty claims remain permanently documented.

**Reason:** Avoid retrospective confirmation bias and preserve auditability.

## Methodological policy — P1/P6 is discovery evidence

**Decision:** Historical P1/P6 results are not reused as confirmatory P2 evidence.

**Reason:** P2 confirmatory claims require a fresh and properly frozen evaluation design.

## Methodological policy — decision-time vs post-hoc information

**Decision:** Features intended to represent decision-time information must not depend on gold SQL, gold answer, P0 correctness, challenger correctness, replacement status, or other post-hoc information.

**Reason:** Such leakage would invalidate predictive-validity interpretation.

## Methodological policy — exact reproducibility claims

**Decision:** Do not claim byte-identical historical model reproduction unless the historical artifact digest is available and matches.

**Current state:** Historical digest unavailable; recovered model digest recorded separately.

## 2026-09-21 — P2-C1.3 historical cohort reconstruction rejected

**Decision:** Do not fuse the current 12-case X_W measurement cohort with the historical 330/91 P1/P6 outcome cohorts.

**Reason:** The same-unit decision-time evidence required for independent X_W annotation is not preserved in the historical scientific record in the required form. The current X_W cohort is intentionally non-overlapping with the historical outcome units.

**Effect:** Historical P1/P6 remains discovery/mechanism evidence. The 91-case holdout is not called external validation for X_W. Confirmatory M0/M1 modeling remains blocked.

**Next:** Build a new outcome-bearing cohort with frozen B, preserved decision-time evidence, independent X_W annotation, and Y_H linkage.

## 2026-09-21 — Publication evidence-chain requirement

**Decision:** Maintain a living paper draft in parallel with the methodological gate ledger.

**Reason:** Every substantive paper claim must remain traceable to a dated methodological artifact, raw evidence/provenance, analysis, and final claim.

**Effect:** The current paper draft explicitly records negative results and the P2-C1.3 reconstruction failure rather than omitting them.

## 2026-09-30 — Runtime3 pathological-SQL recovery

**Decision:** Adopt a bounded, detector-gated single repair for runaway self-repeating SQL generation (`P2-C1.4-RUNTIME3-PATHOLOGICAL-SQL-RECOVERY-AMENDMENT-2026-09-30`).

**Reason:** A provider-boundary runtime pathology (000091) blocked qualification.

**Effect:** Recovery is disclosed per decision and is never used as a predictor, covariate or outcome.

## 2026-10-01 — Missingness and eligibility

**Decision:** Every frozen decision carries one mechanical `record_status` (EVALUABLE / E1 / E2 / E3E4). The primary analysis uses EVALUABLE decisions with usable evidence. The S1/S2 sensitivity analyses and a systematic-missingness audit are mandatory (`P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01`).

**Reason:** Acquisition `36691960508` failed on a reference SQL the evaluator could not execute and on unrecovered runtime failures. Aligned Outcome Cohort Design §9 requires missingness treatment to be frozen before outcome analysis.

**Effect:** No synthetic outcomes. Two implementation defects were fixed: swallowed P0 runtime failures, and the shard manifest hash.

## 2026-10-01 — Qualification gate G3 replaced

**Decision:** Replace "200/200, 0 runtime failures" with integrity checks plus a 5% runtime-failure ceiling: 10/200 for qualification and 431/8,638 before the cohort lock. Acquisition also requires science code identical to the qualified commit (`P2-C1.4-QUALIFICATION-GATE-G3-AMENDMENT-2026-10-01`).

**Reason:**
- The missingness amendment removed the implicit crash-based enforcement of the old gate.
- The old gate cannot be verified retrospectively.
- An unbounded gate would admit a degraded run.

**Effect:** The ceiling was fixed before any status count of qualification `36847267797` was seen. The 5% value is the author's judgement, not part of the original design.

