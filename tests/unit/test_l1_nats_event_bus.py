# -*- coding: utf-8 -*-
"""
Tests for L1: NATS Event Bus Channel
"""

import pytest
from channels.nats_event_bus import (
    NATSEventBusChannel, NATSMessage, JetStreamStore,
    StreamConfig, ConsumerConfig, StreamState,
    DeliveryPolicy, AckPolicy, RetentionPolicy,
)


@pytest.fixture
def bus():
    ch = NATSEventBusChannel()
    ch.initialize()
    return ch


@pytest.fixture
def store():
    return JetStreamStore()


class TestNATSMessage:
    def test_create_message(self):
        msg = NATSMessage(subject="vessel.engine.temp", data={"temp": 85.0})
        assert msg.subject == "vessel.engine.temp"
        assert msg.data["temp"] == 85.0
        assert msg.msg_id

    def test_to_bytes(self):
        msg = NATSMessage(subject="test", data={"x": 1})
        raw = msg.to_bytes()
        assert isinstance(raw, bytes)

    def test_from_bytes(self):
        msg = NATSMessage(subject="test.sub", data={"value": 42}, headers={"h": "v"})
        raw = msg.to_bytes()
        restored = NATSMessage.from_bytes(raw)
        assert restored.subject == "test.sub"
        assert restored.data["value"] == 42


