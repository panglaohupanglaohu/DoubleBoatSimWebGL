# AI Native 16 小时重构计划（已重构版）

**重构时间**: 2026-03-15 10:30  
**目标**: 基于《深海远洋船舶综合信息系统设计蓝图》重新规划 16 小时冲刺，实现 AI Native 架构落地

---

## 1. 新架构核心：专家认知框架 (ECF) 重构

### 1.1 五层认知模型映射到现有代码

| 蓝图层级 | 当前代码映射 | 重构目标 |
|---------|-------------|----------|
| **多模态感知融合层** | `nmea2000_parser.py` + `sensor_aggregator.py` | 改造为特征级融合，加入 YOLO/Swin-Transformer 视觉验证 |
| **船舶大数据湖仓层** | `data_lake.py` (占位) | 真实接入 HDFS + Kudu/Impala 存储 |
| **认知决策与推理层** | `compliance_digital_expert.py` | 内置海事知识图谱，接入 COLREGs 硬约束 |
| **智能执行与姿态控制层** | `intelligent_engine.py` | 增加 DRL 路径规划，主动姿态控制 |
| **AI 驱动交互层** | `digital-twin.html` + `simple-bridge-chat.js` | 增加 AR 叠加，集成 Gemini LLM |

### 1.2 三大核心 Channel 重新定义

#### A) 智能避碰规划 (CAS) Channel
- **原**: 基础 CPA/TCPA 计算
- **重构**: 
  - 特征级融合 (雷达+AIS+视觉)
  - 基于 COLREGs 的贝叶斯 CRI 评判
  - DRL 路径规划
  - 端到端延迟 < 3 秒

#### B) 数字孪生与结构健康 (SHM) Channel  
- **原**: 静态模型展示
- **重构**:
  - 光纤 FBG 传感器接入
  - AI 模拟海况对寿命影响
  - 实时疲劳监测

#### C) 智能机舱视觉 (IER) Channel
- **原**: 规则引擎 + 数值监控
- **重构**:
  - YOLOv5 + Coordinate Attention
  - 机舱复杂环境目标检测
  - 早期故障视觉识别

---

## 2. 重构后冲刺路线图

### Phase 1: 专家认知框架落地 (2 小时)
- [x] `compliance_digital_expert.py` - 海事知识图谱骨架
- [x] `distributed_perception_hub.py` - 感知融合网络
- [x] `decision_orchestrator.py` - 认知决策编排
- [x] 新增 `worldmonitor_adapter_real.py` - 真实数据适配器

### Phase 2: AI Native 感知层增强 (4 小时)
- [ ] `nmea2000_parser.py` → 特征级融合 (Feature Fusion)
- [ ] `sensor_aggregator.py` → AI 增强感知
- [ ] `vision_detector.py` → YOLOv5 机舱视觉
- [ ] `data_lake.py` → 真实湖仓接入

### Phase 3: 认知决策层升级 (4 小时)  
- [ ] `knowledge_graph.py` → COLREGs 硬约束知识图谱
- [ ] `bayesian_cri_evaluator.py` → 贝叶斯 CRI 评判
- [ ] `drl_path_planner.py` → 深度强化学习路径规划
- [ ] `rcs_attitude_controller.py` → 主动姿态控制

### Phase 4: 交互与可视化增强 (4 小时)
- [ ] `digital-twin.html` → AR 叠加层
- [ ] `simple-bridge-chat.js` → Gemini LLM 接入
- [ ] `openbridge_ui.py` → OpenBridge 标准 UI
- [ ] `hmi_layer.py` → 标准化交互层

### Phase 5: 系统集成与测试 (2 小时)
- [ ] 端到端测试
- [ ] 性能基准测试
- [ ] 安全与合规验证
- [ ] 文档与交付

---

## 3. 关键技术栈映射

### AI/ML 模型
- **视觉**: YOLOv5 + Swin Transformer
- **推理**: 贝叶斯网络 + 知识图谱
- **规划**: DRL (Deep Reinforcement Learning)  
- **预测**: LSTM + Transformer

### 存储
- **数据湖**: HDFS
- **数据仓库**: Kudu/Impala
- **时序**: InfluxDB (NMEA 2000)
- **图谱**: Neo4j (COLREGs)

### 前端
- **3D**: Three.js + globe.gl
- **GIS**: deck.gl + MapLibre GL
- **AR**: WebXR (浏览器原生)
- **LLM**: Gemini 接口

---

## 4. 风险与应对

### R1: 视觉模型训练数据不足
- **应对**: 先用合成数据 + 现有图像数据集训练，逐步替换为真实机舱图像

### R2: 知识图谱构建复杂度高  
- **应对**: 先构建 COLREGs 核心规则子图，逐步扩展到完整海事法规图谱

### R3: 实时性能要求严苛
- **应对**: 采用边缘计算 + 云协同架构，核心推理在边缘，复杂分析上云

---

## 5. 验收标准

### 功能验收
- [ ] 视觉检测精度 > 95% (机舱小目标识别)
- [ ] 避碰决策延迟 < 3 秒
- [ ] AR 叠加延迟 < 50ms
- [ ] 知识图谱覆盖率 > 80% (COLREGs)

### 性能验收  
- [ ] API 响应时间 < 100ms
- [ ] 并发用户支持 > 10
- [ ] 数据处理吞吐 > 1000 TPS
- [ ] 系统可用性 > 99.9%

### 合规验收
- [ ] 符合 IEC 61162 (NMEA 2000)
- [ ] 符合 IEC 62288 (ECDIS)
- [ ] 符合 MSC.415 (智能船舶指南)
- [ ] 符合 CCS《智能船舶规范》

---

## 6. 每半小时状态汇报 Cron Job
已设置每 30 分钟自动汇报任务状态。
