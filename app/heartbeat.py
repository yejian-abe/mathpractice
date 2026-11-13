# -*- coding: utf-8 -*-
"""页面心跳跟踪：前端页面每 3 秒上报一次，服务端在页面全部关闭后自动退出

机制：record() 由 /api/heartbeat 调用刷新最后心跳时间；watchdog 线程定期检查
idle_seconds()，超过阈值（页面从未打开过则不退出）即 os._exit 退出整个服务。
"""
import threading
import time

_lock = threading.Lock()
_last_beat = 0.0  # 最后一次心跳的时间戳；0 表示尚未有页面打开过


def record():
    global _last_beat
    with _lock:
        _last_beat = time.time()


def idle_seconds():
    """距最近一次心跳的秒数；页面从未打开过时返回 None（表示不判定空闲）"""
    with _lock:
        if _last_beat <= 0.0:
            return None
        return time.time() - _last_beat
