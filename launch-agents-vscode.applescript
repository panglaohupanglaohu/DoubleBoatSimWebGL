#!/usr/bin/env osascript
-- launch-agents-vscode.applescript
-- 在 VS Code 的集成终端中逐个启动 7 个 Claude Code Agent
-- Pixel Agents 扩展会自动检测并在面板中显示每个 Agent
--
-- 用法:
--   osascript launch-agents-vscode.applescript
-- 或:
--   ./launch-agents-vscode.applescript
--
-- 注意: 需要 macOS 辅助功能权限（系统设置 → 隐私与安全 → 辅助功能 → 允许 Terminal / VS Code）

set agentList to {¬
    "claude --agent chief_director", ¬
    "claude --agent system_architect", ¬
    "claude --agent marine_researcher", ¬
    "claude --agent dev_lead", ¬
    "claude --agent code_writer", ¬
    "claude --agent qa_engineer", ¬
    "claude --agent doc_writer"}

set agentNames to {¬
    "项目总监", ¬
    "架构设计师", ¬
    "海洋研究员", ¬
    "开发主管", ¬
    "代码开发者", ¬
    "测试工程师", ¬
    "文档工程师"}

tell application "Visual Studio Code"
    activate
end tell

delay 1

repeat with i from 1 to (count of agentList)
    set agentCmd to item i of agentList
    set agentName to item i of agentNames

    -- 创建新的 VS Code 集成终端 (Ctrl+Shift+`)
    tell application "System Events"
        tell process "Code"
            -- Ctrl+Shift+` = Create New Terminal
            key code 50 using {control down, shift down}
        end tell
    end tell

    delay 1.5

    -- 输入 claude 命令
    tell application "System Events"
        tell process "Code"
            keystroke agentCmd
            delay 0.3
            key code 36 -- Enter
        end tell
    end tell

    -- 等待 Pixel Agents 检测到新的 JSONL 会话文件
    -- 扫描间隔 1 秒，需要至少 3 秒让文件出现并被扫描到
    delay 5

end repeat

-- 完成后显示通知
display notification "7 个 Claude Agent 已全部启动" with title "DoubleBoatClawSystem" subtitle "请查看 Pixel Agents 面板"
