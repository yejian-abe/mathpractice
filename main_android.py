# -*- coding: utf-8 -*-
"""Android APK 启动入口（Buildozer 打包用）

方案：在安卓上以子线程运行 Flask 服务，再用 pyjnius 发 Intent
调用系统浏览器打开 http://127.0.0.1:10021。
本文件仅在安卓构建时作为入口；桌面端仍使用 main.py。
"""
import os
import threading
import time

PORT = 10021
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

from app import create_app

flask_app = create_app()


def serve():
    flask_app.run(host="127.0.0.1", port=PORT, threaded=True, debug=False)


t = threading.Thread(target=serve, daemon=True)
t.start()
time.sleep(1.5)

# 看门狗：浏览器页面全部关闭后自动退出服务（与桌面端 main.py 一致）
# 心跳由页面内 Web Worker 每 3 秒上报；阈值 60 秒兼容平板息屏等心跳暂停场景
from app import heartbeat as _hb


def _watchdog():
    while True:
        time.sleep(3)
        idle = _hb.idle_seconds()
        if idle is not None and idle > 60:
            os._exit(0)


threading.Thread(target=_watchdog, daemon=True).start()

# 用系统浏览器打开页面（避免黑屏 Kivy 窗口挡在前台时也能用）
try:
    from jnius import autoclass

    Intent = autoclass("android.content.Intent")
    Uri = autoclass("android.net.Uri")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    intent = Intent(Intent.ACTION_VIEW, Uri.parse("http://127.0.0.1:%d" % PORT))
    intent.setFlags(0x10000000)  # FLAG_ACTIVITY_NEW_TASK
    PythonActivity.mActivity.startActivity(intent)
except Exception as e:
    print("打开浏览器失败：", e)
    print("请手动打开浏览器访问 http://127.0.0.1:%d" % PORT)

# 保持主线程存活，让 Flask 子线程持续服务
while True:
    time.sleep(60)
