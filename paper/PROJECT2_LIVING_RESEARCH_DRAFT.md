# AI Agent Evidence-to-Action Reliability — Project 2

**Status:** Living manuscript — P2-C1.4 confirmatory protocol frozen; confirmatory cohort/results not yet accepted or analyzed  
**Manuscript branch:** `paper/p2-c1-4-frozen-state-update-2026-09-26`  
**Base manuscript commit:** `4c8496d3991dfb6449c34a5468406fa488ae01e2`  
**Update date:** 2026-09-26

> **Evidence-status rule.** This manuscript distinguishes completed methodological gates, runtime qualification, failed/rejected attempts, frozen protocol elements, and pending confirmatory results. No confirmatory predictive result is reported until the aligned cohort, independent X_W annotation, provenance lock, and prespecified analysis have actually completed.

## Abstract

Consequential analytical agents may produce executable and apparently plausible alternatives to an incumbent answer, yet replacing a correct incumbent can cause harm even when an intervention is triggered by decision-time evidence. Project 2 investigates whether an independently measured, observable representation of decision-time evidence provides incremental predictive information about harmful incumbent replacement beyond prespecified decision-time analytical signals.

The research program was motivated by Project 1 discovery evidence in which an incumbent-preserving analytical intervention mechanism produced substantially more harmful replacements than rescues and increased cost. Project 2 deliberately does not treat that historical result as confirmatory evidence for the present construct. Instead, it develops and attacks a decision-time evidence-witness measurement based on seven analytical-obligation dimensions: selection, projection, aggregation, grouping, ordering, extremum, and join/linkage.

A first human-annotation attempt was mechanically preserved but failed forensic protocol review because the submitted worksheet did not faithfully reproduce the frozen evidence packet and imposed systematic annotation constraints inconsistent with the frozen codebook. Its apparent perfect agreement is therefore treated as non-confirmatory and is not used as evidence that the measurement gate was successfully closed. The measurement protocol was subsequently clarified, including a deterministic pre-outcome rule for implementation-only ambiguity.

A separate predictive-validity attack established that the historical Project 1 outcome records cannot be retrospectively aligned with the independently measured X_W cohort because the required decision-time evidence was not preserved on the same decision units. Historical outcomes are therefore not joined to the new measurement cohort. A new aligned outcome-bearing cohort was designed and the confirmatory statistical and collection protocol was frozen before confirmatory outcome collection.

The frozen confirmatory comparison is M0=f(B) versus M1=f(B,X_W), where B contains three prespecified decision-time analytical signals and X_W is the independently annotated evidence-witness score. The binary outcome is harmful incumbent replacement, Y_H. The primary estimand is the paired difference in out-of-sample log loss under repeated nested group-stratified cross-validation. Confirmatory model fitting and predictive-validity claims remain pending until the new aligned cohort and independent X_W annotation satisfy the frozen integrity gates.

## 1. Introduction

### 1.1 Consequential analytical replacement

The safety relevance of an analytical agent is not exhausted by whether an answer is correct. In a replacement setting, the system must also decide whether to displace an incumbent answer. The resulting decision chain is:

[
	ext{analytical correctness}
ightarrow
	ext{intervention}
ightarrow
	ext{replacement consequence}.
]

Project 1 provided discovery evidence that this additional decision layer can fail. The present study treats that observation as motivation and design context, not as confirmatory evidence for the Project 2 predictor.

### 1.2 Research question

The confirmatory question is:

> **Does adding the independently measured decision-time evidence-witness score X_W improve out-of-sample prediction of harmful incumbent replacement beyond the frozen baseline B?**

The outcome is:

[
Y_H =
I(P0 mathrm{correct}
land replacement occurs
land final answer incorrect).
]

The model comparison is:

[
M_0=f(B)
]

versus

[
M_1=f(B,X_W).
]

The intended claim is restricted to incremental predictive validity in the newly collected evaluation population and protocol. It does not authorize causal-protection, universal-reliability, or deployment-safety claims.

### 1.3 Novelty boundary

The manuscript does not claim novelty for generic context sensitivity, evidence sufficiency, semantic invariance, provenance, grounding, robustness, or agent reliability. Those broad areas are already active research topics.

The narrower research seam is:

> whether an independently measured, decision-time observable witness construct provides incremental predictive information about consequential incumbent-replacement harm beyond prespecified analytical decision signals.

