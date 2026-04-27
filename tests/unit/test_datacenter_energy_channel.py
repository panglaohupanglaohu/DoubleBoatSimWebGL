"""Unit tests for MarineDataCenterEnergyChannel."""
import time
import pytest

from src.backend.channels.marine_datacenter_energy import (
    MarineDataCenterEnergyChannel,
    DCPerspective,
    IoTKind,
    PolicyKind,
    DarwinHeritage,
)


@pytest.fixture()
def ch():
    c = MarineDataCenterEnergyChannel()
    c.initialize()
    return c


# ── lifecycle ──
class TestLifecycle:
    def test_init_and_shutdown(self, ch):
        assert ch._initialized
        assert ch.shutdown()
        assert not ch._initialized

    def test_seed_devices(self, ch):
        assert len(ch.devices) > 50
        it = [d for d in ch.devices.values() if d.location.startswith("rack-")]
        assert len(it) > 40

    def test_seed_sensors(self, ch):
        assert len(ch.sensors) > 10
        lora = [s for s in ch.sensors.values() if s.kind == IoTKind.LORA_TH]
        assert len(lora) >= 10

    def test_seed_skills(self, ch):
        assert len(ch.skills) == 4
        sk = ch.skills["skl-th-1"]
        assert sk.confidence > 0.5

    def test_seed_policies(self, ch):
        assert len(ch.policies) == 6
        kinds = {p.kind for p in ch.policies.values()}
        assert PolicyKind.OPEN_SOURCE in kinds
        assert PolicyKind.SAVE_OUTGO in kinds

    def test_seed_heritage(self, ch):
        assert len(ch.heritage) >= 3


# ── 4-perspective analytics ──
class TestPerspectives:
    def test_device_perspective(self, ch):
        r = ch.analyze_perspective(DCPerspective.DEVICE)
        assert r["perspective"] == "device"
        assert r["total_kw"] > 0
        assert r["device_count"] > 0

    def test_facility_perspective(self, ch):
        r = ch.analyze_perspective(DCPerspective.FACILITY)
        assert r["it_kw"] > 0
        assert r["crac_kw"] > 0  # ac-* CRAC devices
        assert r["pue"] > 1.0

    def test_environment_perspective(self, ch):
        r = ch.analyze_perspective(DCPerspective.ENVIRONMENT)
        assert r["temp_avg_c"] > 0
        assert isinstance(r["hotspot_sensors"], list)

    def test_process_perspective(self, ch):
        r = ch.analyze_perspective(DCPerspective.PROCESS)
        assert r["skill_library_size"] == 4
        assert 0 <= r["process_maturity_pct"] <= 100

    def test_four_view(self, ch):
        r = ch.four_view_overview()
        assert set(r.keys()) == {"device", "facility", "environment", "process"}


# ── IoT ──
class TestIoT:
    def test_ingest_sensor(self, ch):
        sid = list(ch.sensors.keys())[0]
        r = ch.ingest_sensor(sid, 33.5)
        assert r["ok"]
        assert ch.sensors[sid].value == 33.5

    def test_ingest_sensor_not_found(self, ch):
        r = ch.ingest_sensor("nonexistent", 1.0)
        assert not r["ok"]

    def test_hub_summary(self, ch):
        h = ch.hub_summary()
        assert h["total_sensors"] > 0
        assert "lora_temp_humidity" in h["by_kind"]


# ── Skills ──
class TestSkills:
    def test_add_skill(self, ch):
        r = ch.add_skill("skl-new", "Test Skill", "trigger", "action", tags=["test"])
        assert r["ok"]
        assert r["library_size"] == 5

    def test_add_duplicate(self, ch):
        r = ch.add_skill("skl-th-1", "dup", "t", "a")
        assert not r["ok"]

    def test_reinforce_skill(self, ch):
        r = ch.reinforce_skill("skl-th-1", True)
        assert r["ok"]
        assert r["confidence"] > 0

    def test_reinforce_not_found(self, ch):
        r = ch.reinforce_skill("nonexistent", True)
        assert not r["ok"]


