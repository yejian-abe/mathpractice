# -*- coding: utf-8 -*-
"""成就徽章：复用现有统计数据判定解锁，不新增数据采集
- 数据源：practice_summary（练习/全对/连续天数）、sprint best 与已交卷局数、
  错题本已掌握数、真题卷完成数、压轴/思维拓展完成数
- 每个徽章带 progress/target 进度，前端徽章墙展示解锁状态与进度
- 纯实时计算，无落盘存储
"""
import os

from app.services import daily_set, finale, papers, sprint
from app.services import wrongbook as wrongbook_svc

# 徽章定义：id / 名称 / 描述 / 图标(前端 SVG 图标 id，见 static/js/app.js ACHIEVE_ICONS) / 目标值
# 判定逻辑在 _badge_value 中按 id 计算（progress, unlocked）
BADGES = [
    {"id": "first_practice", "name": "开练第一天", "icon": "sprout",
     "desc": "完成第一次每日一练", "target": 1},
    {"id": "week_streak", "name": "坚持一周", "icon": "calendar-check",
     "desc": "累计练习 7 天", "target": 7},
    {"id": "month_streak", "name": "坚持一月", "icon": "trophy",
     "desc": "累计练习 20 天", "target": 20},
    {"id": "hundred", "name": "百日坚持", "icon": "gem",
     "desc": "累计练习 100 天", "target": 100},
    {"id": "first_all_ok", "name": "全对时刻", "icon": "star",
     "desc": "第一次全对一整套题", "target": 1},
    {"id": "ten_all_ok", "name": "全对十日", "icon": "sparkles",
     "desc": "累计 10 天全对", "target": 10},
    {"id": "streak7", "name": "连战连捷", "icon": "flame",
     "desc": "历史最长连续全对 7 天（中间没练的天不打断）", "target": 7},
    {"id": "streak3", "name": "小试身手", "icon": "zap",
     "desc": "历史最长连续全对 3 天", "target": 3},
    {"id": "days30", "name": "千锤百炼", "icon": "hammer",
     "desc": "累计练习 30 天", "target": 30},
    {"id": "streak14", "name": "星火不熄", "icon": "sunrise",
     "desc": "历史最长连续全对 14 天", "target": 14},
    {"id": "full_days20", "name": "全对满月", "icon": "badge-check",
     "desc": "累计全对 20 天", "target": 20},
    {"id": "sprint_oral", "name": "口算达人", "icon": "calculator",
     "desc": "限时挑战单局答对率达到 90%", "target": 1},
    {"id": "sprint_perfect", "name": "完美一局", "icon": "circle-check-big",
     "desc": "限时挑战单局全部答对", "target": 1},
    {"id": "sprint_20", "name": "神速手", "icon": "gauge",
     "desc": "限时挑战单局答对 20 题以上", "target": 1},
    {"id": "sprint_five", "name": "挑战常客", "icon": "timer",
     "desc": "完成 5 局限时挑战", "target": 5},
    {"id": "sprint_ten", "name": "挑战狂人", "icon": "repeat",
     "desc": "完成 10 局限时挑战", "target": 10},
    {"id": "wrong_master", "name": "错题克星", "icon": "shield-check",
     "desc": "掌握 10 道错题", "target": 10},
    {"id": "wrong_30", "name": "错题终结者", "icon": "swords",
     "desc": "掌握 30 道错题", "target": 30},
    {"id": "wrong_clear", "name": "卷土重来", "icon": "rotate-ccw",
     "desc": "错题全部掌握（清零时刻）", "target": 1},
    {"id": "paper_first", "name": "试卷首秀", "icon": "file-text",
     "desc": "完成第一张真题卷", "target": 1},
    {"id": "paper_five", "name": "考场老将", "icon": "medal",
     "desc": "完成 5 张真题卷", "target": 5},
    {"id": "paper_ten", "name": "身经百战", "icon": "crown",
     "desc": "完成 10 张真题卷", "target": 10},
    {"id": "finale_done", "name": "思维突破", "icon": "lightbulb",
     "desc": "完成第一道每周一题（压轴/思维拓展）", "target": 1},
    {"id": "finale_4", "name": "思维连击", "icon": "layers",
     "desc": "完成 4 道每周一题", "target": 4},
    {"id": "finale_12", "name": "思维大师", "icon": "graduation-cap",
     "desc": "完成 12 道每周一题", "target": 12},
]


def _sprint_submitted(data_dir, user_id):
    """已交卷的限时挑战局数（扫描题集文件，保留上限 10 局）"""
    d = sprint._dir(data_dir, user_id)
    try:
        n = 0
        for fn in os.listdir(d):
            if not fn.startswith("sp_"):
                continue
            ds = sprint.load_sprint(data_dir, user_id, fn[:-5])
            if ds and ds.get("submitted"):
                n += 1
        return n
    except OSError:
        return 0


