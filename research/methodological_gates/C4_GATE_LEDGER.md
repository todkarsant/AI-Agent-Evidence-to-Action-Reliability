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


## C.4.2.4-A — Double-blind annotation feasibility / adversarial pilot

**Verdict: OPEN — awaiting two genuinely independent raters**

Two outcome-blinded, independently randomized 12-case annotation packets have been prepared from the qualified C4.2.3-D evidence-capture artifact.

The packets expose only question, schema, execution status, result columns, result rows, and counts. Gold SQL, generated SQL, correctness, intervention/replacement, downstream outcomes, and post-hoc labels are excluded.

The pilot contains 7 cases with interpretable execution evidence and 5 execution-failure/no-usable-evidence cases; failures are intentionally retained for feasibility analysis.

No inter-rater reliability coefficient is reported yet. A second model run or duplicate annotation by the same rater would not constitute independent replication.

Required next action: obtain two independently completed raw annotation sets, lock them unchanged, then calculate obligation-level agreement statistics and conduct the predefined disagreement/codebook-failure audit. Any codebook revision after outcome-bearing annotation begins must create a new codebook version and measurement cohort.


## C.4.2.4-A — Model-only adversarial feasibility subtest

**Verdict: NON-CONFIRMATORY / HUMAN VALIDATION STILL REQUIRED**

Two separately specified model annotation passes were run on the blinded 12-case pilot. This does not constitute independent human-rater replication.

Results over 23 binary obligation comparisons:
- raw agreement: 20/23 = 86.96%;
- Cohen's kappa: 0.721;
- Gwet AC1: 0.756.

Three disagreements exposed unresolved boundary cases involving empty-result projection, extremum semantics, and top-k completeness.

The model-only result therefore neither validates nor falsifies the construct. It identifies concrete adversarial cases that must remain in the human annotation cohort.



## C.4.2.4-A.1 — Formal observability matrix

**Verdict: FAIL FOR CURRENT X_E OPERATIONALIZATION**

A case-by-case attack found repeated non-identifiability of semantic sufficiency from (question, schema, result evidence) alone. Selection, top-k/extremum, completeness, join/linkage, and population-level aggregate semantics can admit materially different latent execution states with identical observable result evidence.

This means human agreement cannot rescue the current result-only semantic-sufficiency definition.

Candidate redesigns:
1. add independently verifiable execution/provenance witnesses without collapsing into gold/query verification; or
2. redefine the construct as observable evidence-witness coverage rather than semantic sufficiency.

Next gate: **C.4.2.4-A.2 — redesign + novelty attack**.


## C.4.2.4-A.2 — Observable witness redesign + novelty collision

**Verdict: PASS WITH MAJOR NOVELTY RESTRICTION**

The redesigned observable evidence-witness construct survives the A.1 identifiability attack because it measures only what is visibly inspectable in decision-time evidence rather than hidden SQL correctness.

Current-literature collision attack found that evidence sufficiency, evidence coverage, claim-level support, provenance-aware action auditing, and evidence-backed action gating are already active research areas.

Therefore the witness score is **not** a standalone novelty claim.

The potentially defensible seam remains the incremental predictive validity of an independently measured decision-time witness-coverage variable for consequential incumbent-replacement harm.

## C.4.2.4-A.2b — Mechanical redundancy attack

**Verdict: PRELIMINARY PASS**

A simple attack against currently available coarse trace variables found cardinality/completeness to be mechanically redundant if defined as row count; that dimension is removed from the candidate score.

Projection, aggregation, grouping, ordering, extremum, selection, and join/linkage witness dimensions are not exact functions of the currently available row/column counts and coarse runtime variables.

This is not yet an incremental-validity result because the P2-C1.2 baseline feature set has not been formally frozen.

## C.4.2.4-A.3 — Witness Codebook / Baseline-Independence Attack

**Verdict: CONDITIONAL PASS FOR CONSTRUCT SURVIVAL; FREEZE BLOCKED**

The surviving witness dimensions W1-W7 are not mechanically reconstructible from the currently recovered coarse trace variables and can be defined without hidden SQL. W1 remains the highest semantic-parsing risk. The attack does not establish incremental predictive validity.

Freeze remains blocked until the baseline feature set is explicitly frozen independently of X_W, adversarial examples are finalized, and the final literature collision search is refreshed.