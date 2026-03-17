# 🧪 自动化测试报告

**生成时间**: 2026-03-17 08:01:44

## 📊 测试概览

| 指标 | 数值 |
|------|------|
| 测试总数 | 13 |
| 通过 | 9 ✅ |
| 失败 | 4 ❌ |
| 通过率 | 69.2% |

## 📋 详细结果

### ✅ Channels API 可访问

### ✅ Channels 响应格式

### ✅ EnergyEfficiencyChannel 已注册

### ✅ IntelligentNavigationChannel 已注册

### ✅ 所有 Channel 健康

### ✅ Sensors API 可访问

### ✅ Sensors 响应格式

### ✅ 传感器数量 >= 4 (实际：4)

### ❌ 数字孪生页面可访问

```
HTTPConnectionPool(host='localhost', port=5173): Max retries exceeded with url: /digital-twin.html (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5173): Failed to establish a new connection: [Errno 61] Connection refused"))
```

### ❌ LLM 配置页面可访问

```
HTTPConnectionPool(host='localhost', port=5173): Max retries exceeded with url: /poseidon-config.html (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5173): Failed to establish a new connection: [Errno 61] Connection refused"))
```

### ❌ Bridge Chat 组件存在

```
HTTPConnectionPool(host='localhost', port=5173): Max retries exceeded with url: /digital-twin.html (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5173): Failed to establish a new connection: [Errno 61] Connection refused"))
```

### ✅ API 响应时间 < 1s (实际：0.005s)

### ❌ 前端响应时间 < 2s

```
HTTPConnectionPool(host='localhost', port=5173): Max retries exceeded with url: /digital-twin.html (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5173): Failed to establish a new connection: [Errno 61] Connection refused"))
```