This is a scoped research question rather than a claim that the underlying concepts are globally new. Final novelty positioning must remain bounded by the literature actually reviewed at submission time.

## 2. Project 1 discovery evidence

Project 1 examined an incumbent-preserving intervention mechanism under a Spider Text-to-SQL workload.

The historical development record contained:

- 1,034 benchmark cases;
- 330 intervention-eligible cases;
- 21 harmful replacements;
- 2 rescues;
- a net intervention contribution of (2-21=-19) cases;
- P0 accuracy of 254/1,034;
- P6-IP accuracy of 234/1,034;
- approximately 25.8% higher mean cost for P6-IP on development.

The held-out-schema record contained 91 intervention-eligible cases, 5 harms, and 1 rescue, with approximately 29.2% higher mean cost for P6-IP.

These values are historical Project 1 discovery/mechanism evidence. They do not establish the Project 2 X_W construct, its reliability, or its predictive validity.

In particular, the historical P1/P6 traces did not preserve the decision-time evidence required to independently reconstruct the present X_W measurement. Consequently, historical outcomes are not retrospectively joined to the new X_W cohort.

## 3. Construct development

### 3.1 Rejected result-only evidence construct

The initial evidence-sufficiency concept attempted to judge whether returned results were sufficient for an analytical obligation.

Adversarial analysis rejected a purely result-level interpretation because visible outputs cannot by themselves establish hidden:

- predicate correctness;
- global completeness;
- join correctness;
- aggregate-population correctness;
- SQL semantics.

The current construct therefore measures only observable witnesses.

### 3.2 Frozen witness construct

The frozen witness framework contains seven dimensions:

1. **W1 — Selection witness**
2. **W2 — Projection witness**
3. **W3 — Aggregation witness**
4. **W4 — Grouping witness**
5. **W5 — Ordering witness**
6. **W6 — Extremum witness**
7. **W7 — Join/linkage witness**

For a usable evidence-bearing case:

[
X_W =
rac{sum_{jin A}w_j}{|A|}
]

where (A) is the set of dimensions applicable from the natural-language question and (w_j) indicates whether the corresponding observable witness is present.

Dimensions not entailed by the natural-language question are excluded from the denominator. Genuine natural-language ambiguity follows the frozen operational rule. `NO_USABLE_EVIDENCE` is missing X_W, not zero.

The construct does not claim to measure hidden SQL correctness or global evidence completeness.

### 3.3 Frozen codebook and operational rule

The frozen W1-W7 codebook is:

`research/methodological_gates/C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19.md`

Codebook SHA-1:

`fc33316b172915244e127d050142bb3bac0534b5`.

The later UNCLEAR operational rule was frozen before confirmatory outcome modeling. The chronology is disclosed explicitly: this was a methodological amendment after the initial annotation submission but before outcome-dependent X_W/model analysis. It is not represented as having been prospectively preregistered before that annotation attempt.

The frozen rule distinguishes implementation-only ambiguity from genuine natural-language ambiguity. Hidden/generated implementation uncertainty cannot create applicability uncertainty. Genuine semantic ambiguity is handled conservatively according to the frozen codebook rather than silently converted into a substantive applicability state.

## 4. Measurement qualification and failed annotation attempt

### 4.1 Why the first annotation attempt is not confirmatory

An initial two-rater response set was preserved and mechanically inspected. The submitted labels showed apparent complete agreement. However, forensic review found that the simplified worksheet did not faithfully reproduce the frozen packet.

Verified defects included:

- at least one case being presented with different natural-language content from the frozen packet;
- additional cases being presented as generic database-review prompts rather than their exact frozen questions;
- abbreviated evidence summaries replacing the exact frozen evidence content;
- all W1-W7 dimensions being marked applicable for SUCCESS cases rather than applying the question-specific codebook;
- NO_USABLE_EVIDENCE cases receiving populated UNCLEAR labels despite the frozen stop rule;
- incomplete final independence attestations in the submitted forms.

Because the annotation instrument was not the frozen instrument, the resulting perfect agreement cannot serve as confirmatory reliability evidence.

The raw submissions remain preserved as a failed/invalid annotation attempt. They are not silently corrected into a successful reliability dataset.

### 4.2 Apparent agreement versus confirmatory reliability

The failed submission nevertheless provides a useful forensic distinction: perfect agreement is not sufficient evidence of measurement validity when the raters did not demonstrably annotate the required frozen stimulus under the required protocol.

