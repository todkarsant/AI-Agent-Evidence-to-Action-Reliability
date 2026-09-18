# P2-C1.2 — Baseline Feature Specification Draft v0.1

Status: DRAFT — NOT FROZEN

Purpose: define the decision-time baseline independently of the candidate observable witness construct before any outcome-bearing predictive analysis.

## Candidate baseline signals

From the recovered historical trace:
- execution status
- row count
- column count
- latency
- LLM call count
- input tokens
- output tokens
- cost
- action count
- termination/error indicators

## Exclusion rule

No X_W-derived feature, raw-evidence-derived feature, gold SQL/answer feature, P0 correctness, challenger outcome, replacement outcome, post-hoc evaluator label, or any feature selected because of its association with harm may be added after X_W or outcome inspection.

## Open issue

The repository currently documents the predictive-validity objective but does not yet contain an independently frozen formal baseline specification. Therefore this document is a proposal, not a preregistration or confirmatory model specification.

## Next methodological action

Audit whether each proposed baseline variable is genuinely available at the decision point and whether the set should include any already-documented analytical decision signals. Freeze only after that audit, before outcome-bearing feature selection.