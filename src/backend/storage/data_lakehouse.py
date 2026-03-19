# -*- coding: utf-8 -*-
"""
Data Lakehouse - 船舶大数据湖仓层

实现基于 Parquet + SQLite 的轻量级湖仓架构，支持：
- 本地事件持久化 (JSONL/SQLite/Parquet)
- 云存储同步 (S3/Feishu)
- 事件回放与回溯
- 数据质量校验

设计原则:
1. 轻量优先：先用 SQLite/Parquet，避免 Hadoop 部署复杂度
2. 插件化架构：支持多种后端存储
3. 边缘优先：船端本地缓存 + 云同步
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
import os
from pathlib import Path

from .event_store import EventStore, get_store
from .cloud_sync import CloudStorageAdapter, get_adapter


logger = logging.getLogger(__name__)


class DataLakehouse:
    """船舶大数据湖仓 - 轻量级实现
    
    采用本地+云双层架构：
    - 边缘层：SQLite / JSONL / Parquet (本地事件存储)
    - 云层：S3 / Feishu / 飞书云文档 (远端持久化)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.local_store: Optional[EventStore] = None
        self.cloud_adapter: Optional[CloudStorageAdapter] = None
        self.event_buffer: List[Dict[str, Any]] = []
        self.buffer_max_size = self.config.get("buffer_max_size", 100)
        self.analytics_cache_dir = Path(self.config.get("analytics_cache_dir", "./storage/analytics_cache"))
        self.analytics_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize local store
        store_type = self.config.get("store_type", "sqlite")
        store_config = self.config.get("store_config", {
            "db_path": "./storage/events.db",
            "storage_path": "./storage/events"
        })
        
        try:
            self.local_store = get_store(store_type, store_config)
            logger.info(f"DataLakehouse initialized with {store_type} store")
        except Exception as e:
            logger.error(f"Failed to initialize local store: {e}")
            self.local_store = None
        
        # Initialize cloud adapter (optional)
        cloud_type = self.config.get("cloud_type")
        if cloud_type:
            cloud_config = self.config.get("cloud_config", {})
            try:
                self.cloud_adapter = get_adapter(cloud_type, cloud_config)
                logger.info(f"DataLakehouse initialized with {cloud_type} cloud adapter")
            except Exception as e:
                logger.error(f"Failed to initialize cloud adapter: {e}")
                self.cloud_adapter = None
    
    def save_event(self, event: Dict[str, Any]) -> bool:
        """保存单个事件到湖仓"""
        try:
            # Buffer the event first
            self.event_buffer.append(event)
            
            # If buffer is full, flush to local store
            if len(self.event_buffer) >= self.buffer_max_size:
                self._flush_buffer_to_local()
            
            return True
        except Exception as e:
            logger.error(f"Failed to save event: {e}")
            return False
    
    def save_batch(self, events: List[Dict[str, Any]]) -> bool:
        """批量保存事件到湖仓"""
        try:
            for event in events:
                self.event_buffer.append(event)
            
            if len(self.event_buffer) >= self.buffer_max_size:
                self._flush_buffer_to_local()
            
            return True
        except Exception as e:
            logger.error(f"Failed to save batch: {e}")
            return False
    
    def query_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """查询事件"""
        if self.event_buffer:
            self._flush_buffer_to_local()
        if not self.local_store:
            logger.warning("Local store not initialized")
            return []
        
        return self.local_store.load_events(event_type, limit)
    
    def query_events_by_time(self, start_time: datetime, end_time: datetime, 
                            event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """按时间范围查询事件"""
        if self.event_buffer:
            self._flush_buffer_to_local()
        if not self.local_store:
            logger.warning("Local store not initialized")
            return []
        
        return self.local_store.load_events_by_time(start_time, end_time, event_type)

    def get_storage_profile(self) -> Dict[str, Any]:
        """返回轻量 Lakehouse 架构配置，明确当前不依赖 Hadoop。"""
        store_type = self.config.get("store_type", "sqlite")
        cloud_type = self.config.get("cloud_type", "none")
        archive_format = self.config.get("archive_format", "parquet")
        analytics_engine = self.config.get("analytics_engine", "duckdb")
        return {
            "architecture_mode": "lightweight_edge_lakehouse",
            "hadoop_required": False,
            "hot_store": store_type,
            "hot_store_mode": "wal" if store_type == "sqlite" else "standard",
            "archive_format": archive_format,
            "analytics_engine": analytics_engine,
            "cloud_sync": cloud_type,
            "duckdb_available": analytics_engine == "duckdb",
            "recommended_stack": ["sqlite", archive_format, analytics_engine, "s3-compatible-sync"],
        }

    def archive_events_to_parquet(
        self,
        output_path: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100000,
    ) -> str:
        """将当前事件归档到 Parquet，供 DuckDB 即席分析使用。"""
        if self.event_buffer:
            self._flush_buffer_to_local()

        events = self.query_events(event_type=event_type, limit=limit)
        target_path = output_path or str(
            self.analytics_cache_dir / f"{event_type or 'all_events'}.parquet"
        )

        import pyarrow as pa
        import pyarrow.parquet as pq

        rows = [
            {
                "timestamp": event.get("timestamp"),
                "event_type": event.get("event_type"),
                "source": event.get("source"),
                "payload": event.get("payload", {}),
                "confidence": event.get("confidence", 1.0),
            }
            for event in events
        ]
        table = pa.Table.from_pylist(rows or [{
            "timestamp": None,
            "event_type": None,
            "source": None,
            "payload": {},
            "confidence": None,
        }])
        pq.write_table(table, target_path)
        return target_path

    def run_duckdb_query(
        self,
        sql: str,
        parquet_path: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100000,
    ) -> List[Dict[str, Any]]:
        """使用 DuckDB 对 Parquet 归档执行即席分析。"""
        archive_path = parquet_path or self.archive_events_to_parquet(event_type=event_type, limit=limit)

        import duckdb

        conn = duckdb.connect(database=':memory:')
        escaped_path = archive_path.replace("'", "''")
        conn.execute(f"CREATE VIEW lakehouse_events AS SELECT * FROM read_parquet('{escaped_path}')")
        result = conn.execute(sql)
        columns = [item[0] for item in result.description]
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        conn.close()
        return rows

    def get_memory_profile(self, limit: int = 50) -> Dict[str, Any]:
        """生成近期记忆概况，供协调层和驾驶台消费。"""
        recent_events = self.query_events(limit=limit)
        by_type: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            source = event.get("source", "unknown")
            by_type[event_type] = by_type.get(event_type, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1

        return {
            "recent_events_count": len(recent_events),
            "latest_event_time": recent_events[0].get("timestamp") if recent_events else None,
            "event_type_breakdown": by_type,
            "source_breakdown": by_source,
        }
    
    def _flush_buffer_to_local(self):
        """将缓冲区事件刷入本地存储"""
        if not self.local_store or not self.event_buffer:
            return
        
        try:
            self.local_store.save_events(self.event_buffer)
            logger.debug(f"Flushed {len(self.event_buffer)} events to local store")
            
            # Also sync to cloud if available
            if self.cloud_adapter:
                self.cloud_adapter.upload_batch(self.event_buffer, "batch")
                logger.debug(f"Synced {len(self.event_buffer)} events to cloud")
            
            # Clear buffer
            self.event_buffer = []
        except Exception as e:
            logger.error(f"Failed to flush buffer: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取湖仓状态"""
        status = {
            "local_store": {
                "type": type(self.local_store).__name__ if self.local_store else "none",
                "available": self.local_store is not None
            },
            "cloud_adapter": {
                "type": type(self.cloud_adapter).__name__ if self.cloud_adapter else "none",
                "available": self.cloud_adapter is not None
            },
            "storage_profile": self.get_storage_profile(),
            "buffer_size": len(self.event_buffer),
            "buffer_max_size": self.buffer_max_size,
            "analytics_cache_dir": str(self.analytics_cache_dir),
            "memory_profile": self.get_memory_profile(limit=20) if self.local_store is not None else {},
        }
        
        if self.local_store:
            try:
                # Try to get disk usage or similar info
                info = getattr(self.local_store, "get_info", None)
                if info:
                    status["local_store"]["info"] = info()
            except Exception:
                pass

        if self.cloud_adapter:
            try:
                status["cloud_adapter"]["info"] = self.cloud_adapter.get_bucket_info()
            except Exception as exc:
                status["cloud_adapter"]["info"] = {
                    "available": False,
                    "error": str(exc),
                }

        cloud_info = status["cloud_adapter"].get("info", {})
        status["health"] = {
            "local_store_ready": status["local_store"]["available"],
            "cloud_sync_configured": self.cloud_adapter is not None,
            "cloud_sync_available": bool(cloud_info.get("available", False)),
            "analytics_ready": bool(status["storage_profile"].get("duckdb_available", False)),
        }
        
        return status
    
    def shutdown(self):
        """关闭湖仓，刷出缓冲区"""
        self._flush_buffer_to_local()
        logger.info("DataLakehouse shutdown complete")


# Convenience function
def create_lakehouse(config: Dict[str, Any] = None) -> DataLakehouse:
    """创建 DataLakehouse 实例"""
    return DataLakehouse(config)
