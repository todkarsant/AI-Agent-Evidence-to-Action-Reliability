# C.4.2.4-A.2b — Mechanical Redundancy Attack

**Date:** 2026-09-18  
**Status:** PRELIMINARY — baseline feature set not yet frozen

## Attack question

Could the redesigned observable witness score be reconstructed from already-available baseline trace variables, making its apparent incremental validity tautological?

## Existing trace variables

The qualified P0 pilot exposes:
- execution status;
- row count;
- column count;
- latency;
- LLM call count;
- input/output tokens;
- cost;
- action count;
- termination/error fields.

The raw evidence additionally contains:
- column identities;
- row values;
- row ordering;
- evidence hash.

## Findings

### W7 / cardinality

If W7 were defined simply as returned row count, it would be mechanically redundant with an existing trace variable.

**Decision: remove W7 from the candidate witness score.**

Open-world completeness is also not identifiable from result-only evidence, so completeness must not be reintroduced under another name.

### W2 / projection

Column identity is not contained in the historical trace; only column count is.

Therefore a projection witness based on requested field identity is not mechanically recoverable from column count alone.

**Status: survives redundancy attack.**

### W3 / aggregation

Aggregate field identity and labels are not represented by historical column count.

**Status: survives simple redundancy attack.**

### W4 / grouping

Per-group structure requires row/column identity and values, which are not represented by row/column counts alone.

**Status: survives simple redundancy attack.**

### W5 / ordering

Displayed row ordering is not represented by row count/column count.

**Status: survives simple redundancy attack.**

### W6 / extremum

Candidate values and comparison-field identity are not represented by row/column counts.

**Status: survives simple redundancy attack.**

### W1 / selection

A selection witness may require predicate-bearing field identity and values. These are not represented by row/column counts.

However, W1 requires careful semantic parsing of the question and schema. That parsing must be frozen independently of outcomes.

**Status: survives simple mechanical redundancy attack; semantic parser remains a separate risk.**

### W7 / join/linkage

Entity identifiers/attributes and their displayed relationship are not represented by row/column counts.

**Status: survives simple redundancy attack.**

## Important limitation

This is not yet an incremental-validity result.

The baseline feature set B has not been formally frozen for P2-C1.2. Therefore the attack can only establish that the witness dimensions are not exact functions of the currently observed coarse trace counts.

A later baseline containing raw evidence features could absorb some or all of X_W.

## Required next attack

Before confirmatory analysis:

1. freeze B independently of X_W;
2. prohibit adding raw-evidence-derived baseline features after seeing X_W results;
3. test nested predictive models M0 and M1;
4. quantify incremental information out of sample;
5. use cross-fitting or an otherwise predeclared evaluation split;
6. report whether any incremental signal survives.

## Current verdict

**No fatal mechanical redundancy found for W1–W6 and W7(linkage).**

**W7(cardinality/completeness) removed.**

The construct remains viable as a measurement variable, but its predictive novelty remains unproven.
