# -*- coding: utf-8 -*-
"""分步应用题模板库
每个模板返回：question / steps[{hint, answer}] / answer_display / solution[...]
- 随机参数保证每一步答案为整数（工程问题除外，含分数答案）
- 小学（3-6 年级）用算术法思路；初中（7-9 年级）用方程法思路
"""
import random
from fractions import Fraction


def _frac_str(f):
    """Fraction 显示：整数直出，否则 a/b"""
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    return "%d/%d" % (f.numerator, f.denominator)


# ---------- 模板 1：鸡兔同笼（5-9 年级，北师大五上"数学好玩·尝试与猜测"） ----------

def _tpl_chicken_rabbit(grade):
    c = random.randint(5, 20)   # 鸡
    r = random.randint(3, 15)   # 兔
    h = c + r
    legs = 2 * c + 4 * r
    q = "笼子里有鸡和兔共 %d 只，数一数一共有 %d 只脚。鸡和兔各有几只？" % (h, legs)
    steps = [
        {"hint": "假设笼子里全部是鸡，脚一共有多少只？", "answer": str(2 * h)},
        {"hint": "实际脚数比假设的多多少只？", "answer": str(legs - 2 * h)},
        {"hint": "每把一只鸡换成一只兔，脚会增加 2 只。兔有多少只？",
         "answer": str((legs - 2 * h) // 2)},
        {"hint": "鸡有多少只？", "answer": str(h - r)},
    ]
    if grade >= 7:
        solution = [
            "思路：设兔有 x 只，则鸡有 (%d - x) 只。" % h,
            "列方程：4x + 2(%d - x) = %d" % (h, legs),
            "去括号整理：2x = %d，解得 x = %d" % (legs - 2 * h, r),
            "答：兔 %d 只，鸡 %d 只。验算：4×%d + 2×%d = %d 只脚，符合题意。" % (r, c, r, c, legs),
        ]
    else:
        solution = [
            "思路（假设法）：假设全部是鸡，脚共 2×%d = %d 只。" % (h, 2 * h),
            "实际比假设多 %d - %d = %d 只脚，每把一只鸡换成兔多 2 只脚。" % (legs, 2 * h, legs - 2 * h),
            "所以兔有 %d ÷ 2 = %d 只，鸡有 %d - %d = %d 只。" % (legs - 2 * h, r, h, r, c),
            "答：鸡 %d 只，兔 %d 只。" % (c, r),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "鸡的只数", "value": str(c)},
                    {"label": "兔的只数", "value": str(r)}],
        "answer_display": "鸡 %d 只，兔 %d 只" % (c, r),
        "solution": solution,
    }


# ---------- 模板 2：相遇行程（4-9 年级） ----------

def _tpl_meet(grade):
    va = random.randint(45, 65)
    vb = random.randint(45, 75)
    t = random.randint(2, 4)
    s = (va + vb) * t
    q = ("甲、乙两地相距 %d 千米。一辆客车与一辆轿车同时从两地相向开出，"
         "客车每小时行 %d 千米，轿车每小时行 %d 千米。两车经过几小时相遇？"
         "相遇时客车行了多少千米？" % (s, va, vb))
    steps = [
        {"hint": "两车每小时一共行多少千米？", "answer": str(va + vb)},
        {"hint": "经过几小时两车相遇？", "answer": str(t)},
        {"hint": "相遇时客车行了多少千米？", "answer": str(va * t)},
    ]
    if grade >= 7:
        solution = [
            "思路：设经过 x 小时两车相遇。",
            "列方程：(%d + %d)x = %d" % (va, vb, s),
            "解得 x = %d，即经过 %d 小时相遇。" % (t, t),
            "客车路程：%d × %d = %d 千米。答：经过 %d 小时相遇，客车行了 %d 千米。"
            % (va, t, va * t, t, va * t),
        ]
    else:
        solution = [
            "思路：相遇时间 = 总路程 ÷ 速度和。",
            "速度和：%d + %d = %d（千米/时）" % (va, vb, va + vb),
            "相遇时间：%d ÷ %d = %d（小时）" % (s, va + vb, t),
            "客车路程：%d × %d = %d（千米）。答：经过 %d 小时相遇，客车行了 %d 千米。"
            % (va, t, va * t, t, va * t),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "相遇时间（小时）", "value": str(t)},
                    {"label": "客车行的路程（千米）", "value": str(va * t)}],
        "answer_display": "经过 %d 小时相遇；客车行了 %d 千米" % (t, va * t),
        "solution": solution,
    }


