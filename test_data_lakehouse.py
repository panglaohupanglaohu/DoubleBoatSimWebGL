#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Lakehouse Module Unit Tests
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, 'src')

from backend.storage.data_lakehouse import DataLakehouse, create_lakehouse

def test_data_lakehouse():
    """测试 DataLakehouse"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create lakehouse with SQLite store
        config = {
            "store_type": "sqlite",
            "store_config": {
                "db_path": os.path.join(temp_dir, "events.db")
            },
            "cloud_type": "local",  # Use local file adapter for cloud
            "cloud_config": {
                "storage_path": os.path.join(temp_dir, "cloud")
            }
        }
        
        lakehouse = create_lakehouse(config)
        
        # Get status
        status = lakehouse.get_status()
        assert status["local_store"]["available"], "Local store should be available"
        assert status["cloud_adapter"]["available"], "Cloud adapter should be available"
        
        # Save events
        event1 = {
            "id": "evt-1",
            "timestamp": "2026-03-17T04:00:00",
            "event_type": "navigation_event",
            "source": "intelligent_navigation",
            "payload": {"position": {"lat": 31.23, "lng": 121.47}},
            "confidence": 0.95
        }
        
        event2 = {
            "id": "evt-2",
            "timestamp": "2026-03-17T04:01:00",
            "event_type": "engine_event",
            "source": "intelligent_engine",
            "payload": {"rpm": 120, "temperature": 85},
            "confidence": 0.98
        }
        
        assert lakehouse.save_event(event1), "Failed to save event1"
        assert lakehouse.save_event(event2), "Failed to save event2"
        
        # Flush manually
        lakehouse._flush_buffer_to_local()
        
        # Query events
        events = lakehouse.query_events(limit=10)
        assert len(events) >= 2, f"Expected at least 2 events, got {len(events)}"
        
        # Query by event type
        nav_events = lakehouse.query_events("navigation_event", limit=10)
        assert len(nav_events) >= 1, f"Expected at least 1 nav event, got {len(nav_events)}"
        
        print("✅ DataLakehouse tests passed")
        print(f"   Total events in lakehouse: {len(events)}")
        print(f"   Navigation events: {len(nav_events)}")
        print(f"   Event types: {set(e.get('event_type') for e in events)}")
        
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_lakehouse_status():
    """测试湖仓状态查询"""
    lakehouse = create_lakehouse({
        "store_type": "jsonl",
        "store_config": {
            "storage_path": "./storage/test_events"
        }
    })
    
    status = lakehouse.get_status()
    print("✅ Lakehouse status test passed")
    print(f"   Local store type: {status['local_store']['type']}")
    print(f"   Cloud adapter: {status['cloud_adapter']['type']}")
    print(f"   Buffer size: {status['buffer_size']}")
    
    return True


if __name__ == "__main__":
    print("=== Data Lakehouse Module Unit Tests ===\n")
    
    try:
        test_data_lakehouse()
        print()
        test_lakehouse_status()
        
        print("\n=== All Lakehouse Tests Passed ===")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
