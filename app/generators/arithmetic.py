# -*- coding: utf-8 -*-
"""计算题与竖式题生成器（按年级难度，按北师大版教材册别）
覆盖范围：
- 1 年级：10/20 以内加减、100 以内不进位不退位加减
- 2 年级：100 以内加减、表内乘除、三位数笔算加减
- 3-4 年级：三位数加减、两三位数乘除、简便运算
- 5-6 年级：小数/分数四则、百分数、简便运算
- 7-9 年级：有理数混合运算、含乘方/开方的数值计算
竖式题：1-6 年级的加减乘除竖式（横式呈现，竖式由学生手写）

单元过滤：generate_calc / generate_vertical 支持可选 kinds 参数
（kind 名见 CALC_KINDS / VERT_KINDS 注册表），指定后只生成这些题型，
供设置页"教材单元出题范围"精确按单元出题；kinds 为 None 时保持
原有按册混合出题行为，混合分支也统一委托给 kind 函数，保证两种
路径的参数范围一致。
"""
import random
from fractions import Fraction


# ---------- 工具函数 ----------

def _fmt_answer(frac):
    """Fraction 转规范答案字符串：整数直出；分母只含 2/5 因子时输出精确小数；否则分数形式"""
    frac = Fraction(frac)
    if frac.denominator == 1:
        return str(frac.numerator)
    tmp = frac.denominator
    while tmp % 2 == 0:
        tmp //= 2
    while tmp % 5 == 0:
        tmp //= 5
    if tmp != 1:
        # 无限小数 → 保持分数形式
        return "%d/%d" % (frac.numerator, frac.denominator)
    sign = "-" if frac < 0 else ""
    a = abs(frac)
    twos = 0
    fives = 0
    v = a.denominator
    while v % 2 == 0:
        v //= 2
        twos += 1
    v = a.denominator
    while v % 5 == 0:
        v //= 5
        fives += 1
    k = max(twos, fives)
    digits = str(a.numerator * (10 ** k // a.denominator)).rjust(k + 1, "0")
    if k == 0:
        return sign + digits
    return sign + digits[:-k] + "." + digits[-k:]


def _rounded(frac, places=2):
    """四舍五入到指定小数位，返回答案字符串"""
    val = Fraction(frac)
    q = Fraction(1, 10 ** places)
    scaled = val / q
    n = scaled.numerator // scaled.denominator
    if scaled - n >= Fraction(1, 2):
        n += 1
    return _fmt_answer(Fraction(n) * q)


def _rand_nonzero(lo, hi):
    """随机非零整数"""
    while True:
        v = random.randint(lo, hi)
        if v != 0:
            return v


def _paren(v):
    """负数加括号显示，如 -3 → (-3)"""
    if v < 0:
        return "(-%d)" % abs(v)
    return str(v)


# ---------- 计算题单元级题型（供单元过滤精确出题） ----------

def _k_add10():
    """10 以内加法"""
    a = random.randint(1, 5)
    b = random.randint(1, 10 - a)
    return "%d + %d =" % (a, b), str(a + b)


def _k_sub10():
    """10 以内减法"""
    a = random.randint(3, 10)
    b = random.randint(1, a - 1)
    return "%d - %d =" % (a, b), str(a - b)


def _k_carry_add20():
    """20 以内进位加法"""
    a = random.randint(6, 9)
    b = random.randint(5, 9)
    return "%d + %d =" % (a, b), str(a + b)


def _k_borrow_sub20():
    """20 以内退位减法"""
    while True:
        a = random.randint(11, 18)
        b = random.randint(2, 9)
        if a % 10 < b:
            break
    return "%d - %d =" % (a, b), str(a - b)


def _k_add100_nc():
    """100 以内不进位加法"""
    while True:
        a = random.randint(13, 88)
        b = random.randint(11, 88)
        if a % 10 + b % 10 < 10 and a // 10 + b // 10 < 10:
            break
    return "%d + %d =" % (a, b), str(a + b)


def _k_sub100_nb():
    """100 以内不退位减法"""
    while True:
        a = random.randint(35, 99)
        b = random.randint(12, 88)
        if a > b and a % 10 >= b % 10:
            break
    return "%d - %d =" % (a, b), str(a - b)


def _k_add100_c():
    """100 以内进位加法（笔算）"""
    a = random.randint(11, 88)
    b = random.randint(11, 100 - a)
    return "%d + %d =" % (a, b), str(a + b)


def _k_sub100_b():
    """100 以内退位减法（笔算）"""
    a = random.randint(30, 99)
    b = random.randint(11, a - 1)
    return "%d - %d =" % (a, b), str(a - b)


def _k_mul_t25():
    """表内乘法（2-5 的乘法口诀）"""
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    return "%d × %d =" % (a, b), str(a * b)


def _k_mul_t69():
    """表内乘法（6-9 的乘法口诀）"""
    a = random.randint(6, 9)
    b = random.randint(2, 9)
    return "%d × %d =" % (a, b), str(a * b)


def _k_mul_table():
    """表内乘法复习（2-9 全口诀）"""
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    return "%d × %d =" % (a, b), str(a * b)


def _k_div_t():
    """表内除法（口诀求商）"""
    b = random.randint(2, 9)
    q = random.randint(2, 9)
    return "%d ÷ %d =" % (b * q, b), str(q)


def _k_add3():
    """三位数笔算加法"""
    a = random.randint(120, 879)
    b = random.randint(120, 999 - a)
    return "%d + %d =" % (a, b), str(a + b)


def _k_sub3():
    """三位数笔算减法"""
    a = random.randint(300, 999)
    b = random.randint(120, a - 100)
    return "%d - %d =" % (a, b), str(a - b)


def _k_mixed():
    """混合运算（乘加乘减 / 小括号）"""
    return _g34_mixed()


def _k_oral_muldiv():
    """口算乘除：整十整百数 × / ÷ 一位数"""
    base = random.randint(2, 9)
    k = random.choice([10, 100])
    b = random.randint(2, 9)
    if random.random() < 0.5:
        return "%d × %d =" % (base * k, b), str(base * k * b)
    return "%d ÷ %d =" % (base * k * b, base * k), str(b)


def _k_mul1():
    """多位数乘一位数"""
    a = random.randint(112, 989)
    b = random.randint(2, 9)
    return "%d × %d =" % (a, b), str(a * b)


def _k_div1():
    """两三位数除以一位数（整除）"""
    b = random.randint(2, 9)
    q = random.randint(21, 199)
    return "%d ÷ %d =" % (b * q, b), str(q)


def _k_mul2():
    """两位数乘两位数"""
    a = random.randint(12, 99)
    b = random.randint(12, 99)
    return "%d × %d =" % (a, b), str(a * b)


def _k_mul3():
    """三位数乘两位数"""
    a = random.randint(112, 989)
    b = random.randint(11, 39)
    return "%d × %d =" % (a, b), str(a * b)


def _k_div2():
    """两三位数除以两位数（整除）"""
    b = random.randint(11, 39)
    q = random.randint(11, 49)
    return "%d ÷ %d =" % (b * q, b), str(q)


def _k_simple():
    """简便运算（乘法结合律：25×4 / 125×8）"""
    k = random.randint(3, 25)
    if random.random() < 0.5:
        return "25 × %d × 4 =" % k, str(100 * k)
    return "125 × 8 × %d =" % k, str(1000 * k)


def _k_simple3():
    """简便运算（乘法分配律延伸：102×k / 99×k / 25×k×4）"""
    k = random.randint(11, 49)
    kind = random.randint(0, 2)
    if kind == 0:
        return "102 × %d =" % k, str(102 * k)
    if kind == 1:
        return "99 × %d =" % k, str(99 * k)
    return "25 × %d × 4 =" % k, str(100 * k)


def _k_dec_add():
    """小数加法（一位小数）"""
    fa = Fraction(random.randint(11, 89), 10)
    fb = Fraction(random.randint(11, 89), 10)
    return "%s + %s =" % (_fmt_answer(fa), _fmt_answer(fb)), _fmt_answer(fa + fb)


def _k_dec_sub():
    """小数减法（一位小数，结果为正）"""
    fa = Fraction(random.randint(40, 99), 10)
    fb = Fraction(random.randint(11, 39), 10)
    return "%s - %s =" % (_fmt_answer(fa), _fmt_answer(fb)), _fmt_answer(fa - fb)


def _k_dec_mul_int():
    """小数乘整数"""
    fa = Fraction(random.randint(11, 49), 10)
    b = random.randint(2, 9)
    return "%s × %d =" % (_fmt_answer(fa), b), _fmt_answer(fa * b)


def _k_dec_div():
    """小数除法（一位小数 ÷ 一位数，可能除不尽保留两位小数）"""
    return _dec_div_problem()


def _k_frac_add_diff():
    """异分母分数加法"""
    d1 = random.randint(2, 9)
    d2 = random.randint(2, 9)
    while d2 == d1:
        d2 = random.randint(2, 9)
    n1 = random.randint(1, d1 - 1)
    n2 = random.randint(1, d2 - 1)
    f = Fraction(n1, d1) + Fraction(n2, d2)
    return "%d/%d + %d/%d =" % (n1, d1, n2, d2), _fmt_answer(f)


def _k_frac_mul_mix():
    """分数乘法混合（分数 + 分数×整数）"""
    d1 = random.randint(2, 6)
    n1 = random.randint(1, d1 - 1)
    d2 = random.randint(2, 6)
    n2 = random.randint(1, d2 - 1)
    k = random.randint(2, 9)
    f = Fraction(n1, d1) + Fraction(n2, d2) * k
    return "%d/%d + %d/%d × %d =" % (n1, d1, n2, d2, k), _fmt_answer(f)


def _k_frac_mixed():
    """分数加减混合运算（异分母，结果为正）"""
    return _frac_mixed_problem()


def _k_pct_calc():
    """百分数计算：a × b% ="""
    while True:
        a = random.randint(20, 200)
        b = random.choice([10, 20, 25, 40, 50, 60, 75])
        if (a * b) % 100 == 0:
            break
    return "%d × %d%% =" % (a, b), str(a * b // 100)


# 计算题 kind 注册表：kind 名 → 生成函数（返回 (题面, 答案) 或 (题面, 答案, 容差, 提示)）
CALC_KINDS = {
    "add10": _k_add10, "sub10": _k_sub10,
    "carry_add20": _k_carry_add20, "borrow_sub20": _k_borrow_sub20,
    "add100_nc": _k_add100_nc, "sub100_nb": _k_sub100_nb,
    "add100_c": _k_add100_c, "sub100_b": _k_sub100_b,
    "mul_t25": _k_mul_t25, "mul_t69": _k_mul_t69,
    "mul_table": _k_mul_table, "div_t": _k_div_t,
    "add3": _k_add3, "sub3": _k_sub3, "mixed": _k_mixed,
    "oral_muldiv": _k_oral_muldiv,
    "mul1": _k_mul1, "div1": _k_div1, "mul2": _k_mul2,
    "mul3": _k_mul3, "div2": _k_div2,
    "simple": _k_simple, "simple3": _k_simple3,
    "dec_add": _k_dec_add, "dec_sub": _k_dec_sub,
    "dec_mul_int": _k_dec_mul_int, "dec_div": _k_dec_div,
    "frac_add_diff": _k_frac_add_diff, "frac_mul_mix": _k_frac_mul_mix,
    "frac_mixed": _k_frac_mixed, "pct_calc": _k_pct_calc,
}


# ---------- 计算题（小学部分：按册混合，委托给 kind 函数） ----------

def _calc_g1(volume=None):
    """一年级计算题（北师大 2024 新版教材进度）
    - 上册：10 以内加减法（第二、四单元）
    - 下册：20 以内进位加/退位减 + 100 以内不进位不退位加减
    - volume 为 None（自动/兼容模式）时保持 20 以内加减
    """
    if volume == 1:
        if random.random() < 0.5:
            return _k_add10()
        return _k_sub10()
    if volume == 2:
        r = random.random()
        if r < 0.3:
            return _k_carry_add20()
        if r < 0.6:
            return _k_borrow_sub20()
        if r < 0.8:
            return _k_add100_nc()
        return _k_sub100_nb()
    # 兼容模式（未指定册别）：20 以内加减
    if random.random() < 0.5:
        a = random.randint(1, 10)
        b = random.randint(1, 20 - a)
        return "%d + %d =" % (a, b), str(a + b)
    a = random.randint(2, 20)
    b = random.randint(1, a - 1)
    return "%d - %d =" % (a, b), str(a - b)


def _calc_g2(volume=None):
    """二年级计算题（北师大 2024 新版教材进度）
    - 上册：100 以内进退位加减（第一单元）、2-5/6-9 乘法口诀、口诀求商
    - 下册：三位数笔算加减（"大数加与减(一)"）、表内乘除复习
    - volume 为 None 时保持原有混合（100 以内加减 + 表内乘除）
    """
    if volume == 2:
        r = random.random()
        if r < 0.3:
            return _k_add3()
        if r < 0.55:
            return _k_sub3()
        if r < 0.75:
            return _k_mul_table()
        return _k_div_t()
    r = random.random()
    if r < 0.35:
        return _k_add100_c()
    if r < 0.65:
        return _k_sub100_b()
    if r < 0.8:
        return _k_mul_table()
    return _k_div_t()


def _calc_g34(grade, volume=None):
    """3-4 年级计算题（按北师大版教材进度）
    - 三上：大数加与减（三位数）、混合运算（乘加乘减、小括号）、口算乘除
    - 三下：两三位数乘一位数、两位数乘两位数、两三位数除以一位数
    - 四上：三位数乘两位数、两三位数除以两位数、运算律（简便运算）
    - 四下：小数的意义和加减法、小数乘法
    - volume 为 None 时保持原有全池混合
    """
    r = random.random()
    if grade == 3:
        if volume == 1:
            # 三上：三位数加减、混合运算、整十整百口算乘除
            if r < 0.3:
                return _k_add3()
            if r < 0.6:
                return _k_sub3()
            if r < 0.8:
                return _k_mixed()
            return _k_oral_muldiv()
        if volume == 2:
            # 三下：乘除笔算 + 三位数加减复习
            if r < 0.35:
                return _k_mul1()
            if r < 0.6:
                return _k_div1()
            if r < 0.8:
                return _k_mul2()
            if r < 0.9:
                return _k_add3()
            return _k_sub3()
        # 兼容模式：原有全池
        if r < 0.2:
            return _k_add3()
        if r < 0.4:
            return _k_sub3()
        if r < 0.6:
            return _k_mul1()
        if r < 0.8:
            return _k_div1()
        return _k_mixed()
    # ---- 四年级 ----
    if volume == 1:
        # 四上：三位数乘两位数、除以两位数、运算律简便、三位数加减
        if r < 0.35:
            return _k_mul3()
        if r < 0.6:
            return _k_div2()
        if r < 0.85:
            return _k_simple()
        if r < 0.925:
            return _k_add3()
        return _k_sub3()
    if volume == 2:
        # 四下：小数加减法、小数乘法 + 复习
        if r < 0.3:
            return _k_dec_add()
        if r < 0.55:
            return _k_dec_sub()
        if r < 0.8:
            return _k_dec_mul_int()
        if r < 0.9:
            return _k_mul3()
        return _k_div2()
    # 兼容模式：原有全池
    if r < 0.15:
        return _k_add3()
    if r < 0.3:
        return _k_sub3()
    if r < 0.5:
        return _k_mul3()
    if r < 0.65:
        return _k_div2()
    if r < 0.85:
        return _k_simple()
    if random.random() < 0.6:
        return _k_dec_add()
    return _k_dec_mul_int()


def _g34_mixed():
    """混合运算（三上第一单元）：乘加乘减 / 小括号"""
    if random.random() < 0.6:
        a = random.randint(12, 99)
        b = random.randint(2, 9)
        c = random.randint(2, 9)
        if random.random() < 0.5:
            return "%d + %d × %d =" % (a, b, c), str(a + b * c)
        prod = b * c
        d = random.randint(prod + 5, prod + 80)
        return "%d - %d × %d =" % (d, b, c), str(d - prod)
    a = random.randint(5, 20)
    b = random.randint(5, 20)
    c = random.randint(2, 9)
    return "(%d + %d) × %d =" % (a, b, c), str((a + b) * c)


def _dec_div_problem():
    """小数除法（北师大五上重点）：一位小数 ÷ 一位数
    可能除不尽 → 保留两位小数（容差放宽并加提示）。返回 (题面, 答案, 容差, 提示)
    """
    num = random.randint(11, 99)
    fa = Fraction(num, 10)
    b = random.randint(3, 9)
    q = fa / b
    ans = _fmt_answer(q)
    if "/" in ans:
        # 除不尽：四舍五入保留两位小数，容差放宽
        return ("%.1f ÷ %d =" % (num / 10.0, b), _rounded(q, 2), 0.005,
                "得数保留两位小数")
    return ("%.1f ÷ %d =" % (num / 10.0, b), ans, 1e-9, "")


def _frac_mixed_problem():
    """分数加减混合（北师大六上"分数混合运算"）：异分母加减混合，保证结果为正"""
    while True:
        d1 = random.randint(2, 9)
        d2 = random.randint(2, 9)
        d3 = random.randint(2, 9)
        if d2 == d1 or d3 == d1 or d3 == d2:
            continue
        n1 = random.randint(1, d1 - 1)
        n2 = random.randint(1, d2 - 1)
        n3 = random.randint(1, d3 - 1)
        f = Fraction(n1, d1) + Fraction(n2, d2) - Fraction(n3, d3)
        if f > 0:
            break
    return "%d/%d + %d/%d - %d/%d =" % (n1, d1, n2, d2, n3, d3), _fmt_answer(f)


def _calc_g56(grade, volume=None):
    """5-6 年级计算题（按北师大版教材进度）
    - 五上：小数除法（重点）
    - 五下：分数加减法（异分母）、分数乘法
    - 六上：分数混合运算、百分数
    - 六下：总复习（无新计算内容，全池混合）
    - volume 为 None 时保持原有全池混合
    """
    r = random.random()
    if grade == 5:
        if volume == 1:
            # 五上：小数除法为主 + 小数乘法/简便运算复习
            if r < 0.5:
                return _k_dec_div()
            if r < 0.7:
                return _k_dec_mul_int()
            if r < 0.85:
                return _k_dec_add()
            return _k_simple3()
        # 五下：异分母分数加减、分数乘法（含乘整数混合）
        if r < 0.5:
            return _k_frac_add_diff()
        return _k_frac_mul_mix()
    if grade == 6 and volume == 1:
        # 六上：分数混合运算、百分数、简便运算
        if r < 0.35:
            return _k_frac_mixed()
        if r < 0.65:
            return _k_pct_calc()
        return _k_simple3()
    # 六下总复习 / 兼容模式：全池
    if r < 0.2:
        return _k_dec_add()
    if r < 0.35:
        return _k_dec_mul_int()
    if r < 0.5:
        return _k_dec_div()
    if r < 0.65:
        return _k_frac_add_diff()
    if r < 0.8:
        return _k_frac_mul_mix()
    if r < 0.9:
        return _k_simple3()
    if grade == 6:
        return _k_pct_calc()
    return _k_dec_div()


# ---------- 计算题（初中部分：有理数混合运算） ----------

def _calc_g7():
    # a ± b × c，含负数
    a = _rand_nonzero(-9, 9)
    b = random.randint(2, 9)
    c = random.choice([random.randint(2, 9), random.randint(-9, -2)])
    op = random.choice(["+", "-"])
    if op == "+":
        ans = a + b * c
    else:
        ans = a - b * c
    return "%s %s %d × %s =" % (_paren(a), op, b, _paren(c)), str(ans)


def _calc_g8():
    r = random.random()
    if r < 0.5:
        # (a + b) × (c - d)
        a = _rand_nonzero(-9, 9)
        b = _rand_nonzero(-9, 9)
        c = _rand_nonzero(-9, 9)
        d = _rand_nonzero(-9, 9)
        ans = (a + b) * (c - d)
        return "(%s + %s) × (%s - %s) =" % (_paren(a), _paren(b), _paren(c), _paren(d)), str(ans)
    # 平方差：a² - b²
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    return "%d² - %d² =" % (a, b), str(a * a - b * b)


def _calc_g9():
    r = random.random()
    if r < 0.4:
        # √s + n³ 或 √s - n³
        k = random.randint(3, 12)
        n = random.choice([random.randint(2, 4), random.randint(-4, -2)])
        op = random.choice(["+", "-"])
        ans = k + n ** 3 if op == "+" else k - n ** 3
        return "√%d %s (%d)³ =" % (k * k, op, n), str(ans)
    if r < 0.7:
        # (m)² × (n) - p
        m = random.choice([random.randint(2, 5), random.randint(-5, -2)])
        n = _rand_nonzero(-9, 9)
        p = _rand_nonzero(-20, 20)
        ans = m * m * n - p
        return "(%d)² × %s - (%s) =" % (m, _paren(n), _paren(p)), str(ans)
    # √s1 - √s2
    k1 = random.randint(4, 15)
    k2 = random.randint(2, k1 - 1)
    return "√%d - √%d =" % (k1 * k1, k2 * k2), str(k1 - k2)


def _calc_category(grade, q):
    """根据年级与题面特征归类知识点（用于学情统计与弱点加权）"""
    if "%" in q:
        return "百分数"
    if "√" in q or "²" in q or "³" in q:
        return "乘方开方"
    if "/" in q:
        return "分数运算"
    if "." in q:
        return "小数运算"
    if ("102 ×" in q or "99 ×" in q or ("25 ×" in q and " × 4" in q)
            or "125 × 8" in q):
        return "简便运算"
    if grade == 7 or (grade == 8 and "+" in q and "-" in q):
        return "有理数混合运算"
    if "×" in q and ("+" in q or "-" in q):
        return "乘加乘减混合"
    if "×" in q:
        return "乘法"
    if "÷" in q:
        return "除法"
    if "+" in q:
        return "加法"
    return "减法"


def generate_calc(grade, volume=None, kinds=None):
    """生成一道计算题，返回题目 dict
    volume：1=上册 / 2=下册（按北师大教材册别出题），None=全池混合（兼容模式）
    kinds：单元过滤的题型名列表（CALC_KINDS 的键），指定后只从这些题型随机；
    含未知 kind 时忽略未知项；过滤后为空或 None 时按册混合出题。
    """
    tol = 1e-9
    note = ""
    if kinds:
        valid = [k for k in kinds if k in CALC_KINDS]
        if valid:
            res = CALC_KINDS[random.choice(valid)]()
            if len(res) == 4:
                q, a, tol, note = res
            else:
                q, a = res
            return {
                "type": "calc",
                "grade": grade,
                "category": _calc_category(grade, q),
                "question": q,
                "answer": a,
                "tolerance": tol,
                "note": note,
                "steps": [],
                "solution": [],
            }
    if grade <= 1:
        q, a = _calc_g1(volume)
    elif grade == 2:
        q, a = _calc_g2(volume)
    elif grade <= 4:
        q, a = _calc_g34(grade, volume)
    elif grade <= 6:
        res = _calc_g56(grade, volume)
        if len(res) == 4:
            q, a, tol, note = res
        else:
            q, a = res
    elif grade == 7:
        q, a = _calc_g7()
    elif grade == 8:
        q, a = _calc_g8()
    else:
        q, a = _calc_g9()
    return {
        "type": "calc",
        "grade": grade,
        "category": _calc_category(grade, q),
        "question": q,
        "answer": a,
        "tolerance": tol,
        "note": note,
        "steps": [],
        "solution": [],
    }


# ---------- 竖式题单元级题型 ----------

def _v_add10():
    """10 以内加法竖式"""
    a = random.randint(2, 7)
    b = random.randint(2, 10 - a)
    return "%d + %d =" % (a, b), str(a + b), "竖式加法"


def _v_sub10():
    """10 以内减法竖式"""
    a = random.randint(5, 10)
    b = random.randint(2, a - 1)
    return "%d - %d =" % (a, b), str(a - b), "竖式减法"


def _v_carry_add20():
    """20 以内进位加法竖式"""
    a = random.randint(6, 9)
    b = random.randint(5, 9)
    return "%d + %d =" % (a, b), str(a + b), "竖式加法"


def _v_borrow_sub20():
    """20 以内退位减法竖式"""
    while True:
        a = random.randint(11, 18)
        b = random.randint(2, 9)
        if a % 10 < b:
            break
    return "%d - %d =" % (a, b), str(a - b), "竖式减法"


def _v_add100_nc():
    """100 以内不进位加法竖式"""
    while True:
        a = random.randint(13, 88)
        b = random.randint(11, 88)
        if a % 10 + b % 10 < 10 and a // 10 + b // 10 < 10:
            break
    return "%d + %d =" % (a, b), str(a + b), "竖式加法"


def _v_sub100_nb():
    """100 以内不退位减法竖式"""
    while True:
        a = random.randint(35, 99)
        b = random.randint(12, 88)
        if a > b and a % 10 >= b % 10:
            break
    return "%d - %d =" % (a, b), str(a - b), "竖式减法"


def _v_add100_c():
    """100 以内进退位加法竖式（笔算）"""
    a = random.randint(23, 77)
    b = random.randint(23, 100 - a)
    return "%d + %d =" % (a, b), str(a + b), "竖式加法"


def _v_sub100_b():
    """100 以内退位减法竖式（笔算）"""
    a = random.randint(45, 99)
    b = random.randint(23, a - 10)
    return "%d - %d =" % (a, b), str(a - b), "竖式减法"


def _v_add3():
    """三位数加法竖式"""
    a = random.randint(120, 879)
    b = random.randint(120, 999 - a)
    return "%d + %d =" % (a, b), str(a + b), "竖式加法"


def _v_sub3():
    """三位数减法竖式"""
    a = random.randint(300, 999)
    b = random.randint(120, a - 100)
    return "%d - %d =" % (a, b), str(a - b), "竖式减法"


def _v_mul1():
    """多位数乘一位数竖式"""
    a = random.randint(102, 998)
    b = random.randint(2, 9)
    return "%d × %d =" % (a, b), str(a * b), "竖式乘法"


def _v_mul2():
    """两位数乘两位数竖式"""
    a = random.randint(12, 99)
    b = random.randint(12, 99)
    return "%d × %d =" % (a, b), str(a * b), "竖式乘法"


def _v_mul3():
    """三位数乘两位数竖式"""
    a = random.randint(112, 989)
    b = random.randint(12, 49)
    return "%d × %d =" % (a, b), str(a * b), "竖式乘法"


def _v_div_t():
    """表内除法竖式"""
    b = random.randint(2, 9)
    q = random.randint(2, 9)
    return "%d ÷ %d =" % (b * q, b), str(q), "竖式除法"


def _v_div1():
    """两三位数除以一位数竖式（整除）"""
    b = random.randint(2, 9)
    q = random.randint(21, 199)
    return "%d ÷ %d =" % (b * q, b), str(q), "竖式除法"


def _v_div2():
    """两三位数除以两位数竖式（整除）"""
    b = random.randint(11, 39)
    q = random.randint(11, 49)
    return "%d ÷ %d =" % (b * q, b), str(q), "竖式除法"


def _v_dec_add():
    """小数加法竖式"""
    fa = Fraction(random.randint(11, 89), 10)
    fb = Fraction(random.randint(11, 89), 10)
    return "%s + %s =" % (_fmt_answer(fa), _fmt_answer(fb)), \
        _fmt_answer(fa + fb), "竖式小数加法"


def _v_dec_sub():
    """小数减法竖式"""
    fa = Fraction(random.randint(40, 99), 10)
    fb = Fraction(random.randint(11, 39), 10)
    return "%s - %s =" % (_fmt_answer(fa), _fmt_answer(fb)), \
        _fmt_answer(fa - fb), "竖式小数减法"


def _v_dec_mul():
    """小数乘整数竖式"""
    fa = Fraction(random.randint(11, 49), 10)
    b = random.randint(2, 9)
    return "%s × %d =" % (_fmt_answer(fa), b), _fmt_answer(fa * b), "竖式小数乘法"


def _v_dec_div():
    """小数除法竖式（一位小数 ÷ 一位数，除数只含 2/5 因子保证商为精确小数）"""
    num = random.randint(11, 99)
    fa = Fraction(num, 10)
    b = random.choice([2, 4, 5])
    return "%.1f ÷ %d =" % (num / 10.0, b), _fmt_answer(fa / b), "竖式小数除法"


# 竖式题 kind 注册表：kind 名 → 生成函数（返回 (题面, 答案, 知识点)）
VERT_KINDS = {
    "v_add10": _v_add10, "v_sub10": _v_sub10,
    "v_carry_add20": _v_carry_add20, "v_borrow_sub20": _v_borrow_sub20,
    "v_add100_nc": _v_add100_nc, "v_sub100_nb": _v_sub100_nb,
    "v_add100_c": _v_add100_c, "v_sub100_b": _v_sub100_b,
    "v_add3": _v_add3, "v_sub3": _v_sub3,
    "v_mul1": _v_mul1, "v_mul2": _v_mul2, "v_mul3": _v_mul3,
    "v_div_t": _v_div_t, "v_div1": _v_div1, "v_div2": _v_div2,
    "v_dec_add": _v_dec_add, "v_dec_sub": _v_dec_sub,
    "v_dec_mul": _v_dec_mul, "v_dec_div": _v_dec_div,
}


def _vert_problem(grade, q_str, ans_str, cat):
    """组装竖式题 dict"""
    return {
        "type": "vertical",
        "grade": grade,
        "category": cat,
        "question": "（用竖式计算）" + q_str,
        "answer": ans_str,
        "tolerance": 1e-9,
        "note": "",
        "steps": [],
        "solution": [],
    }


# 3-6 年级竖式混合分支的 ops 名 → kind 名映射
_V_OPS = {
    "add": "v_add3", "sub": "v_sub3", "mul1": "v_mul1", "mul2": "v_mul2",
    "mul3": "v_mul3", "div1": "v_div1", "div2": "v_div2",
    "dec_add": "v_dec_add", "dec_sub": "v_dec_sub",
    "dec_mul": "v_dec_mul", "dec_div": "v_dec_div",
}


def generate_vertical(grade, volume=None, kinds=None):
    """生成一道竖式计算题（横式呈现，标注用竖式计算）——按北师大版教材进度
    - 1 年级：上册 10 以内加减竖式；下册 20 以内进退位 + 100 以内不进位不退位竖式
    - 2 年级：上册 100 以内进退位竖式；下册三位数笔算加减 + 表内除法竖式
    - 3 年级：上册三位数加减竖式；下册乘一位数、两位乘两位、除以一位数竖式
    - 4 年级：上册三位数乘两位数、除以两位数竖式；下册小数加减、小数乘法竖式
    - 5 年级：上册小数除法竖式（五上重点）为主；下册复习池
    - 6 年级：复习池（无新竖式内容）
    volume 为 None 时保持原有全池混合（兼容模式）
    kinds：单元过滤的题型名列表（VERT_KINDS 的键），用法同 generate_calc
    """
    if kinds:
        valid = [k for k in kinds if k in VERT_KINDS]
        if valid:
            q_str, ans_str, cat = VERT_KINDS[random.choice(valid)]()
            return _vert_problem(grade, q_str, ans_str, cat)
    if grade <= 1:
        if volume == 1:
            # 一上：10 以内加减
            if random.random() < 0.5:
                q_str, ans_str, cat = _v_add10()
            else:
                q_str, ans_str, cat = _v_sub10()
        elif volume == 2:
            # 一下：20 以内进退位 + 100 以内不进位不退位
            r = random.random()
            if r < 0.3:
                q_str, ans_str, cat = _v_carry_add20()
            elif r < 0.6:
                q_str, ans_str, cat = _v_borrow_sub20()
            elif r < 0.8:
                q_str, ans_str, cat = _v_add100_nc()
            else:
                q_str, ans_str, cat = _v_sub100_nb()
        else:
            # 兼容模式：20 以内加减（一上旧版/一下内容）
            if random.random() < 0.5:
                a = random.randint(5, 15)
                b = random.randint(4, 20 - a)
                q_str = "%d + %d =" % (a, b)
                ans_str, cat = str(a + b), "竖式加法"
            else:
                a = random.randint(12, 20)
                b = random.randint(3, 11)
                q_str = "%d - %d =" % (a, b)
                ans_str, cat = str(a - b), "竖式减法"
    elif grade <= 2:
        if volume == 2:
            # 二下：三位数笔算加减（"大数加与减(一)"）+ 表内除法竖式 + 100 以内复习
            r = random.random()
            if r < 0.3:
                q_str, ans_str, cat = _v_add3()
            elif r < 0.6:
                q_str, ans_str, cat = _v_sub3()
            elif r < 0.85:
                q_str, ans_str, cat = _v_div_t()
            else:
                q_str, ans_str, cat = _v_add100_c()
        else:
            # 二上：100 以内加减法（进退位笔算），和与差都不超过 100
            if random.random() < 0.5:
                q_str, ans_str, cat = _v_add100_c()
            else:
                q_str, ans_str, cat = _v_sub100_b()
    else:
        # 3-6 年级：先按册别选题型，再统一生成
        if grade == 3:
            if volume == 1:
                ops = ["add", "sub"]                    # 三上：三位数加减
            elif volume == 2:
                ops = ["mul1", "mul2", "div1", "add", "sub"]  # 三下：乘除笔算+复习
            else:
                ops = ["add", "sub", "mul1", "div1", "mul2"]
        elif grade == 4:
            if volume == 1:
                ops = ["mul3", "div2", "add", "sub"]    # 四上
            elif volume == 2:
                ops = ["dec_add", "dec_sub", "dec_mul", "mul3", "div2"]  # 四下小数
            else:
                ops = ["add", "sub", "mul3", "div2"]
        else:
            ops = ["dec_add", "dec_sub", "dec_mul", "dec_div", "mul3", "div2"]
            if grade == 5 and volume == 1:
                # 五上：小数除法竖式为主
                ops = ["dec_div", "dec_div", "dec_mul", "mul3", "div2"]
        kind = _V_OPS[random.choice(ops)]
        q_str, ans_str, cat = VERT_KINDS[kind]()
    return _vert_problem(grade, q_str, ans_str, cat)