# ---------- 模板 3：工程问题（6-9 年级，北师大六上分数混合应用） ----------

# 合作天数 ab/(a+b) 为整数的天数组合
_WORK_PAIRS = [(3, 6), (6, 3), (4, 12), (12, 4), (5, 20), (20, 5),
               (6, 12), (12, 6), (10, 15), (15, 10), (8, 24), (24, 8)]


def _tpl_work(grade):
    a, b = random.choice(_WORK_PAIRS)
    t = a * b // (a + b)
    q = "一项工程，甲队单独做 %d 天完成，乙队单独做 %d 天完成。两队合作，多少天可以完成？" % (a, b)
    together = Fraction(1, a) + Fraction(1, b)
    steps = [
        {"hint": "把总工作量看作 1，甲队每天完成全部工程的几分之几？", "answer": "1/%d" % a},
        {"hint": "乙队每天完成全部工程的几分之几？", "answer": "1/%d" % b},
        {"hint": "两队合作每天完成全部工程的几分之几？", "answer": _frac_str(together)},
        {"hint": "两队合作多少天可以完成？", "answer": str(t)},
    ]
    if grade >= 7:
        solution = [
            "思路：设两队合作 x 天完成。",
            "列方程：(1/%d + 1/%d)x = 1，即 (%s)x = 1" % (a, b, _frac_str(together)),
            "解得 x = %d ÷ %s = %d 天。" % (1, _frac_str(together), t),
            "答：两队合作 %d 天可以完成。" % t,
        ]
    else:
        solution = [
            "思路：把总工作量看作单位 1。",
            "甲队每天完成 1/%d，乙队每天完成 1/%d。" % (a, b),
            "两队合作每天完成 1/%d + 1/%d = %s。" % (a, b, _frac_str(together)),
            "合作天数：1 ÷ %s = %d 天。答：两队合作 %d 天可以完成。"
            % (_frac_str(together), t, t),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "合作天数（天）", "value": str(t)}],
        "answer_display": "%d 天" % t,
        "solution": solution,
    }


# ---------- 模板 4：盈亏问题（3-9 年级） ----------

def _tpl_surplus(grade):
    while True:
        m = random.randint(4, 8)          # 第一种分法：每人 m 个
        n = random.randint(2, m - 1)     # 第二种分法：每人 n 个
        p = random.randint(0, m - 1)     # 第一种分法多出 p 个
        people = random.randint(8, 25)
        lack = people * (m - n) - p      # 第二种分法缺 lack 个
        if 1 <= lack <= 30:
            break
    total = people * m + p
    q = ("老师把一些苹果分给小朋友。如果每人分 %d 个，那么多出 %d 个；"
         "如果每人分 %d 个，那么还缺 %d 个。一共有多少个小朋友？这些苹果一共有多少个？"
         % (m, p, n, lack))
    steps = [
        {"hint": "第二种分法比第一种分法每人少分多少个？", "answer": str(m - n)},
        {"hint": "第一种分法多出的 %d 个，加上第二种分法缺少的 %d 个，总差额是多少个？" % (p, lack),
         "answer": str(p + lack)},
        {"hint": "小朋友一共有多少人？", "answer": str(people)},
        {"hint": "这些苹果一共有多少个？", "answer": str(total)},
    ]
    if grade >= 7:
        solution = [
            "思路：设有 x 个小朋友。",
            "苹果总数不变，列方程：%dx + %d = %dx - %d" % (m, p, n, lack),
            "移项：(%d - %d)x = %d + %d，即 %dx = %d" % (m, n, p, lack, m - n, p + lack),
            "解得 x = %d，苹果总数 = %d × %d + %d = %d 个。"
            "答：一共有 %d 个小朋友，苹果共 %d 个。" % (people, m, p, people, total, people, total),
        ]
    else:
        solution = [
            "思路（盈亏问题）：总差额 = 盈 + 亏。",
            "两次分法相差总数：%d + %d = %d 个。" % (p, lack, p + lack),
            "每人相差：%d - %d = %d 个，所以人数 = %d ÷ %d = %d 人。"
            % (m, n, m - n, p + lack, m - n, people),
            "苹果总数 = %d × %d + %d = %d 个。答：一共有 %d 个小朋友，苹果共 %d 个。"
            % (m, people, p, total, people, total),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "小朋友人数（人）", "value": str(people)},
                    {"label": "苹果总数（个）", "value": str(total)}],
        "answer_display": "%d 个小朋友；苹果共 %d 个" % (people, total),
        "solution": solution,
    }


