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
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging
import os
import json


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
        self.endpoint_url = config.get("endpoint_url") or os.environ.get("AWS_ENDPOINT_URL")
        self.verify_ssl = config.get("verify_ssl", True)
        self.addressing_style = config.get("addressing_style", "path")
        self.max_list_scan = int(config.get("max_list_scan", 1000))
        self.auto_create_bucket = bool(config.get("auto_create_bucket", False))
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
            from botocore.config import Config

            client_kwargs = {
                "service_name": "s3",
                "region_name": self.region,
                "aws_access_key_id": self.access_key,
                "aws_secret_access_key": self.secret_key,
                "verify": self.verify_ssl,
                "config": Config(s3={"addressing_style": self.addressing_style}),
            }
            if self.endpoint_url:
                client_kwargs["endpoint_url"] = self.endpoint_url
            self._client = boto3.client(
                **client_kwargs
            )
            return self._client
        except ImportError:
            logger.warning("boto3 not installed, using mock mode")
            return None
        except Exception as e:
            logger.error(f"S3 client initialization failed: {e}")
            return None

    def _normalize_prefix(self, prefix: str) -> str:
        if not prefix:
            return ""
        return prefix if prefix.endswith("/") else f"{prefix}/"

    def _extract_error_code(self, exc: Exception) -> Optional[str]:
        response = getattr(exc, "response", None)
        if isinstance(response, dict):
            error = response.get("Error", {})
            code = error.get("Code")
            if code is not None:
                return str(code)
        return None

    def _bucket_exists(self) -> bool:
        client = self._get_client()
        if client is None:
            return False
        client.head_bucket(Bucket=self.bucket_name)
        return True

    def ensure_bucket(self) -> Dict[str, Any]:
        """探测并按需创建 bucket。"""
        client = self._get_client()
        checked_at = datetime.now(timezone.utc).isoformat()
        if client is None:
            return {
                "bucket": self.bucket_name,
                "region": self.region,
                "endpoint_url": self.endpoint_url,
                "available": False,
                "auto_create_bucket": self.auto_create_bucket,
                "checked_at": checked_at,
                "error": "S3 client not available",
            }

        try:
            self._bucket_exists()
            return {
                "bucket": self.bucket_name,
                "region": self.region,
                "endpoint_url": self.endpoint_url,
                "prefix": self.prefix,
                "addressing_style": self.addressing_style,
                "available": True,
                "auto_create_bucket": self.auto_create_bucket,
                "checked_at": checked_at,
                "created": False,
            }
        except Exception as exc:
            error_code = (self._extract_error_code(exc) or "").lower()
            missing_bucket = error_code in {"404", "no such bucket", "nosuchbucket", "notfound"}
            if not (missing_bucket and self.auto_create_bucket):
                return {
                    "bucket": self.bucket_name,
                    "region": self.region,
                    "endpoint_url": self.endpoint_url,
                    "available": False,
                    "auto_create_bucket": self.auto_create_bucket,
                    "checked_at": checked_at,
                    "error": str(exc),
                }

        try:
            create_kwargs: Dict[str, Any] = {"Bucket": self.bucket_name}
            if not self.endpoint_url and self.region and self.region != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": self.region}
            client.create_bucket(**create_kwargs)
            return {
                "bucket": self.bucket_name,
                "region": self.region,
                "endpoint_url": self.endpoint_url,
                "prefix": self.prefix,
                "addressing_style": self.addressing_style,
                "available": True,
                "auto_create_bucket": self.auto_create_bucket,
                "checked_at": checked_at,
                "created": True,
            }
        except Exception as exc:
            return {
                "bucket": self.bucket_name,
                "region": self.region,
                "endpoint_url": self.endpoint_url,
                "available": False,
                "auto_create_bucket": self.auto_create_bucket,
                "checked_at": checked_at,
                "error": str(exc),
            }

    def _build_key(self, event_type: str, timestamp: datetime) -> str:
        safe_type = (event_type or "unknown").strip("/") or "unknown"
        safe_prefix = self._normalize_prefix(self.prefix)
        return (
            f"{safe_prefix}{safe_type}/"
            f"{timestamp.strftime('%Y/%m/%d/%H%M%S_%f')}.json"
        )

    def _build_event_prefix(self, event_type: str) -> str:
        """构建事件类型级别的 S3 前缀，用于跨日期分区列举。"""
        safe_type = (event_type or "unknown").strip("/") or "unknown"
        safe_prefix = self._normalize_prefix(self.prefix)
        return f"{safe_prefix}{safe_type}/"

    def _serialize_event(self, event_data: Dict[str, Any], event_type: str) -> bytes:
        event_copy = dict(event_data)
        event_copy.setdefault("event_type", event_type)
        event_copy.setdefault("uploaded_at", datetime.now(timezone.utc).isoformat())
        return json.dumps(event_copy, ensure_ascii=False).encode("utf-8")

    def _parse_event_bytes(self, payload: bytes) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception as exc:
            logger.warning(f"Failed to decode S3 event payload: {exc}")
            return None

    def _event_with_metadata(self, event: Optional[Dict[str, Any]], key: str, last_modified: Any) -> Optional[Dict[str, Any]]:
        if not event:
            return None

        enriched = dict(event)
        enriched.setdefault("cloud_key", key)
        if last_modified is not None:
            if hasattr(last_modified, "isoformat"):
                enriched.setdefault("cloud_last_modified", last_modified.isoformat())
            else:
                enriched.setdefault("cloud_last_modified", str(last_modified))
        return enriched

    def _extract_event_timestamp(self, event: Dict[str, Any], fallback: Optional[Any] = None) -> Optional[datetime]:
        timestamp = event.get("timestamp") or event.get("uploaded_at")
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                pass
        if fallback is not None:
            if isinstance(fallback, datetime):
                return fallback
            if hasattr(fallback, "isoformat"):
                try:
                    return datetime.fromisoformat(fallback.isoformat())
                except ValueError:
                    return None
        return None

    def _iter_objects(self, event_type: str, limit: int) -> List[Dict[str, Any]]:
        client = self._get_client()
        if client is None:
            logger.warning("S3 client not available")
            return []

        prefix = self._build_event_prefix(event_type)
        continuation_token = None
        contents: List[Dict[str, Any]] = []

        while len(contents) < limit:
            request: Dict[str, Any] = {
                "Bucket": self.bucket_name,
                "Prefix": prefix,
                "MaxKeys": min(limit - len(contents), 1000),
            }
            if continuation_token:
                request["ContinuationToken"] = continuation_token

            response = client.list_objects_v2(**request)
            contents.extend(response.get("Contents", []))
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")
            if len(contents) >= self.max_list_scan:
                break

        return contents[:limit]
    
    def upload_event(self, event_data: Dict[str, Any], event_type: str) -> bool:
        """上传单个事件"""
        client = self._get_client()
        if client is None:
            logger.debug(f"[MOCK] Would upload {event_type} event")
            return True
        
        try:
            event_timestamp = self._extract_event_timestamp(event_data, datetime.now(timezone.utc)) or datetime.now(timezone.utc)
            key = self._build_key(event_type, event_timestamp)
            client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=self._serialize_event(event_data, event_type),
                ContentType="application/json; charset=utf-8",
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

        items = self._iter_objects(event_type, self.max_list_scan)
        matched: List[Dict[str, Any]] = []
        for item in items:
            key = item.get("Key")
            if not key:
                continue
            try:
                response = client.get_object(Bucket=self.bucket_name, Key=key)
                payload = response["Body"].read()
                event = self._parse_event_bytes(payload)
                event_timestamp = self._extract_event_timestamp(event or {}, item.get("LastModified"))
                if event_timestamp is None:
                    continue
                if start_time <= event_timestamp <= end_time:
                    enriched = self._event_with_metadata(event, key, item.get("LastModified"))
                    if enriched is not None:
                        matched.append(enriched)
            except Exception as exc:
                logger.warning(f"Failed to download S3 object {key}: {exc}")

        matched.sort(key=lambda event: event.get("timestamp") or event.get("uploaded_at") or "")
        return matched
    
    def list_events(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """列出最近事件"""
        client = self._get_client()
        if client is None:
            logger.warning("S3 client not available")
            return []

        items = self._iter_objects(event_type, limit)
        items.sort(key=lambda item: item.get("LastModified") or datetime.min, reverse=True)

        events: List[Dict[str, Any]] = []
        for item in items:
            key = item.get("Key")
            if not key:
                continue
            try:
                response = client.get_object(Bucket=self.bucket_name, Key=key)
                payload = response["Body"].read()
                event = self._parse_event_bytes(payload)
                enriched = self._event_with_metadata(event, key, item.get("LastModified"))
                if enriched is not None:
                    events.append(enriched)
            except Exception as exc:
                logger.warning(f"Failed to list S3 object {key}: {exc}")
        return events[:limit]
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """获取存储桶信息"""
        return self.ensure_bucket()


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
