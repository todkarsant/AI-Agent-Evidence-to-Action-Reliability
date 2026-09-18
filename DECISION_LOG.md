# Decision Log

This file records material methodological and research decisions. Decisions should be appended rather than rewritten.

## 2026-09-18 — Project 2 canonical repository established

**Decision:** Establish `AI-Agent-Evidence-to-Action-Reliability` as the canonical source of truth for Project 2.

**Reason:** Separate the research program from Project 1 implementation and from the existing LLM evaluation/observability platform.

**Effect:** Future methodological decisions, runtime provenance, experiments, failures, and publication records are versioned here.

## 2026-09-18 — Working project identity

**Decision:** `AI Agent Evidence-to-Action Reliability`

**Repository:** `AI-Agent-Evidence-to-Action-Reliability`

**Scope note:** The project is about AI agents; current experiments are LLM-mediated, but the repository name is intentionally not tied to a single model family.

## Methodological policy — preserve falsification

**Decision:** Failed constructs, negative results, and rejected novelty claims remain permanently documented.

**Reason:** Avoid retrospective confirmation bias and preserve auditability.

## Methodological policy — P1/P6 is discovery evidence

**Decision:** Historical P1/P6 results are not reused as confirmatory P2 evidence.

**Reason:** P2 confirmatory claims require a fresh and properly frozen evaluation design.

## Methodological policy — decision-time vs post-hoc information

**Decision:** Features intended to represent decision-time information must not depend on gold SQL, gold answer, P0 correctness, challenger correctness, replacement status, or other post-hoc information.

**Reason:** Such leakage would invalidate predictive-validity interpretation.

## Methodological policy — exact reproducibility claims

**Decision:** Do not claim byte-identical historical model reproduction unless the historical artifact digest is available and matches.

**Current state:** Historical digest unavailable; recovered model digest recorded separately.