Accordingly, the manuscript does not report the apparent (kappa=1.00) or Gwet AC1=1.00 values as a successful reliability gate. They are retained only as characteristics of the invalid submission and are excluded from confirmatory claims.

### 4.3 Required confirmatory annotation

For the confirmatory cohort, both independent raters must annotate the same frozen decision-time evidence packet under the frozen W1-W7 codebook.

They must be blinded to:

- Y_H;
- P0 correctness;
- replacement/intervention outcome;
- final correctness;
- generated/reference SQL;
- post-hoc evaluator labels.

Raw annotations must remain separately preserved and hash-locked. Packet-to-decision reconciliation must pass before X_W is used in the confirmatory model.

## 5. Predictive-validity attack

Before confirmatory model fitting, the proposed design was attacked for:

- unit-of-analysis alignment;
- predictor timing;
- outcome leakage;
- missing X_W;
- rare-outcome stability;
- out-of-sample evaluation;
- scoring-rule choice;
- cross-validation optimism;
- dependence structure;
- historical holdout validity;
- baseline contamination;
- sample-size feasibility;
- model complexity.

### 5.1 Decisive historical-alignment failure

The historical P1/P6 outcomes contain aggregated outcome-bearing units, including the 330 development intervention-eligible cases and 91 held-out cases.

The independent X_W measurement cohort is a separate 12-case cohort.

A valid predictive row requires the same decision instance to contain:

[
(B_i,E_i^{decision-time},X_{W,i},Y_{H,i}).
]

The historical traces do not preserve the decision-time evidence needed to construct X_W for those same historical decision instances.

Therefore:

- historical X_W values are not reconstructed;
- the 330 historical development outcomes are not joined to the 12-case X_W cohort;
- the 91-case historical holdout is not treated as external validation of X_W.

This is a scientific data-design failure, not an infrastructure failure.

### 5.2 Sample-size and event-rate attack

The historical 21/330 harm rate, approximately 6.36%, is used only as a planning assumption. It is not treated as the future confirmatory prevalence.

The design rejects arbitrary events-per-variable rules as the sole sample-size justification. The protocol instead specifies a low-dimensional model, shrinkage target, planning prevalence, conservative planning performance assumption, all available eligible source-frame units, and a stop rule if realized event variation is inadequate for stable confirmatory modeling.

If the realized cohort cannot support the prespecified model/resampling design, confirmatory fitting stops rather than changing the protocol after outcome inspection.

### 5.3 Model-family and scoring-rule attack

The design rejects flexible outcome-driven model searches, unrestricted interactions, automated feature selection, and outcome-dependent feature engineering.

The frozen candidate confirmatory family is penalized binary logistic regression with L2 regularization.

The primary comparison is a paired out-of-sample proper scoring-loss difference rather than thresholded accuracy.

## 6. Frozen confirmatory protocol

### 6.1 Protocol status

The confirmatory statistical and collection protocol was frozen on 2026-09-21:

**Protocol ID:** `P2-C1.4-CONFIRMATORY-V1-2026-09-21`

The protocol was frozen before confirmatory outcome collection.

### 6.2 Prediction unit

One prediction unit is one immutable decision instance: one question/database case executed once under the pinned P6-IP decision pathway.

Each accepted record must link by `decision_id` to:

- the question/database identity;
- baseline B;
- exact pre-intervention evidence;
- intervention/replacement state;
- final correctness;
- Y_H;
- independent X_W annotations.

Benchmark case identity is retained as the dependence cluster.

Historical outcomes are never joined to newly collected decision instances.

### 6.3 Confirmatory source population

The confirmatory acquisition frame uses the Spider 1.0 training-side source used by the qualified collector:

- `train_spider.json`;
- `train_others.json`.

The frozen 12-case measurement pilot is excluded.

Selection uses every unique ((db_id, question)) available in the pinned source after pilot exclusion. SHA-256 ordering is used only to produce deterministic manifest ordering.

No outcome, X_W label, P0 correctness, replacement state, or final correctness is used for source selection.

The full eligible frame is collected rather than choosing an arbitrary fixed N.

### 6.4 Baseline B

The frozen baseline contains exactly:

- `execution_ok`;
- `row_count`;
- `column_count`.

For modeling, row_count and column_count are transformed using log1p and standardized within each training fold. `execution_ok` remains binary.

No evidence-derived feature is added after outcome inspection.

### 6.5 X_W

X_W is the frozen W1-W7 witness score described above.

