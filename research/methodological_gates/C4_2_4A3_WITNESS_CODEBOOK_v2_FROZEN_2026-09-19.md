# C.4.2.4-A.3 — Evidence-Witness Codebook v2

**Status:** FROZEN FOR NEW HUMAN ANNOTATION COHORT
**Freeze date:** 2026-09-19
**Version:** v2 / W1-W7

## Construct

Candidate score:

X_W = mean over applicable witness dimensions of w_j(Q,S,R)

where w_j is an observable witness indicator. It asks only whether the displayed decision-time evidence exposes information needed to inspect the corresponding analytical obligation. It must never encode hidden SQL correctness.

## Witness dimensions

### W1 — Selection witness
Supported only when the evidence visibly exposes the predicate-bearing attribute/value(s) needed to inspect the requested restriction. A result's existence or plausibility is not a selection witness.

### W2 — Projection witness
Supported when requested output attributes are visibly present at the required granularity. Column count alone is insufficient; field identity matters.

### W3 — Aggregation witness
Supported when the evidence visibly exposes the requested aggregate value and an interpretable field/label indicating the requested operation. It does not establish population correctness.

### W4 — Grouping witness
Supported when the evidence visibly exposes the grouping key and corresponding per-group result structure required by the question.

### W5 — Ordering witness
Supported when displayed evidence exposes the comparison field and displayed ordering relationship. It does not establish global top-k completeness.

### W6 — Extremum witness
Supported when evidence exposes a candidate extreme value and the comparison field needed to inspect an extremum claim. It does not establish global maximality/minimality.

### W7 — Join/linkage witness
Supported when displayed evidence exposes the entity identifiers/attributes needed to inspect the requested cross-entity relationship.

Completeness/cardinality is not a witness dimension and is not part of X_W.

## Scoring

- 1 = observable witness present
- 0 = required witness absent or ambiguous
- NO_USABLE_EVIDENCE = execution failed / no interpretable result

Only obligations explicitly entailed by the natural-language question are applicable. If materially different interpretations exist, score 0 and record the ambiguity reason.

Empty results remain valid evidence and must be judged rather than discarded.

## Blinding boundary

Annotators must not use generated SQL, reference SQL, reference answers, baseline correctness labels, intervention/replacement decisions, downstream outcomes, or post-hoc evaluator labels.

## Reliability requirement

Two genuinely independent outcome-blinded raters annotate separately. Raw disagreement is retained. Any adjudication is a separate artifact and cannot replace the primary raw labels.

Primary reliability reporting: obligation-level percent agreement, Cohen's kappa, Gwet AC1 sensitivity analysis, contingency tables, prevalence/mix, and uncertainty intervals where appropriate. No automatic coefficient threshold constitutes a PASS.

## Freeze rationale / attack record

The prior semantic-sufficiency construct was rejected because result-only evidence cannot generally establish hidden predicate correctness, global completeness, join correctness, or aggregate-population correctness. The W1-W7 redesign restricts the claim to observable evidence witnesses and explicitly disclaims those hidden properties.

The 2026-09-19 literature collision refresh found current work on generic reliability, evidence sufficiency/abstention, evidence grounding, provenance-sensitive action selection, and evidence tracing. Those streams do not establish this exact W1-W7 observable-witness construct as an incremental predictor of consequential incumbent replacement harm. This is a novelty-boundary statement, not proof of novelty.

The construct is now frozen for the new human annotation cohort. It must not be retroactively described as the frozen v1 codebook used by the unrecoverable historical packet claim.
