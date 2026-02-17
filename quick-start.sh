#!/bin/bash
# 快速启动脚本 - 直接打开演示界面

set -e

echo "=================================="
echo "智慧采购系统 - 快速演示启动"
echo "=================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查演示文件是否存在
if [ ! -f "demonstration/demo.html" ]; then
    echo "❌ 错误：未找到演示文件 demonstration/demo.html"
    echo "请确保项目结构完整"
    exit 1
fi

echo "✅ 找到演示文件：demonstration/demo.html"
echo ""

# 清理旧的Python HTTP服务进程
echo "🧹 清理旧服务进程..."
pkill -f "python3 -m http.server" 2>/dev/null || true
sleep 1

# 检查端口8080是否已被占用
if lsof -i :8080 >/dev/null 2>&1; then
    echo "⚠️  端口8080已被占用，尝试使用端口8081..."
    PORT=8081
else
    PORT=8080
fi

# 启动HTTP服务器
echo "🚀 启动演示服务（端口 $PORT）..."
echo ""

# 在后台启动服务
python3 -m http.server $PORT > demo.log 2>&1 &
SERVER_PID=$!

# 等待服务启动
sleep 2

# 验证服务是否正常运行
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ 演示服务启动成功 (PID: $SERVER_PID)"
    echo ""
    echo "=================================="
    echo "📱 访问地址："
    echo "   http://localhost:$PORT/demonstration/demo.html"
    echo ""
    echo "💡 功能演示："
    echo "   • AI聊天对话"
    echo "   • 服务器选型建议"
    echo "   • 价格合理性分析"
    echo "   • 合同风险识别"
    echo "   • 需求完整性检查"
    echo ""
    echo "🛑 停止服务："
    echo "   kill $SERVER_PID"
    echo "   或使用 Ctrl+C"
    echo "=================================="
    echo ""
    echo "正在尝试在浏览器中打开..."

    # 尝试自动打开浏览器
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:$PORT/demonstration/demo.html" 2>/dev/null || echo "请在浏览器中手动打开上述地址"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open "http://localhost:$PORT/demonstration/demo.html" 2>/dev/null || echo "请在浏览器中手动打开上述地址"
    elif [[ "$OSTYPE" == "msys" ]]; then
        # Windows (Git Bash)
        start "http://localhost:$PORT/demonstration/demo.html" 2>/dev/null || echo "请在浏览器中手动打开上述地址"
    fi

    echo ""
    echo "💬 提示：这是一个纯前端演示，不需要后端服务"
    echo "💬 所有AI功能都通过JavaScript模拟实现"
    echo ""
    echo "按 Ctrl+C 停止服务..."
    echo ""

    # 保持服务运行
    trap "echo ''; echo '🛑 正在停止服务...'; kill $SERVER_PID 2>/dev/null; echo '✅ 服务已停止'; exit 0" INT TERM

    wait $SERVER_PID

else
    echo "❌ 服务启动失败"
    echo "请查看日志获取更多信息："
    cat demo.log | tail -20
    exit 1
fi