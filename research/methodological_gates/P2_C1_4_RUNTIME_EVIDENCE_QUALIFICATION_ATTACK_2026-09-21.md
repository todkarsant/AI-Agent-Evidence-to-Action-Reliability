# P2-C1.4-R — Runtime and Decision-Time Evidence Preservation Qualification Attack
**Date:** 2026-09-21
**Status:** ATTACK COMPLETED — IMPLEMENTATION GAP IDENTIFIED; COLLECTION NOT YET AUTHORIZED

## Objective
Determine whether the repository currently contains enough executable infrastructure to create a fresh aligned cohort in which the exact decision-time evidence is captured before replacement/outcome information can contaminate X_W.

## Findings
1. The repository contains the methodological specification and historical evidence-capture provenance, but the current P2 repository does not yet expose a verified, end-to-end cohort collector that writes the required aligned unit:
   (decision_id, B, E_decision_time, intervention/replacement, final_correctness, Y_H).
2. The existing 12-case C4.2.4-A packets prove that decision-time evidence can be packaged and independently annotated for that qualification subset. They do not create an outcome-bearing predictive cohort.
3. Historical P1/P6 artifacts cannot be promoted into the new cohort because P2-C1.3 established that the required decision-time evidence is not reconstructable in the required form.
4. The cohort collector therefore remains the immediate implementation dependency.

## Required runtime contract
For every fresh eligible decision:
A. assign immutable decision_id;
B. capture frozen baseline B;
C. capture exact decision-time evidence E before replacement;
D. persist an evidence hash;
E. persist a manifest/code/runtime identifier;
F. make a blinded annotation packet containing only permitted fields;
G. separately record intervention/replacement and final correctness;
H. derive Y_H deterministically after the predictor/evidence artifacts are locked;
I. preserve all hashes and version identifiers without overwriting prior artifacts.

## Runtime stopping tests
Collection must stop if:
- an evidence artifact changes after packet creation;
- decision_id is duplicated or cannot link all required records;
- annotator-facing data contain P0 correctness, reference/gold SQL, reference answer, intervention/replacement, final correctness, Y_H, or post-hoc labels;
- outcome is available before evidence/annotation lock;
- missing evidence is handled differently across cases without a frozen rule;
- shared database/question/run/trace dependence is not recorded;
- rerunning the same decision cannot be distinguished by immutable run identifiers;
- required artifacts cannot be hashed and reconciled.

## Immediate implementation consequence
Do not start confirmatory collection by manually assembling spreadsheets or by retrofitting existing P6 outputs. Implement the fresh collector and validator first, then run a small non-confirmatory dry run to prove the artifact contract before collecting the confirmatory cohort.

## Disposition
**FAIL FOR COLLECTION READINESS — IMPLEMENTATION REQUIRED.**

This is an engineering/provenance gate, not evidence against the scientific hypothesis.

## Next concrete build
Create:
1. a versioned aligned-cohort record schema;
2. a collector that consumes a fresh decision trace and emits predictor/evidence/outcome-separated artifacts;
3. a validator that mechanically checks leakage, linkage, completeness, hashes, and temporal ordering;
4. a dry-run workflow;
5. only after dry-run PASS, freeze the collection protocol and begin the outcome-bearing cohort.

No confirmatory M0/M1 fitting is authorized.
