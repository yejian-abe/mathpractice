# -*- coding: utf-8 -*-
"""初中解方程 / 化简求值生成器（7-9 年级）
- 7 年级：一元一次方程（含括号、移项变体）
- 8 年级：二元一次方程组、化简求值
- 9 年级：一元二次方程（整数根构造）
所有答案为整数解，便于学生作答与自动判题。
"""
import random


def _rand_nonzero(lo, hi):
    while True:
        v = random.randint(lo, hi)
        if v != 0:
            return v


def _signed(v):
    """常数项符号格式化：+5 / -5"""
    if v >= 0:
        return "+ " + str(v)
    return "- " + str(-v)


def _eq_one_var():
    """一元一次方程：3 种变体，保证整数解"""
    a = random.randint(2, 9)
    x0 = _rand_nonzero(-9, 9)
    style = random.random()
    if style < 0.4:
        # ax ± b = c
        b = random.randint(-20, 20)
        c = a * x0 + b
        q = "解方程：%dx %s = %d" % (a, _signed(b), c)
    elif style < 0.7:
        # a(x ± k) = c
        k = random.randint(-9, 9)
        c = a * (x0 + k)
        q = "解方程：%d(x %s) = %d" % (a, _signed(k), c)
    else:
        # ax ± b = cx ± d（移项）
        c2 = random.randint(1, a - 1)
        b = _rand_nonzero(-15, 15)
        d = (a - c2) * x0 + b
        q = "解方程：%dx %s = %dx %s" % (a, _signed(b), c2, _signed(d))
    return {
        "type": "equation",
        "grade": 7,
        "category": "一元一次方程",
        "question": q,
        "answer": {"x": str(x0)},
        "answer_display": "x = %d" % x0,
        "tolerance": 1e-9,
        "note": "",
        "steps": [],
        "solution": [],
    }


def _eq_system():
    """二元一次方程组"""
    x0 = random.randint(1, 9)
    y0 = random.randint(1, 9)
    while True:
        a1 = random.randint(1, 4)
        b1 = random.randint(1, 4)
        a2 = random.randint(1, 4)
        b2 = random.randint(1, 4)
        if a1 * b2 != a2 * b1:
            break
    c1 = a1 * x0 + b1 * y0
    c2 = a2 * x0 + b2 * y0
    q = "解方程组：%dx + %dy = %d，%dx + %dy = %d" % (a1, b1, c1, a2, b2, c2)
    return {
        "type": "equation",
        "grade": 8,
        "category": "二元一次方程组",
        "question": q,
        "answer": {"x": str(x0), "y": str(y0)},
        "answer_display": "x = %d，y = %d" % (x0, y0),
        "tolerance": 1e-9,
        "note": "",
        "steps": [],
        "solution": [],
    }


def _eq_simplify():
    """化简求值：ax + by - (cx - dy)，其中 x=…，y=…"""
    a = random.randint(2, 6)
    b = random.randint(2, 6)
    c = random.randint(1, a - 1)
    d = random.randint(1, b)
    x0 = _rand_nonzero(-5, 5)
    y0 = _rand_nonzero(-5, 5)
    val = (a - c) * x0 + (b + d) * y0
    q = "先化简，再求值：%dx + %dy - (%dx - %dy)，其中 x = %d，y = %d" % (
        a, b, c, d, x0, y0)
    return {
        "type": "equation",
        "grade": 8,
        "category": "化简求值",
        "question": q,
        "answer": {"值": str(val)},
        "answer_display": "化简后为 %dx + %dy，值为 %d" % (a - c, b + d, val),
        "tolerance": 1e-9,
        "note": "",
        "steps": [],
        "solution": [],
    }


def _eq_quadratic():
    """一元二次方程：由两个不同整数根构造"""
    r1 = _rand_nonzero(-9, 9)
    r2 = _rand_nonzero(-9, 9)
    while r2 == r1:
        r2 = _rand_nonzero(-9, 9)
    if r1 > r2:
        r1, r2 = r2, r1
    bs = -(r1 + r2)  # 一次项系数
    cs = r1 * r2      # 常数项
    text = "x²"
    if bs != 0:
        text += " %s %dx" % ("-" if bs < 0 else "+", abs(bs))
    if cs != 0:
        text += " %s %d" % ("-" if cs < 0 else "+", abs(cs))
    q = "解方程：%s = 0" % text
    return {
        "type": "equation",
        "grade": 9,
        "category": "一元二次方程",
        "question": q,
        "answer": {"x1": str(r1), "x2": str(r2)},
        "answer_display": "x1 = %d，x2 = %d" % (r1, r2),
        "tolerance": 1e-9,
        "note": "",
        "steps": [],
        "solution": [],
    }


def generate_equation(grade):
    """按年级生成解方程类题目"""
    if grade <= 7:
        p = _eq_one_var()
        p["grade"] = grade
        return p
    if grade == 8:
        return random.choice([_eq_system, _eq_simplify])()
    return _eq_quadratic()
