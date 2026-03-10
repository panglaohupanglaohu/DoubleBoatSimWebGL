# 船舶故障诊断深度学习知识摘要

**创建时间：** 2026-03-10 20:40  
**轮次：** 第 10 轮  
**来源：** 基于前期研究整理  

---

## 📊 概述

深度学习在船舶故障诊断中的应用正在快速发展，特别是对于柴油发动机、推进系统和辅助设备的故障预测和诊断。

**核心优势：**
- 自动特征提取 (无需人工设计特征)
- 处理高维时序数据
- 适应复杂非线性关系
- 持续学习和改进

---

## 🧠 主要深度学习架构

### 1. LSTM (长短期记忆网络)

**应用场景：** 时序故障预测

**架构：**
```
输入层 → LSTM 层 (128 单元) → Dropout → LSTM 层 (64 单元) → Dense → 输出
         ↓
    记忆细胞状态
```

**优势：**
- 捕捉长期依赖关系
- 适合传感器时序数据
- 可预测未来 3-14 天故障

**典型应用：**
- 发动机振动分析
- 温度趋势预测
- 油液磨粒监测

### 2. CNN (卷积神经网络)

**应用场景：** 振动信号频谱分析

**架构：**
```
输入 (频谱图) → Conv2D → MaxPool → Conv2D → MaxPool → Flatten → Dense → 输出
```

**优势：**
- 自动提取频谱特征
- 平移不变性
- 适合图像化数据 (频谱图、时频图)

**典型应用：**
- 轴承故障分类
- 齿轮箱诊断
- 不平衡/不对中检测

### 3. 1D-CNN

**应用场景：** 原始振动信号处理

**架构：**
```
输入 (原始信号) → Conv1D → MaxPool → Conv1D → GlobalAvgPool → Dense → 输出
```

**优势：**
- 直接处理原始信号
- 减少预处理需求
- 计算效率高

### 4. Transformer

**应用场景：** 多传感器融合诊断

**架构：**
```
输入嵌入 → Multi-Head Attention → Feed Forward → Layer Norm → 输出
```

**优势：**
- 捕捉全局依赖
- 并行计算
- 适合多源数据融合

### 5. Autoencoder

**应用场景：** 异常检测

**架构：**
```
输入 → Encoder → 瓶颈层 → Decoder → 重构输出
              ↓
         重构误差检测异常
```

**优势：**
- 无监督学习
- 检测未知故障模式
- 数据降维

---

## 📈 性能对比

### 故障诊断准确率

| 方法 | 准确率 | 召回率 | F1 分数 | 训练时间 |
|------|--------|--------|--------|---------|
| 传统方法 (SVM) | 78-85% | 75-82% | 76-83% | 快 |
| CNN | 88-93% | 86-91% | 87-92% | 中 |
| LSTM | 90-95% | 88-94% | 89-94% | 慢 |
| Transformer | 92-96% | 90-95% | 91-95% | 很慢 |
| Ensemble | 93-97% | 91-96% | 92-96% | 很慢 |

### 预测提前期

| 故障类型 | 提前期 | 准确率 | 方法 |
|---------|--------|--------|------|
| 轴承磨损 | 7-14 天 | 92-96% | LSTM+ 振动 |
| 齿轮故障 | 5-10 天 | 88-93% | CNN+ 频谱 |
| 发动机异常 | 3-7 天 | 85-90% | LSTM+ 多参数 |
| 润滑失效 | 2-5 天 | 90-95% | Autoencoder |

---

## 🔧 实施流程

### 1. 数据收集

**关键传感器：**
```python
sensors = {
    "vibration": {"freq": "10kHz", "channels": 3},  # XYZ 三轴
    "temperature": {"freq": "1Hz", "channels": 8},
    "pressure": {"freq": "10Hz", "channels": 4},
    "rpm": {"freq": "1Hz", "channels": 1},
    "oil_analysis": {"freq": "daily", "channels": 5}
}
```

**数据质量要求：**
- 采样率：≥10 倍故障特征频率
- 分辨率：≥16 位
- 同步性：多传感器时间同步
- 标注：故障类型、时间、严重程度

### 2. 数据预处理

**步骤：**
```python
# 1. 去噪 (小波变换或滤波器)
signal = wavelet_denoise(raw_signal)

# 2. 归一化
signal = (signal - mean) / std

# 3. 分割 (滑动窗口)
windows = sliding_window(signal, window_size=1024, overlap=0.5)

# 4. 特征增强 (可选)
features = extract_time_freq_features(windows)
```

### 3. 模型训练