# ---------- 模板 5：行程追及（4-9 年级） ----------

def _tpl_pursuit(grade):
    vb = random.randint(38, 55)          # 乙的速度
    diff = random.randint(6, 20)         # 速度差
    va = vb + diff                       # 甲的速度
    t = random.randint(2, 5)             # 追及时间
    d = diff * t                         # 出发时相差的路程
    q = ("乙骑车先出发，此时甲在乙后方 %d 千米处。乙每小时行 %d 千米，"
         "甲每小时行 %d 千米，两人沿同一条路同向而行。"
         "甲经过几小时追上乙？追上时甲共行了多少千米？" % (d, vb, va))
    steps = [
        {"hint": "甲每小时比乙多行多少千米？", "answer": str(diff)},
        {"hint": "甲需要追完相差的 %d 千米，经过几小时追上乙？" % d, "answer": str(t)},
        {"hint": "追上时甲共行了多少千米？", "answer": str(va * t)},
    ]
    if grade >= 7:
        solution = [
            "思路：设甲经过 x 小时追上乙。",
            "追上时甲比乙多行 %d 千米，列方程：(%d - %d)x = %d" % (d, va, vb, d),
            "解得 %dx = %d，x = %d，即经过 %d 小时追上。" % (diff, d, t, t),
            "甲的路程：%d × %d = %d 千米。答：经过 %d 小时追上乙，甲共行了 %d 千米。"
            % (va, t, va * t, t, va * t),
        ]
    else:
        solution = [
            "思路（追及问题）：追及时间 = 相差路程 ÷ 速度差。",
            "速度差：%d - %d = %d（千米/时）" % (va, vb, diff),
            "追及时间：%d ÷ %d = %d（小时）" % (d, diff, t),
            "甲的路程：%d × %d = %d 千米。答：经过 %d 小时追上乙，甲共行了 %d 千米。"
            % (va, t, va * t, t, va * t),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "追上所用时间（小时）", "value": str(t)},
                    {"label": "甲共行路程（千米）", "value": str(va * t)}],
        "answer_display": "经过 %d 小时追上乙；甲共行了 %d 千米" % (t, va * t),
        "solution": solution,
    }


# ---------- 模板 6：折扣百分数（6-9 年级，北师大六上百分数应用） ----------

