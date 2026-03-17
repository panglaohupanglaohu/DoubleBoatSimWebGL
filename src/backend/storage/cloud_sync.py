# -*- coding: utf-8 -*-
"""
Cloud Sync Adapter - 云存储同步接口占位

为分布式感知网络提供云存储同步能力。
当前实现为接口级占位，预留挂接点。

目标云存储类型:
- S3 兼容对象存储 (AWS S3, MinIO, Alibaba OSS, etc.)
- Azure Blob Storage
- Google Cloud Storage
- Feishu/飞书云文档 (作为轻量级替代)

设计原则:
1. 支持异步批量上传
2. 支持事件流增量同步
3. 支持事件回放与持久化
4. 支持本地缓存 + 远端同步双模式
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
import os


logger = logging.getLogger(__name__)


class CloudStorageAdapter(ABC):
    """云存储适配器基类"""
    
    @abstractmethod
    def upload_event(self, event_data: Dict[str, Any], event_type: str) -> bool:
        """上传单个事件"""
        ...
    
    @abstractmethod
    def upload_batch(self, events: List[Dict[str, Any]], event_type: str) -> bool:
        """批量上传事件"""
        ...
    
    @abstractmethod
    def download_events(self, event_type: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """下载指定时间范围的事件"""
        ...
    
    @abstractmethod
    def list_events(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """列出最近事件"""
        ...
    
    @abstractmethod
    def get_bucket_info(self) -> Dict[str, Any]:
        """获取存储桶信息"""
        ...


class S3CompatibleAdapter(CloudStorageAdapter):
    """S3 兼容存储适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bucket_name = config.get("bucket_name", "doubleboat-events")
        self.region = config.get("region", "us-east-1")
        self.prefix = config.get("prefix", "events/")
        self._client = None
        
        # Check for AWS credentials
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID", config.get("access_key"))
        self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", config.get("secret_key"))
        
        logger.info(f"S3 Adapter initialized: bucket={self.bucket_name}, region={self.region}")
    
    def _get_client(self):
        """获取 S3 客户端"""
        if self._client is not None:
            return self._client
        
        try:
            import boto3
            self._client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
            return self._client
        except ImportError:
            logger.warning("boto3 not installed, using mock mode")
            return None
        except Exception as e:
            logger.error(f"S3 client initialization failed: {e}")
            return None
    
    def upload_event(self, event_data: Dict[str, Any], event_type: str) -> bool:
        """上传单个事件"""
        client = self._get_client()
        if client is None:
            logger.debug(f"[MOCK] Would upload {event_type} event")
            return True
        
        try:
            key = f"{self.prefix}{event_type}/{datetime.now().isoformat()}.json"
            client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=event_data
            )
            logger.debug(f"Uploaded {event_type} event to {key}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def upload_batch(self, events: List[Dict[str, Any]], event_type: str) -> bool:
        """批量上传事件"""
        success = True
        for event in events:
            if not self.upload_event(event, event_type):
                success = False
        return success
    
    def download_events(self, event_type: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """下载指定时间范围的事件"""
        client = self._get_client()
        if client is None:
            logger.warning("S3 client not available")
            return []
        
        # TODO: Implement pagination and time-based filtering
        logger.warning("Download not yet implemented")
        return []
    
    def list_events(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """列出最近事件"""
        client = self._get_client()
        if client is None:
            logger.warning("S3 client not available")
            return []
        
        # TODO: Implement listing with pagination
        logger.warning("List not yet implemented")
        return []
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """获取存储桶信息"""
        client = self._get_client()
        if client is None:
            return {
                "bucket": self.bucket_name,
                "region": self.region,
                "available": False
            }
        
        try:
            info = client.head_bucket(Bucket=self.bucket_name)
            return {
                "bucket": self.bucket_name,
                "region": self.region,
                "available": True,
                "created": info.get('ContentLanguage', 'unknown'),
                "owner": info.get('Owner', {}).get('DisplayName', 'unknown')
            }
        except Exception as e:
            return {
                "bucket": self.bucket_name,
                "region": self.region,
                "available": False,
                "error": str(e)
            }


class FeishuAdapter(CloudStorageAdapter):
    """飞书云文档适配器（轻量级替代）"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.folder_token = config.get("folder_token", "")
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.info("Feishu Adapter initialized")
    
    def upload_event(self, event_data: Dict[str, Any], event_type: str) -> bool:
        """上传单个事件到飞书文档"""
        # TODO: Implement using feishu_doc API
        self.logger.debug(f"[FEISHU MOCK] Would upload {event_type} event")
        return True
    
    def upload_batch(self, events: List[Dict[str, Any]], event_type: str) -> bool:
        """批量上传事件"""
        for event in events:
            if not self.upload_event(event, event_type):
                return False
        return True
    
    def download_events(self, event_type: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """下载事件"""
        self.logger.warning("Download not yet implemented for Feishu")
        return []
    
    def list_events(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """列出事件"""
        self.logger.warning("List not yet implemented for Feishu")
        return []
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """获取信息"""
        return {
            "type": "feishu",
            "folder_token": self.folder_token,
            "available": bool(self.folder_token)
        }


class LocalFileAdapter(CloudStorageAdapter):
    """本地文件适配器（用于测试/开发）"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = config.get("storage_path", "./storage/events")
        os.makedirs(self.storage_path, exist_ok=True)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.info(f"LocalFile Adapter initialized: {self.storage_path}")
    
    def _get_path(self, event_type: str) -> str:
        """获取事件存储路径"""
        return os.path.join(self.storage_path, event_type)
    
    def upload_event(self, event_data: Dict[str, Any], event_type: str) -> bool:
        """上传单个事件到本地文件"""
        try:
            os.makedirs(self._get_path(event_type), exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{timestamp}.json"
            filepath = os.path.join(self._get_path(event_type), filename)
            
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(event_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved {event_type} event to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Save failed: {e}")
            return False
    
    def upload_batch(self, events: List[Dict[str, Any]], event_type: str) -> bool:
        """批量上传事件"""
        success = True
        for event in events:
            if not self.upload_event(event, event_type):
                success = False
        return success
    
    def download_events(self, event_type: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """下载指定时间范围的事件"""
        try:
            path = self._get_path(event_type)
            import json
            
            events = []
            if os.path.exists(path):
                for filename in os.listdir(path):
                    if filename.endswith('.json'):
                        filepath = os.path.join(path, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            events.append(json.load(f))
            
            return events
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return []
    
    def list_events(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """列出最近事件"""
        events = self.download_events(event_type, datetime(1970, 1, 1), datetime.now())
        return events[-limit:]
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """获取信息"""
        return {
            "type": "local",
            "storage_path": self.storage_path,
            "available": True,
            "disk_usage_bytes": self._get_disk_usage()
        }
    
    def _get_disk_usage(self) -> int:
        """获取磁盘使用量"""
        total = 0
        if os.path.exists(self.storage_path):
            for root, dirs, files in os.walk(self.storage_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    total += os.path.getsize(filepath)
        return total


def get_adapter(adapter_type: str, config: Dict[str, Any]) -> CloudStorageAdapter:
    """获取适配器实例"""
    if adapter_type == "s3":
        return S3CompatibleAdapter(config)
    elif adapter_type == "feishu":
        return FeishuAdapter(config)
    elif adapter_type == "local":
        return LocalFileAdapter(config)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
