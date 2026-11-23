# -*- coding: utf-8 -*-
"""安卓系统打印桥：用 pyjnius 调 Android PrintManager + WebView 打印框架，
把页面打印为 PDF（打印对话框中选"另存为 PDF"即为导出）。
仅安卓 webview bootstrap 下可用；桌面端导入安全（pyjnius/android 类
全部在函数内导入，桌面无 jnius 不报错）。
"""
import os
import time

# main_android.py 在 create_app 前设置；桌面端无此变量
ANDROID = os.environ.get("MPT_ANDROID") == "1"

# jnius 的 Java 代理对象需持有 Python 引用，否则 Java 侧回调时可能被 GC
_RUN_REFS = []

# 可用性缓存：WebView 在 Python 启动前已由 bootstrap 创建，检查一次即可
_STATE = {"checked": False, "ok": False}


def _find_webview(layout):
    """从 bootstrap 布局容器中找出应用内 WebView（getLayout() 是公开 API，
    避免访问 protected 的 PythonActivity.mWebView）"""
    try:
        n = layout.getChildCount()
        for i in range(n):
            child = layout.getChildAt(i)
            if child is not None and \
                    "android.webkit.WebView" in child.getClass().getName():
                return child
    except Exception:
        pass
    return None


def is_available():
    """探测当前环境能否调起系统打印（安卓且应用内 WebView 就绪）"""
    if not ANDROID:
        return False
    if _STATE["checked"]:
        return _STATE["ok"]
    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        layout = PythonActivity.getLayout()
        _STATE["ok"] = layout is not None and _find_webview(layout) is not None
    except Exception:
        _STATE["ok"] = False
    _STATE["checked"] = True
    return _STATE["ok"]


def trigger_print(job_name="数学练习"):
    """调起系统打印对话框，打印 WebView 当前内容（前端已先备好打印视图）。
    返回 (ok, err_msg)。打印对话框由 Android 系统异步展示。"""
    if not ANDROID:
        return False, "仅安卓端支持系统打印"
    try:
        from jnius import autoclass, cast, PythonJavaClass, java_method

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        layout = PythonActivity.getLayout()
        webview = _find_webview(layout) if layout is not None else None
        if webview is None:
            return False, "未找到应用内 WebView，无法打印"
        activity = PythonActivity.mActivity
        if activity is None:
            return False, "Android Activity 未就绪"

        class _PrintOnUi(PythonJavaClass):
            """在 UI 线程执行打印调起（PrintManager 要求主线程）"""
            __javainterfaces__ = ["java/lang/Runnable"]

            def __init__(self):
                super().__init__()
                self.error = None

            @java_method("()V")
            def run(self):
                try:
                    Context = autoclass("android.content.Context")
                    PrintManager = autoclass("android.print.PrintManager")
                    Builder = autoclass("android.print.PrintAttributes$Builder")
                    MediaSize = autoclass("android.print.PrintAttributes$MediaSize")
                    attrs = Builder().setMediaSize(MediaSize.ISO_A4).build()
                    adapter = webview.createPrintDocumentAdapter(job_name)
                    pm = cast("android.print.PrintManager",
                              activity.getSystemService(Context.PRINT_SERVICE))
                    pm.print(job_name, adapter, attrs)
                except Exception as e:
                    self.error = e

        run = _PrintOnUi()
        _RUN_REFS.append(run)
        activity.runOnUiThread(run)
        # runOnUiThread 异步执行，稍候收集同步阶段的错误（如参数/服务获取失败）
        time.sleep(1.0)
        if run.error is not None:
            raise run.error
        return True, ""
    except Exception as e:
        return False, str(e)
