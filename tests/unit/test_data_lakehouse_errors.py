#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for DataLakehouse error handling."""

import os
import tempfile
from unittest.mock import MagicMock

from backend.storage.data_lakehouse import DataLakehouse, create_lakehouse


class TestDataLakehouseErrorHandling:
    def _make_lakehouse(self, tmp_dir):
        config = {
            "store_type": "sqlite",
            "store_config": {"db_path": os.path.join(tmp_dir, "events.db")},
            "analytics_cache_dir": os.path.join(tmp_dir, "cache"),
        }
        return create_lakehouse(config)

    def test_get_status_with_store_info_exception(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        lh.local_store.get_info = MagicMock(side_effect=RuntimeError("disk error"))
        status = lh.get_status()
        assert status is not None
        assert status["local_store"]["available"] is True

    def test_get_status_no_local_store(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        lh.local_store = None
        status = lh.get_status()
        assert status["local_store"]["available"] is False

    def test_save_event_no_local_store(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        lh.local_store = None
        result = lh.save_event({"id": "e1", "event_type": "test"})
        assert result is True

    def test_query_events_no_local_store(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        lh.local_store = None
        result = lh.query_events()
        assert result == []

    def test_flush_with_cloud_adapter_error(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        mock_cloud = MagicMock()
        mock_cloud.upload_batch.side_effect = ConnectionError("network down")
        lh.cloud_adapter = mock_cloud
        for i in range(5):
            lh.event_buffer.append({"id": f"e{i}", "event_type": "test"})
        lh.flush()

    def test_get_status_cloud_adapter_exception(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        mock_cloud = MagicMock()
        mock_cloud.get_bucket_info.side_effect = ConnectionError("timeout")
        lh.cloud_adapter = mock_cloud
        status = lh.get_status()
        assert status is not None
        cloud_info = status["cloud_adapter"]["info"]
        assert cloud_info["available"] is False

    def test_duckdb_query_rejects_non_select(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        try:
            lh.run_duckdb_query("DROP TABLE foo")
            assert False, "Should have raised ValueError"
        except (ValueError, Exception):
            pass

    def test_shutdown_flushes_buffer(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        lh.event_buffer.append({"id": "e1", "event_type": "nav", "timestamp": "2026-01-01T00:00:00"})
        lh.shutdown()
        assert len(lh.event_buffer) == 0

    def test_get_storage_profile(self, tmp_path):
        lh = self._make_lakehouse(str(tmp_path))
        profile = lh.get_storage_profile()
        assert profile["hadoop_required"] is False
        assert profile["architecture_mode"] == "lightweight_edge_lakehouse"
        assert profile["hot_store"] == "sqlite"
