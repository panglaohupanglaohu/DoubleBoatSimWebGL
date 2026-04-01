# -*- coding: utf-8 -*-
"""
Tests for L3: Weather Routing Channel — 气象导航
"""

import asyncio
import pytest
from channels.weather_routing_channel import WeatherRoutingChannel


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def channel():
    ch = WeatherRoutingChannel()
    ch.initialize()
    return ch


# ---- 1. 实例化和默认状态 ----

class TestInstantiationAndStatus:
    def test_default_status(self, channel):
        status = channel.get_status()
        assert status["name"] == "weather_routing"
        assert status["active"] is True
        assert status["forecast_count"] == 0
        assert status["alert_level"] == "normal"
        assert status["recommended_routes"] == 0
        assert status["current_weather"] == {}

    def test_uninitialized_channel(self):
        ch = WeatherRoutingChannel()
        status = ch.get_status()
        assert status["active"] is False
        assert status["forecast_count"] == 0

    def test_shutdown(self, channel):
        result = channel.shutdown()
        assert result is True
        status = channel.get_status()
        assert status["active"] is False


# ---- 2. weather_forecast 事件 ----

class TestWeatherForecast:
    def test_cache_forecast(self, channel):
        event = {
            "type": "weather_forecast",
            "region": "east_china_sea",
            "wind_speed": 15.0,
            "wave_height": 1.5,
            "visibility": 8.0,
        }
        result = _run(channel.process_event(event))
        assert result["status"] == "cached"
        assert result["region"] == "east_china_sea"
        assert result["forecast_count"] == 1

    def test_cache_multiple_regions(self, channel):
        for region in ["north", "south", "east"]:
            _run(channel.process_event({
                "type": "weather_forecast",
                "region": region,
                "wind_speed": 10.0,
            }))
        status = channel.get_status()
        assert status["forecast_count"] == 3

    def test_overwrite_same_region(self, channel):
        for wind in [10.0, 20.0]:
            _run(channel.process_event({
                "type": "weather_forecast",
                "region": "same",
                "wind_speed": wind,
            }))
        status = channel.get_status()
        assert status["forecast_count"] == 1


# ---- 3. route_candidate 事件 ----

class TestRouteCandidate:
    def test_evaluate_route(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "test",
            "wind_speed": 10.0,
            "wave_height": 1.0,
            "visibility": 10.0,
        }))
        result = _run(channel.process_event({
            "type": "route_candidate",
            "waypoints": [
                {"lat": 31.0, "lon": 121.0},
                {"lat": 32.0, "lon": 122.0},
            ],
        }))
        assert result["status"] == "evaluated"
        assert result["waypoints_count"] == 2
        assert "risk" in result
        assert "recommendations" in result

    def test_route_no_waypoints(self, channel):
        result = _run(channel.process_event({
            "type": "route_candidate",
            "waypoints": [],
        }))
        assert result["status"] == "error"
        assert "no waypoints" in result["reason"]

    def test_low_risk_route_added_to_recommended(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "calm",
            "wind_speed": 5.0,
            "wave_height": 0.5,
            "visibility": 10.0,
        }))
        _run(channel.process_event({
            "type": "route_candidate",
            "waypoints": [{"lat": 31.0, "lon": 121.0}],
        }))
        status = channel.get_status()
        assert status["recommended_routes"] >= 1


# ---- 4. weather_alert 事件 ----

class TestWeatherAlert:
    def test_alert_warning(self, channel):
        result = _run(channel.process_event({
            "type": "weather_alert",
            "severity": "warning",
            "message": "Tropical storm approaching",
        }))
        assert result["status"] == "alert_received"
        assert result["alert_level"] == "warning"

    def test_alert_critical_sets_health(self, channel):
        _run(channel.process_event({
            "type": "weather_alert",
            "severity": "critical",
            "message": "Typhoon imminent",
        }))
        status = channel.get_status()
        assert status["alert_level"] == "critical"


# ---- 5. 风险评估逻辑 ----

