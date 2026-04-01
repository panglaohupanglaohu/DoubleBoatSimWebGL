# Bug Report: process_event status 被覆盖

## Bug: process_event 返回的 status 字段被 **result 覆盖

- **文件**: `src/backend/channels/autopilot_monitor.py`, `src/backend/channels/echo_sounder_monitor.py`
- **测试**: `tests/unit/test_autopilot_echo_sounder.py::TestAutopilotEvents::test_ap_process_event_update`, `tests/unit/test_autopilot_echo_sounder.py::TestEchoStatus::test_echo_process_event`
- **错误**: `process_event()` 意图返回 `{"status": "updated", ...}` 但实际返回 `{"status": "ok", ...}`
- **根因**: `return {"status": "updated", **result}` 中 `result` 字典包含 `{"status": "ok", ...}`，Python dict 展开时后面的 key 覆盖前面的，导致 `"updated"` 被 `"ok"` 覆盖
- **受影响代码**:
  - `autopilot_monitor.py` L130: `return {"status": "updated", **result}`
  - `echo_sounder_monitor.py` L130: `return {"status": "updated", **result}`
- **修复建议**: 改为 `result["status"] = "updated"; return result` 或 `return {**result, "status": "updated"}`
- **严重级别**: P2 — 不影响功能逻辑，但下游依赖 `status == "updated"` 判断的消费者会收到错误状态码
