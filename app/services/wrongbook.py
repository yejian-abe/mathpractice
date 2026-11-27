# -*- coding: utf-8 -*-
"""错题本：聚合历史题集中首答做错的题（day_record 快照，首答口径）
- 不新增练习数据存储：错题直接从各题集文件的 day_record 聚合，
  索引文件只存错因标记与已掌握标记（删题集文件后对应错题自然消失）
- 当天做错的题答案次日解锁（防止当天先看答案再订正，破坏首答口径）
- 「举一反三」按原题知识点生成同型变式题：应用题优先按同 category
  从分册题库严格抽取（不消耗题库做题进度），其余题型（及题库缺失时）
  用拒绝采样实时生成；每道错题 = 原题重做 + 2 道变式
"""
import copy
import json
import os
import random
import re
from datetime import date, datetime

from app.generators import arithmetic, equations, word_problems
from app.services import bank, daily_set, grading

_PRACTICE_KEEP = 10       # 每用户最多保留的重练题集文件数
_PRACTICE_MAX_KEYS = 5    # 单次重练最多覆盖的错题数
_VARIANTS_PER_KEY = 2     # 每道错题的同型变式数（含原题重做共 3 道）
_GEN_TRIES = 30           # 拒绝采样单轮最大尝试次数


# ---------- 索引文件（错因 / 已掌握标记） ----------

def _index_path(data_dir, user_id):
    return os.path.join(data_dir, "wrongbook", "wrongbook_%s.json" % user_id)


