# C.4.2.4-A.1 — Formal Observability Matrix and Redesign Attack

**Date:** 2026-09-18  
**Status:** ADVERSARIAL CONSTRUCT GATE — REDESIGN REQUIRED BEFORE HUMAN RELIABILITY

## Question

Can the candidate measurement

\[
X_E=\frac{1}{K}\sum_j v(g_j,R,S)
\]

be identified from only the question (Q), schema (S), and decision-time execution evidence (R), without reconstructing hidden SQL semantics?

### Identifiability criterion

An obligation is **identifiable from (Q,S,R)** only if materially different hidden execution semantics cannot produce the same observable (Q,S,R) while changing whether the obligation was actually satisfied.

If two such latent states are observationally indistinguishable, a result-only sufficiency judgment cannot establish the latent semantic property.

## Case-by-case matrix

| Case | Requested obligations | Evidence state | O1 | O2 | O3 | O4 | O5 | O6 | O7 | O8 | Core observability attack |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 academic | conference/year selection; paper attributes; scope | empty, 8 columns | **N** | **P** | — | — | — | — | **N** | **N** | Empty schema exposes requested fields but cannot prove conference/year restriction or completeness. |
| 02 activity_1 | activity selection; faculty first names; faculty-activity linkage | failed | N/U | N/U | — | — | — | — | — | N/U | No result evidence. |
| 03 aircraft | max/min transit passengers | 1 row, 2 explicitly named aggregate columns | — | — | **P** | — | — | **N** | **N** | — | Aggregate labels expose output form, but evidence alone does not establish population-wide extrema. |
| 04 allergy_1 | male selection; student IDs; all male students | 24 IDs only | **N** | **P** | — | — | — | — | **N** | — | Same IDs can arise from correct or incorrect hidden filtering. |
| 05 apartment_rentals | booking attributes; all bookings | failed | N/U | N/U | — | — | — | — | N/U | — | No result evidence. |
| 06 architecture | built-a-mill selection; name/nationality; architect-mill linkage; distinct scope | failed | N/U | N/U | — | — | — | — | N/U | N/U | No result evidence. |
| 07 assets_maintenance | most-visits extremum; engineer identity; visit linkage | failed | N/U | N/U | N/U | — | N/U | N/U | — | N/U | No result evidence. |
| 08 baseball_1 | award-count aggregation; top-3 ordering/extremum; player identity | 3 name/name/id rows | **N** | **P** | **N** | — | **N** | **N** | **N** | — | Three plausible rows do not prove award counts, ordering, or global top-3 status. |
| 09 behavior_monitoring | assessment-note aggregation; maximum; student identity | 1 id/name row | **N** | **P** | **N** | — | — | **N** | **N** | **P** | Identity is visible, but count/max semantics and completeness are not established. |
| 10 bike_1 | temperature threshold selection; trip IDs; all qualifying trips; trip-weather linkage; mean-temperature aggregation | 1323 IDs only | **N** | **P** | **N** | — | — | — | **N** | **N** | IDs expose target field but not temperature predicate, aggregate condition, linkage, or completeness. |
| 11 body_builder | height selection; average total score | failed | N/U | N/U | N/U | — | — | — | — | N/U | No result evidence. |
| 12 book_2 | high-price and low-price publication predicates; publisher output; publisher-publication linkage | 4 publisher names | **N** | **P** | **N** | — | — | — | **N** | **N** | Publisher names alone cannot prove either price predicate, conjunction, or population coverage. |

Legend:
- **Y** = directly identifiable from displayed evidence under the frozen rule.
- **P** = partially/witness-level identifiable, but does not establish the full semantic obligation.
- **N** = not identifiable from result evidence alone.
- **N/U** = no usable evidence because execution failed.
- **—** = obligation not materially applicable.

## Main falsification result

The matrix shows that the central semantic obligations are repeatedly **non-identifiable** from result evidence alone.

The strongest examples are:

### Selection

For C4_2_4A_04:

\[
(Q,S,R)
=
(\text{male students},\text{Student schema},\{StuID\text{ rows}\})
\]

is compatible with both:

- a result produced after correctly applying the male predicate; and
- a result containing arbitrary student IDs.

The observable state is identical while the latent predicate-satisfaction state differs.

Therefore no function of only (Q,S,R) can establish O1 in this case.

### Top-k / extremum

For C4_2_4A_08, three returned players are visible, but no evidence establishes that no fourth player has a larger award count.

Therefore O5/O6 cannot be established from the result set alone.

### Completeness

For cases using “all”, returned rows do not establish that omitted qualifying entities do not exist.

Therefore O7 generally requires a provenance/completeness witness not present in the current evidence representation.

### Join/linkage

C4_2_4A_10 exposes trip IDs, but not the weather/zip relationship that supposedly justifies selection. The output alone cannot establish the linkage predicate.

### Aggregate semantics

C4_2_4A_03 has columns named max/min transit passengers. This is stronger than an arbitrary scalar because the output schema exposes the intended aggregate labels. However, the result still does not independently demonstrate that the aggregate was taken over the complete intended population. Thus the aggregate operation is at most partially observable; population-level extremum is not.

## Construct-level conclusion

The candidate construct currently conflates two different properties:

1. **Observable evidence content** — what the returned evidence visibly contains.
2. **Semantic sufficiency** — whether the evidence proves that the requested analytical operation was correctly carried out over the intended population.

The first is observable.

The second is not generally identifiable from (Q,S,R) alone.

Therefore the original formulation

> “sufficiency of decision-time execution evidence to substantiate the requested analytical result”

is too strong for a result-only evidence representation.

## Redesign attack

Three candidate redesigns were considered.

### R1 — Add verifiable execution/provenance witnesses

Expand decision-time evidence to include independently verifiable semantic/provenance information, such as predicate/group/order/coverage witnesses.

**Advantage:** could make semantic sufficiency identifiable.

**Threat:** if the witness is simply the generated SQL or a post-hoc correctness oracle, the construct collapses into query verification and loses the intended separation.

**Status:** viable only if the witness is independently defined and does not encode gold correctness.

### R2 — Redefine X_E as Observable Evidence Coverage

Measure whether the decision-time evidence contains observable witnesses for each requested obligation, without claiming that it proves hidden query semantics.

For example:

\[
X_W=\frac{1}{K}\sum_j w(g_j,R,S)
\]

where w asks whether the displayed evidence contains the necessary observable fields/relationships/values to inspect the obligation.

**Advantage:** identifiable from the permitted information.

**Cost:** this is a weaker construct than semantic sufficiency and requires a fresh novelty attack.

**Status:** viable candidate.

### R3 — Keep the current semantic-sufficiency construct

**Status: REJECTED FOR CURRENT REPRESENTATION.**

The case-by-case non-identifiability attacks are too direct. Human agreement cannot solve a property that is not observable in the supplied information.

## Gate consequence

**C.4.2.4-A.1: FAIL FOR CURRENT X_E OPERATIONALIZATION.**

This is a methodological failure of the current measurement definition, not a failure of the broader research question.

The next valid gate is:

> **C.4.2.4-A.2 — Redesign and novelty attack of an observable evidence-witness construct.**

No human reliability study should be used to rescue the rejected result-only semantic-sufficiency definition.

Human reliability may become appropriate only after the redesigned construct passes identifiability and codebook attacks.
