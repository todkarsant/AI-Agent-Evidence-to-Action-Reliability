# AI Agent Evidence-to-Action Reliability — Living Research Paper Draft

**Status:** Methodological draft — **confirmatory predictive-validity results not yet available**  
**Last updated:** 2026-09-21

> This document is deliberately not submission-ready. It is a living manuscript scaffold whose claims are constrained by the current evidence ledger.

## Abstract — draft

Consequential analytical agents may produce executable and apparently plausible alternatives to an incumbent answer, yet replacing a correct incumbent can cause harm even when the intervention is triggered by decision-time evidence. We study whether an independently measured, observable representation of decision-time evidence can provide incremental predictive information about harmful incumbent replacement beyond existing decision-time analytical signals.

The research program developed from a negative Project 1 intervention result in which an incumbent-preserving analytical intervention mechanism produced substantially more harmful replacements than rescues and increased cost. Rather than treating generic context sensitivity or evidence sufficiency as the contribution, we redesigned the predictor around observable witnesses of analytical obligations: selection, projection, aggregation, grouping, ordering, extremum, and join/linkage.

The measurement protocol was frozen, independently annotated by two raters, mechanically validated, and preserved with packet and codebook provenance. The submitted annotations showed complete descriptive agreement for both applicability and binary witness labels. However, a subsequent predictive-validity attack identified a decisive cohort-alignment problem: the 12-case measurement cohort is not the same decision population as the historical 330/91 outcome cohorts, and the historical traces do not preserve the decision-time evidence required for independent X_W annotation. We therefore do not fit the planned predictive models. Instead, we document the reconstruction failure and define the requirements for a new aligned outcome-bearing cohort.

The current contribution is therefore methodological and boundary-setting rather than a claim of predictive validity.

## 1. Introduction

### 1.1 Problem

The safety relevance of an analytical agent is not exhausted by whether a generated answer is correct. In a replacement setting, the system must decide whether to displace an incumbent answer. This introduces a consequential decision layer:

[
	ext{analytical correctness}
ightarrow
	ext{intervention}
ightarrow
	ext{replacement consequence}.
]

Project 1 provided discovery evidence that this layer can fail: the P6-IP development experiment recorded 21 harmful replacements against 2 rescues among 330 intervention-eligible cases, with higher mean cost than the P0 incumbent.

These historical results are not treated as confirmatory evidence for the present study. They motivate the present research question.

### 1.2 Research question

> Do preregistered reliability/robustness measures improve out-of-sample prediction of harmful incumbent replacement beyond preregistered decision-time analytical signals?

Formally:

[
Y_H=I(P0 correct land replacement occurs land final answer incorrect).
]

The intended comparison is:

[
M_0=f(B)
]

versus

[
M_1=f(B,X_W).
]

The incremental-validity question is whether adding X_W improves out-of-sample prediction of Y_H.

### 1.3 Novelty discipline

Generic claims about context length, evidence position, semantic invariance, provenance, grounding, evidence sufficiency, or agent reliability are not sufficient novelty claims for this paper. The proposed seam is narrower: an independently measured, decision-time observable witness construct evaluated as an incremental predictor of consequential replacement harm.

Novelty remains a working claim until the final literature review and empirical test are complete.

## 2. Project 1 discovery evidence

Project 1's P6-IP experiment was designed to test whether incumbent preservation and evidence-dependent intervention could improve the reliability/cost trade-off.

The recorded development results were:

- P0 accuracy: 254/1034;
- P6-IP accuracy: 234/1034;
- 21 harmful replacements;
- 2 rescues;
- net intervention gain: -19;
- P6-IP mean cost approximately 25.8% higher than P0.

The held-out-schema record contained 91 intervention-eligible cases, 5 harms, and 1 rescue, with approximately 29.2% higher mean cost for P6-IP.

These numbers are reported as Project 1 discovery/mechanism evidence. They do not establish the present X_W construct or its predictive validity.

## 3. Construct development

### 3.1 Rejected construct: result-only semantic sufficiency

The initial evidence-sufficiency idea attempted to judge whether returned evidence was sufficient for an analytical obligation.

Adversarial analysis rejected a purely result-level interpretation because visible outputs cannot establish hidden:

- predicate correctness;
- global completeness;
- join correctness;
- aggregate population correctness;
- SQL semantics.

### 3.2 Frozen witness construct

The construct was redesigned to measure only observable witnesses needed to inspect analytical obligations.

The seven dimensions are:

1. selection witness;
2. projection witness;
3. aggregation witness;
4. grouping witness;
5. ordering witness;
6. extremum witness;
7. join/linkage witness.

For a SUCCESS case:

[
X_W=rac{sum_{jin A}w_j}{|A|}.
]

Dimensions not entailed by the natural-language question are excluded. Genuine semantic ambiguity receives a conservative zero while remaining in the denominator. NO_USABLE_EVIDENCE is missing X_W, not zero.

The construct does not encode hidden SQL correctness or global completeness.

## 4. Measurement validation

### 4.1 Packet provenance

The historical human packet bytes from the first annotation attempt could not be reconstructed from preserved artifacts. A new versioned cohort was therefore generated rather than silently reconstructing byte-different historical packets.

### 4.2 Independent annotation

The frozen 12-case packet contained 7 SUCCESS and 5 NO_USABLE_EVIDENCE cases.

Across the 7 SUCCESS cases:

- applicability judgments = 49;
- raw agreement = 100%;
- Cohen's kappa = 1.00.

