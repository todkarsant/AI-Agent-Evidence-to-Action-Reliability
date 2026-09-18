# C.4.2.4-A.2 — Observable Evidence-Witness Construct Redesign + Novelty Collision Attack

**Date:** 2026-09-18  
**Status:** COMPLETED — R2 SURVIVES IDENTIFIABILITY BUT FAILS AS A STANDALONE NOVEL CONSTRUCT

## 1. Redesign

C.4.2.4-A.1 rejected semantic sufficiency because result-only evidence cannot generally prove hidden predicates, completeness, extrema, or join semantics.

Candidate R2:

X_W = (1/K) sum_j w(g_j,R,S)

where w=1 means the displayed decision-time evidence contains an observable witness needed to inspect the stated obligation under a frozen evidence contract; w=0 means that witness is absent or ambiguous.

R2 does not claim that the hidden SQL was correct.

## 2. Construct boundary

R2 measures whether decision-time evidence exposes the observable information required to inspect an analytical obligation.

It does not measure generated-query correctness, gold-answer correctness, semantic equivalence, causal provenance, authorization, or final-action correctness.

Example: for “Find all male student IDs”, a result containing only StuID can expose the requested ID witness but not a gender/predicate witness. R2 records that observable gap; it does not infer that the hidden SQL failed.

## 3. Candidate witness dimensions

| Witness | Observable requirement |
|---|---|
| W1 Selection witness | Evidence exposes the attribute/value needed to inspect the requested restriction, or an independently defined result-level witness. |
| W2 Projection witness | Requested output attributes are present at the required granularity. |
| W3 Aggregation witness | Evidence exposes the aggregate value and enough labeling/schema context to identify the requested operation; it does not assert population correctness. |
| W4 Grouping witness | Evidence exposes the requested per-group key/value structure. |
| W5 Ordering witness | Evidence exposes ordered candidate values/keys sufficient to inspect the displayed ordering relation. |
| W6 Extremum witness | Evidence exposes candidate extreme value and comparison field; it does not assert global maximality/minimality. |
| W7 Cardinality witness | Evidence exposes requested count/row cardinality when cardinality itself is observable; it does not assert completeness of an open-world result set. |
| W8 Join/linkage witness | Evidence exposes linked entity identifiers/attributes needed to inspect the requested relationship. |

The central change is that global semantic claims are not encoded as result-only facts.

## 4. Identifiability attack

R2 survives the A.1 impossibility attack because it asks an observable question.

For fixed Q,S,R, “is the required witness visible in R?” is determined by R and the frozen codebook.

The latent question “was the hidden SQL semantically correct?” remains outside the construct. Two hidden SQL states can therefore differ in correctness while having identical X_W. That is acceptable because correctness is deliberately not what X_W measures.

## 5. Novelty collision attack

### Collision 1 — Evidence sufficiency

Recent 2026 work explicitly studies evidence sufficiency as a control signal. The Evidence Sufficiency Benchmark evaluates supportive, partially supportive, irrelevant, absent, and conflicting evidence. SURE-RAG treats evidence sufficiency as a set-level property and aggregates coverage, relation strength, disagreement, conflict, and retrieval uncertainty. Learning Evidence Sufficiency Boundaries studies abstention at the point where evidence becomes sufficient.

Collision: evidence sufficiency is already an active research construct.

Decision: do not claim novelty for evidence sufficiency itself.

### Collision 2 — Evidence coverage

MAP-Law explicitly computes Element Coverage and Evidence Coverage and uses those signals for retrieval control. Recent incident-remediation work also reports an Evidence Coverage Score measuring the proportion of causal claims corroborated by observable telemetry.

Collision: evidence coverage is already a measurable quantity.

Decision: do not claim novelty for the coverage score alone.

### Collision 3 — Evidence-grounded agent action

Recent work studies external knowledge grounding for agents and the transition from evidence to action. Provenance-sensitive action-selection work explicitly tests whether changing source authority changes tool choices.

Collision: evidence supporting an action is already an active research direction.

Decision: do not claim that linking evidence to action is itself novel.

### Collision 4 — Provenance / decision traces

Recent auditability work defines evidence and decision-trace planes including provenance, freshness, retrieval identifiers, tool invocations, intermediate checks, and policy evaluations. SARA separates action induction from runtime authorization and records action-origin provenance and audited evidence.

Collision: provenance-aware action authorization is occupied.

Decision: do not claim provenance tracking or evidence-backed authorization as the novelty.

### Collision 5 — Claim-level evidence verification

Recent work uses claim-level evidence coverage, supporting-fact verification, evidence-chain evaluation, and abstention when support is insufficient.

Collision: decomposing a question/claim into evidence obligations is not automatically novel.

## 6. Remaining potential research seam

The defensible seam is narrower:

“Whether an independently measured, decision-time observable evidence-witness coverage score predicts consequential incumbent-replacement harm and provides incremental predictive validity beyond existing decision-time analytical signals.”

The novelty is therefore not the witness score itself.

The potential contribution is the empirical relationship:

P(Harm | B, X_W)

and specifically whether X_W adds out-of-sample predictive information beyond B.

## 7. Remaining adversarial attacks

### A2-1 — Redundancy
If X_W is mostly a deterministic transformation of row count, column count, execution status, or result shape, incremental validity may disappear.

### A2-2 — Decision proximity
X_W must be measured from information available at the exact authorization boundary.

### A2-3 — Outcome leakage
X_W must not use P0 correctness, gold SQL, gold answer, challenger output, replacement result, or post-hoc verification.

### A2-4 — Mechanical-feature attack
If X_W is reconstructible almost perfectly from existing baseline trace fields, apparent incremental validity may merely be relabeling.

### A2-5 — Construct substitution
If X_W becomes a generic groundedness/relevance score, novelty collapses into existing RAG evaluation.

### A2-6 — Action coupling
The score must be frozen before outcome analysis and must not be optimized to suppress intervention.

## 8. Redesign decision

Original X_E: REJECTED because semantic sufficiency is not identifiable from result-only evidence.

R2 / X_W:
- Identifiable: YES
- Standalone novelty: NO
- Potential research novelty: CONDITIONAL

R2 is viable as a measurement construct, but it must not be presented as a novel evidence-sufficiency or evidence-coverage metric.

## 9. Next gate

C.4.2.4-A.3 — Witness Codebook v2 + Mechanical-Redundancy Attack

Required:
1. freeze a narrower W1–W8 codebook;
2. define exactly what “observable witness” means;
3. test independence from SQL correctness;
4. quantify mechanical derivability from existing baseline trace fields;
5. remove dimensions duplicating baseline variables;
6. rerun novelty collision search;
7. only then perform human reliability.

## 10. Literature limitation

This is a current novelty collision search, not a systematic review. The search covered 2026 work on evidence sufficiency, evidence coverage, external knowledge grounding, provenance-sensitive action selection, and evidence-verified tool execution. Absence from these search results is not evidence that no collision exists.

## Gate verdict

C.4.2.4-A.2: PASS WITH MAJOR NOVELTY RESTRICTION.

R2 survives identifiability.

R2 does not survive as a standalone novelty claim.

The only potentially defensible seam is the incremental predictive validity of independently measured decision-time evidence-witness coverage for consequential incumbent-replacement harm.

No confirmatory predictive-validity claim should be made until A2-1 through A2-6 are tested.
