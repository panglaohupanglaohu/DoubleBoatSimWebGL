# Skills package for marine_engineer_agent
"""
Marine Engineer Skills Module

This package provides various marine engineering skills including:
- Channels: Data integration channels for navigation, cargo, weather, etc.
- Propulsion: Ship propulsion system simulation
- Twins Controller: Digital twin control capabilities
- Hydrodynamics: Hydrodynamic calculations
- Stability Curves: Ship stability analysis
- Fault Diagnosis: Fault detection and diagnosis
- Performance Analysis: Performance benchmarking and caching
"""

from . import channels
from .channels.base import Channel

__all__ = ['channels', 'Channel']