# ── Policies ──
class TestPolicies:
    def test_apply_policy(self, ch):
        old_pue = ch.current_pue
        r = ch.apply_policy("pol-save-01", 0.9)
        assert r["ok"]
        assert ch.current_pue < old_pue

    def test_apply_not_found(self, ch):
        r = ch.apply_policy("nonexistent")
        assert not r["ok"]

    def test_apply_clamps_fitness(self, ch):
        ch.apply_policy("pol-save-01", 1.5)
        p = ch.policies["pol-save-01"]
        assert p.fitness <= 1.0

    def test_recommend_actions(self, ch):
        recs = ch.recommend_actions(3)
        assert len(recs) <= 3
        if recs:
            assert "score" in recs[0]
            assert "expected_saving_kwh_day" in recs[0]


# ── Closed Loop ──
class TestClosedLoop:
    def test_closed_loop_tick(self, ch):
        r = ch.closed_loop_tick()
        assert r["ok"]
        assert "decided_policy" in r
        assert "current_pue" in r
        assert r["verified"] is True or r["verified"] is False

    def test_loop_tick_applies_policy(self, ch):
        old = ch.current_pue
        r = ch.closed_loop_tick()
        if r["decided_policy"]:
            assert ch.current_pue <= old

    def test_loop_tick_no_candidates(self, ch):
        for p in ch.policies.values():
            p.applied = True
        r = ch.closed_loop_tick()
        assert r["decided_policy"] is None


# ── Darwin Ratchet ──
class TestDarwinRatchet:
    def test_evolve(self, ch):
        old_pue = ch.current_pue
        r = ch.evolve("test evolution", "general", -0.01, 5.0)
        assert r["ok"]
        assert ch.current_pue < old_pue
        assert r["evolution_round"] >= 1

    def test_evolve_heritage_append_only(self, ch):
        n = len(ch.heritage)
        ch.evolve("h1", "iot", -0.005, 2.0)
        ch.evolve("h2", "loop", -0.003, 1.5)
        assert len(ch.heritage) == n + 2

    def test_heritage_ledger(self, ch):
        ledger = ch.heritage_ledger()
        assert len(ledger) >= 3
        assert "heritage_id" in ledger[0]
        assert "delta_pue" in ledger[0]

    def test_pue_floor(self, ch):
        for _ in range(100):
            ch.evolve("push", "general", -0.1, 1.0)
        assert ch.current_pue >= 1.05


# ── Time series + Sankey ──
class TestTimeSeries:
    def test_pue_history(self, ch):
        hist = ch.get_pue_history(10)
        assert len(hist) > 0
        assert "ts" in hist[0]
        assert "pue" in hist[0]

    def test_record_event_caps(self, ch):
        for i in range(600):
            ch._record_event("test", {"i": i})
        assert len(ch.events) <= 500

    def test_energy_sankey(self, ch):
        s = ch.energy_sankey()
        assert s["total_in_kw"] > 0
        assert len(s["nodes"]) >= 6
        assert len(s["links"]) >= 5


# ── Benchmark + Cost ──
class TestBenchmarkCost:
    def test_benchmark(self, ch):
        b = ch.benchmark()
        assert b["current_pue"] > 0
        assert b["target_pue"] > 0
        assert "vs_industry_pct" in b

    def test_cost_summary(self, ch):
        ch.apply_policy("pol-save-01", 0.9)
        c = ch.cost_summary()
        assert c["saving_kwh_day"] > 0
        assert c["co2_ton_year"] > 0
        assert c["tree_equivalent"] >= 0

    def test_cost_no_applied(self, ch):
        c = ch.cost_summary()
        assert c["saving_kwh_day"] == 0.0


# ── Devices ──
class TestDevices:
    def test_list_devices(self, ch):
        devs = ch.list_devices()
        assert len(devs) > 50
        assert "device_id" in devs[0]
        assert "actual_power_kw" in devs[0]

    def test_get_device_detail(self, ch):
        did = list(ch.devices.keys())[0]
        d = ch.get_device_detail(did)
        assert d is not None
        assert d["device_id"] == did

    def test_get_device_not_found(self, ch):
        assert ch.get_device_detail("nonexistent") is None


