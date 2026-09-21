# P2-C1.4 — Decision-Time Schema Preservation Audit

**Date:** 2026-09-21  
**Status:** **BLOCKER FOUND AND CORRECTED BEFORE ACCEPTING CONFIRMATORY COHORT**

## Finding

Forensic review of the collector against the frozen P2-C1.4 design found that the collector stored `database_id` but did not store the exact database schema in `decision_time_evidence`.

This violated the design requirement that decision-time evidence preserve the schema/database context required for independent W1-W7 witness annotation.

The omission was discovered before any complete confirmatory cohort was accepted and before any X_W annotation.

## Why this matters

W1-W7 annotation requires the annotator to inspect the analytical obligation against the visible evidence and schema. A database identifier alone is not equivalent to the schema artifact.

Proceeding to annotation without the schema would create an avoidable measurement-design gap.

## Correction

The collector now captures:

`question + database_id + schema + returned_columns + returned_rows + row_count + column_count`

The schema is captured from the same pinned dataset environment used for the decision.

The evidence hash now covers the schema as well as the question, database identifier, returned columns, returned rows, and counts.

The aligned record schema was versioned from:

`P2-C1.4-ALIGNED-V1`

to:

`P2-C1.4-ALIGNED-V2`

The new schema artifact is:

`research/cohort/P2_C1_4_ALIGNED_DECISION_RECORD_SCHEMA_V2.json`

The mechanical validator now requires and hashes the schema field.

## Scientific boundary

This is a pre-acceptance measurement/provenance correction.

It does not use outcomes, Y_H, X_W, or model results to modify the construct.

The affected acquisition attempts remain ineligible for cohort lock.

## Required consequence

The amended runtime acquisition must regenerate the complete aligned cohort so that every accepted decision record contains the schema artifact before the immutable cohort lock.

No X_W annotation may begin until the schema-preservation audit passes.

## Disposition

**Schema-preservation gate: corrected; fresh acquisition required.**

