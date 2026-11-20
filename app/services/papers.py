# -*- coding: utf-8 -*-
"""真题试卷服务：四川各地小学 1-6 年级期末真题卷（组编）
- 题库：data/bank/papers_sichuan.json（随 APK 分发的静态题库）
- 在线答题：选择/填空自动判分（字符串归一化比较 + 数值比较），解答题自评
  三态（done=独立做出来 / hint=看了提示做出来 / fail=没做出来），自评计分：
  done 得满分、hint 得一半（向上取整）、fail 得 0 分
- 答卷：data/papers/<user>.json（按用户存储；APK 打包时该目录被排除，
  不预置运行时数据）
"""
import json
import os
from datetime import datetime
from fractions import Fraction

# 题库文件名（位于 data/bank/ 下）
BANK_FILE = "papers_sichuan.json"

# 自评结果值（与压轴专项一致）
RESULT_DONE, RESULT_HINT, RESULT_FAIL = "done", "hint", "fail"
_VALID_RESULTS = (RESULT_DONE, RESULT_HINT, RESULT_FAIL)

# 对外返回题目时需要隐藏的字段（防止通过开发者工具看答案）
_HIDDEN_FIELDS = ("answer",)

_BANK_CACHE = None  # 题库内容进程级缓存（静态文件，体积小）


def _bank_path(data_dir):
    return os.path.join(data_dir, "bank", BANK_FILE)


def _progress_dir(data_dir):
    return os.path.join(data_dir, "papers")


def _progress_path(data_dir, user_id):
    return os.path.join(_progress_dir(data_dir), "%s.json" % user_id)


def load_bank(data_dir):
    """加载真题卷题库（papers 列表）；文件缺失/损坏返回空列表"""
    global _BANK_CACHE
    if _BANK_CACHE is None:
        try:
            with open(_bank_path(data_dir), "r", encoding="utf-8") as f:
                data = json.load(f)
            _BANK_CACHE = data.get("papers") or []
        except (ValueError, OSError):
            _BANK_CACHE = []
    return _BANK_CACHE


def find_paper(data_dir, paper_id):
    """按 id 查找试卷，找不到返回 None"""
    for p in load_bank(data_dir):
        if p.get("id") == paper_id:
            return p
    return None


def paper_meta(paper):
    """试卷对外列表字段（不含题目内容）"""
    return {
        "id": paper.get("id"),
        "grade": paper.get("grade"),
        "region": paper.get("region"),
        "year": paper.get("year"),
        "title": paper.get("title"),
        "duration": paper.get("duration"),
        "total_score": paper.get("total_score"),
        "note": paper.get("note"),
        "question_count": len(paper.get("questions") or []),
    }


def question_public(q):
    """题目对外字段：客观题隐藏标准答案，解答题保留答案（解析页用时揭示）"""
    pub = {k: v for k, v in q.items() if k not in _HIDDEN_FIELDS}
    # 解答题答案由前端在"查看解析"时展示；填空/选择的标准答案不下发
    return pub


# ---------- 答卷读写 ----------

