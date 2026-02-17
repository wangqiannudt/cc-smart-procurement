#!/bin/bash

# 智慧采购系统增强启动脚本
# 增加了AI功能支持

set -e  # 遇到错误立即退出

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================="
echo "智慧采购系统 - AI增强版启动"
echo "=================================="
echo ""

# 创建必要的日志目录
mkdir -p logs

# 重置颜色
echo -e "\033[0m"

# 检查所有必要组件
E_ALL_DEPS=0

echo "🔄 正在检查环境依赖..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    E_ALL_DEPS=1
else
    echo "✅ Python3 已安装:$(which python3)"
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    E_ALL_DEPS=1
else
    echo "✅ Node.js 已安装:$(which node)"
fi

if [ $E_ALL_DEPS -eq 1 ]; then
    echo "❌ 依赖检查失败，请安装缺失的依赖"
    exit 1
fi

echo "✅ 环境依赖检查通过"

### 后端配置 ###
echo ""
echo "🔧 配置后端服务..."

# 检查是否已有后端venv
if [ -d "backend/venv/bin/activate" ]; then
    echo "✅ 发现后端虚拟环境"
else
    echo "📦 创建后端虚拟环境..."
    cd backend
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
    cd ..
fi

# 激活虚拟环境并安装依赖
cd backend
source venv/bin/activate

# 检查依赖是否需要更新（比较 requirements.txt 哈希）
REQUIREMENTS_HASH=$(md5sum requirements.txt 2>/dev/null | cut -d' ' -f1)
INSTALLED_HASH=$(cat .requirements_installed 2>/dev/null || echo "")

if [ "$REQUIREMENTS_HASH" != "$INSTALLED_HASH" ]; then
    echo "📥 检测到依赖变更，正在安装后端依赖..."
    pip install -r requirements.txt --quiet
    echo "$REQUIREMENTS_HASH" > .requirements_installed
    echo "✅ 后端依赖安装完成"
else
    echo "✅ 后端依赖已是最新，跳过安装"
fi

# 检查AI相关依赖（仅在首次时检查）
if [ ! -f .ai_deps_installed ]; then
    if python3 -c "import langchain" &> /dev/null 2>&1; then
        echo "✅ AI依赖(LangChain)已安装"
    else
        echo "🤖 安装AI依赖(LangChain, SentenceTransformers)..."
        pip install langchain langchain-community sentence-transformers
        echo "✅ AI依赖安装完成"
    fi
    touch .ai_deps_installed
fi

# 启动后端
echo "🚀 启动后端服务..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ 后端服务启动成功 (PID: $BACKEND_PID)"
    echo "📊 后端日志: logs/backend.log"
else
    echo "❌ 后端服务启动失败，查看日志获取详情"
    tail -n 20 ../logs/backend.log
    exit 1
fi
cd ..

# 等待后端启动并验证状态
echo "⏳ 等待后端服务启动..."
sleep 2

# 健康检查验证
echo "🏥 进行后端健康检查..."
max_attempts=10
attempt=0
recovery=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health | grep -q "200"; then
        echo "✅ 后端健康检查通过"
        recovery=1
        break
    else
        echo "⏳ 正在重试连接... ($((attempt+1))/$max_attempts)"
        ((attempt++))
        sleep 2
    fi
done

if [ $recovery -ne 1 ]; then
    echo "❌ 后端健康检查失败，请检查端口和服务状态"
    echo "📋 最后30行日志："
    tail -n 30 logs/backend.log
    exit 1
fi

### 前端配置 ###
echo ""
echo "🎨 配置前端服务..."

# 检查前端node_modules
if [ -d "frontend/node_modules" ]; then
    echo "✅ 前端依赖已安装"
else
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 启动前端
echo "🚀 启动前端服务..."
cd frontend

# 启动前端开发服务器
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "✅ 前端服务启动成功 (PID: $FRONTEND_PID)"
    echo "📊 前端日志: logs/frontend.log"
    cd ..
    # 等待前端启动
    sleep 3

    # 检查前端端口（5173）
    if lsof -i :5173 | grep LISTEN > /dev/null 2>&1; then
        echo "✅ 前端端口(5173)监听正常"
    else
        echo "⚠️  前端端口(5173)未启动，但仍可继续运行"
    fi
else
    echo "❌ 前端服务启动失败"
    cd ..
    exit 1
fi

### 集成与验证 ###
echo ""
echo "🔌 进行最终集成验证..."

# 保存进程ID
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

# 总体状态报告
echo ""
echo "=================================="
echo "🎉 智慧采购系统🎯AI增强版启动完成！"
echo "=================================="
echo ""
echo "🌐 服务地址："
echo "   后端API: http://localhost:8000"
echo "   前端界面: http://localhost:5173"
echo "   健康检查: http://localhost:8000/api/health"
echo ""
echo "🎯 AI功能："
echo "   • APP端点: /api/chat/conversation"
echo "   • 场景分析: /api/chat/procurement-analysis"
echo "   • 价格评估: /api/chat/price-recommendation"
echo ""
echo "📋 管理工具："
echo "   日志目录: logs/"
echo "   停止服务: ./stop.sh"
echo "   进程ID:"
echo "     后端: $BACKEND_PID"
echo "     前端: $FRONTEND_PID"
echo ""
echo "🎮 快速体验："
echo "   curl -X POST http://localhost:8000/api/chat/conversation \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"我需要采购服务器\"}'"
echo ""
echo "🔔 系统已就绪，尽情享受AI采购助手！"
echo ""

# 删除旧的演示服务
echo "🧹 清理旧服务..."
pkill -f "python3 -m http.server" 2>/dev/null || true