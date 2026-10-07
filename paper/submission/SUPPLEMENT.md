# Supplementary Material

*Companion to `MANUSCRIPT.md`. Repository paths are relative to the repository root. At submission, cite the archived release ([[Zenodo DOI]]) rather than the live repository.*

## S0. Index of frozen materials

| Item | Path | Frozen / committed |
|---|---|---|
| Confirmatory protocol `P2-C1.4-CONFIRMATORY-V1-2026-09-21` | `research/methodological_gates/P2_C1_4_CONFIRMATORY_PROTOCOL_FREEZE_V1_2026-09-21.md` | 2026-09-21 (commit `c68f8a4`) |
| W1–W7 witness codebook v2 | `research/methodological_gates/C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19.md` | 2026-09-19 (commit `31cc7bd`) |
| UNCLEAR operational rule | `research/methodological_gates/C4_2_4A_UNCLEAR_XW_OPERATIONAL_RULE_FREEZE_2026-09-21.md` | 2026-09-21 (commit `13dbfb4`) |
| Rater instructions | `research/annotation_ui/P2_C1_4_RATER_INSTRUCTIONS.md` | current version |
| Annotation tool (offline HTML) | `research/annotation_ui/P2_C1_4_XW_ANNOTATOR.html` | current version |
| Response validator | `research/cohort/validate_P2_C1_4_XW_responses.py` | — |
| X_W construction and reliability | `research/cohort/construct_P2_C1_4_XW.py` | — |
| Frozen analysis | `research/P2-C1.2/analysis/run_P2_C1_2_confirmatory_analysis.py` | — |
| Blinded feasibility and subsample | `research/cohort/p2_c1_4_blinded_feasibility_and_subsample.py` | run once: `37663285811` |
| Reference-SQL features (hardness, nesting) | `research/cohort/reference_sql_features_P2_C1_4.py` | CSV SHA-256 `5e1b2edb…5b68` |
| Evidence-availability audit | `research/cohort/p2_c1_4_evidence_availability_audit.py`; result in `research/cohort/results/` | 2026-10-07 |
| Gate (stages 1 and 2, runs once) | `research/cohort/p2_c1_4_post_annotation_gate.py`, `.github/workflows/p2-c1-4-xw-lock-and-analysis.yml` | — |
| Findings renderer | `research/cohort/render_P2_C1_4_findings.py` | — |
| Decision log (dated decisions and reasons) | `DECISION_LOG.md` | continuous |

## S1. Supplementary Note: the invalid first annotation attempt

**What happened.** Before the confirmatory cohort was collected, a first two-rater annotation of the 12-case measurement pilot produced complete agreement (κ = 1.00, AC1 = 1.00). A forensic review then found that the worksheet the raters used did not reproduce the frozen evidence packet:

- at least one case showed different question text;
- other cases appeared as generic database-review prompts instead of their exact questions;
- abbreviated summaries replaced the exact returned rows;
- every dimension was marked applicable for SUCCESS cases, contrary to the question-specific codebook;
- NO_USABLE_EVIDENCE cases received UNCLEAR labels despite the stop rule;
- the independence attestations were incomplete.

**How it was handled.** The attempt is preserved unchanged and classified as invalid. Its agreement values are not used as evidence of reliability. The confirmatory instrument (S0) was rebuilt so that raters see the frozen packet exactly, and the tool validates the frozen vocabulary.

**Source:** `research/methodological_gates/C4_2_4A_HUMAN_RESPONSE_FORENSIC_AUDIT_2026-09-21.md`.

## S2. Supplementary Table: protocol and runtime amendments

All amendments were adopted before any confirmatory outcome was inspected. The commit hashes give the timestamped record.

