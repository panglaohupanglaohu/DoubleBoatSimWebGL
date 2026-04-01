#!/usr/bin/env osascript
-- start-team-iterm.applescript
-- 使用 iTerm2 自动启动团队 Agent

tell application "iTerm"
    activate
    
    -- 创建第一个窗口
    create window with default profile
    
    -- 定义 Agent 列表
    set agent_cmds to {¬
        "cd /Users/panglaohu/Downloads/DoubleBoatClawSystem && claude --agent chief_director", ¬
        "cd /Users/panglaohu/Downloads/DoubleBoatClawSystem && claude --agent system_architect", ¬
        "cd /Users/panglaohu/Downloads/DoubleBoatClawSystem && claude --agent marine_researcher", ¬
        "cd /Users/panglaohu/Downloads/DoubleBoatClawSystem && claude --agent dev_lead", ¬
        "cd /Users/panglaohu/Downloads/DoubleBoatClawSystem && claude --agent code_writer", ¬
        "cd /Users/panglaohu/Downloads/DoubleBoatClawSystem && claude --agent qa_engineer", ¬
        "cd /Users/panglaohu/Downloads/DoubleBoatClawSystem && claude --agent doc_writer"}
    
    -- 获取当前会话
    set mySession to current session of current window
    
    -- 运行第一个 Agent
    tell mySession
        write text (item 1 of agent_cmds)
    end tell
    
    -- 分割并运行剩余 Agent
    repeat with i from 2 to (length of agent_cmds)
        -- 分割垂直
        set newSession to split vertically with default profile
        tell newSession
            write text (item i of agent_cmds)
        end tell
    end repeat
    
end tell
