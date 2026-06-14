#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${CAPITAL_ENV_FILE:-$HOME/.capital-daily-research.env}"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

: "${CAPITAL_REPO_URL:=https://github.com/refcell/capital.git}"
: "${CAPITAL_REPO_DIR:=$HOME/src/capital}"
: "${CAPITAL_LOG_DIR:=$HOME/var/log/capital}"
HERMES_SKILLS_DEFAULT='capital-research'
: "${CAPITAL_TIMEZONE:=America/New_York}"
: "${HERMES_TOOLSETS:=browser,terminal,file,skills}"
: "${HERMES_SKILLS:=$HERMES_SKILLS_DEFAULT}"
: "${HERMES_PROVIDER:=}"
: "${HERMES_MODEL:=}"
: "${DAILY_RESEARCH_DRY_RUN:=1}"

EQUITY_RESEARCH_PROMPT_TEMPLATE='In the capital repo, perform only the research-report step for %s. Use the local capital-research skill, current public sources, and the local research template. Create or update research/%s.md only. Do not modify projections, models, or unrelated files. Do not commit or push; the wrapper script owns commits.'
DCF_MODEL_PROMPT_TEMPLATE='In the capital repo, perform only the workbook-model step for %s. Use the local capital-research skill and the repo\''s workbook style to create the valuation workbook under models/. Do not modify research, projections, or unrelated files. Do not commit or push; the wrapper script owns commits.'
PROJECTION_PROMPT_TEMPLATE='In the capital repo, perform only the projection-sheet step for %s. Create or update projections/%s.md using current public estimates, current market data, the local research report, the local workbook, and projections/README.md guidance. Leave unrelated files untouched. Do not commit or push; the wrapper script owns commits.'

export TZ="$CAPITAL_TIMEZONE"
mkdir -p "$CAPITAL_LOG_DIR" "$CAPITAL_REPO_DIR/automation/state"

LOCK_DIR="$CAPITAL_REPO_DIR/automation/state/daily-company-research.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another daily-company-research run is already active" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR"' EXIT

cd "$CAPITAL_REPO_DIR"

require_clean() {
  if [ -n "$(git status --porcelain)" ]; then
    git status --short
    echo "worktree is dirty; aborting" >&2
    exit 1
  fi
}

run_hermes() {
  local prompt="$1"
  local cmd=(hermes chat --toolsets "$HERMES_TOOLSETS" -s "$HERMES_SKILLS")
  if [ -n "$HERMES_PROVIDER" ]; then
    cmd+=(--provider "$HERMES_PROVIDER")
  fi
  if [ -n "$HERMES_MODEL" ]; then
    cmd+=(--model "$HERMES_MODEL")
  fi
  cmd+=(-q "$prompt")
  "${cmd[@]}"
}

render_prompt() {
  local template="$1"
  shift
  printf "$template" "$@"
}

commit_exact() {
  local message="$1"
  shift

  git add -- "$@"
  if git diff --cached --quiet; then
    echo "nothing staged for: $message" >&2
    exit 1
  fi
  git commit -m "$message"
}

commit_staged() {
  local message="$1"
  if git diff --cached --quiet; then
    echo "nothing staged for: $message" >&2
    exit 1
  fi
  git commit -m "$message"
}

assert_only_paths() {
  local allowed_prefix="$1"
  local bad_status
  bad_status="$(git status --porcelain | awk -v p="$allowed_prefix" '
    {
      path = substr($0, 4)
      if (index(path, p) != 1) print
    }
  ')"
  if [ -n "$bad_status" ]; then
    echo "unexpected changed files:" >&2
    echo "$bad_status" >&2
    exit 1
  fi
}

echo "daily company research run started at $(date -Is)"

git checkout main
git fetch origin
git pull --ff-only origin main
require_clean

TICKER="$(python3 scripts/pick-company-ticker.py)"
if [ -z "$TICKER" ]; then
  echo "ticker picker returned empty ticker" >&2
  exit 1
fi

echo "selected ticker: $TICKER"

if [ "$DAILY_RESEARCH_DRY_RUN" = "1" ]; then
  echo "dry run enabled; exiting before Hermes skill execution"
  exit 0
fi

run_hermes "$(render_prompt "$EQUITY_RESEARCH_PROMPT_TEMPLATE" "$TICKER")"
assert_only_paths "research/$TICKER.md"
commit_exact "research: add $TICKER report" "research/$TICKER.md"

run_hermes "$(render_prompt "$DCF_MODEL_PROMPT_TEMPLATE" "$TICKER")"
assert_only_paths "models/"
MODEL_FILES="$(git status --porcelain | awk '{print substr($0, 4)}' | grep '^models/.*\.xlsx$' || true)"
if [ -z "$MODEL_FILES" ]; then
  git status --short
  echo "DCF step did not create or modify a models/*.xlsx workbook" >&2
  exit 1
fi
while IFS= read -r model_file; do
  [ -n "$model_file" ] || continue
  git add -- "$model_file"
done <<< "$MODEL_FILES"
commit_staged "model: add $TICKER DCF"

run_hermes "$(render_prompt "$PROJECTION_PROMPT_TEMPLATE" "$TICKER")"
assert_only_paths "projections/$TICKER.md"
commit_exact "projection: add $TICKER projection" "projections/$TICKER.md"
require_clean

git push origin main
python3 scripts/pick-company-ticker.py --mark-seen "$TICKER"

echo "daily company research run finished at $(date -Is)"
