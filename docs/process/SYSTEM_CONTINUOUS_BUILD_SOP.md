# System Continuous Build SOP

## 1. Module Purpose
The System Continuous Build module governs automated generation and continuous improvement for both agent sets.

- Shipboard Execution Agent Set: runtime execution and control responsiveness.
- Shore Supervision Agent Set: supervision, policy constraints, and governance.
- Continuous Build Module: cadence, KPIs, automation loop, and hourly reporting.

## 2. Cadence Contract
- Marine researcher: every 15 minutes, external knowledge feedback to architect.
- Architect: every 30 minutes, design delta and development handoff.
- Developer: every 10 minutes, code progress update.
- QA: every 15 minutes, test execution and test authoring update.
- Deploy engineer: every 60 minutes, deployment cycle and issue feedback.
- Hourly summary: every 60 minutes, metrics report to command side.

## 3. KPI Contract
### Marine researcher KPI
- At least 4 external knowledge updates per hour.
- Every update must have explicit handoff to architect.
- Source quality must be actionable to design or rule model.

### Architect KPI
- At least 2 architecture/design increments per hour.
- Every increment must produce a concrete dev task package.
- No unresolved design blocker older than 30 minutes.

### Developer KPI
- At least 6 progress updates per hour.
- Code delta or blocker must be explicit in each update.
- No no-delta idle window longer than 20 minutes.

### QA KPI
- At least 4 QA updates per hour.
- Each update must include executed case status and authored/updated case status.
- Regression defects must be fed back to development immediately.

### Deploy KPI
- 1 deployment attempt per hour.
- Deployment success rate tracked continuously.
- Any deployment failure must be handed to development in same cycle.

## 4. Automation Scripts
- scripts/system_continuous_build_loop.sh
  - Runs the full cadence loop and writes logs.
- scripts/hourly_status_report.sh
  - Generates hourly status report including code increment, test case inventory, deployment success rate, and cadence health.

## 5. Runtime Commands
Start continuous build loop:

```bash
bash scripts/system_continuous_build_loop.sh
```

Generate one hourly report on demand:

```bash
bash scripts/hourly_status_report.sh
```

## 6. Marine Knowledge Feed Integration
If OpenClaw marine engineer agent command is available, set MARINE_FEED_CMD before loop startup:

```bash
export MARINE_FEED_CMD="openclaw ask marine_engineer --prompt 'Provide latest maritime tech/regulatory update for architecture handoff'"
bash scripts/system_continuous_build_loop.sh
```

If not configured, loop uses fallback local summary and still enforces cadence.

## 7. Evidence Paths
- Continuous build log: logs/team_logs/system_continuous_build.log
- Hourly reports: reports/status/HOURLY_STATUS_REPORT_*.md
