# P2-C1.4 Missingness and Eligibility Amendment

**Amendment ID:** `P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01`
**Date:** 2026-10-01
**Status:** Approved by the author 2026-10-01. Adopted before any confirmatory outcome analysis.
**Frozen protocol:** `P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21` (confirmatory question, B, X_W, Y_H, model family, estimand, resampling, seeds unchanged)
**Builds on:** `P2-C1.4-RUNTIME3-PATHOLOGICAL-SQL-RECOVERY-AMENDMENT-2026-09-30`

## 1. Why this amendment exists

Confirmatory acquisition run `36691960508` (main @ `931eccd`) completed 31/44 shards; 13 shards failed and no cohort was locked. Error logs only were read:

- shard 3: the pinned official Spider evaluator crashed executing the **reference** SQL (`sqlite3.OperationalError: ORDER BY clause should come after INTERSECT not before`, `spider/evaluation.py:627`);
- shards 6, 15, 17, 18, 19, 20, 21, 26, 29, 32, 33, 41: `Runtime3 candidate pathological-SQL recovery failed after 2 attempt(s)` during the post-evidence escalation call.

Each shard stops at its first failure, so these are lower bounds. Since 2026-09-21 the only planned response to runtime failure has been "fix the runtime and re-run a complete acquisition" (Runtime Amendments 3 and 5). With the pinned `llama3.2:1b`, an all-or-nothing gate over 8,638 decisions is not achievable.

The frozen design anticipates this situation:

> "If unavoidable missingness remains, its treatment must be frozen before outcome analysis and applied consistently to M0 and M1. Post-hoc convenient complete-case deletion is not acceptable." — Aligned Outcome Cohort Design §9

> "Exclusions must be mechanical and recorded before outcome analysis. No case may be excluded because of its outcome or because X_W is difficult to annotate." — Aligned Outcome Cohort Design §6

> "A timeout remains a runtime failure. It is never converted into a synthetic observation." — Runtime Amendment 5

This amendment freezes that treatment.

## 2. Defects found while preparing this amendment (implementation, not science)

1. **P0 runtime failures were silently converted into outcomes.** Project1 `BenchmarkEnvironment.run()` catches every exception inside a policy run. A bounded Runtime3 failure during P0 therefore produced a trace with no SQL, which the collector treated as `NO_USABLE_EVIDENCE` and which was scored P0-incorrect (Y_H = 0). Escalation-call failures propagated only because `_run_p5` is invoked outside that handler. The collector now detects Runtime3 errors in the P0 trace and classifies them as E2 (§3).
2. **Forensic lock could never pass on a sharded run.** Records carried the shard-file hash as `manifest_hash`; the lock audit compares against the frozen manifest hash. Records now carry the frozen parent hash (and the shard hash separately).

Neither defect affected any accepted cohort; none exists.

## 3. Record status — frozen definitions

Every frozen `decision_id` remains in the cohort, in frozen order. Each aligned record carries exactly one `record_status`:

| Status | Definition (mechanical) | Decision-time evidence / X_W | Outcome fields |
|---|---|---|---|
| `EVALUABLE` | Pathway completed | as captured | P0, replacement, final, Y_H as frozen |
| `EXCLUDED_E1_REFERENCE_NOT_SCOREABLE` | Pre-acquisition census: the reference SQL fails the pinned evaluator's parse (`get_sql`) or raw SQLite execution. Model never called. | none | all null |
| `NON_EVALUABLE_E2_RUNTIME_FAILURE_PRE_EVIDENCE` | Bounded Runtime3 failure before the P0 answer completed | none (missing X_W, frozen §13) | all null |
| `NON_EVALUABLE_E3E4_RUNTIME_FAILURE_POST_EVIDENCE` | Bounded Runtime3 failure after the P0 answer and evidence were complete | as captured; annotatable | `p0_correct` scored; replacement, final, Y_H **null** |

