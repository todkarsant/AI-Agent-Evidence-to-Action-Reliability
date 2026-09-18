# C.4.2.3-D — Observational Evidence-Capture Pilot

**Workflow run:** 35339566289  
**Workflow:** `c4-2-3-evidence-capture12`  
**Commit:** `45944310f9c06f647d7fea112f22a9a73b24b1cc`  
**Pilot:** 12 fresh cases, each executed twice through historical P0  
**Historical P0 commit:** `1765680283df63232018bf7b827d1576c81c3a61`  
**Runtime:** Python 3.11.16; Ollama 0.33.3; `llama3.2:1b`

## Purpose

Validate that the raw execution result needed for the proposed evidence-sufficiency construct can be captured observationally without changing the historical P0 generation/decision path.

The capture evaluator retains the exact historical return contract:

`(ok, error, row_count, column_count)`

while additionally retaining the executed rows and column names. No captured evidence is fed back into P0 generation or routing.

## Gate checks

| Check | Result |
|---|---:|
| Exact P0 SQL agreement across repeats | **12/12** |
| P0 execution-status agreement | **12/12** |
| Captured evidence exact agreement across repeats | **12/12** |
| Historical trace row/column counts = captured counts | **PASS** |
| Capture observational only | **PASS** |
| Gold SQL exposed to provider | **NO** |

For successful executions, the captured evidence contains the actual returned rows and column names. For failed executions, the capture records the execution error and no fabricated result.

## Evidence

GitHub Actions artifact:

`c4-2-3-evidence-capture12`

Artifact SHA-256:

`d6929e66819ddba8c94c871900877a96b9334d9807b2f66348691b3da6d75079`

The artifact contains `evidence_capture_pilot12.json`, including paired trace/capture records and deterministic evidence hashes.

## Verdict

### **C.4.2.3-D = PASS**

The pilot demonstrates that the raw execution evidence required for subsequent evidence-obligation measurement is technically observable while preserving the historical P0 provider path and its output determinism on the fresh pilot.

This is a **measurement-instrument qualification**, not evidence that the proposed construct is valid, reliable, or predictive.

## Boundary

The capture is reconstructed from the same read-only SQLite execution performed by the historical evaluator. Because the historical trace discarded raw rows, this pilot cannot retrospectively prove that every byte of a historical transient result was preserved. It establishes the forward measurement mechanism for the fresh study.

Next gate: freeze the evidence-obligation codebook and run the independent double-blind annotation pilot.## Post-PASS requalification finding — 2026-09-18

A later rerun of this workflow failed the upstream repeatability prerequisite on `behavior_monitoring`. SQL, execution status, and captured evidence differed across the two repeats. The integrity check that captured row/column counts matched the trace still passed, but this does not rescue the repeatability failure.

**Current gate status: REOPENED / FAIL pending determinism characterization.**