class TestJetStreamStore:
    def test_add_stream(self, store):
        config = StreamConfig("TEST", ["test.>"])
        assert store.add_stream(config)

    def test_add_duplicate_stream(self, store):
        config = StreamConfig("TEST", ["test.>"])
        store.add_stream(config)
        assert not store.add_stream(config)

    def test_delete_stream(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        assert store.delete_stream("TEST")
        assert not store.delete_stream("TEST")

    def test_publish(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        msg = NATSMessage(subject="test.data", data={"v": 1})
        seq = store.publish("TEST", msg)
        assert seq == 1

    def test_publish_nonexistent_stream(self, store):
        msg = NATSMessage(subject="test.x", data={})
        assert store.publish("NONEXISTENT", msg) is None

    def test_publish_wrong_subject(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        msg = NATSMessage(subject="other.data", data={})
        assert store.publish("TEST", msg) is None

    def test_get_messages(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        for i in range(5):
            store.publish("TEST", NATSMessage(subject="test.x", data={"i": i}))
        msgs = store.get_messages("TEST")
        assert len(msgs) == 5

    def test_get_messages_with_start_seq(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        for i in range(5):
            store.publish("TEST", NATSMessage(subject="test.x", data={"i": i}))
        msgs = store.get_messages("TEST", start_seq=3)
        assert len(msgs) == 3

    def test_get_messages_nonexistent(self, store):
        assert store.get_messages("NONEXISTENT") == []

    def test_max_msgs_retention(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"], max_msgs=3))
        for i in range(5):
            store.publish("TEST", NATSMessage(subject="test.x", data={"i": i}))
        msgs = store.get_messages("TEST")
        assert len(msgs) == 3

    def test_consumer(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        consumer = ConsumerConfig(name="c1", stream="TEST")
        assert store.add_consumer(consumer)

    def test_duplicate_consumer(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        consumer = ConsumerConfig(name="c1", stream="TEST")
        store.add_consumer(consumer)
        assert not store.add_consumer(consumer)

    def test_ack(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        store.add_consumer(ConsumerConfig(name="c1", stream="TEST"))
        store.publish("TEST", NATSMessage(subject="test.x", data={}))
        assert store.ack("TEST.c1", 1)

    def test_ack_nonexistent(self, store):
        assert not store.ack("nonexistent", 1)

    def test_get_pending(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        store.add_consumer(ConsumerConfig(name="c1", stream="TEST"))
        store.publish("TEST", NATSMessage(subject="test.x", data={}))
        store.publish("TEST", NATSMessage(subject="test.y", data={}))
        pending = store.get_pending("TEST.c1")
        assert len(pending) == 2
        store.ack("TEST.c1", 1)
        pending = store.get_pending("TEST.c1")
        assert len(pending) == 1

    def test_get_pending_with_filter(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        store.add_consumer(ConsumerConfig(name="c1", stream="TEST", filter_subject="test.x"))
        store.publish("TEST", NATSMessage(subject="test.x", data={}))
        store.publish("TEST", NATSMessage(subject="test.y", data={}))
        pending = store.get_pending("TEST.c1")
        assert len(pending) == 1

    def test_get_pending_nonexistent(self, store):
        assert store.get_pending("nonexistent") == []

    def test_get_stream_state(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        store.publish("TEST", NATSMessage(subject="test.x", data={}))
        state = store.get_stream_state("TEST")
        assert state.messages == 1

    def test_get_stream_state_nonexistent(self, store):
        assert store.get_stream_state("X") is None

    def test_get_stream_state_empty(self, store):
        store.add_stream(StreamConfig("TEST", ["test.>"]))
        state = store.get_stream_state("TEST")
        assert state.messages == 0

    def test_subject_matches_exact(self):
        assert JetStreamStore._subject_matches("test.x", ["test.x"])

    def test_subject_matches_wildcard_gt(self):
        assert JetStreamStore._subject_matches("test.x.y", ["test.>"])

    def test_subject_matches_wildcard_star(self):
        assert JetStreamStore._subject_matches("test.x", ["test.*"])

    def test_subject_no_match(self):
        assert not JetStreamStore._subject_matches("other.x", ["test.>"])


class TestNATSEventBus:
    def test_initialize(self, bus):
        assert bus._initialized

    def test_default_streams(self, bus):
        assert len(bus._jetstream._streams) >= 5

    def test_publish(self, bus):
        seq = bus.publish("vessel.nav.position", {"lat": 31.0, "lon": 121.0})
        assert seq is not None
        assert bus._stats["published"] == 1

    def test_subscribe_and_receive(self, bus):
        received = []
        bus.subscribe("vessel.engine.>", lambda msg: received.append(msg))
        bus.publish("vessel.engine.temp", {"temp": 85.0})
        assert len(received) == 1
        assert received[0].data["temp"] == 85.0

    def test_request_handler(self, bus):
        bus.register_handler("vessel.query.status", lambda d: {"ok": True, "query": d.get("q")})
        result = bus.request("vessel.query.status", {"q": "test"})
        assert result["ok"]
        assert result["query"] == "test"

    def test_request_no_handler(self, bus):
        result = bus.request("nonexistent", {})
        assert result is None

    def test_create_stream(self, bus):
        assert bus.create_stream(StreamConfig("CUSTOM", ["custom.>"]))

    def test_create_consumer(self, bus):
        bus.create_stream(StreamConfig("CUSTOM", ["custom.>"]))
        assert bus.create_consumer(ConsumerConfig(name="c1", stream="CUSTOM"))

    def test_get_stream_state(self, bus):
        bus.publish("vessel.nav.position", {"lat": 31.0})
        state = bus.get_stream_state("VESSEL_NAV")
        assert state is not None
        assert state["messages"] >= 1

    def test_get_stream_state_nonexistent(self, bus):
        assert bus.get_stream_state("NONEXISTENT") is None

    def test_check_backpressure(self, bus):
        warnings = bus.check_backpressure()
        assert isinstance(warnings, dict)

    def test_get_status(self, bus):
        status = bus.get_status()
        assert status["name"] == "nats_event_bus"
        assert "stats" in status
        assert "streams" in status

    def test_shutdown(self, bus):
        assert bus.shutdown()
        assert not bus._initialized

    def test_publish_errors_tracked(self, bus):
        def bad_callback(msg):
            raise ValueError("test error")
        bus.subscribe("vessel.safety.>", bad_callback)
        bus.publish("vessel.safety.alert", {"alert": True})
        assert bus._stats["errors"] >= 1
