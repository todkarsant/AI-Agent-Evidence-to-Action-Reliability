# Research Charter

## Project identity

**Project:** AI Agent Evidence-to-Action Reliability

**Repository:** `todkarsant/AI-Agent-Evidence-to-Action-Reliability`

**Role:** canonical scientific source of truth for Project 2.

## Research objective

Develop and rigorously test a defensible construct for decision-time evidence sufficiency/reliability in AI agents, and determine whether that construct adds predictive information about consequential intervention/replacement harm beyond existing decision-time analytical signals.

## Research question

> Do preregistered reliability/robustness measures improve out-of-sample prediction of harmful incumbent replacement beyond preregistered decision-time analytical signals?

This is a working research question, not a confirmed conclusion.

## Primary harm definition

For an evaluation case (i):

[
Y_{H,i}=I(P0 correct land replacement occurs land final answer incorrect)
]

The outcome is defined over the full intervention-eligible population for prospective modeling. P0 correctness is a post-hoc outcome and therefore cannot be used as a prospective inclusion criterion.

## Predictive validity framing

Baseline model:

[
M_0=f(B)
]

Expanded model:

[
M_1=f(B,X)
]

where:

- (B) = preregistered baseline decision-time analytical signals;
- (X) = independently measured candidate reliability/evidence construct.

The scientific question is incremental validity: whether adding (X) improves out-of-sample prediction of consequential harm beyond (B).

## Candidate construct

The current candidate is:

> independently measured sufficiency of decision-time execution evidence to substantiate the requested analytical result.

A provisional operationalization is based on evidence obligations derived from the question and schema, scored against the decision-time execution evidence without use of gold SQL, gold answer, challenger output, replacement outcome, or other post-hoc information.

The operationalization is not yet frozen as a confirmatory measurement instrument.

## Design constraints

- No leakage of post-hoc outcome information into decision-time features.
- Fresh corpus required for confirmatory measurement.
- Annotation must be outcome-blinded.
- Independent raters are required for empirical reliability assessment.
- Measurement reliability must be evaluated before predictive validity is interpreted.
- Repeated perturbations are repeated measurements, not independent harm events.
- Discovery data may motivate hypotheses but cannot silently become confirmatory evidence.

## Stopping / gating philosophy

A construct or analysis does not advance merely because it produces a significant or favorable result. It advances only when the required methodological gate is satisfied.

Failures and redesigns are part of the permanent record.

## Current phase

Methodological validation is in progress. No confirmatory predictive-validity conclusion has been established.
