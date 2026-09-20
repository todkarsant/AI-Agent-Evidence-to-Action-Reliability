# C4.2.4-A Human Annotation Reliability Audit — 2026-09-21

## Status

**Human-rater provenance requirement is satisfied by explicit independent-rater attestation. The previously unresolved UNCLEAR applicability issue has now been attacked and frozen in `C4_2_4A_UNCLEAR_XW_OPERATIONAL_RULE_FREEZE_2026-09-21.md`; C.4.2.4-A is resolved and P2-C1.2 confirmatory X_W construction is unblocked, subject to the remaining preregistered statistical/modeling gates.**

Two response files were received and mechanically validated against the frozen W1-W7 response schema and the live frozen packet cohort.

## Inputs

- Frozen packet version: C4_2_4A_WITNESS_V2_2026-09-19
- Rater A packet SHA-1: 73ac1ae0d3118e62be992839389a6a64c1bb19bd
- Rater B packet SHA-1: ead6a8750ec113c1d1317506da9548f895bb2ada
- Frozen codebook SHA-1: fc33316b172915244e127d050142bb3bac0534b5
- Uploaded A SHA-256: ba1f39268e1b3e3dc223ea91f12c7fc948d370d9fde6e2ff9a96c2ab6dd40028
- Uploaded B SHA-256: 0d8b2e7d8b1408a77561c99e4da32c150313c4c87d2a84bd4f2e13b36ac7f7e8

## Mechanical validation

- 12/12 expected case IDs present in each response.
- Both response files pass the response-schema structural constraints.
- NO_USABLE_EVIDENCE cases contain null applicability/witness fields.
- SUCCESS cases obey the applicability-to-witness dependency.
- No forbidden scientific fields were supplied.

## Frozen-packet status reconciliation

All 12 case statuses match the corresponding frozen packet execution status for both raters.

## Reliability calculations

### Applicability

Across the 8 SUCCESS cases there are 49 populated W1-W7 applicability judgments per rater:

- YES: 24
- NO: 22
- UNCLEAR: 3
- Raw agreement: 49/49 = 100%
- Cohen's kappa: 1.00

Applicability contingency table:

| | B YES | B NO | B UNCLEAR |
|---|---:|---:|---:|
| A YES | 24 | 0 | 0 |
| A NO | 0 | 22 | 0 |
| A UNCLEAR | 0 | 0 | 3 |

### Witness labels

For applicable YES/UNCLEAR dimensions, there are 27 populated binary witness judgments per rater:

- PRESENT: 11
- ABSENT_OR_AMBIGUOUS: 16
- Raw agreement: 27/27 = 100%
- Cohen's kappa: 1.00
- Gwet AC1: 1.00

Witness contingency table:

| | B PRESENT | B ABSENT_OR_AMBIGUOUS |
|---|---:|---:|
| A PRESENT | 11 | 0 |
| A ABSENT_OR_AMBIGUOUS | 0 | 16 |

These statistics describe the submitted labels only. They do not establish scientific validity, correctness of the labels, or rater independence.

## Independence audit

The two uploaded files have different raw SHA-256 hashes because their case ordering differs, but their annotation payloads are **identical after canonical case-ID normalization**. Both also contain the same wording in the sole non-empty case note for C423_0111.

This is **not evidence that either rater copied the other**. It is, however, sufficient to say that the JSON artifacts themselves do not establish that the two annotations were produced independently.

The frozen protocol requires two genuinely independent raters. The submitted response schema contains no cryptographic provenance, timestamped attestation, or independent-rater declaration that can establish this property.

Therefore the reliability coefficients are reported as descriptive results of the submitted annotation sets, but **are not used to close C.4.2.4-A**.

## Independent-rater attestation

On 2026-09-21, the user supplied an explicit protocol attestation that **Human A and Human B each independently completed their annotations without seeing or coordinating the other rater's annotations**. This directly addresses the previously unestablished independence requirement for the two-rater cohort.

This is an attestation of the annotation process, not a cryptographic proof of independence. The raw response files and their hashes remain preserved as the primary artifacts; the attestation is recorded as provenance evidence and is not treated as a statistical result.

## Frozen UNCLEAR → X_W operational rule

The implementation-ambiguity issue identified for C423_0111 has been resolved before confirmatory outcome modeling. `UNCLEAR` is not a substantive X_W state. Applicability is determined from the natural-language question and frozen W1-W7 definitions only. Hidden/generated implementation uncertainty cannot create applicability uncertainty. Genuine natural-language ambiguity follows the frozen codebook rule: score 0 and retain the dimension in the X_W denominator with an ambiguity reason. Implementation-only ambiguity is deterministically resolved to YES or NO from the natural-language question.

For C423_0111, W3/W4/W6 are implementation-only ambiguity and therefore resolve to N/A/NO; W1=0, W2=1, W7=0. The resulting frozen confirmatory score is X_W = 1/3 (approximately 0.3333). This rule was frozen without using outcome variables.

See `research/methodological_gates/C4_2_4A_UNCLEAR_XW_OPERATIONAL_RULE_FREEZE_2026-09-21.md`, commit `13dbfb4f64e0dc16867cd5f8e421b54ef829f70a`.

## Scientific interpretation

The submitted annotations are internally coherent and exactly concordant. No disagreement-driven codebook failure is observed in these submissions.

However, the independent-human boundary is a provenance requirement, not a statistic. Perfect agreement cannot substitute for evidence that the two raters independently completed the frozen packets.

A separate methodological issue remains for confirmatory X_W construction: C423_0111 contains UNCLEAR applicability for W3/W4/W6. The applicability audit permits the UNCLEAR state, while the frozen codebook states that materially different interpretations require a zero score and an ambiguity reason. This needs an explicit pre-confirmatory rule for mapping UNCLEAR applicability into X_W; it must not be decided after looking at the outcome.

## Disposition

- Exact uploaded A and B response files: **PRESERVED IN THE CHAT UPLOADS**
- Mechanical validity: **PASS**
- Frozen-packet status reconciliation: **PASS**
- Descriptive inter-rater agreement: **100%**
- Descriptive Cohen kappa: **1.00**
- Descriptive Gwet AC1: **1.00**
- Independent-rater provenance: **SATISFIED BY EXPLICIT USER-SUPPLIED INDEPENDENT-RATER ATTESTATION**
- C.4.2.4-A: **OPEN — X_W UNCLEAR MAPPING RULE REMAINS**
- P2-C1.2 confirmatory modeling: **BLOCKED PENDING PRE-OUTCOME X_W RULE**

No outcome-dependent feature selection, adjudication, or confirmatory predictive modeling was performed.
