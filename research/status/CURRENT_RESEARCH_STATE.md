# Current Research State — P2-C1.2

**State:** `BLOCKED_EXTERNAL_HUMAN_VALIDATION`

**As of:** 2026-09-19

## Evidence-gate status

- **C.4.2.3-C:** targeted exact-path qualification succeeded for the frozen `behavior_monitoring` case, but this does **not** establish global P0 determinism.
- **C.4.2.3-D:** observational evidence capture qualification succeeded on current `main` under the targeted qualification scope.
- **C.4.2.4-A:** blocked pending two genuinely independent human annotation passes.
- **P2-C1.2:** confirmatory predictive/incremental-validity analysis has **not** started.

## Audited C.4.2.3-D run

Run: [35367903444](https://github.com/todkarsant/AI-Agent-Evidence-to-Action-Reliability/actions/runs/35367903444)

The completed workflow asserted all of the following:

- exact SQL agreement across the two repeats for all 12 pilot cases;
- exact execution-status agreement;
- exact captured-evidence agreement;
- trace row/column counts equal captured counts;
- observational capture only;
- gold SQL excluded from the provider prompt.

Artifact: `c4-2-3-evidence-capture12`, artifact ID `10557028043`, SHA-256 `263189690377c6e38dad655b95a18a68dd6496e0dbc93cc9d9d7b00c351f7a45`.

## Human-validation block

The remaining measurement claim cannot be established by another model run or by duplicate annotation from the same rater.

Required before advancing:

1. Two genuinely independent raters complete the frozen annotation packets.
2. Raters remain blinded to gold SQL/answer, correctness, replacement/intervention outcomes, and downstream outcomes.
3. Raw annotation sets are locked unchanged.
4. Obligation-level agreement is calculated, including contingency tables and agreement statistics.
5. Predefined disagreement/codebook-failure audit is performed.
6. Any codebook revision creates a new version/cohort rather than silently modifying the existing cohort.

## Scientific safety boundary

No confirmatory P2-C1.2 model fitting, feature selection, outcome-conditioned codebook changes, or claims of human measurement reliability are permitted while this state remains active.

The model-only pilot agreement (86.96% raw agreement; Cohen's kappa 0.721; Gwet AC1 0.756 over 23 binary comparisons) remains **non-confirmatory** and is not a substitute for independent human raters.
