# -*- coding: utf-8 -*-
"""
MOB REST API 路由测试

使用 FastAPI TestClient 验证:
  - GET  /api/mob/status
  - POST /api/mob/activate
  - POST /api/mob/deactivate
"""

import sys
import os

# Ensure src/backend is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "backend"))

import pytest
from unittest.mock import patch, MagicMock

from channels.man_overboard import ManOverboardChannel


def _make_registered_channel():
    """Create and register a MOB channel in the default registry."""
    ch = ManOverboardChannel()
    ch.initialize()
    return ch


class TestMOBApiRoutes:
    """MOB REST API 端点测试。"""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Set up TestClient with a registered MOB channel."""
        # Patch the registry to return our channel
        self.mob_channel = _make_registered_channel()

        # We need to import main module and create a TestClient
        from main import app
        from fastapi.testclient import TestClient

        self.client = TestClient(app)

        # Patch get_default_registry to return our channel
        mock_registry = MagicMock()
        mock_registry.get = lambda name: self.mob_channel if name == "man_overboard" else None

        self._patcher = patch(
            "channels.marine_base.get_default_registry",
            return_value=mock_registry,
        )
        self._patcher.start()
        yield
        self._patcher.stop()

    def test_mob_status_endpoint(self):
        """GET /api/mob/status should return MOB status."""
        resp = self.client.get("/api/mob/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "man_overboard"
        assert "result" in data
        assert data["result"]["mob_active"] is False

    def test_mob_activate_endpoint(self):
        """POST /api/mob/activate should activate MOB with coordinates."""
        resp = self.client.post(
            "/api/mob/activate",
            json={"lat": 31.23, "lon": 121.47},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["status"] == "mob_activated"
        assert data["result"]["position"]["lat"] == 31.23

    def test_mob_deactivate_endpoint(self):
        """POST /api/mob/deactivate should cancel MOB alert."""
        # First activate
        self.mob_channel.activate_mob(31.23, 121.47)
        # Then deactivate
        resp = self.client.post("/api/mob/deactivate")
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["status"] == "mob_deactivated"

    def test_mob_activate_missing_fields(self):
        """POST /api/mob/activate with missing fields should return 422."""
        resp = self.client.post("/api/mob/activate", json={"lat": 31.23})
        assert resp.status_code == 422

    def test_mob_full_lifecycle(self):
        """Full API lifecycle: status → activate → status → deactivate → status."""
        # Initial status
        r1 = self.client.get("/api/mob/status")
        assert r1.json()["result"]["mob_active"] is False

        # Activate
        r2 = self.client.post("/api/mob/activate", json={"lat": 31.23, "lon": 121.47})
        assert r2.json()["result"]["status"] == "mob_activated"

        # Status after activate
        r3 = self.client.get("/api/mob/status")
        assert r3.json()["result"]["mob_active"] is True

        # Deactivate
        r4 = self.client.post("/api/mob/deactivate")
        assert r4.json()["result"]["status"] == "mob_deactivated"

        # Status after deactivate
        r5 = self.client.get("/api/mob/status")
        assert r5.json()["result"]["mob_active"] is False