Two independent outcome-blinded raters must annotate the same frozen evidence for every usable evidence-bearing decision instance.

`NO_USABLE_EVIDENCE` remains missing X_W and is never recoded as zero.

### 6.6 Primary analysis population

All eligible source-frame cases remain in the acquisition flow and are reported.

The primary M0-versus-M1 analysis population is restricted to cases for which usable decision-time evidence permits X_W annotation. This restriction is frozen before outcome analysis and is not outcome-dependent.

M0 and M1 are evaluated on the same primary analysis observations.

### 6.7 Model family

Both models use penalized binary logistic regression with L2/ridge regularization:

[
M_0=f(execution_ok,log(1+row_count),log(1+column_count))
]

and

[
M_1=f(execution_ok,log(1+row_count),log(1+column_count),X_W).
]

The intercept is included and not intentionally penalized.

No interactions or nonlinear terms beyond the frozen log1p transformations are introduced. No class weighting, outcome resampling, feature selection, or outcome-driven model-family search is permitted.

Regularization is selected only within training data from:

[
Cin{0.01,0.1,1,10,100}.
]

### 6.8 Out-of-sample evaluation

Primary evaluation uses repeated nested group-stratified cross-validation:

- 5 outer folds;
- 20 repeats;
- 5-fold inner group-stratified tuning;
- repeat seeds 20261001 through 20261020;
- identical outer partitions for M0 and M1;
- dependence groups defined as ((db_id,question));
- all preprocessing and regularization selection confined to training data.

If the realized outcome/group structure makes the frozen resampling design impossible, the confirmatory analysis stops rather than changing the fold structure after seeing outcomes.

### 6.9 Primary estimand

For each outer prediction:

[
d_i =
LogLoss(Y_{H,i},p_{0,i})
-
LogLoss(Y_{H,i},p_{1,i}).
]

The primary incremental-validity estimand is:

[
Delta_{logloss}=
mean(d_i).
]

Positive values indicate lower predictive log loss for M1 under the frozen sign convention.

The primary estimate is based on paired out-of-sample predictions.

No in-sample coefficient, training AUC, thresholded accuracy, or delta-R² is the primary estimand.

### 6.10 Secondary measures

The frozen secondary reporting set contains:

- Brier score;
- AUROC when both classes occur;
- AUPRC when both classes occur;
- calibration intercept and slope, with sparse-event limitations;
- predicted-probability distributions;
- paired per-case log-loss differences.

### 6.11 Uncertainty

The protocol retains all outer predictions and paired losses.

The primary uncertainty summary is the 95% percentile interval over the 20 repeat-level Delta_logloss estimates.

The manuscript will not describe the 20 resampling repeats as 20 independent participants. The repeat-level interval describes resampling instability.

A cluster bootstrap may be used only as a sensitivity analysis and must resample the defined dependence groups and refit the complete nested procedure.

### 6.12 Missingness and stopping

X_W missingness is handled without recoding `NO_USABLE_EVIDENCE` as zero.

Confirmatory analysis stops if, among other failures:

- evidence is captured after intervention;
- evidence mutates after lock;
- outcomes leak into annotation packets;
- decision IDs duplicate;
- decision-to-outcome linkage is unresolved;
- historical outcomes are joined to new decision instances;
- X_W is generated from hidden SQL or outcome information;
- undocumented manual adjudication occurs;
- group identity cannot be preserved;
- runtime nondeterminism prevents identifying decision instances;
- outcome variation is insufficient for the frozen model/resampling design.

No scientific parameter, cohort definition, model family, seed, or exclusion rule may be changed to rescue a failed confirmatory run.

## 7. Runtime and provenance qualification

### 7.1 Non-confirmatory runtime qualification

The aligned collector was tested through non-confirmatory dry runs before fresh confirmatory acquisition.

The successful Runtime3 qualification demonstrated the ability to:

- execute the pinned Project 1 pathway;
- use the pinned Spider evaluator;
- run the pinned Ollama 0.33.3 / `llama3.2:1b` environment;
- capture decision-time evidence before official outcome evaluation;
- serialize aligned evidence/outcome artifacts;
- validate the aligned-record contract and JSON schema;
- preserve the explicit non-confirmatory boundary.

These runtime results establish runtime qualification only. They are not confirmatory outcome results and are not evidence of predictive validity.

### 7.2 Preserved implementation failures

The runtime qualification process identified and corrected several implementation-contract failures before accepting the confirmatory cohort, including:

- explicit separation of confirmatory and non-confirmatory collector modes;
- evidence-hash canonicalization;
- explicit `NO_USABLE_EVIDENCE` semantics;
- alignment between collector provenance and record schema.

The failed attempts remain documented rather than rewritten as successful runs.

### 7.3 Schema-preservation correction

A forensic audit found that an earlier collector version stored `database_id` without the exact database schema in `decision_time_evidence`.

Because W1-W7 annotation requires the visible schema/database context, this was a measurement/provenance blocker.

The collector was corrected to capture:

[
question + database_id + schema + returned_columns + returned_rows + row_count + column_count.
]

The evidence hash was correspondingly expanded to cover the schema and the other canonical evidence fields.

The aligned record contract was advanced from `P2-C1.4-ALIGNED-V1` to `P2-C1.4-ALIGNED-V2`.

This correction occurred before acceptance of a complete confirmatory cohort, before X_W annotation, and without using Y_H or model results.

### 7.4 Runtime3 boundary

Runtime3 is therefore treated as a qualified acquisition environment, not as a scientific finding.

The frozen runtime lineage includes the pinned Project 1 commit, pinned Spider evaluator/archive, Ollama 0.33.3, and `llama3.2:1b`. Exact artifact hashes and runtime manifests are retained in the repository.

## 8. Confirmatory cohort status

### 8.1 Intended acquisition

The frozen source frame yields a target of **8,638 eligible unique records**, deterministically partitioned into **44 non-empty shards** of 200 records except the final shard of 38.

This is the frozen acquisition target generated from the prespecified source frame and selection rule.

### 8.2 Acceptance condition

The 8,638 records are **not treated as scientific results merely because they were specified or targeted**.

Acceptance requires:

1. all expected shards;
2. exact record counts;
3. exact manifest reconciliation;
4. unique decision IDs;
5. evidence-before-intervention;
6. schema-preservation compliance;
7. evidence-hash validation;
8. aligned-record validation;
9. forensic integrity audit;
10. immutable cohort lock.

Only after those conditions pass can the cohort be used for independent X_W annotation and the confirmatory analysis sequence.

### 8.3 Current manuscript boundary

At the time of this manuscript update, no confirmatory M0/M1 predictive result is inserted.

Accordingly, the following remain explicitly pending:

- accepted immutable 8,638-record cohort lock;
- independent blinded X_W annotation of the accepted cohort;
- annotation reliability/provenance lock;
- X_W/Y_H alignment validation;
- confirmatory M0/M1 fitting;
- out-of-sample log-loss comparison;
- secondary performance measures;
- uncertainty analysis;
- falsification/sensitivity analysis;
- final scientific claim lock.

## 9. Results

### 9.1 Completed methodological results

The following methodological states are established:

| Component | Current status |
|---|---|
| W1-W7 witness construct | Frozen |
| Frozen witness codebook | Frozen |
| Historical X_W/Y_H reconstruction | Rejected |
| Historical outcomes joined to new X_W cohort | Not performed |
| Predictive-validity attack | Completed |
| Sample-size/event-rate attack | Completed |
| Model/scoring attack | Completed |
| Confirmatory statistical protocol | Frozen |
| Runtime3 non-confirmatory qualification | Pass |
| Schema-preservation audit | Corrected before cohort acceptance |
| First human annotation attempt | Failed forensic protocol audit; preserved |
| Confirmatory human annotation | Pending |
| Confirmatory cohort immutable lock | Pending unless separately verified by lock artifact |
| M0/M1 confirmatory model | Not run |
| Incremental predictive validity | Not established |

### 9.2 Quantitative confirmatory results

No confirmatory quantitative result is reported in this manuscript version.

In particular, no value for:

- Delta_logloss;
- Brier score;
- AUROC;
- AUPRC;
- calibration;
- model coefficient;
- confidence/uncertainty interval;
- harm prevalence in the new cohort;

is represented as a Project 2 finding until it is generated from the accepted aligned cohort under the frozen analysis protocol.

## 10. Threats to validity

### 10.1 Historical trace incompleteness

The inability to reconstruct decision-time evidence from the historical P1/P6 records prevents retrospective construction of X_W for those outcome units.

### 10.2 Measurement validity

X_W measures observable analytical witnesses. It does not establish hidden SQL correctness, global completeness, or semantic correctness of the underlying query.

### 10.3 Annotation protocol sensitivity

