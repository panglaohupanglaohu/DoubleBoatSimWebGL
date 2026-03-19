#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Storage Module Unit Tests
"""

import os
import tempfile
import shutil
from datetime import datetime

from backend.storage.event_store import JSONLStore, SQLiteStore, get_store
from storage.cloud_sync import get_adapter


# ───────────────────── JSONLStore ─────────────────────


class TestJSONLStore:
    def _make_store(self, tmp):
        return JSONLStore({"storage_path": tmp, "max_events": 10})

    def _sample_event(self, eid="evt-1", etype="navigation_event"):
        return {
            "id": eid,
            "timestamp": "2026-03-17T04:00:00",
            "event_type": etype,
            "source": "intelligent_navigation",
            "payload": {"lat": 31.23},
            "confidence": 0.95,
        }

    def test_save_and_load(self, tmp_path):
        store = self._make_store(str(tmp_path))
        assert store.save_event(self._sample_event())
        events = store.load_events("navigation_event", limit=10)
        assert len(events) == 1
        assert events[0]["id"] == "evt-1"

    def test_save_multiple_types(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event("e1", "navigation_event"))
        store.save_event(self._sample_event("e2", "engine_event"))
        assert len(store.load_events(limit=10)) == 2
        assert len(store.load_events("navigation_event", limit=10)) == 1
        assert len(store.load_events("engine_event", limit=10)) == 1

    def test_save_events_batch(self, tmp_path):
        store = self._make_store(str(tmp_path))
        events = [self._sample_event(f"e{i}", "test_event") for i in range(5)]
        assert store.save_events(events)
        loaded = store.load_events("test_event", limit=10)
        assert len(loaded) == 5

    def test_clear_by_type(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event("e1", "navigation_event"))
        store.save_event(self._sample_event("e2", "engine_event"))
        assert store.clear_events("navigation_event")
        assert len(store.load_events("navigation_event", limit=10)) == 0
        assert len(store.load_events("engine_event", limit=10)) == 1

    def test_clear_all(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event("e1", "navigation_event"))
        store.save_event(self._sample_event("e2", "engine_event"))
        assert store.clear_events()
        assert len(store.load_events(limit=10)) == 0

    def test_load_events_limit(self, tmp_path):
        store = self._make_store(str(tmp_path))
        for i in range(8):
            store.save_event(self._sample_event(f"e{i}", "test_event"))
        loaded = store.load_events("test_event", limit=3)
        assert len(loaded) == 3

    def test_get_info(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event())
        info = store.get_info()
        assert info["storage_path"] == str(tmp_path)
        assert info["max_events"] == 10
        assert info["file_count"] >= 1

    def test_load_events_by_time(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event({
            "id": "e1",
            "timestamp": "2026-03-17T04:00:00",
            "event_type": "test_event",
            "source": "test",
            "payload": {},
        })
        store.save_event({
            "id": "e2",
            "timestamp": "2026-03-17T06:00:00",
            "event_type": "test_event",
            "source": "test",
            "payload": {},
        })
        results = store.load_events_by_time(
            datetime(2026, 3, 17, 3, 0),
            datetime(2026, 3, 17, 5, 0),
        )
        assert len(results) >= 1


# ───────────────────── SQLiteStore ─────────────────────


class TestSQLiteStore:
    def _make_store(self, tmp):
        return SQLiteStore({"db_path": os.path.join(tmp, "events.db")})

    def _sample_event(self, eid="evt-1", etype="navigation_event"):
        return {
            "id": eid,
            "timestamp": "2026-03-17T04:00:00",
            "event_type": etype,
            "source": "intelligent_navigation",
            "payload": {"lat": 31.23},
            "confidence": 0.95,
        }

    def test_save_and_load(self, tmp_path):
        store = self._make_store(str(tmp_path))
        assert store.save_event(self._sample_event())
        events = store.load_events("navigation_event", limit=10)
        assert len(events) == 1
        assert events[0]["source"] == "intelligent_navigation"

    def test_save_events_batch(self, tmp_path):
        store = self._make_store(str(tmp_path))
        events = [self._sample_event(f"e{i}", "test_event") for i in range(5)]
        assert store.save_events(events)
        loaded = store.load_events("test_event", limit=10)
        assert len(loaded) == 5

    def test_filter_by_type(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event("e1", "navigation_event"))
        store.save_event(self._sample_event("e2", "engine_event"))
        assert len(store.load_events("navigation_event", limit=10)) == 1
        assert len(store.load_events("engine_event", limit=10)) == 1

    def test_clear_by_type(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event("e1", "navigation_event"))
        store.save_event(self._sample_event("e2", "engine_event"))
        assert store.clear_events("navigation_event")
        assert len(store.load_events("navigation_event", limit=10)) == 0
        assert len(store.load_events("engine_event", limit=10)) == 1

    def test_clear_all(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event("e1", "navigation_event"))
        store.save_event(self._sample_event("e2", "engine_event"))
        assert store.clear_events()
        assert len(store.load_events(limit=10)) == 0

    def test_load_events_limit(self, tmp_path):
        store = self._make_store(str(tmp_path))
        for i in range(8):
            store.save_event(self._sample_event(f"e{i}", "test_event"))
        loaded = store.load_events("test_event", limit=3)
        assert len(loaded) == 3

    def test_load_events_by_time(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event({
            "id": "e1",
            "timestamp": "2026-03-17T04:00:00",
            "event_type": "test_event",
            "source": "test",
            "payload": {},
        })
        store.save_event({
            "id": "e2",
            "timestamp": "2026-03-17T06:00:00",
            "event_type": "test_event",
            "source": "test",
            "payload": {},
        })
        results = store.load_events_by_time(
            datetime(2026, 3, 17, 3, 0),
            datetime(2026, 3, 17, 5, 0),
        )
        assert len(results) >= 1

    def test_wal_mode_enabled(self, tmp_path):
        store = self._make_store(str(tmp_path))
        import sqlite3
        conn = sqlite3.connect(os.path.join(str(tmp_path), "events.db"))
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode == "wal"

    def test_get_info(self, tmp_path):
        store = self._make_store(str(tmp_path))
        store.save_event(self._sample_event())
        info = store.get_info()
        assert "db_path" in info
        assert "wal_enabled" in info
        assert info["wal_enabled"] is True


# ───────────────────── get_store factory ─────────────────────


class TestGetStoreFactory:
    def test_create_jsonl(self, tmp_path):
        store = get_store("jsonl", {"storage_path": str(tmp_path)})
        assert isinstance(store, JSONLStore)

    def test_create_sqlite(self, tmp_path):
        store = get_store("sqlite", {"db_path": os.path.join(str(tmp_path), "test.db")})
        assert isinstance(store, SQLiteStore)


# ───────────────────── LocalFileAdapter ─────────────────────


class TestLocalFileAdapter:
    def test_upload_and_list(self, tmp_path):
        adapter = get_adapter("local", {"storage_path": str(tmp_path)})
        event = {
            "id": "evt-local-1",
            "timestamp": "2026-03-18T09:00:00",
            "event_type": "test_event",
            "payload": {"value": 42},
        }
        assert adapter.upload_event(event, "test_event")
        listed = adapter.list_events("test_event", limit=10)
        assert len(listed) >= 1

    def test_upload_batch(self, tmp_path):
        adapter = get_adapter("local", {"storage_path": str(tmp_path)})
        events = [
            {"id": f"evt-{i}", "timestamp": "2026-03-18T09:00:00", "event_type": "test_event", "payload": {}}
            for i in range(3)
        ]
        assert adapter.upload_batch(events, "test_event")
        listed = adapter.list_events("test_event", limit=10)
        assert len(listed) >= 3

    def test_bucket_info(self, tmp_path):
        adapter = get_adapter("local", {"storage_path": str(tmp_path)})
        info = adapter.get_bucket_info()
        assert info["available"] is True
        assert info["type"] == "local"
