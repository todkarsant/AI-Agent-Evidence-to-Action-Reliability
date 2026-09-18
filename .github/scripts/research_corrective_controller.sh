#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:?}"
DIAGNOSTIC_WORKFLOW="c4-2-3-exact-path-diagnostic.yml"
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
  runs="$(get_latest)"
  read_latest
done

echo "Diagnostic run $id reached terminal state: $conclusion"

if [[ "$conclusion" == "success" ]]; then
  echo "C.4.2.3 exact-path diagnostic succeeded. Advancing only to the predefined C.4.2.3-D evidence-capture qualification."

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
      echo "C.4.2.3-D succeeded. C.4.2.4-A requires genuinely independent human raters and is therefore not auto-executable."
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
