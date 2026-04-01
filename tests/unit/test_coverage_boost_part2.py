# -*- coding: utf-8 -*-
"""
Coverage boost tests part 2: Marine Message Bus, Marine Base,
Event Store, Config Loader, Cloud Sync.
"""

import asyncio
import json
import time
import math
import os
import tempfile
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

# ---------- Marine Message Bus ----------
from channels.marine_message_bus import (
    MarineMessageBus, MarineMessage, MessageType, MessagePriority,
    Subscription, create_safety_alert, create_engine_problem,
)


@pytest.fixture
def msg_bus():
    bus = MarineMessageBus()
    bus.register_channel("nav")
    bus.register_channel("engine")
    bus.register_channel("weather")
    return bus


class TestMessageBusRegistration:
    def test_register_channel(self, msg_bus):
        assert msg_bus.register_channel("new_ch")
        assert not msg_bus.register_channel("new_ch")  # duplicate

    def test_unregister_channel(self, msg_bus):
        assert msg_bus.unregister_channel("nav")
        assert not msg_bus.unregister_channel("nonexistent")


class TestMessageBusSubscription:
    def test_subscribe(self, msg_bus):
        sub_id = msg_bus.subscribe("nav", {MessageType.SAFETY_ALERT})
        assert sub_id == "nav"

    def test_unsubscribe(self, msg_bus):
        msg_bus.subscribe("nav", {MessageType.SAFETY_ALERT})
        assert msg_bus.unsubscribe("nav")

    def test_unsubscribe_nonexistent(self, msg_bus):
        assert not msg_bus.unsubscribe("nonexistent")

    def test_unsubscribe_with_id(self, msg_bus):
        msg_bus.subscribe("nav", {MessageType.SAFETY_ALERT})
        assert msg_bus.unsubscribe("nav", subscription_id="nav")