def _tpl_discount(grade):
    while True:
        a = random.randint(20, 50) * 10      # 原价
        z = random.choice([9, 8, 7, 6])       # 打 z 折
        cur = Fraction(a * z, 10)            # 现价
        save = a - cur                       # 便宜的钱
        if cur.denominator == 1 and save.denominator == 1 and save > 0:
            break
    q = ("一件商品原价 %d 元，商店促销打 %d 折出售。"
         "现价是多少元？比原价便宜了多少元？" % (a, z))
    steps = [
        {"hint": "打 %d 折表示现价是原价的十分之 %d，现价是多少元？" % (z, z),
         "answer": _frac_str(cur)},
        {"hint": "比原价便宜了多少元？", "answer": _frac_str(save)},
    ]
    if grade >= 7:
        solution = [
            "思路：打 %d 折即现价 = 原价 × %d/10。" % (z, z),
            "现价：%d × %d/10 = %d 元。" % (a, z, cur),
            "便宜的钱数：%d - %d = %d 元。答：现价 %d 元，比原价便宜 %d 元。"
            % (a, cur, save, cur, save),
        ]
    else:
        solution = [
            "思路：打几折就是按原价的十分之几出售。",
            "现价：%d × %d/10 = %d 元。" % (a, z, cur),
            "便宜的钱数：%d - %d = %d 元。答：现价 %d 元，比原价便宜 %d 元。"
            % (a, cur, save, cur, save),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "现价（元）", "value": _frac_str(cur)},
                    {"label": "便宜的钱（元）", "value": _frac_str(save)}],
        "answer_display": "现价 %d 元，比原价便宜 %d 元" % (cur, save),
        "solution": solution,
    }


# ---------- 模板 7：浓度问题（6-9 年级） ----------

def _tpl_concentration(grade):
    while True:
        p1 = random.randint(5, 30)           # 甲含盐率（%）
        p2 = random.randint(5, 30)
        while p2 == p1:
            p2 = random.randint(5, 30)       # 乙含盐率（%）
        m1 = random.randint(1, 5) * 100       # 甲质量（克）
        m2 = random.randint(1, 5) * 100       # 乙质量（克）
        salt1 = Fraction(p1 * m1, 100)
        salt2 = Fraction(p2 * m2, 100)
        total_mass = m1 + m2
        pct = Fraction(100) * (salt1 + salt2) / total_mass   # 百分号前的数
        if (salt1.denominator == 1 and salt2.denominator == 1
                and pct.denominator == 1):
            break
    q = ("有甲、乙两杯盐水。甲杯 %d 克，含盐率 %d%%；乙杯 %d 克，含盐率 %d%%。"
         "把两杯倒进同一个容器里混合，混合后的含盐率是百分之几？" % (m1, p1, m2, p2))
    steps = [
        {"hint": "甲杯含盐多少克？", "answer": _frac_str(salt1)},
        {"hint": "乙杯含盐多少克？", "answer": _frac_str(salt2)},
        {"hint": "混合后盐水一共多少克？", "answer": str(total_mass)},
        {"hint": "混合后一共含盐多少克？", "answer": _frac_str(salt1 + salt2)},
        {"hint": "含盐率 = 盐 ÷ 盐水 × 100%，混合后的含盐率是百分之几（只填百分号前的数）？",
         "answer": _frac_str(pct)},
    ]
    if grade >= 7:
        solution = [
            "思路：设混合后含盐率为 x%。",
            "混合前后的盐量不变，列方程：(%d + %d)·x%% = %d + %d" % (m1, m2, p1 * m1 // 100, p2 * m2 // 100),
            "解得 x = %d。答：混合后的含盐率是 %d%%。" % (pct, pct),
        ]
    else:
        solution = [
            "思路：混合后含盐率 = 总盐量 ÷ 总质量 × 100%。",
            "甲杯含盐 %d × %d%% = %d 克，乙杯含盐 %d × %d%% = %d 克。"
            % (m1, p1, salt1, m2, p2, salt2),
            "混合后共含盐 %d + %d = %d 克，盐水共 %d 克。" % (salt1, salt2, salt1 + salt2, total_mass),
            "含盐率：%d ÷ %d = %d%%。答：混合后的含盐率是 %d%%。"
            % (salt1 + salt2, total_mass, pct, pct),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "混合后含盐率（百分号前的数）", "value": _frac_str(pct)}],
        "answer_display": "混合后的含盐率是 %d%%" % pct,
        "solution": solution,
    }


# ---------- 模板 8：利润问题（6-9 年级） ----------

