# -*- coding: utf-8 -*-
"""统一判题：所有数值答案用 fractions.Fraction 精确比较
支持输入形式：整数（"3"）、负数（"-3"）、分数（"3/4"）、小数（"0.75"）
"""
from fractions import Fraction


def parse_value(v):
    """把用户输入解析为 Fraction；无法解析返回 None"""
    if v is None:
        return None
    s = str(v).strip()
    # 去空格、统一全角/特殊负号
    s = s.replace(" ", "").replace("\u3000", "")
    s = s.replace("−", "-").replace("－", "-").replace("—", "-")
    if not s:
        return None
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None


def _check_single(user_input, expected, tolerance):
    """单值比较"""
    u = parse_value(user_input)
    e = parse_value(expected)
    if u is None or e is None:
        return False
    return abs(u - e) <= tolerance


def grade_problem(problem, payload):
    """判题入口。
    problem: 题目 dict（含 answer/tolerance/steps）
    payload: {"main": str 或 dict, "steps": [str, ...]}
    返回判题结果 dict，供前端展示与存档。
    """
    tolerance = float(problem.get("tolerance") or 1e-9)
    ptype = problem.get("type")
    result = {
        "problem_id": problem.get("id"),
        "type": ptype,
        "correct": False,
    }

    if ptype in ("calc", "vertical"):
        # 单值答案：只返回对错，不直接给出正确答案（鼓励重做）
        ok = _check_single(payload.get("main"), problem.get("answer"), tolerance)
        result["correct"] = ok

    elif ptype == "equation":
        # 变量答案：{"x": "3"} / {"x": "2", "y": "1"} / {"x1": ..., "x2": ...}
        # 只返回每个变量的对错，不直接给出正确答案
        expected = problem.get("answer") or {}
        main = payload.get("main")
        if not isinstance(main, dict):
            main = {}
        details = {}
        all_ok = True
        for var, exp in expected.items():
            ok = _check_single(main.get(var), exp, tolerance)
            details[var] = {"correct": ok}
            if not ok:
                all_ok = False
        result["correct"] = all_ok
        result["details"] = details

    elif ptype == "word":
        # 只判最终答案：各最终数量全部正确才算对；
        # 完整的分步解答与思路在解析（steps + solution）中展示
        expected = problem.get("answer") or []
        user_answers = payload.get("answers") or []
        answer_results = []
        all_ok = len(expected) > 0
        for i, exp in enumerate(expected):
            uv = user_answers[i] if i < len(user_answers) else None
            ok = _check_single(uv, exp, tolerance)
            answer_results.append({"correct": ok})
            if not ok:
                all_ok = False
        result["correct"] = all_ok
        result["answer_results"] = answer_results
        # 完整步骤（含每步答案）与解题思路，供前端在解析区展示
        result["steps"] = [
            {"hint": st.get("hint", ""), "answer": st.get("answer", "")}
            for st in (problem.get("steps") or [])
        ]
        result["solution"] = problem.get("solution", [])
        result["answer_display"] = problem.get("answer_display", "")

    return result
