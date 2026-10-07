# Does Decision-Time Evidence Predict Harmful Answer Replacement by an Analytical Agent? A Prospective, Outcome-Blinded Incremental-Validity Study

**Manuscript status:** submission draft, journal-agnostic. The methods are final. Results marked `[[R: …]]` are filled mechanically from `P2_C1_4_FINDINGS.json` / `.md`, which the frozen pipeline produces after annotation. No value in brackets has been observed.

**Authors:** [[AUTHOR LIST AND AFFILIATIONS — to confirm]]
**Corresponding author:** [[name, email — to confirm]]
**Word count (main text, excluding tables and references):** [[to compute at freeze]]

---

## Abstract

**Background.** Analytical agents increasingly propose changes to answers that are already in place. When an agent replaces a correct incumbent answer with an incorrect one, the replacement causes harm even if the system was "trying to help". It is not known whether the evidence visible at the moment of decision carries information about when such replacements are harmful, beyond simple execution signals.

**Methods.** We ran a prospective study with a frozen protocol on a fixed agent pathway: a pinned 1-billion-parameter language model performing Text-to-SQL on the Spider benchmark, with an incumbent-preserving replacement step. The study had five parts.

- **Cohort.** Every unique (database, question) pair in the Spider training-side sources, after excluding a pilot, was run once: 8,638 decisions. Decision-time evidence was hash-locked before any outcome was evaluated.
- **Outcome.** Harmful replacement (Y_H): the incumbent answer was correct, a replacement occurred, and the final answer was incorrect.
- **Predictor.** Two independent human raters, blinded to outcomes, scored an evidence-witness index (X_W) from the preserved evidence. X_W covers seven analytical obligations: selection, projection, aggregation, grouping, ordering, extremum and join/linkage.
- **Analysis.** We compared L2-penalised logistic regression on a frozen execution baseline (M0) with the same model plus X_W (M1). Comparison used repeated nested group-stratified cross-validation, with the paired out-of-sample log-loss difference as the primary estimand.
- **Annotation scope.** A blinded, run-once feasibility check governed how many decisions were annotated.

**Results.** 41.6% of decisions (3,590/8,638) produced no executable evidence and were outside the primary population by protocol. These decisions were concentrated in harder queries. Of the 5,044 eligible primary decisions, 1,705 were randomly sampled for double annotation. [[R: inter-rater agreement summary]]. The primary population comprised [[R: n]] decisions with [[R: events]] harmful replacements. Δlog-loss (M0 − M1) was [[R: Δ]] (95% repeat interval [[R: interval]]); [[R: robustness flag and one-sentence sensitivity summary]].

**Conclusions.** [[To be written after results; see §5 for the prespecified interpretation of each possible outcome.]]

**Keywords:** analytical agents; incumbent replacement; decision-time evidence; incremental predictive validity; Text-to-SQL; inter-rater reliability; prospective protocol

---

## 1. Introduction

As more capable models are deployed where outputs carry consequences, the central design question is no longer only whether a system can produce a better answer. It is also whether the system should be authorised to act on that answer.

One response is to separate what a model may *propose* from what it is *authorised to do*:

- the model reasons and proposes;
- authorisation is a separate, auditable decision;
- only approved steps are executed.

This separation is a design position that motivates the work. It is not a finding of this study. This study examines one measurable part of the authorisation step.

**The replacement setting.** Consider an analytical agent that has already produced an answer, the *incumbent*, and that may replace it with a revised answer. Replacement is itself a consequential decision. Replacing a correct incumbent with an incorrect answer is a harm that would not have occurred without the intervention.

Discovery work that preceded this study used the same Spider workload and the same intervention code base. In its development record, an incumbent-preserving intervention mechanism produced 21 harmful replacements against 2 rescues among 330 intervention-eligible cases. We treat that observation as motivation only, not as evidence for the present predictor (§3.11).

**Research question.** If replacement can harm, an authorisation policy needs signals that indicate *when* it is likely to harm. The most available signal is the evidence visible at decision time: the question, the schema, and the rows and columns the incumbent query returned. We ask:

> Does an independently measured, decision-time evidence-witness index (X_W) improve out-of-sample prediction of harmful incumbent replacement beyond a frozen baseline of execution signals?

