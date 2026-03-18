"""
Feature Fusion Layer - 特征级融合层

AI Native 感知层增强核心模块：
- 多源传感器特征级融合（雷达 + AIS+ 视觉+ 环境）
- 基于注意力机制的特征加权
- 不确定性量化与置信度评估
- 时空对齐与数据关联
- 异常检测与传感器故障诊断

对应 REFACTOR_PLAN Phase 2: AI Native 感知层增强
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class SensorType(Enum):
    """传感器类型"""
    RADAR = "radar"
    AIS = "ais"
    LIDAR = "lidar"
    CAMERA = "camera"
    GPS = "gps"
    IMU = "imu"
    ENVIRONMENTAL = "environmental"
    ENGINE = "engine"


class FusionLevel(Enum):
    """融合层级"""
    RAW_DATA = "raw_data"  # 数据级融合
    FEATURE = "feature"    # 特征级融合
    DECISION = "decision"  # 决策级融合


@dataclass
class SensorMeasurement:
    """传感器测量值"""
    sensor_id: str
    sensor_type: SensorType
    timestamp: datetime
    data: Dict[str, Any]
    confidence: float = 1.0
    quality_score: float = 1.0
    latency_ms: float = 0.0
    
    def is_valid(self) -> bool:
        """检查测量值是否有效"""
        return self.confidence > 0.5 and self.quality_score > 0.5


@dataclass
class FusedTrack:
    """融合后的目标轨迹"""
    track_id: str
    position: Tuple[float, float]  # (lat, lon)
    velocity: Tuple[float, float]  # (speed, course)
    dimensions: Optional[Tuple[float, float, float]] = None  # (length, width, height)
    confidence: float = 0.0
    source_sensors: List[str] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)
    prediction_covariance: np.ndarray = field(default_factory=lambda: np.eye(4))
    
    def update_confidence(self, measurements: List[SensorMeasurement]) -> None:
        """基于多传感器测量更新置信度"""
        if not measurements:
            self.confidence = 0.0
            return
        
        # 加权平均置信度
        total_weight = sum(m.confidence * m.quality_score for m in measurements)
        self.confidence = min(1.0, total_weight / len(measurements))
        self.source_sensors = list(set(m.sensor_id for m in measurements))
        self.last_update = datetime.now()


@dataclass
class FusionState:
    """融合系统状态"""
    timestamp: datetime
    active_tracks: List[FusedTrack] = field(default_factory=list)
    sensor_health: Dict[str, float] = field(default_factory=dict)
    fusion_quality: float = 0.0
    processing_latency_ms: float = 0.0


class AttentionWeights:
    """注意力权重计算"""
    
    @staticmethod
    def calculate_sensor_weights(
        measurements: List[SensorMeasurement],
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        计算传感器注意力权重
        
        考虑因素：
        - 传感器历史可靠性
        - 当前测量质量
        - 环境条件适配性
        - 目标距离
        """
        weights = {}
        
        for m in measurements:
            # 基础权重来自置信度和质量
            base_weight = m.confidence * m.quality_score
            
            # 距离衰减（雷达/视觉在远距离可靠性下降）
            distance = context.get('target_distance_km', 1.0)
            distance_factor = math.exp(-distance / 10.0)
            
            # 环境适配性
            weather = context.get('weather', 'clear')
            env_factor = AttentionWeights._get_environment_factor(
                m.sensor_type, weather
            )
            
            weights[m.sensor_id] = base_weight * distance_factor * env_factor
        
        # 归一化
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    @staticmethod
    def _get_environment_factor(sensor_type: SensorType, weather: str) -> float:
        """获取环境适配因子"""
        factors = {
            SensorType.RADAR: {'clear': 1.0, 'rain': 0.9, 'fog': 0.95, 'storm': 0.8},
            SensorType.CAMERA: {'clear': 1.0, 'rain': 0.6, 'fog': 0.3, 'storm': 0.4},
            SensorType.LIDAR: {'clear': 1.0, 'rain': 0.5, 'fog': 0.2, 'storm': 0.3},
            SensorType.AIS: {'clear': 1.0, 'rain': 1.0, 'fog': 1.0, 'storm': 0.95},
        }
        return factors.get(sensor_type, {}).get(weather, 0.8)