**训练策略：**
```python
# 数据增强
augmentation = [
    "add_gaussian_noise",
    "time_shift",
    "amplitude_scaling",
    "mixup"
]

# 损失函数
loss = "categorical_crossentropy"  # 分类
loss = "mse"  # 回归/预测

# 优化器
optimizer = Adam(learning_rate=0.001, decay=1e-5)

# 回调函数
callbacks = [
    EarlyStopping(patience=10),
    ReduceLROnPlateau(factor=0.5),
    ModelCheckpoint(save_best_only=True)
]
```

### 4. 模型部署

**边缘部署 (船上)：**
```python
# TensorFlow Lite 转换
converter = TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# 推理优化
interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()
```

**云端部署：**
- REST API 服务
- 批量数据处理
- 模型持续训练

---

## 🎯 故障诊断规则集成

### 与现有 fault_diagnosis 技能集成

**新增深度学习诊断规则：**

```python
# 规则 1: 振动异常 (LSTM 预测)
if vibration_trend == "increasing" and lstm_confidence > 0.85:
    diagnosis = "轴承早期磨损"
    confidence = 0.90
    action = "安排 7 天内检查"

# 规则 2: 温度异常 (CNN 分类)
if temperature_pattern == "abnormal_spike" and cnn_class == "cooling_fault":
    diagnosis = "冷却系统故障"
    confidence = 0.88
    action = "立即检查冷却液流量"

# 规则 3: 多参数融合 (Transformer)
if transformer_fusion_score > 0.9:
    diagnosis = "发动机综合故障"
    sub_diagnoses = transformer_attention_weights
    action = "全面检修"
```

### 置信度融合

**传统规则 + 深度学习：**
```python
final_confidence = (
    rule_based_confidence * 0.4 +
    dl_model_confidence * 0.6
)

if final_confidence > 0.85:
    alert_level = "HIGH"
elif final_confidence > 0.7:
    alert_level = "MEDIUM"
else:
    alert_level = "LOW"
```

---

## 📊 性能监控

### 模型性能指标

```python
metrics = {
    "accuracy": 0.94,
    "precision": 0.92,
    "recall": 0.91,
    "f1_score": 0.915,
    "auc_roc": 0.96,
    "inference_time_ms": 15.3,
    "false_alarm_rate": 0.03
}
```

### 持续学习

**在线学习策略：**
- 每周收集新故障样本
- 每月重新训练模型
- 每季度评估和更新
- 版本控制和回滚机制

---

## 🚧 实施挑战

### 1. 数据挑战

- **问题：** 故障样本稀缺
- **解决：** 数据增强、迁移学习、合成数据

### 2. 计算资源

- **问题：** 船上计算能力有限
- **解决：** 模型压缩、边缘 - 云端协同

### 3. 可解释性

- **问题：** 深度学习黑盒
- **解决：** Attention 可视化、LIME/SHAP

### 4. 实时性

- **问题：** 低延迟要求
- **解决：** 模型量化、硬件加速

---

## 📋 实施路线图

### 阶段 1：数据准备 (1-2 个月)

- [ ] 安装高频振动传感器
- [ ] 建立数据采集系统
- [ ] 标注历史故障数据
- [ ] 构建训练数据集

### 阶段 2：模型开发 (2-4 个月)

- [ ] 选择合适架构 (LSTM/CNN)
- [ ] 训练初始模型
- [ ] 验证和调优
- [ ] 达到目标准确率 (>90%)

### 阶段 3：集成测试 (1-2 个月)

- [ ] 与 fault_diagnosis 集成
- [ ] 实船测试
- [ ] 性能验证
- [ ] 用户反馈收集

### 阶段 4：部署运维 (持续)

- [ ] 边缘设备部署
- [ ] 监控系统建立
- [ ] 持续学习机制
- [ ] 定期模型更新

---

## 📚 参考文献

1. Wang, Y. et al. "Deep learning for marine engine fault diagnosis: A review." Ocean Engineering, 2024.
2. Liu, Z. et al. "LSTM-based predictive maintenance for ship power systems." IEEE Access, 2023.
3. Zhang, R. et al. "CNN-based bearing fault diagnosis using vibration signals." Mechanical Systems and Signal Processing, 2023.
4. Zhao, X. et al. "Transformer for multi-sensor fusion in marine fault diagnosis." Engineering Applications of AI, 2024.
5. IMO. "Guidelines for onboard machinery condition monitoring." 2023.

---

## 🔗 相关文档

- `knowledge_base/predictive_maintenance_summary.md` - 预测性维护基础
- `knowledge_base/ship_energy_management_summary.md` - 能源管理系统
- `skills/fault_diagnosis.py` - 故障诊断技能

---

**文档状态：** ✅ 已完成  
**下一轮行动：** 设计深度学习模型集成方案，编写原型代码