class TestMessageBusPublishSync:
    def test_publish_sync_broadcast(self, msg_bus):
        received = []
        msg_bus.subscribe("nav", {MessageType.SAFETY_ALERT}, lambda m: received.append(m))
        msg = msg_bus.create_message(
            MessageType.SAFETY_ALERT, "weather", "Storm Warning", {"severity": "high"}
        )
        recipients = msg_bus.publish_sync(msg)
        assert "nav" in recipients

    def test_publish_sync_unicast(self, msg_bus):
        received = []
        msg_bus.subscribe("engine", {MessageType.STATUS_UPDATE}, lambda m: received.append(m))
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Status", {"speed": 12},
            target="engine"
        )
        recipients = msg_bus.publish_sync(msg)
        assert "engine" in recipients

    def test_publish_sync_multicast(self, msg_bus):
        msg_bus.subscribe("nav", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg_bus.subscribe("engine", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "weather", "Update", {},
            targets=["nav", "engine"]
        )
        recipients = msg_bus.publish_sync(msg)
        assert len(recipients) == 2

    def test_publish_expired_message(self, msg_bus):
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Old", {},
        )
        msg.expiry_time = time.time() - 10
        recipients = msg_bus.publish_sync(msg)
        assert len(recipients) == 0

    def test_publish_duplicate_message(self, msg_bus):
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Dup", {}
        )
        msg_bus.publish_sync(msg)
        recipients = msg_bus.publish_sync(msg)  # Same message ID
        assert len(recipients) == 0

    def test_priority_filter(self, msg_bus):
        received = []
        msg_bus.subscribe(
            "nav", {MessageType.STATUS_UPDATE},
            callback=lambda m: received.append(m),
            priority_filter=MessagePriority.SAFETY,
        )
        # Routine priority (lower than safety)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "engine", "Routine", {},
            target="nav", priority=MessagePriority.ROUTINE
        )
        msg_bus.publish_sync(msg)
        assert len(received) == 0

    def test_callback_error_handling(self, msg_bus):
        def bad_callback(m):
            raise ValueError("test error")
        msg_bus.subscribe("nav", {MessageType.STATUS_UPDATE}, bad_callback)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "engine", "Test", {},
            target="nav"
        )
        recipients = msg_bus.publish_sync(msg)
        # Should not crash, but delivery fails
        assert len(recipients) == 0

    def test_no_subscription_no_delivery(self, msg_bus):
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "engine", "Test", {},
            target="nav"
        )
        recipients = msg_bus.publish_sync(msg)
        assert len(recipients) == 0

    def test_inactive_subscription(self, msg_bus):
        """Inactive subscriptions don't fire callbacks but delivery still succeeds."""
        received = []
        sub = Subscription(
            channel_id="nav",
            message_types={MessageType.STATUS_UPDATE},
            callback=lambda m: received.append(m),
            active=False,
        )
        msg_bus._subscriptions["nav"].append(sub)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "engine", "Test", {},
            target="nav"
        )
        msg_bus.publish_sync(msg)
        assert len(received) == 0  # Callback not fired

    def test_message_type_mismatch(self, msg_bus):
        """Mismatched type: callback not fired, but delivery still succeeds."""
        received = []
        msg_bus.subscribe("nav", {MessageType.SAFETY_ALERT}, lambda m: received.append(m))
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "engine", "Test", {},
            target="nav"
        )
        msg_bus.publish_sync(msg)
        assert len(received) == 0  # Callback not fired due to type mismatch

    def test_publish_to_nonexistent_target(self, msg_bus):
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Test", {},
            target="does_not_exist"
        )
        recipients = msg_bus.publish_sync(msg)
        assert len(recipients) == 0

    def test_broadcast_excludes_sender(self, msg_bus):
        msg_bus.subscribe("nav", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg_bus.subscribe("engine", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg_bus.subscribe("weather", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Test", {}
        )
        recipients = msg_bus.publish_sync(msg)
        assert "nav" not in recipients


class TestMessageBusPublishAsync:
    def test_publish_async(self, msg_bus):
        received = []
        msg_bus.subscribe("engine", {MessageType.SAFETY_ALERT}, lambda m: received.append(m))
        msg = msg_bus.create_message(
            MessageType.SAFETY_ALERT, "nav", "Alert", {"type": "collision"}
        )
        recipients = asyncio.run(msg_bus.publish(msg))
        assert len(recipients) > 0

    def test_publish_async_expired(self, msg_bus):
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Test", {}
        )
        msg.expiry_time = time.time() - 10
        recipients = asyncio.run(msg_bus.publish(msg))
        assert len(recipients) == 0

    def test_publish_async_duplicate(self, msg_bus):
        msg_bus.subscribe("engine", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Test", {}
        )
        asyncio.run(msg_bus.publish(msg))
        msg_bus._lock = None  # Reset lock for new event loop
        recipients = asyncio.run(msg_bus.publish(msg))
        assert len(recipients) == 0


class TestMessageBusStats:
    def test_get_stats(self, msg_bus):
        stats = msg_bus.get_stats()
        assert "messages_sent" in stats
        assert stats["registered_channels"] == 3

    def test_get_message_log(self, msg_bus):
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Test", {}
        )
        msg_bus.publish_sync(msg)
        log = msg_bus.get_message_log()
        assert len(log) == 1

    def test_get_message_log_filtered(self, msg_bus):
        for mt in [MessageType.STATUS_UPDATE, MessageType.SAFETY_ALERT]:
            msg = msg_bus.create_message(mt, "nav", "Test", {})
            msg_bus.publish_sync(msg)
        log = msg_bus.get_message_log(message_type=MessageType.SAFETY_ALERT)
        assert len(log) == 1

    def test_get_message_log_by_sender(self, msg_bus):
        msg = msg_bus.create_message(MessageType.STATUS_UPDATE, "engine", "Test", {})
        msg_bus.publish_sync(msg)
        log = msg_bus.get_message_log(sender="engine")
        assert len(log) == 1

    def test_clear_log(self, msg_bus):
        msg = msg_bus.create_message(MessageType.STATUS_UPDATE, "nav", "Test", {})
        msg_bus.publish_sync(msg)
        count = msg_bus.clear_log()
        assert count == 1
        assert len(msg_bus._message_log) == 0

    def test_stats_after_broadcast(self, msg_bus):
        msg_bus.subscribe("nav", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "engine", "Test", {}
        )
        msg_bus.publish_sync(msg)
        stats = msg_bus.get_stats()
        assert stats["broadcasts"] >= 1
        assert stats["messages_sent"] >= 1

    def test_stats_after_unicast(self, msg_bus):
        msg_bus.subscribe("nav", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "engine", "Test", {},
            target="nav"
        )
        msg_bus.publish_sync(msg)
        stats = msg_bus.get_stats()
        assert stats["unicasts"] >= 1

    def test_stats_after_multicast(self, msg_bus):
        msg_bus.subscribe("nav", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg_bus.subscribe("engine", {MessageType.STATUS_UPDATE}, lambda m: None)
        msg = msg_bus.create_message(
            MessageType.STATUS_UPDATE, "weather", "Test", {},
            targets=["nav", "engine"]
        )
        msg_bus.publish_sync(msg)
        stats = msg_bus.get_stats()
        assert stats["multicasts"] >= 1


class TestMarineMessageHelpers:
    def test_message_to_dict(self):
        msg = MarineMessage(
            message_type=MessageType.SAFETY_ALERT,
            priority=MessagePriority.SAFETY,
            sender_channel="nav",
            subject="Test",
            content={"data": "yes"},
        )
        d = msg.to_dict()
        assert d["message_type"] == "safety_alert"
        assert d["priority"] == 2
        assert d["sender_channel"] == "nav"
        assert d["subject"] == "Test"
        assert d["content"] == {"data": "yes"}

    def test_message_from_dict(self):
        d = {
            "message_type": "safety_alert",
            "priority": 2,
            "sender_channel": "nav",
            "subject": "Test",
            "content": {"data": "yes"},
        }
        msg = MarineMessage.from_dict(d)
        assert msg.message_type == MessageType.SAFETY_ALERT
        assert msg.priority == MessagePriority.SAFETY

    def test_message_roundtrip(self):
        orig = MarineMessage(
            message_type=MessageType.NAVIGATION_WARNING,
            priority=MessagePriority.URGENCY,
            sender_channel="nav",
            target_channel="engine",
            subject="Test",
            content={"lat": 31.0},
            correlation_id="corr-123",
        )
        d = orig.to_dict()
        restored = MarineMessage.from_dict(d)
        assert restored.message_type == orig.message_type
        assert restored.correlation_id == "corr-123"
        assert restored.target_channel == "engine"

    def test_message_expiry(self):
        msg = MarineMessage(expiry_time=time.time() - 10)
        assert msg.is_expired()

    def test_message_not_expired(self):
        msg = MarineMessage(expiry_time=time.time() + 100)
        assert not msg.is_expired()

    def test_message_no_expiry(self):
        msg = MarineMessage()
        assert not msg.is_expired()

    def test_create_safety_alert(self):
        msg = create_safety_alert("nav", "storm", "Storm approaching", {"lat": 31.0, "lon": 121.0})
        assert msg.message_type == MessageType.SAFETY_ALERT
        assert msg.priority == MessagePriority.SAFETY

    def test_create_safety_alert_no_position(self):
        msg = create_safety_alert("nav", "fog", "Dense fog")
        assert msg.message_type == MessageType.SAFETY_ALERT

    def test_create_engine_problem(self):
        msg = create_engine_problem("engine", "overheating", "critical", {"temp": 99})
        assert msg.message_type == MessageType.ENGINE_PROBLEM
        assert msg.priority == MessagePriority.URGENCY

    def test_message_type_enum_values(self):
        assert MessageType.SAFETY_ALERT.value == "safety_alert"
        assert MessageType.HEARTBEAT.value == "heartbeat"
        assert MessageType.COMMAND.value == "command"
        assert MessageType.DATA_REQUEST.value == "data_request"
        assert MessageType.DATA_RESPONSE.value == "data_response"

    def test_priority_enum_values(self):
        assert MessagePriority.DISTRESS.value == 0
        assert MessagePriority.URGENCY.value == 1
        assert MessagePriority.SAFETY.value == 2
        assert MessagePriority.ROUTINE.value == 3


class TestCreateMessage:
    def test_with_expiry_seconds(self):
        bus = MarineMessageBus()
        msg = bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Test", {},
            expiry_seconds=60.0
        )
        assert msg.expiry_time is not None
        assert msg.expiry_time > time.time()

    def test_with_correlation_id(self):
        bus = MarineMessageBus()
        msg = bus.create_message(
            MessageType.DATA_REQUEST, "nav", "Query", {},
            correlation_id="req-001"
        )
        assert msg.correlation_id == "req-001"

    def test_with_target(self):
        bus = MarineMessageBus()
        msg = bus.create_message(
            MessageType.COMMAND, "nav", "Steer", {},
            target="steering"
        )
        assert msg.target_channel == "steering"

    def test_with_targets(self):
        bus = MarineMessageBus()
        msg = bus.create_message(
            MessageType.STATUS_UPDATE, "nav", "Test", {},
            targets=["engine", "weather"]
        )
        assert "engine" in msg.target_channels
        assert "weather" in msg.target_channels


