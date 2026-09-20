# C.4.2.4-A — UNCLEAR → X_W Operational Rule Freeze

**Status:** FROZEN FOR CONFIRMATORY X_W CONSTRUCTION  
**Freeze date:** 2026-09-21  
**Applies to:** C4_2_4A W1-W7 witness construct, frozen human cohort  
**Parent codebook:** C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19  
**Codebook SHA-1:** fc33316b172915244e127d050142bb3bac0534b5

## 1. Decision

`UNCLEAR` is **not** a substantive X_W score and is never silently dropped.

It is a diagnostic annotation state that must be resolved by the following deterministic, outcome-blind rule before X_W is constructed:

1. **Applicability is determined from the natural-language question and the frozen W1-W7 definitions only.**
2. **Hidden implementation uncertainty does not create applicability uncertainty.** Questions about whether an unseen/generated query used aggregation, grouping, extrema, joins, filters, or another implementation are outside the construct and cannot be used to mark a dimension `UNCLEAR`.
3. If the natural-language question explicitly entails the witness dimension, set applicability to **YES** and use the observed witness label (`PRESENT` = 1; `ABSENT_OR_AMBIGUOUS` = 0).
4. If the natural-language question does not entail the witness dimension, set applicability to **NO** and exclude that dimension from the X_W denominator.
5. If the natural-language wording itself admits **materially different interpretations about whether the dimension is entailed**, the frozen codebook rule applies: **score that dimension as 0 and record the ambiguity reason**. For X_W construction, that dimension remains in the denominator so the ambiguity cannot inflate the score.
6. No applicability/X_W decision may use reference SQL, generated SQL, reference answers, correctness labels, intervention/replacement status, downstream outcomes, or post-hoc evaluator labels.
7. This rule is fixed before confirmatory outcome modeling and cannot be changed in response to observed X_W values, associations, or outcomes.

## 2. X_W construction

For a SUCCESS case:

$$
X_W = \\frac{\\sum_{j \\in A} w_j}{|A|}
$$

where `A` is the set of dimensions classified `YES` under the rule above, **plus any dimension classified as a genuine natural-language ambiguity under rule 5**.

- `YES + PRESENT` → `w_j = 1`
- `YES + ABSENT_OR_AMBIGUOUS` → `w_j = 0`
- `NO` → excluded from numerator and denominator
- genuine semantic `UNCLEAR` → `w_j = 0`, included in denominator
- implementation-only `UNCLEAR` → resolved to `YES` or `NO` from the natural-language question; it does not remain `UNCLEAR`
- `NO_USABLE_EVIDENCE` → X_W is missing/not constructed; it is **not** converted to seven zeros.

No dimension is allowed to disappear from the denominator merely because its witness is difficult to observe.

## 3. Adversarial attack

### Attack A — Drop UNCLEAR from the denominator

**Rejected.**

If an unresolved dimension were omitted, the score could increase solely because an ambiguity was encountered. That creates an information-dependent denominator and can make evidence look more sufficient when the coding problem is greater.

This also conflicts with the frozen codebook instruction that materially different interpretations receive score 0.

### Attack B — Treat every UNCLEAR as a zero

**Rejected as the universal rule.**

A universal zero would conflate two different situations:

- the question genuinely entails an obligation but the evidence fails to expose its witness; and
- the question does not actually entail that obligation, but a rater became uncertain because of hidden implementation possibilities.

The latter would incorrectly penalize cases for obligations outside X_W.

### Attack C — Let the hidden/generated implementation resolve applicability

**Rejected.**

The construct is deliberately limited to observable decision-time evidence and explicitly forbids using generated/reference SQL. Allowing hidden implementation reasoning would reintroduce the exact latent-correctness problem that motivated the W1-W7 redesign.

### Attack D — Resolve UNCLEAR after observing outcomes

**Rejected.**

This would make feature construction outcome-dependent and introduce researcher degrees of freedom into the confirmatory predictor. The operational rule therefore precedes outcome modeling and is frozen here.

Preregistration guidance emphasizes making design/analysis decisions before viewing relevant data and specifying contingencies in advance. citeturn0search7turn1search0

### Attack E — Treat all natural-language ambiguity as N/A

**Rejected.**

The frozen codebook explicitly states that when materially different interpretations exist, the dimension receives score 0 with an ambiguity reason. Converting that state to N/A would erase the prespecified conservative treatment and could increase X_W.

## 4. Application to the observed UNCLEAR case: C423_0111

Question:

> Show the publishers that have publications with price higher than 10000000 and publications with price lower than 5000000.

The prior `UNCLEAR` labels for W3/W4/W6 were based on uncertainty about whether the unseen implementation might have used aggregation/MAX/MIN or separate existence predicates.

That is **implementation uncertainty**, not natural-language applicability uncertainty.

The question does not request:

- an aggregate value or aggregation operation → **W3 = NO**
- per-group results → **W4 = NO**
- an ordering/top-k or extreme-value result → **W6 = NO**

The requested semantics are two price predicates connected to publishers/publications. Therefore the frozen operational resolution is:

- W1 = YES; witness ABSENT_OR_AMBIGUOUS → 0
- W2 = YES; witness PRESENT → 1
- W3 = NO → excluded
- W4 = NO → excluded
- W5 = NO → excluded
- W6 = NO → excluded
- W7 = YES; witness ABSENT_OR_AMBIGUOUS → 0

Thus:

$$
X_W(C423\\_0111)=\\frac{0+1+0}{3}=\\mathbf{1/3}
$$

approximately **0.3333**.

This value is determined entirely from the frozen question/codebook/evidence rule and does not use any outcome.

## 5. Consequences for the current human cohort

The two raters independently supplied the same `UNCLEAR` W3/W4/W6 labels for C423_0111. Those labels remain preserved as raw annotations.

The frozen operational rule does **not** alter the raw human records. It defines the deterministic normalization used to construct X_W for confirmatory analysis.

Because both raters made the same implementation-based ambiguity annotation, the normalized applicability and witness decisions remain identical; however, the substantive interpretation of the three dimensions is now fixed by the frozen rule rather than by post-hoc adjudication.

No new human annotation cohort is required for this rule because it does not introduce a new scientific construct, new case, new evidence, or outcome-dependent criterion; it resolves an operational ambiguity already explicitly identified before confirmatory modeling.

## 6. Gate disposition

- Human independence: **SATISFIED BY EXPLICIT ATTESTATION**
- Human response mechanical validity: **PASS**
- Frozen packet reconciliation: **PASS**
- Raw inter-rater agreement: **DESCRIPTIVELY 100%**
- UNCLEAR → X_W rule: **FROZEN**
- Outcome-dependent rule selection: **NONE**
- C4.2.4-A human-validation gate: **RESOLVED**
- P2-C1.2 confirmatory X_W construction: **UNBLOCKED**, subject to the remaining preregistered statistical/modeling gates.
- This document is the controlling operational rule for UNCLEAR handling in the current confirmatory cohort.

## 7. Non-retroactivity

This freeze applies to the current C4_2_4A W1-W7 confirmatory cohort only.

It does not rewrite the historical v1 O1-O8 construct, historical packet claims, or prior non-confirmatory analyses.

Any future change to this rule requires a new version, explicit rationale, and a separately identified deviation or new cohort.