#!/bin/bash

# 智慧采购系统停止脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=================================="
echo "停止智慧采购系统"
echo "=================================="
echo ""

# 停止后端
if [ -f "$SCRIPT_DIR/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/logs/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        echo "后端服务已停止 (PID: $BACKEND_PID)"
    else
        echo "后端服务未运行"
    fi
    rm -f "$SCRIPT_DIR/logs/backend.pid"
fi

# 停止前端
if [ -f "$SCRIPT_DIR/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/logs/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        echo "前端服务已停止 (PID: $FRONTEND_PID)"
    else
        echo "前端服务未运行"
    fi
    rm -f "$SCRIPT_DIR/logs/frontend.pid"
fi

# 清理可能的残留进程
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "已清理后端残留进程"
pkill -f "vite" 2>/dev/null && echo "已清理前端残留进程"

echo ""
echo "所有服务已停止"
