# 🔗 前端 - 后端 Channel 打通方案

**创建时间**: 2026-03-14 12:48  
**目标**: 前端模块与后端 Channel 数据流打通

---

## 📊 当前状态

### 后端 Channel (已注册)
| Channel | 状态 | API 端点 | 功能 |
|---------|------|----------|------|
| `energy_efficiency` | ✅ ok | `/api/v1/channels` | EEXI/CII/SEEMP |
| `intelligent_navigation` | ✅ ok | `/api/v1/channels` | CPA/TCPA/避碰 |

### 前端模块
| 模块 | 状态 | 数据源 |
|------|------|--------|
| Bridge Chat | ✅ 已集成 | LLM API |
| 3D 数字孪生 | ✅ 已集成 | WebSocket |
| LLM 配置 | ✅ 已集成 | localStorage |

### 缺失的数据流
- ❌ 前端 → Channel API 调用
- ❌ Channel 数据 → 前端显示
- ❌ Bridge Chat → Channel 查询
- ❌ 实时数据 → Bridge Chat 上下文

---

## 🔧 打通方案

### 方案 1: Bridge Chat 集成 Channel 查询

**文件**: `src/frontend/digital-twin/simple-bridge-chat.js`

**添加 Channel 查询功能**:

```javascript
// 添加 Channel 数据查询方法
async queryChannelData(channelName, query) {
  try {
    const response = await fetch(`http://localhost:8080/api/v1/channels/${channelName}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });
    
    if (!response.ok) {
      throw new Error(`Channel API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Failed to query channel ${channelName}:`, error);
    throw error;
  }
}

// 更新 sendMessage 方法，支持 Channel 查询
async sendMessage() {
  const input = document.getElementById('bridge-input');
  const text = input.value.trim();
  
  if (!text || !this.config.apiKey) return;
  
  this.addMessage('user', text);
  input.value = '';
  
  // 显示思考中
  this.addMessage('assistant', '🤔 正在思考...');
  
  try {
    // 1. 先尝试从 Channel 获取数据
    let channelContext = '';
    
    if (text.includes('碰撞') || text.includes('风险') || text.includes('AIS')) {
      // 查询智能导航 Channel
      const navData = await this.queryChannelData('intelligent_navigation', text);
      channelContext = `\n\n[导航数据]: ${JSON.stringify(navData)}`;
    } else if (text.includes('能效') || text.includes('CII') || text.includes('EEXI')) {
      // 查询能效管理 Channel
      const effData = await this.queryChannelData('energy_efficiency', text);
      channelContext = `\n\n[能效数据]: ${JSON.stringify(effData)}`;
    }
    
    // 2. 调用 LLM (带上 Channel 数据作为上下文)
    const response = await this.callLLM(text + channelContext);
    
    // 3. 移除思考中消息
    const messagesContainer = document.getElementById('bridge-messages');
    messagesContainer.lastChild.remove();
    
    this.addMessage('assistant', response);
  } catch (error) {
    console.error('LLM call failed:', error);
    const messagesContainer = document.getElementById('bridge-messages');
    messagesContainer.lastChild.remove();
    this.addMessage('system', `❌ 调用失败：${error.message}`);
  }
}
```

---

### 方案 2: 后端添加 Channel Query API

**文件**: `src/backend/main.py`

**添加 Channel 查询端点**:

```python
from .channels.intelligent_navigation import IntelligentNavigationChannel
from .channels.energy_efficiency_manager import EnergyEfficiencyChannel
from channels.marine_base import get_default_registry

@app.get("/api/v1/channels")
async def get_channels():
    """获取已注册 Channel 列表"""
    from channels.marine_base import get_default_registry
    registry = get_default_registry()
    
    channels = []
    for name in registry.list_channels():
        channel = registry.get(name)
        if channel:
            status = channel.get_status()
            channels.append({
                "name": name,
                "description": channel.description,
                "version": status.get("version", "1.0.0"),
                "health": status.get("health", "unknown"),
                "initialized": status.get("initialized", False),
                "status": status
            })
    
    return {"channels": channels}