# ---------- Marine Base Extended ----------
from channels.marine_base import (
    MarineChannel, ChannelRegistry, ChannelHealth, ChannelMetrics,
    ChannelStatus, ChannelPriority, get_default_registry, create_registry,
)


class ConcreteChannel(MarineChannel):
    name = "test_channel"
    description = "Test Channel"

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "OK")
        return True

    def get_status(self):
        return {"name": self.name, "health": self._health.status.value}

    def shutdown(self) -> bool:
        self._initialized = False
        return True


class ConcreteChannel2(MarineChannel):
    name = "test_channel_2"
    description = "Test Channel 2"
    priority = ChannelPriority.P0

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "OK")
        return True

    def get_status(self):
        return {"name": self.name}

    def shutdown(self) -> bool:
        self._initialized = False
        return True


class FailingChannel(MarineChannel):
    name = "failing_channel"
    description = "A channel that fails"

    def initialize(self) -> bool:
        raise RuntimeError("Init failed!")

    def get_status(self):
        return {"error": True}

    def shutdown(self) -> bool:
        raise RuntimeError("Shutdown failed!")


class TestChannelRegistry:
    def test_register(self):
        reg = create_registry()
        ch = ConcreteChannel()
        assert reg.register(ch)

    def test_register_duplicate(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        with pytest.raises(ValueError):
            reg.register(ConcreteChannel())

    def test_register_no_name(self):
        reg = create_registry()

        class NoNameChannel(MarineChannel):
            name = ""
            description = "no name"
            def initialize(self): return True
            def get_status(self): return {}
            def shutdown(self): return True

        with pytest.raises(ValueError):
            reg.register(NoNameChannel())

    def test_unregister(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        assert reg.unregister("test_channel")
        assert not reg.unregister("test_channel")

    def test_get(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        assert reg.get("test_channel") is ch
        assert reg.get("nonexistent") is None

    def test_list_channels(self):
        reg = create_registry()
        reg.register(ConcreteChannel())
        assert "test_channel" in reg.list_channels()

    def test_initialize_all(self):
        reg = create_registry()
        reg.register(ConcreteChannel())
        results = reg.initialize_all()
        assert results["test_channel"] is True

    def test_initialize_all_with_failure(self):
        reg = create_registry()
        reg.register(FailingChannel())
        results = reg.initialize_all()
        assert results["failing_channel"] is False

    def test_shutdown_all(self):
        reg = create_registry()
        reg.register(ConcreteChannel())
        reg.initialize_all()
        results = reg.shutdown_all()
        assert results["test_channel"] is True

    def test_shutdown_all_with_failure(self):
        reg = create_registry()
        reg.register(FailingChannel())
        results = reg.shutdown_all()
        assert results["failing_channel"] is False

    def test_get_all_status(self):
        reg = create_registry()
        reg.register(ConcreteChannel())
        reg.initialize_all()
        status = reg.get_all_status()
        assert "test_channel" in status

    def test_get_healthy_channels(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        ch.initialize()
        healthy = reg.get_healthy_channels()
        assert ch in healthy

    def test_get_unhealthy_channels(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        unhealthy = reg.get_unhealthy_channels()
        assert ch in unhealthy  # Not initialized

    def test_get_metrics_summary(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        summary = reg.get_metrics_summary()
        assert summary["total_channels"] == 1

    def test_get_metrics_summary_with_calls(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        ch._record_call(True, 5.0)
        ch._record_call(False, 10.0)
        summary = reg.get_metrics_summary()
        assert summary["total_calls"] == 2
        assert summary["total_success"] == 1
        assert summary["total_failed"] == 1
        assert summary["success_rate"] == 0.5

    def test_get_metrics_summary_no_calls(self):
        reg = create_registry()
        ch = ConcreteChannel()
        reg.register(ch)
        summary = reg.get_metrics_summary()
        assert summary["success_rate"] == 0.0

    def test_multiple_channels(self):
        reg = create_registry()
        reg.register(ConcreteChannel())
        reg.register(ConcreteChannel2())
        assert len(reg.list_channels()) == 2
        results = reg.initialize_all()
        assert all(results.values())

    def test_get_default_registry(self):
        reg = get_default_registry()
        assert isinstance(reg, ChannelRegistry)


class TestMarineChannelBase:
    def test_check_not_initialized(self):
        ch = ConcreteChannel()
        status, msg = ch.check()
        assert status == "off"

    def test_check_ok(self):
        ch = ConcreteChannel()
        ch.initialize()
        status, msg = ch.check()
        assert status == "ok"

    def test_check_warn(self):
        ch = ConcreteChannel()
        ch._initialized = True
        ch._set_health(ChannelStatus.WARN, "Warning test")
        status, msg = ch.check()
        assert status == "warn"

    def test_check_error(self):
        ch = ConcreteChannel()
        ch._initialized = True
        ch._set_health(ChannelStatus.ERROR, "Error test")
        status, msg = ch.check()
        assert status == "error"

    def test_get_health(self):
        ch = ConcreteChannel()
        h = ch.get_health()
        assert isinstance(h, ChannelHealth)

    def test_get_metrics(self):
        ch = ConcreteChannel()
        m = ch.get_metrics()
        assert isinstance(m, ChannelMetrics)

    def test_reset_metrics(self):
        ch = ConcreteChannel()
        ch._metrics.calls_total = 10
        ch.reset_metrics()
        assert ch._metrics.calls_total == 0

    def test_record_call(self):
        ch = ConcreteChannel()
        ch._record_call(True, 5.0)
        assert ch._metrics.calls_total == 1
        assert ch._metrics.calls_success == 1
        assert ch._metrics.avg_latency_ms == 5.0

    def test_record_call_failure(self):
        ch = ConcreteChannel()
        ch._record_call(False, 10.0)
        assert ch._metrics.calls_failed == 1

    def test_record_multiple_calls(self):
        ch = ConcreteChannel()
        ch._record_call(True, 10.0)
        ch._record_call(True, 20.0)
        assert ch._metrics.avg_latency_ms == 15.0
        assert ch._metrics.max_latency_ms == 20.0
        assert ch._metrics.min_latency_ms == 10.0

    def test_set_health(self):
        ch = ConcreteChannel()
        ch._set_health(ChannelStatus.ERROR, "Test error")
        assert ch._health.error_count == 1
        ch._set_health(ChannelStatus.WARN, "Test warn")
        assert ch._health.warning_count == 1

    def test_set_health_ok(self):
        ch = ConcreteChannel()
        ch._set_health(ChannelStatus.OK, "All good")
        assert ch._health.status == ChannelStatus.OK

    def test_get_uptime(self):
        ch = ConcreteChannel()
        assert ch.get_uptime() == 0.0
        ch._initialized = True
        assert ch.get_uptime() > 0

    def test_validate_config(self):
        ch = ConcreteChannel()
        valid, errors = ch.validate_config()
        assert valid

    def test_validate_config_no_name(self):
        class EmptyChannel(MarineChannel):
            name = ""
            description = ""
            def initialize(self): return True
            def get_status(self): return {}
            def shutdown(self): return True

        ch = EmptyChannel()
        valid, errors = ch.validate_config()
        assert not valid
        assert len(errors) > 0

    def test_get_info(self):
        ch = ConcreteChannel()
        info = ch.get_info()
        assert info["name"] == "test_channel"
        assert "uptime_seconds" in info
        assert "version" in info
        assert "priority" in info
        assert "initialized" in info

    def test_channel_with_kwargs(self):
        ch = ConcreteChannel(custom_param="hello")
        assert ch._config.get("custom_param") == "hello"

    def test_channel_status_enum(self):
        assert ChannelStatus.OK.value == "ok"
        assert ChannelStatus.WARN.value == "warn"
        assert ChannelStatus.ERROR.value == "error"
        assert ChannelStatus.OFF.value == "off"

    def test_channel_priority_enum(self):
        assert ChannelPriority.P0.value == 0
        assert ChannelPriority.P1.value == 1
        assert ChannelPriority.P2.value == 2

    def test_channel_health_dataclass(self):
        h = ChannelHealth(status=ChannelStatus.OK, message="good")
        assert h.error_count == 0
        assert h.warning_count == 0
        assert isinstance(h.last_check, datetime)

    def test_channel_metrics_defaults(self):
        m = ChannelMetrics()
        assert m.calls_total == 0
        assert m.min_latency_ms == float('inf')
        assert m.last_call_time is None

    def test_last_call_time_updates(self):
        ch = ConcreteChannel()
        ch._record_call(True, 5.0)
        assert ch._metrics.last_call_time is not None


# ---------- Config Loader ----------
from config_loader import ConfigLoader


class TestConfigLoader:
    def test_singleton(self):
        c1 = ConfigLoader()
        c2 = ConfigLoader()
        assert c1 is c2

    def test_get_nested_key(self):
        cl = ConfigLoader()
        # This tests the dot-notation key access
        result = cl.get("nonexistent.deep.key", "default_val")
        assert result == "default_val"

    def test_get_top_level_key(self):
        cl = ConfigLoader()
        result = cl.get("nonexistent_key", 42)
        assert result == 42

    def test_backend_url_property(self):
        cl = ConfigLoader()
        url = cl.backend_url
        assert isinstance(url, str)

    def test_frontend_url_property(self):
        cl = ConfigLoader()
        url = cl.frontend_url
        assert isinstance(url, str)

    def test_llm_url_property(self):
        cl = ConfigLoader()
        url = cl.llm_url
        assert isinstance(url, str)

    def test_websocket_url_property(self):
        cl = ConfigLoader()
        url = cl.websocket_url
        assert isinstance(url, str)

    def test_debug_property(self):
        cl = ConfigLoader()
        d = cl.debug
        assert isinstance(d, bool)

    def test_environment_property(self):
        cl = ConfigLoader()
        env = cl.environment
        assert isinstance(env, str)

    def test_load_invalid_path(self):
        cl = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            cl.load("/nonexistent/path/config.json")


# ---------- Cloud Sync ----------
from storage.cloud_sync import S3CompatibleAdapter


class TestS3CompatibleAdapter:
    def test_init(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test-bucket"})
        assert adapter.bucket_name == "test-bucket"

    def test_default_config(self):
        adapter = S3CompatibleAdapter({})
        assert adapter.bucket_name == "doubleboat-events"
        assert adapter.region == "us-east-1"
        assert adapter.prefix == "events/"

    def test_upload_event_mock_mode(self):
        adapter = S3CompatibleAdapter({})
        adapter._client = None  # Force mock mode
        with patch.object(adapter, '_get_client', return_value=None):
            result = adapter.upload_event({"data": "test"}, "test_event")
            assert result is True

    def test_upload_batch_mock_mode(self):
        adapter = S3CompatibleAdapter({})
        adapter._client = None
        with patch.object(adapter, '_get_client', return_value=None):
            result = adapter.upload_batch([{"data": "a"}, {"data": "b"}], "test")
            assert result is True

    def test_build_key(self):
        adapter = S3CompatibleAdapter({"prefix": "data/"})
        now = datetime(2026, 3, 24, 12, 30, 45)
        key = adapter._build_key("sensor", now)
        assert "sensor" in key
        assert "2026/03/24" in key

    def test_build_event_prefix(self):
        adapter = S3CompatibleAdapter({"prefix": "events/"})
        prefix = adapter._build_event_prefix("navigation")
        assert prefix == "events/navigation/"

    def test_normalize_prefix(self):
        adapter = S3CompatibleAdapter({})
        assert adapter._normalize_prefix("data") == "data/"
        assert adapter._normalize_prefix("data/") == "data/"
        assert adapter._normalize_prefix("") == ""

    def test_serialize_event(self):
        adapter = S3CompatibleAdapter({})
        data = {"key": "value"}
        result = adapter._serialize_event(data, "test")
        parsed = json.loads(result.decode("utf-8"))
        assert parsed["event_type"] == "test"
        assert "uploaded_at" in parsed

    def test_parse_event_bytes(self):
        adapter = S3CompatibleAdapter({})
        data = json.dumps({"key": "value"}).encode("utf-8")
        result = adapter._parse_event_bytes(data)
        assert result["key"] == "value"

    def test_parse_event_bytes_invalid(self):
        adapter = S3CompatibleAdapter({})
        result = adapter._parse_event_bytes(b"not json")
        assert result is None

    def test_event_with_metadata(self):
        adapter = S3CompatibleAdapter({})
        event = {"data": "test"}
        enriched = adapter._event_with_metadata(event, "path/key.json", datetime(2026, 1, 1))
        assert enriched["cloud_key"] == "path/key.json"
        assert "cloud_last_modified" in enriched

    def test_event_with_metadata_none(self):
        adapter = S3CompatibleAdapter({})
        result = adapter._event_with_metadata(None, "key", None)
        assert result is None

    def test_extract_event_timestamp_iso(self):
        adapter = S3CompatibleAdapter({})
        event = {"timestamp": "2026-03-24T12:00:00"}
        result = adapter._extract_event_timestamp(event)
        assert result is not None

    def test_extract_event_timestamp_missing(self):
        adapter = S3CompatibleAdapter({})
        result = adapter._extract_event_timestamp({})
        assert result is None

    def test_list_events_no_client(self):
        adapter = S3CompatibleAdapter({})
        with patch.object(adapter, '_get_client', return_value=None):
            result = adapter.list_events("test")
            assert result == []

    def test_download_events_no_client(self):
        adapter = S3CompatibleAdapter({})
        with patch.object(adapter, '_get_client', return_value=None):
            result = adapter.download_events("test", datetime.now(), datetime.now())
            assert result == []

    def test_get_bucket_info_no_client(self):
        adapter = S3CompatibleAdapter({})
        with patch.object(adapter, '_get_client', return_value=None):
            info = adapter.get_bucket_info()
            assert isinstance(info, dict)
            assert "bucket" in info

    def test_ensure_bucket_no_client(self):
        adapter = S3CompatibleAdapter({})
        with patch.object(adapter, '_get_client', return_value=None):
            result = adapter.ensure_bucket()
            assert result["available"] is False

    def test_extract_error_code(self):
        adapter = S3CompatibleAdapter({})
        exc = Exception("test")
        assert adapter._extract_error_code(exc) is None

    def test_extract_error_code_with_response(self):
        adapter = S3CompatibleAdapter({})
        exc = Exception("test")
        exc.response = {"Error": {"Code": "404"}}
        assert adapter._extract_error_code(exc) == "404"


# ---------- Event Store (JSONL + SQLite) ----------
from storage.event_store import JSONLStore, SQLiteStore


class TestJSONLStore:
    @pytest.fixture
    def store(self, tmp_path):
        return JSONLStore({"storage_path": str(tmp_path / "events")})

    def test_save_event(self, store):
        event = {"event_type": "test", "timestamp": datetime.now().isoformat(), "data": {"v": 1}}
        assert store.save_event(event) is True

    def test_save_and_load(self, store):
        event = {"event_type": "sensor", "timestamp": datetime.now().isoformat(), "value": 42}
        store.save_event(event)
        events = store.load_events(event_type="sensor")
        assert len(events) >= 1

    def test_save_events_batch(self, store):
        events = [
            {"event_type": "batch", "timestamp": datetime.now().isoformat(), "i": i}
            for i in range(5)
        ]
        assert store.save_events(events) is True
        loaded = store.load_events(event_type="batch")
        assert len(loaded) == 5

    def test_load_all_events(self, store):
        for etype in ["alpha", "beta"]:
            store.save_event({"event_type": etype, "timestamp": datetime.now().isoformat()})
        events = store.load_events()
        assert len(events) >= 2

    def test_load_nonexistent_type(self, store):
        events = store.load_events(event_type="nonexistent")
        assert events == []

    def test_clear_events_by_type(self, store):
        store.save_event({"event_type": "to_clear", "timestamp": datetime.now().isoformat()})
        assert store.clear_events(event_type="to_clear") is True
        events = store.load_events(event_type="to_clear")
        assert len(events) == 0

    def test_clear_all_events(self, store):
        store.save_event({"event_type": "a", "timestamp": datetime.now().isoformat()})
        store.save_event({"event_type": "b", "timestamp": datetime.now().isoformat()})
        assert store.clear_events() is True

    def test_load_events_by_time(self, store):
        now = datetime.now()
        store.save_event({"event_type": "timed", "timestamp": now.isoformat()})
        events = store.load_events_by_time(
            now - timedelta(minutes=1),
            now + timedelta(minutes=1),
            event_type="timed"
        )
        assert len(events) >= 1

    def test_get_info(self, store):
        store.save_event({"event_type": "info_test", "timestamp": datetime.now().isoformat()})
        info = store.get_info()
        assert "storage_path" in info
        assert info["file_count"] >= 1

    def test_trim_file(self, store):
        store.max_events = 3
        for i in range(5):
            store.save_event({"event_type": "trim", "timestamp": datetime.now().isoformat(), "i": i})
        events = store.load_events(event_type="trim")
        assert len(events) <= 3


class TestSQLiteStore:
    @pytest.fixture
    def store(self, tmp_path):
        return SQLiteStore({"db_path": str(tmp_path / "test_events.db")})

    def test_save_event(self, store):
        event = {"event_type": "test", "timestamp": datetime.now().isoformat(), "payload": {"v": 1}}
        assert store.save_event(event) is True

    def test_save_and_load(self, store):
        event = {"event_type": "sensor", "timestamp": datetime.now().isoformat(), "payload": {"val": 42}}
        store.save_event(event)
        events = store.load_events(event_type="sensor")
        assert len(events) >= 1

    def test_save_events_batch(self, store):
        events = [
            {"event_type": "batch", "timestamp": datetime.now().isoformat(), "payload": {"i": i}}
            for i in range(5)
        ]
        assert store.save_events(events) is True
        loaded = store.load_events(event_type="batch")
        assert len(loaded) == 5

    def test_load_all_events(self, store):
        for etype in ["alpha", "beta"]:
            store.save_event({"event_type": etype, "timestamp": datetime.now().isoformat()})
        events = store.load_events()
        assert len(events) >= 2

    def test_load_events_by_time(self, store):
        now = datetime.now()
        store.save_event({"event_type": "timed", "timestamp": now.isoformat()})
        events = store.load_events_by_time(
            now - timedelta(minutes=1),
            now + timedelta(minutes=1),
            event_type="timed"
        )
        assert len(events) >= 1

    def test_load_events_by_time_no_type(self, store):
        now = datetime.now()
        store.save_event({"event_type": "any", "timestamp": now.isoformat()})
        events = store.load_events_by_time(
            now - timedelta(minutes=1),
            now + timedelta(minutes=1),
        )
        assert len(events) >= 1

    def test_clear_events_by_type(self, store):
        store.save_event({"event_type": "to_clear", "timestamp": datetime.now().isoformat()})
        assert store.clear_events(event_type="to_clear") is True
        events = store.load_events(event_type="to_clear")
        assert len(events) == 0

    def test_clear_all_events(self, store):
        store.save_event({"event_type": "a", "timestamp": datetime.now().isoformat()})
        assert store.clear_events() is True
        events = store.load_events()
        assert len(events) == 0

    def test_get_info(self, store):
        info = store.get_info()
        assert "db_path" in info
        assert info["wal_enabled"] is True