def _load_index(data_dir, user_id):
    try:
        with open(_index_path(data_dir, user_id), "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {"resolved": [], "tags": {}}


def _save_index(data_dir, user_id, idx):
    path = _index_path(data_dir, user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)


def item_key(date_str, grade, problem_id):
    return "%s|G%d|%s" % (date_str, grade, problem_id)


def _parse_key(key):
    try:
        date_str, g, pid = str(key).split("|", 2)
        return date_str, int(g[1:]), pid
    except (ValueError, AttributeError):
        return None


def tag_mistake(data_dir, user_id, key, tag):
    """标记错因：careless=粗心失误 / unknown=知识点不会；空串=取消标记"""
    tag = tag if tag in ("careless", "unknown") else ""
    idx = _load_index(data_dir, user_id)
    tags = idx.setdefault("tags", {})
    if tag:
        tags[key] = tag
    else:
        tags.pop(key, None)
    _save_index(data_dir, user_id, idx)
    return True


def mark_resolved(data_dir, user_id, keys, resolved=True):
    """标记/取消已掌握"""
    idx = _load_index(data_dir, user_id)
    rs = set(idx.get("resolved") or [])
    for k in keys or []:
        if resolved:
            rs.add(k)
        else:
            rs.discard(k)
    idx["resolved"] = sorted(rs)
    _save_index(data_dir, user_id, idx)
    return True


# ---------- 错题聚合 ----------

def _answer_text(p):
    """正确答案的展示文本（仅用于已过期错题的复习展示）"""
    t = p.get("type")
    if t == "equation":
        return "，".join("%s=%s" % (k, v)
                        for k, v in (p.get("answer") or {}).items())
    if t == "word":
        return (p.get("answer_display")
                or "；".join(str(a) for a in (p.get("answer") or [])))
    return str(p.get("answer"))


def match_keys(keys, grade=0, volume=0):
    """按年级/册别过滤错题 key 列表（册别按错题日期的学期规则推导）
    成就按「年级×册别」组合隔离统计时用"""
    out = []
    for k in keys or []:
        parsed = _parse_key(k)
        if not parsed:
            continue
        date_str, g, _pid = parsed
        if grade and g != grade:
            continue
        if volume and bank.current_volume(date_str) != volume:
            continue
        out.append(k)
    return out


def list_wrong(data_dir, user_id, today=None, grade=0, volume=0):
    """聚合该用户全部首答做错的题
    排序：未掌握在前 → 错因（不会 < 粗心 < 未标记）→ 日期倒序
    grade 非 0 时只返回该年级；volume 非 0 时只返回该册别（按日期推导）
    """
    today = today or date.today().isoformat()
    idx = _load_index(data_dir, user_id)
    resolved = set(idx.get("resolved") or [])
    tags = idx.get("tags") or {}
    items = []
    for it in daily_set.list_history(data_dir, user_id):
        if grade and it["grade"] != grade:
            continue
        if volume and bank.current_volume(it["date"]) != volume:
            continue
        ds = daily_set.load_set(data_dir, it["date"], it["grade"], user_id)
        dr = daily_set.day_record_of(ds)
        if not dr:
            continue
        full = {p.get("id"): p for p in (ds.get("problems") or [])}
        for q in dr.get("problems") or []:
            if q.get("correct") is not False:  # 答对 / 未作答不收录
                continue
            key = item_key(it["date"], it["grade"], q.get("id"))
            entry = {
                "key": key,
                "date": it["date"],
                "grade": it["grade"],
                "type": q.get("type"),
                "category": q.get("category"),
                "question": q.get("question", ""),
                "user_answer": q.get("user_answer", ""),
                "sub_results": q.get("sub_results"),
                "answer_labels": q.get("answer_labels"),
                "resolved": key in resolved,
                "tag": tags.get(key) or "",
            }
            if it["date"] != today:  # 答案次日解锁
                src = full.get(q.get("id"))
                if src is not None:
                    entry["answer_text"] = _answer_text(src)
            items.append(entry)
    # 先按日期倒序，再利用稳定排序叠加"未掌握优先 / 错因优先"
    items.sort(key=lambda e: (e["date"], e["grade"]), reverse=True)
    tag_order = {"unknown": 0, "careless": 1}
    items.sort(key=lambda e: (e["resolved"], tag_order.get(e["tag"], 2)))
    return items


# ---------- 举一反三（同型变式） ----------

def _accept(q, cat, seen):
    """候选题可用性：非空、题干未重复、（有知识点要求时）category 一致"""
    return (q is not None
            and q.get("question")
            and q.get("question") not in seen
            and (not cat or q.get("category") == cat))


def _gen_variants(p, grade, volume, data_dir, user_id, today, count, seen):
    """按原题知识点生成 count 道同型变式题；失败时返回已生成部分"""
    t = p.get("type")
    cat = p.get("category")
    out = []

    def _reject_sample(gen, tries=_GEN_TRIES):
        for _ in range(tries):
            q = gen()
            if _accept(q, cat, seen):
                out.append(q)
                seen.add(q.get("question"))
                if len(out) >= count:
                    return out
        # 严格同知识点失败 → 放宽知识点限制补足（保证有题可练）
        for _ in range(tries // 3):
            q = gen()
            if q is not None and q.get("question") \
                    and q.get("question") not in seen:
                out.append(q)
                seen.add(q.get("question"))
                if len(out) >= count:
                    return out

    if t in ("calc", "vertical"):
        gen = (lambda: arithmetic.generate_calc(grade, volume, None)) \
            if t == "calc" else \
            (lambda: arithmetic.generate_vertical(grade, volume, None))
        _reject_sample(gen)
    elif t == "equation":
        _reject_sample(lambda: equations.generate_equation(grade))
    elif t == "word":
        # 1) 分册题库严格同知识点抽取（不消耗题库做题进度）
        volume = volume if volume in (1, 2) else bank.current_volume(today)
        pool = bank._load_bank_file(data_dir, grade, volume) or []
        pool = [q for q in pool if q.get("category") == cat] if cat else pool
        random.shuffle(pool)
        for q in pool:
            if q.get("question") and q.get("question") not in seen:
                out.append(copy.deepcopy(q))
                seen.add(q.get("question"))
                if len(out) >= count:
                    return out
        # 2) 实时生成补足（拒绝采样）
        def _gen_word():
            ws = word_problems.generate_word(grade, 1)
            return ws[0] if ws else None
        _reject_sample(_gen_word)
    return out


# ---------- 重练题集 ----------

def _practice_dir(data_dir, user_id):
    return os.path.join(data_dir, "wrongbook", "practice", user_id)


def _cleanup_practice(data_dir, user_id):
    d = _practice_dir(data_dir, user_id)
    try:
        files = sorted(fn for fn in os.listdir(d) if fn.endswith(".json"))
        for fn in files[:-_PRACTICE_KEEP]:
            os.remove(os.path.join(d, fn))
    except OSError:
        pass


def build_practice(data_dir, user_id, keys, today=None):
    """按错题 key 列表生成重练题集（原题重做 + 同型变式）
    返回 (set_id, dataset)；无有效错题时返回 (None, None)
    """
    today = today or date.today().isoformat()
    keys = [k for k in (keys or []) if _parse_key(k)][:_PRACTICE_MAX_KEYS]
    if not keys:
        return None, None
    problems = []
    seen = set()
    for key in keys:
        date_str, grade, pid = _parse_key(key)
        ds = daily_set.load_set(data_dir, date_str, grade, user_id)
        if ds is None:
            continue
        src = daily_set.find_problem(ds, pid)
        if src is None:
            continue
        volume = ds.get("volume") if ds.get("volume") in (1, 2) \
            else bank.current_volume(date_str)
        group = [copy.deepcopy(src)]
        seen.add(src.get("question"))
        group += _gen_variants(src, grade, volume, data_dir, user_id, today,
                               _VARIANTS_PER_KEY, seen)
        for q in group:
            q["origin_key"] = key
            problems.append(q)
    if not problems:
        return None, None
    for i, q in enumerate(problems):
        q["id"] = "wr%d" % (i + 1)
    set_id = "pr_%s" % datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset = {
        "set_id": set_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "origin_keys": keys,
        "problems": problems,
        "attempts": {},
    }
    d = _practice_dir(data_dir, user_id)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, set_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=1)
    _cleanup_practice(data_dir, user_id)
    return set_id, dataset


def load_practice(data_dir, user_id, set_id):
    """读取重练题集（含答案，仅供服务端判题使用）；set_id 白名单校验防路径穿越"""
    if not re.match(r"^pr_[0-9]{8}_[0-9]{6}$", str(set_id or "")):
        return None
    try:
        with open(os.path.join(_practice_dir(data_dir, user_id),
                               set_id + ".json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def answer_practice(data_dir, user_id, set_id, problem_id, payload):
    """重练题集判题：判分并把作答写回重练题集文件（刷新后可恢复）
    整组全部答对后自动把对应错题标记为已掌握（无需手动点击）"""
    ds = load_practice(data_dir, user_id, set_id)
    if ds is None:
        return None
    p = daily_set.find_problem(ds, problem_id)
    if p is None:
        return None
    result = grading.grade_problem(p, payload)
    ds.setdefault("attempts", {})[problem_id] = {
        "payload": payload,
        "result": result,
        "at": datetime.now().isoformat(),
    }
    with open(os.path.join(_practice_dir(data_dir, user_id),
                           str(set_id) + ".json"), "w", encoding="utf-8") as f:
        json.dump(ds, f, ensure_ascii=False, indent=1)
    # 自动标记：全部题目都已作答且全部答对 → 对应错题标记已掌握
    problems = ds.get("problems") or []
    attempts = ds.get("attempts") or {}
    if result.get("correct") and ds.get("origin_keys") \
            and len(attempts) == len(problems) \
            and all((a.get("result") or {}).get("correct")
                    for a in attempts.values()):
        mark_resolved(data_dir, user_id, ds["origin_keys"], True)
    return result
