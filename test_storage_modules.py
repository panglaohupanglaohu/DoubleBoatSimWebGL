#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Storage Module Unit Tests
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, 'src')

from backend.storage.event_store import JSONLStore, SQLiteStore, get_store

def test_jsonl_store():
    """测试 JSONLStore"""
    # Create temp dir
    temp_dir = tempfile.mkdtemp()
    
    try:
        store = JSONLStore({
            "storage_path": temp_dir,
            "max_events": 10
        })
        
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
        
        assert store.save_event(event1), "Failed to save event1"
        assert store.save_event(event2), "Failed to save event2"
        
        # Load events
        nav_events = store.load_events("navigation_event", limit=10)
        assert len(nav_events) == 1, f"Expected 1 nav event, got {len(nav_events)}"
        assert nav_events[0]["id"] == "evt-1", "Event ID mismatch"
        
        all_events = store.load_events(limit=10)
        assert len(all_events) == 2, f"Expected 2 events, got {len(all_events)}"
        
        # Clear events
        assert store.clear_events("navigation_event"), "Failed to clear navigation events"
        nav_events = store.load_events("navigation_event", limit=10)
        assert len(nav_events) == 0, "Navigation events should be empty"
        
        print("✅ JSONLStore tests passed")
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_sqlite_store():
    """测试 SQLiteStore"""
    # Create temp db
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "events.db")
    
    try:
        store = SQLiteStore({
            "db_path": db_path
        })
        
        # Save events
        event1 = {
            "timestamp": "2026-03-17T04:00:00",
            "event_type": "navigation_event",
            "source": "intelligent_navigation",
            "payload": {"position": {"lat": 31.23, "lng": 121.47}},
            "confidence": 0.95
        }
        
        event2 = {
            "timestamp": "2026-03-17T04:01:00",
            "event_type": "engine_event",
            "source": "intelligent_engine",
            "payload": {"rpm": 120, "temperature": 85},
            "confidence": 0.98
        }
        
        assert store.save_event(event1), "Failed to save event1"
        assert store.save_event(event2), "Failed to save event2"
        
        # Load events
        nav_events = store.load_events("navigation_event", limit=10)
        assert len(nav_events) == 1, f"Expected 1 nav event, got {len(nav_events)}"
        assert nav_events[0]["source"] == "intelligent_navigation", "Source mismatch"
        
        all_events = store.load_events(limit=10)
        assert len(all_events) == 2, f"Expected 2 events, got {len(all_events)}"
        
        # Clear events
        assert store.clear_events(), "Failed to clear all events"
        all_events = store.load_events(limit=10)
        assert len(all_events) == 0, "Events should be empty"
        
        print("✅ SQLiteStore tests passed")
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=== Storage Module Unit Tests ===\n")
    
    try:
        test_jsonl_store()
        print()
        test_sqlite_store()
        
        print("\n=== All Storage Tests Passed ===")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