**Scope of the claim.** The claim is restricted to incremental predictive validity in the newly collected evaluation population under the frozen protocol. No claim of causal protection, universal reliability or deployment safety is made.

**Contributions.** The study contributes:

1. a frozen, observable evidence-witness construct with a codebook that excludes hidden-SQL and outcome information;
2. a prospectively collected, hash-locked cohort in which predictor, baseline and outcome are measured on the same decision unit;
3. a confirmatory test of incremental predictive validity with a pre-specified estimand and stopping rules;
4. a documented account of design failures that make such claims non-identifiable after the fact: a historical alignment failure and an invalid first annotation attempt.

## 2. Related work

**Agent reliability.** Recent work treats agent reliability as multidimensional. Rabanser et al. (2026) separate consistency, robustness, predictability and safety. Gupta (2026) stresses agents under production-like faults and perturbations. Raj et al. (2026) formalise consistency as a statistically testable property. de Zarzà et al. (2026) study semantic invariance under meaning-preserving transformations. These works establish that single-run success is an insufficient reliability measure. We do not claim novelty for perturbation robustness or consistency.

**Evidence sufficiency and grounding.** A separate line asks whether the available evidence suffices for an answer:

- set-level sufficiency verification for selective retrieval-augmented generation (Qiu et al., 2026);
- sufficiency benchmarks for abstention calibration (Zhang & Wu, 2026);
- learned sufficiency boundaries for multi-hop question answering (Sato et al., 2026).

These works concern whether a model should *answer*. Our question is whether evidence predicts the harm of *replacing* an existing answer, and our construct records only *observable witnesses* to analytical obligations, not sufficiency in general.

**Authorisation, provenance and evidence-gated action.** Closest in spirit are studies that separate the induction of an action from its authorisation:

- Guo et al. (2026) separate action induction from runtime authorisation in tool-augmented agents;
- Liao (2026) audits how agent action selection responds to source provenance;
- Zheng et al. (2026) gate remediation on verified evidence;
- Wu and Gong (2026) show policy violations that arise when the facts needed for judgment are invisible at decision time;
- Theodorakopoulos and Theodoropoulou (2026) review auditable decision traces for operational LLM autonomy.

Related measurement concerns include:

- Tang et al. (2026), who show that harmless outcomes can reflect incapability rather than safe judgment, a distinction that parallels our separation of outcome class from mechanism;
- Uluırmak and Kurban (2026), who survey divergences between evaluation proxies and safety targets;
- Adeli (2026), who treats verification as a resource-constrained decision.

None of these, to our knowledge, tests whether a human-measured decision-time evidence index adds *predictive* information about harmful replacement beyond execution signals, under a prospective protocol. This positioning is bounded by the literature reviewed up to [[date of final literature search]]. It will be re-checked immediately before submission because the field is moving quickly.

**Prediction-model methodology.** Our design follows established guidance for developing and validating prediction models. The guidance we draw on covers:

- sample size by the criteria of Riley et al. (2019, 2020);
- proper scoring rules (Gneiting & Raftery, 2007);
- tuning inside nested cross-validation to avoid optimistic error estimates (Varma & Simon, 2006);
- calibration reporting (Van Calster et al., 2019);
- the TRIPOD+AI reporting items (Collins et al., 2024), which we follow where they apply outside the clinical setting.

Agreement is reported with Cohen's κ (Cohen, 1960), with Gwet's AC1 (Gwet, 2008) as a sensitivity statistic under skewed marginals.

## 3. Methods

### 3.1 Agent pathway and setting

Every decision was produced by one pinned pathway:

- **Workload:** Text-to-SQL on Spider 1.0 (Yu et al., 2018).
- **Model:** Llama 3.2 1B (Meta, 2024), served locally through Ollama 0.33.3.
- **Code:** a pinned commit of the discovery code base.

For each question, the agent first produces an incumbent query and answer (P0). The intervention pathway (P6-IP) may then propose a challenger and decide whether to replace the incumbent. Correctness is judged by execution against the official Spider evaluator at a pinned version.

Two bounded runtime amendments are part of the frozen pathway and were adopted before cohort acceptance:

- a detector-gated recovery from runaway self-repeating SQL generation, which fired in 227 decisions (2.6%);
- replacement of one escalation-prompt sentence that reproducibly triggered runaway generation in the pinned runtime.

