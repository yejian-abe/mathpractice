# -*- coding: utf-8 -*-
"""学情统计：按用户聚合练习结果
- daily：按日期聚合（最近 30 个有作答的日期）→ 正确率曲线
- semester_curve：整个学期的正确率曲线（按学期时间窗过滤全部练习日）
- type_daily / cat_daily：题型 / 知识点逐日正确率序列 → 弹窗曲线
- by_type / by_category：按题型 / 知识点聚合
- weak_points：薄弱知识点（做题 ≥5 且正确率 < 80%，按严重程度排序，前 5 个）
"""
from datetime import date

from app.services import daily_set

# 题型中文名（老题集文件无 category 字段时按题型兜底归类）
_TYPE_LABELS = {"calc": "计算题", "vertical": "竖式计算",
                "equation": "解方程", "word": "应用题"}

# 薄弱点判定阈值
_WEAK_MIN_ATTEMPTS = 5     # 至少做过 5 道才纳入判断（小样本易误判）
_WEAK_RATE = 80.0          # 正确率低于 80% 视为薄弱


def _semester_window(semester="0"):
    """学期时间窗（按当前学年起算，学年 = 9 月至次年 8 月）：
    semester 1=上学期（9/1—次年1/31）、2=下学期（次年2/1—8/31）、
    0=自动（按今天所在学期）。返回 (标签, 起始日期串, 结束日期串)
    """
    today = date.today()
    y, m = today.year, today.month
    sy = y if m >= 9 else y - 1  # 当前学年起始年
    if semester == "2" or (semester != "1" and not (m >= 9 or m == 1)):
        return ("%d-%d 学年下学期" % (sy, sy + 1),
                "%d-02-01" % (sy + 1), "%d-08-31" % (sy + 1))
    return ("%d-%d 学年上学期" % (sy, sy + 1),
            "%d-09-01" % sy, "%d-01-31" % (sy + 1))


def _make_curve(daily):
    """{date: [做题数, 正确数]} → 按日期升序的曲线点列表"""
    return [{
        "date": dt,
        "total": daily[dt][0],
        "correct": daily[dt][1],
        "rate": round(daily[dt][1] * 100.0 / daily[dt][0], 1),
    } for dt in sorted(daily.keys())]


def compute_stats(data_dir, user_id="default", grade=None, semester="0"):
    """聚合该用户（可选限定年级）的全部作答记录"""
    daily = {}       # date -> [做题数, 正确数]
    type_daily = {}  # type -> {date: [做题数, 正确数]}
    cat_daily = {}   # category -> {date: [做题数, 正确数]}
    by_type = {}     # type -> [做题数, 正确数]
    by_cat = {}      # category -> [做题数, 正确数]

    for item in daily_set.list_history(data_dir, user_id):
        if grade is not None and item["grade"] != grade:
            continue
        ds = daily_set.load_set(data_dir, item["date"], item["grade"], user_id)
        if not ds:
            continue
        attempts = ds.get("attempts") or {}
        d_total = d_correct = 0
        for p in ds.get("problems", []):
            att = attempts.get(p.get("id"))
            if not att:
                continue
            ok = 1 if (att.get("result") or {}).get("correct") else 0
            d_total += 1
            d_correct += ok
            t = p.get("type")
            by_type.setdefault(t, [0, 0])
            by_type[t][0] += 1
            by_type[t][1] += ok
            td = type_daily.setdefault(t, {}).setdefault(
                item["date"], [0, 0])
            td[0] += 1
            td[1] += ok
            cat = p.get("category") or _TYPE_LABELS.get(t, t)
            by_cat.setdefault(cat, [0, 0])
            by_cat[cat][0] += 1
            by_cat[cat][1] += ok
            cd = cat_daily.setdefault(cat, {}).setdefault(
                item["date"], [0, 0])
            cd[0] += 1
            cd[1] += ok
        if d_total:
            daily[item["date"]] = [d_total, d_correct]

    # 正确率曲线：按日期升序，取最近 30 个有作答的日期
    curve = _make_curve(daily)[-30:]

    # 整个学期曲线：按学期时间窗过滤全部练习日
    sem_label, sem_start, sem_end = _semester_window(semester)
    sem_daily = {dt: v for dt, v in daily.items()
                 if sem_start <= dt <= sem_end}

    total = sum(v[0] for v in daily.values())
    correct = sum(v[1] for v in daily.values())

    by_type_out = _to_sorted(by_type)
    by_cat_out = _to_sorted(by_cat)

    # 薄弱知识点：做题 ≥5 且正确率 < 80%，按 (1-正确率) × min(题量,10) 降序
    weak = []
    for cat, (n, c) in by_cat.items():
        rate = c * 100.0 / n if n else 0
        if n >= _WEAK_MIN_ATTEMPTS and rate < _WEAK_RATE:
            weak.append({
                "category": cat,
                "attempts": n,
                "correct": c,
                "rate": round(rate, 1),
                "score": round((1 - rate / 100.0) * min(n, 10), 2),
            })
    weak.sort(key=lambda w: -w["score"])
    weak = weak[:5]
    for w in weak:
        w.pop("score")

    return {
        "summary": {
            "total": total,
            "correct": correct,
            "rate": round(correct * 100.0 / total, 1) if total else 0,
        },
        "daily": curve,
        "semester_label": sem_label,
        "semester_curve": _make_curve(sem_daily),
        "type_daily": {t: _make_curve(td) for t, td in type_daily.items()},
        "cat_daily": {c: _make_curve(cd) for c, cd in cat_daily.items()},
        "by_type": by_type_out,
        "by_category": by_cat_out,
        "weak_points": weak,
    }


def _to_sorted(counter):
    """{key: [total, correct]} → 按做题数降序的列表"""
    out = []
    for k, (n, c) in counter.items():
        out.append({
            "name": k,
            "attempts": n,
            "correct": c,
            "rate": round(c * 100.0 / n, 1) if n else 0,
        })
    out.sort(key=lambda x: -x["attempts"])
    return out
