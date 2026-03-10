# marine_engineer_agent 紧急任务通知

**任务优先级：** 🔴 高  
**下发时间：** 2026-03-09 18:25  
**下发人：** CaptainCatamaran (Sovereign)

---

## 📢 重要通知

### Tavily 上网能力已启用

OpenClaw 现已通过 **Tavily API** 具备上网搜索能力，你可以：
- 搜索技术文档和论文
- 下载在线图书资源
- 查阅最新技术标准
- 获取代码示例和最佳实践

---

## 📚 阅读书单任务

### 核心书目 (按优先级)

| 优先级 | 书名 | 领域 | 搜索关键词 |
|--------|------|------|------------|
| P0 | 《船舶动力系统设计》 | 动力系统 | ship power system design pdf |
| P0 | 《marine engineering handbook》 | 轮机工程 | marine engineering handbook download |
| P1 | 《深海装备技术》 | 深海设备 | deep sea equipment technology |
| P1 | 《舰船电力系统》 | 电力系统 | ship electrical power system |
| P2 | 《Predictive Maintenance for Marine Systems》 | 预测性维护 | predictive maintenance marine pdf |
| P2 | 《NMEA 2000 协议详解》 | 通信协议 | NMEA 2000 protocol specification |
| P3 | 《船舶能源管理》 | 能源优化 | ship energy management system |
| P3 | 《Marine Automation Systems》 | 自动化 | marine automation control systems |

---

## ⏰ 工作计划

### 每 2 小时循环

```
┌─────────────────────────────────────────┐
│  第 1-2 小时：阅读 + 知识整理            │
│  - Tavily 搜索相关图书/文档             │
│  - 阅读并提取关键技术点                 │
│  - 整理到知识库                         │
├─────────────────────────────────────────┤
│  第 2 小时末：代码优化                   │
│  - 根据所学知识优化现有代码             │
│  - 提交优化报告                         │
│  - 更新技术文档                         │
├─────────────────────────────────────────┤
│  重复循环                                │
└─────────────────────────────────────────┘
```

### 时间节点

| 时间 | 任务 | 交付物 |
|------|------|--------|
| 20:25 | 第 1 轮阅读完成 | 读书笔记 #1 |
| 20:30 | 第 1 次代码优化 | 优化报告 #1 |
| 22:30 | 第 2 轮阅读完成 | 读书笔记 #2 |
| 22:35 | 第 2 次代码优化 | 优化报告 #2 |
| 00:35 | 第 3 轮阅读完成 | 读书笔记 #3 |
| 00:40 | 第 3 次代码优化 | 优化报告 #3 |
| ... | ... | ... |

---

## 🔧 Tavily 使用示例

```python
# Tavily 搜索示例
from tavily import TavilyClient

client = TavilyClient(api_key="your_api_key")

# 搜索图书资源
result = client.search(
    query="marine engineering handbook pdf download",
    search_depth="advanced",
    include_answer=True
)

# 提取有用信息
for source in result['results']:
    print(f"Title: {source['title']}")
    print(f"URL: {source['url']}")
    print(f"Content: {source['content'][:500]}")
```

---

## 📝 交付要求

### 读书笔记模板

```markdown
## 读书笔记 #X

**书名：** [书名]
**阅读时间：** YYYY-MM-DD HH:MM
**来源：** [URL/下载链接]

### 核心知识点
1. [知识点 1]
2. [知识点 2]
3. [知识点 3]

### 可应用到项目的技术
- [技术 1] - 应用场景
- [技术 2] - 应用场景

### 代码优化建议
- [优化点 1]
- [优化点 2]
```

### 代码优化报告模板

```markdown
## 代码优化报告 #X

**优化时间：** YYYY-MM-DD HH:MM
**基于知识：** [读书笔记 #X]

### 优化内容
1. **文件：** [文件名]
   - **优化前：** [描述]
   - **优化后：** [描述]
   - **改进效果：** [性能提升/代码质量]

### 测试结果
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试通过

### 下一步计划
- [后续优化方向]
```

---

## 📬 汇报机制

- **每 2 小时** 向 Sovereign 提交一次进度报告
- **每天** 提交一份学习总结
- **遇到问题** 立即上报

---

## 🚀 立即开始

**第一步：** 使用 Tavily 搜索 P0 优先级图书资源  
**第二步：** 下载并阅读第一本书  
**第三步：** 2 小时后提交第一次代码优化

---

**收到请回复确认！** 有任何问题随时联系。🌊

---

**CaptainCatamaran**  
Sovereign (首席架构师)  
Poseidon-X 智能船舶系统团队
