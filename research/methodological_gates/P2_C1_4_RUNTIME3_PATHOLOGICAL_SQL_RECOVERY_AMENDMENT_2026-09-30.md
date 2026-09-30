# P2-C1.4 Runtime3 Pathological-SQL Recovery Implementation Amendment

**Amendment ID:** `P2-C1.4-RUNTIME3-PATHOLOGICAL-SQL-RECOVERY-AMENDMENT-2026-09-30`
**Date:** 2026-09-30
**Status:** approved by the author 2026-09-30; G1 passed; G2 implemented; G3 (200-case re-qualification) pending
**Supplements (does not replace):** `P2-C1.4-RUNTIME3-ESCALATION-WORDING-AMENDMENT-2026-09-26`
**Frozen protocol:** `P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21` (unchanged)

## 1. Purpose

This amendment adopts a bounded, detector-gated recovery for one Runtime3
provider-boundary failure mode: runaway, self-repeating nested-SQL generation
that exhausts the output-token ceiling or the read timeout before a complete
JSON object is produced.

It is adopted **before any confirmatory outcome data exist** so that every frozen
decision can remain evaluable without converting a runtime failure into a
synthetic observation and without changing the preregistered denominator.

The frozen cohort, manifest, 8,638 target, 44-shard layout, outcome definition,
evidence definition, X_W definition, annotation protocol, statistical estimand,
model family, seeds, model identity, temperature and Project1 code are unchanged.

## 2. Why an amendment is required

The frozen protocol provides no rule for runtime non-evaluable decisions
(§13 covers only missing X_W; §16 stops analysis if missingness handling differs
from the protocol). Runtime Amendment 5 states that a timeout "is never converted
into a synthetic observation." Therefore neither silently dropping nor
synthetically scoring a runtime failure is permitted. Preventing the failure at
the provider boundary, under a disclosed rule fixed before outcomes, is the
route that leaves the frozen analysis untouched.

## 3. Evidence basis

| Evidence | Run / ID | Finding |
|---|---|---|
| Sequential qualification | Run #32 | A generation reached exactly 8,192 tokens (eval ≈838 s); not an HTTP timeout. |
| Sequential qualification | Run #33 `36444107708` | Preflight 000091 passed; full sequential run again reached an 8,192-token generation. |
| Sequential qualification (continuation branch) | Run #59 `36522954069` | 200 frozen IDs, **199 evaluable, 1 runtime failure: `P2C14-CONF-000091`** (per `RESEARCH_STATUS.md`). |
| Isolated diagnostic | Pathology diagnostic #1 `36586138646` | 000091 alone: escalated (P5/P6) call hit `httpx.ReadTimeout` at 120 s on both attempts (non-streaming transport). |
| Isolated diagnostic | Pathology diagnostic #6 `36674475911` | 000091 alone: two normal generations (41 and 49 tokens, `stop`); recovery **not triggered**; exit 0. |
| Unit test | `test_runtime3_candidate_stream_recovers_pathological_partial_response` | Mechanism verified against a mock server (13/13 transport tests pass at `f073729`). |

Interpretation: the failure is run-context-dependent and not deterministic.
No random seed is introduced and no determinism is claimed.

**Real-output check (G1, passed 2026-09-30):** the Run #59 artifact
(`p2-c1-4-runtime3-sequential-qualification-200`) retains the first-attempt
response for 000091 in both the preflight and the 200-case ledgers. The two are
byte-identical: `done_reason=length`, `eval_count=4096`, 19,404 characters,
SHA-256 `ab8f20776aa46cd37db6d287fd8628e8f6a50fe7e662c15f6e434b062d52eb94`,
not a complete JSON object. The unmodified detector returns true on it, first
by character 264. The second attempt timed out. This exact text is committed as
the test fixture `research/tests/fixtures/p2c14_000091_run59_runaway_4096.txt`.

## 4. Exact implementation rule

### 4.1 Activation
Enabled only when `RUNTIME3_ENABLE_PATHOLOGICAL_SQL_REPAIR=1`, set identically
for the 200-case re-qualification and for all 44 acquisition shards. It must be
either on for the whole confirmatory acquisition or off for all of it.

### 4.2 Detector (unchanged from current code)
`_has_pathological_sql_repetition(text)`: lower-case, tokenize with parentheses
separated, require ≥24 tokens, and return true if any contiguous 8-token window
occurs ≥3 times.

### 4.3 Trigger
Recovery is considered only when the assistant content is **not** a complete
JSON object and either:
- (a) the generation ended with `done_reason == "length"`, or
- (b) the stream ended by timeout/network/protocol error after partial content,

