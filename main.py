# -*- coding: utf-8 -*-
"""mathPractice_tool 入口：Flask 应用
台式机运行本文件后，平板/台式机浏览器访问 http://<本机IP>:10021
"""
import os
import socket
import sys
import threading
import time
import webbrowser

from flask import Flask, send_from_directory

from app.routes import api_bp

# 服务端口：选用高位端口，避免与常见软件的默认端口（如 8000）冲突
PORT = 10021


def get_lan_ip():
    """获取本机局域网 IP：通过向外连接（不实际发送数据）确定出口地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def create_app():
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后：静态资源在解包目录（sys._MEIPASS），
        # 题集/配置等运行数据必须放在 exe 同级目录（可写、重启不丢）
        base_dir = sys._MEIPASS
        data_dir = os.path.join(os.path.dirname(sys.executable), "data")
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    app = Flask(__name__,
                static_folder=os.path.join(base_dir, "static"),
                static_url_path="/static")
    app.config["BASE_DIR"] = base_dir
    app.config["DATA_DIR"] = data_dir
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def index():
        # 单页应用入口
        return send_from_directory(app.static_folder, "index.html")

    return app


if __name__ == "__main__":
    application = create_app()
    print("=" * 50)
    print("台式机访问:  http://localhost:%d" % PORT)
    print("平板访问:    http://%s:%d" % (get_lan_ip(), PORT))
    print("=" * 50)

    # 看门狗：页面（浏览器标签页）全部关闭后自动退出服务
    # 页面（经 Web Worker）每 3 秒发一次 /api/heartbeat；超过 60 秒收不到（且曾有
    # 页面打开过）即退出。阈值取 60 秒：兼容整机睡眠、平板息屏等心跳暂停场景，
    # 避免页面仍开着却被误杀；正常关闭页面后约 1 分钟退出
    from app import heartbeat

    def watchdog():
        # MPT_NO_WATCHDOG=1 时禁用（开发/自动化测试用，避免无页面场景误退出）
        if os.environ.get("MPT_NO_WATCHDOG") == "1":
            return
        while True:
            time.sleep(3)
            idle = heartbeat.idle_seconds()
            if idle is not None and idle > 60:
                print("页面已全部关闭，服务自动退出")
                os._exit(0)

    threading.Thread(target=watchdog, daemon=True).start()

    # 双击图标（exe）启动后自动打开浏览器页面；服务就绪约需 1 秒
    # Termux 环境下 webbrowser 不可用，由 start.sh 用 termux-open 打开
    if os.environ.get("MPT_NO_BROWSER") != "1" and not os.environ.get("TERMUX_VERSION"):
        threading.Timer(1.0, webbrowser.open, args=("http://127.0.0.1:%d" % PORT,)).start()
    application.run(host="0.0.0.0", port=PORT, debug=False)