| Date | Amendment ID | Type | What changed | Commit |
|---|---|---|---|---|
| 2026-09-21 | `P2-C1.4-CONFIRMATORY-V1-2026-09-21` | Protocol freeze | Population, outcome, baseline, X_W, model, CV design, estimand, uncertainty, stopping rules | `c68f8a4` |
| 2026-09-21 | UNCLEAR operational rule | Measurement | Implementation-only ambiguity cannot create applicability uncertainty; genuine linguistic ambiguity handled conservatively | `13dbfb4` |
| 2026-09-21/22 | Runtime amendments 2–5 and timeout amendment | Runtime | Tokeniser data, HTTP timeout, source transport, long-request handling; no scientific parameter changed | `fc171a1`, `6f40dd6`, `be107a8`, `332551a`, `ba4a2ef` |
| 2026-09-26 | `P2-C1.4-RUNTIME3-ESCALATION-WORDING-AMENDMENT-2026-09-26` | Runtime | One escalation-prompt sentence replaced, because it reproducibly triggered runaway generation in the pinned runtime | `87bf57d` |
| 2026-09-30 | `P2-C1.4-RUNTIME3-PATHOLOGICAL-SQL-RECOVERY-AMENDMENT-2026-09-30` | Runtime | Detector-gated, bounded recovery from self-repeating SQL generation; fired in 227 decisions (2.6%) | `97bb8ff` |
| 2026-10-01 | `P2-C1.4-QUALIFICATION-GATE-G3-AMENDMENT-2026-10-01` | Acquisition gate | Re-qualification gate criteria; adopted before any record-status count of the qualification run was seen | `9b9d008` |
| 2026-10-01 | `P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01` | **Statistical** | Record statuses E1–E3/E4; primary population; S1/S2 sensitivity analyses; robustness rule; missingness audit | `59c462e` |
| 2026-10-02 | `P2-C1.4-XW-CONSTRUCTION-AND-ANALYSIS-IMPLEMENTATION-AMENDMENT-2026-10-02` | **Statistical** | Rater combination (mean X_W); Riley criteria as a hard stop; reliability bootstrap; outcome-blind missingness audit | `0bda9f0` |
| 2026-10-07 | `P2-C1.4-BLINDED-FEASIBILITY-AND-ANNOTATION-SUBSAMPLE-AMENDMENT-2026-10-07` | **Statistical** | Run-once blinded feasibility check; random annotation subsample (1,709 per rater) | `dae925e` |

## S3. Supplementary Table: systematic-missingness audit

[[R: from `results.json` → `missingness_audit`. E2, E3/E4 and EVALUABLE by database, question length, reference-SQL hardness and nesting depth. Descriptive; no test.]]

## S4. Supplementary Table: evidence availability (complete)

The source is `research/cohort/results/P2_C1_4_EVIDENCE_AVAILABILITY_AUDIT.json` (SHA-256 `4c53e956…2457`). It was computed from blinded packet A; packet B gives identical values.

| Characteristic | Usable evidence | No usable evidence |
|---|---|---|
| Decisions | 5,048 | 3,590 |
| Question length, median [IQR] (characters) | 61 [47, 78] | 69 [52, 87] |
| Hardness: easy / medium / hard / extra | 30.2 / 36.7 / 19.9 / 13.2 % | 12.6 / 31.8 / 25.4 / 30.2 % |
| Nesting depth: 0 / 1 / ≥2 | 84.4 / 14.9 / 0.7 % | 84.5 / 14.0 / 1.5 % |

The no-usable-evidence rate per database had a median of 38.1% and a range of 11.8–72.0% across 146 databases.

**Figures behind the main text:**

- **Status breakdown.** No usable evidence comprises 3,560 EVALUABLE, 23 E2, 4 E3/E4 and 3 E1 decisions. Usable evidence comprises 5,044 EVALUABLE and 4 E3/E4 decisions.
- **Usable evidence and `execution_ok`.** Usable evidence coincides exactly with `execution_ok` = 1.

## S5. Supplementary Table: inter-rater reliability (full)

[[R: from `P2_C1_4_XW_RELIABILITY.json`. Full contingency tables per dimension for applicability (3×3) and witness (2×2); normalised-indicator agreement; marginals per rater.]]

## S6. Reporting checklist

[[TRIPOD+AI items mapped to manuscript sections; prepare once the target journal is fixed and confirm whether it requires TRIPOD+AI or another checklist.]]

## S7. Reproducing the analysis

1. Check out the archived release.
2. Obtain the locked cohort and blinded packets from the release archive; verify the cohort SHA-256 `da537c75ce5778af3c36d05d8e59f7cea296aa5b8a4bc0c527b7cf352ebd9b8b`.
3. Install Python 3.11 with numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0, statsmodels 0.15.0.
4. Run `python research/cohort/p2_c1_4_post_annotation_gate.py stage1 …` and then `stage2 …` with the arguments listed in `.github/workflows/p2-c1-4-xw-lock-and-analysis.yml`.
5. Run `python research/cohort/render_P2_C1_4_findings.py …`.
6. Compare `results.json` with the published SHA-256 [[R: results_json_sha256]].
