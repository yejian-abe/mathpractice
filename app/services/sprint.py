# -*- coding: utf-8 -*-
"""口算限时挑战：按专项实时生成题集 → 计时作答 → 服务端校验用时并判分
- 题集文件 data/sprint/<user>/sp_<时间戳>.json（含答案，仅供服务端判题）
- best.json 记录每个专项的个人最佳（答对数优先、用时短优先），跨日期保留
- 过期题集自动清理（每用户最多保留 _SET_KEEP 份）
"""
import json
import os
import random
import re
from datetime import datetime

from app.generators import arithmetic
from app.services import grading

_SET_KEEP = 10   # 每用户最多保留的挑战题集文件数
_GRACE = 8       # 交卷宽限秒数（前端倒计时到 0 后自动交卷的网络延迟）


def _dir(data_dir, user_id):
    return os.path.join(data_dir, "sprint", user_id)


def _cleanup(data_dir, user_id):
    d = _dir(data_dir, user_id)
    try:
        files = sorted(fn for fn in os.listdir(d) if fn.startswith("sp_"))
        for fn in files[:-_SET_KEEP]:
            os.remove(os.path.join(d, fn))
    except OSError:
        pass


def list_specials(grade):
    """当前年级可参与的专项列表（含个人最佳信息由前端自行匹配）"""
    return [{"id": sp["id"], "name": sp["name"], "count": sp["count"],
             "seconds": sp["seconds"]}
            for sp in arithmetic.SPECIALS if grade in sp["grades"]]


def create_sprint(data_dir, user_id, grade, special_id, now=None):
    """生成一局限时挑战题集；专项不存在/不适合该年级时返回 (None, None)"""
    sp = arithmetic.find_special(special_id, grade)
    if sp is None:
        return None, None
    now = now or datetime.now()
    problems = []
    seen = set()
    tries = 0
    while len(problems) < sp["count"] and tries < sp["count"] * 5:
        tries += 1
        q, a = arithmetic.CALC_KINDS[random.choice(sp["kinds"])]()
        if q in seen:
            continue
        seen.add(q)
        problems.append({
            "id": "p%d" % (len(problems) + 1),
            "type": "calc",
            "grade": grade,
            "category": sp["name"],
            "question": q,
            "answer": str(a),
            "tolerance": 1e-9,
            "note": "",
            "steps": [],
            "solution": [],
        })
    if not problems:
        return None, None
    set_id = "sp_%s" % now.strftime("%Y%m%d_%H%M%S")
    if os.path.isfile(os.path.join(_dir(data_dir, user_id),
                                   set_id + ".json")):
        # 同一秒内再次开局（连开两局）：追加 4 位十六进制后缀避免覆盖
        set_id += "_%04x" % (now.microsecond // 256 % 0xFFFF)
    dataset = {
        "set_id": set_id,
        "user_id": user_id,
        "grade": grade,
        "special_id": special_id,
        "special_name": sp["name"],
        "count": len(problems),
        "seconds": sp["seconds"],
        "started_at": now.isoformat(),
        "submitted": False,
        "problems": problems,
    }
    d = _dir(data_dir, user_id)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, set_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=1)
    _cleanup(data_dir, user_id)
    return set_id, dataset


def load_sprint(data_dir, user_id, set_id):
    """读取挑战题集（含答案，仅供服务端判题）；set_id 白名单校验防路径穿越"""
    if not re.match(r"^sp_[0-9]{8}_[0-9]{6}(_[0-9a-f]{4})?$",
                    str(set_id or "")):
        return None
    try:
        with open(os.path.join(_dir(data_dir, user_id),
                               set_id + ".json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ---------- 个人最佳 ----------

def _best_path(data_dir, user_id):
    return os.path.join(_dir(data_dir, user_id), "best.json")


def load_best(data_dir, user_id):
    try:
        with open(_best_path(data_dir, user_id), "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def _better(new, old):
    """新成绩是否优于旧最佳：答对数优先，相同比用时（秒）"""
    if old is None:
        return True
    if new["correct"] != old["correct"]:
        return new["correct"] > old["correct"]
    return new["elapsed"] < old["elapsed"]


def _update_best(data_dir, user_id, special_id, score, grade=None,
                 seconds=None):
    """写入个人最佳；返回 (best, record)：record=True 表示打破既有纪录
    条目带 grade（成就按年级隔离统计用；旧条目无 grade 视为全年级通用）
    条目带 seconds（「极速满分」用时≤限时60% 判定用；旧条目无 seconds 不计）"""
    bests = load_best(data_dir, user_id)
    old = bests.get(special_id)
    record = bool(old) and _better(score, old)
    if old is None or _better(score, old):
        bests[special_id] = {
            "correct": score["correct"],
            "total": score["total"],
            "elapsed": score["elapsed"],
            "date": score["date"],
            "grade": grade,
            "seconds": seconds,
        }
        path = _best_path(data_dir, user_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(bests, f, ensure_ascii=False, indent=1)
    return bests.get(special_id), record


# ---------- 交卷判分 ----------

def submit_sprint(data_dir, user_id, set_id, answers, now=None):
    """交卷：校验用时 → 逐题判分 → 更新个人最佳
    返回 dict（含 error 时为业务错误）；题集不存在返回 None
    """
    ds = load_sprint(data_dir, user_id, set_id)
    if ds is None:
        return None
    now = now or datetime.now()
    if ds.get("submitted"):
        return {"error": "already", "result": ds.get("result")}

    try:
        started = datetime.fromisoformat(ds["started_at"])
        elapsed = round((now - started).total_seconds(), 1)
    except (KeyError, ValueError):
        return None
    if elapsed < 0 or elapsed > ds.get("seconds", 3600) + _GRACE:
        return {"error": "expired"}

    items = answers if isinstance(answers, list) else []
    by_id = {p["id"]: p for p in ds["problems"]}
    detail = []
    correct = 0
    for p in ds["problems"]:
        payload = {"main": "", "answers": None}
        for it in items:
            if isinstance(it, dict) and it.get("problem_id") == p["id"]:
                payload = {"main": it.get("main"), "answers": None}
                break
        result = grading.grade_problem(p, payload)
        ok = bool(result.get("correct"))
        if ok:
            correct += 1
        detail.append({
            "problem_id": p["id"],
            "question": p["question"],
            "user_answer": str(payload.get("main") or ""),
            "answer": str(p.get("answer")),
            "correct": ok,
        })

    from datetime import date
    score = {
        "correct": correct,
        "total": len(ds["problems"]),
        "elapsed": elapsed,
        "date": date.today().isoformat(),
    }
    best, record = _update_best(data_dir, user_id, ds["special_id"], score,
                                grade=ds.get("grade"),
                                seconds=ds.get("seconds"))

    result = {
        "special_name": ds.get("special_name", ""),
        "score": score,
        "record": record,       # True = 打破个人最佳（首次挑战只刷新不提示破纪录）
        "best": best,
        "detail": detail,
    }
    ds["submitted"] = True
    ds["result"] = result
    with open(os.path.join(_dir(data_dir, user_id), str(set_id) + ".json"),
              "w", encoding="utf-8") as f:
        json.dump(ds, f, ensure_ascii=False, indent=1)
    return result
