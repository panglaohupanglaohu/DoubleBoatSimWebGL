"""Tests for MarineDataCenterEnergyChannel — covers all 4 perspectives,
IoT, Skill/Policy, evolution, forecast, anomaly, what-if, drift tick,
and Musk five-step audit.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from channels.marine_datacenter_energy import (  # noqa: E402
    MarineDataCenterEnergyChannel,
    DCPerspective,
    PolicyKind,
    IoTKind,
)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if not asyncio.iscoroutine(coro) else asyncio.run(coro)


@pytest.fixture()
def ch():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    return c


# ── lifecycle ──
def test_initialize_seeds(ch):
    assert ch.devices and ch.sensors and ch.skills and ch.policies and ch.heritage
    assert ch.baseline_pue >= ch.target_pue


def test_shutdown(ch):
    assert ch.shutdown() is True


# ── status / four-view ──
def test_get_status(ch):
    st = ch.get_status()
    assert st["name"] == "marine_datacenter_energy"
    assert "current_pue" in st and "baseline_pue" in st


def test_four_view_overview(ch):
    fv = ch.four_view_overview()
    for k in ("device", "facility", "environment", "process"):
        assert k in fv


@pytest.mark.parametrize("p", list(DCPerspective))
def test_analyze_perspective(ch, p):
    res = ch.analyze_perspective(p)
    assert isinstance(res, dict) and res


# ── IoT ──
def test_hub_summary(ch):
    s = ch.hub_summary()
    assert isinstance(s, dict) and s
    assert "by_kind" in s or "plc_agents_online" in s


def test_ingest_sensor(ch):
    sid = next(iter(ch.sensors))
    r = ch.ingest_sensor(sid, 25.5)
    assert r["ok"] is True
    assert ch.sensors[sid].value == 25.5


def test_ingest_unknown_sensor(ch):
    r = ch.ingest_sensor("missing-id", 1.0)
    assert r["ok"] is False


# ── Skill / Policy ──
def test_add_and_reinforce_skill(ch):
    before = len(ch.skills)
    ch.add_skill("skl-test-x", "自定义_X", "trigger", "action")
    assert len(ch.skills) == before + 1
    ch.reinforce_skill("skl-test-x", success=True)
    assert ch.skills["skl-test-x"].confidence > 0


def test_apply_policy(ch):
    pid = next(iter(ch.policies))
    r = ch.apply_policy(pid)
    assert r["ok"] is True
    assert ch.policies[pid].applied is True


def test_apply_policy_unknown(ch):
    r = ch.apply_policy("does-not-exist")
    assert r["ok"] is False


# ── closed-loop / evolve ──
def test_closed_loop_tick(ch):
    r = ch.closed_loop_tick()
    assert "applied" in r or "ok" in r


def test_evolve(ch):
    r = ch.evolve("测试遗产", "test", -0.01, 1.0)
    assert "round" in r or "ok" in r


def test_heritage_ledger(ch):
    h = ch.heritage_ledger()
    assert isinstance(h, list)


# ── PUE history / sankey / recommend / benchmark / cost ──
def test_pue_history(ch):
    hist = ch.get_pue_history(limit=10)
    assert isinstance(hist, list)


def test_energy_sankey(ch):
    s = ch.energy_sankey()
    assert "nodes" in s and "links" in s


def test_recommend_actions(ch):
    recs = ch.recommend_actions(top_n=2)
    assert isinstance(recs, list) and len(recs) <= 2


def test_benchmark(ch):
    b = ch.benchmark()
    assert "industry_avg_pue" in b


def test_cost_summary(ch):
    c = ch.cost_summary()
    assert "elec_price_cny_per_kwh" in c or "annual_cost_cny" in c


# ── devices ──
def test_list_devices(ch):
    devs = ch.list_devices()
    assert len(devs) == len(ch.devices)


def test_device_detail(ch):
    did = next(iter(ch.devices))
    d = ch.get_device_detail(did)
    assert d and d.get("device_id") == did


# ── auto loop / ai insight ──
def test_set_auto_loop(ch):
    r = ch.set_auto_loop(True, 30)
    assert r["enabled"] is True
    assert r["interval_s"] == 30


def test_ai_insight(ch):
    ins = ch.ai_insight("节能策略")
    assert ins["ok"] and ins["bullets"]


# ── NEW: forecast / anomalies / what-if / drift tick / musk audit ──
def test_forecast_pue(ch):
    f = ch.forecast_pue(hours=6, sample_step_min=60)
    assert f["horizon_hours"] == 6
    assert len(f["points"]) >= 6
    assert f["peak"]["pue"] >= f["valley"]["pue"]


def test_forecast_with_applied_policy(ch):
    pid = next(iter(p for p, v in ch.policies.items() if v.kind == PolicyKind.SAVE_OUTGO))
    ch.apply_policy(pid)
    f = ch.forecast_pue(hours=3, sample_step_min=60)
    assert f["applied_save_policies"] >= 1


def test_detect_anomalies(ch):
    a = ch.detect_anomalies()
    assert a["ok"] and "by_severity" in a
    assert a["total"] == len(a["anomalies"])


def test_detect_anomalies_with_overload(ch):
    d = next(iter(ch.devices.values()))
    d.cpu_util = 0.99
    a = ch.detect_anomalies()
    kinds = {x["kind"] for x in a["anomalies"]}
    assert "device_overload" in kinds


def test_what_if_with_policy(ch):
    pid = next(iter(ch.policies))
    r = ch.what_if([{"policy_id": pid, "fitness": 0.9, "capex_cny": 10000}])
    assert r["ok"] and r["scenario_count"] == 1
    assert r["projected_pue"] <= r["current_pue"]


def test_what_if_custom_scenario(ch):
    r = ch.what_if([{"delta_pue": -0.02, "delta_kwh_day": 5, "capex_cny": 1000, "title": "X"}])
    assert r["scenarios"][0]["title"] == "X"
    assert r["payback_years"] is not None


def test_what_if_empty(ch):
    r = ch.what_if([])
    assert r["scenario_count"] == 0
    assert r["projected_pue"] == ch.current_pue


def test_simulate_tick_grows_history(ch):
    n0 = len(ch.pue_history)
    for _ in range(5):
        ch.simulate_tick()
    assert len(ch.pue_history) >= n0 + 5


def test_simulate_tick_drift_bounded(ch):
    for _ in range(50):
        ch.simulate_tick()
    assert ch.target_pue * 0.95 <= ch.current_pue <= ch.baseline_pue + 0.06


def test_musk_five_step_audit(ch):
    a = ch.musk_five_step_audit()
    assert a["ok"]
    keys = a["steps"].keys()
    for k in ("1_question_requirements", "2_delete", "3_simplify_optimize",
              "4_accelerate_cycle", "5_automate"):
        assert k in keys


# ── async process_event ──
def test_process_event_status():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    r = asyncio.run(c.process_event({"type": "status"}))
    assert r["ok"] is True


def test_process_event_forecast():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    r = asyncio.run(c.process_event({"type": "forecast", "hours": 3, "step_min": 60}))
    assert r["ok"] and r["result"]["horizon_hours"] == 3


def test_process_event_anomalies():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    r = asyncio.run(c.process_event({"type": "anomalies"}))
    assert r["ok"] and "anomalies" in r["result"]


def test_process_event_what_if():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    r = asyncio.run(c.process_event({
        "type": "what_if",
        "scenarios": [{"delta_pue": -0.01, "delta_kwh_day": 1}],
    }))
    assert r["ok"] and r["result"]["scenario_count"] == 1


def test_process_event_simulate_tick():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    r = asyncio.run(c.process_event({"type": "simulate_tick"}))
    assert r["ok"] and r["result"]["history_size"] >= 1


def test_process_event_musk_audit():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    r = asyncio.run(c.process_event({"type": "musk_audit"}))
    assert r["ok"] and "steps" in r["result"]


def test_process_event_unknown():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    r = asyncio.run(c.process_event({"type": "nope"}))
    assert r["ok"] is False