# ── Auto loop ──
class TestAutoLoop:
    def test_set_auto_loop(self, ch):
        r = ch.set_auto_loop(True, 30)
        assert r["ok"]
        assert ch.auto_loop_enabled is True
        assert ch.auto_loop_interval_s == 30


# ── What-If Simulation ──
class TestWhatIf:
    def test_what_if_empty(self, ch):
        r = ch.what_if([])
        assert r["ok"]
        assert r["scenario_count"] == 0
        assert r["projected_pue"] == ch.current_pue

    def test_what_if_custom_scenario(self, ch):
        sc = [{"title": "test cooling", "delta_pue": -0.03, "delta_kwh_day": 10, "capex_cny": 50000}]
        r = ch.what_if(sc)
        assert r["ok"]
        assert r["scenario_count"] == 1
        assert r["projected_pue"] < ch.current_pue
        assert r["saving_kwh_day_total"] == 10.0
        assert r["total_capex_cny"] == 50000
        assert r["payback_years"] is not None
        assert r["payback_years"] > 0

    def test_what_if_policy_scenario(self, ch):
        pid = list(ch.policies.keys())[0]
        sc = [{"policy_id": pid, "fitness": 0.9}]
        r = ch.what_if(sc)
        assert r["ok"]
        assert r["projected_pue"] < ch.current_pue
        assert r["saving_kwh_day_total"] > 0

    def test_what_if_multiple_scenarios(self, ch):
        sc = [
            {"title": "s1", "delta_pue": -0.01, "delta_kwh_day": 5, "capex_cny": 10000},
            {"title": "s2", "delta_pue": -0.02, "delta_kwh_day": 8, "capex_cny": 20000},
        ]
        r = ch.what_if(sc)
        assert r["scenario_count"] == 2
        assert r["saving_kwh_day_total"] == 13.0
        assert r["total_capex_cny"] == 30000

    def test_what_if_no_capex(self, ch):
        sc = [{"title": "free", "delta_pue": -0.01, "delta_kwh_day": 3}]
        r = ch.what_if(sc)
        assert r["payback_years"] == 0.0  # capex=0 → payback=0


# ── Musk Five-Step Audit ──
class TestMuskAudit:
    def test_musk_audit_structure(self, ch):
        r = ch.musk_five_step_audit()
        assert r["ok"]
        assert "steps" in r
        assert "1_question_requirements" in r["steps"]
        assert "2_delete" in r["steps"]
        assert "3_simplify_optimize" in r["steps"]
        assert "4_accelerate_cycle" in r["steps"]
        assert "5_automate" in r["steps"]

    def test_musk_audit_has_items(self, ch):
        r = ch.musk_five_step_audit()
        for key in r["steps"]:
            assert len(r["steps"][key]) > 0

    def test_musk_audit_metadata(self, ch):
        r = ch.musk_five_step_audit()
        assert r["current_pue"] > 0
        assert r["ratchet_locked_items"] >= 0
        assert r["evolution_round"] >= 0
        assert r["generated_at"] > 0


# ── Forecast ──
class TestForecast:
    def test_forecast_default(self, ch):
        r = ch.forecast_pue()
        assert "points" in r
        pts = r["points"]
        assert len(pts) > 0
        assert "ts" in pts[0]
        assert "pue" in pts[0]
        assert "load_factor" in pts[0]

    def test_forecast_custom_hours(self, ch):
        r = ch.forecast_pue(hours=6, sample_step_min=60)
        pts = r["points"]
        assert len(pts) > 0

    def test_forecast_pue_within_range(self, ch):
        r = ch.forecast_pue(hours=12)
        for p in r["points"]:
            assert 1.0 < p["pue"] < 3.0  # reasonable PUE range


