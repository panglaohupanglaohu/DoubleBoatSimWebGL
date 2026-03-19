# -*- coding: utf-8 -*-
"""
Marine Message Bus / Config Loader / Engine Monitor / Maritime Scene Model 单元测试
"""

import pytest
from datetime import datetime

from channels.marine_message_bus import (
    MarineMessageBus,
    MarineMessage,
    MessageType,
    MessagePriority,
    create_safety_alert,
    create_engine_problem,
)
from channels.engine_monitor import EngineMonitorChannel, AlarmLevel
from channels.maritime_scene_model import MaritimeSceneModel
from config_loader import get_config, ConfigLoader


# ────────────────── Marine Message Bus ──────────────────


class TestMarineMessageBus:
    def test_init(self):
        bus = MarineMessageBus()
        assert bus is not None

    def test_register_channel(self):
        bus = MarineMessageBus()
        assert bus.register_channel("nav") is True

    def test_unregister_channel(self):
        bus = MarineMessageBus()
        bus.register_channel("nav")
        assert bus.unregister_channel("nav") is True
        assert bus.unregister_channel("nonexistent") is False

    def test_subscribe(self):
        bus = MarineMessageBus()
        bus.register_channel("nav")
        sub_id = bus.subscribe("nav", message_types={MessageType.SAFETY_ALERT})
        assert isinstance(sub_id, str)

    def test_publish_sync(self):
        bus = MarineMessageBus()
        bus.register_channel("sender")
        bus.register_channel("receiver")

        received = []
        bus.subscribe("receiver", callback=lambda msg: received.append(msg))

        msg = bus.create_message(
            message_type=MessageType.STATUS_UPDATE,
            sender="sender",
            subject="test",
            content={"status": "ok"},
            target="receiver",
        )
        delivered = bus.publish_sync(msg)
        assert isinstance(delivered, list)

    def test_create_message(self):
        bus = MarineMessageBus()
        msg = bus.create_message(
            message_type=MessageType.NAVIGATION_WARNING,
            sender="nav",
            subject="CPA alert",
            content={"cpa": 0.3},
        )
        assert msg.message_type == MessageType.NAVIGATION_WARNING
        assert msg.sender_channel == "nav"

    def test_get_stats(self):
        bus = MarineMessageBus()
        stats = bus.get_stats()
        assert isinstance(stats, dict)

    def test_safety_alert_helper(self):
        msg = create_safety_alert("nav", "collision_risk", "CPA < 0.5nm")
        assert msg.message_type == MessageType.SAFETY_ALERT
        assert msg.priority == MessagePriority.SAFETY

    def test_engine_problem_helper(self):
        msg = create_engine_problem("engine", "overtemp", "warning", {"temp": 95})
        assert msg.message_type == MessageType.ENGINE_PROBLEM

    def test_message_to_dict(self):
        bus = MarineMessageBus()
        msg = bus.create_message(
            message_type=MessageType.HEARTBEAT,
            sender="sys",
            subject="heartbeat",
            content={},
        )
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert "message_type" in d

    def test_get_message_log(self):
        bus = MarineMessageBus()
        bus.register_channel("a")
        msg = bus.create_message(
            message_type=MessageType.STATUS_UPDATE,
            sender="a",
            subject="x",
            content={},
        )
        bus.publish_sync(msg)
        log = bus.get_message_log(limit=10)
        assert isinstance(log, list)


# ────────────────── Config Loader ──────────────────


class TestConfigLoader:
    def test_get_config_returns_dict(self):
        cfg = get_config()
        assert isinstance(cfg, (dict, ConfigLoader))

    def test_backend_url(self):
        from config_loader import get_backend_url
        url = get_backend_url()
        assert isinstance(url, str)
        assert ":" in url  # should contain port


# ────────────────── Engine Monitor ──────────────────


class TestEngineMonitor:
    def test_init(self):
        ch = EngineMonitorChannel()
        assert ch.name == "engine_monitor"

    def test_initialize(self):
        ch = EngineMonitorChannel()
        assert ch.initialize() is True

    def test_update_parameter(self):
        ch = EngineMonitorChannel()
        ch.initialize()
        param = ch.update_parameter("coolant_temp", 82.0, "°C")
        assert param.name == "coolant_temp"
        assert param.value == 82.0

    def test_simulate_data(self):
        ch = EngineMonitorChannel()
        ch.initialize()
        data = ch.simulate_data()
        assert isinstance(data, dict)

    def test_engine_status(self):
        ch = EngineMonitorChannel()
        ch.initialize()
        ch.simulate_data()
        status = ch.get_engine_status()
        assert hasattr(status, "engine_id")

    def test_get_status(self):
        ch = EngineMonitorChannel()
        ch.initialize()
        status = ch.get_status()
        assert isinstance(status, dict)
        assert "health" in status


# ────────────────── Maritime Scene Model ──────────────────


class TestMaritimeSceneModel:
    def test_evaluate(self):
        model = MaritimeSceneModel()
        result = model.evaluate(
            own_ship={"lat": 31.23, "lon": 121.47, "course": 90, "speed": 12},
            targets=[],
        )
        assert isinstance(result, dict)
        assert "scene_type" in result

    def test_evaluate_with_targets(self):
        model = MaritimeSceneModel()
        targets = [
            {"lat": 31.24, "lon": 121.48, "course": 270, "speed": 8, "mmsi": "123456789"},
        ]
        result = model.evaluate(
            own_ship={"lat": 31.23, "lon": 121.47, "course": 90, "speed": 12},
            targets=targets,
        )
        assert isinstance(result, dict)
        assert "target_density" in result