The first human annotation attempt demonstrated that even a simple worksheet can alter the measurement instrument. Exact packet preservation is therefore treated as part of the measurement protocol rather than as administrative metadata.

### 10.4 Rare outcomes

The historical discovery outcome is relatively sparse. The confirmatory protocol therefore uses a low-dimensional penalized model and prespecified feasibility/stopping criteria rather than relying on a simple events-per-variable rule.

### 10.5 Missing evidence

`NO_USABLE_EVIDENCE` is not equivalent to zero witness sufficiency. Treating it as zero would change the construct.

### 10.6 Dependence

Nominal record count may exceed the amount of independent information if cases share database/question structure. The frozen outer evaluation therefore preserves the defined dependence grouping.

### 10.7 External validity

Any eventual predictive-validity finding will be restricted to the tested source population, decision pathway, evidence representation, model family, and confirmatory protocol. It will not establish universal agent safety.

### 10.8 Runtime/model dependence

The acquisition pathway depends on a pinned implementation and local model/runtime configuration. Runtime qualification demonstrates reproducibility at the tested boundary but does not establish invariance across other models, runtimes, hardware, or agent architectures.

## 11. Reproducibility and evidence chain

The intended evidence chain is:

[
	ext{research question}
ightarrow
	ext{literature/gap}
ightarrow
	ext{construct attack}
ightarrow
	ext{frozen protocol}
ightarrow
	ext{pinned runtime}
ightarrow
	ext{decision-time evidence}
ightarrow
	ext{immutable cohort}
ightarrow
	ext{independent annotation}
ightarrow
	ext{out-of-sample predictions}
ightarrow
	ext{statistical analysis}
ightarrow
	ext{paper claim}.
]

Failed gates and rejected constructs remain versioned rather than being removed from the research history.

The central provenance principle is:

> **The predictor and consequential outcome must be measured on the same decision unit, and the evidence required to construct the predictor must be preserved before the consequential intervention/outcome is evaluated.**

## 12. Discussion — current methodological interpretation

The present work does not yet establish that decision-time evidence witnesses predict harmful incumbent replacement.

It does establish a set of methodological constraints required to test that proposition without retrospective leakage:

1. decision-time evidence must be preserved before outcome evaluation;
2. predictor and outcome must share the same decision unit;
3. X_W must be independently annotated from the preserved evidence;
4. `NO_USABLE_EVIDENCE` must not be silently converted into a substantive score;
5. model tuning must occur inside the training data;
6. M0 and M1 must be evaluated on identical out-of-sample observations;
7. the confirmatory protocol must not be modified to rescue an unfavorable or infeasible result.

The historical reconstruction failure is therefore itself informative about evaluation design: a predictive-validity claim can become non-identifiable after the fact if decision-time evidence needed for the proposed predictor was not preserved.

The confirmatory cohort is intended to resolve that provenance/alignment limitation prospectively.

## 13. Conclusion — current state

Project 2 has progressed from a broad robustness/safety question to a narrower predictive-validity test of an independently measured decision-time evidence-witness construct.

The historical P1/P6 records cannot support that test retrospectively because the required evidence-to-outcome alignment was not preserved. A new same-unit outcome-bearing cohort was therefore specified, and the confirmatory statistical and collection protocol was frozen before confirmatory outcome collection.

The first human annotation attempt was rejected as non-confirmatory because the annotation instrument did not faithfully reproduce the frozen packet. The failure is preserved rather than converted into an apparent reliability success.

The remaining scientific question is empirical:

> **Does adding X_W to the frozen baseline B improve out-of-sample prediction of harmful incumbent replacement under the frozen P2-C1.4 protocol?**

That question remains open until the accepted aligned cohort, independent blinded annotation, provenance lock, and prespecified analysis are completed.

## 14. Reporting plan after confirmatory completion

After the immutable cohort and annotation gates pass, this manuscript should be extended with:

- accepted cohort flow and exclusions;
- outcome prevalence;
- independent-rater reliability and provenance;
- X_W distribution and missingness;
- preregistration/registration record;
- frozen model implementation details;
- out-of-sample M0/M1 predictions;
- primary paired log-loss difference;
- uncertainty interval;
- Brier score;
- AUROC/AUPRC where estimable;
- calibration results;
- prespecified sensitivity/falsification analyses;
- complete limitations;
- claim-by-claim evidence mapping.

No result should be inserted into these sections until it is generated and provenance-checked under the frozen protocol.
