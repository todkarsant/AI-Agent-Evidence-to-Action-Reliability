# P2-C1.4 X_W rater exports

Commit **both** final exports here **in one commit**, and only after **both** raters have finished:

- `P2_C1_4_XW_RESPONSES_RATER_A_FINAL.json`
- `P2_C1_4_XW_RESPONSES_RATER_B_FINAL.json`

The repository is public. Committing one rater's export before the other rater has finished would expose
labels and break independence.

A push that adds or changes a `.json` file in this folder starts the workflow
`P2-C1.4 X_W lock, construction and confirmatory analysis`
(`.github/workflows/p2-c1-4-xw-lock-and-analysis.yml`). Its two stages are:

- **Stage 1 (outcome-blind):** validates the exports, locks the raw labels, writes the reliability report and builds X_W.
- **Stage 2:** runs the frozen analysis once.

See `research/annotation/P2_C1_4_POST_ANNOTATION_RUNBOOK.md`.
