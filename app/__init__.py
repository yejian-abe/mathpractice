# -*- coding: utf-8 -*-
"""mathPractice_tool 应用包：Flask 应用工厂与公共常量

create_app 由桌面入口（main.py）与 Android 入口（main_android.py，CI 构建时
作为 main.py 打包）共用；base_dir 统一取本包的上级目录（项目根），
在源码运行、PyInstaller、Android 三种场景下均指向 static 所在目录。
"""
import os
import sys

from flask import Flask, send_from_directory

from app.routes import api_bp

# 服务端口：选用高位端口，避免与常见软件的默认端口（如 8000）冲突
PORT = 10021


def create_app():
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后：静态资源在解包目录（sys._MEIPASS），
        # 题集/配置等运行数据必须放在 exe 同级目录（可写、重启不丢）
        base_dir = sys._MEIPASS
        data_dir = os.path.join(os.path.dirname(sys.executable), "data")
    else:
        # 本包的上级目录即项目根（static 位于项目根下；Android 上为
        # /data/data/<pkg>/files/app，p4a 已将应用文件释放到该可写目录）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
