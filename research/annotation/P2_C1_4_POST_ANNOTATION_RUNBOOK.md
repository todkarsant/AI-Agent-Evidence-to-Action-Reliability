# P2-C1.4 runbook: from rater exports to the confirmatory analysis

**Purpose:** step-by-step guide for the research lead, covering the path from the two raters' finished exports to the frozen confirmatory analysis.

**Applies to:** cohort `da537c75ce5778af3c36d05d8e59f7cea296aa5b8a4bc0c527b7cf352ebd9b8b` (acquisition run `36853456589`) and blinded packets from post-lock run `37017913823`.

> **Update 2026-10-07: the raters annotate a subsample, not the full cohort.**
>
> - **Why:** amendment `P2-C1.4-BLINDED-FEASIBILITY-AND-ANNOTATION-SUBSAMPLE-AMENDMENT-2026-10-07`.
> - **Feasibility run:** `37663285811`, verdict `SUBSAMPLE_DRAWN`.
> - **Workload:** 1,709 cases per rater.
> - **Rater packets:** come from artifact `p2-c1-4-xw-subsample-annotation-packets` of run `37663285811` (packets A `f7bd7bac…`, B `50a32588…`). They expire around 2027-01-05.
> - **Full packets:** the full packets from `37017913823` / `37283958876` are **no longer sent** to raters.
> - **Automatic handling:** the sources file already points the gate at the subsample. Stage 1 checks the sampling record, and Stage 2 expands X_W to the full cohort automatically.

**Governing documents:**
- frozen protocol `P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21`;
- missingness amendment (2026-10-01);
- X_W construction and analysis implementation amendment (frozen 2026-10-02), which sets the Riley criteria as a **hard stop**.

## The pipeline at a glance

```
Rater A export ─┐
                ├─► one commit to main ─► GitHub Actions: "P2-C1.4 X_W lock, construction and confirmatory analysis"
Rater B export ─┘        │
                         ├─ Stage 1 (outcome-blind, never sees the cohort)
                         │    1. both FINAL exports present?
                         │    2. packets match the packet manifest (SHA-256)?
                         │    3. each export passes the validator (complete, attested, frozen vocabulary)
                         │    4. raw labels hash-locked → reliability report → X_W built
                         │
                         ├─ Features (outcome-blind, in parallel with Stage 1)
                         │    reference-SQL hardness + nesting depth, must reproduce CSV 5e1b2edb…
                         │
                         └─ Stage 2 (only if Stage 1 and Features passed; runs ONCE ever)
                              5. refuse if a confirmatory result already exists
                              6. cohort SHA = expected = the cohort the packets came from
                              7. frozen M0 vs M1 analysis (20 repeats, no test mode),
                                 missingness audit includes hardness and nesting depth
                                 → ANALYSIS_COMPLETED, FEASIBILITY_STOP_RILEY or FEASIBILITY_STOP
```

## Ground rules (read before anything else)

1. **Independence.** Raters must never see each other's packet, answers or progress. They must not see any GitHub run or artifact, or this repository.
2. **One commit, both files.** The repository is public. Never commit one rater's export while the other rater is still working.
3. **Raw labels are never edited.** If an export fails validation, the **rater** fixes it in the tool and re-exports. Nobody edits the JSON by hand.
4. **The analysis runs once.** Stage 2 refuses to run a second time, and there is no override. Do not rename or delete the results artifact to get around this.
5. **Blinding until the analysis.** Do not open the cohort artifact or its outcome summaries before Stage 2 has run.

---

## Step 1: Secure the artifacts (do this now, before raters finish)

GitHub artifacts expire on the following dates. The gate needs the packets and the cohort, so they must still exist when the raters finish.

| Artifact | Approx. expiry |
|---|---|
| `p2-c1-4-confirmatory-frozen-manifest` | ~2026-10-15 |
| `p2-c1-4-xw-blinded-annotation-packets` | ~2026-10-16 |
| `p2-c1-4-confirmatory-aligned-cohort` | ~2026-11-01 |