Both are disclosed in Supplementary Table S2.

### 3.2 Unit, outcome and cohort

**Unit.** The prediction unit is one immutable decision: one (database, question) pair executed once.

**Outcome.** $Y_H = \mathbb{1}[\text{P0 correct} \wedge \text{replacement occurred} \wedge \text{final answer incorrect}]$.

**Source frame.** The frame was every unique (database, question) pair in Spider's `train_spider.json` and `train_others.json`, after excluding the 12-case measurement pilot. This gave 8,638 decisions in a frozen, hash-ordered manifest of 44 shards. No outcome, annotation or correctness information was used to select decisions.

**Acquisition and lock.** The accepted cohort comes from one complete 44-shard run. An earlier engineering attempt was discarded after only its error logs were read (§3.11). Records were accepted only if all of the following held:

- exact reconciliation with the frozen manifest;
- unique decision identifiers;
- evidence captured before intervention;
- valid evidence hashes;
- a forensic lock audit passed.

The consolidated cohort file has SHA-256 `da537c75…9ebd9b8b`.

**Record statuses.** Every decision carries exactly one mechanical record status:

- **E1:** the reference SQL is not scoreable by the official evaluator, found by a census before acquisition. The model is never called.
- **E2:** a runtime failure before decision-time evidence was complete.
- **E3/E4:** a runtime failure after evidence capture.
- **EVALUABLE:** the pathway completed.

No outcome is synthesised for non-evaluable decisions.

### 3.3 Baseline B

The frozen baseline contains three execution signals of the incumbent query:

- `execution_ok`;
- $\log(1+\text{row\_count})$;
- $\log(1+\text{column\_count})$.

The two count features are standardised within each training fold.

**Reported feature (not a change).** Among decisions with usable evidence, `execution_ok` is 1 in all 5,044 cases, by construction (§3.4). In the primary analysis B is therefore effectively the two count features. The frozen model retains the constant column, and under L2 penalisation it receives a zero coefficient. Synthetic tests confirmed the analysis runs unchanged in this configuration.

### 3.4 Evidence-witness index X_W

**Decision-time evidence.** For each decision the preserved evidence is:

- the question;
- the database identifier and schema;
- the column names and rows returned by the incumbent query;
- the row and column counts.

**Exclusions from evidence.** The evidence contains no generated or reference SQL, no correctness label and no outcome. A decision whose incumbent query produced no executable result has `NO_USABLE_EVIDENCE` and missing X_W, never zero. In this cohort `NO_USABLE_EVIDENCE` coincides exactly with `execution_ok` = 0.

**Construct.** Raters judge seven dimensions:

- W1 selection;
- W2 projection;
- W3 aggregation;
- W4 grouping;
- W5 ordering;
- W6 extremum;
- W7 join/linkage.

For each dimension, raters first judge *applicability* from the natural-language question: YES, NO, or UNCLEAR when the wording itself admits both readings. For applicable dimensions they then judge whether an observable *witness* is PRESENT in the returned evidence, or ABSENT/AMBIGUOUS.

With $A$ the set of applicable dimensions and $w_j \in \{0,1\}$ the witness indicator,

$$X_W = \frac{1}{|A|}\sum_{j \in A} w_j .$$

Dimensions not entailed by the question are excluded from the denominator.

**What X_W does not measure.** The construct deliberately does not measure hidden predicate correctness, completeness or SQL semantics. Those cannot be established from visible output.

**Codebook and combination rule.** The codebook (v2) and an operational rule for UNCLEAR were frozen before any confirmatory annotation. The combined predictor is the mean of the two raters' X_W, as specified in the implementation amendment of 2026-10-02.

### 3.5 Annotation

**Raters.** Two independent raters annotated with an offline tool. Each rater received only their own packet, containing the same decisions in a different random order.

**Blinding.** Packets were generated by an explicit field allowlist and contained no outcome, correctness, intervention state or SQL. Raters attested to independence in the tool. Raw labels were hash-locked before X_W was constructed. Reliability is reported descriptively, and no coefficient threshold constitutes a pass.

**Annotation scope (amendment, 2026-10-07).** The frozen protocol originally required double annotation of every decision with usable evidence, about 8,600 cases per rater. This was judged infeasible. It was replaced by two steps, specified and frozen before execution (§3.9):

