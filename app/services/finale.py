# -*- coding: utf-8 -*-
"""压轴专项服务：初中中考压轴题"每周一题"
- 题库：data/bank/finale_grade9_pilot.json（随 APK 分发的精选静态题库）
- 排期：每周推送 1 道（周六为推送日，本周内可提前查看）；未完成的题跨周
  一直展示，直到自评完成
- 自评三态：done=独立做出来 / hint=看了提示做出来 / fail=没做出来；
  fail 的题进入错题回收队列，约 3 周后推送一道同类型没做过的新题
- 进度：data/finale/<user>.json（按用户存储；APK 打包时该目录被排除，
  不预置运行时数据）
"""
import json
import os
from datetime import date, datetime, timedelta

# 题库文件名（位于 data/bank/ 下，与配图目录 finale_figs/ 同级）
BANK_FILE = "finale_grade9_pilot.json"
FIG_DIR = "finale_figs"

# 自评结果值
RESULT_DONE, RESULT_HINT, RESULT_FAIL = "done", "hint", "fail"
_VALID_RESULTS = (RESULT_DONE, RESULT_HINT, RESULT_FAIL)

# 错题回收间隔（天）：2-3 周后推送同类型新题
RETRY_AFTER_DAYS = 21

_BANK_CACHE = None  # 题库内容进程级缓存（静态文件，体积小）


def _bank_path(data_dir):
    return os.path.join(data_dir, "bank", BANK_FILE)


def _fig_dir(data_dir):
    return os.path.join(data_dir, "bank", FIG_DIR)


def _progress_dir(data_dir):
    return os.path.join(data_dir, "finale")


def _progress_path(data_dir, user_id):
    return os.path.join(_progress_dir(data_dir), "%s.json" % user_id)


def load_bank(data_dir):
    """加载压轴题题库（questions 列表）；文件缺失/损坏返回空列表"""
    global _BANK_CACHE
    if _BANK_CACHE is None:
        try:
            with open(_bank_path(data_dir), "r", encoding="utf-8") as f:
                data = json.load(f)
            _BANK_CACHE = data.get("questions") or []
        except (ValueError, OSError):
            _BANK_CACHE = []
    return _BANK_CACHE


def fig_path(data_dir, name):
    """配图安全路径：仅允许纯文件名且真实存在于 finale_figs/ 中"""
    name = os.path.basename(name or "")
    if not name or "/" in name or "\\" in name or name.startswith("."):
        return None
    path = os.path.join(_fig_dir(data_dir), name)
    return path if os.path.isfile(path) else None


# ---------- 进度读写 ----------