def _tpl_profit(grade):
    while True:
        c = random.randint(10, 20) * 20       # 进价
        r = random.choice([20, 25, 50])       # 利润率（%）
        z = random.choice([9, 8, 7])          # 促销折扣
        p = c + Fraction(c * r, 100)          # 定价
        s = p * z / 10                        # 售价
        gain = s - c                          # 获利
        if (p.denominator == 1 and s.denominator == 1
                and gain.denominator == 1 and gain > 0):
            break
    q = ("商店购进一批商品，每件进价 %d 元，按 %d%% 的利润率定价。"
         "促销时打 %d 折出售，每件售价是多少元？每件仍可获利多少元？" % (c, r, z))
    steps = [
        {"hint": "每件定价多少元？", "answer": _frac_str(p)},
        {"hint": "打 %d 折后每件售价多少元？" % z, "answer": _frac_str(s)},
        {"hint": "每件仍可获利多少元？", "answer": _frac_str(gain)},
    ]
    if grade >= 7:
        solution = [
            "思路：定价 = 进价 × (1 + 利润率)，售价 = 定价 × 折扣。",
            "定价：%d × (1 + %d%%) = %d 元。" % (c, r, p),
            "售价：%d × %d/10 = %d 元。" % (p, z, s),
            "获利：%d - %d = %d 元。答：每件售价 %d 元，仍可获利 %d 元。"
            % (s, c, gain, s, gain),
        ]
    else:
        solution = [
            "思路：先按利润率算定价，再按折扣算售价，最后减进价得利润。",
            "每件利润：%d × %d%% = %d 元，定价 = %d + %d = %d 元。"
            % (c, r, c * r // 100, c, c * r // 100, p),
            "打 %d 折售价：%d × %d/10 = %d 元。" % (z, p, z, s),
            "获利：%d - %d = %d 元。答：每件售价 %d 元，仍可获利 %d 元。"
            % (s, c, gain, s, gain),
        ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "售价（元）", "value": _frac_str(s)},
                    {"label": "获利（元）", "value": _frac_str(gain)}],
        "answer_display": "每件售价 %d 元，仍可获利 %d 元" % (s, gain),
        "solution": solution,
    }


# ---------- 模板 9：乘加购物（3-6 年级，配合北师大三下乘法/混合运算单元） ----------