**and** the accumulated partial content is detector-positive.
A complete JSON object is always accepted as-is, including under `length`.

### 4.4 Single bounded repair
At most **one** repair per provider call. The repair request is the original
prompt followed by this fixed text (verbatim, as currently implemented and tested):

> CANDIDATE DIAGNOSTIC RECOVERY: The previous generation was pathologically
> repetitive. Produce one concise read-only SELECT that directly answers the
> question using only the supplied schema. Return only the required JSON object.

Repair output ceiling: `RUNTIME3_PATHOLOGICAL_REPAIR_OUTPUT_TOKENS=2048`.
Same model, temperature 0, same JSON schema, same context window (16,384).
Total attempts remain bounded by `RUNTIME3_OLLAMA_MAX_ATTEMPTS=2`.

### 4.5 Transport
With recovery enabled, the provider uses Ollama streaming so partial content is
observable on timeout. Model, options and schema are identical to the
non-streaming path. This transport difference is disclosed as part of the
amendment.

### 4.6 Fail closed
If the repair does not yield a complete JSON object, the provider raises the
existing bounded `RuntimeError`. No SQL is invented, truncated or edited.
The acquisition then fails its gate; it does not continue by relabeling.

### 4.7 Disclosure / provenance (implementation required)
For every decision the collector records, in the aligned-record provenance
(written after the evidence lock) and never in the decision-time evidence
artifact from which annotation packets are built:
- `runtime3_pathology_recovery_enabled` (true/false);
- `runtime3_pathology_recovery_amendment` = this amendment ID when enabled;
- `runtime3_pathology_recovery_applied` (true/false).

A separate `pathology_recovery_ledger.json` lists, per affected decision, each
repair's trigger (`length` or `transport_error`), SHA-256 and length of the
pre-repair partial content, repair ceiling, and whether the repair completed.
The run manifest records `runtime3_pathology_recovery_decision_count`.

The manuscript reports the number of decisions in which recovery fired.
Recovery status is **not** used as a predictor, covariate, exclusion criterion
or outcome, and is never shown to annotators.

## 5. What this amendment does NOT permit
- It does not authorize PR #28's non-evaluable continuation for confirmatory data.
- It does not raise output ceilings or timeouts.
- It does not alter prompts for any decision whose generation is not
  detector-positive.
- It does not permit case-specific handling of 000091 or any other decision.

## 6. Scientific status
This is an **implementation amendment adopted after the original runtime freeze
and before any confirmatory outcome data**, in response to an observed runtime
pathology. It is not represented as part of the original prospective
implementation. For affected decisions, the evaluated SQL is the post-repair
SQL, and this is disclosed.

## 7. Acceptance gates (all required, in order)
- **G1 — Real-output detector check:** the detector returns true on a real
  captured runaway output from 000091 (e.g. the retained 4,096-token response in
  the Run #59 artifact). If it returns false, stop and revise this amendment
  before any further run.
- **G2 — Implementation + tests:** §4.7 provenance implemented; transport and
  collector unit tests pass in CI.
- **G3 — Re-qualification:** one sequential 200-case qualification with recovery
  enabled: **200/200 evaluable, 0 runtime failures**, recovery-fired count reported.
- **G4 — Acquisition:** only then the 8,638-record / 44-shard acquisition under
  identical settings, followed by exact manifest reconciliation, forensic audit
  and immutable lock.

Failure of any gate keeps confirmatory acquisition blocked.

## 8. Reproducibility
- Implementation: `runtime3_ollama.py` (`Runtime3OllamaProvider._chat`,
  `_has_pathological_sql_repetition`)
- Tests: `research/tests/test_runtime3_ollama_transport.py` (17 tests; pass with recovery on and off)
- Real-output fixture: `research/tests/fixtures/p2c14_000091_run59_runaway_4096.txt`
- Workflows (identical settings): `p2-c1-4-runtime3-sequential-qualification.yml`, `p2-c1-4-confirmatory-acquisition-runtime3.yml`
- Collector provenance: `research/cohort/collect_P2_C1_4_aligned_cohort.py`
- Aligned-record schema: `research/cohort/P2_C1_4_ALIGNED_DECISION_RECORD_SCHEMA_V2.json`
  gains optional provenance properties `runtime3_pathology_recovery_enabled`,
  `runtime3_pathology_recovery_amendment`, `runtime3_pathology_recovery_applied`,
  and the previously unlisted `runtime3_implementation_amendment` (emitted since
  2026-09-26). Required fields, decision-time evidence fields, hashes and the
  `P2-C1.4-ALIGNED-V2` protocol version are unchanged; unknown fields remain rejected.
  Records in the PR #28 non-evaluable format remain schema-invalid.
