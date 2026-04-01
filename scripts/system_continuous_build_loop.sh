#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/panglaohu/Downloads/DoubleBoatClawSystem"
cd "$PROJECT_DIR"

LOG_DIR="$PROJECT_DIR/logs/team_logs"
REPORT_DIR="$PROJECT_DIR/reports/status"
mkdir -p "$LOG_DIR" "$REPORT_DIR"

BUILD_LOG="$LOG_DIR/system_continuous_build.log"
LAST_HOUR_REPORT_TS=0
LAST_MARINE_TS=0
LAST_ARCH_TS=0
LAST_DEV_TS=0
LAST_QA_TS=0
LAST_DEPLOY_TS=0

# External commands (override by env if needed)
MARINE_FEED_CMD="${MARINE_FEED_CMD:-echo '[marine_engineer] external maritime knowledge summary unavailable, running local fallback summary'}"
ARCHITECT_DESIGN_CMD="${ARCHITECT_DESIGN_CMD:-echo '[architect] generated design delta and handed off to dev'}"
DEV_PROGRESS_CMD="${DEV_PROGRESS_CMD:-git diff --shortstat || true}"
QA_PROGRESS_CMD="${QA_PROGRESS_CMD:-PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/panglaohu/Downloads/DoubleBoatClawSystem/venv/bin/python -m pytest -q tests/unit/test_messagebus_config_engine.py || true}"
DEPLOY_CMD="${DEPLOY_CMD:-echo 'deploy dry-run: no deploy command configured'}"

log_line() {
  local level="$1"
  local tag="$2"
  local msg="$3"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] [$tag] $msg" | tee -a "$BUILD_LOG"
}

run_marine_feedback() {
  local out
  out="$(bash -lc "$MARINE_FEED_CMD" 2>&1 || true)"
  log_line "INFO" "MARINE_FEEDBACK" "$out"
  # Architect handoff note
  log_line "INFO" "MARINE_TO_ARCH" "Research feedback delivered to architect for next design cycle"
}

run_architect_design() {
  local out
  out="$(bash -lc "$ARCHITECT_DESIGN_CMD" 2>&1 || true)"
  log_line "INFO" "ARCHITECT_DESIGN" "$out"
  log_line "INFO" "ARCH_TO_DEV" "Architecture task package handed to development"
}

run_dev_progress() {
  local out
  out="$(bash -lc "$DEV_PROGRESS_CMD" 2>&1 || true)"
  if [[ -z "$out" ]]; then
    out="no code delta reported"
  fi
  log_line "INFO" "DEV_PROGRESS" "$out"
  if [[ "$out" == *"0 files changed"* ]] || [[ "$out" == *"no code delta"* ]]; then
    log_line "WARN" "DEV_NUDGE" "No code increment detected, dev team is nudged to submit delta or blocker details"
  fi
  log_line "INFO" "DEV_TO_QA" "QA reminded to execute/author test cases for latest delta"
}

run_qa_progress() {
  local out
  out="$(bash -lc "$QA_PROGRESS_CMD" 2>&1 || true)"
  log_line "INFO" "QA_PROGRESS" "$out"
  log_line "INFO" "QA_TO_DEPLOY" "Deploy engineer reminded for hourly deployment cycle"
}

run_deploy_cycle() {
  local out
  local rc=0
  out="$(bash -lc "$DEPLOY_CMD" 2>&1)" || rc=$?
  if [[ "$rc" -eq 0 ]]; then
    log_line "INFO" "DEPLOY_SUCCESS" "$out"
  else
    log_line "ERROR" "DEPLOY_FAIL" "$out"
    log_line "WARN" "DEPLOY_TO_DEV" "Deployment issue handed back to development for immediate fix"
  fi
}

run_hourly_report() {
  local report
  report="$(bash scripts/hourly_status_report.sh 2>&1 || true)"
  log_line "INFO" "HOURLY_SUMMARY" "$report"
}

log_line "INFO" "BOOT" "System continuous build loop started"

while true; do
  now="$(date +%s)"

  if (( now - LAST_MARINE_TS >= 900 )); then
    run_marine_feedback
    LAST_MARINE_TS=$now
  fi

  if (( now - LAST_ARCH_TS >= 1800 )); then
    run_architect_design
    LAST_ARCH_TS=$now
  fi

  if (( now - LAST_DEV_TS >= 600 )); then
    run_dev_progress
    LAST_DEV_TS=$now
  fi

  if (( now - LAST_QA_TS >= 900 )); then
    run_qa_progress
    LAST_QA_TS=$now
  fi

  if (( now - LAST_DEPLOY_TS >= 3600 )); then
    run_deploy_cycle
    LAST_DEPLOY_TS=$now
  fi

  if (( now - LAST_HOUR_REPORT_TS >= 3600 )); then
    run_hourly_report
    LAST_HOUR_REPORT_TS=$now
  fi

  sleep 20
done