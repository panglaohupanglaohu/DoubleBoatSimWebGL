# 🌍 WorldMonitor 集成方案

**集成时间**: 2026-03-14 12:30  
**开源项目**: https://github.com/koala73/worldmonitor  
**应用场景**: 导航及监控模块

---

## 📊 WorldMonitor 项目概览

### 核心功能
- **实时全球情报仪表板**
- **435+ 策划新闻源** (AI 综合摘要)
- **双地图引擎**: 3D 地球仪 (globe.gl) + WebGL 平面地图 (deck.gl)
- **45 个数据层** (军事、经济、灾害、升级信号)
- **国家情报指数** (12 类信号的综合风险评分)
- **金融雷达** (92 个证券交易所、大宗商品、加密货币)
- **本地 AI** (Ollama，无需 API Key)
- **21 种语言支持**

### 技术栈
| 类别 | 技术 |
|------|------|
| **前端** | Vanilla TypeScript, Vite, globe.gl + Three.js, deck.gl + MapLibre GL |
| **AI/ML** | Ollama / Groq / OpenRouter, Transformers.js |
| **地图** | globe.gl (3D), deck.gl (WebGL), MapLibre GL |
| **部署** | Vercel, Docker, PWA |

---

## 🎯 集成目标

将 WorldMonitor 的 **导航监控** 和 **态势感知** 功能集成到 DoubleBoatClawSystem：

### 1. 导航监控
- [ ] 实时 AIS 目标追踪
- [ ] 海洋气象数据
- [ ] 航线优化建议
- [ ] 碰撞风险预警

### 2. 态势感知
- [ ] 周边海域态势
- [ ] 港口状态监控
- [ ] 航道拥堵情况
- [ ] 海上安全预警

### 3. 数据可视化
- [ ] 3D 地球仪视图 (globe.gl)
- [ ] 2D 海图视图 (deck.gl + MapLibre)
- [ ] 多层数据叠加
- [ ] 实时数据更新

---

## 🔧 集成方案

### 方案 A: 前端组件复用 (推荐)

**优势**:
- ✅ 直接使用成熟的地图引擎
- ✅ 丰富的数据层支持
- ✅ 美观的 UI 设计
- ✅ 无需重复开发

**实现步骤**:

1. **安装依赖**
```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem/src/frontend
npm install globe.gl deck.gl maplibre-gl three
```

2. **创建导航监控组件**
```javascript
// src/frontend/digital-twin/NavigationMonitor.js
import Globe from 'globe.gl';

export class NavigationMonitor {
  constructor(containerId, config = {}) {
    this.container = document.getElementById(containerId);
    this.globe = Globe()
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
      .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
      .showAtmosphere(config.showAtmosphere ?? true)
      .labelsData(config.labelsData ?? [])
      .labelLabel(d => d.name)
      .labelColor(d => d.color ?? 'rgba(255,165,0,0.75)')
      .labelResolution(2)
      .labelSize(d => d.size ?? 1.5)
      .arcsData(config.arcsData ?? [])
      .arcColor(d => d.color ?? 'rgba(255, 200, 0, 0.4)')
      .arcDashLength(d => d.dashLength ?? 0.6)
      .arcDashGap(d => d.dashGap ?? 0.2)
      .arcDashInitialGap(d => d.initialGap ?? 0)
      .arcDashAnimateTime(d => d.animateTime ?? 2000);
    
    this.globe(this.container);
  }
  
  // 添加 AIS 目标
  addAISTarget(target) {
    // target: { lat, lng, name, color, size }
    const currentLabels = this.globe.labelsData();
    this.globe.labelsData([...currentLabels, target]);
  }
  
  // 更新本船位置
  updateOwnShip(lat, lng, heading) {
    this.globe.pointOfView({ lat, lng, altitude: 1.5 }, 1000);
  }
}
```

