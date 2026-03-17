#!/bin/bash
#
# 自动化测试运行脚本
# 
# 用法：
#   ./run_automation_tests.sh [选项]
#
# 选项:
#   --all       运行所有测试
#   --api       只运行 API 测试
#   --frontend  只运行前端测试
#   --report    生成测试报告
#   --help      显示帮助信息
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路径定义
PROJECT_ROOT="/Users/panglaohu/Downloads/DoubleBoatClawSystem"
TEST_DIR="$PROJECT_ROOT/tests/integration"
REPORT_DIR="$PROJECT_ROOT/tests/reports"
VENV="$PROJECT_ROOT/venv"

# 创建报告目录
mkdir -p "$REPORT_DIR"

# 帮助信息
show_help() {
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  --all       运行所有测试"
    echo "  --api       只运行 API 测试"
    echo "  --frontend  只运行前端测试"
    echo "  --report    生成测试报告"
    echo "  --help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --all"
    echo "  $0 --api"
    echo "  $0 --frontend"
}

# 运行 API 测试
run_api_tests() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}运行 API 自动化测试...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    cd "$PROJECT_ROOT"
    source "$VENV/bin/activate"
    
    pytest tests/integration/test_poseidon_x_integration.py \
        -v \
        --tb=short \
        --html="$REPORT_DIR/api_test_report.html" \
        --self-contained-html \
        -k "TestChannels or TestSensors or TestRoot or TestAPI"
}

# 运行前端测试
run_frontend_tests() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}运行前端自动化测试...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    cd "$PROJECT_ROOT"
    source "$VENV/bin/activate"
    
    pytest tests/integration/test_poseidon_x_integration.py \
        -v \
        --tb=short \
        --html="$REPORT_DIR/frontend_test_report.html" \
        --self-contained-html \
        -k "TestLLMConfig or TestBridgeChat or TestFrontend"
}

# 运行集成测试
run_integration_tests() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}运行集成自动化测试...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    cd "$PROJECT_ROOT"
    source "$VENV/bin/activate"
    
    pytest tests/integration/test_poseidon_x_integration.py \
        -v \
        --tb=short \
        --html="$REPORT_DIR/integration_test_report.html" \
        --self-contained-html \
        -k "TestEndToEnd or TestPerformance or TestWebSocket"
}

# 运行所有测试
run_all_tests() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}运行所有自动化测试...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    cd "$PROJECT_ROOT"
    source "$VENV/bin/activate"
    
    pytest tests/integration/test_poseidon_x_integration.py \
        -v \
        --tb=short \
        --html="$REPORT_DIR/full_test_report.html" \
        --self-contained-html
    
    # 显示测试结果
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}测试完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "测试报告：$REPORT_DIR/full_test_report.html"
}

# 生成测试报告
generate_report() {
    echo -e "${YELLOW}生成测试报告...${NC}"
    
    cd "$PROJECT_ROOT"
    source "$VENV/bin/activate"
    
    # 运行测试并生成 JUnit XML 报告
    pytest tests/integration/test_poseidon_x_integration.py \
        -v \
        --tb=short \
        --junitxml="$REPORT_DIR/junit.xml" \
        --html="$REPORT_DIR/report.html" \
        --self-contained-html
    
    # 生成 Markdown 报告
    python3 << EOF
import xml.etree.ElementTree as ET
from datetime import datetime

tree = ET.parse('$REPORT_DIR/junit.xml')
root = tree.getroot()

testsuites = root.find('testsuite')
if testsuites is None:
    testsuites = root

tests = int(testsuites.get('tests', 0))
failures = int(testsuites.get('failures', 0))
errors = int(testsuites.get('errors', 0))
skipped = int(testsuites.get('skipped', 0))
time_taken = float(testsuites.get('time', 0))

passed = tests - failures - errors - skipped
pass_rate = (passed / tests * 100) if tests > 0 else 0

report = f"""# 🧪 自动化测试报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 测试概览

| 指标 | 数值 |
|------|------|
| 测试总数 | {tests} |
| 通过 | {passed} ✅ |
| 失败 | {failures} ❌ |
| 错误 | {errors} ⚠️ |
| 跳过 | {skipped} ⏭️ |
| 执行时间 | {time_taken:.2f} 秒 |
| 通过率 | {pass_rate:.1f}% |

## 📋 详细结果

"""

    for testcase in testsuites.findall('testcase'):
        name = testcase.get('name')
        classname = testcase.get('classname')
        
        # 检查是否有失败或错误
        failure = testcase.find('failure')
        error = testcase.find('error')
        
        if failure is not None:
            status = "❌ 失败"
            message = failure.get('message', '')
        elif error is not None:
            status = "⚠️ 错误"
            message = error.get('message', '')
        else:
            status = "✅ 通过"
            message = ""
        
        report += f"### {status}: {classname}.{name}\n\n"
        if message:
            report += f"```\n{message}\n```\n\n"

    with open('$REPORT_DIR/report.md', 'w') as f:
        f.write(report)
    
    print(f"✅ 测试报告已生成：$REPORT_DIR/report.md")
    print(f"📄 HTML 报告：$REPORT_DIR/report.html")
EOF
}

# 主程序
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    case "$1" in
        --all)
            run_all_tests
            ;;
        --api)
            run_api_tests
            ;;
        --frontend)
            run_frontend_tests
            ;;
        --integration)
            run_integration_tests
            ;;
        --report)
            generate_report
            ;;
        --help)
            show_help
            ;;
        *)
            echo -e "${RED}未知选项：$1${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
