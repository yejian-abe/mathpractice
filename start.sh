#!/data/data/com.termux/files/usr/bin/bash
# mathPractice_tool Termux 一键启动脚本
# 用法：bash start.sh
cd "$(dirname "$0")" || exit 1

echo "首次运行会安装依赖（flask / reportlab / python-docx），请稍候..."
pip install -r requirements.txt -q || {
    echo "依赖安装失败，请检查网络后重试：pip install -r requirements.txt"
    exit 1
}

# 停掉旧实例
pkill -f "python.*main.py" 2>/dev/null
sleep 1

# 后台启动服务
nohup python main.py > app.log 2>&1 &
sleep 2

# 自动打开浏览器（termux-open 为 Termux 自带）
termux-open "http://127.0.0.1:10021" 2>/dev/null \
  || echo "请手动打开浏览器访问 http://127.0.0.1:10021"

echo ""
echo "===================================="
echo "服务已启动: http://127.0.0.1:10021"
echo "停止服务:   bash stop.sh 或 pkill -f main.py"
echo "运行日志:   app.log"
echo "===================================="
