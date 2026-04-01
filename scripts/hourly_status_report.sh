#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/panglaohu/Downloads/DoubleBoatClawSystem"
cd "$PROJECT_DIR"

REPORT_DIR="$PROJECT_DIR/reports/status"
LOG_DIR="$PROJECT_DIR/logs/team_logs"
mkdir -p "$REPORT_DIR" "$LOG_DIR"

NOW_HUMAN="$(date '+%Y-%m-%d %H:%M:%S')"
NOW_FILE="$(date '+%Y%m%d_%H%M%S')"
REPORT_FILE="$REPORT_DIR/HOURLY_STATUS_REPORT_${NOW_FILE}.md"

# Code increment (last 1 hour)
CODE_SUMMARY="$(git log --since='1 hour ago' --pretty=tformat: --numstat -- . ':(exclude)venv' | awk 'NF==3 {ins+=$1; del+=$2; files+=1} END {printf("files=%d, +%d/-%d", files, ins, del)}')"
if [[ -z "$CODE_SUMMARY" ]]; then
  CODE_SUMMARY="files=0, +0/-0"
fi

# Test case inventory
TEST_CASE_TOTAL="$(rg -n '^\s*def\s+test_' tests 2>/dev/null | wc -l | tr -d ' ')"
UNIT_TEST_FILES="$(find tests/unit -type f -name 'test_*.py' 2>/dev/null | wc -l | tr -d ' ')"
INTEG_TEST_FILES="$(find tests/integration -type f -name 'test_*.py' 2>/dev/null | wc -l | tr -d ' ')"

# Deployment success rate from continuous build log (last 24h)
BUILD_LOG="$LOG_DIR/system_continuous_build.log"
DEPLOY_OK=0
DEPLOY_FAIL=0
if [[ -f "$BUILD_LOG" ]]; then
  DEPLOY_OK="$(grep -c 'DEPLOY_SUCCESS' "$BUILD_LOG" || true)"
  DEPLOY_FAIL="$(grep -c 'DEPLOY_FAIL' "$BUILD_LOG" || true)"
fi
TOTAL_DEPLOY=$((DEPLOY_OK + DEPLOY_FAIL))
if [[ "$TOTAL_DEPLOY" -gt 0 ]]; then
  DEPLOY_RATE="$(awk -v ok="$DEPLOY_OK" -v total="$TOTAL_DEPLOY" 'BEGIN {printf("%.2f", (ok/total)*100)}')%"
else
  DEPLOY_RATE="N/A"
fi

# Team cadence checks from last window
RESEARCH_FEEDBACK_15M="MISSING"
ARCH_DESIGN_30M="MISSING"
DEV_PROGRESS_10M="MISSING"
QA_PROGRESS_15M="MISSING"

if [[ -f "$BUILD_LOG" ]]; then
  grep -q 'MARINE_FEEDBACK' "$BUILD_LOG" && RESEARCH_FEEDBACK_15M="OK"
  grep -q 'ARCHITECT_DESIGN' "$BUILD_LOG" && ARCH_DESIGN_30M="OK"
  grep -q 'DEV_PROGRESS' "$BUILD_LOG" && DEV_PROGRESS_10M="OK"
  grep -q 'QA_PROGRESS' "$BUILD_LOG" && QA_PROGRESS_15M="OK"
fi

cat > "$REPORT_FILE" <<EOF
# Hourly Status Report - $NOW_HUMAN

## 1. Code Increment
- Last 1h: $CODE_SUMMARY

## 2. Test Metrics
- Total test cases (def test_): $TEST_CASE_TOTAL
- Unit test files: $UNIT_TEST_FILES
- Integration test files: $INTEG_TEST_FILES

## 3. Deployment Metrics
- Deployment success count: $DEPLOY_OK
- Deployment fail count: $DEPLOY_FAIL
- Deployment success rate: $DEPLOY_RATE

## 4. Continuous Build Cadence Check
- Marine researcher (15m network feedback): $RESEARCH_FEEDBACK_15M
- Architect (30m design output): $ARCH_DESIGN_30M
- Developer (10m code progress): $DEV_PROGRESS_10M
- QA (15m test progress): $QA_PROGRESS_15M

## 5. KPI Watch
- Researcher KPI: Every 15m external knowledge feedback delivered to architect.
- Architect KPI: Every 30m architecture/design increment and task handoff to dev.
- Dev KPI: Every 10m code delta or blocker update, no idle window > 20m.
- QA KPI: Every 15m test execution + test authoring status.
- Deploy KPI: Hourly deployment attempt + defect feedback loop to dev.

## 6. Evidence
- Continuous build log: logs/team_logs/system_continuous_build.log
- Generated at: $NOW_HUMAN
EOF

echo "[HOURLY_REPORT] $NOW_HUMAN -> $REPORT_FILE" | tee -a "$BUILD_LOG"
echo "$REPORT_FILE"