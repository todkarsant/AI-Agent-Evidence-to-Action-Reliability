# P2-C1.2 — Predictive / Incremental Validity Attack

## Objective

Test whether the proposed reliability/evidence construct contributes information about consequential incumbent-replacement harm beyond preregistered decision-time analytical signals.

## Outcome

[
Y_H = I(P0 correct land replacement occurs land final answer incorrect)
]

The outcome is defined over the full intervention-eligible population. P0 correctness is post-hoc and cannot be used to prospectively select the analysis population.

## Model comparison

Baseline:

[
M_0=f(B)
]

Expanded:

[
M_1=f(B,X)
]

where (B) is the preregistered baseline signal set and (X) is the independently measured candidate construct.

## Scientific claim under test

The target is **incremental predictive validity**, not generic robustness, perturbation stability, provenance sensitivity, or an assertion that reliability is equivalent to safety.

## Required sequence

1. Freeze construct/codebook.
2. Establish measurement reliability.
3. Freeze baseline and expanded models.
4. Define out-of-sample evaluation.
5. Execute without outcome-dependent feature selection.
6. Report incremental performance and uncertainty.
7. Preserve null/negative findings.

## Current status

PENDING. No confirmatory predictive-validity result exists.
