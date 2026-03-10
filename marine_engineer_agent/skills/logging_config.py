"""
日志配置模块

提供 JSON 结构化日志格式、日志轮转配置和日志级别管理。
支持按大小和时间轮转，可配置日志输出目标。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

import logging
import json
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from dataclasses import dataclass, field


@dataclass
class LoggingConfig:
    """日志配置数据类"""
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    log_dir: str = "logs"
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    rotation_type: str = "size"  # "size" or "time"
    time_interval: str = "midnight"  # for time-based rotation
    include_timestamp: bool = True
    include_source: bool = True
    include_extra_fields: bool = True


class JSONFormatter(logging.Formatter):
    """
    JSON 格式日志格式化器
    
    将日志记录格式化为 JSON 对象，便于日志分析和聚合。
    """
    
    def __init__(self, include_extra: bool = True):
        """
        初始化 JSON 格式化器
        
        :param include_extra: 是否包含额外字段
        """
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON
        
        :param record: 日志记录对象
        :return: JSON 格式的日志字符串
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
            "process_name": record.processName,
        }
        
        # 添加异常信息（如果有）
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if self.include_extra:
            # 排除标准字段
            standard_fields = {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                'message', 'asctime'
            }
            
            for key, value in record.__dict__.items():
                if key not in standard_fields:
                    log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class TextFormatter(logging.Formatter):
    """
    文本格式日志格式化器
    
    提供人类可读的日志格式，适合开发调试。
    """
    
    def __init__(self, include_source: bool = True):
        """
        初始化文本格式化器
        
        :param include_source: 是否包含源文件信息
        """
        if include_source:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
            )
        else:
            format_string = "%(asctime)s - %(levelname)s - %(message)s"
        
        super().__init__(format_string)


def get_log_level(level_name: str) -> int:
    """
    获取日志级别对应的整数值
    
    :param level_name: 日志级别名称 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    :return: 日志级别整数值
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(level_name.upper(), logging.INFO)


def setup_logging(
    logger_name: str = "marine_engineer",
    config: Optional[LoggingConfig] = None,
    console_output: bool = True,
    file_output: bool = True
) -> logging.Logger:
    """
    配置日志系统
    
    :param logger_name: 日志记录器名称
    :param config: 日志配置，None 则使用默认配置
    :param console_output: 是否输出到控制台
    :param file_output: 是否输出到文件
    :return: 配置好的日志记录器
    """
    if config is None:
        config = LoggingConfig()
    
    # 获取或创建日志记录器
    logger = logging.getLogger(logger_name)
    logger.setLevel(get_log_level(config.log_level))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 创建格式化器
    if config.log_format == "json":
        formatter = JSONFormatter(include_extra=config.include_extra_fields)
    else:
        formatter = TextFormatter(include_source=config.include_source)
    
    # 添加控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(get_log_level(config.log_level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件处理器
    if file_output:
        # 确保日志目录存在
        log_dir = config.log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建轮转处理器
        if config.rotation_type == "size":
            file_handler = RotatingFileHandler(
                filename=os.path.join(log_dir, f"{logger_name}.log"),
                maxBytes=config.max_bytes,
                backupCount=config.backup_count,
                encoding='utf-8'
            )
        else:  # time-based
            file_handler = TimedRotatingFileHandler(
                filename=os.path.join(log_dir, f"{logger_name}.log"),
                when=config.time_interval,
                backupCount=config.backup_count,
                encoding='utf-8'
            )
        
        file_handler.setLevel(get_log_level(config.log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 防止日志传播到根记录器
    logger.propagate = False
    
    logger.info(f"日志系统初始化完成 (级别：{config.log_level}, 格式：{config.log_format})")
    
    return logger


def get_logger(name: str = "marine_engineer") -> logging.Logger:
    """
    获取日志记录器的便捷函数
    
    :param name: 日志记录器名称
    :return: 日志记录器
    """
    return logging.getLogger(name)


class LogContext:
    """
    日志上下文管理器
    
    用于在特定上下文中添加额外的日志字段。
    """
    
    def __init__(self, logger: logging.Logger, **extra_fields):
        """
        初始化日志上下文
        
        :param logger: 日志记录器
        :param extra_fields: 额外字段
        """
        self.logger = logger
        self.extra_fields = extra_fields
        self.old_factory = None
    
    def __enter__(self):
        """进入上下文"""
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.extra_fields.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


def log_function_call(logger: logging.Logger):
    """
    函数调用日志装饰器
    
    自动记录函数的调用参数和返回值。
    
    :param logger: 日志记录器
    :return: 装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"调用 {func.__name__}, 参数：args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} 返回：{result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} 异常：{e}", exc_info=True)
                raise
        return wrapper
    return decorator


# 默认日志配置实例
default_config = LoggingConfig()

# 预配置的日志记录器
marine_logger = setup_logging(
    logger_name="marine_engineer",
    config=default_config,
    console_output=True,
    file_output=True
)


if __name__ == "__main__":
    # 测试日志系统
    print("测试日志系统...")
    
    # 测试 JSON 格式
    json_config = LoggingConfig(log_format="json", log_level="DEBUG")
    json_logger = setup_logging("test_json", json_config, file_output=False)
    
    json_logger.debug("这是一条 DEBUG 日志")
    json_logger.info("这是一条 INFO 日志")
    json_logger.warning("这是一条 WARNING 日志")
    json_logger.error("这是一条 ERROR 日志")
    
    # 测试额外字段
    with LogContext(json_logger, user_id="12345", action="test"):
        json_logger.info("带上下文的日志")
    
    # 测试函数调用日志
    @log_function_call(json_logger)
    def test_function(x, y):
        return x + y
    
    result = test_function(10, 20)
    print(f"测试结果：{result}")
    
    print("\n日志系统测试完成!")