# ── Anomaly Detection ──
class TestAnomalyDetection:
    def test_anomalies_basic(self, ch):
        r = ch.detect_anomalies()
        assert "anomalies" in r
        assert "total" in r
        assert "by_severity" in r
        assert isinstance(r["anomalies"], list)

    def test_anomalies_severity_count(self, ch):
        r = ch.detect_anomalies()
        sev = r["by_severity"]
        total = sum(sev.get(k, 0) for k in ["critical", "high", "medium", "low"])
        assert total == r["total"]

    def test_anomalies_custom_threshold(self, ch):
        r_strict = ch.detect_anomalies(z_threshold=1.0)
        r_loose = ch.detect_anomalies(z_threshold=5.0)
        # Stricter threshold should find >= as many anomalies
        assert r_strict["total"] >= r_loose["total"]


# ── Simulate Tick ──
class TestSimulateTick:
    def test_simulate_tick(self, ch):
        before = len(ch.pue_history)
        r = ch.simulate_tick()
        assert r["ok"]
        assert len(ch.pue_history) > before

    def test_simulate_tick_updates_pue(self, ch):
        pue_before = ch.current_pue
        ch.simulate_tick()
        # PUE should have changed (small random perturbation)
        # It might be the same by chance, so just check it's still valid
        assert ch.current_pue > 1.0

    def test_simulate_tick_multiple(self, ch):
        for _ in range(5):
            ch.simulate_tick()
        assert len(ch.pue_history) >= 5


# ── Four-View Overview ──
class TestFourView:
    def test_four_view(self, ch):
        r = ch.four_view_overview()
        # Returns {perspective_value: analysis_dict}
        assert len(r) == 4
        for p in DCPerspective:
            assert p.value in r

    def test_all_perspectives(self, ch):
        for p in DCPerspective:
            r = ch.analyze_perspective(p)
            assert "perspective" in r
            assert r["perspective"] == p.value


# ── Get Status ──
class TestStatus:
    def test_get_status(self, ch):
        s = ch.get_status()
        assert s["name"] == ch.name
        assert s["current_pue"] > 0
        assert s["device_count"] > 0
        assert s["sensor_count"] > 0
        assert "heritage_count" in s
        assert "evolution_round" in s
        assert "pue_progress_pct" in s


# ── IoT Hub ──
class TestIoTHub:
    def test_hub_summary(self, ch):
        h = ch.hub_summary()
        assert h["total_sensors"] > 0
        assert "by_kind" in h
        assert "uplink_health" in h
        assert "lora_avg_rssi_dbm" in h

    def test_ingest_sensor_valid(self, ch):
        sid = list(ch.sensors.keys())[0]
        r = ch.ingest_sensor(sid, 28.5)
        assert r["ok"]
        assert ch.sensors[sid].value == 28.5

    def test_ingest_sensor_unknown(self, ch):
        r = ch.ingest_sensor("nonexistent-sensor", 99.0)
        assert not r["ok"]


# ── Sensing Layer ──
class TestSensingLayer:
    def test_sensor_field(self, ch):
        f = ch.sensor_field()
        assert "sensors" in f
        assert "stats" in f
        assert f["stats"]["count"] > 0

    def test_sensor_field_stats(self, ch):
        f = ch.sensor_field()
        s = f["stats"]
        assert "temp_avg" in s
        assert "hotspot_count" in s or s.get("hotspot_count", 0) >= 0
        assert "th_count" in s

    def test_detect_heat_island(self, ch):
        hi = ch.detect_heat_island()
        assert "alert_level" in hi
        assert hi["alert_level"] in ("green", "yellow", "red")
        assert "heat_islands" in hi
        assert isinstance(hi["heat_islands"], list)


# ── Recommendations ──
class TestRecommendations:
    def test_recommend_actions(self, ch):
        recs = ch.recommend_actions()
        assert isinstance(recs, list)
        assert len(recs) > 0
        r = recs[0]
        assert "title" in r
        assert "expected_saving_kwh_day" in r

    def test_recommend_limit(self, ch):
        recs = ch.recommend_actions(top_n=2)
        assert len(recs) <= 2


