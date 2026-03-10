"""
船舶工程智能体配置模块

提供配置类封装、验证逻辑和默认值管理。
支持安全配置、运行时配置和功能配置的分层设计。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SafetyConfig:
    """安全配置数据类"""
    require_warning: bool = True
    require_ppe: bool = True
    require_loto: bool = True
    
    def validate(self) -> None:
        """验证安全配置有效性"""
        if not isinstance(self.require_warning, bool):
            raise ValueError("require_warning 必须是布尔值")
        if not isinstance(self.require_ppe, bool):
            raise ValueError("require_ppe 必须是布尔值")
        if not isinstance(self.require_loto, bool):
            raise ValueError("require_loto 必须是布尔值")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SafetyConfig':
        """从字典创建安全配置"""
        return cls(
            require_warning=config_dict.get("require_warning", True),
            require_ppe=config_dict.get("require_ppe", True),
            require_loto=config_dict.get("require_loto", True)
        )


@dataclass
class RuntimeConfig:
    """运行时配置数据类"""
    max_context_length: int = 4096
    include_sources: bool = True
    log_level: str = "INFO"
    
    def validate(self) -> None:
        """验证运行时配置有效性"""
        if not isinstance(self.max_context_length, int):
            raise ValueError("max_context_length 必须是整数")
        if self.max_context_length < 100:
            raise ValueError("max_context_length 必须 >= 100")
        if self.max_context_length > 100000:
            raise ValueError("max_context_length 必须 <= 100000")
        if not isinstance(self.include_sources, bool):
            raise ValueError("include_sources 必须是布尔值")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"log_level 必须是有效的日志级别：{self.log_level}")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RuntimeConfig':
        """从字典创建运行时配置"""
        return cls(
            max_context_length=config_dict.get("max_context_length", 4096),
            include_sources=config_dict.get("include_sources", True),
            log_level=config_dict.get("log_level", "INFO")
        )


@dataclass
class MarineEngineerConfig:
    """
    船舶工程智能体主配置类
    
    整合安全配置和运行时配置，提供统一的配置管理接口。
    支持从字典加载、验证和导出配置。
    
    :ivar safety: 安全配置对象
    :ivar runtime: 运行时配置对象
    :ivar features: 功能开关配置
    """
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    features: Dict[str, bool] = field(default_factory=dict)
    
    def validate(self) -> None:
        """验证所有配置有效性"""
        self.safety.validate()
        self.runtime.validate()
        
        # 验证功能开关
        for key, value in self.features.items():
            if not isinstance(value, bool):
                raise ValueError(f"功能开关 {key} 必须是布尔值")
        
        logger.info("配置验证通过")
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置导出为字典"""
        return {
            "safety": {
                "require_warning": self.safety.require_warning,
                "require_ppe": self.safety.require_ppe,
                "require_loto": self.safety.require_loto
            },
            "runtime": {
                "max_context_length": self.runtime.max_context_length,
                "include_sources": self.runtime.include_sources,
                "log_level": self.runtime.log_level
            },
            "features": self.features.copy()
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MarineEngineerConfig':
        """
        从字典创建配置对象
        
        :param config_dict: 配置字典，包含 safety/runtime/features 键
        :return: MarineEngineerConfig 实例
        """
        safety_dict: Dict[str, Any] = config_dict.get("safety", {})
        runtime_dict: Dict[str, Any] = config_dict.get("runtime", {})
        features_dict: Dict[str, bool] = config_dict.get("features", {})
        
        config = cls(
            safety=SafetyConfig.from_dict(safety_dict),
            runtime=RuntimeConfig.from_dict(runtime_dict),
            features=features_dict
        )
        
        # 自动验证配置
        config.validate()
        
        return config
    
    @classmethod
    def default(cls) -> 'MarineEngineerConfig':
        """创建默认配置"""
        return cls()


def get_config(config_dict: Optional[Dict[str, Any]] = None) -> MarineEngineerConfig:
    """
    获取配置对象的便捷函数
    
    :param config_dict: 配置字典，None 则使用默认配置
    :return: 验证后的 MarineEngineerConfig 实例
    """
    if config_dict is None:
        return MarineEngineerConfig.default()
    
    return MarineEngineerConfig.from_dict(config_dict)
