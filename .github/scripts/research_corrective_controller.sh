#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:?}"
DIAGNOSTIC_WORKFLOW="c4-2-3-exact-path-diagnostic.yml"
MAX_AUTO_RETRIES=2
POLL_SECONDS=30

get_latest() {
  gh run list --repo "$REPO" --workflow "$DIAGNOSTIC_WORKFLOW" --limit 5     --json databaseId,status,conclusion,headSha,createdAt,url
}

read_latest() {
  id="$(echo "$runs" | jq -r '.[0].databaseId // empty')"
  status="$(echo "$runs" | jq -r '.[0].status // empty')"
  conclusion="$(echo "$runs" | jq -r '.[0].conclusion // empty')"
  latest_sha="$(echo "$runs" | jq -r '.[0].headSha // empty')"
}

runs="$(get_latest)"
echo "$runs" | jq .
read_latest

if [[ -z "$id" ]]; then
  echo "No diagnostic run exists. Dispatching one and attaching to it."
  gh workflow run "$DIAGNOSTIC_WORKFLOW" --repo "$REPO" --ref main
  for _ in {1..10}; do
    sleep 3
    runs="$(get_latest)"
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
  echo "Latest diagnostic succeeded. Scientific result is preserved; no automatic methodological change."
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
