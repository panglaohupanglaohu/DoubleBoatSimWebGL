"""
Feature Fusion Layer 单元测试
"""

import unittest
from datetime import datetime

import numpy as np

from src.backend.channels.feature_fusion_layer import (
    AttentionWeights,
    FeatureFusionLayer,
    FusionState,
    FusedTrack,
    KalmanFilter2D,
    SensorMeasurement,
    SensorType,
)


class TestSensorMeasurement(unittest.TestCase):
    """传感器测量测试"""
    
    def test_valid_measurement(self):
        """有效测量"""
        m = SensorMeasurement(
            sensor_id="radar_1",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.now(),
            data={"lat": 31.2, "lon": 121.5},
            confidence=0.9,
            quality_score=0.85
        )
        self.assertTrue(m.is_valid())
    
    def test_invalid_measurement_low_confidence(self):
        """低置信度测量"""
        m = SensorMeasurement(
            sensor_id="camera_1",
            sensor_type=SensorType.CAMERA,
            timestamp=datetime.now(),
            data={"lat": 31.2, "lon": 121.5},
            confidence=0.3,
            quality_score=0.9
        )
        self.assertFalse(m.is_valid())
    
    def test_invalid_measurement_low_quality(self):
        """低质量测量"""
        m = SensorMeasurement(
            sensor_id="lidar_1",
            sensor_type=SensorType.LIDAR,
            timestamp=datetime.now(),
            data={"lat": 31.2, "lon": 121.5},
            confidence=0.9,
            quality_score=0.4
        )
        self.assertFalse(m.is_valid())


class TestFusedTrack(unittest.TestCase):
    """融合轨迹测试"""
    
    def test_track_creation(self):
        """轨迹创建"""
        track = FusedTrack(
            track_id="track_001",
            position=(31.2, 121.5),
            velocity=(10.5, 45.0)
        )
        self.assertEqual(track.track_id, "track_001")
        self.assertEqual(track.position, (31.2, 121.5))
        self.assertEqual(track.velocity, (10.5, 45.0))
    
    def test_confidence_update(self):
        """置信度更新"""
        track = FusedTrack(
            track_id="track_001",
            position=(31.2, 121.5),
            velocity=(10.5, 45.0)
        )
        
        measurements = [
            SensorMeasurement(
                sensor_id="radar_1",
                sensor_type=SensorType.RADAR,
                timestamp=datetime.now(),
                data={"lat": 31.2, "lon": 121.5},
                confidence=0.9,
                quality_score=0.8
            ),
            SensorMeasurement(
                sensor_id="ais_1",
                sensor_type=SensorType.AIS,
                timestamp=datetime.now(),
                data={"lat": 31.2, "lon": 121.5},
                confidence=0.95,
                quality_score=0.9
            )
        ]
        
        track.update_confidence(measurements)
        self.assertGreater(track.confidence, 0.0)
        self.assertIn("radar_1", track.source_sensors)
        self.assertIn("ais_1", track.source_sensors)


class TestAttentionWeights(unittest.TestCase):
    """注意力权重测试"""
    
    def test_sensor_weight_calculation(self):
        """传感器权重计算"""
        measurements = [
            SensorMeasurement(
                sensor_id="radar_1",
                sensor_type=SensorType.RADAR,
                timestamp=datetime.now(),
                data={"lat": 31.2, "lon": 121.5},
                confidence=0.9,
                quality_score=0.8
            ),
            SensorMeasurement(
                sensor_id="camera_1",
                sensor_type=SensorType.CAMERA,
                timestamp=datetime.now(),
                data={"lat": 31.2, "lon": 121.5},
                confidence=0.85,
                quality_score=0.7
            )
        ]
        
        weights = AttentionWeights.calculate_sensor_weights(
            measurements,
            context={'target_distance_km': 1.0, 'weather': 'clear'}
        )
        
        self.assertIn("radar_1", weights)
        self.assertIn("camera_1", weights)
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=5)
    
    def test_environment_factor_rain(self):
        """雨天环境因子"""
        # 相机在雨天性能下降
        camera_factor = AttentionWeights._get_environment_factor(
            SensorType.CAMERA, 'rain'
        )
        self.assertLess(camera_factor, 1.0)
        
        # AIS 在雨天不受影响
        ais_factor = AttentionWeights._get_environment_factor(
            SensorType.AIS, 'rain'
        )
        self.assertEqual(ais_factor, 1.0)


class TestKalmanFilter2D(unittest.TestCase):
    """2D 卡尔曼滤波器测试"""
    
    def test_filter_initialization(self):
        """滤波器初始化"""
        kf = KalmanFilter2D(dt=1.0)
        self.assertEqual(kf.x.shape, (4,))
        self.assertEqual(kf.P.shape, (4, 4))
    
    def test_predict_update_cycle(self):
        """预测 - 更新循环"""
        kf = KalmanFilter2D(dt=1.0)
        
        # 初始测量
        z = np.array([31.2, 121.5])
        state, covariance = kf.update(z)
        
        self.assertEqual(state.shape, (4,))
        self.assertEqual(covariance.shape, (4, 4))
        
        # 验证状态已更新（非零）
        self.assertNotEqual(state[0], 0.0)
        self.assertNotEqual(state[1], 0.0)
        
        # 第二次测量
        z2 = np.array([31.21, 121.51])
        state2, covariance2 = kf.update(z2)
        
        # 验证状态持续更新
        self.assertEqual(state2.shape, (4,))
        self.assertEqual(covariance2.shape, (4, 4))


