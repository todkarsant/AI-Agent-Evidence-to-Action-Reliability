# C.4.2.4-A — Model-Only 23-vs-25 Forensic Reconciliation

Date: 2026-09-20
Status: COMPLETED — NON-CONFIRMATORY METHODOLOGICAL AUDIT
Human reliability gate: OPEN

## Executive finding

The historical model-only result of 23 obligation-level comparisons and the fresh model-only result of 25 applicable binary obligations are not measurements of the same annotation instrument and therefore must not be compared as if they were repeated measurements of one frozen codebook.

The repository artifacts establish:
- Historical 23-comparison pilot: C4.2.4 Evidence-Obligation Codebook v1, frozen 2026-09-18, obligation classes O1-O8.
- Current frozen cohort: Witness Codebook v2, frozen 2026-09-19, dimensions W1-W7.
- v2 explicitly removed cardinality/completeness and redesigned the construct as observable evidence witnesses.
- Historical raw model-pass CSV bytes are not currently preserved in the repository; only their SHA-256 hashes are recorded. Therefore a cell-by-cell reanalysis of the historical 23 labels is not possible from the currently preserved artifacts.

## 1. Historical 23-comparison result

The repository artifact C4_2_4A_MODEL_ONLY_ADVERSARIAL_RESULT_2026-09-18.md records:
- 12 cases
- 7 cases with interpretable execution evidence
- 5 NO_USABLE_EVIDENCE
- 23 obligation-level binary comparisons
- raw agreement: 20/23 = 86.96%
- Cohen's kappa: 0.721
- Gwet AC1: 0.756

Recorded disagreements:
1. O2 Projection — empty-result output columns versus substantive output support.
2. O6 Extremum — labeled maximum/minimum output versus independent demonstration of the population extremum.
3. O7 Cardinality/completeness — exactly three displayed rows versus completeness of a top-3 population.

These statistics are explicitly marked non-confirmatory in the repository.

## 2. Why the 23 and 25 denominators differ

### Historical instrument: v1
The 2026-09-18 codebook defines O1 Selection/filtering, O2 Projection/requested attributes, O3 Aggregation, O4 Grouping/per-group structure, O5 Ordering/top-k, O6 Extremum, O7 Cardinality/completeness, and O8 Join/entity linkage.

The historical pilot therefore allowed an obligation class that was later removed: O7 Cardinality/completeness.

### Current instrument: v2
The 2026-09-19 frozen W1-W7 codebook defines W1 Selection witness, W2 Projection witness, W3 Aggregation witness, W4 Grouping witness, W5 Ordering witness, W6 Extremum witness, and W7 Join/linkage witness.

It explicitly states that completeness/cardinality is not a witness dimension and is not part of X_W.

The v2 redesign therefore changed both the construct boundary and the possible obligation set. A denominator change is consequently expected and is not, by itself, evidence of selective analysis.

## 3. The three historical disagreements under the redesign

| Historical disagreement | v1 | v2 treatment | Reconciliation status |
|---|---|---|---|
| Empty-result requested attributes | O2 Projection | W2 Projection witness | Same broad concept, but v2 narrows the evidentiary claim |
| Maximum/minimum labeled output | O6 Extremum | W6 Extremum witness | Same broad concept, but v2 explicitly disclaims global maximality/minimality |
| Top-3 row count/completeness | O7 Cardinality/completeness | Removed | Deliberately excluded from X_W |

The third disagreement cannot be carried forward as a W1-W7 disagreement because the corresponding construct was intentionally removed.

## 4. Historical raw-data limitation

The repository packet reconstruction audit establishes that the historical Rater A/B packet bytes and historical model-pass CSV payloads are not currently preserved in a form that permits cryptographic reconstruction of the original annotation cohort.

The historical model-only result records hashes for the model-pass A CSV, model-pass B CSV, and REPORT.json, but the corresponding raw CSV payloads are not currently available in the preserved repository tree.

No attempt is made to reverse-engineer the historical 23 labels from the summary statistics. That would create reconstructed data rather than recovered data.

## 5. Fresh 25-obligation model-only pass

A separate fresh pass was performed against the currently frozen v2 packets using only the frozen codebook and displayed packet evidence.

It produced:
- 25 binary applicable-obligation judgments
- 25/25 agreement between the two fresh model passes
- Cohen's kappa = 1.000
- Gwet AC1 = 1.000

These results are not directly comparable to the historical 23-comparison statistics because the annotation instrument and obligation definitions changed.

The fresh labels are therefore retained only as a new non-confirmatory v2 codebook stress test.

## 6. Important methodological correction

The earlier statement that the new 25-result discrepancy itself required reconciliation as though both experiments used the same instrument was too strong.

The repository evidence now establishes a more precise conclusion:

The 23-versus-25 difference is primarily explained by a documented codebook transition from O1-O8/v1 to W1-W7/v2, including deliberate removal of cardinality/completeness.

What remains unrecoverable is the historical raw label-level mapping. The summary statistics alone cannot establish whether any additional scoring differences existed.

## 7. Secondary issue discovered before human annotation

The frozen v2 codebook distinguishes 1 = witness present, 0 = witness absent or ambiguous, and NO_USABLE_EVIDENCE = failed execution/no interpretable result.

It also states that only obligations entailed by the question are applicable.

The packet JSON schema, however, currently exposes W1-W7 annotation slots without a separate machine-readable applicability/N-A state.

This does not invalidate the frozen cohort, but it creates an operational question for human annotation: how will a rater represent a dimension that is genuinely non-applicable, as distinct from an applicable witness that is absent?

This must be resolved explicitly before human annotation begins. It should not be silently handled differently by different raters.

## 8. Gate status

The forensic audit does not close C4.2.4-A.

Current status:
- Historical 23-result: preserved as v1 model-only non-confirmatory
- Fresh 25-result: preserved as v2 model-only non-confirmatory
- Direct statistical comparison: not valid
- Historical raw-label reconstruction: not possible from preserved artifacts
- Current v2 cohort: remains frozen
- Human reliability: still required
- P2-C1.2 confirmatory modeling: still blocked

## 9. Required next methodological action

Before independent human annotation begins, perform a short v2 applicability/N-A operationalization audit against all 12 cases.

The purpose is not to change labels after seeing outcomes. It is to ensure both human raters receive an unambiguous representation of:
1. applicable + witness present;
2. applicable + witness absent/ambiguous;
3. non-applicable;
4. no usable evidence.

If a schema change is required, create a new version and new cohort rather than modifying the frozen v2 cohort in place.

Bottom line: the 23-vs-25 discrepancy is now explained at the instrument level. The old 23 result belongs to the retired O1-O8/v1 pilot; the new 25 result belongs to the frozen W1-W7/v2 stress test. They should remain separate in the research record.