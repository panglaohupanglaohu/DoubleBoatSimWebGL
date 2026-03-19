#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Lakehouse Module Unit Tests
"""

import os
import tempfile
import shutil
import asyncio
from io import BytesIO
from datetime import datetime

from backend.storage.data_lakehouse import create_lakehouse
from storage.cloud_sync import S3CompatibleAdapter

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


def test_parquet_store_round_trip():
    """测试 Parquet 存储读写。"""
    temp_dir = tempfile.mkdtemp()

    try:
        lakehouse = create_lakehouse({
            "store_type": "parquet",
            "store_config": {
                "storage_path": os.path.join(temp_dir, "parquet_events")
            }
        })

        assert lakehouse.save_event({
            "id": "evt-parquet-1",
            "timestamp": "2026-03-18T09:00:00",
            "event_type": "navigation_event",
            "source": "intelligent_navigation",
            "payload": {"cpa": 0.42, "tcpa": 12.0},
            "confidence": 0.93,
        })
        lakehouse._flush_buffer_to_local()

        events = lakehouse.query_events("navigation_event", limit=5)
        assert len(events) == 1
        assert events[0]["payload"]["cpa"] == 0.42
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_duckdb_analytics_query():
    """测试 DuckDB 即席分析接口。"""
    temp_dir = tempfile.mkdtemp()

    try:
        lakehouse = create_lakehouse({
            "store_type": "sqlite",
            "store_config": {
                "db_path": os.path.join(temp_dir, "events.db")
            },
            "analytics_cache_dir": os.path.join(temp_dir, "analytics_cache"),
        })

        lakehouse.save_batch([
            {
                "id": "evt-ana-1",
                "timestamp": "2026-03-18T09:10:00",
                "event_type": "navigation_event",
                "source": "intelligent_navigation",
                "payload": {"risk": "medium"},
                "confidence": 0.95,
            },
            {
                "id": "evt-ana-2",
                "timestamp": "2026-03-18T09:11:00",
                "event_type": "navigation_event",
                "source": "intelligent_navigation",
                "payload": {"risk": "high"},
                "confidence": 0.99,
            },
            {
                "id": "evt-ana-3",
                "timestamp": "2026-03-18T09:12:00",
                "event_type": "engine_event",
                "source": "intelligent_engine",
                "payload": {"alert": "cooling"},
                "confidence": 0.97,
            },
        ])
        lakehouse._flush_buffer_to_local()

        rows = lakehouse.run_duckdb_query(
            "SELECT event_type, COUNT(*) AS total FROM lakehouse_events GROUP BY event_type ORDER BY event_type"
        )

        assert rows == [
            {"event_type": "engine_event", "total": 1},
            {"event_type": "navigation_event", "total": 2},
        ]

        profile = lakehouse.get_storage_profile()
        assert profile["hot_store_mode"] == "wal"
        assert profile["duckdb_available"] is True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_s3_adapter_lists_and_downloads_events():
    """测试 S3 兼容适配器可列举并按时间窗口下载事件。"""

    class FakeS3Client:
        def __init__(self):
            self.objects = {
                "lake/navigation_event/2026/03/18/091000_000000.json": {
                    "payload": {
                        "id": "evt-s3-1",
                        "timestamp": "2026-03-18T09:10:00",
                        "event_type": "navigation_event",
                        "source": "intelligent_navigation",
                        "payload": {"risk": "medium"},
                    },
                    "last_modified": datetime(2026, 3, 18, 9, 10, 5),
                },
                "lake/navigation_event/2026/03/18/091500_000000.json": {
                    "payload": {
                        "id": "evt-s3-2",
                        "timestamp": "2026-03-18T09:15:00",
                        "event_type": "navigation_event",
                        "source": "intelligent_navigation",
                        "payload": {"risk": "high"},
                    },
                    "last_modified": datetime(2026, 3, 18, 9, 15, 5),
                },
            }

        def list_objects_v2(self, Bucket, Prefix, MaxKeys, ContinuationToken=None):
            contents = [
                {"Key": key, "LastModified": value["last_modified"]}
                for key, value in self.objects.items()
                if key.startswith(Prefix)
            ]
            contents.sort(key=lambda item: item["LastModified"], reverse=True)
            return {"Contents": contents[:MaxKeys], "IsTruncated": False}

        def get_object(self, Bucket, Key):
            payload = self.objects[Key]["payload"]
            return {"Body": BytesIO(__import__("json").dumps(payload).encode("utf-8"))}

        def head_bucket(self, Bucket):
            return {}

    adapter = S3CompatibleAdapter({
        "bucket_name": "test-bucket",
        "prefix": "lake",
        "endpoint_url": "http://127.0.0.1:9000",
    })
    adapter._client = FakeS3Client()

    listed = adapter.list_events("navigation_event", limit=10)
    assert len(listed) == 2
    assert listed[0]["id"] == "evt-s3-2"
    assert listed[0]["cloud_key"].endswith("091500_000000.json")

    downloaded = adapter.download_events(
        "navigation_event",
        datetime(2026, 3, 18, 9, 12, 0),
        datetime(2026, 3, 18, 9, 16, 0),
    )
    assert downloaded == [listed[0]]

    info = adapter.get_bucket_info()
    assert info["available"] is True
    assert info["endpoint_url"] == "http://127.0.0.1:9000"


def test_s3_adapter_auto_creates_bucket_when_enabled():
    """测试 S3 兼容适配器可按配置自动创建 bucket。"""

    class MissingBucketError(Exception):
        def __init__(self):
            self.response = {"Error": {"Code": "NoSuchBucket"}}
            super().__init__("bucket missing")

    class FakeS3Client:
        def __init__(self):
            self.created = False
            self.last_create_kwargs = None

        def head_bucket(self, Bucket):
            if not self.created:
                raise MissingBucketError()
            return {}

        def create_bucket(self, **kwargs):
            self.created = True
            self.last_create_kwargs = kwargs
            return {}

    adapter = S3CompatibleAdapter({
        "bucket_name": "test-bucket",
        "region": "us-east-1",
        "endpoint_url": "http://127.0.0.1:9000",
        "auto_create_bucket": True,
    })
    adapter._client = FakeS3Client()

    info = adapter.ensure_bucket()

    assert info["available"] is True
    assert info["created"] is True
    assert info["auto_create_bucket"] is True
    assert adapter._client.last_create_kwargs == {"Bucket": "test-bucket"}


def test_memory_analytics_api_routes():
    """测试记忆层 analytics API。"""
    import main as backend_main

    temp_dir = tempfile.mkdtemp()
    original_lakehouse = backend_main.data_lakehouse
    backend_main.data_lakehouse = create_lakehouse({
        "buffer_max_size": 1,
        "store_type": "sqlite",
        "store_config": {
            "db_path": os.path.join(temp_dir, "events.db")
        },
        "analytics_cache_dir": os.path.join(temp_dir, "analytics_cache"),
    })

    try:
        backend_main.data_lakehouse.save_batch([
            {
                "id": "evt-api-1",
                "timestamp": "2026-03-18T10:00:00",
                "event_type": "decision_event",
                "source": "decision_orchestrator",
                "payload": {"severity": "medium"},
            },
            {
                "id": "evt-api-2",
                "timestamp": "2026-03-18T10:01:00",
                "event_type": "decision_event",
                "source": "decision_orchestrator",
                "payload": {"severity": "high"},
            },
        ])
        backend_main.data_lakehouse._flush_buffer_to_local()

        status_json = asyncio.run(backend_main.get_ai_native_memory_analytics_status())
        assert status_json["status"] == "ready"
        assert status_json["storage_profile"]["analytics_engine"] == "duckdb"

        archive_json = asyncio.run(
            backend_main.archive_ai_native_memory(
                backend_main.MemoryArchiveRequest(event_type="decision_event", limit=20)
            )
        )
        assert archive_json["status"] == "archived"
        assert archive_json["parquet_path"].endswith("decision_event.parquet")

        query_json = asyncio.run(
            backend_main.query_ai_native_memory_analytics(
                backend_main.MemoryAnalyticsQueryRequest(
                    sql="SELECT event_type, COUNT(*) AS total FROM lakehouse_events GROUP BY event_type",
                    event_type="decision_event",
                    limit=20,
                )
            )
        )
        assert query_json["count"] == 1
        assert query_json["rows"] == [{"event_type": "decision_event", "total": 2}]
    finally:
        backend_main.data_lakehouse = original_lakehouse
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_lakehouse_status_exposes_cloud_sync_health():
    """测试湖仓状态包含云同步健康信息。"""

    class FakeCloudAdapter:
        def get_bucket_info(self):
            return {
                "bucket": "poseidon-test",
                "endpoint_url": "http://127.0.0.1:9000",
                "available": True,
            }

    temp_dir = tempfile.mkdtemp()
    try:
        lakehouse = create_lakehouse({
            "store_type": "sqlite",
            "store_config": {
                "db_path": os.path.join(temp_dir, "events.db")
            },
        })
        lakehouse.cloud_adapter = FakeCloudAdapter()

        status = lakehouse.get_status()

        assert status["cloud_adapter"]["info"]["bucket"] == "poseidon-test"
        assert status["health"]["local_store_ready"] is True
        assert status["health"]["cloud_sync_configured"] is True
        assert status["health"]["cloud_sync_available"] is True
        assert status["health"]["analytics_ready"] is True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
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
