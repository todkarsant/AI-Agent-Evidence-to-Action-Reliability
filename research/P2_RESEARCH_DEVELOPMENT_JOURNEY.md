# Project 2 — Research Development Journey Ledger

**Purpose:** Preserve the methodological development path, failed constructs, negative findings, corrections, and evidence boundaries for the eventual research paper.

This ledger is an audit trail, not a polished narrative. Historical decisions are retained rather than rewritten.

## Phase 1 — Problem discovery

### P1/P6 discovery evidence

Project 1 established an intervention/replacement setting in which a policy could replace an incumbent analytical answer.

Historical P6-IP development results reported:

- 330 intervention-eligible cases;
- 21 harms;
- 2 rescues;
- net intervention gain = -19;
- lower overall accuracy than P0;
- higher mean cost than P0.

The held-out schema set reported:

- 91 intervention-eligible cases;
- 5 harms;
- 1 rescue;
- net intervention gain = -4;
- higher mean cost than P0.

These results motivated the question of why decision-time evidence was insufficient for safe consequential replacement.

**Evidence boundary:** these are historical Project 1 discovery/mechanism results, not confirmatory Project 2 evidence.

## Phase 2 — Novelty attacks

### P2-C1.1

Generic context perturbation, evidence sufficiency, semantic invariance, provenance, and reliability framings were attacked against contemporary literature.

Generic versions were rejected as insufficiently novel.

The surviving research seam became narrower:

> whether an independently measured, decision-time observable evidence-witness measure has incremental predictive validity for consequential replacement harm beyond existing decision-time signals.

## Phase 3 — Construct redesign

### Historical semantic-sufficiency construct X_E

Rejected because result-only evidence cannot establish hidden predicate correctness, completeness, join correctness, aggregate population correctness, or hidden SQL correctness.

### W1-W7 witness construct X_W

Frozen as an observable decision-time witness construct:

- W1 Selection
- W2 Projection
- W3 Aggregation
- W4 Grouping
- W5 Ordering
- W6 Extremum
- W7 Join/linkage

The construct deliberately excludes hidden SQL correctness and global completeness/cardinality.

## Phase 4 — Measurement validation

### Historical packet provenance problem

The earlier human annotation packet bytes could not be cryptographically reconstructed from preserved Project 2 artifacts.

Decision: never silently recreate byte-different packets and call them historical.

### New frozen cohort

A deterministic 12-case blinded W1-W7 cohort was generated with pinned schema, source evidence, generator, codebook, and packet hashes.

### Human annotation

Two independent human annotations were supplied and preserved.

Observed descriptive agreement:

- applicability: 49/49;
- Cohen kappa = 1.00;
- witness: 27/27;
- Cohen kappa = 1.00;
- Gwet AC1 = 1.00.

The explicit independent-rater attestation satisfies the protocol's provenance requirement, while the perfect agreement remains descriptive and does not itself prove construct validity.

### UNCLEAR rule

An implementation-ambiguity issue was identified and frozen before confirmatory outcome modeling.

The chronology is explicitly disclosed as a **pre-outcome methodological amendment**, not as prospective preregistration before annotation.

## Phase 5 — Predictive-validity attack

P2-C1.2 was attacked before fitting M0/M1.

The attack identified:

1. X_W/Y_H unit mismatch.
2. unresolved missing-X_W design.
3. rare binary outcome requiring a deliberately stable model.
4. need for true out-of-sample incremental-validity evaluation.
5. need to freeze primary scoring metric.
6. need to freeze outer resampling and dependence structure.
7. historical holdout cannot be external validation for X_W.

Confirmatory modeling was blocked.

## Phase 6 — P2-C1.3 aligned-cohort reconstruction

The historical Project 1 repository, P6 experiment design/runner/workflow, and Project 2 provenance were inspected.

Result:

> The historical outcome cohort and current X_W measurement cohort cannot be joined at the required decision-unit/evidence level from the preserved scientific record.

The P6 workflow did produce historical trace artifacts, but the scientific record does not establish preservation of the raw decision-time evidence required for independent W1-W7 annotation across the historical outcome units.

Therefore historical reconstruction is rejected.

## Current scientific state

[
\boxed{
B + X_W + Y_H
\text{ must be collected/aligned on the same decision units before modeling}
}
]

No confirmatory M0/M1 result exists.

## Publication principle

The final paper should report both:

- the positive methodological achievement: a frozen, independently annotated observable witness construct with documented reliability and provenance;
- the negative methodological finding: historical P1/P6 traces cannot support retrospective incremental-validity fusion because the required decision-time evidence was not preserved in the needed form.

This negative finding is part of the evidence chain, not an omission.

## Required future cohort

Each new outcome-bearing decision unit must preserve:

[
(id, B, E_{decision-time}, intervention, final correctness, Y_H)
]

and permit independent outcome-blinded W1-W7 annotation.

Only after this aligned cohort is locked should the statistical model and confirmatory analysis be frozen.


### P2-C1.4 acquisition forensic update — 2026-09-21
- Confirmatory acquisition attempts exposed runtime Ollama HTTP timeouts; a versioned transport-only amendment now pins Project 1 commit `7bef895846f2ac89d885827be16b30e69986b013` and `OLLAMA_TIMEOUT_SECONDS=300` under protocol `P2-C1.4-CONFIRMATORY-V1-RUNTIME1-2026-09-21`.
- Forensic audit also found that the collector did not preserve the exact decision-time schema required for W1-W7 annotation. This was corrected before accepting any confirmatory cohort; aligned records are now V2 and include schema in the evidence hash.
- A mechanical forensic lock auditor is now wired into consolidation and will fail closed unless all 8,638 source-frame decision IDs are present in exact order and evidence/outcome invariants pass.
- Current target acquisition run: `35598330749` (run #12), currently pending GitHub Actions capacity. No cohort is locked; no X_W annotation or M0/M1 analysis has begun.