### 1a. Local archive (the archive of record)

1. Open the run pages and download each artifact (you must be signed in):
   - Acquisition run 36853456589: frozen manifest, aligned cohort, G3 gate verdict, and optionally spider-source (263 MB) and the 44 shards.
   - Post-lock run 37017913823: blinded annotation packets.
2. Store them in a private location the raters cannot access.
3. Record the SHA-256 of each zip and of `P2_C1_4_CONFIRMATORY_ALIGNED_RECORDS.json`, which must equal `da537c75…9ebd9b8b`.

   Windows PowerShell: `Get-FileHash <file> -Algorithm SHA256`.

### 1b. Extend the retention on GitHub (so the automated gate keeps working)

> **Status 2026-10-03: done once.**
>
> - **Run:** `37102281986`.
> - **Verification:** packets matched their manifest; the cohort matched `da537c75…`; the packets were generated from that cohort.
> - **Sources file:** now points to `37102281986`.
> - **New expiry:** about 90 days after 2026-10-03, so around 2027-01-01. This assumes the repository's maximum artifact retention is 90 days; check the expiry on the run page.
> - **Next refresh:** due before about 2026-12-20, if Stage 2 has not run by then.
>
> **Status 2026-10-05: refreshed again.**
>
> - **Run:** `37283958876`.
> - **Coverage:** it now also keeps the Spider source bundle, and it verified the frozen manifest `4500d33b…`.
> - **Sources file:** all three run IDs now point to `37283958876`.
> - **New expiry:** around 2027-01-03.
> - **Next refresh:** due before about 2026-12-22.


