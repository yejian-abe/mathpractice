# -*- coding: utf-8 -*-
"""每日题集：生成、按日期+年级+用户落盘（同一天同一套题，刷新不变）
文件位置：
- 默认用户：data/daily/YYYY-MM-DD_G{grade}.json（与老版本一致，老数据无缝保留）
- 其他用户：data/daily/YYYY-MM-DD_G{grade}_u{user_id}.json
生成新题集时会参考该用户的学情统计，偏重薄弱知识点（弱点注入）。
支持教材单元过滤（units 参数，见 services/units.py）：只针对勾选单元出题，
题量不足时按教材顺序用更早已学单元补足，仍不足则减量。
"""
import json
import os
from datetime import datetime

from app.config import load_config
from app.generators import arithmetic, equations, word_problems
from app.services import bank, stats
from app.services import units as units_svc

DEFAULT_USER = "default"


def _daily_dir(data_dir):
    return os.path.join(data_dir, "daily")


def _set_path(data_dir, date_str, grade, user_id=DEFAULT_USER):
    """题集文件路径：默认用户沿用老文件名（无后缀）"""
    name = "%s_G%d.json" % (date_str, grade)
    if user_id != DEFAULT_USER:
        name = "%s_G%d_u%s.json" % (date_str, grade, user_id)
    return os.path.join(_daily_dir(data_dir), name)


def _save(data_dir, date_str, grade, dataset, user_id=DEFAULT_USER):
    path = _set_path(data_dir, date_str, grade, user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)


