# C.4.2.4-A.3 — Evidence-Witness Codebook v2 Draft

**Status:** DRAFT — NOT FROZEN  
**Purpose:** remove non-identifiable semantic claims and mechanically redundant dimensions before any human reliability cohort.

## Construct

Candidate score:

X_W = mean over applicable witness dimensions of w_j(Q,S,R)

w_j is an observable witness indicator. It asks only whether the displayed decision-time evidence exposes information needed to inspect the corresponding analytical obligation.

It must never encode whether hidden SQL was correct.

## Proposed dimensions

### W1 — Selection witness
Supported only when the evidence visibly exposes the predicate-bearing attribute/value(s) needed to inspect the requested restriction.

Examples:
- Question: students with age > 20.
- Evidence containing only student IDs: W1 = 0.
- Evidence containing student ID + age values: W1 may be 1 if the requested predicate can be inspected directly.

A result's existence or plausibility is not a selection witness.

### W2 — Projection witness
Supported when requested output attributes are visibly present at the required granularity.

Column count alone is insufficient; field identity matters.

### W3 — Aggregation witness
Supported when the evidence visibly exposes the requested aggregate value and an interpretable field/label indicating the requested operation.

W3 does not establish that the aggregate was computed over the correct population.

### W4 — Grouping witness
Supported when the evidence visibly exposes the grouping key and corresponding per-group result structure required by the question.

### W5 — Ordering witness
Supported when displayed evidence exposes the comparison field and the displayed ordering relationship.

W5 does not establish global top-k completeness.

### W6 — Extremum witness
Supported when the evidence exposes a candidate extreme value and the comparison field needed to inspect an extremum claim.

W6 does not establish that the candidate is globally maximal/minimal.

### W7 — Join/linkage witness
Supported when the displayed evidence exposes the entity identifiers/attributes needed to inspect the requested cross-entity relationship.

### Removed W8 — Completeness/cardinality
Removed from the candidate score.

Reason: simple cardinality is already represented by existing row-count trace data, creating mechanical redundancy; open-world completeness is not identifiable from result-only evidence.

## Scoring states

- 1 = observable witness present
- 0 = required witness absent or ambiguous
- NO_USABLE_EVIDENCE = execution failed / no interpretable result

No score may be assigned using generated SQL, gold SQL, gold answer, P0 correctness, challenger output, replacement outcome, or post-hoc verification.

## Critical boundary

X_W is an evidence-observability measure, not a correctness measure.

A high X_W may coexist with an incorrect query.
A low X_W may coexist with a correct query whose output omits the fields needed for independent inspection.

This distinction is intentional.

## Freeze condition

Do not freeze v2 until the mechanical-redundancy attack and current-literature collision attack are complete.
