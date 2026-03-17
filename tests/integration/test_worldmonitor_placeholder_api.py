#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorldMonitor 方案层占位 API 集成测试
"""

import requests

import os

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:18085")


def test_worldmonitor_ais_placeholder():
    response = requests.get(f"{BASE_URL}/api/v1/worldmonitor/ais")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "placeholder"
    assert data["kind"] == "ais"
    assert data["connected"] is False
    assert "targets" in data


def test_worldmonitor_weather_placeholder():
    response = requests.get(f"{BASE_URL}/api/v1/worldmonitor/weather?lat=31.23&lng=121.47")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "placeholder"
    assert data["kind"] == "marine_weather"
    assert data["connected"] is False
    assert data["position"]["lat"] == 31.23


def test_worldmonitor_ports_placeholder():
    response = requests.get(f"{BASE_URL}/api/v1/worldmonitor/ports")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "placeholder"
    assert data["kind"] == "ports"
    assert "ports" in data


def test_worldmonitor_routes_placeholder():
    response = requests.get(f"{BASE_URL}/api/v1/worldmonitor/routes")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "placeholder"
    assert data["kind"] == "shipping_routes"
    assert "routes" in data


def test_dashboard_contains_worldmonitor_section():
    response = requests.get(f"{BASE_URL}/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "worldmonitor" in data
    wm = data["worldmonitor"]
    assert wm["mode"] == "placeholder"
    assert "endpoints" in wm
    assert "/api/v1/worldmonitor/ais" == wm["endpoints"]["ais"]