1. a blinded, run-once feasibility check;
2. a simple random subsample.

### 3.6 Populations

**Primary population.** EVALUABLE decisions that have usable evidence, a defined combined X_W and an observed Y_H.

**Sensitivity analyses.** These are pre-specified (missingness amendment, 2026-10-01):

- **S1** adds post-evidence failures in which P0 was incorrect. For these, $Y_H = 0$ follows from the definition.
- **S2** adds post-evidence failures with P0 correct, at $Y_H = 0$ (S2-low) and $Y_H = 1$ (S2-high).

The result is called *robust* only if the sign of Δlog-loss agrees across the primary, S1, S2-low and S2-high analyses.

### 3.7 Models and evaluation

**Models.** Both models are L2-penalised logistic regressions with an unpenalised intercept:

- **M0:** baseline B;
- **M1:** B plus X_W.

There are no interactions, class weighting, resampling or feature selection.

**Evaluation.** Evaluation used nested, group-stratified cross-validation with groups = (database, question):

- 5 outer folds × 20 repeats, seeds 20261001–20261020;
- the penalty $C \in \{0.01, 0.1, 1, 10, 100\}$ tuned by 5-fold inner cross-validation on the training portion only, choosing the smaller $C$ on ties;
- identical outer partitions for M0 and M1.

**Primary estimand.**

$$\Delta_{\text{logloss}} = \operatorname{mean}_i\big[\ell(Y_{H,i}, p_{0,i}) - \ell(Y_{H,i}, p_{1,i})\big],$$

with $\ell$ the log loss. Positive values favour M1.

**Uncertainty.** Uncertainty is the 2.5th–97.5th percentile of the 20 repeat-level estimates. This describes instability across resampling, not a population confidence interval. No significance threshold is pre-specified, and none is applied.

**Secondary measures.** Reported for both models:

- Brier score;
- AUROC;
- AUPRC;
- calibration intercept and slope, with a sparse-event caveat;
- the distribution of predicted probabilities.

### 3.8 Missingness audit

E2 and E3/E4 decisions are compared with EVALUABLE decisions on characteristics fixed before any outcome:

- database;
- question length;
- reference-SQL hardness by the official Spider categorisation;
- nesting depth of the reference SQL.

Hardness and nesting depth were computed by a separate, outcome-blind script before annotation. The comparison is descriptive.

### 3.9 Sample size and feasibility

**Sample-size criteria.** Sample size was assessed with criteria (i) and (iii) of Riley et al. (2020) at frozen planning values:

- 4 parameters;
- target shrinkage 0.90;
- anticipated $R^2_{CS}$ equal to 15% of its maximum;
- an intercept margin of error of 0.05.

A shortfall on either criterion is a *hard stop*. No model is fitted, and only descriptive results are reported.

**Blinded feasibility check.** Before annotation, this check was applied once to the full eligible primary population: EVALUABLE decisions with usable evidence and Y_H defined. Only the pooled event count entered the calculation, and it was never displayed.

**Subsample size.** Because the criteria were met, the subsample size was

$$n_{\text{sub}} = \min\!\big(N,\ \max(\lceil 1.5\, n_{\text{Riley}} \rceil,\ \lceil 50/\hat\phi \rceil)\big),$$

where:

- $N$ is the eligible population size;
- $n_{\text{Riley}}$ is the larger of the two criterion minima;
- $\hat\phi$ is the pooled event rate.

The subsample was drawn by simple random sampling with seed 20261007. All post-evidence-failure decisions with usable evidence were added for S1/S2.

**Decisions not sampled.** These have X_W missing completely at random by design (Rubin, 1976). The hard stop is applied again to the realised primary population.

### 3.10 Software and reproducibility

**Software.** The analysis runs with Python 3.11, scikit-learn 1.8.0 (Pedregosa et al., 2011), NumPy 2.4.4, SciPy 1.17.1 and statsmodels 0.15.0, in a pinned CI environment.

**Single-run pipeline.** The gate that runs the analysis executes once, refusing to run again if a results artifact exists. It has three stages:

1. **Stage 1, outcome-blind:** validates the exports, locks the raw labels and builds X_W.
2. **Stage 2:** reads the locked cohort and runs the frozen analysis.
3. **Report:** renders the results report after checking the hash chain.

**Testing.** All code was tested on synthetic data before any real annotation existed. This included a test that the subsample selection is invariant to the outcome assignment.

### 3.11 Protocol registration, amendments and discovery data

**Registration.** The confirmatory statistical and collection protocol was frozen in a version-controlled repository on 2026-09-21, before confirmatory outcome collection. It was **not** registered with an external registry such as OSF. The commit history provides the timestamped record.

**Amendments.** Three statistically relevant amendments were adopted after the freeze. Each was made before any outcome was inspected and is reported in full in Supplementary Table S2:

1. **Missingness and eligibility (2026-10-01).** Adopted after a failed engineering acquisition run of which only error logs were read. It defined record statuses and the S1/S2 analyses.
2. **X_W construction and analysis implementation (2026-10-02).** It fixed the rater-combination rule, the Riley hard stop and the outcome-blind missingness audit.
3. **Blinded feasibility and annotation subsample (2026-10-07).** The outcome *rate*, but not any association with it, informed the annotation sample size through a pre-specified rule run once. The subsample size therefore reveals the rate approximately. The inflation factor, the minimum of 50 expected events and the seed were set by the implementer before execution.

Runtime amendments that affected only acquisition mechanics are listed separately.

**Discovery data.** The discovery data were not used confirmatorily. The historical traces did not preserve the decision-time evidence needed to construct X_W, so historical outcomes were never joined to the new cohort (§5.2).

## 4. Results

### 4.1 Cohort flow

Of 8,638 frozen decisions:

| Status | n |
|---|---|
| E1 (reference SQL not scoreable) | 3 |
| E2 (runtime failure before evidence) | 23 |
| E3/E4 (runtime failure after evidence) | 8 |
| EVALUABLE | 8,604 |

Runtime failures (E2 + E3/E4) affected 31 decisions (0.36%), within the frozen ceiling of 431.

- Among EVALUABLE decisions, 5,044 had usable evidence and 3,560 had `NO_USABLE_EVIDENCE`.
- The 5,044 decisions with usable evidence formed the eligible primary population.
- Of these, 1,705 were randomly sampled for annotation.
- 4 post-evidence-failure decisions with usable evidence were added for S1/S2.
- Each rater therefore annotated 1,709 decisions.
- [[R: n sampled with undefined combined X_W]] sampled decisions had an undefined combined X_W.
- The primary population comprised [[R: n]] decisions in [[R: groups]] (database, question) groups.

Figure 1 shows the full flow.

### 4.2 Evidence availability

`NO_USABLE_EVIDENCE` occurred in 3,590 of 8,638 decisions (41.6%). This was computed outcome-blind from the blinded packets and is a descriptive analysis that was not pre-specified.

**These decisions are not a random subset (Table 1).** Compared with decisions with usable evidence:

- their reference queries were more often "extra hard" (30.2% vs 13.2%) and less often "easy" (12.6% vs 30.2%);
- their questions were longer (median 69 vs 61 characters);
- the rate ranged from 11.8% to 72.0% across 146 databases (median 38.1%).

**Table 1.** Reference-SQL hardness by evidence availability. Spider categories; proportions within column.

| Hardness | Usable evidence (n = 5,048) | No usable evidence (n = 3,589) |
|---|---|---|
| easy | 30.2% | 12.6% |
| medium | 36.7% | 31.8% |
| hard | 19.9% | 25.4% |
| extra | 13.2% | 30.2% |

*One decision has no hardness value because its reference SQL could not be parsed.*

**Excluding these decisions removes no possible harms.** Because P0 cannot be scored correct when its query produced no executable result, these decisions cannot be harmful replacements by the outcome definition. The primary population therefore contains every decision at which a harmful replacement was possible. This follows from the definitions; it will be confirmed mechanically on the locked outcomes: [[R: Y_H count among NO_USABLE_EVIDENCE EVALUABLE decisions; expected 0]].

### 4.3 Annotation reliability

[[R: Table 2 — applicability agreement, Cohen's κ and Gwet's AC1 with 95% case-bootstrap intervals for W1–W7; witness agreement where both raters judged a dimension applicable; UNCLEAR counts; between-rater X_W correlation and mean absolute difference.]]

