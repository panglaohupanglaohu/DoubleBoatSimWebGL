#!/usr/bin/env zsh
# start-all.sh - 深海远洋双体船舶智能综合信息系统 一键启动脚本
# 功能: 启动后端 + 前端 + Agent 团队监控
# 用法: ./start-all.sh [选项]
#   选项:
#     --backend-only   仅启动后端
#     --frontend-only  仅启动前端
#     --agents-only    仅启动 Agent 监控
#     --no-agents      启动前后端，不启动 Agent
#     --port <端口>    指定后端端口 (默认 8080)
#     --help           显示帮助

set -euo pipefail

# ── 配置 ──────────────────────────────────────────────
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PORT=8080
FRONTEND_PORT=5173
PID_FILE="$PROJECT_DIR/.running_pids"
LOG_DIR="$PROJECT_DIR/logs"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 启动标志
START_BACKEND=true
START_FRONTEND=true
START_AGENTS=true

# ── 参数解析 ──────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)  START_FRONTEND=false; START_AGENTS=false; shift ;;
        --frontend-only) START_BACKEND=false;  START_AGENTS=false; shift ;;
        --agents-only)   START_BACKEND=false;  START_FRONTEND=false; shift ;;
        --no-agents)     START_AGENTS=false; shift ;;
        --port)          BACKEND_PORT="$2"; shift 2 ;;
        --help)
            head -9 "$0" | tail -8
            exit 0
            ;;
        *) echo -e "${RED}未知选项: $1${NC}"; exit 1 ;;
    esac
done

