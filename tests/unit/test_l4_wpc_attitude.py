# -*- coding: utf-8 -*-
"""
Tests for L4: Wave-Piercing Catamaran Active Attitude Control Channel
"""

import pytest
from channels.wpc_attitude_control import (
    WPCAttitudeControlChannel, MotionState, TFoilState,
    InterceptorState, FBGSensor, StressField, RCSMode, SeaState,
)


@pytest.fixture
def wpc():
    ch = WPCAttitudeControlChannel()
    ch.initialize()
    return ch


class TestWPCInit:
    def test_initialize(self, wpc):
        assert wpc._initialized
        assert wpc._mode == RCSMode.ACTIVE_FULL

    def test_t_foils_created(self, wpc):
        assert len(wpc._t_foils) == 3
        assert "bow_foil" in wpc._t_foils

    def test_interceptors_created(self, wpc):
        assert len(wpc._interceptors) == 2
        assert "int_port" in wpc._interceptors

    def test_fbg_sensors_created(self, wpc):
        assert len(wpc._fbg_sensors) >= 8


class TestTFoil:
    def test_set_angle(self):
        foil = TFoilState(foil_id="test")
        actual = foil.set_angle(10.0)
        assert actual == 10.0
        assert foil.lift_force_kn != 0

    def test_angle_clamping_max(self):
        foil = TFoilState(foil_id="test")
        actual = foil.set_angle(20.0)
        assert actual == 15.0

    def test_angle_clamping_min(self):
        foil = TFoilState(foil_id="test")
        actual = foil.set_angle(-20.0)
        assert actual == -15.0

    def test_drag_force(self):
        foil = TFoilState(foil_id="test")
        foil.set_angle(10.0)
        assert foil.drag_force_kn > 0


class TestInterceptor:
    def test_set_extension(self):
        ic = InterceptorState(interceptor_id="test", side="port")
        actual = ic.set_extension(150.0)
        assert actual == 150.0
        assert ic.force_kn > 0

    def test_extension_clamping_max(self):
        ic = InterceptorState(interceptor_id="test", side="port")
        actual = ic.set_extension(500.0)
        assert actual == 300.0

    def test_extension_clamping_min(self):
        ic = InterceptorState(interceptor_id="test", side="port")
        actual = ic.set_extension(-10.0)
        assert actual == 0.0


class TestRCSControl:
    def test_update_motion(self, wpc):
        result = wpc.update_motion(heave=0.5, pitch=2.0, roll=3.0)
        assert "motion" in result
        assert "commands" in result
        assert result["commands"] is not None

    def test_update_motion_off(self, wpc):
        wpc._mode = RCSMode.OFF
        result = wpc.update_motion(heave=0.5, pitch=2.0, roll=3.0)
        assert result["commands"] is None

    def test_update_motion_passive(self, wpc):
        wpc._mode = RCSMode.PASSIVE
        result = wpc.update_motion(heave=0.5, pitch=2.0, roll=3.0)
        assert result["commands"] is None

    def test_compute_rcs_commands(self, wpc):
        wpc._motion = MotionState(heave=1.0, pitch=3.0, roll=2.0,
                                  heave_rate=0.2, pitch_rate=0.5, roll_rate=0.3)
        commands = wpc._compute_rcs_commands()
        assert "bow_foil_angle" in commands
        assert "stern_port_angle" in commands
        assert "interceptor_port_mm" in commands

    def test_set_mode(self, wpc):
        assert wpc.set_mode("off")
        assert wpc._mode == RCSMode.OFF
        assert wpc.set_mode("active_full")
        assert wpc._mode == RCSMode.ACTIVE_FULL

    def test_set_mode_invalid(self, wpc):
        assert not wpc.set_mode("invalid_mode")


class TestFBG:
    def test_update_fbg_strain(self, wpc):
        result = wpc.update_fbg_strain("FBG-01", 500.0, 25.0)
        assert result is not None
        assert result["sensor_id"] == "FBG-01"
        assert result["raw_strain"] == 500.0

    def test_update_fbg_unknown_sensor(self, wpc):
        result = wpc.update_fbg_strain("NONEXISTENT", 100.0)
        assert result is None

    def test_temperature_compensation(self, wpc):
        result1 = wpc.update_fbg_strain("FBG-01", 500.0, 20.0)
        result2 = wpc.update_fbg_strain("FBG-01", 500.0, 40.0)
        # Different temperatures should give different mechanical strains
        assert result1["mechanical_strain"] != result2["mechanical_strain"]


class TestIFEM:
    def test_run_ifem_reconstruction(self, wpc):
        # Set strain values on ALL sensors
        for sid in wpc._fbg_sensors:
            wpc.update_fbg_strain(sid, 300.0)
        fields = wpc.run_ifem_reconstruction()
        assert len(fields) > 0
        for sf in fields:
            assert sf.von_mises_mpa > 0
            assert "xx" in sf.stress_mpa

    def test_ifem_insufficient_sensors(self, wpc):
        for s in wpc._fbg_sensors.values():
            s.is_healthy = False
        fields = wpc.run_ifem_reconstruction()
        assert len(fields) == 0

    def test_fatigue_damage(self, wpc):
        for sid in list(wpc._fbg_sensors.keys())[:4]:
            wpc.update_fbg_strain(sid, 1000.0)  # High strain
        fields = wpc.run_ifem_reconstruction()
        for sf in fields:
            assert sf.fatigue_damage >= 0


class TestMSDV:
    def test_calculate_msdv(self, wpc):
        msdv = wpc.calculate_msdv()
        assert msdv >= 0

    def test_msdv_with_motion(self, wpc):
        wpc.update_motion(heave=1.0, pitch=3.0, roll=5.0,
                         heave_rate=0.5, pitch_rate=1.0, roll_rate=0.8)
        msdv = wpc.calculate_msdv()
        assert msdv >= 0


class TestRCSEffectiveness:
    def test_get_rcs_effectiveness(self, wpc):
        result = wpc.get_rcs_effectiveness()
        assert "mode" in result
        assert "reduction_pct" in result
        assert "t_foils" in result
        assert "interceptors" in result

    def test_effectiveness_shows_reduction(self, wpc):
        wpc.update_motion(heave=0.5, pitch=2.0, roll=1.5)
        result = wpc.get_rcs_effectiveness()
        assert result["reduction_pct"] >= 0


class TestWPCStatus:
    def test_get_status(self, wpc):
        status = wpc.get_status()
        assert status["name"] == "wpc_attitude_control"
        assert status["rcs_mode"] == "active_full"
        assert "fbg_sensors" in status
        assert "msdv" in status

    def test_shutdown(self, wpc):
        assert wpc.shutdown()
        assert wpc._mode == RCSMode.OFF
        assert not wpc._initialized
