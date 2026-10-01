# P2-C1.4 Qualification Gate (G3) Amendment

**Amendment ID:** `P2-C1.4-QUALIFICATION-GATE-G3-AMENDMENT-2026-10-01`
**Date:** 2026-10-01
**Status:** Approved by the author 2026-10-01. Adopted while qualification run `36847267797` was in progress and before any of its record-status counts were seen.
**Frozen protocol:** `P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21` (unchanged)
**Replaces:** gate G3 in §7 of `P2-C1.4-RUNTIME3-PATHOLOGICAL-SQL-RECOVERY-AMENDMENT-2026-09-30` ("200/200 evaluable, 0 runtime failures").
**Builds on:** `P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01`.

## 1. Why

The missingness amendment made runtime failures recorded, mechanically classified outcomes (E2, E3/E4) instead of crashes. That had a side effect that was not written down: the collector no longer crashes on a runtime failure, so qualification could pass with failures and start acquisition automatically. Before that amendment, the "0 runtime failures" rule was only enforced implicitly, by the crash.

There were two further problems:

- The old G3 cannot be verified retrospectively. Project 1 silently scored P0 runtime failures as ordinary incorrect answers, so the 200/200 result of qualification #70 (`36689586772`) may contain hidden failures.
- With `llama3.2:1b`, the discarded acquisition run `36691960508` showed at least 12 unrecovered failures across the cohort (a lower bound). A clean 200/200 would mostly reflect which 200 cases were sampled, not the reliability of the run.

Requiring zero failures in qualification therefore no longer matches how the confirmatory acquisition treats failures. Leaving the gate unbounded would let a badly degraded run proceed, which would bias the primary population and make the S2 bounds uninformative.

## 2. Amended gate (frozen)

### G3 — qualification (200 frozen decisions P2C14-CONF-000001…000200)

Qualification passes only if all of the following hold. Each check fails closed.

1. Exactly the 200 frozen decision IDs, in frozen order.
2. Every record carries one valid `record_status`.
3. The aligned-record validator and the JSON schema pass.
4. E1 status agrees with the pre-acquisition reference-SQL census.
5. **Runtime failures (E2 + E3/E4) ≤ floor(0.05 × 200) = 10.**

### G4 lock condition — confirmatory cohort (8,638 frozen decisions)

The forensic immutable lock is refused unless all existing lock checks pass **and runtime failures (E2 + E3/E4) ≤ floor(0.05 × 8,638) = 431**. A refused cohort is preserved as an unlocked artifact, diagnosed and not analysed.

### Code identity

Acquisition starts only if the science code is byte-identical to the qualified commit. The science code is `runtime3_ollama.py`, the prompt amendment, and the collector, census, validator and schema files.

## 3. Choice of the 5% ceiling

The frozen design does not specify a ceiling. The value is a judgement fixed before any status count from the current run was seen. The only evidence used was:

- 1/200 runtime failures in Run #59;
- at least 12 failures across the discarded acquisition.

5% leaves margin above both while still excluding a seriously degraded run. The denominator is all frozen records in the checked set, including E1.

## 4. What is not changed

The cohort, manifest, status definitions, primary analysis, S1/S2, estimand, model, temperature, seeds and Project 1 code are unchanged. Failure counts and the pathological-SQL recovery count are reported whatever the gate outcome.

## 5. Implementation

- `research/cohort/check_P2_C1_4_runtime_failure_gate.py` (new). It is outcome-blind: it reads only decision IDs, `record_status` and the census.
- `p2-c1-4-runtime3-sequential-qualification.yml`: G3 check after validation. The qualification manifest is copied into the uploaded artifact, and the verdict is written to `G3_GATE_VERDICT.json`.
- `p2-c1-4-confirmatory-acquisition-runtime3.yml`:
  - a new first job, `qualification-gate`, verifies the authorising qualification run (success, on main), checks code identity, downloads that run's artifact and re-applies G3;
  - manual dispatch must name a qualification run ID;
  - the 5% ceiling runs before the forensic lock;
  - a refused cohort is uploaded as `p2-c1-4-confirmatory-cohort-REFUSED-NOT-LOCKED`.
- Run `36847267797` was started from commit `b3e5eb7`, before this gate existed. Its own workflow does not apply the 5% check. The acquisition's `qualification-gate` job applies it to that run's artifact.
- Run `36847267797` finished while this amendment was being implemented. The old, ungated workflow auto-started acquisition run `36852043181`, which was cancelled before any shard completed. Only its manifest-freeze and transport-test jobs finished, and none of its artifacts were read.
- Acquisition was then re-dispatched under the gated workflow as run `36853456589` (main @ `87a66ef`), naming qualification run `36847267797`.

## 6. Verification

The checker was tested locally:

- passes at 10/200 failures, including with 2 E1 records;
- fails at 11/200;
- fails on: an E1 record not in the census, a census E1 missing from the records, a missing record, an unknown status, a missing status, and a decision-order swap.

The ceiling for 8,638 records is 431.