def _tpl_shopping(grade):
    """购物情境的乘加 / 连乘 / 乘减找零问题（答案与步骤均为整数）"""
    kind = random.randint(0, 2)
    if kind == 0:
        # 乘加：单价 × 数量 + 另一件的价钱
        x = random.randint(3, 12)          # 每包饼干价钱
        y = random.randint(2, 8)           # 包数
        z = random.randint(2, 15)          # 果汁价钱
        total = x * y + z
        q = ("超市里饼干每包 %d 元，小明买了 %d 包饼干，又买了一瓶 %d 元的果汁。"
             "他一共要付多少元？" % (x, y, z))
        steps = [
            {"hint": "买 %d 包饼干要多少元？" % y, "answer": str(x * y)},
            {"hint": "再加上果汁的价钱，一共要付多少元？", "answer": str(total)},
        ]
        solution = [
            "思路：先算饼干的价钱，再加上果汁的价钱。",
            "饼干：%d × %d = %d（元）" % (x, y, x * y),
            "一共：%d + %d = %d（元）。答：他一共要付 %d 元。" % (x * y, z, total, total),
        ]
        return {
            "question": q, "steps": steps,
            "answers": [{"label": "一共要付（元）", "value": str(total)}],
            "answer_display": "一共要付 %d 元" % total,
            "solution": solution,
        }
    if kind == 1:
        # 连乘：每箱盒数 × 每盒支数 × 箱数（北师大三下连乘问题）
        a = random.randint(6, 24)          # 每箱盒数
        b = random.randint(4, 12)          # 每盒支数
        c = random.randint(2, 5)           # 箱数
        total = a * b * c
        q = ("文具店购进一批铅笔，每箱 %d 盒，每盒 %d 支，一共购进 %d 箱。"
             "这批铅笔一共有多少支？" % (a, b, c))
        steps = [
            {"hint": "每箱有铅笔多少支？", "answer": str(a * b)},
            {"hint": "%d 箱一共有多少支？" % c, "answer": str(total)},
        ]
        solution = [
            "思路：先算每箱的支数，再算总支数。",
            "每箱：%d × %d = %d（支）" % (a, b, a * b),
            "一共：%d × %d = %d（支）。答：这批铅笔一共有 %d 支。" % (a * b, c, total, total),
        ]
        return {
            "question": q, "steps": steps,
            "answers": [{"label": "铅笔总支数（支）", "value": str(total)}],
            "answer_display": "一共有 %d 支" % total,
            "solution": solution,
        }
    # 乘减找零：付整百元，算找回的钱
    x = random.randint(12, 48)              # 单价
    y = random.randint(2, 6)                # 数量
    cost = x * y
    pay = (cost // 100 + 1) * 100          # 付整百元
    change = pay - cost
    q = ("一本图书 %d 元，学校买了 %d 本，付给售货员 %d 元。"
         "应找回多少元？" % (x, y, pay))
    steps = [
        {"hint": "买 %d 本书一共多少元？" % y, "answer": str(cost)},
        {"hint": "付了 %d 元，应找回多少元？" % pay, "answer": str(change)},
    ]
    solution = [
        "思路：先算总价，再用付出的钱减去总价。",
        "总价：%d × %d = %d（元）" % (x, y, cost),
        "找回：%d - %d = %d（元）。答：应找回 %d 元。" % (pay, cost, change, change),
    ]
    return {
        "question": q, "steps": steps,
        "answers": [{"label": "应找回（元）", "value": str(change)}],
        "answer_display": "应找回 %d 元" % change,
        "solution": solution,
    }


# ---------- 模板注册表 ----------

_TEMPLATES = [
    {"func": _tpl_chicken_rabbit, "lo": 5, "hi": 9, "name": "鸡兔同笼"},
    {"func": _tpl_meet, "lo": 4, "hi": 9, "name": "相遇行程"},
    {"func": _tpl_work, "lo": 6, "hi": 9, "name": "工程问题"},
    {"func": _tpl_surplus, "lo": 3, "hi": 9, "name": "盈亏问题"},
    {"func": _tpl_pursuit, "lo": 4, "hi": 9, "name": "行程追及"},
    {"func": _tpl_discount, "lo": 6, "hi": 9, "name": "折扣百分数"},
    {"func": _tpl_concentration, "lo": 6, "hi": 9, "name": "浓度问题"},
    {"func": _tpl_profit, "lo": 6, "hi": 9, "name": "利润问题"},
    {"func": _tpl_shopping, "lo": 3, "hi": 6, "name": "乘加购物"},
]


def generate_word(grade, count):
    """生成 count 道分步应用题：优先选不同模板，超出模板数时允许重复
    该年级没有可用模板（如 1-2 年级）时返回空列表，由调用方回退到题库。"""
    pool = [t for t in _TEMPLATES if t["lo"] <= grade <= t["hi"]]
    if not pool:
        return []
    picked = random.sample(pool, min(count, len(pool)))
    while len(picked) < count:
        picked.append(random.choice(pool))
    problems = []
    for tpl in picked:
        data = tpl["func"](grade)
        problems.append({
            "type": "word",
            "grade": grade,
            "category": "应用题-" + tpl["name"],
            "question": data["question"],
            "steps": data["steps"],
            # 最终答案值列表（对外隐藏，判题用）；标签对外可见，前端据此渲染输入框
            "answer": [a["value"] for a in data["answers"]],
            "answer_labels": [a["label"] for a in data["answers"]],
            "answer_display": data["answer_display"],
            "solution": data["solution"],
            "tolerance": 1e-9,
            "note": "",
        })
    return problems