Across applicable binary witness judgments:

- binary judgments = 27;
- raw agreement = 100%;
- Cohen's kappa = 1.00;
- Gwet AC1 = 1.00.

These are descriptive reliability results of the submitted annotations. Independence is supported by an explicit independent-rater attestation; the artifacts themselves are not treated as cryptographic proof of human independence.

### 4.3 Methodological amendment

One annotation ambiguity was identified around whether hidden implementation details should determine witness applicability. A deterministic UNCLEAR-to-X_W operational rule was frozen before outcome modeling.

The chronology is explicitly disclosed: this was a pre-outcome methodological amendment made after annotation submission, not a prospective preregistration decision made before annotation.

## 5. Predictive-validity design attack

Before fitting any predictive model, the design was attacked for:

- unit-of-analysis alignment;
- outcome leakage;
- predictor timing;
- missing X_W;
- rare outcome stability;
- out-of-sample evaluation;
- scoring metric choice;
- cross-validation optimism;
- dependence structure;
- historical holdout validity;
- baseline contamination.

The decisive failure was unit alignment.

## 6. P2-C1.3 aligned-cohort reconstruction result

### 6.1 Historical outcome cohort

The historical P1/P6 record provides outcome summaries for:

- 330 intervention-eligible development cases;
- 91 intervention-eligible held-out cases.

### 6.2 Current X_W cohort

The current measurement cohort contains 12 fresh cases and was deliberately non-overlapping with historical P1/P6 schemas/questions.

### 6.3 Required alignment

A valid predictive row must contain:

[
(B_i,E_i^{decision-time},X_{W,i},Y_{H,i})
]

for the same decision instance.

The preserved research record does not establish this alignment for the historical P1/P6 cohort.

### 6.4 Decision

Historical reconstruction is rejected.

No X_W values will be retrofitted to the 330/91 historical outcome units. The 91-case holdout will not be described as external validation for X_W.

This is a scientific data-design failure, not an infrastructure failure.

## 7. Proposed new aligned cohort

The next cohort must preserve, for every eligible decision instance:

- decision identifier;
- baseline B;
- exact decision-time evidence;
- temporal/provenance metadata;
- intervention/replacement decision;
- final correctness;
- Y_H;
- independently collected W1-W7 annotation;
- raw annotation files and hashes.

Human annotators must remain blinded to Y_H, P0 correctness, replacement outcome, generated/reference SQL, and post-hoc evaluator labels.

## 8. Statistical analysis — frozen only after cohort alignment

The following elements remain intentionally unfrozen until the aligned cohort exists:

- exact model family;
- regularization/penalization;
- missing-X_W strategy;
- primary proper scoring rule;
- outer resampling scheme;
- dependence/cluster unit.

The confirmatory estimand will compare paired out-of-sample predictive loss:

[
Delta_L=E[L(Y,p_0)]-E[L(Y,p_1)].
]

Positive values indicate lower loss for M1 under the chosen convention.

No coefficient, p-value, AUC, Brier score, or log-loss difference is currently a research result.

## 9. Threats to validity

### Historical trace incompleteness

The absence of preserved decision-time evidence prevents retrospective construction of X_W.

### Construct validity

X_W measures observable witnesses, not hidden SQL correctness or evidence completeness.

### Rare outcome

The historical development harm rate is approximately 6.36% among 330 eligible cases. A future model must remain low-dimensional and stability-oriented.

### Missing predictor

NO_USABLE_EVIDENCE cannot be treated as X_W=0 without changing the construct.

### Generalization

The eventual claim will be limited to the tested decision protocol and population.

## 10. Reproducibility and evidence chain

The intended paper evidence chain is:

[
	ext{frozen construct}
ightarrow
	ext{packet hash}
ightarrow
	ext{raw annotation}
ightarrow
	ext{aligned outcome cohort}
ightarrow
	ext{frozen model protocol}
ightarrow
	ext{out-of-sample predictions}
ightarrow
	ext{statistical analysis}
ightarrow
	ext{paper claim}.
]

Failed gates and rejected constructs remain versioned in the repository.

## 11. Current results table

| Result | Status |
|---|---|
| W1-W7 construct frozen | Established |
| Human annotation mechanical validity | Established |
| Descriptive inter-rater agreement | Established |
| Human independence provenance | Attested |
| UNCLEAR operational rule | Frozen as pre-outcome amendment |
| Historical X_W/Y_H alignment | **Failed** |
| Confirmatory predictive model | **Not run** |
| Incremental predictive validity | **Not established** |
| Generalization | **Not established** |

## 12. Conclusion — current draft

The present study has not yet demonstrated that observable decision-time evidence witnesses predict harmful incumbent replacement. Instead, the methodological development has established a more important boundary condition: a predictive-validity claim requires the predictor and consequential outcome to be measured on the same decision units, with the evidence needed to construct the predictor preserved at decision time.

The current historical Project 1 outcome records cannot satisfy that requirement retrospectively. The appropriate next step is therefore a new aligned outcome-bearing cohort, not statistical modeling of incompatible historical and measurement datasets.

## 13. Planned next section

Once P2-C1.4 is completed, this document should be extended with:

- aligned cohort construction;
- preregistration/registration record;
- sample-size justification;
- frozen model specification;
- out-of-sample evaluation;
- calibration/discrimination results;
- incremental proper-scoring-loss comparison;
- sensitivity analyses;
- complete limitations and reporting checklist.

**No results should be inserted into those sections until they are actually generated and provenance-checked.**