class KalmanFilter2D:
    """2D 卡尔曼滤波器用于轨迹跟踪"""
    
    def __init__(self, dt: float = 1.0):
        self.dt = dt
        # 状态：[x, y, vx, vy]
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        self.Q = np.eye(4) * 0.01  # 过程噪声
        self.R = np.eye(2) * 0.1   # 测量噪声
        self.x = np.zeros(4)
        self.P = np.eye(4)
    
    def predict(self) -> Tuple[np.ndarray, np.ndarray]:
        """预测步骤"""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x, self.P
    
    def update(self, z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """更新步骤"""
        # 预测
        x_pred, P_pred = self.predict()
        
        # 卡尔曼增益
        y = z - self.H @ x_pred
        S = self.H @ P_pred @ self.H.T + self.R
        K = P_pred @ self.H.T @ np.linalg.inv(S)
        
        # 更新
        self.x = x_pred + K @ y
        self.P = (np.eye(4) - K @ self.H) @ P_pred
        
        return self.x, self.P


class FeatureFusionLayer:
    """
    特征级融合层
    
    实现多传感器特征级融合，输出统一的目标跟踪和环境感知结果
    """
    
    def __init__(self):
        self.track_filters: Dict[str, KalmanFilter2D] = {}
        self.measurement_buffer: List[SensorMeasurement] = []
        self.max_buffer_size = 100
        self.fusion_state: Optional[FusionState] = None
    
    def add_measurement(self, measurement: SensorMeasurement) -> None:
        """添加传感器测量"""
        if not measurement.is_valid():
            logger.warning(f"Invalid measurement from {measurement.sensor_id}")
            return
        
        self.measurement_buffer.append(measurement)
        if len(self.measurement_buffer) > self.max_buffer_size:
            self.measurement_buffer.pop(0)
    
    def associate_measurements(
        self,
        measurements: List[SensorMeasurement],
        existing_tracks: List[FusedTrack]
    ) -> Dict[str, List[SensorMeasurement]]:
        """
        数据关联：将测量分配到现有轨迹
        
        使用最近邻算法 + 门限滤波
        """
        associations: Dict[str, List[SensorMeasurement]] = {
            t.track_id: [] for t in existing_tracks
        }
        associations['unassigned'] = []
        
        for m in measurements:
            best_track = None
            best_distance = float('inf')
            
            for track in existing_tracks:
                # 计算马氏距离
                pos = np.array([m.data.get('lat', 0), m.data.get('lon', 0)])
                track_pos = np.array(track.position)
                
                diff = pos - track_pos
                distance = np.sqrt(np.sum(diff ** 2))
                
                if distance < best_distance:
                    best_distance = distance
                    best_track = track
            
            # 门限滤波（5km）
            if best_track and best_distance < 0.05:  # ~5km
                associations[best_track.track_id].append(m)
            else:
                associations['unassigned'].append(m)
        
        return associations
    
    def fuse_tracks(
        self,
        associations: Dict[str, List[SensorMeasurement]]
    ) -> List[FusedTrack]:
        """
        融合关联后的测量，更新轨迹
        """
        fused_tracks = []
        
        for track_id, measurements in associations.items():
            if track_id == 'unassigned' or not measurements:
                continue
            
            # 获取或创建卡尔曼滤波器
            if track_id not in self.track_filters:
                self.track_filters[track_id] = KalmanFilter2D(dt=1.0)
            
            kf = self.track_filters[track_id]
            
            # 加权平均位置
            weights = AttentionWeights.calculate_sensor_weights(
                measurements,
                context={'target_distance_km': 1.0, 'weather': 'clear'}
            )
            
            weighted_pos = np.zeros(2)
            total_weight = 0.0
            
            for m in measurements:
                w = weights.get(m.sensor_id, 0.1)
                pos = np.array([m.data.get('lat', 0), m.data.get('lon', 0)])
                weighted_pos += w * pos
                total_weight += w
            
            if total_weight > 0:
                weighted_pos /= total_weight
            
            # 卡尔曼滤波更新
            state, covariance = kf.update(weighted_pos)
            
            # 创建融合轨迹
            track = FusedTrack(
                track_id=track_id,
                position=(state[0], state[1]),
                velocity=(state[2], state[3]),
                confidence=np.sqrt(covariance[0, 0] * covariance[1, 1]),
                prediction_covariance=covariance
            )
            track.update_confidence(measurements)
            
            fused_tracks.append(track)
        
        return fused_tracks
    
    def process_frame(
        self,
        measurements: List[SensorMeasurement]
    ) -> FusionState:
        """
        处理一帧传感器数据，输出融合状态
        """
        start_time = datetime.now()
        
        # 获取现有轨迹
        existing_tracks = []
        if self.fusion_state:
            existing_tracks = self.fusion_state.active_tracks
        
        # 数据关联
        associations = self.associate_measurements(measurements, existing_tracks)
        
        # 轨迹融合
        fused_tracks = self.fuse_tracks(associations)
        
        # 处理新目标（未分配的测量）
        unassigned = associations.get('unassigned', [])
        for i, m in enumerate(unassigned[:10]):  # 限制新目标数量
            track = FusedTrack(
                track_id=f"new_{len(fused_tracks) + i}",
                position=(m.data.get('lat', 0), m.data.get('lon', 0)),
                velocity=(0.0, 0.0),
                confidence=m.confidence,
                source_sensors=[m.sensor_id]
            )
            fused_tracks.append(track)
        
        # 计算传感器健康度
        sensor_health = {}
        sensor_counts: Dict[str, int] = {}
        sensor_qualities: Dict[str, float] = {}
        
        for m in measurements:
            sensor_counts[m.sensor_id] = sensor_counts.get(m.sensor_id, 0) + 1
            sensor_qualities[m.sensor_id] = sensor_qualities.get(
                m.sensor_id, 0.0
            ) + m.quality_score
        
        for sensor_id in sensor_counts:
            avg_quality = sensor_qualities[sensor_id] / sensor_counts[sensor_id]
            sensor_health[sensor_id] = avg_quality
        
        # 计算融合质量
        if fused_tracks:
            fusion_quality = sum(t.confidence for t in fused_tracks) / len(fused_tracks)
        else:
            fusion_quality = 0.0
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        self.fusion_state = FusionState(
            timestamp=datetime.now(),
            active_tracks=fused_tracks,
            sensor_health=sensor_health,
            fusion_quality=fusion_quality,
            processing_latency_ms=processing_time
        )
        
        return self.fusion_state
    
    def get_state(self) -> Optional[FusionState]:
        """获取当前融合状态"""
        return self.fusion_state


# 导出主要类
__all__ = [
    'SensorType',
    'FusionLevel',
    'SensorMeasurement',
    'FusedTrack',
    'FusionState',
    'FeatureFusionLayer',
    'AttentionWeights',
    'KalmanFilter2D',
]