1. Go to **Actions → P2-C1.4 artifact retention refresh → Run workflow** (branch `main`).
2. The run checks every hash before re-uploading anything: the packets against their manifest, the cohort against `da537c75…`, and that the packets were generated from that cohort. It then re-uploads all three artifacts with **90-day** retention. The contents are unchanged.
3. When it finishes, copy its **run ID** (the number in the run's URL).
4. Edit `research/annotation/P2_C1_4_POST_ANNOTATION_SOURCES.json` and set **both** `packets_run_id` and `cohort_run_id` to that run ID. Do **not** change `expected_cohort_sha256`. Commit to `main`.
5. Repeat 1b about every 80 days until Stage 2 has run.

> If the refresh run fails at "Verify hashes", **stop**. Do not change the expected hash. The hash chain is broken or the hash on record is wrong, and this must be resolved before any annotation is used.

## Step 2: Send each rater their kit

Send each rater **only** their own three files, privately (by email or a shared drive, not GitHub links):

| Rater A gets | Rater B gets |
|---|---|
| `P2_C1_4_XW_ANNOTATOR.html` (from `research/annotation_ui/`) | same tool |
| `P2_C1_4_RATER_INSTRUCTIONS.md` | same instructions |
| `P2_C1_4_XW_RATER_A.json` (from the **subsample** packets artifact, run `37663285811`; 1,709 cases) | `P2_C1_4_XW_RATER_B.json` (same artifact) |

Never send the packet manifest, `SAMPLING_RECORD.json`, the cohort, or the other rater's packet.

## Step 3: While the raters work

- Raters should export a backup at least once per session. Exports are named `..._PARTIAL_<n>.json`.
- **Optional progress check** on your own computer, with a partial export. This never counts for the lock.

  ```bash
  python research/cohort/validate_P2_C1_4_XW_responses.py \
    --packet P2_C1_4_XW_RATER_A.json \
    --response P2_C1_4_XW_RESPONSES_RATER_A_PARTIAL_1200.json --allow-partial
  ```

- Do not share one rater's progress or answers with the other.
- Keep the artifact retention alive (Step 1b).

## Step 4: Collect the final exports

When a rater has completed every case, the tool exports a file named:

- `P2_C1_4_XW_RESPONSES_RATER_A_FINAL.json` (rater A)
- `P2_C1_4_XW_RESPONSES_RATER_B_FINAL.json` (rater B)

1. Receive both files privately.
2. **Keep the file names exactly as exported.** The gate looks for these names.
3. Optional local pre-check, which should print `"status": "PASS"` for each:

   ```bash
   python research/cohort/validate_P2_C1_4_XW_responses.py --packet P2_C1_4_XW_RATER_A.json --response P2_C1_4_XW_RESPONSES_RATER_A_FINAL.json
   python research/cohort/validate_P2_C1_4_XW_responses.py --packet P2_C1_4_XW_RATER_B.json --response P2_C1_4_XW_RESPONSES_RATER_B_FINAL.json
   ```

4. If a check fails, send the problem list back to **that rater only**. They fix it in the tool, using **Resume from an earlier export**, and send a new FINAL file.

## Step 5: Commit both exports in one commit

**On github.com:**

1. Open `research/annotation/p2_c1_4_xw_responses/`.
2. Click **Add file → Upload files**.
3. Drag in **both** FINAL files together. The browser upload limit is 25 MB per file; for a larger file, use git (below).
4. Commit message: `P2-C1.4: rater A and B final X_W exports`.
5. Choose **Commit directly to the main branch** and click **Commit changes**.

**Or with git:**

```bash
git checkout main && git pull
cp <path>/P2_C1_4_XW_RESPONSES_RATER_A_FINAL.json <path>/P2_C1_4_XW_RESPONSES_RATER_B_FINAL.json research/annotation/p2_c1_4_xw_responses/
git add research/annotation/p2_c1_4_xw_responses/*.json
git commit -m "P2-C1.4: rater A and B final X_W exports"
git push origin main
```

The push starts the workflow automatically. Nothing else needs to be triggered.

## Step 6: Watch the run

Go to **Actions → P2-C1.4 X_W lock, construction and confirmatory analysis**. The newest run should have been started by your commit.

| Stage | Takes about | Pass looks like | Artifact |
|---|---|---|---|
| Stage 1 | a few minutes | `PASS_RAW_ANNOTATIONS_LOCKED_XW_CONSTRUCTED` in the run summary | `p2-c1-4-xw-raw-lock-and-construction`, which holds the raw-annotation lock, `P2_C1_4_XW_RELIABILITY.json`, `P2_C1_4_XW.json`, the per-rater X_W and both validation reports |
| Stage 2 | ~20–40 min | `ANALYSIS_EXECUTED`, with the primary verdict in the run summary | `p2-c1-4-confirmatory-analysis-results`, which holds `analysis/results.json`, `summary.md`, the per-case CSVs, `run_metadata.json` and `STAGE2_VERDICT.json` |

**Reading the Stage 2 primary verdict:**

| Verdict | Meaning |
|---|---|
| `ANALYSIS_COMPLETED` | The primary Δlog-loss, its 20-repeat interval, S1/S2 and the robustness flag are in `results.json`. |
| `FEASIBILITY_STOP_RILEY` | The primary population misses Riley criterion (i) or (iii). As frozen, no model is fitted; report descriptives and the shortfall. This is a valid confirmatory outcome, not an error. |
| `FEASIBILITY_STOP` | The frozen group-stratified folds cannot be built. Report it as above. |

After Stage 2:

1. Download both artifacts.
2. Archive them with the cohort.
3. Share the results artifact with the analysis lead for the paper (§9.3). Every reported number must cite the `results.json` SHA-256 printed in `STAGE2_VERDICT.json`.

## Step 7: If something fails

| Where | Message | What to do |
|---|---|---|
| Stage 1 | `both FINAL rater exports must be committed together` | Only one file is in the folder, or a name was changed. Add the missing file with its exact exported name, or fix the name. Do not rename by editing contents. |
| Stage 1 | `rater X export failed validation` | Download `p2-c1-4-xw-stage1-refusal`, read `P2_C1_4_XW_VALIDATION_X.json`, and send the problems to rater X only. They fix the export in the tool, and you commit the new FINAL file. The workflow re-runs. |
| Stage 1 | `packet X does not match the packet manifest` | The wrong packets were downloaded. Check `packets_run_id` in the sources file. |
| Stage 1 | download of packets fails | The artifact expired. Use your local archive and contact the analysis lead; the packets must be re-supplied with identical bytes. This is why Step 1b matters. |
| Stage 2 | `already been executed once` | Working as designed. Use the existing results artifact. |
| Stage 2 | `cohort SHA-256 differs …` | Stop. Do not change the expected hash. Report it. The cohort artifact is not the locked cohort. |
| Stage 2 | `analysis refused its inputs (exit 2)` | Input-integrity failure. Read `p2-c1-4-analysis-stage2-refusal` and report it before doing anything else. |

## What is automatic and what is not

| Automatic (GitHub Actions) | Manual (you) |
|---|---|
| Export validation, raw-label lock, reliability report, X_W construction, frozen analysis (once) | Sending kits, collecting exports, committing both files together, refreshing retention, local archiving, writing results into the paper |

## Files

| Path | Role |
|---|---|
| `.github/workflows/p2-c1-4-xw-lock-and-analysis.yml` | Two-stage gate workflow |
| `.github/workflows/p2-c1-4-artifact-retention-refresh.yml` | Hash-checked 90-day re-upload |
| `research/annotation/P2_C1_4_POST_ANNOTATION_SOURCES.json` | Source run IDs and the expected cohort SHA-256 |
| `research/annotation/p2_c1_4_xw_responses/` | Where the two FINAL exports are committed |
| `research/cohort/p2_c1_4_post_annotation_gate.py` | Stage 1 / Stage 2 logic (fail closed) |
| `research/cohort/validate_P2_C1_4_XW_responses.py` | Export validator |
| `research/cohort/construct_P2_C1_4_XW.py` | Raw-label lock, reliability report, X_W |
| `research/P2-C1.2/analysis/run_P2_C1_2_confirmatory_analysis.py` | Frozen M0 vs M1 analysis |
| `research/tests/test_P2_C1_4_post_annotation_gate.py` | End-to-end synthetic tests of the whole chain |
| `.github/workflows/p2-c1-4-reference-sql-features.yml` | Outcome-blind reference-SQL features (called by the gate; also runnable by hand) |
| `research/cohort/reference_sql_features_P2_C1_4.py` | Spider hardness and nesting depth from the pinned evaluator |

## Reference-SQL features (missingness audit)

The audit compares E2, E3/E4 and EVALUABLE on Spider **hardness** and on **nesting depth** of the reference SQL. Both are computed outcome-blind: the script reads only the frozen manifest, the Spider bundle and the pinned evaluator.

- **First run:** 2026-10-05, on this computer, over all 8,638 decisions. 8,637 got features.
- **CI reproduction:** run `37284300121` reproduced the CSV byte for byte.
- **The one unparseable decision:** `P2C14-CONF-001800`, the same decision the frozen E1 census marks `REFERENCE_SQL_NOT_PARSEABLE`.
- **Expected CSV hash:** `5e1b2edb195adde12a74f05310a05eef84c3fd0c33c58d9f89e257eecb5a5b68`, recorded in the sources file. The CI job fails closed if its CSV differs.
- **Nesting depth:** the maximum depth of nested query blocks. It counts subqueries in WHERE, HAVING and ON, FROM-clause subqueries, and INTERSECT/UNION/EXCEPT branches.
- **Retention:** the Spider bundle artifact must stay alive too. The retention refresh now re-uploads it, and `spider_source_run_id` in the sources file must point at the latest refresh.
