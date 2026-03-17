# -*- coding: utf-8 -*-
"""
Event Store - 本地事件持久化存储

支持 JSONL、SQLite 和 Parquet 格式。
用于事件流的本地持久化和回放。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
import json
import os


logger = logging.getLogger(__name__)


class EventStore(ABC):
    """事件存储基类"""
    
    @abstractmethod
    def save_event(self, event: Dict[str, Any]) -> bool:
        """保存单个事件"""
        ...
    
    @abstractmethod
    def save_events(self, events: List[Dict[str, Any]]) -> bool:
        """批量保存事件"""
        ...
    
    @abstractmethod
    def load_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """加载事件"""
        ...
    
    @abstractmethod
    def load_events_by_time(self, start_time: datetime, end_time: datetime, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """按时间范围加载事件"""
        ...
    
    @abstractmethod
    def clear_events(self, event_type: Optional[str] = None) -> bool:
        """清除事件"""
        ...


class JSONLStore(EventStore):
    """JSONL 格式存储（每行一个事件）"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = config.get("storage_path", "./storage/events")
        self.max_events = config.get("max_events", 10000)
        os.makedirs(self.storage_path, exist_ok=True)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.info(f"JSONL Store initialized: {self.storage_path}")
    
    def _get_path(self, event_type: str) -> str:
        """获取事件文件路径"""
        return os.path.join(self.storage_path, f"{event_type}.jsonl")
    
    def save_event(self, event: Dict[str, Any]) -> bool:
        """保存单个事件"""
        try:
            event_type = event.get("event_type", "unknown")
            event["saved_at"] = datetime.now().isoformat()
            
            filepath = self._get_path(event_type)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
            
            # Check if we need to trim
            self._trim_file(filepath)
            return True
        except Exception as e:
            self.logger.error(f"Save failed: {e}")
            return False
    
    def save_events(self, events: List[Dict[str, Any]]) -> bool:
        """批量保存事件"""
        success = True
        for event in events:
            if not self.save_event(event):
                success = False
        return success
    
    def load_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """加载事件"""
        try:
            if event_type:
                filepath = self._get_path(event_type)
                if not os.path.exists(filepath):
                    return []
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                events = []
                for line in lines:
                    try:
                        events.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
                
                return events[-limit:]
            
            # Load all event types
            events = []
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.jsonl'):
                    filepath = os.path.join(self.storage_path, filename)
                    event_type = filename[:-6]  # Remove .jsonl
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                event = json.loads(line.strip())
                                event["source_file"] = event_type
                                events.append(event)
                            except json.JSONDecodeError:
                                continue
            
            # Sort by timestamp and return latest
            events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return events[:limit]
        
        except Exception as e:
            self.logger.error(f"Load failed: {e}")
            return []
    
    def load_events_by_time(self, start_time: datetime, end_time: datetime, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """按时间范围加载事件"""
        events = self.load_events(event_type, limit=10000)
        
        start_ts = start_time.isoformat()
        end_ts = end_time.isoformat()
        
        return [
            e for e in events
            if start_ts <= e.get("timestamp", "") <= end_ts
        ]
    
    def clear_events(self, event_type: Optional[str] = None) -> bool:
        """清除事件"""
        try:
            if event_type:
                filepath = self._get_path(event_type)
                if os.path.exists(filepath):
                    os.remove(filepath)
            else:
                for filename in os.listdir(self.storage_path):
                    if filename.endswith('.jsonl'):
                        os.remove(os.path.join(self.storage_path, filename))
            return True
        except Exception as e:
            self.logger.error(f"Clear failed: {e}")
            return False
    
    def _trim_file(self, filepath: str):
        """ trimming file if too large """
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) > self.max_events:
                lines = lines[-self.max_events:]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
        except Exception as e:
            self.logger.warning(f"Trim failed: {e}")


class SQLiteStore(EventStore):
    """SQLite 数据库存储"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config.get("db_path", "./storage/events.db")
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.info(f"SQLite Store initialized: {self.db_path}")
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT,
                    payload TEXT NOT NULL,
                    confidence REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Init DB failed: {e}")
            raise
    
    def save_event(self, event: Dict[str, Any]) -> bool:
        """保存单个事件"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            event_type = event.get("event_type", "unknown")
            source = event.get("source", "")
            payload = json.dumps(event.get("payload", event), ensure_ascii=False)
            confidence = event.get("confidence", 1.0)
            timestamp = event.get("timestamp", datetime.now().isoformat())
            
            cursor.execute("""
                INSERT INTO events (timestamp, event_type, source, payload, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, event_type, source, payload, confidence))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Save failed: {e}")
            return False
    
    def save_events(self, events: List[Dict[str, Any]]) -> bool:
        """批量保存事件"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for event in events:
                event_type = event.get("event_type", "unknown")
                source = event.get("source", "")
                payload = json.dumps(event.get("payload", event), ensure_ascii=False)
                confidence = event.get("confidence", 1.0)
                timestamp = event.get("timestamp", datetime.now().isoformat())
                
                cursor.execute("""
                    INSERT INTO events (timestamp, event_type, source, payload, confidence)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, event_type, source, payload, confidence))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Save failed: {e}")
            return False
    
    def load_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """加载事件"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if event_type:
                cursor.execute("""
                    SELECT timestamp, event_type, source, payload, confidence
                    FROM events
                    WHERE event_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (event_type, limit))
            else:
                cursor.execute("""
                    SELECT timestamp, event_type, source, payload, confidence
                    FROM events
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                events.append({
                    "timestamp": row[0],
                    "event_type": row[1],
                    "source": row[2],
                    "payload": json.loads(row[3]),
                    "confidence": row[4]
                })
            
            return events
        except Exception as e:
            self.logger.error(f"Load failed: {e}")
            return []
    
    def load_events_by_time(self, start_time: datetime, end_time: datetime, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """按时间范围加载事件"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_ts = start_time.isoformat()
            end_ts = end_time.isoformat()
            
            if event_type:
                cursor.execute("""
                    SELECT timestamp, event_type, source, payload, confidence
                    FROM events
                    WHERE event_type = ? AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp DESC
                """, (event_type, start_ts, end_ts))
            else:
                cursor.execute("""
                    SELECT timestamp, event_type, source, payload, confidence
                    FROM events
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp DESC
                """, (start_ts, end_ts))
            
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                events.append({
                    "timestamp": row[0],
                    "event_type": row[1],
                    "source": row[2],
                    "payload": json.loads(row[3]),
                    "confidence": row[4]
                })
            
            return events
        except Exception as e:
            self.logger.error(f"Load failed: {e}")
            return []
    
    def clear_events(self, event_type: Optional[str] = None) -> bool:
        """清除事件"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if event_type:
                cursor.execute("DELETE FROM events WHERE event_type = ?", (event_type,))
            else:
                cursor.execute("DELETE FROM events")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Clear failed: {e}")
            return False


def get_store(store_type: str, config: Dict[str, Any]) -> EventStore:
    """获取存储实例"""
    if store_type == "jsonl":
        return JSONLStore(config)
    elif store_type == "sqlite":
        return SQLiteStore(config)
    else:
        raise ValueError(f"Unknown store type: {store_type}")