def _load_progress(data_dir, user_id):
    try:
        with open(_progress_path(data_dir, user_id), "r",
                  encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (ValueError, OSError):
        pass
    return {"user": user_id, "assigned": [], "retry": []}


def _save_progress(data_dir, progress):
    os.makedirs(_progress_dir(data_dir), exist_ok=True)
    with open(_progress_path(data_dir, progress.get("user") or "default"),
              "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=1)


# ---------- 排期工具 ----------

def _week_key(d):
    """ISO 周标识，如 2026-W47"""
    iso = d.isocalendar()
    return "%04d-W%02d" % (iso[0], iso[1])


def _saturday_of_week(d):
    """该日期所在 ISO 周的周六（推送日）"""
    iso = d.isocalendar()
    monday = date.fromisocalendar(iso[0], iso[1], 1)
    return monday + timedelta(days=5)


def question_meta(q):
    """题目对外字段（题干 + 分步引导 + 解析，揭示时机由前端控制）"""
    return {
        "id": q.get("id"),
        "source": q.get("source"),
        "region": q.get("region"),
        "type": q.get("type"),
        "grade": q.get("grade"),
        "difficulty": q.get("difficulty"),
        "topics": q.get("topics") or [],
        "tags": q.get("tags") or [],
        "stem": q.get("stem"),
        "figure": q.get("figure"),
        "steps": q.get("steps") or [],
        "final_answer": q.get("final_answer"),
        "analysis": q.get("analysis"),
        "knowledge": q.get("knowledge") or [],
    }


def _used_qids(progress):
    return {a.get("qid") for a in progress.get("assigned", [])}


def _pick_new_question(data_dir, progress, today):
    """挑选下一道推送题：优先错题回收（到期的同类型换题），否则按题库
    顺序取下一道没做过的题；全部做完返回 None"""
    bank = load_bank(data_dir)
    if not bank:
        return None
    used = _used_qids(progress)
    by_id = {q["id"]: q for q in bank}

    # 1) 回收队列中最早到期且未换新题的条目
    for entry in sorted(progress.get("retry", []),
                        key=lambda e: e.get("due") or ""):
        if entry.get("new_qid") or (entry.get("due") or "9999") > \
                today.isoformat():
            continue
        want_type = entry.get("type")
        for q in bank:
            if q["id"] not in used and q.get("type") == want_type:
                entry["new_qid"] = q["id"]
                return q
        # 该类型没有新题了，标记避免每次都扫它
        entry["new_qid"] = entry.get("origin") or ""

    # 2) 按题库顺序取下一道没用过的题
    for q in bank:
        if q["id"] not in used:
            return q
    return None


def _ensure_assignment(data_dir, progress, today, force):
    """确保有可展示的题目；返回 (assignment, status, next_push)
    status: active=有未完成题 / completed=本周已完成 / upcoming=未到推送日
    """
    assigned = progress.setdefault("assigned", [])

    # 1) 有未完成的题 → 跨周一直展示
    for a in assigned:
        if not a.get("assessed"):
            return a, "active", None

    # 2) 本周已有完成的题 → 下周六见
    this_week = _week_key(today)
    for a in assigned:
        if a.get("week") == this_week:
            return None, "completed", _saturday_of_week(today) + \
                timedelta(days=7)

    # 3) 本周还没有题：周六起自动推送；force=1 允许提前查看
    if not force and today.weekday() < 5:  # 周一~周五，未到推送日
        return None, "upcoming", _saturday_of_week(today)

    q = _pick_new_question(data_dir, progress, today)
    if q is None:
        return None, "empty", None
    entry = {"qid": q["id"], "week": this_week, "assigned_at":
             today.isoformat(), "assessed": None, "assessed_at": None}
    assigned.append(entry)
    _save_progress(data_dir, progress)
    return entry, "active", None


def _public_assignment(data_dir, entry, status, next_push):
    """组装对外响应：active 附题目内容，其余附提示信息"""
    resp = {"status": status}
    if next_push:
        resp["next_push"] = next_push.isoformat()
    if entry is None:
        return resp
    bank = load_bank(data_dir)
    for q in bank:
        if q["id"] == entry.get("qid"):
            resp["question"] = question_meta(q)
            resp["assessed"] = entry.get("assessed")
            break
    return resp


def get_current(data_dir, user_id, today=None, force=False):
    """当前应推送的压轴题（含排期状态）"""
    today = today or date.today()
    progress = _load_progress(data_dir, user_id)
    entry, status, next_push = _ensure_assignment(data_dir, progress, today,
                                                  force)
    return _public_assignment(data_dir, entry, status, next_push)


def assess(data_dir, user_id, qid, result, today=None):
    """记录自评三态；fail 进错题回收队列。返回 (ok, error)"""
    today = today or date.today()
    if result not in _VALID_RESULTS:
        return False, "无效的自评结果"
    progress = _load_progress(data_dir, user_id)
    entry = None
    for a in progress.setdefault("assigned", []):
        if a.get("qid") == qid:
            entry = a  # 取最近一次分配（同题可能重复出现于回收）
    if entry is None:
        return False, "未找到该题的推送记录"
    entry["assessed"] = result
    entry["assessed_at"] = datetime.now().isoformat()
    if result == RESULT_FAIL:
        bank = load_bank(data_dir)
        qtype = next((q.get("type") for q in bank if q["id"] == qid), None)
        progress.setdefault("retry", []).append({
            "origin": qid,
            "type": qtype,
            "added": today.isoformat(),
            "due": (today + timedelta(days=RETRY_AFTER_DAYS)).isoformat(),
            "new_qid": None,
        })
    _save_progress(data_dir, progress)
    return True, None


def list_history(data_dir, user_id):
    """已完成（已自评）的推送记录，按分配时间倒序"""
    progress = _load_progress(data_dir, user_id)
    bank = {q["id"]: q for q in load_bank(data_dir)}
    items = []
    for a in progress.get("assigned", []):
        if not a.get("assessed"):
            continue
        q = bank.get(a.get("qid")) or {}
        items.append({
            "qid": a.get("qid"),
            "week": a.get("week"),
            "assigned_at": a.get("assigned_at"),
            "assessed_at": a.get("assessed_at"),
            "result": a.get("assessed"),
            "source": q.get("source"),
            "region": q.get("region"),
            "type": q.get("type"),
            "difficulty": q.get("difficulty"),
            "topics": q.get("topics") or [],
        })
    items.reverse()
    return {"items": items}
