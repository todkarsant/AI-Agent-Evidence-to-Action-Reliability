# C4.2.4-A — Human Response Forensic Audit — 2026-09-21

## Disposition

**Human A and Human B submissions are preserved but INVALID FOR PRIMARY RELIABILITY ANALYSIS.**

This is not a finding that the two humans are scientifically incapable or that their individual judgments are wrong. The submitted worksheet did not faithfully reproduce the frozen packet and the completed forms contain systematic protocol violations. Therefore the apparent perfect agreement cannot be used as confirmatory reliability evidence.

## Verified submission facts

- 12/12 case statuses agree.
- Both raters marked all 7 dimensions applicable for all 8 SUCCESS cases: 56 YES applicability labels per rater.
- Both raters marked all 7 dimensions UNCLEAR for all 4 NO_USABLE_EVIDENCE cases: 28 UNCLEAR labels per rater.
- Witness labels agree on every populated field.
- The apparent agreement is therefore perfect, but **non-confirmatory** because the annotation instrument/protocol was not validly executed.

## Critical source/instrument defect

The simple worksheet altered the frozen packet content.

Most importantly:

- **C423_0061** in the frozen packet is `assets_maintenance`, **NO_USABLE_EVIDENCE**, with the exact question: “Which engineer has visited the most times? Show the engineer id, first name and last name.” The submitted worksheet instead presented a generic grouped-analytics question and marked the case SUCCESS.
- **C423_0041**, **C423_0051**, and **C423_0101** were also presented as generic database-review prompts rather than their exact frozen natural-language questions.
- The frozen packet includes exact schema/evidence content. The simple worksheet exposed only abbreviated evidence summaries. Therefore the human judgments were not judgments over the frozen displayed evidence.

## Protocol violations

The frozen codebook requires only obligations explicitly entailed by the natural-language question to be applicable.

The submitted forms marked every W1-W7 applicable for every SUCCESS case.

The instructions also required NO_USABLE_EVIDENCE cases to leave W1-W7 unanswered. Both raters instead marked all seven dimensions UNCLEAR for each such case.

The final independence checkboxes were also not fully affirmed.

## Statistical handling

No Cohen kappa, Gwet AC1, or other reliability statistic from these submissions will be used as a gate result.

The raw submissions remain preserved as an **invalid/failed annotation attempt**. No labels are silently corrected or replaced.

## Recovery

C4.2.4-A remains OPEN and P2-C1.2 remains BLOCKED.

A fresh independent cohort must annotate the **actual frozen packet**, with exact original questions, execution status, columns/rows/schema as applicable, and the frozen W1-W7 codebook. The corrected instrument must enforce the NO_USABLE_EVIDENCE stop rule and must not prepopulate applicability or witness judgments.

The recovery should require no statistical work from the human raters.