- **E3** = post-evidence failure with `p0_correct = false`. **E4** = post-evidence failure with `p0_correct = true`.
- For E3 only, `y_h_implied_by_definition = 0` is stored in a **separate field**, because Y_H = I(P0 correct ∧ replacement ∧ final incorrect) is 0 whenever P0 is incorrect. `y_h` itself remains null. Nothing is imputed for E4.
- The runtime-failure ledger (stage, exception, recovery events) is written after the evidence lock, kept out of the decision-time evidence artifact, and never shown to raters.
- E1 is decided by `research/cohort/census_P2_C1_4_reference_sql.py` immediately after the manifest is frozen, before any model call; the forensic lock fails if any record's E1 status disagrees with the census.

## 4. Analysis — frozen before outcome analysis

**Primary (unchanged estimand):** Δlog-loss on decisions that are `EVALUABLE` and have usable evidence (frozen §7), M0 and M1 on identical observations.

**Prespecified sensitivity analyses, reported alongside the primary estimate (not optional):**

- **S1:** primary population plus E3 decisions with usable evidence, using `y_h_implied_by_definition = 0`.
- **S2 (bounds):** S1 plus E4 decisions with usable evidence, once with Y_H = 0 and once with Y_H = 1 for all E4. The conclusion is reported as robust only if the sign of Δlog-loss agrees across the primary analysis, S1 and both S2 bounds.

X_W is annotated for every record with usable evidence, including E3/E4; raters cannot tell which records failed later.

## 5. Systematic-missingness audit (Cohort Design §20)

Before outcome analysis, compare E2/E3/E4 against `EVALUABLE` decisions on pre-outcome characteristics only: database, Spider hardness level of the reference SQL, nesting depth of the reference SQL, and question length. Report the comparison. If the failures are concentrated, this is stated as a limitation and a threat to generalisability.

## 6. Reporting (flow diagram)

source frame → −12 pilot → 8,638 frozen → −E1 → acquired → −E2 → −E3/E4 → −other `NO_USABLE_EVIDENCE` → primary population. Every arrow reports a count and the decision IDs. Also reported: pathological-SQL recovery count, runtime-failure rate by stage, S1/S2 results, and the missingness audit.

## 7. What is not changed

The confirmatory question, B, X_W construct and codebook, Y_H definition, model family, regularisation grid, resampling, seeds, estimand, model identity, temperature, Project1 code and the 8,638-decision frozen manifest are unchanged. No case is removed from the cohort ledger.

## 8. Transparency about what was inspected

- Run `36691960508`: only job error logs were read. No outcome-bearing artifact was downloaded or opened. The run is discarded.
- Non-confirmatory engineering artifacts that were opened during development: pathology diagnostics #6/#7 (000091), and the Run #59 qualification artifact (cases 000001–000200 and the 000091 preflight). From the latter, only the runtime-failure ledger text and schema-validation error categories were used. No outcome summary was computed for decision-making.
- The rules above depend only on stage completion and reference-SQL scoreability. They cannot be tuned towards a result.

This amendment was adopted after a failed engineering run and before any outcome analysis. That is stated as such in the manuscript, together with the fact that it changes missing-data handling, not merely transport.

## 9. Implementation and verification

- `research/cohort/census_P2_C1_4_reference_sql.py` (new), `collect_P2_C1_4_aligned_cohort.py`, `validate_P2_C1_4_aligned_records.py`, `forensic_lock_audit_P2_C1_4.py`, `P2_C1_4_ALIGNED_DECISION_RECORD_SCHEMA_V2.json` (additive), sequential-qualification and acquisition-runtime3 workflows.
- Manuscript: `paper/PROJECT2_LIVING_RESEARCH_DRAFT.md` §6.6, §6.12, §7.2, §8.2, §10.5, §14.
- End-to-end test with the real collector, pinned Project1 and pinned Spider evaluator on a synthetic database and a mock Ollama server: one record of each status produced; validator, schema, forensic lock (with census check) and packet generator pass; decision-time evidence and rater packets contain no status or failure information.
- Negative tests: synthetic Y_H on a failure record, inconsistent implied Y_H, unknown status, evidence on a pre-evidence failure, E1 relabelling, non-census E1, and a missing shard failure ledger are all rejected.
