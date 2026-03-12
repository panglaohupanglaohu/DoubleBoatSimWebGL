"""
Navigation Data Channel - 导航数据集成

整合船舶导航传感器数据：GPS、罗经、测深仪、计程仪等
支持 NMEA 0183/NMEA 2000 协议，提供统一的导航数据接口

Author: CaptainCatamaran 🐱⛵
Version: 1.0.0
Date: 2026-03-12
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .base import Channel

logger = logging.getLogger(__name__)


class NavSourceType(Enum):
    """导航传感器类型"""
    GPS = "gps"
    GNSS = "gnss"
    COMPASS = "compass"
    GYRO = "gyro"
    DEPTH = "depth"
    LOG = "log"
    AIS = "ais"
    RADAR = "radar"
    WIND = "wind"
    IMU = "imu"


class NavFixQuality(Enum):
    """定位质量"""
    INVALID = 0
    GPS_FIX = 1
    DGPS_FIX = 2
    PPS_FIX = 3
    RTK_FIX = 4
    FLOAT_RTK = 5
    ESTIMATED = 6
    MANUAL = 7
    SIMULATION = 8


@dataclass
class GPSPosition:
    """GPS 位置数据"""
    latitude: float  # 纬度 (-90 to 90)
    longitude: float  # 经度 (-180 to 180)
    altitude_m: Optional[float] = None  # 海拔高度 (米)
    quality: NavFixQuality = NavFixQuality.INVALID  # 定位质量
    satellites: int = 0  # 可见卫星数
    hdop: float = 99.9  # 水平精度因子
    vdop: float = 99.9  # 垂直精度因子
    pdop: float = 99.9  # 位置精度因子
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "GPS"
    
    def is_valid(self) -> bool:
        """检查位置数据是否有效"""
        return (
            self.quality != NavFixQuality.INVALID
            and -90 <= self.latitude <= 90
            and -180 <= self.longitude <= 180
            and self.satellites >= 3
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude_m": self.altitude_m,
            "quality": self.quality.name,
            "satellites": self.satellites,
            "hdop": self.hdop,
            "vdop": self.vdop,
            "pdop": self.pdop,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "valid": self.is_valid()
        }


@dataclass
class Heading:
    """航向数据"""
    true_heading: float  # 真航向 (0-360°)
    magnetic_heading: Optional[float] = None  # 磁航向
    magnetic_variation: float = 0.0  # 磁差
    rate_of_turn: float = 0.0  # 转向速率 (°/min)
    accuracy: float = 0.0  # 精度 (°)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "GYRO"
    status: str = "OK"  # OK/WARNING/FAILURE
    
    def is_valid(self) -> bool:
        """检查航向数据是否有效"""
        return 0 <= self.true_heading < 360 and self.status == "OK"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "true_heading": self.true_heading,
            "magnetic_heading": self.magnetic_heading,
            "magnetic_variation": self.magnetic_variation,
            "rate_of_turn": self.rate_of_turn,
            "accuracy": self.accuracy,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "status": self.status,
            "valid": self.is_valid()
        }


@dataclass
class Depth:
    """水深数据"""
    depth_m: float  # 水深 (米)
    offset_m: float = 0.0  # 传感器偏移 (米)
    temperature_c: Optional[float] = None  # 水温 (°C)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "ECHO"
    
    def is_valid(self) -> bool:
        """检查水深数据是否有效"""
        return self.depth_m >= 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "depth_m": self.depth_m,
            "offset_m": self.offset_m,
            "temperature_c": self.temperature_c,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "valid": self.is_valid()
        }


@dataclass
class Speed:
    """速度数据"""
    speed_knots: float  # 速度 (节)
    speed_kmh: Optional[float] = None  # 速度 (km/h)
    speed_ms: Optional[float] = None  # 速度 (m/s)
    distance_nm: float = 0.0  # 累计航程 (海里)
    trip_distance_nm: float = 0.0  # 航次航程 (海里)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "LOG"
    
    def __post_init__(self):
        """单位转换"""
        if self.speed_kmh is None:
            self.speed_kmh = self.speed_knots * 1.852
        if self.speed_ms is None:
            self.speed_ms = self.speed_knots * 0.514444
    
    def is_valid(self) -> bool:
        """检查速度数据是否有效"""
        return self.speed_knots >= 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "speed_knots": self.speed_knots,
            "speed_kmh": self.speed_kmh,
            "speed_ms": self.speed_ms,
            "distance_nm": self.distance_nm,
            "trip_distance_nm": self.trip_distance_nm,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "valid": self.is_valid()
        }


@dataclass
class NavStatus:
    """导航状态"""
    position: Optional[GPSPosition] = None
    heading: Optional[Heading] = None
    depth: Optional[Depth] = None
    speed: Optional[Speed] = None
    course_over_ground: float = 0.0  # 对地航向
    speed_over_ground: float = 0.0  # 对地速度
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_navigating(self) -> bool:
        """检查是否在航行中"""
        return (
            self.position is not None
            and self.position.is_valid()
            and self.speed is not None
            and self.speed.speed_knots > 0.5
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "position": self.position.to_dict() if self.position else None,
            "heading": self.heading.to_dict() if self.heading else None,
            "depth": self.depth.to_dict() if self.depth else None,
            "speed": self.speed.to_dict() if self.speed else None,
            "course_over_ground": self.course_over_ground,
            "speed_over_ground": self.speed_over_ground,
            "timestamp": self.timestamp.isoformat(),
            "navigating": self.is_navigating()
        }


class NavigationDataChannel(Channel):
    """
    导航数据集成 Channel
    
    功能:
    - GPS/GNSS 位置数据
    - 罗经/陀螺罗经航向
    - 测深仪水深
    - 计程仪速度/航程
    - NMEA 0183/2000 协议支持
    - 多传感器数据融合
    """
    
    name = "navigation_data"
    description = "船舶导航数据集成 (GPS/罗经/测深/计程仪)"
    version = "1.0.0"
    
    # NMEA 0183 句子类型
    NMEA_SENTENCES = {
        "GGA": "GPS Fix Data",
        "RMC": "Recommended Minimum Navigation Information",
        "HDT": "Heading - True",
        "HDG": "Heading - Magnetic",
        "ROT": "Rate of Turn",
        "DBT": "Depth Below Transducer",
        "DPT": "Depth",
        "VLW": "Distance Traveled",
        "VTG": "Course Over Ground and Ground Speed",
        "GSA": "GNSS DOP and Active Satellites",
        "GSV": "GNSS Satellites in View",
    }
    
    def __init__(self):
        """初始化导航数据 Channel"""
        super().__init__()
        self._position: Optional[GPSPosition] = None
        self._heading: Optional[Heading] = None
        self._depth: Optional[Depth] = None
        self._speed: Optional[Speed] = None
        self._sensors: Dict[str, Dict[str, Any]] = {}
        self._alarms: List[Dict[str, Any]] = []
        self._last_update: Dict[str, datetime] = {}
        
        # 阈值配置
        self._config = {
            "depth_warning_m": 10.0,  # 水深警告阈值
            "depth_critical_m": 5.0,  # 水深危险阈值
            "speed_max_knots": 30.0,  # 最大速度警告
            "heading_drift_deg": 5.0,  # 航向漂移警告
            "gps_timeout_s": 30.0,  # GPS 超时阈值
        }
    
    def check(self) -> Tuple[str, str]:
        """
        检查导航数据通道状态
        
        Returns:
            Tuple[str, str]: (状态，消息)
        """
        try:
            status_parts = []
            warnings = []
            
            # 检查 GPS
            if self._position and self._position.is_valid():
                status_parts.append(f"GPS: OK ({self._position.satellites} satellites)")
            else:
                warnings.append("GPS: No valid fix")
            
            # 检查罗经
            if self._heading and self._heading.is_valid():
                status_parts.append(f"Compass: OK ({self._heading.true_heading:.1f}°)")
            else:
                warnings.append("Compass: No valid data")
            
            # 检查测深
            if self._depth and self._depth.is_valid():
                status_parts.append(f"Depth: OK ({self._depth.depth_m:.1f}m)")
            else:
                warnings.append("Depth: No valid data")
            
            # 检查计程仪
            if self._speed and self._speed.is_valid():
                status_parts.append(f"Log: OK ({self._speed.speed_knots:.1f} kn)")
            else:
                warnings.append("Log: No valid data")
            
            # 检查传感器超时
            now = datetime.now(timezone.utc)
            for sensor, last_time in self._last_update.items():
                delta = (now - last_time).total_seconds()
                if delta > self._config["gps_timeout_s"]:
                    warnings.append(f"{sensor}: Timeout ({delta:.0f}s)")
            
            if warnings:
                return "warn", "; ".join(status_parts + warnings)
            elif status_parts:
                return "ok", "; ".join(status_parts)
            else:
                return "off", "No navigation data available"
                
        except Exception as e:
            logger.error(f"Navigation data check failed: {e}")
            return "off", f"Error: {str(e)}"
    
    def can_handle(self, url: str) -> bool:
        """
        检查是否能处理给定的 URL
        
        Args:
            url: URL 字符串
            
        Returns:
            bool: 是否能处理
        """
        # 不支持 URL 处理，这是传感器数据通道
        return False
    
    def process(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """
        处理导航数据请求
        
        Args:
            url: 请求 URL (未使用)
            **kwargs: 额外参数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        return {
            "status": "ok",
            "channel": self.name,
            "data": self.get_nav_status(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # ==================== 数据更新接口 ====================
    
    def update_position(
        self,
        latitude: float,
        longitude: float,
        altitude_m: Optional[float] = None,
        quality: int = 1,
        satellites: int = 0,
        hdop: float = 99.9,
        vdop: float = 99.9,
        pdop: float = 99.9,
        source: str = "GPS"
    ) -> GPSPosition:
        """
        更新 GPS 位置数据
        
        Args:
            latitude: 纬度
            longitude: 经度
            altitude_m: 海拔高度
            quality: 定位质量 (0-8)
            satellites: 可见卫星数
            hdop: 水平精度因子
            vdop: 垂直精度因子
            pdop: 位置精度因子
            source: 数据源
            
        Returns:
            GPSPosition: 更新后的位置数据
        """
        try:
            fix_quality = NavFixQuality(quality) if quality in range(9) else NavFixQuality.INVALID
            
            self._position = GPSPosition(
                latitude=latitude,
                longitude=longitude,
                altitude_m=altitude_m,
                quality=fix_quality,
                satellites=satellites,
                hdop=hdop,
                vdop=vdop,
                pdop=pdop,
                timestamp=datetime.now(timezone.utc),
                source=source
            )
            self._last_update["GPS"] = self._position.timestamp
            
            # 检查定位质量
            if fix_quality == NavFixQuality.INVALID:
                self._add_alarm("GPS", "Invalid fix", "warning")
            elif satellites < 4:
                self._add_alarm("GPS", f"Low satellites ({satellites})", "warning")
            
            return self._position
            
        except Exception as e:
            logger.error(f"Failed to update position: {e}")
            raise
    
    def update_heading(
        self,
        true_heading: float,
        magnetic_heading: Optional[float] = None,
        magnetic_variation: float = 0.0,
        rate_of_turn: float = 0.0,
        accuracy: float = 0.0,
        status: str = "OK",
        source: str = "GYRO"
    ) -> Heading:
        """
        更新航向数据
        
        Args:
            true_heading: 真航向 (0-360°)
            magnetic_heading: 磁航向
            magnetic_variation: 磁差
            rate_of_turn: 转向速率
            accuracy: 精度
            status: 状态
            source: 数据源
            
        Returns:
            Heading: 更新后的航向数据
        """
        try:
            # 标准化航向到 0-360
            true_heading = true_heading % 360
            if magnetic_heading is not None:
                magnetic_heading = magnetic_heading % 360
            
            self._heading = Heading(
                true_heading=true_heading,
                magnetic_heading=magnetic_heading,
                magnetic_variation=magnetic_variation,
                rate_of_turn=rate_of_turn,
                accuracy=accuracy,
                timestamp=datetime.now(timezone.utc),
                source=source,
                status=status
            )
            self._last_update["COMPASS"] = self._heading.timestamp
            
            # 检查状态
            if status != "OK":
                self._add_alarm("COMPASS", f"Status: {status}", "warning")
            
            return self._heading
            
        except Exception as e:
            logger.error(f"Failed to update heading: {e}")
            raise
    
    def update_depth(
        self,
        depth_m: float,
        offset_m: float = 0.0,
        temperature_c: Optional[float] = None,
        source: str = "ECHO"
    ) -> Depth:
        """
        更新水深数据
        
        Args:
            depth_m: 水深 (米)
            offset_m: 传感器偏移
            temperature_c: 水温
            source: 数据源
            
        Returns:
            Depth: 更新后的水深数据
        """
        try:
            self._depth = Depth(
                depth_m=depth_m,
                offset_m=offset_m,
                temperature_c=temperature_c,
                timestamp=datetime.now(timezone.utc),
                source=source
            )
            self._last_update["DEPTH"] = self._depth.timestamp
            
            # 检查水深警告
            if depth_m < self._config["depth_critical_m"]:
                self._add_alarm("DEPTH", f"Critical depth: {depth_m:.1f}m", "critical")
            elif depth_m < self._config["depth_warning_m"]:
                self._add_alarm("DEPTH", f"Shallow water: {depth_m:.1f}m", "warning")
            
            return self._depth
            
        except Exception as e:
            logger.error(f"Failed to update depth: {e}")
            raise
    
    def update_speed(
        self,
        speed_knots: float,
        distance_nm: float = 0.0,
        trip_distance_nm: float = 0.0,
        source: str = "LOG"
    ) -> Speed:
        """
        更新速度数据
        
        Args:
            speed_knots: 速度 (节)
            distance_nm: 累计航程
            trip_distance_nm: 航次航程
            source: 数据源
            
        Returns:
            Speed: 更新后的速度数据
        """
        try:
            self._speed = Speed(
                speed_knots=speed_knots,
                distance_nm=distance_nm,
                trip_distance_nm=trip_distance_nm,
                timestamp=datetime.now(timezone.utc),
                source=source
            )
            self._last_update["LOG"] = self._speed.timestamp
            
            # 检查超速
            if speed_knots > self._config["speed_max_knots"]:
                self._add_alarm("LOG", f"High speed: {speed_knots:.1f} kn", "warning")
            
            return self._speed
            
        except Exception as e:
            logger.error(f"Failed to update speed: {e}")
            raise
    
    # ==================== 数据查询接口 ====================
    
    def get_position(self) -> Optional[GPSPosition]:
        """获取当前位置"""
        return self._position
    
    def get_heading(self) -> Optional[Heading]:
        """获取当前航向"""
        return self._heading
    
    def get_depth(self) -> Optional[Depth]:
        """获取当前水深"""
        return self._depth
    
    def get_speed(self) -> Optional[Speed]:
        """获取当前速度"""
        return self._speed
    
    def get_nav_status(self) -> NavStatus:
        """获取完整导航状态"""
        return NavStatus(
            position=self._position,
            heading=self._heading,
            depth=self._depth,
            speed=self._speed,
            timestamp=datetime.now(timezone.utc)
        )
    
    def get_sensor_status(self) -> Dict[str, Any]:
        """获取传感器状态"""
        now = datetime.now(timezone.utc)
        sensors = {}
        
        for sensor_name, last_time in self._last_update.items():
            delta = (now - last_time).total_seconds()
            sensors[sensor_name] = {
                "last_update": last_time.isoformat(),
                "age_seconds": delta,
                "status": "ok" if delta < self._config["gps_timeout_s"] else "timeout"
            }
        
        return {
            "sensors": sensors,
            "total_sensors": len(sensors),
            "active_sensors": sum(1 for s in sensors.values() if s["status"] == "ok")
        }
    
    def get_alarms(self) -> List[Dict[str, Any]]:
        """获取当前报警"""
        return self._alarms.copy()
    
    def clear_alarms(self) -> None:
        """清除所有报警"""
        self._alarms.clear()
    
    def configure_thresholds(
        self,
        depth_warning_m: Optional[float] = None,
        depth_critical_m: Optional[float] = None,
        speed_max_knots: Optional[float] = None,
        gps_timeout_s: Optional[float] = None
    ) -> None:
        """
        配置报警阈值
        
        Args:
            depth_warning_m: 水深警告阈值
            depth_critical_m: 水深危险阈值
            speed_max_knots: 最大速度警告
            gps_timeout_s: GPS 超时阈值
        """
        if depth_warning_m is not None:
            self._config["depth_warning_m"] = depth_warning_m
        if depth_critical_m is not None:
            self._config["depth_critical_m"] = depth_critical_m
        if speed_max_knots is not None:
            self._config["speed_max_knots"] = speed_max_knots
        if gps_timeout_s is not None:
            self._config["gps_timeout_s"] = gps_timeout_s
    
    # ==================== 辅助方法 ====================
    
    def _add_alarm(self, sensor: str, message: str, level: str) -> None:
        """添加报警"""
        alarm = {
            "sensor": sensor,
            "message": message,
            "level": level,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._alarms.append(alarm)
        logger.warning(f"Navigation alarm [{level}]: {sensor} - {message}")
    
    def register_sensor(
        self,
        sensor_id: str,
        sensor_type: NavSourceType,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        注册传感器
        
        Args:
            sensor_id: 传感器 ID
            sensor_type: 传感器类型
            config: 配置参数
        """
        self._sensors[sensor_id] = {
            "type": sensor_type.value,
            "config": config or {},
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        logger.info(f"Registered sensor: {sensor_id} ({sensor_type.value})")
    
    def get_sensor_list(self) -> List[Dict[str, Any]]:
        """获取传感器列表"""
        return [
            {"id": sid, **info}
            for sid, info in self._sensors.items()
        ]
    
    def simulate_data(self) -> NavStatus:
        """
        生成仿真导航数据 (用于测试)
        
        Returns:
            NavStatus: 仿真导航状态
        """
        import random
        
        # 仿真位置 (中国沿海)
        self.update_position(
            latitude=22.0 + random.uniform(-0.1, 0.1),
            longitude=114.0 + random.uniform(-0.1, 0.1),
            altitude_m=random.uniform(0, 10),
            quality=1,
            satellites=random.randint(6, 12),
            hdop=random.uniform(0.8, 2.0),
            source="GPS_SIM"
        )
        
        # 仿真航向
        self.update_heading(
            true_heading=random.uniform(0, 360),
            magnetic_heading=random.uniform(0, 360),
            magnetic_variation=-2.5,
            rate_of_turn=random.uniform(-5, 5),
            source="GYRO_SIM"
        )
        
        # 仿真水深
        self.update_depth(
            depth_m=random.uniform(10, 100),
            temperature_c=random.uniform(15, 30),
            source="ECHO_SIM"
        )
        
        # 仿真速度
        self.update_speed(
            speed_knots=random.uniform(5, 15),
            distance_nm=random.uniform(100, 1000),
            source="LOG_SIM"
        )
        
        return self.get_nav_status()


# ==================== NMEA 解析辅助函数 ====================

def parse_nmea_gga(sentence: str) -> Optional[Dict[str, Any]]:
    """
    解析 NMEA GGA 句子 (GPS Fix Data)
    
    $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
    
    Returns:
        Dict with: time, latitude, longitude, quality, satellites, hdop, altitude
    """
    try:
        parts = sentence.split(",")
        if len(parts) < 15 or not parts[0].endswith("GGA"):
            return None
        
        def parse_lat(value: str, direction: str) -> float:
            """解析纬度 (DDMM.MMMM)"""
            if not value or not direction:
                return 0.0
            degrees = float(value[:2])  # 纬度 2 位度数
            minutes = float(value[2:])
            result = degrees + minutes / 60.0
            if direction in ["S", "W"]:
                result = -result
            return result
        
        def parse_lon(value: str, direction: str) -> float:
            """解析经度 (DDDMM.MMMM)"""
            if not value or not direction:
                return 0.0
            degrees = float(value[:3])  # 经度 3 位度数
            minutes = float(value[3:])
            result = degrees + minutes / 60.0
            if direction in ["S", "W"]:
                result = -result
            return result
        
        return {
            "time": parts[1],
            "latitude": parse_lat(parts[2], parts[3]),
            "longitude": parse_lon(parts[4], parts[5]),
            "quality": int(parts[6]) if parts[6] else 0,
            "satellites": int(parts[7]) if parts[7] else 0,
            "hdop": float(parts[8]) if parts[8] else 99.9,
            "altitude": float(parts[9]) if parts[9] else None,
        }
    except Exception as e:
        logger.error(f"Failed to parse GGA: {e}")
        return None


def parse_nmea_rmc(sentence: str) -> Optional[Dict[str, Any]]:
    """
    解析 NMEA RMC 句子 (Recommended Minimum Navigation Information)
    
    $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
    
    Returns:
        Dict with: time, status, latitude, longitude, speed, course, date
    """
    try:
        # Remove checksum part
        if "*" in sentence:
            sentence = sentence.split("*")[0]
        
        parts = sentence.split(",")
        if len(parts) < 12 or not parts[0].endswith("RMC"):
            return None
        
        def parse_lat(value: str, direction: str) -> float:
            """解析纬度 (DDMM.MMMM)"""
            if not value or not direction:
                return 0.0
            degrees = float(value[:2])
            minutes = float(value[2:])
            result = degrees + minutes / 60.0
            if direction in ["S", "W"]:
                result = -result
            return result
        
        def parse_lon(value: str, direction: str) -> float:
            """解析经度 (DDDMM.MMMM)"""
            if not value or not direction:
                return 0.0
            degrees = float(value[:3])
            minutes = float(value[3:])
            result = degrees + minutes / 60.0
            if direction in ["S", "W"]:
                result = -result
            return result
        
        return {
            "time": parts[1],
            "status": parts[2],  # A=Active, V=Void
            "latitude": parse_lat(parts[3], parts[4]),
            "longitude": parse_lon(parts[5], parts[6]),
            "speed_knots": float(parts[7]) if parts[7] else 0.0,
            "course": float(parts[8]) if parts[8] else 0.0,
            "date": parts[9],
            "magnetic_variation": float(parts[10]) if parts[10] else 0.0,
        }
    except Exception as e:
        logger.error(f"Failed to parse RMC: {e}")
        return None


def parse_nmea_hdt(sentence: str) -> Optional[float]:
    """
    解析 NMEA HDT 句子 (Heading - True)
    
    $HEHDT,123.4,T*1A
    
    Returns:
        True heading in degrees, or None
    """
    try:
        # Remove checksum part
        if "*" in sentence:
            sentence = sentence.split("*")[0]
        
        parts = sentence.split(",")
        if len(parts) < 3 or not parts[0].endswith("HDT"):
            return None
        
        if parts[2].strip().upper() != "T":
            return None
        
        return float(parts[1])
    except Exception as e:
        logger.error(f"Failed to parse HDT: {e}")
        return None


def parse_nmea_dbt(sentence: str) -> Optional[float]:
    """
    解析 NMEA DBT 句子 (Depth Below Transducer)
    
    $SDDBT,025.5,f,007.8,M,004.2,F*XX
    
    Returns:
        Depth in meters, or None
    """
    try:
        # Remove checksum part
        if "*" in sentence:
            sentence = sentence.split("*")[0]
        
        parts = sentence.split(",")
        if len(parts) < 6 or not parts[0].endswith("DBT"):
            return None
        
        # 优先使用米制单位
        if len(parts) > 4 and parts[4] == "M":
            return float(parts[3]) if parts[3] else None
        # 转换英尺到米
        elif len(parts) > 2 and parts[2] == "f":
            feet = float(parts[1]) if parts[1] else 0
            return feet * 0.3048
        
        return None
    except Exception as e:
        logger.error(f"Failed to parse DBT: {e}")
        return None


def parse_nmea_vlw(sentence: str) -> Optional[Dict[str, float]]:
    """
    解析 NMEA VLW 句子 (Distance Traveled)
    
    $XXVLW,002.5,N,015.3,N*XX
    
    Returns:
        Dict with cumulative and trip distance in nautical miles
    """
    try:
        parts = sentence.split(",")
        if len(parts) < 5 or parts[0] not in ["$XXVLW", "$VLW"]:
            return None
        
        return {
            "cumulative_nm": float(parts[1]) if parts[1] else 0.0,
            "trip_nm": float(parts[3]) if parts[3] else 0.0,
        }
    except Exception as e:
        logger.error(f"Failed to parse VLW: {e}")
        return None
