# Research Status

**Last updated:** 2026-09-21

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