3. **集成到数字孪生页面**
```html
<!-- digital-twin.html -->
<div id="navigation-monitor"></div>
<script type="module">
  import { NavigationMonitor } from './digital-twin/NavigationMonitor.js';
  
  const navMonitor = new NavigationMonitor('navigation-monitor', {
    showAtmosphere: true,
    labelsData: [],
    arcsData: []
  });
  
  // 从后端获取 AIS 数据
  fetch('/api/v1/ais/targets')
    .then(r => r.json())
    .then(data => {
      data.targets.forEach(target => {
        navMonitor.addAISTarget({
          lat: target.latitude,
          lng: target.longitude,
          name: `MMSI ${target.mmsi}`,
          color: 'rgba(255, 0, 0, 0.8)',
          size: 1.0
        });
      });
    });
</script>
```

---

### 方案 B: 数据源集成

**优势**:
- ✅ 复用 WorldMonitor 的数据源
- ✅ 获取全球情报数据
- ✅ AI 摘要功能

**实现步骤**:

1. **配置数据源**
```javascript
// src/frontend/digital-twin/dataSources.js
export const DATA_SOURCES = {
  // AIS 数据
  ais: {
    url: 'https://api.worldmonitor.app/api/v1/ais',
    refreshInterval: 5000
  },
  
  // 海洋气象
  marineWeather: {
    url: 'https://api.worldmonitor.app/api/v1/marine-weather',
    refreshInterval: 60000
  },
  
  // 港口状态
  ports: {
    url: 'https://api.worldmonitor.app/api/v1/ports',
    refreshInterval: 300000
  },
  
  // 航道拥堵
  shippingRoutes: {
    url: 'https://api.worldmonitor.app/api/v1/shipping-routes',
    refreshInterval: 60000
  }
};
```

2. **创建数据聚合器**
```javascript
// src/frontend/digital-twin/DataAggregator.js
export class DataAggregator {
  constructor() {
    this.cache = new Map();
    this.subscribers = new Map();
  }
  
  async fetchData(source) {
    const cached = this.cache.get(source);
    if (cached && Date.now() - cached.timestamp < 60000) {
      return cached.data;
    }
    
    const response = await fetch(source.url);
    const data = await response.json();
    
    this.cache.set(source, {
      data,
      timestamp: Date.now()
    });
    
    this.notifySubscribers(source, data);
    return data;
  }
  
  subscribe(source, callback) {
    if (!this.subscribers.has(source)) {
      this.subscribers.set(source, []);
      this.startPolling(source);
    }
    this.subscribers.get(source).push(callback);
  }
  
  notifySubscribers(source, data) {
    const callbacks = this.subscribers.get(source) || [];
    callbacks.forEach(cb => cb(data));
  }
  
  startPolling(source) {
    setInterval(() => {
      this.fetchData(source);
    }, source.refreshInterval);
  }
}
```

---

### 方案 C: 后端服务集成

**优势**:
- ✅ 统一数据源管理
- ✅ 数据缓存和预处理
- ✅ 减少前端请求

**实现步骤**:

1. **创建 WorldMonitor 适配器**
```python
# src/backend/adapters/worldmonitor_adapter.py
import aiohttp
from datetime import datetime

class WorldMonitorAdapter:
    """WorldMonitor 数据适配器"""
    
    def __init__(self):
        self.base_url = "https://api.worldmonitor.app/api/v1"
        self.cache = {}
        self.cache_ttl = 60  # 秒
    
    async def get_ais_targets(self, lat_range=None, lng_range=None):
        """获取 AIS 目标"""
        cache_key = f"ais_{lat_range}_{lng_range}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        async with aiohttp.ClientSession() as session:
            params = {}
            if lat_range:
                params['lat_min'], params['lat_max'] = lat_range
            if lng_range:
                params['lng_min'], params['lng_max'] = lng_range
            
            async with session.get(f"{self.base_url}/ais", params=params) as resp:
                data = await resp.json()
                self.cache[cache_key] = data
                return data
    
    async def get_marine_weather(self, lat, lng):
        """获取海洋气象数据"""
        cache_key = f"weather_{lat}_{lng}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        async with aiohttp.ClientSession() as session:
            params = {'lat': lat, 'lng': lng}
            async with session.get(f"{self.base_url}/marine-weather", params=params) as resp:
                data = await resp.json()
                self.cache[cache_key] = data
                return data
    
    def _is_cache_valid(self, key):
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return (datetime.now().timestamp() - timestamp) < self.cache_ttl
```

