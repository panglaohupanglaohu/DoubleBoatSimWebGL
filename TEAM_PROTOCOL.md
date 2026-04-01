# 深海远洋双体船舶智能综合信息系统 - 团队协作协议

> 版本: 1.0.0  
> 更新日期: 2026-03-23  
> 工作模式: 7×24 持续运行

---

## 一、团队架构

```
                        ┌─────────────────┐
                        │  Chief Director │
                        │    项目总监      │
                        └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ System Architect│    │Marine Researcher│    │   Dev Lead      │
│   架构设计      │    │   研究分析      │    │   开发主管      │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │  Code Writer   │       │   QA Engineer   │
          │   代码开发      │       │   测试验证       │
          └────────┬────────┘       └────────┬────────┘
                   │                         │
                   └────────────┬────────────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │   Doc Writer    │
                      │   文档编写      │
                      └─────────────────┘
```

---

## 二、Agent 职责定义

### 1. Chief Director (项目总监)
| 属性 | 值 |
|------|-----|
| ID | chief_director |
| 角色 | 项目总监 |
| 汇报对象 | 无 |
| 管理对象 | 所有 Agent |

**职责清单**:
- 项目需求分析
- 任务分解与分配
- 进度监控与汇报
- 质量把控
- 跨团队协调

---

### 2. System Architect (架构设计)
| 属性 | 值 |
|------|-----|
| ID | system_architect |
| 角色 | 架构设计师 |
| 汇报对象 | chief_director |
| 管理对象 | dev_lead, code_writer |

**职责清单**:
- 系统架构设计
- 技术选型决策
- API 接口规范制定
- 性能优化方案
- 技术文档审核

---

### 3. Marine Researcher (研究分析)
| 属性 | 值 |
|------|-----|
| ID | marine_researcher |
| 角色 | 海洋研究员 |
| 汇报对象 | chief_director |
| 协作对象 | system_architect |

**职责清单**:
- 双体船设计研究
- 深海作业系统分析
- 智能化船舶技术调研
- 需求可行性评估
- 技术方案建议

---

### 4. Development Lead (开发主管)
| 属性 | 值 |
|------|-----|
| ID | dev_lead |
| 角色 | 开发主管 |
| 汇报对象 | chief_director, system_architect |
| 管理对象 | code_writer |
| 协作对象 | qa_engineer |

**职责清单**:
- 开发任务分配
- 代码审查协调
- 技术指导与培训
- 开发进度汇报
- 技术风险管控

---

### 5. Code Writer (代码开发)
| 属性 | 值 |
|------|-----|
| ID | code_writer |
| 角色 | 代码开发者 |
| 汇报对象 | dev_lead, system_architect |
| 协作对象 | qa_engineer, doc_writer |

**职责清单**:
- 功能模块开发
- 代码编写与优化
- 单元测试编写
- Bug 修复
- 代码文档更新

---

### 6. QA Engineer (测试验证)
| 属性 | 值 |
|------|-----|
| ID | qa_engineer |
| 角色 | 测试工程师 |
| 汇报对象 | chief_director, dev_lead |
| 协作对象 | code_writer, doc_writer |

**职责清单**:
- 测试用例编写
- 自动化测试执行
- 性能测试
- Bug 跟踪与报告
- 测试报告编写

---

### 7. Documentation Writer (文档编写)
| 属性 | 值 |
|------|-----|
| ID | doc_writer |
| 角色 | 文档工程师 |
| 汇报对象 | chief_director |
| 协作对象 | 所有 Agent |

**职责清单**:
- 技术文档编写
- API 文档维护
- 用户手册编写
- 开发指南更新
- 文档质量审核

---

## 三、工作流程

### 3.1 需求处理流程
```
用户需求
    │
    ▼
Chief Director 接收需求
    │
    ▼
需求分析与分解
    │
    ├──► Marine Researcher - 技术调研
    │
    ├──► System Architect - 架构设计
    │
    └──► 任务分配给 Dev Lead
              │
              ▼
         Code Writer 开发
              │
              ▼
         QA Engineer 测试
              │
              ▼
         Doc Writer 文档更新
              │
              ▼
         Chief Director 验收
```

