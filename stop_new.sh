#!/bin/bash

# 智慧采购系统AI增强版 - 停止脚本
# 可以彻底停止所有服务，支持残留进程清理

set -e  # 遇到错误立即退出

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================="
echo "🛑 停止智慧采购系统 - AI增强版"
echo "=================================="
echo ""

# 记录当前状态
QUIET_MODE=0
if [ "$1" = "--quiet" ] || [ "$1" = "-q" ]; then
    QUIET_MODE=1
fi

log() {
    if [ $QUIET_MODE -eq 0 ]; then
        echo "$1"
    fi
}

# 停止基于PID文件的服务
stop_service() {
    local service_name="$1"
    local pid_file="$2"
    local process_name="$3"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")

        if ps -p $pid > /dev/null 2>&1; then
            log "🛑 正在停止 ${service_name} 服务 (PID: $pid)..."

            # 优雅停止
            kill -TERM $pid 2>/dev/null

            # 等待服务停止（最多5秒）
            local count=0
            while [ $count -lt 10 ] && ps -p $pid > /dev/null 2>&1; do
                sleep 0.5
                ((count++))
            done

            # 如果还不停止，强制终止
            if ps -p $pid > /dev/null 2>&1; then
                log "⚠️  强制终止 ${service_name} (PID: $pid)"
                kill -KILL $pid 2>/dev/null
            fi

            log "✅ ${service_name} 服务已停止"
        else
            log "⚠️  ${service_name} 服务进程不存在 (PID: $pid)"
        fi

        rm -f "$pid_file"
    else
        log "ℹ️  未找到 ${service_name} 的PID文件"
    fi
}

# 停止特定模式的进程
stop_by_pattern() {
    local pattern="$1"
    local friendly_name="$2"

    local pids=$(pgrep -f "$pattern" || true)

    if [ -n "$pids" ]; then
        log "🧹 正在停止残留进程: $friendly_name"

        for pid in $pids; do
            log "  🛑 终止进程 $pid"
            kill $pid 2>/dev/null || true
        done

        # 等待进程完全退出
        sleep 1

        # 如果还有进程，强制结束
        local remaining_pids=$(pgrep -f "$pattern" || true)
        if [ -n "$remaining_pids" ]; then
            log "  ⚡ 强制终止剩余进程"
            for pid in $remaining_pids; do
                log "     🗑️ 强制结束 $pid"
                kill -KILL $pid 2>/dev/null || true
            done
        fi
    fi
}

# 清理PID文件
clean_pid_files() {
    log "🧹 清理PID文件..."
    rm -f logs/*.pid || true
}

# 清理日志文件（可选）
clean_logs() {
    local clear_logs=false
    if [ "$1" = "--clean-logs" ] || [ "$1" = "-c" ]; then
        clear_logs=true
    fi

    if [ "$clear_logs" = true ]; then
        log "🗑️ 清理日志文件..."
        rm -f logs/*.log || true
        log "✅ 日志文件已清理"
    fi
}

# 服务状态检查
check_status() {
    local all_clear=true
    local status_code=0

    log ""
    log "🔍 检查服务状态:"

    # 检查后端
    if lsof -i :8000 >/dev/null 2>&1; then
        log "❌ 后端服务仍在8000端口运行"
        all_clear=false
        status_code=1
    else
        log "✅ 后端端口8000监听已释放"
    fi

    # 检查前端
    if lsof -i :5173 >/dev/null 2>&1; then
        log "❌ 前端服务仍在5173端口运行"
        all_clear=false
        status_code=1
    else
        log "✅ 前端端口5173监听已释放"
    fi

    # 检查演示服务
    if lsof -i :8080 >/dev/null 2>&1; then
        log "❌ 演示服务仍在8080端口运行"
        all_clear=false
        status_code=1
    else
        log "✅ 演示端口8080监听已释放"
    fi

    return $status_code
}

# 主流程
echo "=================================="
echo "🛑 停止智慧采购系统 - AI增强版"
echo "=================================="
echo ""

# 保存当前状态以进行报告
STOPPED_SERVICES=""
STOPPED_PIDS=""

### 停止主要服务 ###

# 停止后端服务
stop_service "后端API" "logs/backend.pid" "uvicorn app.main"

# 停止前端服务
stop_service "前端开发服务" "logs/frontend.pid" "vite"

# 清理残留进程
stop_by_pattern "uvicorn app.main:app" "(后端UVICORN)"
stop_by_pattern "node.*vite" "(VITE前端)"

### 清理和验证 ###

# 清理PID文件
clean_pid_files

# 等待清理完成并检查状态
echo ""
echo "⏳ 等待系统资源释放..."
sleep 2

echo ""
echo "✅ 停止流程完成"

# 额外功能
if [ "$1" = "--clean-logs" ] || [ "$1" = "-c" ]; then
    clean_logs
fi

# 最终状态确认
echo ""
echo "📋 最终状态报告:"
check_status

# 退出代码
EXIT_CODE=0
if killall -0 send >/dev/null 2>&1 || pgrep -f "uvicorn\|vite\|node" >/dev/null 2>&1; then
    echo "❌ 仍有服务进程残留，请手动检查如下进程:"
    ps aux | grep -E "uvicorn|vite|python|node" | grep -v grep | head -10
    EXIT_CODE=1
else
    echo ""
    echo "🎉 所有服务已成功停止"
    echo "💡 提示信息："
    echo "   • 查看日志: tail -f logs/backend.log"
    echo "   • 重启服务: ./dev.sh"
    echo "   • 清理日志: $0 --clean-logs"
fi

exit $EXIT_CODE