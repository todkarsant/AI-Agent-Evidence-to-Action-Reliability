#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:?}"
DIAGNOSTIC_WORKFLOW="c4-2-3-exact-path-diagnostic.yml"
SMOKE_WORKFLOW="c4-2-3-evidence-capture-smoke.yml"
EVIDENCE_WORKFLOW="c4-2-3-evidence-capture12.yml"
MAX_AUTO_RETRIES=2
POLL_SECONDS=30

get_latest() {
  gh run list --repo "$REPO" --workflow "$1" --limit 5     --json databaseId,status,conclusion,headSha,createdAt,url
}

read_latest() {
  id="$(echo "$runs" | jq -r '.[0].databaseId // empty')"
  status="$(echo "$runs" | jq -r '.[0].status // empty')"
  conclusion="$(echo "$runs" | jq -r '.[0].conclusion // empty')"
  latest_sha="$(echo "$runs" | jq -r '.[0].headSha // empty')"
}

runs="$(get_latest "$DIAGNOSTIC_WORKFLOW")"
echo "$runs" | jq .
read_latest

if [[ -z "$id" ]]; then
  echo "No diagnostic run exists. Dispatching one and attaching to it."
  gh workflow run "$DIAGNOSTIC_WORKFLOW" --repo "$REPO" --ref main
  for _ in {1..10}; do
    sleep 3
    runs="$(get_latest "$DIAGNOSTIC_WORKFLOW")"
    read_latest
    [[ -n "$id" ]] && break
  done
fi

if [[ -z "$id" ]]; then
  echo "Diagnostic dispatch was accepted but its run could not yet be resolved."
  exit 0
fi

while [[ "$status" != "completed" ]]; do
  echo "Diagnostic run $id is active ($status). Polling again in ${POLL_SECONDS}s."
  sleep "$POLL_SECONDS"
  runs="$(get_latest "$DIAGNOSTIC_WORKFLOW")"
  read_latest
done

echo "Diagnostic run $id reached terminal state: $conclusion"

