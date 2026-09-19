#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:?}"
DIAGNOSTIC_WORKFLOW="c4-2-3-exact-path-diagnostic.yml"
SMOKE_WORKFLOW="c4-2-3-evidence-capture-smoke.yml"
EVIDENCE_WORKFLOW="c4-2-3-evidence-capture12.yml"
PACKET_SMOKE_WORKFLOW="c4-2-4a-packet-generation-smoke.yml"
PACKET_WORKFLOW="c4-2-4a-packet-generation.yml"
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
    smoke_dispatch_url="$(gh workflow run "$SMOKE_WORKFLOW" --repo "$REPO" --ref main)"
    smoke_id="${smoke_dispatch_url##*/}"
    test -n "$smoke_id"
    echo "Dispatched smoke test run $smoke_id."
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

  evidence_invalidating=0
  if [[ -n "$evidence_sha" ]]; then
    changed_files="$(gh api "repos/$REPO/compare/$evidence_sha...main" --paginate -q '.files[].filename' || true)"
    while IFS= read -r changed; do
      [[ -z "$changed" ]] && continue
      case "$changed" in
        .github/workflows/c4-2-3-evidence-capture12.yml|research/spider_benchmark/*|research/deterministic_solver/*|data/manifests/C4_2_3B_PILOT12_CASES.json)
          evidence_invalidating=1 ;;
      esac
    done <<< "$changed_files"
  fi

  if [[ -n "$evidence_id" && "$evidence_invalidating" -eq 0 ]]; then
    echo "Using qualified C.4.2.3-D run $evidence_id; later commits do not modify evidence-capture machinery."
    if [[ "$evidence_status" != "completed" ]]; then
      while [[ "$evidence_status" != "completed" ]]; do
        sleep "$POLL_SECONDS"
        evidence_status="$(gh run view "$evidence_id" --repo "$REPO" --json status -q .status)"
        evidence_conclusion="$(gh run view "$evidence_id" --repo "$REPO" --json conclusion -q .conclusion)"
        echo "C.4.2.3-D run $evidence_id status=$evidence_status conclusion=$evidence_conclusion"
      done
    fi
    if [[ "$evidence_conclusion" == "success" ]]; then
      echo "C.4.2.3-D is valid. Advancing to source-pinned W1-W7 cohort generation."
      provenance="$(git show main:research/annotation_packets/C4_2_4A_WITNESS_V2_PROVENANCE.md 2>/dev/null || true)"
      if grep -q "Source C.4.2.3-D run: $evidence_id" <<< "$provenance"; then
        packet_ready=1
      else
        packet_ready=0
      fi
      if [[ "$packet_ready" -eq 0 ]]; then
        packet_smoke_runs="$(get_latest "$PACKET_SMOKE_WORKFLOW")"
        packet_smoke_id="$(echo "$packet_smoke_runs" | jq -r '.[0].databaseId // empty')"
        packet_smoke_status="$(echo "$packet_smoke_runs" | jq -r '.[0].status // empty')"
        packet_smoke_conclusion="$(echo "$packet_smoke_runs" | jq -r '.[0].conclusion // empty')"
        if [[ -z "$packet_smoke_id" || "$packet_smoke_status" == "completed" ]]; then
          dispatch="$(gh workflow run "$PACKET_SMOKE_WORKFLOW" --repo "$REPO" --ref main -f source_run_id="$evidence_id")"
          packet_smoke_id="${dispatch##*/}"
          test -n "$packet_smoke_id"
          echo "Dispatched packet-generation smoke run $packet_smoke_id."
        fi
        while [[ "$packet_smoke_status" != "completed" ]]; do
          sleep "$POLL_SECONDS"
          packet_smoke_status="$(gh run view "$packet_smoke_id" --repo "$REPO" --json status -q .status)"
          packet_smoke_conclusion="$(gh run view "$packet_smoke_id" --repo "$REPO" --json conclusion -q .conclusion)"
          echo "Packet smoke run $packet_smoke_id status=$packet_smoke_status conclusion=$packet_smoke_conclusion"
        done
        if [[ "$packet_smoke_conclusion" != "success" ]]; then
          echo "Packet-generation smoke failed; actual W1-W7 cohort generation remains blocked."
          exit 0
        fi
        dispatch="$(gh workflow run "$PACKET_WORKFLOW" --repo "$REPO" --ref main -f source_run_id="$evidence_id")"
        packet_id="${dispatch##*/}"
        test -n "$packet_id"
        echo "Packet-generation smoke passed. Dispatched actual W1-W7 cohort run $packet_id."
        packet_status=""
        packet_conclusion=""
        while [[ "$packet_status" != "completed" ]]; do
          sleep "$POLL_SECONDS"
          packet_status="$(gh run view "$packet_id" --repo "$REPO" --json status -q .status)"
          packet_conclusion="$(gh run view "$packet_id" --repo "$REPO" --json conclusion -q .conclusion)"
          echo "Packet generation run $packet_id status=$packet_status conclusion=$packet_conclusion"
        done
        if [[ "$packet_conclusion" != "success" ]]; then
          echo "Actual W1-W7 cohort generation failed; human annotation remains blocked."
          exit 0
        fi
      fi
      title="C.4.2.4-A — Human validation required before X_W freeze"
      existing_issue="$(gh issue list --repo "$REPO" --state open --search "in:title $title" --json number)"
      if [[ "$(echo "$existing_issue" | jq length)" -eq 0 ]]; then
        gh issue create --repo "$REPO" --title "$title" --body "Research progression is blocked at C.4.2.4-A pending two genuinely independent outcome-blinded human annotation passes.

Completed:
- C.4.2.3-C: limited-scope exact-path qualification; global determinism remains unestablished.
- C.4.2.3-D: qualified evidence-capture run $evidence_id.
- W1-W7 packet-generation smoke test passed.
- W1-W7: new versioned blinded annotation cohort generated from source run $evidence_id with automated leakage/integrity checks and immutable provenance.

Required before P2-C1.2 confirmatory modeling:
1. Two independent raters complete frozen packets.
2. Raw annotations are locked unchanged.
3. Obligation-level agreement statistics and contingency tables are calculated.
4. The predefined disagreement/codebook-failure audit is completed.
5. Any codebook revision creates a new version/cohort.

Scientific safety boundary: no automatic changes to scientific code, data, model parameters, seeds, annotations, or gate verdicts."
      fi
    else
      echo "C.4.2.3-D failed; preserve failure and do not advance."
    fi
    exit 0
  fi

  echo "No valid qualified C.4.2.3-D run exists after evidence-machinery audit. Dispatching a new evidence-capture qualification."
  evidence_dispatch_url="$(gh workflow run "$EVIDENCE_WORKFLOW" --repo "$REPO" --ref main)"
  evidence_id="${evidence_dispatch_url##*/}"
  test -n "$evidence_id"
  echo "Dispatched C.4.2.3-D run $evidence_id."
  exit 0
fi

  echo "No current-main C.4.2.3-D run exists. Dispatching the predefined evidence-capture qualification."
  evidence_dispatch_url="$(gh workflow run "$EVIDENCE_WORKFLOW" --repo "$REPO" --ref main)"
  evidence_id="${evidence_dispatch_url##*/}"
  test -n "$evidence_id"
  echo "Dispatched C.4.2.3-D run $evidence_id."
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