class TestFeatureFusionLayer(unittest.TestCase):
    """特征融合层测试"""
    
    def test_layer_initialization(self):
        """融合层初始化"""
        layer = FeatureFusionLayer()
        self.assertEqual(len(layer.measurement_buffer), 0)
        self.assertIsNone(layer.fusion_state)
    
    def test_add_measurement(self):
        """添加测量"""
        layer = FeatureFusionLayer()
        
        m = SensorMeasurement(
            sensor_id="radar_1",
            sensor_type=SensorType.RADAR,
            timestamp=datetime.now(),
            data={"lat": 31.2, "lon": 121.5},
            confidence=0.9,
            quality_score=0.85
        )
        
        layer.add_measurement(m)
        self.assertEqual(len(layer.measurement_buffer), 1)
    
    def test_add_invalid_measurement(self):
        """添加无效测量（应被拒绝）"""
        layer = FeatureFusionLayer()
        
        m = SensorMeasurement(
            sensor_id="camera_1",
            sensor_type=SensorType.CAMERA,
            timestamp=datetime.now(),
            data={"lat": 31.2, "lon": 121.5},
            confidence=0.3,  # 低置信度
            quality_score=0.4  # 低质量
        )
        
        layer.add_measurement(m)
        self.assertEqual(len(layer.measurement_buffer), 0)
    
    def test_process_frame(self):
        """处理帧"""
        layer = FeatureFusionLayer()
        
        measurements = [
            SensorMeasurement(
                sensor_id="radar_1",
                sensor_type=SensorType.RADAR,
                timestamp=datetime.now(),
                data={"lat": 31.2, "lon": 121.5},
                confidence=0.9,
                quality_score=0.85
            ),
            SensorMeasurement(
                sensor_id="ais_1",
                sensor_type=SensorType.AIS,
                timestamp=datetime.now(),
                data={"lat": 31.21, "lon": 121.51},
                confidence=0.95,
                quality_score=0.9
            )
        ]
        
        state = layer.process_frame(measurements)
        
        self.assertIsInstance(state, FusionState)
        self.assertGreater(len(state.active_tracks), 0)
        self.assertGreater(state.fusion_quality, 0.0)
        self.assertGreater(state.processing_latency_ms, 0.0)
    
    def test_sensor_health_tracking(self):
        """传感器健康追踪"""
        layer = FeatureFusionLayer()
        
        measurements = [
            SensorMeasurement(
                sensor_id="radar_1",
                sensor_type=SensorType.RADAR,
                timestamp=datetime.now(),
                data={"lat": 31.2, "lon": 121.5},
                confidence=0.9,
                quality_score=0.85
            ),
            SensorMeasurement(
                sensor_id="radar_1",
                sensor_type=SensorType.RADAR,
                timestamp=datetime.now(),
                data={"lat": 31.21, "lon": 121.51},
                confidence=0.88,
                quality_score=0.82
            )
        ]
        
        state = layer.process_frame(measurements)
        
        self.assertIn("radar_1", state.sensor_health)
        self.assertGreater(state.sensor_health["radar_1"], 0.8)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_multi_sensor_fusion(self):
        """多传感器融合"""
        layer = FeatureFusionLayer()
        
        # 模拟多传感器输入
        measurements = []
        for i in range(5):
            measurements.append(SensorMeasurement(
                sensor_id=f"radar_{i}",
                sensor_type=SensorType.RADAR,
                timestamp=datetime.now(),
                data={"lat": 31.2 + i * 0.001, "lon": 121.5 + i * 0.001},
                confidence=0.85 + i * 0.02,
                quality_score=0.8 + i * 0.03
            ))
        
        for i in range(3):
            measurements.append(SensorMeasurement(
                sensor_id=f"ais_{i}",
                sensor_type=SensorType.AIS,
                timestamp=datetime.now(),
                data={"lat": 31.2 + i * 0.002, "lon": 121.5 + i * 0.002},
                confidence=0.9 + i * 0.02,
                quality_score=0.9 + i * 0.02
            ))
        
        # 处理多帧
        for frame in range(3):
            state = layer.process_frame(measurements)
            self.assertIsInstance(state, FusionState)
        
        # 验证融合结果
        final_state = layer.get_state()
        self.assertIsNotNone(final_state)
        self.assertGreater(len(final_state.active_tracks), 0)
        self.assertGreater(final_state.fusion_quality, 0.0)


if __name__ == '__main__':
    unittest.main()
