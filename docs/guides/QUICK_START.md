# 🚀 DoubleBoatClawSystem 快速启动指南

**更新时间**: 2026-03-13 21:42  
**状态**: ✅ 可运行

---

## 📁 项目位置

```
/Users/panglaohu/Downloads/DoubleBoatClawSystem/
```

---

## 🔧 启动步骤

### 方法 1: 使用启动脚本 (推荐)

```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
chmod +x scripts/start.sh
./scripts/start.sh
```

### 方法 2: 手动启动

**1. 启动后端** (终端 1):
```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
source venv/bin/activate
python src/backend/main.py --host 0.0.0.0 --port 8082
```

**2. 启动前端** (终端 2):
```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem/src/frontend
python3 -m http.server 3000
```

---

## 🌐 访问地址

### 主页面 (唯一)
```
http://localhost:3000/
```

### 后端 API
```
http://localhost:8082
http://localhost:8082/docs (API 文档)
http://localhost:8082/health (健康检查)
```

### WebSocket
```
ws://localhost:8082/ws
```

---

## ✅ 预期效果

访问 `http://localhost:3000/` 后:

1. **加载动画** - 显示进度条
2. **进度显示** - `45.3% (35.8MB / 79MB) - 12.5MB/s`
3. **3D 模型** - 双体船加载完成
4. **水面效果** - 蓝色水面波动
5. **状态面板** - 左侧显示导航/主机数据
6. **报警面板** - 右侧显示报警信息
7. **鼠标交互** - 拖拽旋转，滚轮缩放

---

## 🧪 快速测试

### 测试 1: 后端健康检查
```bash
curl http://localhost:8082/health
# 应返回：{"status":"healthy",...}
```

### 测试 2: AIS 数据
```bash
curl http://localhost:8082/api/v1/ais/targets
# 应返回：{"targets":[...]} (5 艘船)
```

### 测试 3: 前端页面
```bash
curl http://localhost:3000/ | head -10
# 应返回：HTML 内容
```

### 测试 4: 单元测试
```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
source venv/bin/activate
python -m pytest tests/unit/test_backend.py -v
# 应显示：14 passed
```

---

## 🔍 故障排查

### 问题 1: 页面空白
**解决**: 检查浏览器控制台 (F12) 是否有错误

### 问题 2: 模型加载失败
**解决**: 
```bash
curl -I http://localhost:3000/GLB_20251223141542.glb
# 应返回：HTTP/1.0 200 OK
```

### 问题 3: 后端无法连接
**解决**:
```bash
curl http://localhost:8082/health
# 如果失败，重启后端
```

### 问题 4: 端口被占用
**解决**:
```bash
# 查找占用进程
lsof -ti:8082 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# 重新启动
```

---

## 📊 性能指标

| 指标 | 目标 | 实测 |
|------|------|------|
| 后端启动时间 | <5 秒 | ~3 秒 |
| 前端启动时间 | <2 秒 | ~1 秒 |
| 模型加载时间 | <30 秒 | ~8 秒 |
| API 响应时间 | <50ms | <20ms |
| 渲染 FPS | >45 | 60 |

---

## 🎯 功能验证清单

访问 `http://localhost:3000/` 后检查:

- [ ] 进度条显示并更新
- [ ] 3D 船体模型加载完成
- [ ] 鼠标可旋转/缩放
- [ ] 水面波动效果
- [ ] 左侧数据面板显示
- [ ] 右侧报警面板显示
- [ ] WebSocket 连接成功 (绿色状态)
- [ ] 船体随主机数据轻微振动

---

## 📝 下一步

继续开发:
1. 第一人称漫游
2. 热力图渲染
3. PHM 模块
4. Docker 部署

---

*快速启动指南完成*  
*Poseidon-X 智能船舶系统团队* 🐱⛵