# ── 工具函数 ──────────────────────────────────────────
log_info()  { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step()  { echo -e "${BLUE}[→]${NC} $1"; }

check_port() {
    local port=$1
    if lsof -i :"$port" &>/dev/null; then
        return 0  # 端口已占用
    fi
    return 1  # 端口空闲
}

wait_for_service() {
    local url=$1 name=$2 timeout=${3:-15}
    local elapsed=0
    while ! curl -sf "$url" &>/dev/null; do
        sleep 1
        ((elapsed++))
        if [[ $elapsed -ge $timeout ]]; then
            log_warn "$name 在 ${timeout}s 内未就绪，可能仍在启动..."
            return 1
        fi
    done
    return 0
}

save_pid() {
    echo "$1:$2" >> "$PID_FILE"
}

# ── 清理函数 ──────────────────────────────────────────
cleanup() {
    echo ""
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  正在关闭所有服务...${NC}"
    echo -e "${YELLOW}════════════════════════════════════════${NC}"

    if [[ -f "$PID_FILE" ]]; then
        while IFS=: read -r name pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null && log_info "已停止 $name (PID: $pid)" || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi

    # 停止 Agent 监控子进程
    jobs -p 2>/dev/null | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true

    log_info "所有服务已关闭"
    exit 0
}

trap cleanup SIGINT SIGTERM

# ── 主流程 ────────────────────────────────────────────
cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"
rm -f "$PID_FILE"

echo ""
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🚢 深海远洋双体船舶智能综合信息系统${NC}"
echo -e "${CYAN}  DoubleBoatClawSystem - 一键启动${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "  📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "  📁 ${PROJECT_DIR}"
echo ""

# ── 1. 环境检查 ──────────────────────────────────────
log_step "检查运行环境..."

if [[ ! -d "$PROJECT_DIR/venv" ]]; then
    log_error "Python 虚拟环境不存在，请先执行: python3 -m venv venv"
    exit 1
fi
source "$PROJECT_DIR/venv/bin/activate"
log_info "Python 虚拟环境已激活"

if ! command -v node &>/dev/null; then
    log_warn "未检测到 Node.js，前端开发服务器可能无法启动"
fi

echo ""

# ── 2. 启动后端 ──────────────────────────────────────
if [[ "$START_BACKEND" == true ]]; then
    log_step "启动后端 FastAPI 服务 (端口 $BACKEND_PORT)..."

    if check_port "$BACKEND_PORT"; then
        log_warn "端口 $BACKEND_PORT 已被占用，跳过后端启动"
        log_info "现有后端服务可用"
    else
        cd "$PROJECT_DIR/src/backend"
        nohup python main.py --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
        BACKEND_PID=$!
        save_pid "Backend" "$BACKEND_PID"
        cd "$PROJECT_DIR"

        log_step "等待后端就绪..."
        if wait_for_service "http://127.0.0.1:${BACKEND_PORT}/health" "Backend" 20; then
            log_info "后端已就绪 (PID: $BACKEND_PID)"
        fi
    fi
    echo ""
fi

# ── 3. 启动前端 ──────────────────────────────────────
if [[ "$START_FRONTEND" == true ]]; then
    log_step "启动前端 Vite 开发服务器 (端口 $FRONTEND_PORT)..."

    if check_port "$FRONTEND_PORT"; then
        log_warn "端口 $FRONTEND_PORT 已被占用，跳过前端启动"
        log_info "现有前端服务可用"
    else
        cd "$PROJECT_DIR"
        nohup npx vite --config vite.config.mjs > "$LOG_DIR/frontend.log" 2>&1 &
        FRONTEND_PID=$!
        save_pid "Frontend" "$FRONTEND_PID"

        log_step "等待前端就绪..."
        if wait_for_service "http://127.0.0.1:${FRONTEND_PORT}" "Frontend" 15; then
            log_info "前端已就绪 (PID: $FRONTEND_PID)"
        fi
    fi
    echo ""
fi

# ── 4. 启动 Agent 团队监控 ───────────────────────────
if [[ "$START_AGENTS" == true ]]; then
    log_step "启动 Agent 团队监控..."

    # Agent ID 与名称映射 (用平行数组替代关联数组，兼容 bash 3.x)
    AGENT_IDS=(chief_director system_architect marine_researcher dev_lead code_writer qa_engineer doc_writer)
    AGENT_NAMES=("项目总监" "架构设计师" "海洋研究员" "开发主管" "代码开发者" "测试工程师" "文档工程师")

    get_agent_name() {
        local target=$1
        case "$target" in
            chief_director)    echo "项目总监" ;;
            system_architect)  echo "架构设计师" ;;
            marine_researcher) echo "海洋研究员" ;;
            dev_lead)          echo "开发主管" ;;
            code_writer)       echo "代码开发者" ;;
            qa_engineer)       echo "测试工程师" ;;
            doc_writer)        echo "文档工程师" ;;
            *)                 echo "$target" ;;
        esac
    }

    # 初始化进度跟踪
    TRACKER="$PROJECT_DIR/progress_tracker.txt"
    touch "$TRACKER"

    # Agent 工作函数
    agent_chief_director() {
        while true; do
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            py_files=$(find "$PROJECT_DIR/src" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
            test_files=$(find "$PROJECT_DIR/tests" -name "test_*.py" 2>/dev/null | wc -l | tr -d ' ')
            echo "[$ts] chief_director: 团队监控 - 源文件: ${py_files}, 测试文件: ${test_files}" >> "$TRACKER"
            sleep 30
        done
    }

    agent_system_architect() {
        while true; do
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            print_count=$(grep -rl "print(" "$PROJECT_DIR/src/" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
            except_count=$(grep -rl "except Exception" "$PROJECT_DIR/src/" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
            echo "[$ts] system_architect: 架构审计 - print残留: ${print_count}文件, 宽泛异常: ${except_count}文件" >> "$TRACKER"
            sleep 45
        done
    }

    agent_code_writer() {
        while true; do
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            todo_count=$(grep -r "TODO\|FIXME\|HACK" "$PROJECT_DIR/src/" --include="*.py" --include="*.js" 2>/dev/null | wc -l | tr -d ' ')
            echo "[$ts] code_writer: 代码巡检 - 待处理标记: ${todo_count}处" >> "$TRACKER"
            sleep 40
        done
    }

    agent_qa_engineer() {
        while true; do
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            test_funcs=$(grep -r "def test_" "$PROJECT_DIR/tests/" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
            assert_count=$(grep -r "assert " "$PROJECT_DIR/tests/" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
            echo "[$ts] qa_engineer: 测试统计 - 测试函数: ${test_funcs}, 断言: ${assert_count}" >> "$TRACKER"
            sleep 50
        done
    }

    agent_marine_researcher() {
        while true; do
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            doc_count=$(find "$PROJECT_DIR/docs" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
            echo "[$ts] marine_researcher: 技术调研 - 文档库: ${doc_count}篇" >> "$TRACKER"
            sleep 60
        done
    }

    agent_doc_writer() {
        while true; do
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            total_lines=$(find "$PROJECT_DIR/docs" -name "*.md" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
            echo "[$ts] doc_writer: 文档维护 - 文档总行数: ${total_lines:-0}" >> "$TRACKER"
            sleep 55
        done
    }

    agent_dev_lead() {
        while true; do
            ts=$(date '+%Y-%m-%d %H:%M:%S')
            recent=$(tail -7 "$TRACKER" 2>/dev/null | wc -l | tr -d ' ')
            echo "[$ts] dev_lead: 进度汇总 - 近期活动: ${recent}条" >> "$TRACKER"
            sleep 35
        done
    }

    # 启动所有 Agent 后台进程
    for agent_id in "${AGENT_IDS[@]}"; do
        agent_${agent_id} &
        save_pid "Agent:$(get_agent_name $agent_id)" "$!"
        log_info "已启动 $(get_agent_name $agent_id) ($agent_id)"
    done

    echo ""
fi

# ── 5. 状态面板 ──────────────────────────────────────
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  ✅ 系统启动完成${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

if [[ "$START_FRONTEND" == true ]]; then
    echo -e "  ${GREEN}🎨 前端${NC}"
    echo -e "     主页:       http://localhost:${FRONTEND_PORT}/"
    echo -e "     驾驶舱:     http://localhost:${FRONTEND_PORT}/captain-cockpit.html"
    echo -e "     数字孪生:   http://localhost:${FRONTEND_PORT}/digital-twin.html"
    echo -e "     监控地图:   http://localhost:${FRONTEND_PORT}/worldmonitor-map.html"
    echo ""
fi

if [[ "$START_BACKEND" == true ]]; then
    echo -e "  ${GREEN}🔌 后端${NC}"
    echo -e "     API:        http://localhost:${BACKEND_PORT}"
    echo -e "     API 文档:   http://localhost:${BACKEND_PORT}/docs"
    echo -e "     WebSocket:  ws://localhost:${BACKEND_PORT}/ws"
    echo ""
fi

if [[ "$START_AGENTS" == true ]]; then
    echo -e "  ${GREEN}🤖 Agent 团队 (7 个 Agent 已激活)${NC}"
    echo -e "     进度日志:   $PROJECT_DIR/progress_tracker.txt"
    echo -e "     查看状态:   tail -f progress_tracker.txt"
    echo ""
    echo -e "  ${BLUE}💡 手动启动 Claude Agent:${NC}"
    echo -e "     claude --agent chief_director"
    echo -e "     claude --agent code_writer"
    echo -e "     claude --agent system_architect"
    echo ""
fi

echo -e "  ${GREEN}📋 日志目录${NC}: $LOG_DIR/"
echo -e "     后端日志:   tail -f logs/backend.log"
echo -e "     前端日志:   tail -f logs/frontend.log"
echo ""
echo -e "  ${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# ── 保持脚本运行 ──────────────────────────────────────
while true; do
    sleep 60

    # 每分钟检查服务状态
    if [[ "$START_BACKEND" == true ]] && ! check_port "$BACKEND_PORT"; then
        log_warn "后端服务已断开 (端口 $BACKEND_PORT)"
    fi
    if [[ "$START_FRONTEND" == true ]] && ! check_port "$FRONTEND_PORT"; then
        log_warn "前端服务已断开 (端口 $FRONTEND_PORT)"
    fi
done
