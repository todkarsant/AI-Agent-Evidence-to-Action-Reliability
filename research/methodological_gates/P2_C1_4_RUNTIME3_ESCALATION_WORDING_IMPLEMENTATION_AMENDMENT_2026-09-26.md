# P2-C1.4 Runtime3 Escalation-Wording Implementation Amendment

**Amendment ID:** `P2-C1.4-RUNTIME3-ESCALATION-WORDING-AMENDMENT-2026-09-26`  
**Date:** 2026-09-26  
**Status:** implementation correction pending confirmatory re-qualification smoke

## Purpose

The frozen P2-C1.4 confirmatory cohort and statistical protocol are not changed by
this amendment. The amendment changes one Runtime3 provider-boundary prompt
sentence because the frozen Project1 escalation wording was observed to trigger
a reproducible runaway-generation pathology in the pinned local Runtime3
environment.

## Evidence basis

The non-confirmatory qualification recorded in
`research/qualification/p2_c1_4_escalation_wording_qualification.py` used the
actual pinned Project1 `p6_ip_runner.run_case()` path and compared:

**Baseline**

> This is a post-evidence escalation. Re-check joins, filters, grouping,
> ordering and nested-query semantics before answering.

**Candidate**

> This is a post-evidence escalation. Re-check the SQL against the schema and
> question before answering.

The earlier qualification established the candidate wording on the frozen
12-case pilot. Case `P2C14-CONF-000046` was also directly ablated: the baseline
wording reproduced the output-limit pathology while the candidate wording
completed in the controlled ablation.

On 2026-09-26, the current local Runtime3 qualification smoke independently
reproduced the case-46 failure with the exact previously captured P6 prompt
hashes:

- call 1: `b38d0e9ca9f5b1b801768a95fa480cee4353c73f03bf6661fb5ff480e2104f05`
- call 2: `0a422005e9536fcf204c6df5c321c9682ec8dc7e6501147fa5296331ccabb5ca`

The second call terminated at the configured 2048-output-token guard.

## Exact implementation change

The pinned Project1 code is not modified.

The P2-C1.4 Runtime3 provider boundary now:

1. leaves prompts containing no escalation sentence unchanged;
2. replaces exactly one occurrence of the frozen escalation sentence with the
   candidate sentence;
3. fails closed if more than one occurrence is present;
4. records the amendment identifier in confirmatory provenance/metadata.

No SQL, schema, model, case selection, outcome rule, evidence definition,
annotation rule, statistical model, seed, or cohort manifest is changed.

## Scientific status

This is an **implementation correction discovered after the original runtime
freeze**, not a retroactive claim that the correction was part of the original
prospective implementation.

The original frozen confirmatory cohort selection rule remains unchanged.
The correction must pass the current two-case Runtime3 smoke before any
confirmatory acquisition is started.

A failure of the amended smoke keeps the confirmatory acquisition blocked.

## Reproducibility

The correction is implemented in:

- `research/runtime3_confirmatory_prompt_amendment.py`
- `research/cohort/collect_P2_C1_4_aligned_cohort.py`

Unit tests are in:

- `research/tests/test_runtime3_confirmatory_prompt_amendment.py`

The confirmatory collector records:

`runtime3_implementation_amendment =
P2-C1.4-RUNTIME3-ESCALATION-WORDING-AMENDMENT-2026-09-26`

in provenance/qualification metadata.
