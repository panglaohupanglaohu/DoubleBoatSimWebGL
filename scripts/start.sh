#!/bin/bash
# DoubleBoatClawSystem 启动脚本

set -e

echo "🚀 Starting DoubleBoatClawSystem..."

# 进入项目目录
cd "$(dirname "$0")/.."

# 激活 Python 虚拟环境
echo "📦 Activating Python virtual environment..."
source venv/bin/activate

# 可选：通过环境变量切换到 S3 / MinIO 云同步
# export POSEIDON_LAKEHOUSE_CLOUD_TYPE=s3
# export POSEIDON_LAKEHOUSE_S3_ENDPOINT_URL=http://127.0.0.1:9000
# export POSEIDON_LAKEHOUSE_S3_BUCKET=doubleboat-events
# export POSEIDON_LAKEHOUSE_S3_REGION=us-east-1
# export POSEIDON_LAKEHOUSE_S3_ADDRESSING_STYLE=path
# export POSEIDON_LAKEHOUSE_S3_VERIFY_SSL=false
# export POSEIDON_LAKEHOUSE_S3_AUTO_CREATE_BUCKET=true

# 启动后端服务器
echo "🌐 Starting backend server on port 8082..."
nohup python src/backend/main.py --host 0.0.0.0 --port 8082 > /tmp/poseidon.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 检查后端状态
if curl -s http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️ Backend may still be starting..."
fi

# 启动前端 HTTP 服务器 (使用 Python)
echo "🎨 Starting frontend server on port 3000..."
cd src/frontend
nohup python -m http.server 3000 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# 输出访问信息
echo ""
echo "=========================================="
echo "  DoubleBoatClawSystem 已启动!"
echo "=========================================="
echo ""
echo "  🌐 前端访问：http://localhost:3000/digital-twin.html"
echo "  🔌 后端 API:  http://localhost:8082"
echo "  📡 WebSocket: ws://localhost:8082/ws"
echo "  📊 API 文档：http://localhost:8082/docs"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '🛑 Services stopped'; exit 0" INT

# 保持运行
wait
