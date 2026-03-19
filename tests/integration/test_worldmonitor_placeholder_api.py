#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorldMonitor API 集成测试 — 使用 starlette TestClient (无需启动服务器)
"""

import pytest
from starlette.testclient import TestClient
from main import app


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_worldmonitor_ais_endpoint(client):
    response = client.get("/api/v1/worldmonitor/ais")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert "targets" in data or "count" in data


def test_worldmonitor_weather_endpoint(client):
    response = client.get("/api/v1/worldmonitor/weather?lat=31.23&lng=121.47")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data


def test_worldmonitor_ports_endpoint(client):
    response = client.get("/api/v1/worldmonitor/ports")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data


def test_worldmonitor_routes_endpoint(client):
    response = client.get("/api/v1/worldmonitor/routes")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data


def test_dashboard_contains_worldmonitor_section(client):
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "worldmonitor" in data
    wm = data["worldmonitor"]
    assert "endpoints" in wm
    assert "/api/v1/worldmonitor/ais" == wm["endpoints"]["ais"]