def load_set(data_dir, date_str, grade, user_id=DEFAULT_USER):
    """读取已存在的题集；不存在返回 None"""
    path = _set_path(data_dir, date_str, grade, user_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return None


def find_problem(dataset, problem_id):
    for p in dataset.get("problems", []):
        if p.get("id") == problem_id:
            return p
    return None


# ---------- 弱点注入 ----------

def _semester_volume(semester):
    """学期参数转册别：semester=1 上册 / 2 下册 / 0 或其他 按日期自动判断（None）"""
    return semester if semester in (1, 2) else None


def _prev_volume(grade, volume):
    """教材顺序的上一册（单元补足最后一级用）：
    下册 → 本年级上册；上册 → 上一年级下册；一年级上册无上一册返回 None
    """
    if volume == 2:
        return (grade, 1)
    if grade > 1:
        return (grade - 1, 2)
    return None


def _gen_by_spec(gen, sel, sel_all, prev_gen=None):
    """按单元题型参数生成一题（三级回退）：
    - sel 为 None：不限制，直接生成
    - 先用勾选单元的题型拒绝采样（最多 30 次）
    - 不足时并入教材顺序更早单元的题型补足（最多 20 次）
    - 仍不足时用上一册全池补足（最多 30 次，prev_gen 为上一册生成函数）
    - 最后仍失败返回 None（该题减量）
    """
    if sel is None:
        return gen(None)
    if sel:
        for _ in range(30):
            p = gen(sel)
            if p is not None:
                return p
    if sel_all and sel_all != sel:
        for _ in range(20):
            p = gen(sel_all)
            if p is not None:
                return p
    if prev_gen is not None:
        for _ in range(30):
            p = prev_gen()
            if p is not None:
                return p
    return None


def _gen_word_by_spec(grade, word_sel, word_all):
    """实时生成一道符合单元过滤的应用题（拒绝采样），失败返回 None"""
    if word_sel is None:
        ws = word_problems.generate_word(grade, 1)
        return ws[0] if ws else None
    stages = [word_sel] if word_sel else []
    if word_all and word_all != word_sel:
        stages.append(word_all)
    for cats in stages:
        for _ in range(30):
            ws = word_problems.generate_word(grade, 1)
            if ws and ws[0].get("category") in cats:
                return ws[0]
    return None


def _gen_of_category(data_dir, date_str, user_id, grade, category, semester=0,
                     kind="all", specs=None):
    """生成一道指定知识点的题目：应用题优先从题库按知识点抽取，
    其余题型（及题库缺失时）用拒绝采样实时生成（最多尝试 50 次），失败返回 None
    specs：单元出题参数（见 units_svc.question_specs）；None = 不限制。
    薄弱知识点若不属于允许的单元范围则直接返回 None（注入受单元过滤限制）。
    """
    # 学期册别：手动指定优先，否则按日期自动判断（计算/竖式也按册别出题）
    volume = _semester_volume(semester) or bank.current_volume(date_str)
    if specs is None:
        specs = units_svc.question_specs(grade, volume, None)
    calc_kinds = specs["calc_all"]
    vert_kinds = specs["vert_all"]
    word_cats = specs["word_all"]
    if category.startswith("应用题"):
        # 单元过滤：该应用题模板不在允许范围 → 不注入
        if word_cats is not None and category not in word_cats:
            return None
        w = bank.pick_words(data_dir, date_str, grade, 1, user_id,
                            categories=[category], volume=volume, kind=kind,
                            word_cats=word_cats)
        if w:
            return w[0]
    gens = []
    if calc_kinds is None or calc_kinds:
        gens.append(lambda: arithmetic.generate_calc(grade, volume, calc_kinds))
    if grade <= 6:
        if vert_kinds is None or vert_kinds:
            gens.append(lambda: arithmetic.generate_vertical(
                grade, volume, vert_kinds))
    else:
        gens.append(lambda: equations.generate_equation(grade))

    def _gen_word():
        # 1-2 年级经典模板池为空，generate_word 返回 []，返回 None 跳过
        ws = word_problems.generate_word(grade, 1)
        return ws[0] if ws else None

    gens.append(_gen_word)
    for _ in range(50):
        for g in gens:
            p = g()
            if p is None:
                continue
            if p.get("category") == category:
                return p
    return None


def _inject_weak(data_dir, date_str, user_id, grade, groups, weak_points,
                 semester=0, kind="all", specs=None):
    """用薄弱知识点的题目替换同题型中的一部分题
    groups: {"calc": [...], "middle": [...], "word": [...]}
    每个弱点替换 max(1, 该题型题量//3) 道（最多 2 道）
    specs：单元出题参数；弱点知识点不在允许单元范围时不注入。
    返回注入的知识点列表（用于 dataset.focus_categories 展示）
    """
    focus = []
    for w in weak_points[:3]:
        cat = w.get("category")
        p = _gen_of_category(data_dir, date_str, user_id, grade, cat,
                             semester, kind, specs)
        if p is None:
            continue
        key = "word" if p["type"] == "word" else (
            "middle" if p["type"] in ("vertical", "equation") else "calc")
        lst = groups[key]
        if not lst:
            continue
        n = min(2, max(1, len(lst) // 3))
        injected = 0
        for _ in range(n):
            q = _gen_of_category(data_dir, date_str, user_id, grade, cat,
                                 semester, kind)
            if q is None:
                break
            # 替换列表尾部（保持前几道稳定）
            lst[len(lst) - 1 - injected] = q
            injected += 1
        if injected:
            focus.append(cat)
    return focus


# ---------- 生成与读写 ----------

def get_or_create(data_dir, date_str, grade, user_id=DEFAULT_USER, semester=0,
                  kind="all", units=None):
    """获取当日题集；不存在则按配置生成并立即落盘（保证刷新不变）
    生成前参考该用户学情统计，偏重薄弱知识点。
    semester: 0=按日期自动判断学期册别，1=上册，2=下册（题库抽题使用）。
    kind: 'all'=易错题+常见题都抽，'error'=仅易错题，'common'=仅常见题（题库抽题使用）。
    units: 勾选的教材单元名列表（None/空=不限制）；只针对所选单元出题，
    题量不足时按教材顺序用更早已学单元补足，仍不足用上一册补足，最后才减量。
    """
    dataset = load_set(data_dir, date_str, grade, user_id)
    if dataset is not None:
        return dataset

    cfg = load_config(data_dir)

    # 学期册别：手动指定优先，否则按日期自动判断
    # （题库抽题、计算题与竖式题均按册别对齐教材）
    volume = _semester_volume(semester) or bank.current_volume(date_str)

    # 单元出题参数：勾选单元 kind 并集 + 更早已学单元补足集
    specs = units_svc.question_specs(grade, volume, units)
    # 教材顺序的上一册（更早已学单元仍不足时的最后补足级，1-6 年级才有单元体系）
    prev_vol = _prev_volume(grade, volume) if grade <= 6 else None

    # 学情统计（新用户无记录 → 弱点为空，行为与原版一致）
    try:
        weak_points = stats.compute_stats(data_dir, user_id, grade)["weak_points"]
    except Exception:
        weak_points = []  # 统计失败不影响正常出题

    prev_calc = (lambda: arithmetic.generate_calc(prev_vol[0], prev_vol[1], None)
                 ) if prev_vol else None
    calcs = []
    for _ in range(cfg.get("calc_count", 5)):
        p = _gen_by_spec(
            lambda ks: arithmetic.generate_calc(grade, volume, ks),
            specs["calc_sel"], specs["calc_all"], prev_calc)
        if p is not None:
            calcs.append(p)

    prev_vert = (lambda: arithmetic.generate_vertical(prev_vol[0], prev_vol[1],
                                                      None)) if prev_vol else None
    middle = []
    for _ in range(cfg.get("vertical_count", 4)):
        if grade <= 6:
            p = _gen_by_spec(
                lambda ks: arithmetic.generate_vertical(grade, volume, ks),
                specs["vert_sel"], specs["vert_all"], prev_vert)
        else:
            p = equations.generate_equation(grade)
        if p is not None:
            middle.append(p)

    # 应用题：优先从分册题库抽取（按学期选册、按用户避开已用题、
    # 按勾选单元过滤），先勾选单元 → 更早已学单元 → 上一册 → 实时生成补足
    word_count = cfg.get("word_count", 2)
    words = bank.pick_words(data_dir, date_str, grade, word_count, user_id,
                            volume=volume, kind=kind,
                            word_cats=specs["word_sel"])
    if (len(words) < word_count
            and specs["word_all"] != specs["word_sel"]):
        words.extend(bank.pick_words(
            data_dir, date_str, grade, word_count - len(words), user_id,
            volume=volume, kind=kind, word_cats=specs["word_all"]))
    if len(words) < word_count and prev_vol:
        # 上一册题库补足（不限类别，最后一道防线）
        words.extend(bank.pick_words(
            data_dir, date_str, prev_vol[0], word_count - len(words),
            user_id, volume=prev_vol[1], kind=kind))
    if len(words) < word_count:
        for _ in range(word_count - len(words)):
            w = _gen_word_by_spec(grade, specs["word_sel"], specs["word_all"])
            if w is not None:
                words.append(w)

    # 弱点注入：替换部分题目为薄弱知识点的题（受单元过滤限制）
    focus_categories = _inject_weak(
        data_dir, date_str, user_id, grade,
        {"calc": calcs, "middle": middle, "word": words}, weak_points,
        semester, kind, specs)

    problems = []
    for i, p in enumerate(calcs):
        p["id"] = "c%d" % (i + 1)
        problems.append(p)
    for i, p in enumerate(middle):
        p["id"] = ("v%d" if p["type"] == "vertical" else "e%d") % (i + 1)
        problems.append(p)
    for i, p in enumerate(words):
        p["id"] = "w%d" % (i + 1)
        problems.append(p)

    if not problems and units:
        # 勾选单元全部无题（如仅选认识类单元）→ 回退不限制，保证有题可做
        return get_or_create(data_dir, date_str, grade, user_id, semester,
                             kind, units=None)

    dataset = {
        "date": date_str,
        "grade": grade,
        "user_id": user_id,
        "volume": volume,  # 出题所用册别（1=上册 2=下册），练习记录展示用
        "units": list(units or []),  # 出题限定的单元（空=不限制）
        "created_at": datetime.now().isoformat(),
        "focus_categories": focus_categories,
        "problems": problems,
        "attempts": {},
    }
    _save(data_dir, date_str, grade, dataset, user_id)
    return dataset


def regenerate(data_dir, date_str, grade, user_id=DEFAULT_USER, semester=0,
               kind="all", units=None):
    """家长强制重新生成当日题集（删除旧文件重新生成）"""
    path = _set_path(data_dir, date_str, grade, user_id)
    if os.path.exists(path):
        os.remove(path)
    return get_or_create(data_dir, date_str, grade, user_id, semester, kind,
                         units)


def update_attempt(data_dir, date_str, grade, problem_id, attempt,
                   user_id=DEFAULT_USER):
    """把一次作答与判题结果写回题集文件，刷新后仍能看到成绩"""
    dataset = load_set(data_dir, date_str, grade, user_id)
    if dataset is None:
        return None
    if "attempts" not in dataset or not isinstance(dataset["attempts"], dict):
        dataset["attempts"] = {}
    dataset["attempts"][problem_id] = attempt
    _save(data_dir, date_str, grade, dataset, user_id)
    return dataset


def _parse_set_filename(fn):
    """解析题集文件名：YYYY-MM-DD_G{grade}[_u{user}].json → (date, grade, uid)
    不符合命名规则返回 None"""
    if not fn.endswith(".json") or "_G" not in fn:
        return None
    base = fn[:-5]
    try:
        date_str, g = base.rsplit("_G", 1)
    except ValueError:
        return None
    if "_u" in g:
        grade_part, uid = g.split("_u", 1)
    else:
        grade_part, uid = g, DEFAULT_USER
    try:
        grade = int(grade_part)
    except ValueError:
        return None
    return date_str, grade, uid


def list_history(data_dir, user_id=DEFAULT_USER):
    """列出该用户的历史题集（按日期倒序）
    默认用户匹配无后缀文件；其他用户匹配 _u{user_id} 后缀文件。
    """
    d = _daily_dir(data_dir)
    if not os.path.isdir(d):
        return []
    items = []
    for fn in os.listdir(d):
        parsed = _parse_set_filename(fn)
        if parsed and parsed[2] == user_id:
            items.append({"date": parsed[0], "grade": parsed[1]})
    items.sort(key=lambda x: (x["date"], x["grade"]), reverse=True)
    return items


# ---------- 练习记录 ----------

VOLUME_NAMES = {1: "上册", 2: "下册"}


def volume_of(dataset, semester=0):
    """题集册别：显式指定学期 > 题集记录的 volume 字段 > 按日期推断（老题集）"""
    if semester in (1, 2):
        return semester
    v = dataset.get("volume")
    return v if v in (1, 2) else bank.current_volume(dataset.get("date") or
                                                     "2026-01-01")


def _record_item(dataset):
    """一条练习记录：日期/年级/册别 + 各题型正确数统计"""
    counts = {}
    attempts = dataset.get("attempts") or {}
    for p in dataset.get("problems", []):
        c = counts.setdefault(p.get("type"), {"correct": 0, "total": 0})
        c["total"] += 1
        att = attempts.get(p.get("id"))
        if isinstance(att, dict):
            r = att.get("result") or {}
            if r.get("correct"):
                c["correct"] += 1
    return {
        "date": dataset["date"],
        "grade": dataset["grade"],
        "volume": volume_of(dataset),
        "counts": counts,
        "correct": sum(c["correct"] for c in counts.values()),
        "total": sum(c["total"] for c in counts.values()),
    }


def list_records(data_dir, user_id=DEFAULT_USER, grade=0,
                 date_from=None, date_to=None):
    """练习记录列表（按日期倒序）：筛选条件内题集的分题型正确统计
    grade=0 表示取范围内最高年级的记录（"最高年级"默认筛选）。
    """
    d = _daily_dir(data_dir)
    found = []
    if os.path.isdir(d):
        for fn in os.listdir(d):
            parsed = _parse_set_filename(fn)
            if not parsed or parsed[2] != user_id:
                continue
            date_str, g, _ = parsed
            if date_from and date_str < date_from:
                continue
            if date_to and date_str > date_to:
                continue
            found.append((date_str, g))
    found.sort(key=lambda x: x[0], reverse=True)
    if not found:
        return {"items": [], "grade_used": grade or 0}
    if grade:
        grade_used = grade
    else:
        grade_used = max(g for _, g in found)
    items = []
    for date_str, g in found:
        if g != grade_used:
            continue
        dataset = load_set(data_dir, date_str, g, user_id)
        if dataset is not None:
            items.append(_record_item(dataset))
    return {"items": items, "grade_used": grade_used}


def record_detail(data_dir, date_str, grade, user_id=DEFAULT_USER):
    """单次练习详情：逐题题干、我的作答与对错判定。
    不返回正确答案/解析（防止通过接口抄答案）。题集不存在返回 None。
    """
    dataset = load_set(data_dir, date_str, grade, user_id)
    if dataset is None:
        return None
    attempts = dataset.get("attempts") or {}
    problems = []
    for p in dataset.get("problems", []):
        item = {
            "id": p.get("id"),
            "type": p.get("type"),
            "question": p.get("question", ""),
            "correct": None,  # None=未作答
            "user_answer": "",
        }
        if p.get("type") == "word":
            item["answer_labels"] = p.get("answer_labels") or []
        att = attempts.get(p.get("id"))
        if isinstance(att, dict):
            r = att.get("result") or {}
            item["correct"] = bool(r.get("correct"))
            payload = att.get("payload") or {}
            main = payload.get("main")
            if p.get("type") == "equation":
                if isinstance(main, dict) and main:
                    item["user_answer"] = "，".join(
                        "%s=%s" % (k, v) for k, v in main.items())
                item["sub_results"] = [
                    {"correct": bool(d.get("correct"))}
                    for d in (r.get("details") or {}).values()]
            elif p.get("type") == "word":
                answers = payload.get("answers") or []
                item["user_answer"] = "；".join(str(a) for a in answers)
                item["sub_results"] = [
                    {"correct": bool(a.get("correct"))}
                    for a in (r.get("answer_results") or [])]
            else:
                item["user_answer"] = "" if main is None else str(main)
        problems.append(item)
    return {
        "date": dataset["date"],
        "grade": dataset["grade"],
        "volume": volume_of(dataset),
        "correct": sum(1 for q in problems if q["correct"]),
        "total": len(problems),
        "problems": problems,
    }