def _sprint_oral_ok(data_dir, user_id):
    """任一专项单局答对率 ≥ 90%"""
    bests = sprint.load_best(data_dir, user_id) or {}
    for b in bests.values():
        if b.get("total") and b["correct"] * 10 >= b["total"] * 9:
            return True
    return False


def _sprint_best_correct(data_dir, user_id):
    """历届单局最高答对数（所有专项取最大）"""
    bests = sprint.load_best(data_dir, user_id) or {}
    return max([int(b.get("correct") or 0) for b in bests.values()] or [0])


def _sprint_perfect(data_dir, user_id):
    """任一专项单局全部答对"""
    bests = sprint.load_best(data_dir, user_id) or {}
    for b in bests.values():
        if b.get("total") and b.get("correct") == b["total"]:
            return True
    return False


def _wrong_cleared(data_dir, user_id):
    """错题全部掌握：曾经有过错题（已掌握 ≥1）且当前未掌握错题清零"""
    idx = wrongbook_svc._load_index(data_dir, user_id)
    if not (idx.get("resolved") or []):
        return False
    try:
        return len(wrongbook_svc.list_wrong(data_dir, user_id, grade=0)) == 0
    except Exception:
        return False


def _finale_done_count(data_dir, user_id):
    """每周一题完成数：小学思维拓展（mind）+ 初中压轴（finale）两个进度库求和"""
    n = 0
    for grade in (1, 9):  # 1→mind 题库 / 9→finale 题库
        try:
            n += len(finale.list_history(data_dir, user_id,
                                         grade=grade).get("items", []))
        except Exception:
            pass
    return n


def _badge_values(data_dir, user_id):
    """计算各徽章的当前进度值（进度/解锁共用一份数据源）"""
    summary = daily_set.practice_summary(data_dir, user_id)
    idx = wrongbook_svc._load_index(data_dir, user_id)
    return {
        "days": summary.get("days", 0),
        "full_days": summary.get("full_days", 0),
        "streak": summary.get("streak", 0),
        "max_streak": summary.get("max_streak", 0),
        "sprint_ok": 1 if _sprint_oral_ok(data_dir, user_id) else 0,
        "sprint_perfect": 1 if _sprint_perfect(data_dir, user_id) else 0,
        "sprint_best_correct": _sprint_best_correct(data_dir, user_id),
        "sprint_count": _sprint_submitted(data_dir, user_id),
        "wrong_resolved": len(idx.get("resolved") or []),
        "wrong_clear": 1 if _wrong_cleared(data_dir, user_id) else 0,
        "papers": len(papers.list_done(data_dir, user_id) or []),
        "finale_done": _finale_done_count(data_dir, user_id),
    }


def _progress_of(key, values):
    """徽章 id → 当前进度值"""
    return {
        "first_practice": values["days"],
        "week_streak": values["days"],
        "month_streak": values["days"],
        "hundred": values["days"],
        "days30": values["days"],
        "first_all_ok": values["full_days"],
        "ten_all_ok": values["full_days"],
        "full_days20": values["full_days"],
        "streak7": values["max_streak"],
        "streak3": values["max_streak"],
        "streak14": values["max_streak"],
        "sprint_oral": values["sprint_ok"],
        "sprint_perfect": values["sprint_perfect"],
        "sprint_20": values["sprint_best_correct"],
        "sprint_five": values["sprint_count"],
        "sprint_ten": values["sprint_count"],
        "wrong_master": values["wrong_resolved"],
        "wrong_30": values["wrong_resolved"],
        "wrong_clear": values["wrong_clear"],
        "paper_first": values["papers"],
        "paper_five": values["papers"],
        "paper_ten": values["papers"],
        "finale_done": values["finale_done"],
        "finale_4": values["finale_done"],
        "finale_12": values["finale_done"],
    }.get(key, 0)


def list_achievements(data_dir, user_id):
    """徽章列表（含解锁状态与进度）"""
    values = _badge_values(data_dir, user_id)
    items = []
    for b in BADGES:
        progress = _progress_of(b["id"], values)
        items.append({
            "id": b["id"],
            "name": b["name"],
            "desc": b["desc"],
            "icon": b["icon"],
            "target": b["target"],
            "progress": min(progress, b["target"]),
            "unlocked": progress >= b["target"],
        })
    unlocked = sum(1 for it in items if it["unlocked"])
    return {"badges": items, "unlocked_count": unlocked,
            "total_count": len(items)}