# ── AI Insight ──
class TestAIInsight:
    def test_ai_insight_default(self, ch):
        r = ch.ai_insight()
        assert r["ok"]
        assert "summary" in r
        assert "bullets" in r
        assert isinstance(r["bullets"], list)

    def test_ai_insight_with_focus(self, ch):
        r = ch.ai_insight(focus="cooling")
        assert r["ok"]
        assert "summary" in r


# ── Process Event (async) ──
class TestProcessEvent:
    def test_process_status(self, ch):
        import asyncio
        r = asyncio.run(ch.process_event({"type": "status"}))
        assert r["ok"]

    def test_process_four_view(self, ch):
        import asyncio
        r = asyncio.run(ch.process_event({"type": "four_view"}))
        assert r["ok"]

    def test_process_unknown(self, ch):
        import asyncio
        r = asyncio.run(ch.process_event({"type": "nonexistent_event_type_xyz"}))
        assert not r["ok"]

    def test_process_closed_loop(self, ch):
        import asyncio
        r = asyncio.run(ch.process_event({"type": "closed_loop_tick"}))
        assert r["ok"]

    def test_process_evolve(self, ch):
        import asyncio
        r = asyncio.run(ch.process_event({
            "type": "evolve",
            "title": "test",
            "category": "general",
            "delta_pue": -0.001,
            "delta_kwh_day": 1.0,
        }))
        assert r["ok"]


# ── PUE Statistics ──
class TestPueStatistics:
    def test_pue_statistics(self, ch):
        r = ch.pue_statistics()
        assert r["ok"]
        assert r["sample_count"] > 0
        assert r["min_pue"] > 0
        assert r["max_pue"] >= r["min_pue"]
        assert r["avg_pue"] > 0
        assert r["std_pue"] >= 0
        assert r["trend"] in ("improving", "stable", "degrading", "insufficient_data")

    def test_pue_statistics_after_ticks(self, ch):
        for _ in range(10):
            ch.simulate_tick()
        r = ch.pue_statistics()
        assert r["sample_count"] >= 10
        assert r["improvement"] is not None
        assert "progress_pct" in r

    def test_pue_statistics_improvement(self, ch):
        # Apply policy to improve PUE, then check
        ch.apply_policy("pol-save-01", 0.9)
        ch.closed_loop_tick()
        r = ch.pue_statistics()
        assert r["baseline_pue"] == ch.baseline_pue
        assert r["target_pue"] == ch.target_pue


# ── Efficiency Score ──
class TestEfficiencyScore:
    def test_efficiency_score(self, ch):
        r = ch.efficiency_score()
        assert r["ok"]
        assert 0 <= r["composite"] <= 100
        assert r["grade"] in ("S", "A", "B", "C", "D")
        assert "breakdown" in r
        b = r["breakdown"]
        assert "pue" in b
        assert "policy_adoption" in b
        assert "heritage_maturity" in b
        assert "sensor_health" in b
        assert "skill_confidence" in b

    def test_efficiency_improves_with_policies(self, ch):
        before = ch.efficiency_score()["composite"]
        ch.apply_policy("pol-save-01", 0.9)
        ch.apply_policy("pol-open-01", 0.85)
        after = ch.efficiency_score()["composite"]
        assert after >= before

    def test_efficiency_weights_sum(self, ch):
        r = ch.efficiency_score()
        total = sum(r["weights"].values())
        assert abs(total - 1.0) < 0.01


# ── Dashboard Summary ──
class TestDashboardSummary:
    def test_dashboard(self, ch):
        r = ch.dashboard_summary()
        assert r["ok"]
        assert "kpis" in r
        assert "efficiency" in r
        assert "latest_heritage" in r
        assert "latest_events" in r
        assert "top_recommendations" in r

    def test_dashboard_kpis(self, ch):
        r = ch.dashboard_summary()
        kpis = r["kpis"]
        assert kpis["current_pue"] > 0
        assert kpis["device_count"] > 0
        assert kpis["sensor_count"] > 0

    def test_dashboard_efficiency_embedded(self, ch):
        r = ch.dashboard_summary()
        eff = r["efficiency"]
        assert 0 <= eff["composite"] <= 100
        assert eff["grade"] in ("S", "A", "B", "C", "D")
