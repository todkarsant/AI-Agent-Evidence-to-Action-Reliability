# C.4.2.4 Evidence-Obligation Annotation Codebook v1

**Status:** FROZEN FOR PILOT ANNOTATION  
**Freeze date:** 2026-09-18  
**Purpose:** measure decision-time evidence sufficiency independently of generated SQL correctness and downstream intervention outcome.

## Construct

For case (i), let (Q_i) be the natural-language analytical request, (S_i) the supplied database schema, and (R_i) the execution evidence visible at decision time.

Define an obligation set:

[
G_i = {g_{i1},ldots,g_{iK_i}}
]

and an obligation-level judgment:

[
v(g_{ij},R_i,S_i)in{0,1}.
]

The candidate aggregate is:

[
X_{E,i} = rac{1}{K_i}sum_j v(g_{ij},R_i,S_i).
]

If execution fails and no result evidence exists, the case is recorded as **NO_USABLE_EVIDENCE** rather than assigning a substantive 0 to individual analytical obligations. This preserves a distinction between absent evidence and evidence that fails an obligation.

## Information permitted to annotators

Annotators may see:

- case identifier;
- natural-language question;
- database schema;
- decision-time execution result: column names and returned rows, including an explicitly empty result;
- execution-status indicator only insofar as needed to distinguish a failed execution from an empty result.

Annotators must not see:

- gold SQL;
- gold answer;
- generated SQL;
- P0 correctness;
- challenger SQL;
- replacement/intervention decision;
- downstream outcome;
- post-hoc evaluator labels;
- any feature derived from those variables.

## Obligation classes

Annotators first identify obligations explicitly entailed by the question. Only obligations relevant to the requested analytical result are scored.

### O1 Selection / filtering
Whether the evidence demonstrates the requested restriction on entities/records or predicates.

Examples: male students; price > threshold; year after a cutoff; trips in a qualifying ZIP area.

### O2 Projection / requested attributes
Whether the evidence contains the requested output attributes at an interpretable granularity.

Examples: requested ID + first name + last name; apartment number + start date + end date.

### O3 Aggregation
Whether the evidence supports the requested aggregate operation.

Examples: count, average, sum, maximum, minimum.

A scalar aggregate result can satisfy an aggregation obligation when its meaning is directly interpretable from the schema and question.

### O4 Grouping / per-group structure
Whether the evidence preserves the grouping structure required by the question.

Example: a result that must provide a value for each group rather than one global aggregate.

### O5 Ordering / top-k
Whether the evidence supports a requested ordering or top/bottom-k relationship.

Example: “most”, “least”, “top 3”, “highest”.

### O6 Extremum
Whether the evidence supports a requested maximum/minimum/extreme-value relationship rather than merely returning multiple candidate rows.

### O7 Cardinality / completeness
Whether the evidence supports the requested scope or number of returned entities.

Examples: “all”, “exactly 3”, “how many”.

This obligation is scored only when the question explicitly requires a cardinality/completeness claim that can be assessed from the evidence.

### O8 Join / entity linkage
Whether the evidence preserves the requested relationship across entities/tables.

Example: identifying faculty members associated with activities; linking an engineer to visits and personal attributes.

## Scoring rule

For each identified obligation:

**1 — Supported:** The displayed evidence is sufficient, by itself and using only the supplied schema, to substantiate the obligation.

**0 — Not supported:** The evidence is present but does not substantiate the obligation.

**NO_USABLE_EVIDENCE:** Execution failed or no interpretable result evidence exists. Do not convert this state into an obligation-level 0.

## Critical anti-leakage rule

Annotators must judge evidence sufficiency, **not whether the generated query was correct**.

Do not reconstruct missing predicates, joins, grouping, ordering, or semantics from knowledge of what SQL the system might have generated.

## Ambiguity rule

If the evidence could support an obligation under multiple materially different interpretations, mark **0** and record the ambiguity reason. Do not resolve ambiguity using gold SQL or external assumptions.

## Empty-result rule

An empty result is valid evidence and must be judged as such. Do not automatically classify an empty result as insufficient.

For example, a question asking for records satisfying a condition can be substantively supported by an empty result if the evidence structure is otherwise sufficient to substantiate that no qualifying records were returned. The annotator must not infer correctness of the underlying query.

## Adjudication

Each case is independently annotated by two outcome-blinded raters.

A disagreement is retained as a disagreement for primary reliability analysis. Adjudication, if performed, is a separate secondary artifact and must not overwrite the original ratings.

## Reliability analysis

Primary agreement is assessed at the obligation level, not only the case-level aggregate.

Report:

1. raw percent agreement;
2. Cohen's (kappa);
3. Gwet's AC1 as a sensitivity analysis;
4. obligation-level contingency tables;
5. aggregate-score agreement descriptively.

No threshold is declared in this codebook as an automatic success criterion. Reliability adequacy must be interpreted with the observed prevalence, obligation mix, sample size, and confidence intervals.

## Freeze boundary

This codebook must not be modified after outcome-bearing annotation begins. Any later revision creates a new version and a new measurement cohort.

**Important limitation:** this codebook is a candidate measurement instrument. The pilot annotation is intended to falsify it, not to establish that it is valid merely because raters agree.
