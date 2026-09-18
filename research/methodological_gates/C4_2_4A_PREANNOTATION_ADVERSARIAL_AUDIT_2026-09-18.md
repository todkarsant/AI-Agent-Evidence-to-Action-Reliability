# C.4.2.4-A — Pre-annotation adversarial audit

**Date:** 2026-09-18  
**Status:** ADVISORY AUDIT — does not substitute for independent raters

## Scope

This audit inspects the frozen 12-case packets before raw human annotations exist. It does not generate rater labels and therefore does not produce inter-rater reliability statistics.

## Structural verification

Both packets contain:
- 12 identical case IDs;
- identical underlying question/schema/evidence content;
- different case order;
- blank annotation forms;
- identical blinding exclusions.

The five execution-failure cases are represented as `NO_USABLE_EVIDENCE` evidence and must remain in the pilot.

## Construct attacks exposed by the pilot

### 1. Selection/filtering cannot always be substantiated by output rows alone

Example: “student ids for all male students” exposes only `StuID` values. Without a gender-bearing column in the displayed result, the evidence cannot by itself demonstrate the male restriction. A rater must not infer the hidden predicate from the question alone.

**Threat:** a rater who treats plausible output as proof of the predicate would be reconstructing hidden SQL.

### 2. Cardinality/completeness is intrinsically difficult

Questions containing “all” can require a completeness claim that a finite returned result does not independently establish. The codebook therefore correctly limits O7 to cases where the requested completeness/cardinality claim can actually be assessed from the evidence.

**Threat:** treating row count as proof that the result is complete.

### 3. Extremum/top-k can be visually plausible but not evidentially demonstrated

For “most” or “top 3” questions, a returned row or three rows does not, by itself, establish that no omitted candidate exceeds the returned value. O5/O6 must not be inferred merely from the number of displayed rows.

### 4. Join/entity linkage can be underdetermined

A result may contain requested attributes while failing to demonstrate that the relationship between entities satisfies the requested linkage. The schema can show possible relationships, but the evidence must substantiate the requested linkage without hidden SQL reconstruction.

### 5. Empty result is a genuine edge case

The academic case has an empty result with eight columns. It must not be automatically classified as insufficient. The rater must determine whether the evidence structure can substantiate the requested analytical obligation without assuming that the underlying query was correct.

### 6. Aggregate output can be semantically interpretable

The aircraft case returns named maximum/minimum aggregate columns and one row. This is a useful positive feasibility case for O3, but it does not prove the underlying aggregate was computed over the intended population. Raters must judge only what the displayed evidence itself establishes under the frozen rule.

## Critical conclusion

The pilot reveals a central construct-validity tension:

> **Result evidence can demonstrate the shape/content of an output without necessarily demonstrating the semantic provenance or completeness of that output.**

This is not a reason to alter labels before annotation. It is precisely the falsification target of C.4.2.4-A.

## Reliability prohibition

No Cohen's kappa, Gwet AC1, agreement percentage, or PASS verdict may be reported until two genuinely independent raw annotation sets are supplied.

A second model-generated label set would not satisfy the independence requirement.

## Gate state

**C.4.2.4-A remains OPEN.**

Next valid operation: obtain and lock Rater A and Rater B raw annotation forms, then run the prespecified statistical and disagreement analyses.
