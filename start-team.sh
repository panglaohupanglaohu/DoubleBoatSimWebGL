#!/bin/bash
# start-team.sh - 启动 Claude Code Agent 团队
# 使用方法: ./start-team.sh

set -e

PROJECT_DIR="/Users/panglaohu/Downloads/DoubleBoatClawSystem"

echo "=========================================="
echo "🚀 启动 Claude Code Agent 团队"
echo "=========================================="
echo ""

# Agent 列表
declare -a AGENTS=(
    "chief_director:项目总监"
    "system_architect:架构设计师"
    "marine_researcher:海洋研究员"
    "dev_lead:开发主管"
    "code_writer:代码开发者"
    "qa_engineer:测试工程师"
    "doc_writer:文档工程师"
)

cd "$PROJECT_DIR"

echo "📁 项目目录: $PROJECT_DIR"
echo ""
echo "Agent 列表:"
for agent in "${AGENTS[@]}"; do
    IFS=':' read -r id desc <<< "$agent"
    echo "  • $id - $desc"
done
echo ""
echo "=========================================="
echo "💡 使用说明:"
echo "=========================================="
echo ""
echo "1. 此脚本会启动 7 个 Claude Code 会话"
echo ""
echo "2. 每个会话对应一个 Agent 角色"
echo ""
echo "3. 在 Pixel Agents 面板中，每个会话会显示为一个角色"
echo ""
echo "4. 关闭窗口即可关闭对应的 Agent"
echo ""
echo "=========================================="
echo "⚠️  启动方式选择:"
echo "=========================================="
echo ""
echo "A) 手动方式 - 在终端中逐个运行:"
for agent in "${AGENTS[@]}"; do
    IFS=':' read -r id desc <<< "$agent"
    echo "   claude --agent $id"
done
echo ""
echo "B) 使用 iTerm2 (推荐) - 自动分屏:"
echo "   1. 打开 iTerm2"
echo "   2. 菜单 > Shell > Split Vertically (Cmd+D)"
echo "   3. 在每个分屏中运行上述命令"
echo ""
echo "C) 使用 VS Code Terminal - 分屏:"
echo "   1. Cmd+Shift+P > Pixel Agents: Show Panel"
echo "   2. 打开新的集成终端 (Cmd+Shift+`)"
echo "   3. 菜单 > Terminal > Split Terminal"
echo "   4. 在每个分屏中运行上述命令"
echo ""
echo "=========================================="
echo "🎯 快速启动命令:"
echo "=========================================="
echo ""
echo "# 启动项目总监"
echo "cd $PROJECT_DIR && claude --agent chief_director"
echo ""
echo "# 启动代码开发者"
echo "cd $PROJECT_DIR && claude --agent code_writer"
echo ""
echo "=========================================="
