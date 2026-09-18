#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:?}"
DIAGNOSTIC_WORKFLOW="c4-2-3-exact-path-diagnostic.yml"
MAX_AUTO_RETRIES=2

runs="$(gh run list --repo "$REPO" --workflow "$DIAGNOSTIC_WORKFLOW" --limit 5 --json databaseId,status,conclusion,headSha,createdAt,url)"
echo "$runs" | jq .

id="$(echo "$runs" | jq -r '.[0].databaseId // empty')"
status="$(echo "$runs" | jq -r '.[0].status // empty')"
conclusion="$(echo "$runs" | jq -r '.[0].conclusion // empty')"
latest_sha="$(echo "$runs" | jq -r '.[0].headSha // empty')"

if [[ -z "$id" ]]; then
  echo "No diagnostic run exists. Dispatching one."
  gh workflow run "$DIAGNOSTIC_WORKFLOW" --repo "$REPO" --ref main
  exit 0
fi

if [[ "$status" != "completed" ]]; then
  echo "Latest diagnostic is still running. No action."
  exit 0
fi

if [[ "$conclusion" == "success" ]]; then
  echo "Latest diagnostic succeeded. No action."
  exit 0
fi

current_sha="$(gh api "repos/$REPO/commits/main" -q .sha")

# Any failure from an older diagnostic revision must be re-evaluated against
# current main. This prevents a corrected harness from being blocked by stale
# failures while preserving the scientific result itself.
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