def _load_progress(data_dir, user_id):
    try:
        with open(_progress_path(data_dir, user_id), "r",
                  encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (ValueError, OSError):
        pass
    return {"user": user_id, "papers": {}}


def _save_progress(data_dir, progress):
    os.makedirs(_progress_dir(data_dir), exist_ok=True)
    with open(_progress_path(data_dir, progress.get("user") or "default"),
              "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=1)


# ---------- 客观题判分 ----------

def _norm_text(s):
    """答案字符串归一化：去空格、全角转半角、统一标点与运算符"""
    if s is None:
        return ""
    s = str(s).strip()
    table = {ord("　"): " ", ord("，"): ",", ord("。"): ".",
             ord("："): ":", ord("；"): ";", ord("＋"): "+",
             ord("－"): "-", ord("×"): "*", ord("÷"): "/",
             ord("−"): "-", ord("—"): "-"}
    # 全角 ASCII 区（！~ ～，U+FF01-U+FF5E）转半角，含全角字母/数字/括号
    for i in range(0xFF01, 0xFF5F):
        table.setdefault(i, i - 0xFEE0)
    s = s.translate(table).replace(" ", "").replace("\t", "")
    return s


def _parse_num(s):
    """把输入解析为 Fraction（支持整数/小数/分数）；失败返回 None"""
    s = _norm_text(s).replace("．", ".")
    if not s:
        return None
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None


def grade_objective(q, user_answer):
    """客观题判分。
    choice：字母比较（大小写、全半角归一化）；
    fill：先做字符串归一化比较，再做数值（Fraction）精确比较（兼容
    分数/小数写法，如 1/2 与 0.5）。
    """
    expected = q.get("answer")
    if q.get("type") == "choice":
        return _norm_text(user_answer).upper() == _norm_text(expected).upper()
    # 填空：文本归一化相等（文字性答案如"长方形"、"厘米"）
    if _norm_text(user_answer) == _norm_text(expected):
        return True
    # 数值比较：两边都能解析为分数/小数时精确比较
    u, e = _parse_num(user_answer), _parse_num(expected)
    return u is not None and e is not None and u == e


# ---------- 答卷提交与成绩 ----------

def submit(data_dir, user_id, paper_id, answers, self_assess, when=None):
    """提交整卷：判客观题 + 存自评 + 计分，返回 (result, error)
    answers: {qid: 用户输入}（choice 选 A/B/C/D；fill 文本）
    self_assess: {qid: done|hint|fail}（解答题自评，可缺省=未做）
    """
    paper = find_paper(data_dir, paper_id)
    if paper is None:
        return None, "试卷不存在"
    answers = answers or {}
    self_assess = self_assess or {}

    graded = {}
    obj_score = 0.0
    for q in paper.get("questions", []):
        qid = q["id"]
        if q.get("type") == "solve":
            result = self_assess.get(qid)
            if result not in _VALID_RESULTS:
                result = None  # 未自评按未做处理
            graded[qid] = {"type": "solve", "self": result}
        else:
            ok = grade_objective(q, answers.get(qid))
            graded[qid] = {"type": q.get("type"), "correct": ok}
            if ok:
                obj_score += q.get("score") or 0

    # 解答题按自评计分：done 满分 / hint 半分（向上取整）/ fail 0 分
    solve_score = 0
    for q in paper.get("questions", []):
        if q.get("type") != "solve":
            continue
        entry = graded.get(q["id"]) or {}
        if entry.get("self") == RESULT_DONE:
            solve_score += q.get("score") or 0
        elif entry.get("self") == RESULT_HINT:
            solve_score += -(-(q.get("score") or 0) // 2)  # 向上取整

    score = int(obj_score) + solve_score
    record = {
        "paper_id": paper_id,
        "answers": {k: str(v) for k, v in answers.items()},
        "graded": graded,
        "score": score,
        "submitted_at": (when or datetime.now()).isoformat(),
    }
    progress = _load_progress(data_dir, user_id)
    progress.setdefault("papers", {})[paper_id] = record
    _save_progress(data_dir, progress)
    return {"score": score, "record": record}, None


def get_answers_state(data_dir, user_id, paper_id):
    """取某用户的整卷答卷记录（用于恢复作答状态），无记录返回 None"""
    progress = _load_progress(data_dir, user_id)
    return progress.get("papers", {}).get(paper_id)


def list_done(data_dir, user_id):
    """该用户已提交的真题卷列表（卷 id、得分、提交时间）"""
    progress = _load_progress(data_dir, user_id)
    items = []
    for paper_id, rec in progress.get("papers", {}).items():
        items.append({
            "paper_id": paper_id,
            "score": rec.get("score"),
            "submitted_at": rec.get("submitted_at"),
        })
    return items