@app.post("/api/v1/channels/{channel_name}/query")
async def query_channel(channel_name: str, query: dict):
    """查询 Channel 数据"""
    registry = get_default_registry()
    channel = registry.get(channel_name)
    
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found")
    
    # 根据 Channel 类型处理查询
    if channel_name == "intelligent_navigation":
        # 智能导航 Channel 查询
        if hasattr(channel, 'query_navigation_status'):
            result = channel.query_navigation_status(query.get("query", ""))
            return {"result": result}
        else:
            return {"result": channel.get_collision_risks()}
    
    elif channel_name == "energy_efficiency":
        # 能效管理 Channel 查询
        return {
            "result": {
                "vessel": channel.vessel.vessel_name if channel.vessel else None,
                "eexi": channel.calculate_eexi(10000, 170).to_dict() if channel.eexi_calculator else None,
                "cii": channel.calculate_cii(15000000, 45000, 2026).to_dict() if channel.cii_calculator else None,
                "recommendations": channel.get_recommendations()
            }
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Channel '{channel_name}' does not support query")
```

---

### 方案 3: 实时更新 Bridge Chat 上下文

**文件**: `src/frontend/digital-twin/simple-bridge-chat.js`

**添加船舶数据更新**:

```javascript
// 添加船舶上下文更新方法
updateShipContext(data) {
  this.shipContext = {
    ...this.shipContext,
    ...data
  };
  
  // 在 LLM 调用时自动带上上下文
  console.log('🚢 Ship context updated:', this.shipContext);
}

// 启动时获取初始数据
async initializeShipContext() {
  try {
    // 获取传感器数据
    const sensorsResponse = await fetch('http://localhost:8080/api/v1/sensors');
    const sensorsData = await sensorsResponse.json();
    
    // 获取 Channel 状态
    const channelsResponse = await fetch('http://localhost:8080/api/v1/channels');
    const channelsData = await channelsResponse.json();
    
    // 更新上下文
    this.updateShipContext({
      sensors: sensorsData.sensors,
      channels: channelsData.channels,
      timestamp: new Date().toISOString()
    });
    
    console.log('✅ Ship context initialized');
  } catch (error) {
    console.error('❌ Failed to initialize ship context:', error);
  }
}

// 在构造函数中调用
constructor() {
  this.config = this.loadConfig();
  this.container = null;
  this.messages = [];
  this.isExpanded = true;
  this.dragState = null;
  this.shipContext = {}; // 添加船舶上下文
  
  this.init();
  this.initializeShipContext(); // 初始化船舶上下文
  
  // 定期更新 (每 5 秒)
  setInterval(() => this.updateShipContextFromAPI(), 5000);
}

// 定期更新船舶上下文
async updateShipContextFromAPI() {
  try {
    const response = await fetch('http://localhost:8080/api/v1/sensors');
    const data = await response.json();
    this.updateShipContext({
      sensors: data.sensors,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Failed to update ship context:', error);
  }
}
```

---

### 方案 4: 添加 Channel 状态显示面板

**文件**: `src/frontend/digital-twin.html`

**在左侧面板添加 Channel 状态**:

```html
<!-- 在左侧数据面板添加 Channel 状态 -->
<div class="data-card">
    <h3>🤖 Channel 状态</h3>
    <div id="channel-status-list">
        <div style="text-align: center; color: #a0a0a0; padding: 10px;">
            加载中...
        </div>
    </div>
</div>

<script>
// 添加 Channel 状态更新函数
async function updateChannelStatus() {
    try {
        const response = await fetch('http://localhost:8080/api/v1/channels');
        const data = await response.json();
        
        const container = document.getElementById('channel-status-list');
        container.innerHTML = data.channels.map(ch => `
            <div style="padding: 8px; margin: 4px 0; background: rgba(${ch.health === 'ok' ? '76,175,80' : '255,167,38'}, 0.2); border-radius: 4px; border-left: 3px solid ${ch.health === 'ok' ? '#4caf50' : '#ffa726'};">
                <div style="font-weight: bold; color: #fff;">${ch.name}</div>
                <div style="font-size: 12px; color: #aaa;">${ch.description}</div>
                <div style="font-size: 11px; color: #888; margin-top: 4px;">
                    状态：${ch.health === 'ok' ? '✅' : '⚠️'} ${ch.health}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to update channel status:', error);
    }
}

// 每 10 秒更新一次
setInterval(updateChannelStatus, 10000);

// 初始加载
updateChannelStatus();
</script>
```

---

## 📋 任务分配 (marine_engineer_agent)

### 任务 1: 后端 Channel Query API (优先级：高)

**预计完成**: 13:30

**需要编写的文件**:
- [ ] `src/backend/main.py` - 添加 `/api/v1/channels/{channel_name}/query` 端点
- [ ] `src/backend/channels/intelligent_navigation.py` - 添加 `query_navigation_status()` 方法
- [ ] `src/backend/channels/energy_efficiency_manager.py` - 添加 `query_efficiency_status()` 方法

**验收标准**:
- API 端点可访问
- 返回正确的 Channel 数据
- 支持自然语言查询

---

### 任务 2: 前端 Bridge Chat 集成 (优先级：高)

**预计完成**: 14:00

**需要编写的文件**:
- [ ] `src/frontend/digital-twin/simple-bridge-chat.js` - 添加 Channel 查询功能
- [ ] `src/frontend/digital-twin.html` - 添加 Channel 状态面板

**验收标准**:
- Bridge Chat 能查询 Channel 数据
- Channel 状态实时显示
- 数据流打通

---

### 任务 3: 实时数据更新 (优先级：中)

**预计完成**: 14:30

**需要编写的文件**:
- [ ] `src/frontend/digital-twin/simple-bridge-chat.js` - 添加船舶上下文更新
- [ ] `src/frontend/digital-twin.html` - 添加 WebSocket 连接 (可选)

**验收标准**:
- 船舶数据每 5 秒更新
- Bridge Chat 上下文包含最新数据
- 无内存泄漏

---

## 📊 数据流架构

```
┌─────────────────┐
│   Bridge Chat   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP POST /query
         ▼
┌─────────────────┐
│  Channel Query  │
│     API         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Channel        │
│  (Intelligent   │
│  Navigation /   │
│  Energy         │
│  Efficiency)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM API        │
│  (with Channel  │
│  Context)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Bridge Chat   │
│   (Response)    │
└─────────────────┘
```

---

## ✅ 验收标准

### 功能要求
- [ ] Bridge Chat 能查询 Channel 数据
- [ ] Channel 状态实时显示
- [ ] 船舶上下文自动更新
- [ ] LLM 回答包含 Channel 数据

### 性能要求
- [ ] API 响应时间 <1s
- [ ] 数据更新延迟 <5s
- [ ] 无内存泄漏

### 测试要求
- [ ] 集成测试通过
- [ ] 手动测试验证
- [ ] 用户场景测试

---

**分配者**: CaptainCatamaran  
**执行者**: marine_engineer_agent  
**时间**: 12:48
