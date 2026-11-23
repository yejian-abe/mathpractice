# -*- coding: utf-8 -*-
"""Android APK 启动入口（Buildozer 打包用）

方案：webview bootstrap——子线程运行 Flask 服务，再用 pyjnius 调
PythonActivity.loadUrl 把页面加载进应用内 WebView。
不再跳系统浏览器：应用退后台会成为缓存进程，Android 12+ 缓存应用
冻结器会整体冻结进程，本地 127.0.0.1 请求被内核代答后永远得不到
服务，页面提交等所有 fetch 挂起（debug 构建不暴露：debuggable 进程
不冻结）。应用内 WebView 使应用始终前台，进程不会被冻结。
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

# 看门狗：页面全部关闭后自动退出服务（与桌面端 main.py 一致）
# 心跳由页面内 Web Worker 每 3 秒上报；阈值 60 秒兼容平板息屏等心跳暂停场景
from app import heartbeat as _hb


def _watchdog():
    while True:
        time.sleep(3)
        idle = _hb.idle_seconds()
        if idle is not None and idle > 60:
            os._exit(0)


threading.Thread(target=_watchdog, daemon=True).start()

# 用应用内 WebView 打开页面（webview bootstrap 的 PythonActivity 提供
# 静态 loadUrl；removeLoadingScreen 移除启动图标遮罩）。若失败回退
# 老方案：调系统浏览器打开
try:
    from jnius import autoclass

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    PythonActivity.loadUrl("http://127.0.0.1:%d" % PORT)
    PythonActivity.mActivity.removeLoadingScreen()
except Exception as e:
    print("WebView 加载失败，回退系统浏览器：", e)
    try:
        from jnius import autoclass

        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        intent = Intent(Intent.ACTION_VIEW, Uri.parse("http://127.0.0.1:%d" % PORT))
        intent.setFlags(0x10000000)  # FLAG_ACTIVITY_NEW_TASK
        PythonActivity.mActivity.startActivity(intent)
    except Exception as e2:
        print("打开浏览器失败：", e2)
        print("请手动打开浏览器访问 http://127.0.0.1:%d" % PORT)

# 保持主线程存活，让 Flask 子线程持续服务
while True:
    time.sleep(60)
