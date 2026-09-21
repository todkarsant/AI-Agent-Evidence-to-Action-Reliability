# P2-C1.4 Confirmatory Aligned Cohort — Acquisition Forensic Audit

**Date:** 2026-09-21  
**Status:** **ACQUISITION IN PROGRESS — NOT YET COHORT-COMPLETE**

## 1. Scope

This audit records the forensic inspection of the actual GitHub Actions confirmatory acquisition runs. It does not treat failed runs as scientific data and does not authorize X_W annotation or M0/M1 modeling.

## 2. Confirmatory run history inspected

### Run #1
- Workflow: `p2-c1-4-confirmatory-acquisition`
- Run ID: `35595401984`
- Commit: `408e86bec3dc3c04c205c9b8e2de61b918faa3b9`
- Conclusion: FAILURE
- Freeze-manifest job: PASS
- Frozen source-frame manifest: generated successfully
- Source-frame case count: **8,638**
- Pilot exclusions: **12**
- Manifest SHA-256: `4534bff6c3cbb074e5dc336a1ea48c6606de8e3628dc940ee8b29ed3ce72291d`

### Run #1 failure
The collector reached the execution step but stopped before scientific collection because the runtime guard required the pinned Ollama provider and the workflow did not export `LLM_PROVIDER=ollama`.

This is a runtime configuration failure, not a scientific result.

### Run #2
- Workflow: `p2-c1-4-confirmatory-acquisition`
- Run ID: `35595461664`
- Commit: `bc73c06f35ed23e75d1c50e92755e818d80b2ba2`
- Conclusion: FAILURE
- Freeze-manifest job: PASS
- Collector failure: all inspected shards stopped at the collector input stage.

### Run #2 failure
The workflow created `data/confirmatory_questions_source.json` in the manifest job, but each matrix shard runs on a fresh GitHub runner and therefore did not have that generated file. The collector consequently failed with:

`FileNotFoundError: data/confirmatory_questions_source.json`

This is an infrastructure/workflow artifact-transfer error, not a scientific result.

### Run #3 — new failure discovered

Run #3 (`35596426619`) reached the collector with the provider/source fixes active. Several shards then failed with `FAIL: no execution capture` for individual cases. Inspection of the collector and pinned P6-IP runner established that some P0 cases legitimately produce no SQL, so there is no executable decision-time result to capture. The prior collector incorrectly escalated this to a shard failure.

This was treated as a protocol-preserving implementation defect: genuine no-SQL/no-execution cases are now represented as `NO_USABLE_EVIDENCE` (null evidence fields), while a case that has executable P0 SQL but lacks a capture still fails closed. No X_W value is generated.

The same run also exposed a consolidation risk: the previous consolidator could combine only successful shards. It has now been changed to fail closed unless every expected non-empty shard is present with the exact manifest decision IDs/counts.

## 3. Corrective change

Commit:
`714f311bc3994018fe05a1b711dd1c66f1125d0d`

The workflow was corrected to:
1. reconstruct the combined training-side question source inside every acquisition shard;
2. export `LLM_PROVIDER=ollama`;
3. explicitly use the pinned `llama3.2:1b` provider endpoint.

The frozen scientific protocol was not changed.

## 4. Corrective change commit

Commit `a30e8bcd674a6559dc3ba99a49746610fa600281` implements the genuine-NO_USABLE_EVIDENCE handling.

Commit `6229b237383fbe4c5db7c45bf2134b6cab40d8fb` adds fail-closed complete-shard reconciliation.

These changes do not alter the frozen scientific construct, outcome definition, model family, or analysis protocol.

## 5. Current run

Run #3:
- Run ID: `35596426619`
- Commit: `714f311bc3994018fe05a1b711dd1c66f1125d0d`
- Status at audit time: **IN PROGRESS**
- Freeze-manifest: PASS
- Confirmatory source frame: 8,638 cases
- Acquisition: active across the matrix shards
- No X_W annotation
- No M0/M1 fitting

The first ten acquisition shards are currently executing in parallel; remaining shards are queued. No shard failure had been observed at the audit checkpoint.


### Current reruns

- Run #4: `35596975423` — started from the no-evidence hardening commit.
- Run #5: `35596992786` — started from the complete-shard fail-closed hardening commit and is the **current target run**.
- Earlier runs remain forensic-only and are not eligible as confirmatory cohort sources.

## 6. Scientific integrity decision

The two failed runs are retained as infrastructure failures and are **not** incorporated into the confirmatory cohort.

No scientific parameter was altered:
- source population unchanged;
- protocol ID unchanged;
- model family unchanged;
- X_W definition unchanged;
- outcome definition unchanged;
- resampling plan unchanged.

The confirmatory cohort is not considered complete until the frozen source frame is reconciled against all successful shard records and the forensic auditor passes.

## 7. Completion criteria

Cohort completion requires:
1. all source-frame cases accounted for;
2. no missing shard coverage;
3. unique decision IDs;
4. exact manifest-to-record reconciliation;
5. pilot exclusion verified;
6. evidence-before-intervention verified;
7. evidence hash verification passed;
8. NO_USABLE_EVIDENCE represented as missing, never zero;
9. Y_H formula verified;
10. no forbidden outcome/correctness/SQL fields in decision-time evidence;
11. consolidated cohort hash recorded;
12. forensic audit artifact preserved.

Only after these conditions pass may the independent blinded X_W annotation stage begin.

## 8. Current disposition

**P2-C1.4 acquisition: IN PROGRESS.**  
**Forensic cohort PASS: NOT YET ESTABLISHED.**  
**X_W annotation: BLOCKED pending cohort lock.**  
**M0/M1 modeling: BLOCKED.**

