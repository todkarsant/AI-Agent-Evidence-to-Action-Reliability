# P2-C1.4-R — Aligned Cohort Runtime Qualification / Dry-Run Audit
**Date:** 2026-09-21
**Status:** **PASS — NON-CONFIRMATORY RUNTIME QUALIFICATION**

## Objective
Verify that the new P2-C1.4 collector can execute the qualified C4.2.3-D/P6-IP path on fresh, non-confirmatory cases and produce same-unit evidence/outcome records without leaking post-hoc information into decision-time evidence.

## Execution
Workflow:
`.github/workflows/p2-c1-4-aligned-cohort-dry-run.yml`

Successful run:
**35591634277**

Head commit:
`69a0945780b6b30e0a396df7a2a879ebd1abf990`

The workflow:
- checks out the qualified P6-IP implementation at `ffb4cc5ecf8b762baf03ddb42ecf401c1957e640`;
- uses Spider 1.0 with the pinned official evaluator;
- uses Ollama 0.33.3 and `llama3.2:1b`;
- excludes all 12 frozen C4.2.3-B pilot cases;
- deterministically selects four fresh non-confirmatory cases;
- captures P0 decision-time rows/columns before intervention;
- locks and hashes the decision-time artifact;
- evaluates official correctness only after that artifact is locked;
- constructs same-unit aligned records;
- validates the aligned records mechanically and against the JSON schema.

## Result
All workflow steps passed:
1. qualified P1 path checkout;
2. dependency installation;
3. Spider archive verification;
4. fresh-case manifest generation;
5. pinned Ollama installation/fingerprint;
6. four-case aligned cohort collection;
7. mechanical aligned-record validation;
8. JSON-schema validation;
9. explicit non-confirmatory assertion;
10. artifact upload.

The collector produced:
- decision-time evidence artifact;
- post-lock outcome artifact;
- aligned records;
- runtime qualification metadata.

The dry run is **not confirmatory data** and does not establish predictive validity.

## Hardening failures preserved

### Attempt 1
Collector refused because the workflow did not pass the explicit `--non-confirmatory` safety flag.

Run: **35590449515**

Disposition: workflow corrected; no scientific data were accepted.

### Attempt 2
Collector completed, but the validator rejected an evidence-hash mismatch.

Run: **35590665563**

Cause: collector used the raw C4.2.3-D evidence hash over rows/columns while the frozen P2 aligned-record validator requires the canonical hash over question, database_id, columns, rows, row_count, and column_count.

Disposition: collector corrected to the frozen hash contract.

### Attempt 3
Collector completed, but validation rejected execution-failure cases because missing evidence had been represented as empty arrays/implicit counts.

Run: **35590998123**

Disposition: explicit `NO_USABLE_EVIDENCE` semantics were hardened. Missing rows/columns/counts remain null and evidence_hash remains null; they are never converted to zeros or fabricated empty evidence.

### Attempt 4
Schema validation exposed a record-contract mismatch between the collector provenance/outcome payload and the schema.

Run: **35591330503**

Disposition: collector provenance/outcome structure and schema were reconciled. This was an implementation-contract correction, not a scientific parameter change.

## Scientific boundary
The dry run demonstrates **runtime feasibility and artifact integrity only**.

It does **not**:
- validate X_W reliability on the new cases;
- establish X_W/Y_H predictive validity;
- justify a confirmatory sample size;
- authorize confirmatory M0/M1 fitting;
- establish global P0 determinism;
- turn the four dry-run cases into the confirmatory cohort.

## Current gate disposition
**P2-C1.4-R runtime/evidence-preservation qualification = PASS for non-confirmatory dry-run scope.**

The next scientific gates remain:
1. freeze sample-size/event-rate planning;
2. freeze model/scoring/resampling protocol;
3. freeze the confirmatory cohort manifest;
4. run the actual fresh outcome-bearing cohort;
5. independently annotate X_W blind to outcomes;
6. lock X_W/Y_H/provenance;
7. only then execute confirmatory M0 vs M1.

## Reproducibility note
The successful run is retained as the runtime qualification proof. Failed attempts remain documented rather than overwritten.
