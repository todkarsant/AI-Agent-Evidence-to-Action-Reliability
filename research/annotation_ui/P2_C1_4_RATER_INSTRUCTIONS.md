# P2-C1.4 X_W annotation: rater instructions

You are one of two independent raters, A or B. You will receive two files:

- `P2_C1_4_XW_ANNOTATOR.html`, the annotation tool. It runs offline in any modern browser.
- Your packet, `P2_C1_4_XW_RATER_A.json` **or** `P2_C1_4_XW_RATER_B.json`. Open only your own packet.

Each packet holds the same 8,638 decisions, in a different random order.

## Independence (required)

- Do not open, see or discuss the other rater's packet, answers or progress.
- Do not look at any other project file, GitHub run, artifact, SQL, reference answer, correctness label or outcome.
- Judge only what the tool shows: the question, the database schema and the returned rows.
- You will be asked to confirm this in the tool before you start. That confirmation is recorded in your export.

## How to work

1. Open the HTML file, choose your packet, enter your name or initials, tick the confirmation, and click **Start annotating**.
2. For each case and each dimension W1–W7:
   - **Applicable?**
     - **YES**: the question asks for this kind of thing.
     - **NO**: the question does not ask for it.
     - **UNCLEAR**: only if the wording of the question itself can reasonably be read both ways. Write the reason in the note.
   - **Witness:** if applicable, choose **PRESENT** when the shown rows and columns let you inspect it. Otherwise choose **ABSENT / AMBIGUOUS**.
3. Do **not** use UNCLEAR because you wonder how a hidden query was written. Decide YES or NO from the question.
4. Empty results (0 rows) are real evidence; judge them.
5. For **NO_USABLE_EVIDENCE** cases, answer applicability from the question. The witness buttons are locked.
6. Keyboard:
   - **↑ / ↓** choose a dimension.
   - **Y / N / U** set applicability.
   - **P / A** set the witness.
   - **Enter** moves to the next incomplete case once the current one is complete.

## Saving

- The tool saves your progress in this browser automatically.
- Also click **Export responses** at least once per session, and keep the file somewhere safe. You can resume on any computer with **Resume from an earlier export**.
- When every case is complete, export the **FINAL** file and send it only to the research lead.

## The seven dimensions (frozen codebook v2)

- **W1 Selection:** the attribute/values needed to check the requested restriction are visible.
- **W2 Projection:** the requested output fields are visible at the right granularity.
- **W3 Aggregation:** the aggregate value and a label for the operation are visible.
- **W4 Grouping:** the grouping key and per-group results are visible.
- **W5 Ordering:** the comparison field and the displayed order are visible.
- **W6 Extremum:** a candidate extreme value and its comparison field are visible.
- **W7 Join/linkage:** the identifiers/attributes linking the requested entities are visible.

Completeness or row count is not a dimension.
