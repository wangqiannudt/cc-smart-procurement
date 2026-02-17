#!/bin/bash

# 智慧采购系统开发启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=================================="
echo "智慧采购系统 - 开发环境启动"
echo "=================================="
echo ""

# 检查是否已安装依赖
if [ ! -d "backend/venv" ]; then
    echo "正在创建 Python 虚拟环境..."
    cd backend
    
    python3 -m venv venv
    echo "虚拟环境创建完成"
    cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "正在安装前端依赖..."
    cd frontend
    npm install
    echo "前端依赖安装完成"
    cd ..
fi

# 启动后端
echo "正在启动后端服务..."
cd backend
source venv/bin/activate

# 检查依赖是否需要更新（比较 requirements.txt 哈希）
REQUIREMENTS_HASH=$(md5sum requirements.txt 2>/dev/null | cut -d' ' -f1)
INSTALLED_HASH=$(cat .requirements_installed 2>/dev/null || echo "")

if [ "$REQUIREMENTS_HASH" != "$INSTALLED_HASH" ]; then
    echo "检测到依赖变更，正在安装..."
    pip install -q -r requirements.txt
    echo "$REQUIREMENTS_HASH" > .requirements_installed
    echo "依赖安装完成"
else
    echo "依赖已是最新，跳过安装"
fi

nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "后端日志: logs/backend.log"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo "正在启动前端服务..."
cd ../frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo "前端日志: logs/frontend.log"
echo ""

# 保存进程ID
echo $BACKEND_PID > ../logs/backend.pid
echo $FRONTEND_PID > ../logs/frontend.pid

echo "=================================="
echo "服务启动完成！"
echo "=================================="
echo ""
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:5173"
echo ""
echo "停止服务: ./stop.sh"
echo ""
echo "后端健康检查: http://localhost:8000/api/health"
echo ""
