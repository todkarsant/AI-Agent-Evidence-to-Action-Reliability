# C.4.2.4-A — v2 Applicability / N-A Operationalization Audit

Date: 2026-09-20
Status: NON-CONFIRMATORY DESIGN AUDIT

## Purpose

Determine, before human annotation, which W1-W7 dimensions are conceptually applicable to each of the 12 frozen cases, and identify where the current packet schema needs to distinguish non-applicability from an applicable-but-unsupported witness.

This audit does not assign human labels and does not change the frozen cohort.

## Proposed applicability map

| Case | W1 | W2 | W3 | W4 | W5 | W6 | W7 | Primary reason |
|---|---|---|---|---|---|---|---|---|
| C423_0091 | A | A | A | A | N/A | N/A | A | Selection by temperature condition; requested IDs; average by ZIP; trip-weather linkage |
| C423_0021 | N/A | A | A | N/A | N/A | A | N/A | Requested max/min aggregate over transit passengers |
| C423_0061 | N/A | A | A | A | A | A | A | Most visits requires count/group/order/extremum and engineer-visit linkage |
| C423_0071 | N/A | A | A | A | A | A | A | Top 3 by award count requires projection, count, grouping, ordering, extremum and linkage |
| C423_0041 | N/A | A | N/A | N/A | N/A | N/A | A | Requested apartment number and booking dates require apartment-booking linkage |
| C423_0081 | N/A | A | A | A | A | A | A | Most assessment notes requires count/group/order/extremum and student-note linkage |
| C423_0001 | A | UNCLEAR | N/A | N/A | N/A | N/A | A | VLDB/year restriction plus publication-conference linkage; requested output attributes are not explicitly enumerated |
| C423_0031 | A | A | N/A | N/A | N/A | N/A | N/A | Male restriction and requested student IDs |
| C423_0011 | A | A | N/A | N/A | N/A | N/A | A | Activity restriction, requested first names, faculty-activity linkage |
| C423_0111 | A | A | N/A | N/A | N/A | N/A | A | Two price predicates plus publisher-publication relationship |
| C423_0051 | N/A | A | N/A | N/A | N/A | N/A | A | Requested architect attributes plus architect-mill relationship |
| C423_0101 | A | A | A | N/A | N/A | N/A | A | Height restriction, requested average, and body-builder/people linkage |

Legend: A = conceptually applicable; N/A = not entailed by the question; UNCLEAR = applicability depends on how the requested output 'papers' is operationalized.

## Critical findings

### 1. Applicability is not equivalent to witness support

A dimension can be applicable even when the displayed evidence does not contain its witness. For example, C423_0031 entails W1 because the question explicitly requires a male restriction, but the result contains only StuID. The appropriate human label is therefore an applicable W1 with witness absent/ambiguous, not W1=N/A.

### 2. C423_0001 exposes an output-scope ambiguity

The question asks for 'the papers on VLDB conference after 2000' without explicitly naming output attributes. The displayed result has eight columns. Whether W2 is applicable depends on the frozen interpretation of what constitutes the requested paper representation. This should be resolved before humans annotate.

### 3. NO_USABLE_EVIDENCE does not remove conceptual applicability

Five cases have NO_USABLE_EVIDENCE. Their applicable obligations can still be identified conceptually, but the annotation state must remain NO_USABLE_EVIDENCE rather than being converted into binary 0/1 witness judgments.

### 4. W5 and W6 need explicit distinction

Questions using 'most', 'highest', 'top 3', or similar language can entail both an ordering/top-k obligation and an extremum relationship. The codebook should make clear that W5 concerns the displayed ordering relationship while W6 concerns the displayed candidate extreme and comparison field. Humans should not infer global completeness/maximality.

### 5. W7 is the main relationship witness

Cases involving two tables/entities require W7 when the requested result depends on a cross-entity relationship. W7 should not be replaced by W1 merely because the relationship appears as a predicate.

## Operational recommendation

Before human annotation, the annotation form should explicitly separate two questions:

1. Is this witness dimension applicable to the question? YES / NO.
2. If applicable, is the observable witness present? YES / NO / AMBIGUOUS.

For execution failure, the case-level status should remain NO_USABLE_EVIDENCE and substantive witness scoring should not be forced.

This is preferable to overloading W1-W7 values with N/A because the current codebook already defines 0 as absent or ambiguous. A single binary field cannot simultaneously encode 'not applicable' and 'applicable but unsupported' without losing information.

## Gate implication

This audit identifies an operational specification issue, not a demonstrated construct failure.

However, because the issue can cause two independent human raters to use different denominators, it must be resolved before confirmatory human reliability statistics are collected.

If the annotation schema is changed, create a new version and new packet cohort rather than silently modifying the frozen v2 packets.

Human validation remains blocked until this applicability representation is frozen.
