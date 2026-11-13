#!/data/data/com.termux/files/usr/bin/bash
# 停止 mathPractice_tool 服务
pkill -f "python.*main.py" && echo "服务已停止" || echo "服务未在运行"