if [[ "$conclusion" == "success" ]]; then
  echo "C.4.2.3 exact-path diagnostic succeeded. Mandatory smoke-test gate precedes C.4.2.3-D actual use."

  smoke_runs="$(get_latest "$SMOKE_WORKFLOW")"
  smoke_id="$(echo "$smoke_runs" | jq -r '.[0].databaseId // empty')"
  smoke_status="$(echo "$smoke_runs" | jq -r '.[0].status // empty')"
  smoke_conclusion="$(echo "$smoke_runs" | jq -r '.[0].conclusion // empty')"
  smoke_sha="$(echo "$smoke_runs" | jq -r '.[0].headSha // empty')"
  # Smoke validity is tied to the evidence-capture implementation it exercised.
  # Controller-only changes after the smoke do not invalidate that machinery test.
  changed_files="$(gh api "repos/$REPO/compare/$smoke_sha...main" --paginate -q '.files[].filename' || true)"
  invalidating=0
  while IFS= read -r changed; do
    [[ -z "$changed" ]] && continue
    case "$changed" in
      .github/workflows/c4-2-3-evidence-capture12.yml|research/spider_benchmark/*|research/deterministic_solver/*|data/manifests/C4_2_3B_PILOT12_CASES.json)
        invalidating=1 ;;
    esac
  done <<< "$changed_files"

  if [[ -z "$smoke_id" || "$smoke_conclusion" != "success" || "$invalidating" -eq 1 ]]; then
    echo "Smoke test is absent, failed, or invalidated by evidence-capture changes. Dispatching mandatory smoke test and stopping before actual evidence capture."
    gh workflow run "$SMOKE_WORKFLOW" --repo "$REPO" --ref main
    for _ in {1..10}; do
      sleep 3
      smoke_runs="$(get_latest "$SMOKE_WORKFLOW")"
      smoke_id="$(echo "$smoke_runs" | jq -r '.[0].databaseId // empty')"
      smoke_status="$(echo "$smoke_runs" | jq -r '.[0].status // empty')"
      smoke_conclusion="$(echo "$smoke_runs" | jq -r '.[0].conclusion // empty')"
      [[ -n "$smoke_id" ]] && break
    done
    if [[ -z "$smoke_id" ]]; then
      echo "Smoke dispatch accepted but run could not be resolved; controller will resume on its next trigger."
      exit 0
    fi
  fi

  if [[ "$smoke_status" != "completed" ]]; then
    echo "Smoke test $smoke_id is active ($smoke_status). Polling it; no actual evidence capture will start."
    while [[ "$smoke_status" != "completed" ]]; do
      sleep "$POLL_SECONDS"
      smoke_runs="$(get_latest "$SMOKE_WORKFLOW")"
      smoke_status="$(echo "$smoke_runs" | jq -r '.[0].status // empty')"
      smoke_conclusion="$(echo "$smoke_runs" | jq -r '.[0].conclusion // empty')"
      echo "Smoke test $smoke_id status=$smoke_status conclusion=$smoke_conclusion"
    done
  fi

  if [[ "$smoke_conclusion" != "success" ]]; then
    echo "Mandatory smoke test $smoke_id failed. Actual C.4.2.3-D evidence capture remains blocked."
    title="Research controller: evidence-capture smoke-test failure #$smoke_id"
    existing="$(gh issue list --repo "$REPO" --state open --search "in:title $title" --json number)"
    if [[ "$(echo "$existing" | jq length)" -eq 0 ]]; then
      gh issue create --repo "$REPO" --title "$title" --body "Mandatory pre-use smoke test failed for current main.

Run: https://github.com/$REPO/actions/runs/$smoke_id

No C.4.2.3-D actual evidence capture was started. Preserve the failure and fix the smoke-test implementation before proceeding."
    fi
    exit 0
  fi

  echo "Mandatory smoke test $smoke_id passed on current main. Actual C.4.2.3-D qualification may now proceed."

  evidence_runs="$(get_latest "$EVIDENCE_WORKFLOW")"
  evidence_id="$(echo "$evidence_runs" | jq -r '.[0].databaseId // empty')"
  evidence_status="$(echo "$evidence_runs" | jq -r '.[0].status // empty')"
  evidence_conclusion="$(echo "$evidence_runs" | jq -r '.[0].conclusion // empty')"
  evidence_sha="$(echo "$evidence_runs" | jq -r '.[0].headSha // empty')"
  current_sha="$(gh api "repos/$REPO/commits/main" -q .sha)"

  if [[ -n "$evidence_id" && "$evidence_sha" == "$current_sha" ]]; then
    echo "Existing C.4.2.3-D run $evidence_id on current main: status=$evidence_status conclusion=$evidence_conclusion"
    if [[ "$evidence_status" != "completed" ]]; then
      while [[ "$evidence_status" != "completed" ]]; do
        sleep "$POLL_SECONDS"
        evidence_runs="$(get_latest "$EVIDENCE_WORKFLOW")"
        evidence_status="$(echo "$evidence_runs" | jq -r '.[0].status // empty')"
        evidence_conclusion="$(echo "$evidence_runs" | jq -r '.[0].conclusion // empty')"
        echo "C.4.2.3-D run $evidence_id status=$evidence_status conclusion=$evidence_conclusion"
      done
    fi
    if [[ "$evidence_conclusion" == "success" ]]; then
      echo "C.4.2.3-D succeeded. Generating the frozen W1-W7 human-annotation cohort before the human-validation boundary."
      mkdir -p /tmp/c4_2_4a
      gh run download "$evidence_id" --repo "$REPO" -n c4-2-3-evidence-capture12 -D /tmp/c4_2_4a
      test -f /tmp/c4_2_4a/evidence_capture_pilot12.json
      source_sha="$(sha256sum /tmp/c4_2_4a/evidence_capture_pilot12.json | cut -d' ' -f1)"
      echo "Current qualified source evidence SHA-256: $source_sha"
      echo "Qualified source run: $evidence_id"
      python research/methodological_gates/generate_C4_2_4A_witness_packets_v2.py \
        --evidence /tmp/c4_2_4a/evidence_capture_pilot12.json \
        --schema-fixture data/fixtures/C4_2_4A_SPIDER12_SCHEMA_FIXTURE.json \
        --manifest data/manifests/C4_2_3B_PILOT12_CASES.json \
        --out research/annotation_packets
      git config user.name "research-pipeline-bot"
      git config user.email "research-pipeline-bot@users.noreply.github.com"
      git add research/annotation_packets
      if ! git diff --cached --quiet; then
        git commit -m "research: generate frozen W1-W7 annotation cohort"
        git push
        echo "Frozen W1-W7 cohort committed; stop controller before issuing any further scientific action."
      else
        echo "Frozen W1-W7 cohort already present and deterministic; no packet mutation."
      fi
      echo "C.4.2.3-D succeeded. C.4.2.4-A requires genuinely independent human raters and is therefore not auto-executable."
      title="C.4.2.4-A — Human validation required before X_W freeze"
      existing_issue="$(gh issue list --repo "$REPO" --state open --search "in:title $title" --json number)"
      if [[ "$(echo "$existing_issue" | jq length)" -eq 0 ]]; then
        gh issue create --repo "$REPO" --title "$title" --body "Research progression is blocked at C.4.2.4-A pending two genuinely independent outcome-blinded human annotation passes.

Completed:
- C.4.2.3-C: limited-scope exact-path qualification; global determinism remains unestablished.
- C.4.2.3-D: current-main evidence-capture qualification succeeded in run $evidence_id.

Required before P2-C1.2 confirmatory modeling:
1. Two independent raters complete frozen packets.
2. Raw annotations are locked unchanged.
3. Obligation-level agreement statistics and contingency tables are calculated.
4. The predefined disagreement/codebook-failure audit is completed.
5. Any codebook revision creates a new version/cohort.

Scientific safety boundary: no automatic changes to scientific code, data, model parameters, seeds, annotations, or gate verdicts."
      fi
    else
      echo "C.4.2.3-D failed on current main. Preserve failure and do not advance."
      title="Research controller: C.4.2.3-D evidence-capture failure #$evidence_id"
      existing="$(gh issue list --repo "$REPO" --state open --search "in:title $title" --json number)"
      if [[ "$(echo "$existing" | jq length)" -eq 0 ]]; then
        gh issue create --repo "$REPO" --title "$title" --body "Automated research-progression controller detected failure of the predefined C.4.2.3-D evidence-capture qualification on current main.

Run: https://github.com/$REPO/actions/runs/$evidence_id

Safety boundary: no scientific code, benchmark data, model parameters, seeds, annotations, or gate verdicts were modified automatically."
      fi
    fi
    exit 0
  fi

  echo "No current-main C.4.2.3-D run exists. Dispatching the predefined evidence-capture qualification."
  gh workflow run "$EVIDENCE_WORKFLOW" --repo "$REPO" --ref main
  for _ in {1..10}; do
    sleep 3
    evidence_runs="$(get_latest "$EVIDENCE_WORKFLOW")"
    evidence_id="$(echo "$evidence_runs" | jq -r '.[0].databaseId // empty')"
    evidence_status="$(echo "$evidence_runs" | jq -r '.[0].status // empty')"
    evidence_conclusion="$(echo "$evidence_runs" | jq -r '.[0].conclusion // empty')"
    [[ -n "$evidence_id" ]] && break
  done
  if [[ -z "$evidence_id" ]]; then
    echo "Evidence-capture dispatch accepted but run could not be resolved; controller will resume on its next trigger."
    exit 0
  fi
  while [[ "$evidence_status" != "completed" ]]; do
    echo "C.4.2.3-D run $evidence_id is active ($evidence_status). Polling every ${POLL_SECONDS}s."
    sleep "$POLL_SECONDS"
    evidence_runs="$(get_latest "$EVIDENCE_WORKFLOW")"
    evidence_status="$(echo "$evidence_runs" | jq -r '.[0].status // empty')"
    evidence_conclusion="$(echo "$evidence_runs" | jq -r '.[0].conclusion // empty')"
  done
  echo "C.4.2.3-D run $evidence_id reached terminal state: $evidence_conclusion"
  exit 0
fi

current_sha="$(gh api "repos/$REPO/commits/main" -q .sha)"

if [[ "$latest_sha" != "$current_sha" ]]; then
  echo "Latest diagnostic failed on an older revision; dispatching current revision."
  gh workflow run "$DIAGNOSTIC_WORKFLOW" --repo "$REPO" --ref main
  exit 0
fi

log="$(gh run view "$id" --repo "$REPO" --log-failed 2>&1 || true)"
printf '%s\n' "$log" > /tmp/diagnostic_failure.log

if grep -Eqi "command not found|exit code 127|connection reset|connection refused|timed out|rate limit|502|503|504|runner.*failed|no space left|network.*unavailable" /tmp/diagnostic_failure.log; then
  failures="$(gh run list --repo "$REPO" --workflow "$DIAGNOSTIC_WORKFLOW" --limit 20 --json conclusion,headSha     | jq --arg sha "$current_sha" '[.[] | select(.conclusion=="failure" and .headSha==$sha)] | length')"

  if [[ "$failures" -lt "$MAX_AUTO_RETRIES" ]]; then
    echo "Known infrastructure failure on current revision; retry $((failures + 1))."
    gh workflow run "$DIAGNOSTIC_WORKFLOW" --repo "$REPO" --ref main
  else
    echo "Automatic retry guard reached."
  fi
  exit 0
fi

title="Research controller: unclassified diagnostic failure #$id"
existing="$(gh issue list --repo "$REPO" --state open --search "in:title $title" --json number)"
if [[ "$(echo "$existing" | jq length)" -eq 0 ]]; then
  gh issue create --repo "$REPO" --title "$title" --body "Automated controller detected an unclassified failure in the C.4.2.3 exact historical-path diagnostic.

Run: https://github.com/$REPO/actions/runs/$id

Safety boundary: no scientific code, benchmark data, model parameters, seeds, annotations, or gate verdicts are modified automatically for unclassified failures."
fi