### 4.4 Outcome prevalence and feasibility

[[R: events, prevalence; Riley criterion minima and verdict on the realised primary population; primary verdict ANALYSIS_COMPLETED or FEASIBILITY_STOP_RILEY.]]

### 4.5 Primary estimand

[[R: Δlog-loss (M0 − M1), 95% repeat interval, number of outer predictions, convergence warnings.]]

### 4.6 Secondary measures

[[R: Table 3 — log loss, Brier, AUROC, AUPRC, calibration intercept and slope for M0 and M1.]]

### 4.7 Sensitivity and missingness

[[R: Table 4 — Δlog-loss and interval for primary, S1, S2-low and S2-high; robustness flag. Missingness audit, Supplementary Table S3.]]

## 5. Discussion

### 5.1 Principal finding

[[To be written from §4. The interpretation of each possible result was fixed before results were seen, and is set out below.]]

The possible results, and how each will be read:

- **Δ > 0 with the repeat interval above 0, and robust.** Observable decision-time evidence carries information about harmful replacement beyond execution signals in this population. It is then a candidate input to an authorisation policy. This is a statement about prediction, not about the effect of using X_W to gate replacements.
- **Interval includes 0, or the result is not robust.** No incremental predictive value is shown under this protocol. This is not evidence of no effect. The precision is limited by the annotated subsample, and the result does not generalise beyond this pathway.
- **Δ < 0.** Adding X_W worsened out-of-sample prediction. This is consistent with no signal plus the cost of an extra parameter.
- **Feasibility stop.** Too few harmful replacements occurred in the realised population for a stable model at the frozen planning values. Only descriptive results are reported. This is itself a finding about the rarity of the event.

### 5.2 What holds regardless of the primary result

1. **The at-risk population is shaped by capability.** Four in ten decisions never reach a state in which replacement can harm, and these are disproportionately the harder questions. A risk signal for replacement therefore operates on a population already filtered by the agent's ability to execute. Evaluations of replacement policies should report this denominator.
2. **Predictive claims about agent decisions can become non-identifiable after the fact.** The discovery traces recorded outcomes but not the decision-time evidence needed to measure the predictor on the same units. No retrospective analysis could repair this. Preserving evidence before the outcome is evaluated is a precondition for this kind of study, not an implementation detail.
3. **Perfect agreement is not evidence of a valid measurement.** A first annotation attempt produced complete agreement, but used a simplified worksheet that did not reproduce the frozen evidence and that imposed labels the codebook did not allow. It was rejected and preserved as invalid (Supplementary Note S1). The instrument is part of the measurement.

### 5.3 Relation to prior work

[[To be written after results, against the works in §2. Position relative to evidence-sufficiency work (answer/abstain) and to authorisation/provenance work (gating).]]

## 6. Limitations

- **Single pathway.** One small model, one runtime, one benchmark and one intervention mechanism. Results may not transfer to larger models, other agents or production data.
- **Evidence representation.** X_W scores only observable witnesses in returned rows and columns. It cannot detect wrong predicates or incomplete results that look plausible.
- **Annotated subsample.** Annotating a random subsample reduces precision relative to full-cohort annotation. The outcome rate informed the subsample size (§3.11).
- **Selection by evidence availability.** The primary population over-represents easier questions (§4.2). The conclusions apply to decisions in which the incumbent query executed.
- **Dependence.** Each (database, question) pair occurs once, but questions share databases. Grouping protects against leakage between identical cases, not against database-level similarity.
- **Uncertainty summary.** The repeat-level interval reflects resampling instability, not sampling from a population. No significance test is pre-specified.
- **No external registration.** The protocol and its amendments are timestamped in version control rather than an external registry.
- **Post-freeze amendments.** Three amendments were made after the protocol freeze, all before any outcome was inspected (§3.11).
- **Sparse-event calibration.** Calibration estimates may be unstable if events are few.

## 7. Conclusion

[[To be written after results. Two to three sentences: the answer to the research question, its scope, and the methodological implication in §5.2.]]

---

## Declarations

**Data availability.** The study materials are available at [[repository URL]] and archived at [[Zenodo DOI — to create at submission]]. They comprise:

- the frozen protocol and amendments;
- the codebook and rater instructions;
- the blinded annotation packets;
- the locked cohort, including outcomes [[confirm that the full cohort will be released]];
- the raw rater exports;
- all code, tests and run records.

The Spider benchmark is publicly available from its authors under its own licence.

**Code availability.** All analysis and acquisition code is in the same repository, under the licence [[to choose: e.g., MIT or Apache-2.0 for code, CC BY 4.0 for data and text]].

**Ethics.** The two raters annotated benchmark questions and machine outputs. No personal data about the raters was collected beyond their names and independence attestations. [[Confirm with the target journal whether this requires an ethics statement or exemption, and whether raters' consent to be named is needed.]]

**Acknowledgements.** [[Raters, if they agree to be named and are not authors; collaborators.]]

**Author contributions.** [[CRediT roles — to confirm.]]

**Funding.** [[None / to confirm.]]

**Competing interests.** [[None / to confirm.]]

**Use of AI tools.** [[Author to complete according to the target journal's policy.]]

**Model licence notice.** Llama 3.2 is licensed under the Llama 3.2 Community License. Built with Llama.

---

## Figures and tables

- **Figure 1.** Cohort flow: frozen decisions → record status → evidence availability → eligible → sampled → annotated → primary population. [[to draw from §4.1 and the findings report]]
- **Figure 2.** Δlog-loss with repeat intervals across the primary, S1, S2-low and S2-high analyses. [[after results]]
- **Table 1.** Reference-SQL hardness by evidence availability (§4.2).
- **Table 2.** Inter-rater reliability. [[after results]]
- **Table 3.** Secondary performance measures. [[after results]]
- **Table 4.** Sensitivity analyses. [[after results]]

---

## References

Adeli, S. (2026). *Strategic verification for long-running LLM agents* [Preprint]. Preprints.org. https://doi.org/10.20944/preprints202608.2057.v1

Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement, 20*(1), 37–46. https://doi.org/10.1177/001316446002000104

Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L., Van Calster, B., Ghassemi, M., Liu, X., Reitsma, J. B., van Smeden, M., Boulesteix, A.-L., Camaradou, J. C., Celi, L. A., Denaxas, S., Denniston, A. K., Glocker, B., Golub, R. M., Harvey, H., Heinze, G., … Logullo, P. (2024). TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ, 385*, e078378. https://doi.org/10.1136/bmj-2023-078378

de Zarzà, I., de Curtò, J., Cabot, J., Manzoni, P., & Calafate, C. T. (2026). *Semantic invariance in agentic AI* (arXiv:2603.13173) [Preprint]. arXiv. https://arxiv.org/abs/2603.13173

Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*. https://doi.org/10.1198/016214506000001437 [[volume, issue and pages to confirm from the publisher page]]

Guo, X., Xu, Z., Huo, D., Zhang, Y., Wang, W., Yang, Q., Yu, D., & Wang, Y. (2026). *When tool outputs become commands: Separating action induction from runtime authorization in tool-augmented LLM agents* (arXiv:2608.27146) [Preprint]. arXiv. https://arxiv.org/abs/2608.27146

Gupta, A. (2026). *ReliabilityBench: Evaluating LLM agent reliability under production-like stress conditions* (arXiv:2601.06112) [Preprint]. arXiv. https://arxiv.org/abs/2601.06112

Gwet, K. L. (2008). Computing inter-rater reliability and its variance in the presence of high agreement. *British Journal of Mathematical and Statistical Psychology, 61*, 29–48. https://doi.org/10.1348/000711006X126600

Liao, J. (2026). *Auditing provenance sensitivity in LLM agent action selection* (arXiv:2607.20827) [Preprint]. arXiv. https://arxiv.org/abs/2607.20827

Meta. (2024). *Llama-3.2-1B* [Large language model]. Hugging Face. https://huggingface.co/meta-llama/Llama-3.2-1B

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html

Qiu, J., Han, Z., & Huang, C. (2026). *SURE-RAG: Sufficiency and uncertainty-aware evidence verification for selective retrieval-augmented generation* (arXiv:2605.03534) [Preprint]. arXiv. https://arxiv.org/abs/2605.03534

Rabanser, S., Kapoor, S., Kirgis, P., Liu, K., Utpala, S., & Narayanan, A. (2026). *Towards a science of AI agent reliability* (arXiv:2602.16666) [Preprint; accepted at ICML 2026]. arXiv. https://arxiv.org/abs/2602.16666

Raj, H., Orkat, N., Mukherjee, S., Guha, A., Flynn, C., & Majumdar, S. (2026). *Consistency as a testable property: Statistical methods to evaluate AI agent reliability* (arXiv:2605.10516) [Preprint]. arXiv. https://arxiv.org/abs/2605.10516

Riley, R. D., Ensor, J., Snell, K. I. E., Harrell, F. E., Jr., Martin, G. P., Reitsma, J. B., Moons, K. G. M., Collins, G., & van Smeden, M. (2020). Calculating the sample size required for developing a clinical prediction model. *BMJ, 368*, m441. https://doi.org/10.1136/bmj.m441

Riley, R. D., Snell, K. I. E., Ensor, J., Burke, D. L., Harrell, F. E., Jr., Moons, K. G. M., & Collins, G. S. (2019). Minimum sample size for developing a multivariable prediction model: Part II—Binary and time-to-event outcomes. *Statistics in Medicine, 38*(7), 1276–1296. https://doi.org/10.1002/sim.7992

Rubin, D. B. (1976). Inference and missing data. *Biometrika, 63*(3), 581–592. https://doi.org/10.1093/biomet/63.3.581

Sato, H., Tanaka, Y., Nakamura, R., Kobayashi, A., & Ito, M. (2026). *Learning evidence sufficiency boundaries for selective answering in grounded multi-hop QA* (arXiv:2609.01687) [Preprint]. arXiv. https://arxiv.org/abs/2609.01687

Tang, Z., et al. (2026). *Safe, or simply incapable? Rethinking safety evaluation for phone-use agents* (arXiv:2605.07630) [Preprint]. arXiv. https://arxiv.org/abs/2605.07630 [[full author list to confirm from arXiv if the journal style requires it]]

Theodorakopoulos, L., & Theodoropoulou, A. (2026). Auditable LLM autonomy for operational decision-making: Big data evidence and decision traces [Review]. *Computers, Materials & Continua, 88*(2), 10. https://doi.org/10.32604/cmc.2026.082270

Uluırmak, B. A., & Kurban, R. (2026). *EvalSafetyGap: A hybrid survey and conceptual framework for LLM evaluation-safety failures* (arXiv:2606.30219) [Preprint]. arXiv. https://arxiv.org/abs/2606.30219

Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., Steyerberg, E. W., & Topic Group "Evaluating diagnostic tests and prediction models" of the STRATOS initiative. (2019). Calibration: The Achilles heel of predictive analytics. *BMC Medicine, 17*, 230. https://doi.org/10.1186/s12916-019-1466-7

Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics, 7*, 91. https://doi.org/10.1186/1471-2105-7-91

Wu, J., & Gong, M. (2026). *Policy-invisible violations in LLM-based agents* (arXiv:2604.12177) [Preprint]. arXiv. https://arxiv.org/abs/2604.12177

Yu, T., Zhang, R., Yang, K., Yasunaga, M., Wang, D., Li, Z., Ma, J., Li, I., Yao, Q., Roman, S., Zhang, Z., & Radev, D. (2018). Spider: A large-scale human-labeled dataset for complex and cross-domain semantic parsing and text-to-SQL task. In *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing* (pp. 3911–3921). Association for Computational Linguistics. https://doi.org/10.18653/v1/D18-1425

Zhang, H., & Wu, W. (2026). Do LLMs know when evidence is insufficient? An evidence sufficiency benchmark for answer-abstention calibration in retrieval-augmented generation. *Computers, Materials & Continua, 89*(1), 69. https://doi.org/10.32604/cmc.2026.086343

Zheng, Y., Zhou, J., Hu, R., & Fang, R. (2026). *Evidence-verified LLM agents for safe backend incident remediation* [Preprint]. ResearchGate. https://doi.org/10.13140/RG.2.2.24026.91840

*Reference verification:* every entry above was checked against a primary page (publisher, arXiv, DOI registry, ACL Anthology or JMLR) on 2026-10-08. Remaining gaps are marked `[[…]]`. One register entry (an SSRN working paper) could not be verified and is not cited.