class TestRiskAssessment:
    def test_high_wind_risk(self, channel):
        """风速 > 40kn → 高风险"""
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "storm",
            "wind_speed": 50.0,
            "wave_height": 2.0,
            "visibility": 5.0,
        }))
        status = channel.get_status()
        assert status["current_weather"]["risk_level"] == "high"

    def test_high_wave_risk(self, channel):
        """浪高 > 4m → 中风险"""
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "swell",
            "wind_speed": 15.0,
            "wave_height": 5.0,
            "visibility": 8.0,
        }))
        status = channel.get_status()
        assert status["current_weather"]["risk_level"] == "medium"

    def test_low_visibility_risk(self, channel):
        """能见度 < 1nm → 高风险"""
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "fog",
            "wind_speed": 5.0,
            "wave_height": 1.0,
            "visibility": 0.5,
        }))
        status = channel.get_status()
        assert status["current_weather"]["risk_level"] == "high"

    def test_normal_weather_low_risk(self, channel):
        """正常天气 → 低风险"""
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "calm",
            "wind_speed": 10.0,
            "wave_height": 1.0,
            "visibility": 10.0,
        }))
        status = channel.get_status()
        assert status["current_weather"]["risk_level"] == "low"

    def test_evaluate_route_empty_waypoints(self, channel):
        risk = channel.evaluate_route_weather_risk([])
        assert risk["risk_score"] == 0.0
        assert risk["risk_level"] == "low"

    def test_evaluate_route_high_wind(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "x",
            "wind_speed": 60.0,
            "wave_height": 1.0,
            "visibility": 10.0,
        }))
        risk = channel.evaluate_route_weather_risk([{"lat": 0, "lon": 0}])
        assert risk["risk_score"] >= 50
        assert risk["risk_level"] in ("high", "critical")

    def test_level_from_score(self):
        assert WeatherRoutingChannel._level_from_score(0) == "low"
        assert WeatherRoutingChannel._level_from_score(24) == "low"
        assert WeatherRoutingChannel._level_from_score(25) == "medium"
        assert WeatherRoutingChannel._level_from_score(49) == "medium"
        assert WeatherRoutingChannel._level_from_score(50) == "high"
        assert WeatherRoutingChannel._level_from_score(74) == "high"
        assert WeatherRoutingChannel._level_from_score(75) == "critical"
        assert WeatherRoutingChannel._level_from_score(100) == "critical"

    def test_compute_point_risk_level(self):
        assert WeatherRoutingChannel._compute_point_risk_level(
            {"wind_speed": 50, "wave_height": 1, "visibility": 10}
        ) == "high"
        assert WeatherRoutingChannel._compute_point_risk_level(
            {"wind_speed": 30, "wave_height": 5, "visibility": 10}
        ) == "medium"
        assert WeatherRoutingChannel._compute_point_risk_level(
            {"wind_speed": 10, "wave_height": 1, "visibility": 0.5}
        ) == "high"
        assert WeatherRoutingChannel._compute_point_risk_level(
            {"wind_speed": 10, "wave_height": 1, "visibility": 10}
        ) == "low"


# ---- 6. generate_weather_recommendations ----

class TestWeatherRecommendations:
    def test_no_weather_data(self, channel):
        recs = channel.generate_weather_recommendations()
        assert len(recs) == 1
        assert "无可用天气数据" in recs[0]

    def test_high_wind_recommendation(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "t",
            "wind_speed": 45.0,
            "wave_height": 1.0,
            "visibility": 10.0,
        }))
        recs = channel.generate_weather_recommendations()
        assert any("风速" in r for r in recs)

    def test_high_wave_recommendation(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "t",
            "wind_speed": 10.0,
            "wave_height": 5.0,
            "visibility": 10.0,
        }))
        recs = channel.generate_weather_recommendations()
        assert any("浪高" in r for r in recs)

    def test_low_visibility_recommendation(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "t",
            "wind_speed": 10.0,
            "wave_height": 1.0,
            "visibility": 0.3,
        }))
        recs = channel.generate_weather_recommendations()
        assert any("能见度" in r for r in recs)

    def test_normal_conditions_recommendation(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "t",
            "wind_speed": 10.0,
            "wave_height": 1.0,
            "visibility": 10.0,
        }))
        recs = channel.generate_weather_recommendations()
        assert any("适合航行" in r for r in recs)

    def test_max_three_recommendations(self, channel):
        _run(channel.process_event({
            "type": "weather_forecast",
            "region": "t",
            "wind_speed": 50.0,
            "wave_height": 6.0,
            "visibility": 0.3,
        }))
        recs = channel.generate_weather_recommendations()
        assert len(recs) <= 3


# ---- 7. 未知事件类型 ----

class TestUnknownEvent:
    def test_unknown_event_type(self, channel):
        result = _run(channel.process_event({"type": "alien_invasion"}))
        assert result["status"] == "ignored"

    def test_empty_type(self, channel):
        result = _run(channel.process_event({}))
        assert result["status"] == "ignored"


# ---- 8. 空数据输入 ----

class TestEmptyData:
    def test_forecast_no_region(self, channel):
        result = _run(channel.process_event({
            "type": "weather_forecast",
        }))
        assert result["status"] == "cached"
        assert result["region"] == "unknown"

    def test_route_candidate_missing_waypoints_key(self, channel):
        result = _run(channel.process_event({
            "type": "route_candidate",
        }))
        assert result["status"] == "error"

    def test_alert_no_severity(self, channel):
        result = _run(channel.process_event({
            "type": "weather_alert",
        }))
        assert result["status"] == "alert_received"
        assert result["alert_level"] == "warning"

    def test_score_point_no_weather(self, channel):
        score = channel._score_point(31.0, 121.0)
        assert score == 0.0

    def test_start_stop(self, channel):
        _run(channel.start())
        status = channel.get_status()
        assert status["active"] is True
        _run(channel.stop())
        status = channel.get_status()
        assert status["active"] is False
