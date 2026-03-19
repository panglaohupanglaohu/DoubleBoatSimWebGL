# -*- coding: utf-8 -*-
"""
集成测试：NMEA2000 解析器 -> 智能机舱数据流
"""

import sys
import os
import pytest
from datetime import datetime

# sys.path is handled by PYTHONPATH

from backend.channels.nmea2000_parser import NMEA2000ParserChannel
from backend.channels.intelligent_engine import IntelligentEngineChannel
from pydantic import BaseModel
from types import SimpleNamespace

class DummyRawMessage:
    def __init__(self, pgn, fields):
        self.pgn = pgn
        self.fields = fields
        self.timestamp = datetime.now()

@pytest.fixture
def parser():
    channel = NMEA2000ParserChannel()
    channel.initialize()
    return channel

@pytest.fixture
def engine():
    channel = IntelligentEngineChannel()
    channel.initialize()
    # Clear seeded data
    channel.snapshots.clear()
    return channel

def test_nmea2000_to_engine_pipeline(parser, engine):
    # Simulate receiving raw CAN messages
    # PGN 127488: Engine Parameters, Rapid Update (speed)
    msg_127488 = DummyRawMessage(
        pgn=127488,
        fields={"engine_instance": 0, "speed": 780.0}
    )
    
    # PGN 127489: Engine Parameters, Dynamic
    msg_127489 = DummyRawMessage(
        pgn=127489,
        fields={
            "engine_instance": 0, 
            "engine_load": 45.0, 
            "fuel_rate": 320.0,
            "oil_pressure": 400000.0, # 4 bar in Pascals
            "coolant_temp": 353.15    # 80 C
        }
    )
    
    # Normally parser passes data to a pub/sub. Since we don't have a full pub/sub tied dynamically here,
    # we manually chain them.
    success_1 = engine.ingest_nmea2000_message(msg_127488)
    assert success_1 is False # Need more data for a snapshot

    success_2 = engine.ingest_nmea2000_message(msg_127489)
    assert success_2 is True # Snapshot generated
    
    status = engine.get_status()
    assert status["latest_snapshot"] is not None
    assert status["latest_snapshot"]["rpm"] == 780.0
    assert status["latest_snapshot"]["load"] == 45.0
    assert status["latest_snapshot"]["oil_pressure"] == 4.0
    assert status["latest_snapshot"]["coolant_temp"] == 80.0
    assert status["latest_snapshot"]["fuel_rate"] == 320.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
