# AI Agent Evidence-to-Action Reliability

A research program investigating evidence-to-action reliability in AI agents: whether the sufficiency and reliability of decision-time evidence can explain or predict consequential intervention and replacement errors beyond existing decision signals.

## Research status

**Current phase:** methodological validation / pre-confirmatory work.

The present research program is not yet a confirmed claim of improved safety, reliability, generality, or novelty. Candidate constructs and measurement procedures are being subjected to adversarial methodological attacks before confirmatory implementation.

## Core research idea

The working research chain is:

`decision-time evidence → evidence sufficiency/reliability → agent decision → intervention/replacement → consequential outcome`

The central question is whether evidence available to an AI agent at decision time contains measurable information about consequential action error beyond existing decision-time analytical signals.

## Scientific boundary

This repository is the canonical source of truth for Project 2. It records:

- research questions and hypotheses;
- literature and novelty analysis;
- methodological gates and falsification attacks;
- preregistration decisions;
- dataset and runtime provenance;
- pilot and confirmatory experiment records;
- analysis specifications and results;
- failures, exclusions, and negative findings;
- reproducibility artifacts and implementation decisions.

Historical evidence must not be rewritten to fit later results.

## Relationship to other repositories

- **Project 1:** `todkarsant/Enterprise-Analytics-Copilot`
- **LLM evaluation/observability tooling:** `todkarsant/LLM-Evaluation-Observability-Platform`
- **This repository:** Project 2 research source of truth.

## Current methodological position

The current candidate seam is not generic robustness or generic provenance. Those areas are already represented in the literature. The working seam is narrower:

> Whether an independently measured decision-time evidence-sufficiency construct provides incremental predictive validity for consequential incumbent-replacement harm beyond preregistered decision-time analytical signals.

This proposition remains to be tested and may be falsified.

## Working principles

1. Preserve discovery, null, and failure evidence.
2. Separate decision-time information from post-hoc oracle information.
3. Prevent leakage from gold SQL, gold answers, replacement outcomes, or other post-hoc information into decision-time constructs.
4. Validate construct identifiability before measuring it.
5. Validate measurement reliability before testing predictive validity.
6. Use fresh evaluation data for confirmatory claims.
7. Do not treat repeated perturbations as independent outcome events.
8. Do not claim exact historical reproducibility where model/artifact identity was not recorded.
9. Freeze specifications before outcome-dependent analysis.
10. Prefer falsification over confirmation.

## Status at repository creation

The research record imported into this repository begins from an existing P1/P6 discovery program. That evidence is retained as discovery/mechanism evidence and is not treated as confirmatory P2 evidence.

The current P2 methodological sequence includes:

- construct identifiability attack;
- construct separation/redesign;
- deterministic evidence-obligation extraction;
- measurement reliability attack;
- fresh corpus and double-blind annotation;
- predictive/incremental validity attack.

The first fresh-corpus acquisition gate has passed; fresh P0 execution remains a separate step and must be provenance-recorded before use.

## Canonical rule

When repository content conflicts with an informal statement in conversation, the repository's versioned research record is authoritative until a documented amendment is made.
