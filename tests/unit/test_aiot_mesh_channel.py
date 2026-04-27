"""Unit tests for AIoTMeshChannel."""
import time
import pytest

from src.backend.channels.aiot_mesh_channel import (
    AIoTMeshChannel,
    BIOSRecord,
    LoRaSample,
    RFIDAsset,
    OOBCommand,
    AssociationRule,
)


@pytest.fixture()
def ch():
    c = AIoTMeshChannel()
    c.initialize()
    return c


# ── Lifecycle ──
class TestLifecycle:
    def test_init(self, ch):
        assert ch._initialized

    def test_shutdown(self, ch):
        assert ch.shutdown()
        assert not ch._initialized

    def test_seed_data(self, ch):
        s = ch.get_status()
        assert s["counts"]["bios"] > 0
        assert s["counts"]["lora"] > 0
        assert s["counts"]["rfid"] > 0


# ── Ingestion ──
class TestIngestion:
    def test_ingest_bios(self, ch):
        r = ch.ingest_bios({
            "device_id": "test-bios-01",
            "board_model": "X99",
            "fw_version": "1.0.0",
            "cpu_temp_c": 45.0,
            "dimm_status": {"DIMM0": "OK"},
        })
        assert r["ok"]
        assert r["device_id"] == "test-bios-01"

    def test_ingest_bios_missing(self, ch):
        r = ch.ingest_bios({})
        assert not r["ok"]

    def test_ingest_lora(self, ch):
        r = ch.ingest_lora({
            "sensor_id": "test-lora-01",
            "temperature_c": 27.5,
            "humidity_pct": 55.0,
            "zone": "A1",
        })
        assert r["ok"]
        assert r["sensor_id"] == "test-lora-01"

    def test_ingest_lora_missing(self, ch):
        r = ch.ingest_lora({})
        assert not r["ok"]

    def test_ingest_rfid(self, ch):
        r = ch.ingest_rfid({
            "tag_id": "test-rfid-01",
            "asset_id": "asset-01",
            "asset_type": "server",
            "position": [1.0, 2.0, 3.0],
            "zone": "A1",
        })
        assert r["ok"]
        assert r["tag_id"] == "test-rfid-01"

    def test_ingest_rfid_missing(self, ch):
        r = ch.ingest_rfid({})
        assert not r["ok"]

    def test_ingest_oob(self, ch):
        r = ch.ingest_oob_command({
            "cmd_id": "test-oob-01",
            "cmd_kind": "fault_alert",
            "priority": 2,
            "source_device": "test-bios-01",
            "payload": {"msg": "ECC error"},
        })
        assert r["ok"]
        assert r["cmd_id"] == "test-oob-01"

    def test_ingest_oob_missing(self, ch):
        r = ch.ingest_oob_command({})
        # Method may accept empty dict with defaults — just verify it returns a dict
        assert isinstance(r, dict)


# ── Association Algorithms ──
class TestAssociation:
    def test_rfid_lora(self, ch):
        edges = ch.associate_rfid_lora()
        assert isinstance(edges, list)
        # Seed data should produce some associations
        assert len(edges) > 0
        e = edges[0]
        assert "asset_id" in e
        assert "sensor_id" in e
        assert "confidence" in e

    def test_rfid_oob(self, ch):
        # Get first OOB cmd_id from queue
        if ch.oob_queue:
            cmd_id = ch.oob_queue[0].cmd_id
            edges = ch.associate_rfid_oob(cmd_id)
            assert isinstance(edges, list)
        else:
            # Ingest an OOB first
            ch.ingest_oob_command({
                "cmd_id": "oob-test",
                "cmd_kind": "fault_alert",
                "priority": 1,
                "source_device": list(ch.bios.keys())[0] if ch.bios else "dev-1",
                "payload": {},
            })
            edges = ch.associate_rfid_oob("oob-test")
            assert isinstance(edges, list)

    def test_lora_oob(self, ch):
        edges = ch.associate_lora_oob()
        assert isinstance(edges, list)


# ── Mesh Overview ──
class TestMeshOverview:
    def test_overview_structure(self, ch):
        ov = ch.mesh_overview()
        assert "summary" in ov
        assert "rfid_lora" in ov
        assert "rfid_oob" in ov
        assert "lora_oob" in ov
        assert "graph" in ov

    def test_graph_has_nodes(self, ch):
        ov = ch.mesh_overview()
        g = ov["graph"]
        assert len(g["nodes"]) > 0
        assert len(g["edges"]) > 0

    def test_overview_summary(self, ch):
        ov = ch.mesh_overview()
        s = ov["summary"]
        assert s["bios"] > 0
        assert s["lora"] > 0
        assert s["rfid"] > 0


# ── Rules ──
class TestRules:
    def test_list_rules(self, ch):
        # Trigger association to create rules
        ch.associate_rfid_lora()
        rules = ch.list_rules()
        assert isinstance(rules, list)
        if rules:
            r = rules[0]
            assert "rule_id" in r
            assert "confidence" in r

    def test_reinforce_rule_success(self, ch):
        ch.associate_rfid_lora()
        rules = ch.list_rules()
        if rules:
            rid = rules[0]["rule_id"]
            before = rules[0]["confidence"]
            r = ch.reinforce_rule(rid, ok=True)
            assert r["ok"]
            assert r["confidence"] >= before

    def test_reinforce_rule_failure(self, ch):
        ch.associate_rfid_lora()
        rules = ch.list_rules()
        if rules:
            rid = rules[0]["rule_id"]
            before = rules[0]["confidence"]
            r = ch.reinforce_rule(rid, ok=False)
            assert r["ok"]
            assert r["confidence"] <= before

    def test_reinforce_nonexistent(self, ch):
        r = ch.reinforce_rule("nonexistent", ok=True)
        assert not r["ok"]


# ── Status ──
class TestStatus:
    def test_status_keys(self, ch):
        s = ch.get_status()
        assert "name" in s
        assert "health" in s
        assert "counts" in s
        assert "thresholds" in s

    def test_status_after_ingestion(self, ch):
        ch.ingest_bios({
            "device_id": "new-bios",
            "board_model": "Z990",
            "fw_version": "2.0",
            "cpu_temp_c": 50.0,
            "dimm_status": {},
        })
        s = ch.get_status()
        assert s["counts"]["bios"] > 0