### 3.2 任务协作流程
```
┌─────────────────────────────────────────────────────────────┐
│                      任务协作循环                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. Dev Lead 接收任务                                       │
│           │                                                  │
│           ▼                                                  │
│   2. Code Writer 执行开发                                   │
│           │                                                  │
│           ▼                                                  │
│   3. QA Engineer 进行测试                                    │
│           │                                                  │
│           ▼                                                  │
│   4. 如有问题 ←──────────── 返回 Code Writer 修复            │
│           │                                                  │
│           │ 测试通过                                          │
│           ▼                                                  │
│   5. Doc Writer 更新文档                                    │
│           │                                                  │
│           ▼                                                  │
│   6. Dev Lead 代码审查                                       │
│           │                                                  │
│           ▼                                                  │
│   7. Chief Director 最终验收                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、沟通协议

### 4.1 日常沟通
| 场景 | 沟通对象 | 方式 |
|------|----------|------|
| 任务分配 | dev_lead → code_writer | 直接分配 |
| 技术指导 | system_architect → dev_lead | 建议反馈 |
| 问题上报 | qa_engineer → dev_lead | 问题报告 |
| 进度汇报 | 所有 Agent → chief_director | 定期汇报 |
| 文档审核 | code_writer → doc_writer | 文档提交 |

### 4.2 协作规则
1. **及时响应**: Agent 应在接收到任务后立即响应
2. **状态同步**: 每完成一个阶段需更新状态
3. **问题升级**: 无法解决的问题应立即上报
4. **质量优先**: 代码必须通过测试才能继续

---

## 五、质量标准

### 5.1 代码质量
- 代码覆盖率 ≥ 80%
- 无高危 Bug
- 通过 Code Review
- 符合编码规范

### 5.2 文档质量
- 文档与代码同步更新
- API 文档完整
- 用户手册清晰易懂

### 5.3 测试质量
- 单元测试通过率 100%
- 集成测试通过率 100%
- 性能测试达标

---

## 六、Pixel Agents 监控

### 6.1 监控指标
| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 任务完成率 | 已完成任务/总任务 | < 80% |
| 通信频率 | Agent 间交互次数 | < 5次/小时 |
| 代码产出 | 代码提交次数 | < 3次/小时 |
| Bug 数量 | 活跃 Bug 数 | > 10 |

### 6.2 状态显示
- 🟢 **运行中**: 正在处理任务
- 🟡 **空闲**: 等待任务分配
- 🔴 **停滞**: 超过30分钟无活动

---

## 七、使用指南

### 7.1 启动 Agent
```bash
# 方式1: 使用 agent 名称
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
claude --agent chief_director

# 方式2: 使用 agents 参数
claude --agents '{
  "chief_director": {"description": "项目总监", "prompt": "..."},
  "system_architect": {"description": "架构师", "prompt": "..."}
}'

# 方式3: 直接使用 prompt
claude -p "使用代码开发 Agent 开发登录模块"
```

### 7.2 查看 Pixel Agents 面板
1. 打开 VS Code
2. 找到 Pixel Agents 扩展
3. 查看团队状态面板
4. 监控各 Agent 忙闲状态

---

## 八、附录

### 8.1 项目路径
```
/Users/panglaohu/Downloads/DoubleBoatClawSystem
```

### 8.2 配置文件
- `pixel-agents.json` - Pixel Agents 监控配置
- `CLAUDE.md` - Claude Code 项目配置
- `.claude/settings.local.json` - Agent 本地设置
- `.claude/agents.json` - Agent 定义文件

### 8.3 联系方式
- Chief Director: chief_director@deep-ocean-ship.local
- System Architect: system_architect@deep-ocean-ship.local
- Marine Researcher: marine_researcher@deep-ocean-ship.local
- Dev Lead: dev_lead@deep-ocean-ship.local
- Code Writer: code_writer@deep-ocean-ship.local
- QA Engineer: qa_engineer@deep-ocean-ship.local
- Doc Writer: doc_writer@deep-ocean-ship.local

---

**文档版本**: v1.0.0  
**最后更新**: 2026-03-23  
**维护团队**: 深海远洋双体船舶智能综合信息系统开发团队
