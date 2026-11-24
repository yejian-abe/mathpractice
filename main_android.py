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
import shutil
import threading
import time

PORT = 10021
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

# 安卓标记：在 create_app 前设置，服务端据此上报设备能力（/api/caps 的
# print 字段供前端显示「打印 / 保存 PDF」），print_bridge 也据此放行
os.environ["MPT_ANDROID"] = "1"

from app import create_app


def _android_data_dir():
    """运行数据目录：外部应用专属目录（Android/data/<pkg>/files/data）。
    不能放应用解包目录 files/app——p4a 每次安装新 APK 检测到
    private_version 变化会递归删除 files/app 再重新解包，数据升级即丢
    （用户 #25 升级后练习记录/用户全丢的根因）；getExternalFilesDir
    不受解包影响，覆盖安装保留，仅卸载时清除，且无需存储权限。"""
    from jnius import autoclass

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    ext = PythonActivity.mActivity.getExternalFilesDir(None)
    if ext is None:
        raise RuntimeError("getExternalFilesDir 返回 null")
    return os.path.join(ext.getAbsolutePath(), "data")


try:
    DATA_DIR = _android_data_dir()
    print("Android 数据目录：", DATA_DIR)
    # 首次使用外部数据目录：把 APK 内置的题库模板（解包目录 data/bank，
    # buildozer 已随包释放）播种过去；已存在则不动（保留用户运行数据）
    bundled_bank = os.path.join(BASE, "data", "bank")
    target_bank = os.path.join(DATA_DIR, "bank")
    if os.path.isdir(bundled_bank) and not os.path.isdir(target_bank):
        shutil.copytree(bundled_bank, target_bank)
        print("已播种内置题库到外部数据目录")
except Exception as e:
    # 取不到外部目录时回退应用内目录（能跑，但升级会丢数据）
    print("获取外部数据目录失败，回退应用内目录：", e)
    DATA_DIR = None

flask_app = create_app(DATA_DIR)


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
