# -*- coding: utf-8 -*-
"""应用题题库服务：为每日练习按学期册别抽题
- 册别规则：9 月至次年 1 月用上册（vol1），2-8 月用下册（vol2）
- 按用户记录每册已用题下标，避免短期内重复；整册用完自动开启新一轮
- 题库文件不存在（如初中年级）时返回空列表，由调用方回退到实时生成
"""
import copy
import json
import os
import random


def _bank_dir(data_dir):
    return os.path.join(data_dir, "bank")


def _bank_path(data_dir, grade, volume):
    return os.path.join(_bank_dir(data_dir),
                        "grade%d_vol%d_word_bank.json" % (grade, volume))


def _progress_path(data_dir, user_id):
    return os.path.join(_bank_dir(data_dir), "progress_%s.json" % user_id)


def current_volume(date_str):
    """按日期判断学期册别：9 月-次年 1 月为上册，2-8 月为下册"""
    month = int(date_str[5:7])
    return 1 if month >= 9 or month == 1 else 2


def _load_bank_file(data_dir, grade, volume):
    path = _bank_path(data_dir, grade, volume)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("problems") or None
    except (ValueError, OSError):
        return None


def _load_progress(data_dir, user_id):
    path = _progress_path(data_dir, user_id)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return {}


def _save_progress(data_dir, user_id, progress):
    os.makedirs(_bank_dir(data_dir), exist_ok=True)
    with open(_progress_path(data_dir, user_id), "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False)


def pick_words(data_dir, date_str, grade, count, user_id,
               categories=None, volume=None, kind="all", word_cats=None):
    """从指定册别的题库抽 count 道应用题
    volume 为 None 时按日期自动判断学期册别；为 1/2 时使用指定册别（手动选学期）。
    categories 非空时优先抽这些知识点的题（用于弱点注入）。
    kind：'all'=全部（默认），'error'=易错题，'common'=常见题。
    word_cats：单元过滤的应用题 category 集合（"应用题-模板名"）；
    None=不限制，非 None 时只抽集合内的题（空集合直接返回空）。
    返回题目字典列表（深拷贝）；题库不存在或不足时返回已抽到的部分（可能为空），
    由调用方回退到实时生成。
    """
    if count <= 0:
        return []
    volume = volume if volume in (1, 2) else current_volume(date_str)
    problems = _load_bank_file(data_dir, grade, volume)
    if not problems:
        return []
    if kind in ("error", "common"):
        label = "易错题" if kind == "error" else "常见题"
        problems = [p for p in problems if p.get("kind", "易错题") == label]
    if not problems:
        return []
    if word_cats is not None:
        problems = [p for p in problems if p.get("category") in word_cats]
        if not problems:
            return []
    progress = _load_progress(data_dir, user_id)
    key = "g%d_v%d" % (grade, volume)
    used = set(progress.get(key, []))
    avail = [i for i in range(len(problems)) if i not in used]
    if not avail:
        # 本册题库已全部用完 → 清空记录，开启新一轮
        avail = list(range(len(problems)))
        used = set()
    if categories:
        cat_set = set(categories)
        pri = [i for i in avail if problems[i].get("category") in cat_set]
    else:
        pri = []
    pri_set = set(pri)
    rest = [i for i in avail if i not in pri_set]
    random.shuffle(pri)
    random.shuffle(rest)
    chosen = (pri + rest)[:count]
    used.update(chosen)
    progress[key] = sorted(used)
    _save_progress(data_dir, user_id, progress)
    return [copy.deepcopy(problems[i]) for i in chosen]


def remove_progress(data_dir, user_id):
    """删除用户的题库进度（用户被删除时调用）"""
    path = _progress_path(data_dir, user_id)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
