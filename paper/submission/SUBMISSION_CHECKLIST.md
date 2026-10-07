# Submission checklist

*Last updated 2026-10-08. Items marked **[author]** need a decision or action by the author.*

## Blocked on the analysis

- [ ] Both FINAL rater exports committed in one commit; gate Stage 1 → Stage 2 → findings report has run once.
- [ ] Fill every `[[R: …]]` in `MANUSCRIPT.md` and `SUPPLEMENT.md` from `P2_C1_4_FINDINGS.json` / `.md`, citing the `results.json` SHA-256.
- [ ] Mechanical check: Y_H = 0 for every EVALUABLE decision with NO_USABLE_EVIDENCE (§4.2). This follows from the outcome definition and must be confirmed on the locked outcomes. If it fails, revise §4.2 and §5.2.
- [ ] Write §5.1, §5.3, §7 and the Abstract conclusions, using the interpretation fixed in advance in §5.1.
- [ ] Draw Figure 1 (cohort flow) and Figure 2 (Δlog-loss across analyses); build Tables 2–4.
- [ ] Claim-to-evidence table: every claim mapped to a file and a hash (living draft §14).

## Decisions for the author

- [ ] **[author]** Target journal. Choosing it fixes the word limit, structure, reference style, checklist and AI-use policy. The candidate list is in `research/REFERENCES.md` §D.
- [ ] **[author]** Author list, affiliations, corresponding author, CRediT roles.
- [ ] **[author]** Licence: code (e.g. MIT or Apache-2.0) and data/text (e.g. CC BY 4.0). Add a `LICENSE` file; the repository has none.
- [ ] **[author]** Whether to release the full locked cohort, including outcomes, publicly.
- [ ] **[author]** Raters: consent to be named in acknowledgements, or co-authorship.
- [ ] **[author]** Ethics: confirm with the journal whether annotation by two raters needs a statement or exemption.
- [ ] **[author]** Funding and competing-interest statements.
- [ ] **[author]** AI-use disclosure, worded to the chosen journal's policy.

## Before submission

- [ ] Re-run the literature search for 2026 work on agent reliability, evidence sufficiency and authorisation; update §2 and the novelty statement.
- [ ] Confirm the remaining reference gaps:
  - volume, issue and pages for Gneiting & Raftery (2007);
  - Gwet (2008) issue number;
  - full author list for Tang et al. (2026), if the style requires it;
  - whether Rabanser et al. (2026) now has ICML proceedings details.
- [ ] Re-check the reference-list format against the journal's style.
- [ ] Create an archived release (e.g. Zenodo) and put its DOI in the manuscript and supplement.
- [ ] Internal review by the collaborator.
- [ ] Format to the journal template and compute the word count.
- [ ] Write the cover letter, covering scope fit, the prospective design and the honest reporting of amendments.
- [ ] Remove all `[[…]]` placeholders; final consistency pass between numbers in the text and the findings report.

## Done

- [x] Submission manuscript in standard structure (`MANUSCRIPT.md`): methods final, results as placeholders.
- [x] Methods disclosures: no external registration; three statistical amendments, all before any outcome was inspected; the evidence-availability audit was not prespecified; constant `execution_ok` in the primary population.
- [x] Verified reference list (2026-10-08). One unverifiable SSRN entry excluded.
- [x] Supplementary material index, amendments table, invalid-annotation note and evidence-availability table (`SUPPLEMENT.md`).
- [x] Findings renderer wired into Stage 2.
