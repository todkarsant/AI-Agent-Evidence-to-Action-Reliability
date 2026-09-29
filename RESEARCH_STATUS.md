# Research Status

**Last updated:** 2026-09-29

## Overall status

**Project 2 is in confirmatory-design preparation.**

The repository is the canonical source of truth. The project has completed the current measurement-validation work and the P2-C1.2/P2-C1.3 methodological attacks. Confirmatory predictive modeling remains blocked by a scientific cohort-alignment requirement.

## Gate ledger

| Gate | Status | Record |
|---|---|---|
| P1/P6 discovery evidence | Complete | Discovery/mechanism evidence only |
| P2-C1.1 novelty/falsification work | Complete to current stage | Generic perturbation/reliability novelty seam rejected |
| C.4.1-A Construct Identifiability | **FAIL** | Historical P6 path cannot observe representation-level evidence perturbations |
| C.4.1-B Alternative Construct Attack | **PARTIAL / REDESIGN** | Observable evidence-witness construct survived |
| C.4.1-C Construct Separation | **CONDITIONAL PASS** | Fresh isolated pilot required/used |
| C.4.2.1 Deterministic Obligation Extraction | **PROVISIONAL PASS** | Frozen W1-W7 construct |
| C.4.2.2 Measurement Reliability | **RESOLVED** | Independent human annotation + mechanical/provenance audit |
| C.4.2.3-A Fresh Corpus Acquisition/Freedom From Historical Overlap | **PASS** | Fresh 12-case qualification subset |
| C.4.2.3-B Clean Execution Input | **PASS** | Gold-derived fields excluded from annotator-facing input |
| C.4.2.3-C Fresh P0 Execution | **LIMITED / GLOBAL DETERMINISM NOT ESTABLISHED** | Targeted exact-path success does not establish global repeatability |
| C.4.2.3-D Evidence Capture | **QUALIFIED UNDER TARGETED SCOPE** | Evidence-capture workflow and provenance verified |
| C.4.2.4-A Human X_W validation | **RESOLVED** | 49/49 applicability and 27/27 witness agreement; explicit independence attestation |
| P2-C1.2 Predictive / Incremental Validity Attack | **COMPLETE** | Confirmatory modeling blocked by alignment/missingness/model-protocol issues |
| P2-C1.3 Aligned cohort reconstruction | **COMPLETE — FAILED** | Historical outcome/X_W alignment cannot be established |
| P2-C1.4 New aligned cohort | **RUNTIME QUALIFIED — NON-CONFIRMATORY** | Four fresh dry-run cases passed aligned artifact validation; confirmatory collection still requires protocol freeze |
| Confirmatory M0 vs M1 | **BLOCKED** | Do not fit until P2-C1.4 is complete |

## Latest execution progress — 2026-09-21

P2-C1.4-R runtime qualification passed in GitHub Actions run **35591634277**. Four fresh non-confirmatory cases were collected with the pinned P6-IP path, decision-time evidence was locked before official outcome derivation, and aligned records passed mechanical and JSON-schema validation. Hardening failures remain preserved in `research/methodological_gates/P2_C1_4_RUNTIME_DRY_RUN_AUDIT_2026-09-21.md`.

This is runtime qualification only; no confirmatory predictive-validity claim is authorized.

## Important negative findings

### P1/P6 intervention mechanism

Historical P6-IP produced more harms than rescues and increased cost. This remains discovery/mechanism evidence and motivates Project 2; it is not the X_W predictive-validation dataset.

### Construct identifiability

Historical P6 did not preserve the decision-time evidence needed for a non-tautological W1-W7 measurement across its outcome-bearing units.

### Cohort alignment

The current 12-case X_W measurement cohort cannot be retrofitted to the historical 330/91 outcome cohorts.

## Publication discipline

The paper must explicitly distinguish:

1. historical Project 1 discovery evidence;
2. Project 2 measurement/reliability evidence;
3. methodological amendments;
4. confirmatory predictive-validity evidence.

No predictive-validity result may be written before the same-unit B/X_W/Y_H cohort exists and the complete modeling protocol is frozen.

See `research/P2_RESEARCH_DEVELOPMENT_JOURNEY.md` and `paper/PROJECT2_LIVING_RESEARCH_DRAFT.md`.


### P2-C1.4 acquisition forensic update — 2026-09-21
- Confirmatory acquisition attempts exposed runtime Ollama HTTP timeouts; a versioned transport-only amendment now pins Project 1 commit `7bef895846f2ac89d885827be16b30e69986b013` and `OLLAMA_TIMEOUT_SECONDS=300` under protocol `P2-C1.4-CONFIRMATORY-V1-RUNTIME1-2026-09-21`.
- Forensic audit also found that the collector did not preserve the exact decision-time schema required for W1-W7 annotation. This was corrected before accepting any confirmatory cohort; aligned records are now V2 and include schema in the evidence hash.
- A mechanical forensic lock auditor is now wired into consolidation and will fail closed unless all 8,638 source-frame decision IDs are present in exact order and evidence/outcome invariants pass.
- Current target acquisition run: `35598330749` (run #12), currently pending GitHub Actions capacity. No cohort is locked; no X_W annotation or M0/M1 analysis has begun.

### P2-C1.4 Runtime3 execution update — 2026-09-29

Run #59 (**36522954069**) completed at the software/artifact level on the continuation branch, but the **scientific qualification gate did not pass**.

- The qualification artifact contains exactly **200 frozen decision IDs**, **199 evaluable records**, and **1 explicit NON_EVALUABLE_RUNTIME_FAILURE**.
- The non-evaluable record is **P2C14-CONF-000091**. It is retained in the frozen cohort; no synthetic SQL, outcome, Y_H, or replacement label was generated.
- The 000091 preflight artifact also records a bounded Runtime3 generation failure. The qualification Ollama server log contains 10-minute HTTP 500 terminations during long generations; the collector's final diagnostic can retain the earlier 4096-token response while a later retry times out, so the existing diagnostic fields are not sufficient to infer the exact second-attempt token ceiling without a targeted diagnostic.
- Therefore **200/200 evaluable + 0 runtime failures is not established**, PR #28 must not merge, and the 8,638-case confirmatory acquisition remains blocked.
- An autonomous **Runtime3 blocker diagnostic workflow** has now been added on main. It consumes the failed qualification artifact, identifies the runtime-failure decision IDs, reconstructs the exact frozen one-case manifests, and runs six isolated diagnostic repeats without changing the confirmatory cohort, model, prompt, temperature, or statistical estimand.
- The current blocker diagnostic was triggered automatically for Run #59 and is running as GitHub Actions run **36541862037**. Its purpose is forensic diagnosis only; its result does not itself authorize confirmatory acquisition.
- The same diagnostic workflow is wired to future successful qualification runs with runtime failures, so this failure class no longer requires manual discovery before diagnosis.
- The 200/200 scientific progression gate remains unchanged: only an artifact with exactly 200 evaluable records and zero runtime failures can authorize PR #28 progression and the downstream acquisition chain.

No confirmatory predictive-validity result exists yet.