2. **添加 API 端点**
```python
# src/backend/main.py
from .adapters.worldmonitor_adapter import WorldMonitorAdapter

worldmonitor = WorldMonitorAdapter()

@app.get("/api/v1/worldmonitor/ais")
async def get_worldmonitor_ais():
    """获取 WorldMonitor AIS 数据"""
    data = await worldmonitor.get_ais_targets()
    return {"targets": data}

@app.get("/api/v1/worldmonitor/weather")
async def get_worldmonitor_weather(lat: float, lng: float):
    """获取 WorldMonitor 海洋气象数据"""
    data = await worldmonitor.get_marine_weather(lat, lng)
    return data
```

---

## 📋 任务分配 (marine_engineer_agent)

### 任务 1: 前端组件集成 (优先级：高)

**预计完成**: 14:00

**需要编写的文件**:
- [ ] `src/frontend/digital-twin/NavigationMonitor.js` - 导航监控组件
- [ ] `src/frontend/digital-twin/DataAggregator.js` - 数据聚合器
- [ ] `src/frontend/digital-twin.html` - 集成导航监控 (更新)

**依赖安装**:
```bash
npm install globe.gl deck.gl maplibre-gl three
```

---

### 任务 2: 后端适配器 (优先级：中)

**预计完成**: 14:30

**需要编写的文件**:
- [ ] `src/backend/adapters/worldmonitor_adapter.py` - WorldMonitor 适配器
- [ ] `src/backend/main.py` - API 端点 (更新)

---

### 任务 3: 数据源配置 (优先级：低)

**预计完成**: 15:00

**需要编写的文件**:
- [ ] `src/frontend/digital-twin/dataSources.js` - 数据源配置
- [ ] `config/worldmonitor_config.json` - 配置文件

---

## ✅ 验收标准

### 功能要求
- [ ] 3D 地球仪视图正常显示
- [ ] AIS 目标实时追踪
- [ ] 本船位置显示
- [ ] 海洋气象数据展示
- [ ] 数据更新延迟 <5 秒

### 性能要求
- [ ] 地图加载时间 <2 秒
- [ ] 目标渲染帧率 >30fps
- [ ] API 响应时间 <1 秒

### 测试要求
- [ ] 集成测试通过
- [ ] 性能测试达标
- [ ] 无内存泄漏

---

## 📊 集成架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                            │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Digital Twin │  │ Navigation   │                    │
│  │ (3D 模型)     │  │ Monitor      │                    │
│  │              │  │ (globe.gl)   │                    │
│  └──────────────┘  └──────────────┘                    │
├─────────────────────────────────────────────────────────┤
│                    数据聚合层                            │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Data         │  │ WorldMonitor │                    │
│  │ Aggregator   │  │ Adapter      │                    │
│  └──────────────┘  └──────────────┘                    │
├─────────────────────────────────────────────────────────┤
│                    外部数据源                            │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ WorldMonitor │  │ 本地传感器   │                    │
│  │ API          │  │ 数据         │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 参考资料

- **WorldMonitor 文档**: https://docs.worldmonitor.app
- **globe.gl 文档**: https://globe.gl
- **deck.gl 文档**: https://deck.gl
- **MapLibre GL 文档**: https://maplibre.org

---

**分配者**: CaptainCatamaran 🐱⛵  
**执行者**: marine_engineer_agent  
**时间**: 12:30
