# -*- coding: utf-8 -*-
"""
Configuration Loader - 配置加载器

从 config/settings.json 加载系统配置。
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """配置加载器."""
    
    _instance: Optional['ConfigLoader'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls) -> 'ConfigLoader':
        """单例模式."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置加载器."""
        if not self._config:
            self.load()
    
    def load(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件."""
        if config_path is None:
            # 默认路径：项目根目录/config/settings.json
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / 'config' / 'settings.json'
        else:
            config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def backend_url(self) -> str:
        """获取后端 API 地址."""
        return self.get('api.backend.base_url', 'http://127.0.0.1:8000')
    
    @property
    def frontend_url(self) -> str:
        """获取前端地址."""
        return self.get('api.frontend.base_url', 'http://127.0.0.1:5173')
    
    @property
    def llm_url(self) -> str:
        """获取 LLM API 地址."""
        return self.get('llm.local', 'http://127.0.0.1:11434/v1')
    
    @property
    def websocket_url(self) -> str:
        """获取 WebSocket 地址."""
        return self.get('websocket.url', 'ws://127.0.0.1:8765')
    
    @property
    def debug(self) -> bool:
        """获取调试模式状态."""
        return self.get('debug', False)
    
    @property
    def environment(self) -> str:
        """获取环境配置."""
        return self.get('environment', 'development')


# 全局配置实例
config = ConfigLoader()


def get_config() -> ConfigLoader:
    """获取全局配置实例."""
    return config


def get_backend_url() -> str:
    """获取后端 API 地址."""
    return config.backend_url


def get_frontend_url() -> str:
    """获取前端地址."""
    return config.frontend_url


def get_llm_url() -> str:
    """获取 LLM API 地址."""
    return config.llm_url


def get_websocket_url() -> str:
    """获取 WebSocket 地址."""
    return config.websocket_url
