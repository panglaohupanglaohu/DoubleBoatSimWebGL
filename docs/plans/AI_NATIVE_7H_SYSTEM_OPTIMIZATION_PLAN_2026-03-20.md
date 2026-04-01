# AI Native 7-Hour System Optimization Sprint (2026-03-20)

## Goal
Build a continuous, non-stop 7-hour optimization run with UI-first execution, full AI Native alignment, complete feature hardening, and full test pass.

## Definition of Done
- UI cockpit is schema-tolerant, status-aware, and operational when partial backend data is missing.
- SVESSEL + AI Native endpoints are behaviorally consistent (request/response semantics aligned).
- Integration tests cover newly added AI Native endpoints and critical response contracts.
- Full automated test suite runs successfully in configured environment.
- Final report includes changed files, validation evidence, residual risks, and next-step backlog.

## Execution Rules (AI Native)
- Short feedback loop: implement -> validate -> adapt every 20-30 minutes.
- Telemetry-first: every new UI block reads from normalized model, never raw endpoint payload.
- Contract-first: API response keys normalized and backward-compatible.
- Safety-first: do not regress existing routes, command loop, or decision pipeline.

## 7-Hour Timeline

### Hour 1 - UI Baseline and Observability (UI-first)
- Refactor cockpit UI data ingestion via normalization layer.
- Add metric tone states (ok/warn/danger) and alert emphasis.
- Keep graceful fallback for absent fields.
- Validation: manual refresh path and zero JS runtime errors.

### Hour 2 - API Contract Alignment
- Align autonomy transition and MASS/LR semantics.
- Align link/PHM/cyber payload keys with cockpit consumption contract.
- Add backward-compatible aliases where needed.
- Validation: endpoint smoke tests and response shape checks.

### Hour 3 - Decision Pipeline Consistency
- Ensure decision orchestrator reads normalized priority/link values.
- Verify PHM maintenance priority handling supports enum/string safely.
- Ensure package summary fields are consistent and non-null where required.
- Validation: unit assertions for package fields.

### Hour 4 - Integration Test Expansion
- Add tests for:
  - /api/v1/ai-native/autonomy/status
  - /api/v1/ai-native/autonomy/transition
  - /api/v1/ai-native/phm/status
  - /api/v1/ai-native/phm/maintenance-plan
  - /api/v1/ai-native/ship-shore/status
  - /api/v1/ai-native/cybersecurity/status
- Validate status code, payload structure, and key type guarantees.

### Hour 5 - Full Regression and Failure Burn-down
- Run full pytest suite with controlled plugin isolation.
- Fix regressions in priority order: API correctness -> runtime safety -> presentation.
- Re-run until stable green.

### Hour 6 - Performance and Stability Sweep
- Run critical API response-time checks.
- Confirm dashboard refresh loop handles partial endpoint failure.
- Validate no uncaught errors in command/analytics loops.

### Hour 7 - Closure and Handover
- Produce execution report:
  - completed work
  - test evidence
  - known gaps and impact
  - next-iteration backlog
- Prepare merge-ready change summary.

## Immediate Start Sequence (already initiated)
1. Hour 1 UI schema normalization and status-tone mapping.
2. Hour 2 API contract hardening.
3. Hour 4 integration tests for new endpoints.
4. Hour 5 full regression run.

## Risk Controls
- If external pytest plugins fail, run with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 and record rationale.
- Never block cockpit refresh on one endpoint failure (Promise.allSettled strategy retained).
- Keep API compatibility by adding aliases instead of breaking key renames.
