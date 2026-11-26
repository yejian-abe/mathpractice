# -*- coding: utf-8 -*-
"""mathPractice_tool 应用包：Flask 应用工厂与公共常量

create_app 由桌面入口（main.py）与 Android 入口（main_android.py，CI 构建时
作为 main.py 打包）共用；base_dir 统一取本包的上级目录（项目根），
在源码运行、PyInstaller、Android 三种场景下均指向 static 所在目录。
"""
import os
import shutil
import sys

from flask import Flask, send_from_directory

from app.routes import api_bp

# 服务端口：选用高位端口，避免与常见软件的默认端口（如 8000）冲突
PORT = 10021


def _tree_signature(root):
    """目录内容签名（文件名+内容哈希），检测内置题库是否随版本更新"""
    import hashlib

    h = hashlib.sha1()
    for dirpath, _dirs, files in sorted(os.walk(root)):
        for name in sorted(files):
            h.update(name.encode("utf-8"))
            try:
                with open(os.path.join(dirpath, name), "rb") as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        h.update(chunk)
            except OSError:
                pass
    return h.hexdigest()


def _sync_bundled_bank(base_dir, data_dir):
    """单文件 exe 发布：内置题库自动同步到 exe 旁数据目录。
    - 签名与 .bundled_sig 标记一致 → 跳过（日常启动近乎零开销）
    - 签名变化（新版本更新了题库/配图）→ 覆盖内置侧存在的文件；
      数据目录独有的运行文件（progress_*.json 等）不受影响
    - 失败仅打印警告，不阻断启动（题库缺失时服务会回退实时生成）
    """
    bundled = os.path.join(base_dir, "data", "bank")
    target = os.path.join(data_dir, "bank")
    if not os.path.isdir(bundled):
        return
    os.makedirs(target, exist_ok=True)
    marker = os.path.join(target, ".bundled_sig")
    old = ""
    try:
        with open(marker, "r", encoding="utf-8") as f:
            old = f.read().strip()
    except OSError:
        pass
    sig = _tree_signature(bundled)
    if sig == old:
        return
    print("内置题库有更新，同步到数据目录…")
    n = 0
    for dirpath, _dirs, files in os.walk(bundled):
        rel = os.path.relpath(dirpath, bundled)
        dest = target if rel == "." else os.path.join(target, rel)
        os.makedirs(dest, exist_ok=True)
        for name in files:
            try:
                shutil.copy2(os.path.join(dirpath, name),
                             os.path.join(dest, name))
                n += 1
            except OSError as e:
                print("题库同步失败：", name, e)
    try:
        with open(marker, "w", encoding="utf-8") as f:
            f.write(sig)
        print("题库同步完成：%d 个文件" % n)
    except OSError:
        pass


def create_app(data_dir=None):
    """应用工厂。data_dir：运行数据目录，None 时按运行环境推导。
    Android 入口必须显式传入外部专属目录（getExternalFilesDir）：
    p4a 在每次安装新 APK 时会按 private_version 检测到版本变化并
    递归删除整个 files/app 再重新解包（PythonUtil.unpackAsset 的
    cleanup_on_version_update=true），写在解包目录内的数据升级即丢。"""
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后：静态资源在解包目录（sys._MEIPASS），
        # 题集/配置等运行数据必须放在 exe 同级目录（可写、重启不丢）
        base_dir = sys._MEIPASS
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(sys.executable), "data")
        # 内置题库随版本增量同步（签名一致跳过；更新则覆盖模板文件，
        # progress_* 与用户数据不受影响）
        _sync_bundled_bank(base_dir, data_dir)
    else:
        # 本包的上级目录即项目根（static 位于项目根下）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if data_dir is None:
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
