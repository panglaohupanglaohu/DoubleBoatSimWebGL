# -*- coding: utf-8 -*-
"""
Marine Channels Package

船舶工程监控 Channel 模块包

This package provides specialized channels for marine engineering monitoring:
- Navigation Data: GPS, compass, depth, speed sensors
- Cargo Monitor: Reefer containers, liquid bulk tanks
- Weather Routing: Meteorological navigation
- Vessel AIS: AIS target tracking
- Engine Monitor: Main engine parameters
- Power Management: Electrical power systems
- NMEA Parser: NMEA 0183 protocol parsing
"""

from .base import Channel
from .navigation_data import NavigationDataChannel
from .cargo_monitor import CargoMonitorChannel, CargoType
from .weather_routing import WeatherRoutingChannel, RoutingStrategy
from .vessel_ais import VesselAISChannel, VesselPosition
from .engine_monitor import EngineMonitorChannel, AlarmLevel
from .power_management import PowerManagementChannel
from .nmea_parser import NMEAParserChannel

__all__ = [
    'Channel',
    'NavigationDataChannel',
    'CargoMonitorChannel',
    'CargoType',
    'WeatherRoutingChannel',
    'RoutingStrategy',
    'VesselAISChannel',
    'VesselPosition',
    'EngineMonitorChannel',
    'AlarmLevel',
    'PowerManagementChannel',
    'NMEAParserChannel',
]
