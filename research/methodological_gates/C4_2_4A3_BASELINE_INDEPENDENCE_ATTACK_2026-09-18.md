# C.4.2.4-A.3 — Witness Codebook v2 / Baseline-Independence Attack

Date: 2026-09-18
Status: ATTACK COMPLETED — codebook remains NOT FROZEN

## Purpose
Attack the observable evidence-witness construct before human reliability work: whether each witness is observable without hidden SQL leakage and whether it is distinct from recovered decision-time trace signals.

## Candidate construct
X_W = mean over applicable witness dimensions of w_j(Q,S,R)

Current dimensions: W1 Selection; W2 Projection; W3 Aggregation; W4 Grouping; W5 Ordering; W6 Extremum; W7 Join/linkage.

Cardinality/completeness remains excluded because simple row-count coverage is mechanically redundant with the existing row_count trace variable and open-world completeness is not identifiable from result-only evidence.

## Leakage attack
A witness may use only the natural-language question, database schema, decision-time execution status, displayed result column identities, and displayed result rows.

Prohibited inputs: generated SQL, gold SQL, gold answer, P0 correctness, challenger output, intervention/replacement, and post-hoc evaluator labels.

Result: all seven surviving dimensions can be stated without requiring hidden SQL. W1 is the highest-risk dimension because predicate-bearing attributes/values must be derived from question/schema without importing unobserved SQL semantics. W1 therefore requires explicit adversarial examples before freeze.

## Hidden-correctness attack
A visible witness is not proof that the underlying query is correct.
- W1 can be present for a wrong population.
- W5 can be present even when omitted rows change a global top-k answer.
- W6 can be present even when the displayed candidate is not globally extreme.
- W3 can be present when the aggregate uses the wrong population.
- W7 can be present when a relationship is inspectable but the underlying join is wrong.

Therefore X_W is an observability/inspectability variable, not a correctness label.

## Baseline-independence attack
Recovered historical trace variables are: execution status, row count, column count, latency, LLM call count, input/output tokens, cost, action count, and termination/error fields. Raw evidence additionally contains column identities, row values, row ordering, and an evidence hash.

No surviving W dimension is an exact function of the coarse row/column counts and runtime variables alone. This reproduces the A.2b mechanical-redundancy finding.

This does not establish incremental validity. A future baseline could include raw-evidence-derived variables and absorb some or all of X_W.

## Required baseline freeze
Before confirmatory P2-C1.2 analysis, the baseline must be frozen independently of X_W and must prohibit adding evidence-derived variables after observing X_W or harm outcomes.

A conservative baseline candidate is the already-observed coarse decision/runtime trace plus only explicitly documented decision-time analytical signals that existed before X_W was introduced. This is a baseline proposal, not yet a preregistered baseline.

## Verdict
A.3: CONDITIONAL PASS FOR CONSTRUCT SURVIVAL; FREEZE BLOCKED.

The witness dimensions survive the current hidden-SQL and simple redundancy attacks, but the codebook cannot honestly be frozen for confirmatory use until W1-W7 are tightened with adversarial examples, the P2-C1.2 baseline is explicitly frozen independently of X_W, and the literature collision search is refreshed against the final wording.

No predictive-validity claim is made by this gate.