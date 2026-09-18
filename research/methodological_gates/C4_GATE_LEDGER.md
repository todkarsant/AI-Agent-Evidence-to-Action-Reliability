# C.4 Methodological Gate Ledger

## C.4.1-A — Construct Identifiability

**Verdict: FAIL**

Historical P6 eligibility is computed from:

`D = f(Q, SQL, row_count)`

Although the trace stores execution status and column count, the selector does not consume the raw execution result or representation. Most selector branches are independent of row count; the only row-count-sensitive condition concerns zero/nonzero results.

Therefore a semantic-preserving transformation of an underlying result representation could not affect the historical P6 decision path in a meaningful way.

A perturbation-stability construct applied retrospectively would therefore be tautologically invariant for the existing decision-visible representation.

**Implication:** historical P6 cannot be used as the empirical measurement instrument for the proposed evidence perturbation construct.

## C.4.1-B — Alternative Construct Attack

**Verdict: PARTIAL / REDESIGN**

Candidate alternatives considered:

- rich execution-result stability;
- question/query stability;
- decision-state/policy-path stability;
- verification margin;
- provenance completeness;
- evidence sufficiency.

The surviving seam is evidence sufficiency, but generic evidence sufficiency is not claimed as novel. Any defensible novelty must be tied to incremental predictive validity for consequential replacement harm.

## C.4.1-C — Construct Separation

**Verdict: CONDITIONAL PASS**

Candidate construct:

> Independently measured sufficiency of decision-time execution evidence to substantiate the requested analytical result.

Potential formulation:

[
X_E = rac{1}{K}sum_j v(g_j,R,S)
]

where obligations are derived from question/schema and judged against decision-time execution evidence.

The construct must not depend on gold SQL, gold answer, P0 correctness, challenger correctness, replacement outcome, or post-hoc information.

Fresh pilot is required because historical P6 traces do not preserve the underlying evidence.

## C.4.2.1 — Deterministic Obligation Extraction

**Verdict: PROVISIONAL PASS**

Obligation classes can be specified from question/schema without gold SQL. Candidate classes include selection, projection, aggregation, grouping, ordering, extremum, cardinality, and join/entity linkage.

This is provisional: the codebook must be frozen and tested on fresh cases before confirmatory use.

## C.4.2.2 — Measurement Reliability

**Verdict: CONDITIONAL PASS**

Primary measurement must be obligation-level with genuine independent raters.

Required safeguards:

- outcome-blinded annotation;
- no gold SQL/answer;
- independent raters;
- separate frozen codebook;
- intra-rater subset;
- adversarial/borderline cases;
- agreement statistics beyond raw percent agreement.

No empirical reliability coefficient is claimed at this stage because the independent annotation corpus has not yet been completed.

## C.4.2.3-A — Fresh Corpus

**Verdict: PASS**

120 cases across 12 schemas with no historical schema or question overlap.

## C.4.2.3-B — Leakage-safe Input

**Verdict: PASS**

Gold-derived fields are excluded from annotator-facing execution input.

## C.4.2.3-C — Fresh P0 Execution

**Verdict: PASS — pilot qualified**

A 12-case fresh pilot was executed twice through the exact historical P0 provider path. All 12 cases produced identical SQL across repeats and identical execution status. The pilot artifact is preserved in GitHub Actions run 35335264293.

This qualifies runtime/trace determinism only; it does not establish full-corpus accuracy or historical model-artifact identity.

## C.4.2.3-D — Observational Evidence Capture

**Verdict: PASS — measurement path qualified**

A second 12-case pilot captured raw SQLite execution rows and column names observationally while preserving the historical P0 return contract. Across two repeats, SQL, execution status, and captured evidence were identical for all 12 cases; captured row/column counts matched the historical trace counts.

This establishes the forward evidence-capture mechanism. It does not retroactively prove preservation of discarded historical raw evidence.

## P2-C1.2 — Predictive / Incremental Validity

**Verdict: PENDING**

Must use a frozen baseline feature set and candidate construct, evaluate out of sample, and preserve the specification before outcome-dependent analysis.
