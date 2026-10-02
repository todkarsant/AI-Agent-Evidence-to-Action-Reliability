# Current Research State — P2-C1.4

**State:** `P2_C1_4_COHORT_LOCKED_XW_ANNOTATION_IN_PROGRESS`

**As of:** 2026-10-02

## Summary — 2026-10-02

The confirmatory aligned cohort is **locked**. Independent human X_W annotation of the full cohort is **in progress**. No outcome has been examined, and no M0/M1 model has been fitted.

| Item | Status | Record |
|---|---|---|
| Runtime3 pathological-SQL recovery | Adopted 2026-09-30 | `P2-C1.4-RUNTIME3-PATHOLOGICAL-SQL-RECOVERY-AMENDMENT-2026-09-30` |
| Missingness and eligibility (`record_status` E1/E2/E3E4/EVALUABLE; S1/S2; audit) | Adopted 2026-10-01 | `P2_C1_4_MISSINGNESS_AND_ELIGIBILITY_AMENDMENT_2026-10-01.md` |
| Qualification gate G3 (integrity + 5% runtime-failure ceiling) | Adopted 2026-10-01 | `P2_C1_4_QUALIFICATION_GATE_G3_AMENDMENT_2026-10-01.md` |
| Sequential qualification | PASS (200 EVALUABLE, 0 runtime failures) | run `36847267797` |
| Confirmatory acquisition | COMPLETE: 44/44 shards, 8,638 records in frozen order | run `36853456589` (main @ `87a66ef`) |
| Forensic cohort lock (G4) | PASS; 31 runtime failures vs ceiling 431 | cohort SHA-256 `da537c75ce5778af3c36d05d8e59f7cea296aa5b8a4bc0c527b7cf352ebd9b8b` |
| Blinded rater packets A/B | Generated | post-lock run `37017913823` |
| X_W annotation (two independent raters) | IN PROGRESS | `research/annotation_ui/P2_C1_4_XW_ANNOTATOR.html`, `P2_C1_4_RATER_INSTRUCTIONS.md` |
| X_W construction and analysis implementation amendment | APPROVED and FROZEN 2026-10-02 | `P2_C1_4_XW_CONSTRUCTION_AND_ANALYSIS_IMPLEMENTATION_AMENDMENT_2026-10-02.md` |
| Confirmatory M0 vs M1 | BLOCKED until the raw annotations are locked and X_W is constructed | `research/P2-C1.2/analysis/` (synthetic tests only) |

**Record-status counts.** These contain no outcome information.

- EVALUABLE 8,604
- E1 (reference SQL not scoreable) 3
- E2 (runtime failure before evidence) 23
- E3/E4 (runtime failure after evidence) 8

**Pathological-SQL recovery** fired in 227 decisions.

**Blinding.** The outcome summaries in the lock artifact have not been opened. Raters must not access the GitHub Actions artifacts; the cohort artifact contains outcomes.

**Frozen implementation choices** (author decision, 2026-10-02):

- Combined X_W is the mean of the two raters' X_W.
- If the primary population fails Riley et al. (2020) criterion (i) or (iii), the run is a **hard stop** (`FEASIBILITY_STOP_RILEY`): no model is fitted.
- The missingness audit compares E2 and E3/E4 combined against EVALUABLE. E3 and E4 are not split, to preserve blinding.

**Tooling.** All of this has been tested on synthetic data only:

- the response validator and the raw-annotation lock / reliability / X_W construction (18 tests);
- the frozen analysis pipeline (24 tests).

## Next gate (2026-10-02)

1. Raters A and B finish annotating independently, then export.
2. `validate_P2_C1_4_XW_responses.py` passes on both exports.
3. `construct_P2_C1_4_XW.py` hash-locks the raw annotations, writes the reliability report and constructs X_W, without reading the cohort or any outcome.
4. Run the frozen analysis once on the locked cohort and the locked X_W.
   - If the run stops (mechanical or Riley), only descriptives are reported.
   - Otherwise, report the primary estimand together with S1/S2 and the missingness audit.
5. Archive the GitHub Actions artifacts before they expire:
   - frozen manifest, about 2026-10-15;
   - packets, about 2026-10-16;
   - cohort, about 2026-11-01.

---

*The sections below are the historical record up to 2026-09-21, kept unchanged except where marked as superseded.*

## Gate status as of 2026-09-21

- **C.4.2.3-C:** global P0 determinism remains unestablished; targeted exact-path qualification is not a global guarantee.
- **C.4.2.3-D:** fresh observational evidence capture was qualified under the documented targeted scope.
- **C.4.2.4-A:** **RESOLVED** after independent-rater attestation, mechanical validation, packet reconciliation, and frozen UNCLEAR operational rule.
- **P2-C1.2 methodological attack:** **COMPLETED**.
- **P2-C1.3 aligned outcome-bearing cohort reconstruction:** **COMPLETED — historical reconstruction rejected**.
- **P2-C1.2 confirmatory modeling:** **BLOCKED** pending an aligned outcome-bearing cohort.

## Decisive scientific blocker (as of 2026-09-21; addressed by the new P2-C1.4 cohort)

The current W1-W7 X_W measurement cohort contains 12 fresh cases, while the historical P1/P6 outcome summaries contain 330 eligible development cases and 91 held-out cases.

The current 12-case X_W cohort was intentionally non-overlapping with the historical P1/P6 schemas/questions.

The historical Project 1 repository preserves experiment code, protocol, analysis logic, and GitHub Actions provenance. Historical P6 runs also produced machine trace artifacts. However, the preserved scientific record does not establish preservation of the decision-time evidence in a form that supports independent W1-W7 annotation across the historical outcome-bearing units.

Therefore the required row-level structure:

[
(B_i,E_i^{decision-time},X_{W,i},Y_{H,i})
]

does not currently exist for the same decision units.

## What is now established

### Measurement

- W1-W7 witness construct is frozen.
- Human response artifacts are preserved.
- Applicability: 49/49 descriptive agreement; Cohen kappa 1.00.
- Binary witness labels: 27/27 descriptive agreement; Cohen kappa 1.00; Gwet AC1 1.00.
- Independent-rater provenance is supported by explicit attestation.
- UNCLEAR handling is frozen as a pre-outcome methodological amendment.

### Predictive-validity design

The following requirements remain before confirmatory modeling:

1. common decision unit;
2. preserved decision-time evidence;
3. B/X_W/Y_H linkage;
4. predefined missing-X_W handling;
5. frozen model family/regularization/preprocessing;
6. frozen primary proper scoring metric;
7. frozen outer resampling and dependence structure.

## Prohibited shortcuts

Do not:

- retrofit 12 X_W values onto the historical 330/91 outcome units;
- infer X_W from row/column counts or hidden SQL;
- convert NO_USABLE_EVIDENCE to X_W=0;
- call the historical 91-case holdout external validation for X_W;
- fit M0/M1 before aligned data exist.

## Latest movement — 2026-09-21

P2-C1.4 has advanced beyond a design-only document. Three sub-attacks were executed:

- **P2-C1.4-S:** sample-size/event-rate feasibility — PASS WITH CONDITIONS; no arbitrary N frozen.
- **P2-C1.4-M:** model/scoring-rule attack — PASS WITH CONDITIONS; low-dimensional penalized logistic + paired out-of-sample proper-loss comparison is the candidate protocol, not yet frozen.
- **P2-C1.4-R:** runtime/evidence-preservation — FAIL FOR COLLECTION READINESS because the repository did not yet contain a verified aligned-cohort collector/validator contract.

Implementation has now started. Added:
- `research/cohort/P2_C1_4_ALIGNED_DECISION_RECORD_SCHEMA_V1.json`
- `research/cohort/validate_P2_C1_4_aligned_records.py`
- `research/cohort/P2_C1_4_ALIGNED_DECISION_RECORD_DRY_RUN.json`

The dry-run fixture is synthetic and is not scientific outcome data.

## Latest runtime qualification — 2026-09-21

**P2-C1.4-R = PASS for non-confirmatory runtime scope.**

Successful GitHub Actions run: `35591634277`.

The collector executed four fresh non-confirmatory cases, excluding the frozen 12-case C4.2.3-B pilot, using the pinned Project 1 P6-IP path, Spider 1.0, and Ollama 0.33.3. It captured decision-time evidence, locked and hashed that artifact, then derived official correctness/outcome fields after the evidence lock. The aligned records passed both the mechanical validator and the JSON schema validator.

Three implementation-contract failures and one safety-gating failure occurred before the successful run. All are preserved in `research/methodological_gates/P2_C1_4_RUNTIME_DRY_RUN_AUDIT_2026-09-21.md`.

Important: this is **runtime qualification**, not confirmatory evidence and not predictive-validity evidence.

## Latest movement — confirmatory protocol freeze and acquisition launch

**P2-C1.4-S = FROZEN.**  
**P2-C1.4-M = FROZEN.**  
**P2-C1.4 collection protocol = FROZEN.**  

Frozen protocol:
- `research/methodological_gates/P2_C1_4_CONFIRMATORY_PROTOCOL_FREEZE_V1_2026-09-21.md`
- protocol ID `P2-C1.4-CONFIRMATORY-V1-2026-09-21`

The confirmatory acquisition workflow has been launched. It freezes an outcome-blind source-frame manifest from Spider 1.0 training-side data, excludes the frozen 12-case pilot, shards acquisition into immutable artifacts, validates each shard, and consolidates only successful aligned records.

The collector now requires explicit `--confirmatory` plus the frozen protocol authorization before confirmatory execution.

No X_W annotation and no M0/M1 fitting occur during this acquisition stage.

## Next gate (as of 2026-09-21; superseded)

**Complete and audit the acquired aligned cohort → independently annotate X_W → lock raw annotations/provenance → run the frozen reliability gate → only then fit M0/M1.**

## Publication record

The complete methodological development path is now documented in:

- `research/P2_RESEARCH_DEVELOPMENT_JOURNEY.md`
- `research/methodological_gates/P2_C1_3_ALIGNED_COHORT_RECONSTRUCTION_AUDIT_2026-09-21.md`
- `paper/PROJECT2_LIVING_RESEARCH_DRAFT.md`

No confirmatory predictive model, p-value, AUC, Brier score, log-loss difference, or incremental-validity result exists.


### P2-C1.4 acquisition forensic update — 2026-09-21
- Confirmatory acquisition attempts exposed runtime Ollama HTTP timeouts; a versioned transport-only amendment now pins Project 1 commit `7bef895846f2ac89d885827be16b30e69986b013` and `OLLAMA_TIMEOUT_SECONDS=300` under protocol `P2-C1.4-CONFIRMATORY-V1-RUNTIME1-2026-09-21`.
- Forensic audit also found that the collector did not preserve the exact decision-time schema required for W1-W7 annotation. This was corrected before accepting any confirmatory cohort; aligned records are now V2 and include schema in the evidence hash.
- A mechanical forensic lock auditor is now wired into consolidation and will fail closed unless all 8,638 source-frame decision IDs are present in exact order and evidence/outcome invariants pass.
- Current target acquisition run: `35598330749` (run #12), currently pending GitHub Actions capacity. No cohort is locked; no X_W annotation or M0/M1 analysis has begun. *(Superseded: see the 2026-10-02 summary at the top. The cohort was locked by run `36853456589`.)*
