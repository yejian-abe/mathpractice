# -*- coding: utf-8 -*-
"""应用题题库生成器（按北师大版教材单元与常见易错题型组织）
- 每个年级一套模板池：低年级基础应用 + 各年级易错题型专项
- 三年级以上复用 word_problems 的经典模板（盈亏、相遇、鸡兔同笼等）
- 所有步骤答案与最终答案均为整数（小数/分数题除外，均为精确值）
- generate_bank(grade, count)：按模板轮转生成并按题干去重
"""
import random
from .word_problems import _TEMPLATES as _CLASSIC_TEMPLATES

# 人名池（用于扩充题面变化，保证去重后题量充足）
_NAMES = ["小明", "小红", "小刚", "小丽", "小华", "小芳", "乐乐", "淘气", "笑笑", "丁当"]


def _name():
    return random.choice(_NAMES)


# ================= 一年级（20 以内加减应用，北师大一上/一下） =================

def _w1_total():
    """求总数：a + b"""
    item = random.choice([("小鸟", "只"), ("蝴蝶", "只"), ("蜻蜓", "只"), ("鸽子", "只")])
    a = random.randint(3, 12)
    b = random.randint(1, 20 - a)
    total = a + b
    q = "树上原来有 %d 只%s，又飞来了 %d 只，现在树上一共有多少只%s？" % (a, item[0], b, item[0])
    return {
        "question": q,
        "steps": [{"hint": "飞来后一共有多少只？", "answer": str(total)}],
        "answers": [{"label": "一共（只）", "value": str(total)}],
        "answer_display": "一共 %d 只" % total,
        "solution": ["思路：飞来说明数量变多，用加法。",
                     "一共：%d + %d = %d（只）。答：现在一共有 %d 只%s。"
                     % (a, b, total, total, item[0])],
    }


def _w1_left():
    """求剩余：a - b"""
    item = random.choice([("苹果", "个"), ("草莓", "颗"), ("橘子", "个"), ("糖果", "颗")])
    a = random.randint(6, 20)
    b = random.randint(1, a - 2)
    left = a - b
    q = "%s买了 %d 个%s，吃掉了 %d 个，还剩下多少个%s？" % (_name(), a, item[0], b, item[0])
    return {
        "question": q,
        "steps": [{"hint": "吃掉后还剩多少个？", "answer": str(left)}],
        "answers": [{"label": "还剩（个）", "value": str(left)}],
        "answer_display": "还剩 %d 个" % left,
        "solution": ["思路：吃掉说明数量变少，用减法。",
                     "还剩：%d - %d = %d（个）。答：还剩下 %d 个%s。"
                     % (a, b, left, left, item[0])],
    }


def _w1_reverse():
    """逆向求原数（易错：见"剩"就减）"""
    item = random.choice([("苹果", "个"), ("糖果", "颗"), ("饼干", "块")])
    n = _name()
    eaten = random.randint(2, 9)
    left = random.randint(1, 9)
    total = eaten + left
    q = "%s吃掉了 %d 个%s，还剩下 %d 个。%s原来有多少个%s？" \
        % (n, eaten, item[0], left, n, item[0])
    return {
        "question": q,
        "steps": [{"hint": "原来的个数 = 吃掉的 + 剩下的，原来是多少个？", "answer": str(total)}],
        "answers": [{"label": "原来有（个）", "value": str(total)}],
        "answer_display": "原来有 %d 个" % total,
        "solution": ["思路（易错点）：已知吃掉的和剩下的，求原来的总数要用加法，不能见\"剩\"就减。",
                     "原来：%d + %d = %d（个）。答：原来有 %d 个%s。"
                     % (eaten, left, total, total, item[0])],
    }


def _w1_compare():
    """比多少（易错：误用加法）"""
    pair = random.choice([("苹果", "梨"), ("白兔", "灰兔"), ("红花", "黄花"), ("皮球", "毽子")])
    big = random.randint(8, 20)
    small = random.randint(2, big - 3)
    diff = big - small
    if random.random() < 0.5:
        q = "%s有 %d 个%s，%d 个%s。%s比%s多几个？" % (_name(), big, pair[0], small, pair[1],
                                                    pair[0], pair[1])
    else:
        q = "%s有 %d 个%s，%d 个%s。%s比%s少几个？" % (_name(), big, pair[0], small, pair[1],
                                                    pair[1], pair[0])
    return {
        "question": q,
        "steps": [{"hint": "求相差数用大数减小数，相差几个？", "answer": str(diff)}],
        "answers": [{"label": "相差（个）", "value": str(diff)}],
        "answer_display": "相差 %d 个" % diff,
        "solution": ["思路（易错点）：求\"多几个/少几个\"是求相差数，用减法，不要算成总数。",
                     "相差：%d - %d = %d（个）。答：相差 %d 个。" % (big, small, diff, diff)],
    }


def _w1_queue():
    """排队问题（易错：忘 +1 或重复数自己）"""
    n = _name()
    if random.random() < 0.5:
        front = random.randint(2, 6)
        behind = random.randint(2, 6)
        total = front + behind + 1
        q = "小朋友们排队，%s前面有 %d 人，后面有 %d 人，这一队一共有多少人？" % (n, front, behind)
        return {
            "question": q,
            "steps": [{"hint": "前面的人数 + 后面的人数 + %s自己，一共多少人？" % n,
                       "answer": str(total)}],
            "answers": [{"label": "一共（人）", "value": str(total)}],
            "answer_display": "一共 %d 人" % total,
            "solution": ["思路（易错点）：容易忘记把 %s 自己也算进去，要加 1。" % n,
                         "一共：%d + %d + 1 = %d（人）。答：这一队一共有 %d 人。"
                         % (front, behind, total, total)],
        }
    a = random.randint(2, 8)
    b = random.randint(2, 8)
    total = a + b - 1
    q = "小朋友们排队做操，从前面数，%s是第 %d 个；从后面数，他是第 %d 个。这一队一共有多少人？" % (n, a, b)
    return {
        "question": q,
        "steps": [{"hint": "%s被数了 2 次，要减 1，一共多少人？" % n, "answer": str(total)}],
        "answers": [{"label": "一共（人）", "value": str(total)}],
        "answer_display": "一共 %d 人" % total,
        "solution": ["思路（易错点）：从前面数和从后面数，%s 被数了 2 次，直接相加会多 1，要减 1。" % n,
                     "一共：%d + %d - 1 = %d（人）。答：这一队一共有 %d 人。"
                     % (a, b, total, total)],
    }


def _w1_chain():
    """连减：总量 - x - y"""
    total = random.randint(10, 20)
    x = random.randint(1, 6)
    y = random.randint(1, total - x - 1)
    left = total - x - y
    q = "%s有 %d 颗糖果，上午吃了 %d 颗，下午吃了 %d 颗，还剩下多少颗？" % (_name(), total, x, y)
    return {
        "question": q,
        "steps": [{"hint": "上午吃了以后还剩多少颗？", "answer": str(total - x)},
                   {"hint": "下午吃了以后还剩多少颗？", "answer": str(left)}],
        "answers": [{"label": "还剩（颗）", "value": str(left)}],
        "answer_display": "还剩 %d 颗" % left,
        "solution": ["思路：依次减去两次吃掉的颗数。",
                     "第一次剩：%d - %d = %d（颗），第二次剩：%d - %d = %d（颗）。"
                     "答：还剩 %d 颗。" % (total, x, total - x, total - x, y, left, left)],
    }


def _w1_pay():
    """购物付钱：找零 / 还差"""
    price = random.randint(3, 15)
    item = random.choice([("文具盒", "个"), ("故事书", "本"), ("皮球", "个"), ("水彩笔", "盒")])
    if random.random() < 0.5:
        pay = price + random.randint(1, 8)
        q = "一个%s %d 元，%s付了 %d 元，应找回多少元？" % (item[0], price, _name(), pay)
        ans = pay - price
        return {
            "question": q,
            "steps": [{"hint": "找回的钱 = 付出的钱 - 价钱，找回多少元？", "answer": str(ans)}],
            "answers": [{"label": "找回（元）", "value": str(ans)}],
            "answer_display": "找回 %d 元" % ans,
            "solution": ["思路：付的钱比价钱多的部分就是找回的钱。",
                         "找回：%d - %d = %d（元）。答：应找回 %d 元。" % (pay, price, ans, ans)],
        }
    have = random.randint(1, price - 1)
    q = "一个%s %d 元，%s只带了 %d 元，还差多少元才能买到？" % (item[0], price, _name(), have)
    ans = price - have
    return {
        "question": q,
        "steps": [{"hint": "还差的钱 = 价钱 - 带的钱，还差多少元？", "answer": str(ans)}],
        "answers": [{"label": "还差（元）", "value": str(ans)}],
        "answer_display": "还差 %d 元" % ans,
        "solution": ["思路：带的钱不够，差的部分用价钱减带的钱（易错：不要反过来减）。",
                     "还差：%d - %d = %d（元）。答：还差 %d 元。" % (price, have, ans, ans)],
    }


def _w1_bus():
    """加减混合：车上人数变化"""
    a = random.randint(5, 15)
    up = random.randint(1, 6)
    down = random.randint(1, a + up - 1)
    now = a + up - down
    q = "一辆公交车上原来有 %d 人，到站后上来了 %d 人，又下去了 %d 人，现在车上有多少人？" % (a, up, down)
    return {
        "question": q,
        "steps": [{"hint": "上来以后车上有多少人？", "answer": str(a + up)},
                   {"hint": "下去以后车上有多少人？", "answer": str(now)}],
        "answers": [{"label": "现在（人）", "value": str(now)}],
        "answer_display": "现在车上有 %d 人" % now,
        "solution": ["思路：上来加、下去减，按先后顺序计算。",
                     "上来后：%d + %d = %d（人），下去后：%d - %d = %d（人）。"
                     "答：现在车上有 %d 人。" % (a, up, a + up, a + up, down, now, now)],
    }


# ================= 二年级（表内乘除、100 以内加减、单位与时间，北师大二上/二下） =================

def _w2_mul():
    """乘法含义：每份数 × 份数"""
    item = random.choice([("饼干", "块"), ("牛奶", "盒"), ("橡皮", "块"), ("电池", "节")])
    per = random.randint(2, 9)
    rows = random.randint(2, 9)
    total = per * rows
    q = "超市里每盒有 %d 块%s，%s买了 %d 盒，一共买了多少块%s？" % (per, item[0], _name(), rows, item[0])
    return {
        "question": q,
        "steps": [{"hint": "求 %d 个 %d 是多少，一共多少块？" % (rows, per), "answer": str(total)}],
        "answers": [{"label": "一共（块）", "value": str(total)}],
        "answer_display": "一共 %d 块" % total,
        "solution": ["思路：每盒同样多，求几个几是多少，用乘法。",
                     "一共：%d × %d = %d（块）。答：一共买了 %d 块%s。"
                     % (per, rows, total, total, item[0])],
    }


def _w2_div():
    """平均分：总数 ÷ 份数"""
    per = random.randint(2, 9)
    rows = random.randint(2, 9)
    total = per * rows
    q = "老师把 %d 粒糖平均分给 %d 个小朋友，每个小朋友分得几粒？" % (total, rows)
    return {
        "question": q,
        "steps": [{"hint": "平均分用除法，每人几粒？", "answer": str(per)}],
        "answers": [{"label": "每人（粒）", "value": str(per)}],
        "answer_display": "每人 %d 粒" % per,
        "solution": ["思路：把总数平均分成几份，用除法。",
                     "每人：%d ÷ %d = %d（粒）。答：每个小朋友分得 %d 粒。" % (total, rows, per, per)],
    }


def _w2_times():
    """倍的含义（易错：逆向倍数误用乘法）"""
    k = random.randint(2, 9)
    s = random.randint(2, 9)
    big = k * s
    if random.random() < 0.5:
        q = "红花有 %d 朵，黄花的朵数是红花的 %d 倍，黄花有多少朵？" % (s, k)
        return {
            "question": q,
            "steps": [{"hint": "求一个数的几倍是多少，用乘法，黄花多少朵？", "answer": str(big)}],
            "answers": [{"label": "黄花（朵）", "value": str(big)}],
            "answer_display": "黄花有 %d 朵" % big,
            "solution": ["思路：求 %d 的 %d 倍是多少，用乘法。" % (s, k),
                         "黄花：%d × %d = %d（朵）。答：黄花有 %d 朵。" % (s, k, big, big)],
        }
    q = "黄花有 %d 朵，是红花的 %d 倍，红花有多少朵？" % (big, k)
    return {
        "question": q,
        "steps": [{"hint": "已知一个数的几倍是多少，求这个数用除法，红花多少朵？", "answer": str(s)}],
        "answers": [{"label": "红花（朵）", "value": str(s)}],
        "answer_display": "红花有 %d 朵" % s,
        "solution": ["思路（易错点）：已知黄花是红花的几倍、求红花朵数时，要\"除以倍数\"，不要用乘法。",
                     "红花：%d ÷ %d = %d（朵）。答：红花有 %d 朵。" % (big, k, s, s)],
    }


def _w2_judge():
    """加乘辨析（易错：不是\"几个几\"却用乘法）"""
    a = random.randint(3, 9)
    b = random.randint(3, 9)
    while b == a:
        b = random.randint(3, 9)
    if random.random() < 0.5:
        total = a + b
        q = ("植树时同学们种了两行树，第一行种了 %d 棵，第二行种了 %d 棵，"
             "两行一共种了多少棵树？" % (a, b))
        return {
            "question": q,
            "steps": [{"hint": "两行的棵数不一样多，能用乘法吗？一共多少棵？", "answer": str(total)}],
            "answers": [{"label": "一共（棵）", "value": str(total)}],
            "answer_display": "一共 %d 棵" % total,
            "solution": ["思路（易错点）：两行棵数不相同，不是\"几个几\"，不能用乘法，要用加法。",
                         "一共：%d + %d = %d（棵）。答：两行一共种了 %d 棵。" % (a, b, total, total)],
        }
    rows = random.randint(3, 9)
    per = random.randint(3, 9)
    total = per * rows
    q = "植树时同学们每行种 %d 棵树，种了 %d 行，一共种了多少棵树？" % (per, rows)
    return {
        "question": q,
        "steps": [{"hint": "求 %d 个 %d 是多少，一共多少棵？" % (rows, per), "answer": str(total)}],
        "answers": [{"label": "一共（棵）", "value": str(total)}],
        "answer_display": "一共 %d 棵" % total,
        "solution": ["思路：每行同样多，是\"几个几\"，用乘法。",
                     "一共：%d × %d = %d（棵）。答：一共种了 %d 棵。" % (per, rows, total, total)],
    }


def _w2_boat():
    """租船进一法（易错：忘记进一）"""
    per = random.randint(3, 6)
    qn = random.randint(3, 7)
    r = random.randint(1, per - 1)
    people = qn * per + r
    q = "%d 个小朋友去公园划船，每条船最多坐 %d 人，他们至少要租多少条船？" % (people, per)
    ans = qn + 1
    return {
        "question": q,
        "steps": [{"hint": "%d ÷ %d = %d 条……剩 %d 人，剩下的 %d 人也要坐船，至少要租几条？"
                   % (people, per, qn, r, r), "answer": str(ans)}],
        "answers": [{"label": "至少（条）", "value": str(ans)}],
        "answer_display": "至少要租 %d 条" % ans,
        "solution": ["思路（易错点）：有余数时，剩下的人也要坐船，船的条数要\"加 1\"（进一法）。",
                     "%d ÷ %d = %d（条）……%d（人），所以至少要租 %d + 1 = %d 条。"
                     "答：至少要租 %d 条船。" % (people, per, qn, r, qn, ans, ans)],
    }


def _w2_money():
    """人民币：找零 / 求和"""
    if random.random() < 0.5:
        price = random.randint(23, 97)
        item = random.choice(["书包", "台灯", "足球", "电风扇"])
        back = 100 - price
        q = "一个%s %d 元，妈妈付给售货员 100 元，应找回多少元？" % (item, price)
        return {
            "question": q,
            "steps": [{"hint": "找回 = 100 - 价钱，找回多少元？", "answer": str(back)}],
            "answers": [{"label": "找回（元）", "value": str(back)}],
            "answer_display": "找回 %d 元" % back,
            "solution": ["思路：付 100 元，找回的钱 = 100 元 - 价钱。",
                         "找回：100 - %d = %d（元）。答：应找回 %d 元。" % (price, back, back)],
        }
    p1 = random.randint(15, 60)
    p2 = random.randint(12, 100 - p1 - 1)
    total = p1 + p2
    q = "%s买一顶帽子 %d 元，一双运动鞋 %d 元，两样各买一件一共要多少元？" % (_name(), p1, p2)
    return {
        "question": q,
        "steps": [{"hint": "两件的价钱合起来，一共多少元？", "answer": str(total)}],
        "answers": [{"label": "一共（元）", "value": str(total)}],
        "answer_display": "一共 %d 元" % total,
        "solution": ["思路：求两件商品的总价，用加法。",
                     "一共：%d + %d = %d（元）。答：一共要 %d 元。" % (p1, p2, total, total)],
    }


def _w2_time():
    """经过时间（易错：满 60 分要向小时进 1）"""
    h1 = random.randint(7, 10)
    m1 = random.choice([0, 10, 20, 30, 40, 50])
    dur = random.choice([10, 20, 30, 40, 50])
    m2 = m1 + dur
    h2 = h1
    if m2 >= 60:
        m2 -= 60
        h2 += 1
    q = ("一节课从 %d 时 %d 分开始，上了 %d 分钟，下课时间是几时几分？"
         % (h1, m1, dur))
    return {
        "question": q,
        "steps": [{"hint": "%d 分 + %d 分 = %d 分，满 60 分要换成 1 小时。下课是几时几分？"
                   % (m1, dur, m1 + dur), "answer": "%d时%d分" % (h2, m2)}],
        "answers": [{"label": "下课（时）", "value": str(h2)},
                    {"label": "下课（分）", "value": str(m2)}],
        "answer_display": "下课时间是 %d 时 %d 分" % (h2, m2),
        "solution": ["思路（易错点）：分与分相加，满 60 分要向小时进 1。",
                     "%d 分 + %d 分 = %d 分 = %d 时 %d 分。"
                     "答：下课时间是 %d 时 %d 分。"
                     % (m1, dur, m1 + dur, h2, m2, h2, m2)],
    }


def _w2_len():
    """长度单位（易错：进率 100 / 比一个数短用加还是减）"""
    if random.random() < 0.5:
        m = random.randint(1, 5)
        cm = random.randint(1, 99)
        total = m * 100 + cm
        q = "一根绳子长 %d 米 %d 厘米，这根绳子一共长多少厘米？" % (m, cm)
        return {
            "question": q,
            "steps": [{"hint": "1 米 = 100 厘米，先把 %d 米化成多少厘米？" % m,
                       "answer": str(m * 100)},
                      {"hint": "再合上 %d 厘米，一共多少厘米？" % cm, "answer": str(total)}],
            "answers": [{"label": "一共（厘米）", "value": str(total)}],
            "answer_display": "一共长 %d 厘米" % total,
            "solution": ["思路（易错点）：米与厘米之间的进率是 100。",
                         "%d 米 = %d 厘米，合起来一共 %d + %d = %d 厘米。"
                         "答：这根绳子长 %d 厘米。" % (m, m * 100, m * 100, cm, total, total)],
        }
    x = random.randint(12, 40)
    y = random.randint(3, 10)
    pen = x + y
    q = "一支铅笔长 %d 厘米，比一支钢笔短 %d 厘米，这支钢笔长多少厘米？" % (x, y)
    return {
        "question": q,
        "steps": [{"hint": "钢笔比铅笔长，求钢笔的长度用加法还是减法？", "answer": str(pen)}],
        "answers": [{"label": "钢笔（厘米）", "value": str(pen)}],
        "answer_display": "钢笔长 %d 厘米" % pen,
        "solution": ["思路（易错点）：\"铅笔比钢笔短\"说明钢笔更长，求钢笔用加法。",
                     "钢笔：%d + %d = %d（厘米）。答：这支钢笔长 %d 厘米。" % (x, y, pen, pen)],
    }


def _w2_twostep():
    """两步应用：先求比多（少）的数，再求总和"""
    a = random.randint(30, 90)
    b = random.randint(5, 40)
    b2 = a + b
    total = a + b2
    q = ("图书角有故事书 %d 本，科技书比故事书多 %d 本。科技书有多少本？"
         "两种书一共有多少本？" % (a, b))
    return {
        "question": q,
        "steps": [{"hint": "科技书比故事书多，科技书有多少本？", "answer": str(b2)},
                  {"hint": "两种书一共有多少本？", "answer": str(total)}],
        "answers": [{"label": "科技书（本）", "value": str(b2)},
                    {"label": "一共（本）", "value": str(total)}],
        "answer_display": "科技书 %d 本，两种书一共 %d 本" % (b2, total),
        "solution": ["思路：先求科技书的本数（比故事书多用加法），再求两种书的总和。",
                     "科技书：%d + %d = %d（本）。" % (a, b, b2),
                     "一共：%d + %d = %d（本）。答：科技书 %d 本，两种书一共 %d 本。"
                     % (a, b2, total, b2, total)],
    }


# ================= 三年级（周长、里程表、归一归总、时间、质量、面积、分数初步） =================

def _w3_perimeter():
    """周长应用（北师大三上）"""
    kind = random.randint(0, 2)
    if kind == 0:
        length = random.randint(6, 30)
        width = random.randint(4, length - 2)
        c = 2 * (length + width)
        q = "一个长方形的长是 %d 厘米，宽是 %d 厘米，它的周长是多少厘米？" % (length, width)
        return {
            "question": q,
            "steps": [{"hint": "长 + 宽 = %d（厘米）" % (length + width),
                       "answer": str(length + width)},
                      {"hint": "周长 =（长 + 宽）× 2，周长是多少？", "answer": str(c)}],
            "answers": [{"label": "周长（厘米）", "value": str(c)}],
            "answer_display": "周长是 %d 厘米" % c,
            "solution": ["思路：长方形周长 =（长 + 宽）× 2。",
                         "（%d + %d）× 2 = %d（厘米）。答：周长是 %d 厘米。"
                         % (length, width, c, c)],
        }
    if kind == 1:
        side = random.randint(5, 25)
        c = 4 * side
        q = "一个正方形的边长是 %d 厘米，它的周长是多少厘米？" % side
        return {
            "question": q,
            "steps": [{"hint": "正方形周长 = 边长 × 4，周长是多少？", "answer": str(c)}],
            "answers": [{"label": "周长（厘米）", "value": str(c)}],
            "answer_display": "周长是 %d 厘米" % c,
            "solution": ["思路：正方形周长 = 边长 × 4。",
                         "%d × 4 = %d（厘米）。答：周长是 %d 厘米。" % (side, c, c)],
        }
    length = random.randint(8, 30)
    width = random.randint(3, length - 3)
    fence = length + 2 * width
    q = ("王爷爷用篱笆靠墙围一块长方形菜地（长边靠墙），菜地长 %d 米，宽 %d 米，"
         "至少需要篱笆多少米？" % (length, width))
    return {
        "question": q,
        "steps": [{"hint": "长边靠墙不用篱笆，只有 1 条长和 2 条宽需要篱笆。",
                   "answer": str(fence)}],
        "answers": [{"label": "篱笆（米）", "value": str(fence)}],
        "answer_display": "至少需要篱笆 %d 米" % fence,
        "solution": ["思路（易错点）：长边靠墙时，篱笆 = 1 条长 + 2 条宽，不要按四边都围来算。",
                     "篱笆：%d + %d × 2 = %d（米）。答：至少需要篱笆 %d 米。"
                     % (length, width, fence, fence)],
    }


def _w3_unit_perimeter():
    """周长单位陷阱（易错：单位不统一直接相加减）"""
    dm = random.randint(2, 9)
    cm = random.randint(3, 9)
    length = dm * 10
    c = 2 * (length + cm)
    q = "一个长方形的长是 %d 分米，宽是 %d 厘米，它的周长是多少厘米？" % (dm, cm)
    return {
        "question": q,
        "steps": [{"hint": "先把长化单位：1 分米 = 10 厘米，%d 分米 = 多少厘米？" % dm,
                   "answer": str(length)},
                  {"hint": "长和宽的单位统一后再算周长，周长是多少厘米？", "answer": str(c)}],
        "answers": [{"label": "周长（厘米）", "value": str(c)}],
        "answer_display": "周长是 %d 厘米" % c,
        "solution": ["思路（易错点）：长和宽的单位不相同，必须先统一单位再计算。",
                     "%d 分米 = %d 厘米，周长 =（%d + %d）× 2 = %d（厘米）。"
                     "答：周长是 %d 厘米。" % (dm, length, length, cm, c, c)],
    }


def _w3_odometer():
    """里程表问题（易错：用起点里程相加减）"""
    if random.random() < 0.5:
        x = random.randint(31200, 98000)
        d = random.randint(120, 950)
        y = x + d
        q = ("一辆汽车从甲地出发时，里程表的读数是 %d 千米；到达乙地时，"
             "里程表的读数是 %d 千米。甲、乙两地相距多少千米？" % (x, y))
        return {
            "question": q,
            "steps": [{"hint": "两地的距离 = 到达读数 - 出发读数，相距多少千米？", "answer": str(d)}],
            "answers": [{"label": "相距（千米）", "value": str(d)}],
            "answer_display": "相距 %d 千米" % d,
            "solution": ["思路（易错点）：里程表读数是累计里程，两地距离 = 两次读数的差。",
                         "%d - %d = %d（千米）。答：甲、乙两地相距 %d 千米。" % (y, x, d, d)],
        }
    x = random.randint(21000, 88000)
    d = random.randint(150, 900)
    y = x + d
    q = "一辆汽车出发时里程表读数是 %d 千米，行驶了 %d 千米后到达，此时读数是多少千米？" % (x, d)
    return {
        "question": q,
        "steps": [{"hint": "到达读数 = 出发读数 + 行驶路程，读数是多少？", "answer": str(y)}],
        "answers": [{"label": "读数（千米）", "value": str(y)}],
        "answer_display": "读数是 %d 千米" % y,
        "solution": ["思路：里程表是累计读数，行驶的路程要加上去。",
                     "%d + %d = %d（千米）。答：此时读数是 %d 千米。" % (x, d, y, y)],
    }


def _w3_guiyi():
    """归一问题"""
    per = random.randint(4, 15)
    n1 = random.randint(3, 9)
    n2 = random.randint(3, 9)
    while n2 == n1:
        n2 = random.randint(3, 9)
    t1 = per * n1
    t2 = per * n2
    q = "%d 箱苹果一共有 %d 个，照这样计算，%d 箱苹果一共有多少个？" % (n1, t1, n2)
    return {
        "question": q,
        "steps": [{"hint": "先求 1 箱有多少个：每箱多少个？", "answer": str(per)},
                  {"hint": "再求 %d 箱有多少个？" % n2, "answer": str(t2)}],
        "answers": [{"label": "一共（个）", "value": str(t2)}],
        "answer_display": "%d 箱一共有 %d 个" % (n2, t2),
        "solution": ["思路（归一问题）：先求出单一量（每箱的个数），再求总量。",
                     "每箱：%d ÷ %d = %d（个），%d 箱：%d × %d = %d（个）。"
                     "答：%d 箱苹果一共有 %d 个。" % (t1, n1, per, n2, per, n2, t2, n2, t2)],
    }


def _w3_guizong():
    """归总问题"""
    while True:
        per = random.randint(3, 9)
        n1 = random.randint(3, 9)
        total = per * n1
        divs = [d for d in range(2, 10) if d != per and total % d == 0]
        if divs:
            break
    per2 = random.choice(divs)
    n2 = total // per2
    q = ("一批苹果共 %d 个，每箱装 %d 个正好装完。如果每箱改装 %d 个，"
         "需要多少个箱子？" % (total, per, per2))
    return {
        "question": q,
        "steps": [{"hint": "苹果总数不变，用总数 ÷ 每箱个数，需要多少个箱子？", "answer": str(n2)}],
        "answers": [{"label": "箱子（个）", "value": str(n2)}],
        "answer_display": "需要 %d 个箱子" % n2,
        "solution": ["思路（归总问题）：总数不变，箱子数 = 总数 ÷ 每箱装的个数。",
                     "%d ÷ %d = %d（个）。答：需要 %d 个箱子。" % (total, per2, n2, n2)],
    }


def _w3_sleep():
    """经过时间（跨日，易错：跨过半夜直接相减）"""
    if random.random() < 0.5:
        sh = random.randint(20, 23)
        eh = random.randint(5, 8)
        hours = 24 - sh + eh
        q = "%s晚上 %d 时睡觉，第二天早上 %d 时起床，他一共睡了多少小时？" % (_name(), sh, eh)
        return {
            "question": q,
            "steps": [{"hint": "先算到半夜 24 时经过几小时，再算到起床又经过几小时。",
                       "answer": str(hours)}],
            "answers": [{"label": "睡眠（小时）", "value": str(hours)}],
            "answer_display": "睡了 %d 小时" % hours,
            "solution": ["思路（易错点）：跨过半夜不能用\"起床时间 - 睡觉时间\"直接相减。",
                         "到 24 时经过 %d 小时，24 时到早上 %d 时经过 %d 小时，"
                         "一共睡了 %d 小时。答：他一共睡了 %d 小时。"
                         % (24 - sh, eh, eh, hours, hours)],
        }
    h1 = random.randint(1, 6)
    m1 = random.choice([0, 30])
    dh = random.randint(1, 4)
    dm = random.choice([0, 30])
    h2 = h1 + dh + (m1 + dm) // 60   # 满 60 分向小时进 1
    m2 = (m1 + dm) % 60
    q = ("一列火车 %d 时 %d 分从甲站开出，%d 时 %d 分到达乙站，"
         "路上用了多长时间？" % (h1, m1, h2, m2))
    return {
        "question": q,
        "steps": [{"hint": "小时部分相差多少小时？", "answer": str(dh)},
                  {"hint": "分钟部分相差多少分钟？", "answer": str(dm)}],
        "answers": [{"label": "用时（小时）", "value": str(dh)},
                    {"label": "用时（分钟）", "value": str(dm)}],
        "answer_display": "用了 %d 小时 %d 分钟" % (dh, dm),
        "solution": ["思路：分别算出小时差和分钟差。",
                     "%d 时 - %d 时 = %d 小时，%d 分 - %d 分 = %d 分钟。"
                     "答：路上用了 %d 小时 %d 分钟。"
                     % (h2, h1, dh, m2, m1, dm, dh, dm)],
    }


def _w3_mass():
    """质量单位（易错：吨与千克进率 1000）"""
    if random.random() < 0.5:
        t = random.randint(2, 9)
        kg = t * 1000
        q = "一头大象重 %d 吨，合多少千克？" % t
        return {
            "question": q,
            "steps": [{"hint": "1 吨 = 1000 千克，%d 吨合多少千克？" % t, "answer": str(kg)}],
            "answers": [{"label": "重量（千克）", "value": str(kg)}],
            "answer_display": "合 %d 千克" % kg,
            "solution": ["思路（易错点）：吨与千克之间的进率是 1000。",
                         "%d 吨 = %d × 1000 = %d 千克。答：合 %d 千克。" % (t, t, kg, kg)],
        }
    t = random.randint(2, 9)
    k = random.randint(1, t * 2 - 1) * 500
    left = t * 1000 - k
    q = "一批货物共 %d 吨，运走了 %d 千克，还剩下多少千克？" % (t, k)
    return {
        "question": q,
        "steps": [{"hint": "先把 %d 吨化成多少千克？" % t, "answer": str(t * 1000)},
                  {"hint": "再减去运走的千克数，还剩多少千克？", "answer": str(left)}],
        "answers": [{"label": "还剩（千克）", "value": str(left)}],
        "answer_display": "还剩 %d 千克" % left,
        "solution": ["思路（易错点）：吨与千克混在同一个题里，要先把吨化成千克再相减。",
                     "%d 吨 = %d 千克，还剩 %d - %d = %d 千克。"
                     "答：还剩下 %d 千克。" % (t, t * 1000, t * 1000, k, left, left)],
    }


def _w3_liandiv():
    """连除应用"""
    per = random.randint(3, 9)
    shelves = random.randint(2, 6)
    layers = random.randint(2, 6)
    total = per * shelves * layers
    q = ("图书馆新进 %d 本图书，平均放在 %d 个书架上，每个书架有 %d 层，"
         "平均每层放多少本？" % (total, shelves, layers))
    return {
        "question": q,
        "steps": [{"hint": "每个书架放多少本？", "answer": str(per * layers)},
                  {"hint": "每个书架的每层放多少本？", "answer": str(per)}],
        "answers": [{"label": "每层（本）", "value": str(per)}],
        "answer_display": "平均每层放 %d 本" % per,
        "solution": ["思路：可以先用总数 ÷ 书架数，再除以层数（连除）。",
                     "每架：%d ÷ %d = %d（本），每层：%d ÷ %d = %d（本）。"
                     "答：平均每层放 %d 本。"
                     % (total, shelves, per * layers, per * layers, layers, per, per)],
    }


def _w3_area():
    """面积应用（易错：周长与面积混淆）"""
    length = random.randint(4, 15)
    width = random.randint(3, 12)
    area = length * width
    if random.random() < 0.5:
        q = "一块长方形菜地长 %d 米，宽 %d 米，它的面积是多少平方米？" % (length, width)
        return {
            "question": q,
            "steps": [{"hint": "长方形面积 = 长 × 宽，面积是多少？", "answer": str(area)}],
            "answers": [{"label": "面积（平方米）", "value": str(area)}],
            "answer_display": "面积是 %d 平方米" % area,
            "solution": ["思路（易错点）：面积是面的大小，用长 × 宽；不要算成周长。",
                         "面积：%d × %d = %d（平方米）。答：面积是 %d 平方米。"
                         % (length, width, area, area)],
        }
    q = "一块长方形菜地的面积是 %d 平方米，长 %d 米，宽是多少米？" % (area, length)
    return {
        "question": q,
        "steps": [{"hint": "宽 = 面积 ÷ 长，宽是多少米？", "answer": str(width)}],
        "answers": [{"label": "宽（米）", "value": str(width)}],
        "answer_display": "宽是 %d 米" % width,
        "solution": ["思路：已知面积和长，求宽用除法（面积 ÷ 长 = 宽）。",
                     "宽：%d ÷ %d = %d（米）。答：宽是 %d 米。" % (area, length, width, width)],
    }


def _w3_fraction():
    """分数初步认识"""
    n = random.randint(2, 9)
    item = random.choice(["一个西瓜", "一块月饼", "一张饼"])
    q = "把%s平均分给 %d 个小朋友，每人分得它的几分之几？" % (item, n)
    return {
        "question": q,
        "steps": [{"hint": "把一个整体平均分成几份，每份就是它的几分之一，每人分得几分之几？",
                   "answer": "1/%d" % n}],
        "answers": [{"label": "每人分得", "value": "1/%d" % n}],
        "answer_display": "每人分得它的 1/%d" % n,
        "solution": ["思路：把一个整体平均分成 %d 份，每份就是这个整体的 1/%d。" % (n, n),
                     "答：每人分得它的 1/%d。" % n],
    }


# ================= 四年级（植树、平均数、和差、单价速度、负数、近似数、小数） =================

def _w4_plant():
    """植树问题（易错：两端栽要加 1 / 两端不栽要减 1）"""
    gap = random.randint(2, 10)
    n = random.randint(4, 25)
    total = gap * n
    kind = random.randint(0, 2)
    if kind == 0:
        trees = n + 1
        q = ("一条小路长 %d 米，在路的一侧从头到尾每隔 %d 米栽一棵树"
             "（两端都栽），一共要栽多少棵树？" % (total, gap))
        key = "两端都栽时，棵数 = 间隔数 + 1"
    elif kind == 1:
        trees = n
        q = ("一条小路长 %d 米，在路的一侧每隔 %d 米栽一棵树"
             "（一端靠墙只栽一端），一共要栽多少棵树？" % (total, gap))
        key = "只栽一端时，棵数 = 间隔数"
    else:
        trees = n - 1
        q = ("两栋楼之间的小路长 %d 米，每隔 %d 米栽一棵树"
             "（两端紧靠楼，都不能栽），一共能栽多少棵树？" % (total, gap))
        key = "两端都不栽时，棵数 = 间隔数 - 1"
    return {
        "question": q,
        "steps": [{"hint": "先求间隔数：%d ÷ %d = 多少个间隔？" % (total, gap), "answer": str(n)},
                  {"hint": "%s，一共栽多少棵树？" % key, "answer": str(trees)}],
        "answers": [{"label": "棵数（棵）", "value": str(trees)}],
        "answer_display": "一共栽 %d 棵树" % trees,
        "solution": ["思路（易错点）：%s。" % key,
                     "间隔数：%d ÷ %d = %d（个），棵数 = %d。答：一共栽 %d 棵树。"
                     % (total, gap, n, trees, trees)],
    }


def _w4_avg():
    """平均数（易错：平均数不等于中间那个数）"""
    kind = random.randint(0, 1)
    n = _name()
    if kind == 0:
        avg = random.randint(78, 97)
        offs = [random.randint(-5, 5) for _ in range(3)]
        s = sum(offs)
        scores = [avg + o for o in offs] + [avg - s]
        while min(scores) < 60:
            avg += 3
            scores = [sc + 3 for sc in scores]
        total = sum(scores)
        q = "%s前四次数学测验的成绩分别是 %d 分、%d 分、%d 分、%d 分，他这四次的平均分是多少？" \
            % (n, scores[0], scores[1], scores[2], scores[3])
        return {
            "question": q,
            "steps": [{"hint": "先求四次的总分，一共多少分？", "answer": str(total)},
                      {"hint": "总分 ÷ 4，平均分是多少？", "answer": str(avg)}],
            "answers": [{"label": "平均分（分）", "value": str(avg)}],
            "answer_display": "平均分是 %d 分" % avg,
            "solution": ["思路（易错点）：平均数 = 总数 ÷ 个数，不能只看某一次的成绩。",
                     "总分：%d + %d + %d + %d = %d（分）。"
                     % (scores[0], scores[1], scores[2], scores[3], total),
                     "平均分：%d ÷ 4 = %d（分）。答：平均分是 %d 分。"
                     % (total, avg, avg)],
        }
    cnt = random.choice([4, 5])
    avg = random.randint(60, 95)
    total = avg * cnt
    q = "%d 名同学的身高加起来一共是 %d 厘米，他们的平均身高是多少厘米？" % (cnt, total)
    return {
        "question": q,
        "steps": [{"hint": "平均身高 = 总身高 ÷ 人数，平均身高是多少？", "answer": str(avg)}],
        "answers": [{"label": "平均身高（厘米）", "value": str(avg)}],
        "answer_display": "平均身高 %d 厘米" % avg,
        "solution": ["思路：平均数 = 总数 ÷ 份数。",
                     "%d ÷ %d = %d（厘米）。答：平均身高是 %d 厘米。" % (total, cnt, avg, avg)],
    }


def _w4_hediff():
    """和差问题（易错：忘记先加后除以 2 或先减后除以 2）"""
    small = random.randint(10, 60)
    diff = random.randint(2, 40)
    big = small + diff
    total = big + small
    q = ("两个自然数的和是 %d，差是 %d。这两个数各是多少？"
         % (total, diff))
    return {
        "question": q,
        "steps": [{"hint": "和 + 差 = 大数的 2 倍，大数是多少？", "answer": str(big)},
                  {"hint": "再用大数减去差，小数是多少？", "answer": str(small)}],
        "answers": [{"label": "较大数", "value": str(big)},
                    {"label": "较小数", "value": str(small)}],
        "answer_display": "较大数是 %d，较小数是 %d" % (big, small),
        "solution": ["思路（和差问题）：（和 + 差）÷ 2 = 大数，（和 - 差）÷ 2 = 小数。",
                     "大数：（%d + %d）÷ 2 = %d，小数：（%d - %d）÷ 2 = %d。"
                     "答：这两个数分别是 %d 和 %d。"
                     % (total, diff, big, total, diff, small, big, small)],
    }


def _w4_give():
    """给后相同（易错：给出去的张数不等于相差数）"""
    if random.random() < 0.5:
        k = random.randint(2, 15)
        ans = 2 * k
        n = _name()
        q = "%s把自己卡片中的 %d 张给了弟弟后，两人的卡片一样多。原来%s比弟弟多多少张卡片？" \
            % (n, k, n)
        return {
            "question": q,
            "steps": [{"hint": "给出去 %d 张，同时弟弟收到了 %d 张，一去一来相差多少张？"
                       % (k, k), "answer": str(ans)}],
            "answers": [{"label": "多（张）", "value": str(ans)}],
            "answer_display": "原来多 %d 张" % ans,
            "solution": ["思路（易错点）：给出 %d 张后两人一样多，说明原来相差的是 %d 张的 2 倍。"
                         % (k, k),
                         "原来多 %d × 2 = %d（张）。答：原来比弟弟多 %d 张。" % (k, ans, ans)],
        }
    a = random.randint(30, 90)
    b = a - 2 * random.randint(2, 12)
    give = (a - b) // 2
    q = "哥哥有 %d 张卡片，弟弟有 %d 张，哥哥给弟弟多少张后两人的卡片一样多？" % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "先求相差多少张：哥哥比弟弟多多少张？", "answer": str(a - b)},
                  {"hint": "多出的部分给弟弟一半，给多少张后一样多？", "answer": str(give)}],
        "answers": [{"label": "给（张）", "value": str(give)}],
        "answer_display": "给 %d 张" % give,
        "solution": ["思路（易错点）：给出后两人一样多，给的是相差数的一半，不是全部相差数。",
                     "相差：%d - %d = %d（张），给出 %d ÷ 2 = %d（张）。"
                     "答：哥哥给弟弟 %d 张后两人一样多。" % (a, b, a - b, a - b, give, give)],
    }


def _w4_price():
    """单价 / 数量 / 总价"""
    kind = random.randint(0, 2)
    p = random.randint(4, 25)
    n = random.randint(2, 9)
    T = p * n
    if kind == 0:
        q = "每支钢笔 %d 元，买 %d 支一共要多少元？" % (p, n)
        return {
            "question": q,
            "steps": [{"hint": "总价 = 单价 × 数量，一共多少元？", "answer": str(T)}],
            "answers": [{"label": "总价（元）", "value": str(T)}],
            "answer_display": "一共 %d 元" % T,
            "solution": ["思路：总价 = 单价 × 数量。",
                         "%d × %d = %d（元）。答：一共要 %d 元。" % (p, n, T, T)],
        }
    if kind == 1:
        q = "%s买 %d 支同样的钢笔，一共花了 %d 元，每支钢笔多少元？" % (_name(), n, T)
        return {
            "question": q,
            "steps": [{"hint": "单价 = 总价 ÷ 数量，每支多少元？", "answer": str(p)}],
            "answers": [{"label": "单价（元）", "value": str(p)}],
            "answer_display": "每支 %d 元" % p,
            "solution": ["思路：单价 = 总价 ÷ 数量。",
                         "%d ÷ %d = %d（元）。答：每支钢笔 %d 元。" % (T, n, p, p)],
        }
    money = T + random.randint(1, p - 1)
    left = money - T
    q = "%s带了 %d 元去买单价 %d 元的钢笔，最多能买几支？还剩多少元？" % (_name(), money, p)
    return {
        "question": q,
        "steps": [{"hint": "最多能买几支？", "answer": str(n)},
                  {"hint": "还剩多少元？", "answer": str(left)}],
        "answers": [{"label": "最多买（支）", "value": str(n)},
                    {"label": "还剩（元）", "value": str(left)}],
        "answer_display": "最多买 %d 支，还剩 %d 元" % (n, left),
        "solution": ["思路：带的钱里最多有几个单价，就能买几支（剩余的不够再买一支）。",
                     "%d ÷ %d = %d（支）……%d（元）。答：最多买 %d 支，还剩 %d 元。"
                     % (money, p, n, left, n, left)],
    }


def _w4_speed():
    """速度 / 时间 / 路程"""
    kind = random.randint(0, 2)
    v = random.randint(40, 80)
    t = random.randint(2, 8)
    s = v * t
    if kind == 0:
        q = "一辆汽车每小时行 %d 千米，照这样计算，%d 小时能行多少千米？" % (v, t)
        return {
            "question": q,
            "steps": [{"hint": "路程 = 速度 × 时间，能行多少千米？", "answer": str(s)}],
            "answers": [{"label": "路程（千米）", "value": str(s)}],
            "answer_display": "能行 %d 千米" % s,
            "solution": ["思路：路程 = 速度 × 时间。",
                         "%d × %d = %d（千米）。答：%d 小时能行 %d 千米。" % (v, t, s, t, s)],
        }
    if kind == 1:
        q = "甲、乙两地相距 %d 千米，一辆汽车每小时行 %d 千米，从甲地到乙地要几小时？" % (s, v)
        return {
            "question": q,
            "steps": [{"hint": "时间 = 路程 ÷ 速度，要几小时？", "answer": str(t)}],
            "answers": [{"label": "时间（小时）", "value": str(t)}],
            "answer_display": "要 %d 小时" % t,
            "solution": ["思路：时间 = 路程 ÷ 速度。",
                         "%d ÷ %d = %d（小时）。答：从甲地到乙地要 %d 小时。" % (s, v, t, t)],
        }
    q = "一列火车 %d 小时行了 %d 千米，这列火车平均每小时行多少千米？" % (t, s)
    return {
        "question": q,
        "steps": [{"hint": "速度 = 路程 ÷ 时间，平均每小时行多少千米？", "answer": str(v)}],
        "answers": [{"label": "速度（千米/时）", "value": str(v)}],
        "answer_display": "每小时行 %d 千米" % v,
        "solution": ["思路：速度 = 路程 ÷ 时间。",
                     "%d ÷ %d = %d（千米/时）。答：平均每小时行 %d 千米。" % (s, t, v, v)],
    }


def _w4_negative():
    """生活中的负数（易错：零上零下混减）"""
    if random.random() < 0.5:
        a = random.randint(1, 15)
        b = random.randint(1, 15)
        if random.random() < 0.5:
            ans = b - a
            q = "早晨的气温是零下 %d ℃（-%d℃），中午上升了 %d ℃，中午的气温是多少摄氏度？" % (a, a, b)
            ans_str = ("%d℃" % ans) if ans >= 0 else "-%d℃" % abs(ans)
            return {
                "question": q,
                "steps": [{"hint": "零下 %d ℃记作 -%d℃，再加上上升的 %d ℃，中午是多少摄氏度？"
                           % (a, a, b), "answer": str(ans)}],
                "answers": [{"label": "中午气温（℃，零下记负数）", "value": str(ans)}],
                "answer_display": "中午的气温是 %s" % ans_str,
                "solution": ["思路（易错点）：零下温度用负数表示，上升是加上正数。",
                             "-%d + %d = %d。答：中午的气温是 %s。" % (a, b, ans, ans_str)],
            }
        h = random.randint(5, 12)
        ans = h + a
        q = "某天最高气温是 %d℃，最低气温是零下 %d ℃（-%d℃），这一天的温差是多少摄氏度？" % (h, a, a)
        return {
            "question": q,
            "steps": [{"hint": "从 -%d℃ 升到 0℃ 要升 %d℃，再升到 %d℃ 又要升 %d℃，温差是多少？"
                       % (a, a, h, h), "answer": str(ans)}],
            "answers": [{"label": "温差（℃）", "value": str(ans)}],
            "answer_display": "温差是 %d℃" % ans,
            "solution": ["思路（易错点）：温差 = 最高气温 - 最低气温，最低是负数时不能直接相减。",
                         "%d -（-%d）= %d + %d = %d（℃）。答：这一天的温差是 %d℃。"
                         % (h, a, h, a, ans, ans)],
        }
    a = random.randint(2, 10)
    down = random.randint(1, 12)
    ans = -(a + down)   # 零下再下降：-a - down
    ans_str = "-%d℃" % abs(ans)
    q = "中午的气温是零下 %d ℃（-%d℃），傍晚又下降了 %d ℃，傍晚的气温是多少摄氏度？" % (a, a, down)
    return {
        "question": q,
        "steps": [{"hint": "下降用减法：-%d - %d 等于多少？" % (a, down), "answer": str(ans)}],
        "answers": [{"label": "傍晚气温（℃，零下记负数）", "value": str(ans)}],
        "answer_display": "傍晚的气温是 %s" % ans_str,
        "solution": ["思路：温度下降就是在原温度上再减。",
                     "-%d - %d = %d。答：傍晚的气温是 %s。" % (a, down, ans, ans_str)],
    }


def _w4_round():
    """大数近似数（易错：看错千位 / 没看后一位）"""
    m = random.randint(10, 99)
    r = random.randint(0, 9999)
    n = m * 10000 + r
    rounded = m + (1 if r >= 5000 else 0)
    q = "某市去年的人口约是 %d 人，省略万位后面的尾数后大约是多少万人？" % n
    return {
        "question": q,
        "steps": [{"hint": "看万位后面的\"千位\"：千位上的数是几？",
                   "answer": str(r // 1000)},
                  {"hint": "省略万位后面的尾数，大约是多少万人？", "answer": str(rounded)}],
        "answers": [{"label": "约（万人）", "value": str(rounded)}],
        "answer_display": "大约是 %d 万人" % rounded,
        "solution": ["思路（易错点）：省略万位后面的尾数，要看千位上的数：满 5 进 1，不满 5 舍去。",
                     "%d 人 ≈ %d 万人。答：大约是 %d 万人。" % (n, rounded, rounded)],
    }


def _w4_angle():
    """角度（平角 / 直角）"""
    a = random.randint(15, 89)
    b = 180 - a
    q = "一个角是 %d 度的锐角，它与多少度的角正好能拼成一个平角？" % a
    return {
        "question": q,
        "steps": [{"hint": "平角是 180 度，拼成平角需要多少度？", "answer": str(b)}],
        "answers": [{"label": "需要（度）", "value": str(b)}],
        "answer_display": "需要 %d 度" % b,
        "solution": ["思路：平角 = 180 度，用 180 度减去已知的角。",
                     "180 - %d = %d（度）。答：它与 %d 度的角正好拼成平角。" % (a, b, b)],
    }


def _w4_decimal():
    """小数加减购物（四下）"""
    a = random.randint(3, 25)
    b = random.randint(1, 9)
    c = random.randint(3, 18)
    d = random.randint(1, 9)
    p1 = a + b / 10.0
    p2 = c + d / 10.0
    total = round(p1 + p2, 1)   # 两件合计不超过 50 元，保证找零为正
    if random.random() < 0.5:
        q = ("一支钢笔 %.1f 元，一本笔记本 %.1f 元，各买一个一共要多少元？"
             % (p1, p2))
        return {
            "question": q,
            "steps": [{"hint": "小数点对齐相加，一共多少元？", "answer": "%.1f" % total}],
            "answers": [{"label": "一共（元）", "value": "%.1f" % total}],
            "answer_display": "一共要 %.1f 元" % total,
            "solution": ["思路：小数相加时小数点要对齐，按元加元、角加角计算。",
                         "%.1f + %.1f = %.1f（元）。答：一共要 %.1f 元。" % (p1, p2, total, total)],
        }
    back = round(50 - total, 1)
    q = "%s买了一支 %.1f 元的钢笔和一本 %.1f 元的笔记本，付了 50 元，应找回多少元？" \
        % (_name(), p1, p2)
    return {
        "question": q,
        "steps": [{"hint": "先算两种文具一共多少元？", "answer": "%.1f" % total},
                  {"hint": "再算应找回多少元？", "answer": "%.1f" % back}],
        "answers": [{"label": "找回（元）", "value": "%.1f" % back}],
        "answer_display": "应找回 %.1f 元" % back,
        "solution": ["思路：先算总价，再用 50 元减去总价。",
                     "总价：%.1f + %.1f = %.1f（元），找回：50 - %.1f = %.1f（元）。"
                     "答：应找回 %.1f 元。" % (p1, p2, total, total, back, back)],
    }


# ================= 五年级（分段计费、和倍差倍、长方体、公倍数、分数除法、小数乘法） =================

def _w5_segfee():
    """分段计费（易错：忽略起步段 / 忘加起步价）"""
    base = random.randint(8, 13)
    incl = random.randint(2, 4)
    per = 2
    dist = random.randint(incl + 2, incl + 18)
    fee = base + (dist - incl) * per
    q = ("某出租车起步价 %d 元（%d 千米以内），超过 %d 千米后每千米另收 %d 元。"
         "%s乘车行了 %d 千米，他应付多少元车费？" % (base, incl, incl, per, _name(), dist))
    return {
        "question": q,
        "steps": [{"hint": "超出部分是多少千米？", "answer": str(dist - incl)},
                  {"hint": "超出部分的车费是多少元？", "answer": str((dist - incl) * per)},
                  {"hint": "加上起步价，一共应付多少元？", "answer": str(fee)}],
        "answers": [{"label": "车费（元）", "value": str(fee)}],
        "answer_display": "应付 %d 元" % fee,
        "solution": ["思路（易错点）：分段计费要把路程分成\"起步段\"和\"超出段\"分别计价再相加。",
                     "超出：%d - %d = %d（千米），超出车费 %d × %d = %d（元）。"
                     % (dist, incl, dist - incl, dist - incl, per, (dist - incl) * per),
                     "总车费：%d + %d = %d（元）。答：他应付 %d 元车费。"
                     % (base, (dist - incl) * per, fee, fee)],
    }


def _w5_hebei():
    """和倍问题（易错：份数忘加 1）"""
    s = random.randint(6, 30)
    k = random.randint(2, 4)
    big = k * s
    small = s
    total = big + small
    q = ("果园里苹果树和梨树一共有 %d 棵，苹果树的棵数是梨树的 %d 倍。"
         "苹果树和梨树各有多少棵？" % (total, k))
    return {
        "question": q,
        "steps": [{"hint": "把梨树看作 1 份，苹果树有这样的 %d 份，一共是几份？"
                   % k, "answer": str(k + 1)},
                  {"hint": "每份（梨树）是多少棵？", "answer": str(s)},
                  {"hint": "苹果树是多少棵？", "answer": str(big)}],
        "answers": [{"label": "苹果树（棵）", "value": str(big)},
                    {"label": "梨树（棵）", "value": str(s)}],
        "answer_display": "苹果树 %d 棵，梨树 %d 棵" % (big, s),
        "solution": ["思路（和倍问题，易错点）：份数 = 倍数 + 1，不要只用倍数去除。",
                     "梨树：%d ÷ %d = %d（棵），苹果树：%d × %d = %d（棵）。"
                     "答：苹果树 %d 棵，梨树 %d 棵。"
                     % (total, k + 1, s, s, k, big, big, s)],
    }


def _w5_chabei():
    """差倍问题（易错：份数忘减 1）"""
    s = random.randint(6, 30)
    k = random.randint(2, 4)
    big = k * s
    diff = big - s
    q = ("学校科技组的图书比美术组多 %d 本，科技组的本数是美术组的 %d 倍。"
         "科技组和美术组各有多少本图书？" % (diff, k))
    return {
        "question": q,
        "steps": [{"hint": "把美术组看作 1 份，科技组有这样的 %d 份，相差（%d - 1）份是 %d 本，"
                   "每份是多少本？" % (k, k, diff), "answer": str(s)},
                  {"hint": "科技组是多少本？", "answer": str(big)}],
        "answers": [{"label": "科技组（本）", "value": str(big)},
                    {"label": "美术组（本）", "value": str(s)}],
        "answer_display": "科技组 %d 本，美术组 %d 本" % (big, s),
        "solution": ["思路（差倍问题，易错点）：相差的份数 = 倍数 - 1，不要直接用倍数除。",
                     "美术组：%d ÷（%d - 1）= %d（本），科技组：%d × %d = %d（本）。"
                     "答：科技组 %d 本，美术组 %d 本。" % (diff, k, s, s, k, big, big, s)],
    }


def _w5_box():
    """长方体表面积与体积（易错：无盖时面数变少）"""
    a = random.randint(3, 12)
    b = random.randint(3, 12)
    c = random.randint(2, 10)
    kind = random.randint(0, 2)
    if kind == 0:
        v = a * b * c
        q = "一个长方体长 %d 厘米、宽 %d 厘米、高 %d 厘米，它的体积是多少立方厘米？" % (a, b, c)
        return {
            "question": q,
            "steps": [{"hint": "长方体体积 = 长 × 宽 × 高，体积是多少？", "answer": str(v)}],
            "answers": [{"label": "体积（立方厘米）", "value": str(v)}],
            "answer_display": "体积是 %d 立方厘米" % v,
            "solution": ["思路：长方体体积 = 长 × 宽 × 高。",
                         "%d × %d × %d = %d（立方厘米）。答：体积是 %d 立方厘米。"
                         % (a, b, c, v, v)],
        }
    if kind == 1:
        sa = 2 * (a * b + a * c + b * c)
        q = ("做一个长 %d 厘米、宽 %d 厘米、高 %d 厘米的长方体纸箱（有盖），"
             "至少需要多少平方厘米硬纸板？" % (a, b, c))
        return {
            "question": q,
            "steps": [{"hint": "上下面：2 × %d = %d（平方厘米）" % (a * b, 2 * a * b),
                       "answer": str(2 * a * b)},
                      {"hint": "前后面：2 × %d = %d（平方厘米）" % (a * c, 2 * a * c),
                       "answer": str(2 * a * c)},
                      {"hint": "左右面：2 × %d = %d（平方厘米）" % (b * c, 2 * b * c),
                       "answer": str(2 * b * c)},
                      {"hint": "六面合起来一共需要多少平方厘米？", "answer": str(sa)}],
            "answers": [{"label": "纸板（平方厘米）", "value": str(sa)}],
            "answer_display": "需要 %d 平方厘米" % sa,
            "solution": ["思路：表面积 =（长×宽 + 长×高 + 宽×高）× 2。",
                         "（%d + %d + %d）× 2 = %d（平方厘米）。答：至少需要 %d 平方厘米硬纸板。"
                         % (a * b, a * c, b * c, sa, sa)],
        }
    sa = a * b + 2 * (a * c + b * c)
    q = ("做一个无盖的长方体玻璃鱼缸（有底面和四周，没有上面），长 %d 厘米、宽 %d 厘米、"
         "高 %d 厘米，至少需要多少平方厘米玻璃？" % (a, b, c))
    return {
        "question": q,
        "steps": [{"hint": "无盖鱼缸只有 1 个底面和 4 个侧面，底面积是多少？"
                   , "answer": str(a * b)},
                  {"hint": "四个侧面的面积一共是多少？", "answer": str(2 * (a * c + b * c))},
                  {"hint": "合起来一共需要多少平方厘米玻璃？", "answer": str(sa)}],
        "answers": [{"label": "玻璃（平方厘米）", "value": str(sa)}],
        "answer_display": "需要 %d 平方厘米" % sa,
        "solution": ["思路（易错点）：无盖鱼缸缺上面，只有 1 个底面 + 4 个侧面，不要按 6 个面算。",
                     "底面：%d × %d = %d（平方厘米），侧面：2 ×（%d × %d + %d × %d）= %d（平方厘米）。"
                     % (a, b, a * b, a, c, b, c, 2 * (a * c + b * c)),
                     "一共：%d + %d = %d（平方厘米）。答：至少需要 %d 平方厘米玻璃。"
                     % (a * b, 2 * (a * c + b * c), sa, sa)],
    }


def _w5_lcm():
    """公倍数应用"""
    a = random.randint(2, 6)
    b = random.randint(2, 6)
    while b == a:
        b = random.randint(2, 6)
    l = a * b // _gcd(a, b)
    best = (50 // l) * l
    q = ("一篮鸡蛋不超过 50 个，无论 %d 个一装还是 %d 个一装都正好装完"
         "（鸡蛋数既是 %d 的倍数，也是 %d 的倍数）。这篮鸡蛋最多有多少个？" % (a, b, a, b))
    return {
        "question": q,
        "steps": [{"hint": "既是 %d 的倍数又是 %d 的倍数的数，最小是多少？" % (a, b),
                   "answer": str(l)},
                  {"hint": "不超过 50 个的公倍数中最大的一个是多少？", "answer": str(best)}],
        "answers": [{"label": "最多（个）", "value": str(best)}],
        "answer_display": "最多 %d 个" % best,
        "solution": ["思路：鸡蛋个数是 %d 和 %d 的公倍数，先求最小公倍数，再找 50 以内最大的公倍数。"
                     % (a, b),
                     "最小公倍数是 %d，50 以内最大的公倍数：%d × %d = %d（个）。"
                     "答：这篮鸡蛋最多有 %d 个。" % (l, l, 50 // l, best, best)],
    }


def _w5_fracrev():
    """分数除法逆向应用（易错：该除算成乘）"""
    d = random.randint(3, 9)
    n = random.randint(1, d - 1)
    k = random.randint(2, 9)
    total = k * d
    y = k * n
    q = ("%s读一本书，已经读了 %d 页，正好占全书的 %d/%d。这本书一共有多少页？"
         % (_name(), y, n, d))
    return {
        "question": q,
        "steps": [{"hint": "全书页数未知，已知它的 %d/%d 是 %d 页，用除法求全书：全书多少页？"
                   % (n, d, y), "answer": str(total)}],
        "answers": [{"label": "全书（页）", "value": str(total)}],
        "answer_display": "这本书一共有 %d 页" % total,
        "solution": ["思路（易错点）：已知一个数的几分之几是多少，求这个数用除法（除以分数），"
                     "不要用乘法。",
                     "全书：%d ÷ %d/%d = %d × %d/%d = %d（页）。"
                     "答：这本书一共有 %d 页。" % (y, n, d, y, d, n, total, total)],
    }


def _w5_decmul():
    """小数乘法应用"""
    a = random.randint(2, 12)
    b = random.randint(1, 9)
    k = random.randint(2, 9)
    p = a + b / 10.0
    total = round(p * k, 1)
    q = "苹果每千克 %.1f 元，买 %d 千克要多少元？" % (p, k)
    return {
        "question": q,
        "steps": [{"hint": "总价 = 单价 × 数量，一共多少元？", "answer": "%.1f" % total}],
        "answers": [{"label": "总价（元）", "value": "%.1f" % total}],
        "answer_display": "要 %.1f 元" % total,
        "solution": ["思路：小数乘整数，按单价 × 数量计算。",
                     "%.1f × %d = %.1f（元）。答：买 %d 千克要 %.1f 元。"
                     % (p, k, total, k, total)],
    }


def _gcd(x, y):
    while y:
        x, y = y, x % y
    return x


# ================= 六年级（涨降价、按比分配、圆、百分率、分数应用、利息、纳税） =================

def _w6_updown():
    """涨价再降价恢复原价问题（易错：两次单位 1 不同）"""
    a = random.choice([10, 20])
    if a == 10:
        X = random.randint(1, 10) * 100
    else:
        X = random.randint(4, 20) * 25
    up = X * (100 + a) // 100
    cur = up * (100 - a) // 100
    save = X - cur
    q = ("一件商品原价 %d 元，先提价 %d%%，后来又降价 %d%%，现在的价钱是多少元？"
         "比原价贵了还是便宜了？便宜（贵了）多少元？" % (X, a, a))
    return {
        "question": q,
        "steps": [{"hint": "提价后的价钱：%d ×（1 + %d%%）是多少元？" % (X, a),
                   "answer": str(up)},
                  {"hint": "再降价是在提价后的价钱上降 %d%%，现在的价钱是多少元？" % a,
                   "answer": str(cur)},
                  {"hint": "与原价相比，相差多少元？", "answer": str(save)}],
        "answers": [{"label": "现价（元）", "value": str(cur)},
                    {"label": "比原价便宜（元）", "value": str(save)}],
        "answer_display": "现价 %d 元，比原价便宜 %d 元" % (cur, save),
        "solution": ["思路（易错点）：提价和降价的百分数虽然相同，但单位\"1\"不同——"
                     "降价是在提价后的价钱上降的，所以不会回到原价。",
                     "提价后：%d ×（1 + %d%%）= %d（元）。" % (X, a, up),
                     "现价：%d ×（1 - %d%%）= %d（元），比原价便宜 %d - %d = %d（元）。"
                     "答：现在的价钱是 %d 元，比原价便宜 %d 元。"
                     % (up, a, cur, X, cur, save, cur, save)],
    }


def _w6_ratio():
    """按比分配（易错：总份数用错）"""
    m = random.randint(1, 5)
    n2 = random.randint(1, 5)
    while n2 == m:
        n2 = random.randint(1, 5)
    qn = random.randint(3, 20)
    total = (m + n2) * qn
    p1 = m * qn
    p2 = n2 * qn
    q = ("水果店运来 %d 个西瓜，按 %d : %d 的比分给甲、乙两个门市部，"
         "两个门市部分别分到多少个西瓜？" % (total, m, n2))
    return {
        "question": q,
        "steps": [{"hint": "先求总份数：%d + %d = 多少份？" % (m, n2), "answer": str(m + n2)},
                  {"hint": "每份是多少个？", "answer": str(qn)},
                  {"hint": "甲分到多少个？", "answer": str(p1)},
                  {"hint": "乙分到多少个？", "answer": str(p2)}],
        "answers": [{"label": "甲门市部（个）", "value": str(p1)},
                    {"label": "乙门市部（个）", "value": str(p2)}],
        "answer_display": "甲分到 %d 个，乙分到 %d 个" % (p1, p2),
        "solution": ["思路（按比分配，易错点）：总份数 = 比的前项 + 后项，先求每份再求各部分。",
                     "总份数 %d 份，每份 %d ÷ %d = %d（个）。"
                     % (m + n2, total, m + n2, qn),
                     "甲：%d × %d = %d（个），乙：%d × %d = %d（个）。"
                     "答：甲分到 %d 个，乙分到 %d 个。"
                     % (m, qn, p1, n2, qn, p2, p1, p2)],
    }


def _w6_circle():
    """圆的周长与面积（π 取 3.14，易错：半圆周长忘加直径）"""
    kind = random.randint(0, 3)
    if kind == 0:
        r = random.choice([2, 3, 4, 5, 6, 8, 10, 15, 20])
        c = 2 * 3.14 * r
        q = "一个圆的半径是 %d 厘米，它的周长是多少厘米？（π 取 3.14）" % r
        return {
            "question": q,
            "steps": [{"hint": "圆的周长 = 2 × π × 半径，周长是多少厘米？", "answer": "%.2f" % c}],
            "answers": [{"label": "周长（厘米）", "value": "%.2f" % c}],
            "answer_display": "周长是 %.2f 厘米" % c,
            "solution": ["思路：圆的周长 C = 2πr。",
                         "2 × 3.14 × %d = %.2f（厘米）。答：周长是 %.2f 厘米。" % (r, c, c)],
        }
    if kind == 1:
        r = random.choice([2, 3, 4, 5, 6, 8, 10])
        area = 3.14 * r * r
        q = "一个圆的半径是 %d 厘米，它的面积是多少平方厘米？（π 取 3.14）" % r
        return {
            "question": q,
            "steps": [{"hint": "圆的面积 = π × 半径 × 半径，面积是多少平方厘米？",
                       "answer": "%.2f" % area}],
            "answers": [{"label": "面积（平方厘米）", "value": "%.2f" % area}],
            "answer_display": "面积是 %.2f 平方厘米" % area,
            "solution": ["思路：圆的面积 S = πr²。",
                         "3.14 × %d × %d = %.2f（平方厘米）。答：面积是 %.2f 平方厘米。"
                         % (r, r, area, area)],
        }
    if kind == 2:
        r = random.choice([2, 4, 6, 8, 10])
        half = 3.14 * r + 2 * r
        q = "一个半圆的半径是 %d 厘米，它的周长是多少厘米？（π 取 3.14）" % r
        return {
            "question": q,
            "steps": [{"hint": "半圆周长 = 圆周长的一半 + 直径。圆周长的一半是多少厘米？",
                       "answer": "%.2f" % (3.14 * r)},
                  {"hint": "再加上直径 %d 厘米，半圆的周长是多少厘米？" % (2 * r),
                   "answer": "%.2f" % half}],
            "answers": [{"label": "周长（厘米）", "value": "%.2f" % half}],
            "answer_display": "周长是 %.2f 厘米" % half,
            "solution": ["思路（易错点）：半圆的周长 = 半个圆的弧长 + 一条直径，容易漏加直径。",
                         "弧长：3.14 × %d = %.2f（厘米），直径：2 × %d = %d（厘米）。"
                         % (r, 3.14 * r, r, 2 * r),
                         "周长：%.2f + %d = %.2f（厘米）。答：半圆的周长是 %.2f 厘米。"
                         % (3.14 * r, 2 * r, half, half)],
        }
    r = random.choice([5, 10, 15, 20, 25])
    c = 2 * 3.14 * r
    q = "一个圆的周长是 %.2f 厘米，它的直径是多少厘米？（π 取 3.14）" % c
    return {
        "question": q,
        "steps": [{"hint": "直径 = 周长 ÷ π，直径是多少厘米？", "answer": str(2 * r)}],
        "answers": [{"label": "直径（厘米）", "value": str(2 * r)}],
        "answer_display": "直径是 %d 厘米" % (2 * r),
        "solution": ["思路：圆的周长除以 π 就是直径。",
                     "%.2f ÷ 3.14 = %d（厘米）。答：它的直径是 %d 厘米。" % (c, 2 * r, 2 * r)],
    }


def _w6_rate():
    """百分率应用（易错：分率用错分母）"""
    total = random.choice([25, 50, 100])
    kind = random.randint(0, 2)
    if kind == 0:
        absent = random.randint(1, 5)
        present = total - absent
        pct = present * 100 // total
        q = "六（1）班有 %d 名同学，今天缺勤 %d 人。今天的出勤率是多少？（只填百分号前的数）" \
            % (total, absent)
        return {
            "question": q,
            "steps": [{"hint": "出勤人数是多少人？" , "answer": str(present)},
                      {"hint": "出勤率 = 出勤人数 ÷ 总人数 × 100%%，出勤率是多少？",
                       "answer": str(pct)}],
            "answers": [{"label": "出勤率（百分号前的数）", "value": str(pct)}],
            "answer_display": "出勤率是 %d%%" % pct,
            "solution": ["思路（易错点）：出勤率的分母是全班总人数，不是出勤人数。",
                         "出勤：%d - %d = %d（人），出勤率：%d ÷ %d × 100%% = %d%%。"
                         "答：今天的出勤率是 %d%%。" % (total, absent, present, present, total, pct, pct)],
        }
    if kind == 1:
        bad = random.choice([2, 4, 5, 10, 20]) * (total // 25)
        good = total - bad
        pct = good * 100 // total
        q = "一批产品共 %d 件，检验出不合格 %d 件。这批产品的合格率是多少？（只填百分号前的数）" \
            % (total, bad)
        return {
            "question": q,
            "steps": [{"hint": "合格的产品有多少件？", "answer": str(good)},
                      {"hint": "合格率 = 合格数 ÷ 总数 × 100%%，合格率是多少？",
                       "answer": str(pct)}],
            "answers": [{"label": "合格率（百分号前的数）", "value": str(pct)}],
            "answer_display": "合格率是 %d%%" % pct,
            "solution": ["思路（易错点）：合格率的分母是产品总数。",
                         "合格：%d - %d = %d（件），合格率：%d ÷ %d × 100%% = %d%%。"
                         "答：合格率是 %d%%。" % (total, bad, good, good, total, pct, pct)],
        }
    n0 = random.choice([20, 40, 50, 80, 90]) * (total // 100 + 1)
    if n0 >= total:
        n0 = total - 10
    pct = n0 * 100 // total
    q = "农科站用 %d 粒种子做发芽实验，结果有 %d 粒种子发了芽。发芽率是多少？（只填百分号前的数）" \
        % (total, n0)
    return {
        "question": q,
        "steps": [{"hint": "发芽率 = 发芽粒数 ÷ 总粒数 × 100%%，发芽率是多少？",
                   "answer": str(pct)}],
        "answers": [{"label": "发芽率（百分号前的数）", "value": str(pct)}],
        "answer_display": "发芽率是 %d%%" % pct,
        "solution": ["思路：发芽率 = 发芽的粒数 ÷ 实验种子总粒数 × 100%。",
                     "%d ÷ %d × 100%% = %d%%。答：发芽率是 %d%%。" % (n0, total, pct, pct)],
    }


def _w6_frac_more():
    """分数应用：比一个数多几分之几（易错：单位 1 判断错）"""
    d = random.randint(3, 9)
    n = random.randint(1, d - 1)
    k = random.randint(2, 9)
    peach = k * (d + n)
    pear = k * d
    q = ("果园里桃树的棵数比梨树多 %d/%d，桃树有 %d 棵。梨树有多少棵？"
         % (n, d, peach))
    return {
        "question": q,
        "steps": [{"hint": "把梨树看作单位\"1\"，桃树相当于梨树的（1 + %d/%d），梨树是多少棵？"
                   % (n, d), "answer": str(pear)}],
        "answers": [{"label": "梨树（棵）", "value": str(pear)}],
        "answer_display": "梨树有 %d 棵" % pear,
        "solution": ["思路（易错点）：\"桃树比梨树多 %d/%d\"中单位\"1\"是梨树，桃树是梨树的（1 + %d/%d），"
                     "已知桃树求梨树用除法。" % (n, d, n, d),
                     "梨树：%d ÷（1 + %d/%d）= %d ÷ %d/%d = %d（棵）。"
                     "答：梨树有 %d 棵。" % (peach, n, d, peach, d + n, d, pear, pear)],
    }


def _w6_interest():
    """利息应用（本息和）"""
    P = random.randint(2, 40) * 500
    r = random.choice([1, 2, 3])
    interest = P * r // 100
    total = P + interest
    q = ("王叔叔把 %d 元存入银行，定期两年，年利率 %d%%。到期后可以获得利息多少元？"
         "本息一共多少元？" % (P, r))
    return {
        "question": q,
        "steps": [{"hint": "利息 = 本金 × 年利率 × 存期，两年可得利息多少元？",
                   "answer": str(interest)},
                  {"hint": "本息和 = 本金 + 利息，本息一共多少元？", "answer": str(total)}],
        "answers": [{"label": "利息（元）", "value": str(interest)},
                    {"label": "本息（元）", "value": str(total)}],
        "answer_display": "利息 %d 元，本息共 %d 元" % (interest, total),
        "solution": ["思路：利息 = 本金 × 年利率 × 时间。",
                     "利息：%d × %d%% × 2 = %d（元），本息：%d + %d = %d（元）。"
                     "答：到期后可获得利息 %d 元，本息一共 %d 元。"
                     % (P, r, interest, P, interest, total, interest, total)],
    }


def _w6_tax():
    """纳税应用"""
    T = random.randint(4, 40) * 500
    r = random.choice([3, 5, 6, 10])
    tax = T * r // 100
    left = T - tax
    q = ("一家商店上个月的营业额是 %d 元，按营业额的 %d%% 缴纳增值税。"
         "应缴税多少元？缴税后剩余多少元？" % (T, r))
    return {
        "question": q,
        "steps": [{"hint": "应缴税 = 营业额 × 税率，应缴税多少元？", "answer": str(tax)},
                  {"hint": "缴税后剩余多少元？", "answer": str(left)}],
        "answers": [{"label": "应缴税（元）", "value": str(tax)},
                    {"label": "剩余（元）", "value": str(left)}],
        "answer_display": "应缴税 %d 元，缴税后剩余 %d 元" % (tax, left),
        "solution": ["思路：应缴税额 = 营业额 × 税率。",
                     "应缴税：%d × %d%% = %d（元），剩余：%d - %d = %d（元）。"
                     "答：应缴税 %d 元，缴税后剩余 %d 元。"
                     % (T, r, tax, T, tax, left, tax, left)],
    }


# ================= 新增题型：易错专项与常见题型补充 =================

# ---------- 一年级补充 ----------

def _w1_part():
    """求部分数（已知总数与其中一部分，求另一部分）"""
    item = random.choice([("鸭子", "白鸭子", "黑鸭子"), ("兔子", "白兔", "灰兔"),
                          ("金鱼", "红金鱼", "黑金鱼"), ("鸽子", "白鸽", "灰鸽")])
    total = random.randint(6, 20)
    a = random.randint(2, total - 2)
    b = total - a
    q = "池塘里一共有 %d 只%s，其中%s有 %d 只，剩下的是%s，%s有多少只？" \
        % (total, item[0], item[1], a, item[2], item[2])
    return {
        "question": q,
        "steps": [{"hint": "从总数里去掉一部分，就是另一部分。另一部分有多少只？",
                   "answer": str(b)}],
        "answers": [{"label": "另一部分（只）", "value": str(b)}],
        "answer_display": "有 %d 只" % b,
        "solution": ["思路：已知总数和其中一部分，求另一部分用减法。",
                     "另一部分：%d - %d = %d（只）。答：%s有 %d 只。"
                     % (total, a, b, item[2], b)],
    }


def _w1_disturb():
    """多余条件（易错：被无关数字干扰）"""
    n = _name()
    pens = random.randint(6, 15)
    erasers = random.randint(2, 8)
    used = random.randint(1, pens - 1)
    left = pens - used
    q = "%s有 %d 支铅笔和 %d 块橡皮，写作业用去了 %d 支铅笔，还剩多少支铅笔？" \
        % (n, pens, erasers, used)
    return {
        "question": q,
        "steps": [{"hint": "橡皮的块数与铅笔无关，还剩多少支铅笔？", "answer": str(left)}],
        "answers": [{"label": "还剩（支）", "value": str(left)}],
        "answer_display": "还剩 %d 支铅笔" % left,
        "solution": ["思路（易错点）：只跟铅笔有关的条件才有用，橡皮的块数是多余条件，不要拿它来计算。",
                     "还剩：%d - %d = %d（支）。答：还剩 %d 支铅笔。" % (pens, used, left, left)],
    }


def _w1_lianadd():
    """连加应用：三部分合起来"""
    n = _name()
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    c = random.randint(2, 9)
    total = a + b + c
    q = "%s第一次跳绳跳了 %d 下，第二次跳了 %d 下，第三次跳了 %d 下，三次一共跳了多少下？" \
        % (n, a, b, c)
    return {
        "question": q,
        "steps": [{"hint": "先把前两次的下数合起来，一共多少下？", "answer": str(a + b)},
                  {"hint": "再加上第三次的下数，一共跳了多少下？", "answer": str(total)}],
        "answers": [{"label": "一共（下）", "value": str(total)}],
        "answer_display": "一共跳了 %d 下" % total,
        "solution": ["思路：求三部分合起来是多少，用连加。",
                     "%d + %d = %d（下），%d + %d = %d（下）。答：三次一共跳了 %d 下。"
                     % (a, b, a + b, a + b, c, total, total)],
    }


def _w1_diffrev():
    """比多少逆向（易错：见\"多\"就加、见\"少\"就减）"""
    n = _name()
    m = _name()
    while m == n:
        m = _name()
    if random.random() < 0.5:
        a = random.randint(6, 20)
        d = random.randint(1, a - 2)
        b = a - d
        q = "%s有 %d 支铅笔，比%s多 %d 支。%s有多少支铅笔？" % (n, a, m, d, m)
        return {
            "question": q,
            "steps": [{"hint": "%s比%s多，说明%s的少。%s有多少支？"
                       % (n, m, m, m), "answer": str(b)}],
            "answers": [{"label": "铅笔（支）", "value": str(b)}],
            "answer_display": "%s有 %d 支铅笔" % (m, b),
            "solution": ["思路（易错点）：\"%s比%s多 %d 支\"说明%s的少，求%s要用减法，不要见\"多\"就加。"
                         % (n, m, d, m, m),
                         "%s：%d - %d = %d（支）。答：%s有 %d 支铅笔。"
                         % (m, a, d, b, m, b)],
        }
    a = random.randint(4, 15)
    d = random.randint(1, a - 1)
    b = a + d
    q = "%s有 %d 张画片，比%s少 %d 张。%s有多少张画片？" % (n, a, m, d, m)
    return {
        "question": q,
        "steps": [{"hint": "%s比%s少，说明%s的多。%s有多少张？"
                   % (n, m, m, m), "answer": str(b)}],
        "answers": [{"label": "画片（张）", "value": str(b)}],
        "answer_display": "%s有 %d 张画片" % (m, b),
        "solution": ["思路（易错点）：\"%s比%s少 %d 张\"说明%s的多，求%s要用加法，不要见\"少\"就减。"
                     % (n, m, d, m, m),
                     "%s：%d + %d = %d（张）。答：%s有 %d 张画片。"
                     % (m, a, d, b, m, b)],
    }


# ---------- 二年级补充 ----------

def _w2_muladd():
    """乘加应用（先乘后加两步）"""
    per = random.randint(2, 9)
    rows = random.randint(2, 9)
    extra = random.randint(1, 8)
    mul = per * rows
    total = mul + extra
    q = "同学们摆积木，每行摆 %d 块，摆了 %d 行，后来又拿来 %d 块。现在一共有多少块积木？" \
        % (per, rows, extra)
    return {
        "question": q,
        "steps": [{"hint": "先算摆出来的积木一共有多少块？", "answer": str(mul)},
                  {"hint": "再加上后来的 %d 块，现在有多少块？" % extra, "answer": str(total)}],
        "answers": [{"label": "现在（块）", "value": str(total)}],
        "answer_display": "现在有 %d 块" % total,
        "solution": ["思路：先用乘法算出摆了多少块，再加上后来的块数。",
                     "%d × %d = %d（块），%d + %d = %d（块）。答：现在一共有 %d 块积木。"
                     % (per, rows, mul, mul, extra, total, total)],
    }


def _w2_mulsub():
    """乘减应用（先乘后减两步）"""
    per = random.randint(3, 9)
    boxes = random.randint(2, 9)
    sold = random.randint(1, per * boxes - 1)
    total = per * boxes
    left = total - sold
    q = "商店运来 %d 盒酸奶，每盒 %d 瓶，卖出了 %d 瓶，还剩下多少瓶？" \
        % (boxes, per, sold)
    return {
        "question": q,
        "steps": [{"hint": "先算运来的酸奶一共有多少瓶？", "answer": str(total)},
                  {"hint": "再减去卖出的 %d 瓶，还剩多少瓶？" % sold, "answer": str(left)}],
        "answers": [{"label": "还剩（瓶）", "value": str(left)}],
        "answer_display": "还剩 %d 瓶" % left,
        "solution": ["思路：先用乘法算出总瓶数，再减去卖出的瓶数。",
                     "%d × %d = %d（瓶），%d - %d = %d（瓶）。答：还剩下 %d 瓶。"
                     % (boxes, per, total, total, sold, left, left)],
    }


def _w2_remainder():
    """有余数除法（易错：商和余数的单位混淆、余数必须比除数小）"""
    per = random.randint(3, 9)
    bags = random.randint(2, 9)
    r = random.randint(1, per - 1)
    total = per * bags + r
    q = "有 %d 颗糖，每 %d 颗装一袋，能装满几袋？还剩几颗？" % (total, per)
    return {
        "question": q,
        "steps": [{"hint": "%d ÷ %d 商是几（装满的袋数）？" % (total, per), "answer": str(bags)},
                  {"hint": "余数是几（剩下的颗数）？", "answer": str(r)}],
        "answers": [{"label": "装满（袋）", "value": str(bags)},
                    {"label": "还剩（颗）", "value": str(r)}],
        "answer_display": "装满 %d 袋，还剩 %d 颗" % (bags, r),
        "solution": ["思路（易错点）：装满的袋数是商（单位：袋），余下的糖是余数（单位：颗），"
                     "单位不同不能混在一起；余数必须比除数小。",
                     "%d ÷ %d = %d（袋）……%d（颗）。答：能装满 %d 袋，还剩 %d 颗。"
                     % (total, per, bags, r, bags, r)],
    }


_CYCLE_SCHEMES = [("红、黄、蓝", 3), ("红、黄、蓝、绿", 4), ("紫、白、红、蓝、黄", 5)]


def _w2_cycle():
    """周期规律（易错：整除时正好是组内最后一面）"""
    scheme, k = random.choice(_CYCLE_SCHEMES)
    n = random.randint(10, 60)
    pos = (n - 1) % k + 1
    q = "广场上按 %s 的顺序循环挂彩旗，第 %d 面彩旗是它所在这一组中的第几面？" % (scheme, n)
    return {
        "question": q,
        "steps": [{"hint": "先算 %d ÷ %d，商是几（组数）？" % (n, k), "answer": str(n // k)},
                  {"hint": "余数是几？（余 0 时正好是组内最后一面）", "answer": str(n % k)},
                  {"hint": "所以第 %d 面是这一组中的第几面？" % n, "answer": str(pos)}],
        "answers": [{"label": "组内第几面", "value": str(pos)}],
        "answer_display": "组内第 %d 面" % pos,
        "solution": ["思路（易错点）：用序号除以每组的面数，余几就是组内第几面；"
                     "正好整除（余 0）时是这一组的最后一面，不是第 0 面。",
                     "%d ÷ %d = %d（组）……%d（面），所以是组内第 %d 面。"
                     "答：第 %d 面彩旗是它所在这一组中的第 %d 面。"
                     % (n, k, n // k, n % k, pos, n, pos)],
    }


def _w2_bignum():
    """万以内的数（二下生活中的大数）"""
    n1 = random.randint(300, 3000)
    diff = random.randint(50, n1 // 2)
    n2 = n1 - diff
    total = n1 + n2
    q = ("一台洗衣机 %d 元，比一辆自行车贵 %d 元。一辆自行车多少元？"
         "买一台洗衣机和一辆自行车一共要多少元？" % (n1, diff))
    return {
        "question": q,
        "steps": [{"hint": "洗衣机贵，自行车便宜。自行车多少元？", "answer": str(n2)},
                  {"hint": "两样各买一件一共多少元？", "answer": str(total)}],
        "answers": [{"label": "自行车（元）", "value": str(n2)},
                    {"label": "一共（元）", "value": str(total)}],
        "answer_display": "自行车 %d 元，一共 %d 元" % (n2, total),
        "solution": ["思路：\"比自行车贵\"说明自行车的价钱少，用减法求自行车的价钱，再相加求总价。",
                     "自行车：%d - %d = %d（元），一共：%d + %d = %d（元）。"
                     "答：一辆自行车 %d 元，一共要 %d 元。"
                     % (n1, diff, n2, n1, n2, total, n2, total)],
    }


def _w2_tail():
    """去尾问题（易错：剩下的钱不够再买一个也多算）"""
    total = random.choice([50, 80, 100])
    price = random.randint(8, 30)
    cnt = total // price
    left = total - cnt * price
    q = "%s有 %d 元，每支钢笔 %d 元，他最多能买几支钢笔？还剩多少元？" \
        % (_name(), total, price)
    return {
        "question": q,
        "steps": [{"hint": "%d 元里最多有几个 %d 元（商是几）？" % (total, price), "answer": str(cnt)},
                  {"hint": "还剩下多少元？", "answer": str(left)}],
        "answers": [{"label": "最多买（支）", "value": str(cnt)},
                    {"label": "还剩（元）", "value": str(left)}],
        "answer_display": "最多买 %d 支，还剩 %d 元" % (cnt, left),
        "solution": ["思路（易错点）：剩下的钱不够再买一支时，只能舍去（去尾法），"
                     "不能把剩下的钱再凑成一支。",
                     "%d ÷ %d = %d（支）……%d（元）。答：最多买 %d 支，还剩 %d 元。"
                     % (total, price, cnt, left, cnt, left)],
    }


# ---------- 三年级补充 ----------

def _w3_lcmul():
    """连乘应用（三上\"买矿泉水\"式两步连乘）"""
    per_box = random.randint(4, 12)
    price = random.randint(2, 8)
    boxes = random.randint(2, 9)
    one_box = per_box * price
    total = one_box * boxes
    q = "矿泉水每箱 %d 瓶，每瓶 %d 元。学校买来 %d 箱矿泉水，一共要多少元？" \
        % (per_box, price, boxes)
    return {
        "question": q,
        "steps": [{"hint": "先算一箱矿泉水要多少元？", "answer": str(one_box)},
                  {"hint": "再算 %d 箱一共要多少元？" % boxes, "answer": str(total)}],
        "answers": [{"label": "一共（元）", "value": str(total)}],
        "answer_display": "一共要 %d 元" % total,
        "solution": ["思路：先求一箱的价钱（每箱瓶数 × 每瓶价钱），再乘箱数（连乘）。",
                     "一箱：%d × %d = %d（元），一共：%d × %d = %d（元）。答：一共要 %d 元。"
                     % (per_box, price, one_box, one_box, boxes, total, total)],
    }


_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # 平年每月天数


def _w3_year():
    """年月日（易错：大小月天数记错、跨月不会推算）"""
    m = random.randint(1, 12)
    d = random.randint(1, 25)
    days = random.randint(5, 25)
    # 出发当天不算，从 a 月 b 日起再过 days 天到几月几日
    em, ed = m, d + days
    while ed > _MONTH_DAYS[em - 1]:
        ed -= _MONTH_DAYS[em - 1]
        em = em + 1 if em < 12 else 1
    q = "爸爸从 %d 月 %d 日出发去出差，一共去了 %d 天（出发当天不算）。他是几月几日回来的？" \
        % (m, d, days)
    return {
        "question": q,
        "steps": [{"hint": "%d 月是大月还是小月？它一共有多少天？"
                   % m, "answer": str(_MONTH_DAYS[m - 1])},
                  {"hint": "从 %d 日再过 %d 天，是 %d 月 %d 日，他是几月几日回来的？"
                   % (d, days, em, ed), "answer": "%d月%d日" % (em, ed)}],
        "answers": [{"label": "几月", "value": str(em)},
                    {"label": "几日", "value": str(ed)}],
        "answer_display": "%d 月 %d 日" % (em, ed),
        "solution": ["思路：先把 %d 月剩下的天数数完（%d 月共 %d 天，还剩 %d 天），"
                     "再继续数下一个月。"
                     % (m, m, _MONTH_DAYS[m - 1], _MONTH_DAYS[m - 1] - d),
                     "再数 %d 天落在 %d 月 %d 日。答：他是 %d 月 %d 日回来的。"
                     % (days, em, ed, em, ed)],
    }


def _w3_decintro():
    """小数初步（三上认识小数：元角分与小数）"""
    n = _name()
    money = random.randint(10, 30)
    ip = random.randint(5, money - 2)
    dp = random.randint(1, 9)
    price = ip + dp / 10.0
    left = round(money - price, 1)
    q = "%s有 %d 元，买一支钢笔用了 %.1f 元，还剩多少元？" % (n, money, price)
    return {
        "question": q,
        "steps": [{"hint": "带的钱 - 钢笔的价钱 = 还剩的钱。还剩多少元？",
                   "answer": "%.1f" % left}],
        "answers": [{"label": "还剩（元）", "value": "%.1f" % left}],
        "answer_display": "还剩 %.1f 元" % left,
        "solution": ["思路：%d 元可以看成 %d.0 元，小数点对齐再相减。"
                     % (money, money),
                     "%d.0 - %.1f = %.1f（元）。答：还剩 %.1f 元。"
                     % (money, price, left, left)],
    }


def _w3_areaunit():
    """面积单位换算（易错：面积单位进率 100 弄错）"""
    kind = random.randint(0, 2)
    if kind == 0:
        m = random.randint(2, 9)
        dm = random.randint(2, 9)
        length = m * 10
        area = length * dm
        q = "一块长方形木板长 %d 米、宽 %d 分米，它的面积是多少平方分米？" % (m, dm)
        return {
            "question": q,
            "steps": [{"hint": "1 米 = 10 分米，长是多少分米？", "answer": str(length)},
                      {"hint": "单位统一后，长 × 宽，面积是多少平方分米？", "answer": str(area)}],
            "answers": [{"label": "面积（平方分米）", "value": str(area)}],
            "answer_display": "面积是 %d 平方分米" % area,
            "solution": ["思路（易错点）：长和宽的单位不同，先统一单位再相乘；"
                         "面积单位进率是 100，不是 10。",
                         "%d 米 = %d 分米，面积 = %d × %d = %d（平方分米）。"
                         "答：面积是 %d 平方分米。" % (m, length, length, dm, area, area)],
        }
    if kind == 1:
        a = random.randint(4, 15)
        b = random.randint(3, 9)
        area = a * b
        sqdm = area * 100
        q = ("一块长方形菜地长 %d 米、宽 %d 米，它的面积是多少平方米？"
             "合多少平方分米？" % (a, b))
        return {
            "question": q,
            "steps": [{"hint": "先算面积：长 × 宽，面积是多少平方米？", "answer": str(area)},
                      {"hint": "1 平方米 = 100 平方分米，合多少平方分米？", "answer": str(sqdm)}],
            "answers": [{"label": "面积（平方米）", "value": str(area)},
                        {"label": "合（平方分米）", "value": str(sqdm)}],
            "answer_display": "%d 平方米，合 %d 平方分米" % (area, sqdm),
            "solution": ["思路（易错点）：平方米与平方分米之间的进率是 100。",
                         "面积：%d × %d = %d（平方米），%d × 100 = %d（平方分米）。"
                         "答：面积是 %d 平方米，合 %d 平方分米。"
                         % (a, b, area, area, sqdm, area, sqdm)],
        }
    a = random.randint(3, 12)
    b = random.randint(2, 9)
    area = a * b
    sqcm = area * 100
    q = ("一张长方形卡片长 %d 分米、宽 %d 分米，它的面积是多少平方分米？"
         "合多少平方厘米？" % (a, b))
    return {
        "question": q,
        "steps": [{"hint": "先算面积：长 × 宽，面积是多少平方分米？", "answer": str(area)},
                  {"hint": "1 平方分米 = 100 平方厘米，合多少平方厘米？", "answer": str(sqcm)}],
        "answers": [{"label": "面积（平方分米）", "value": str(area)},
                    {"label": "合（平方厘米）", "value": str(sqcm)}],
        "answer_display": "%d 平方分米，合 %d 平方厘米" % (area, sqcm),
        "solution": ["思路（易错点）：平方分米与平方厘米之间的进率是 100。",
                     "面积：%d × %d = %d（平方分米），%d × 100 = %d（平方厘米）。"
                     "答：面积是 %d 平方分米，合 %d 平方厘米。"
                     % (a, b, area, area, sqcm, area, sqcm)],
    }


def _w3_muldiv():
    """乘除混合两步应用（三下）"""
    while True:
        per = random.randint(4, 12)
        boxes = random.randint(2, 6)
        total = per * boxes
        divs = [d for d in range(3, 9) if d != per and total % d == 0]
        if divs:
            break
    classes = random.choice(divs)
    each = total // classes
    q = "商店运来 %d 箱苹果，每箱 %d 个。把这些苹果平均分给 %d 个班，每班分到多少个？" \
        % (boxes, per, classes)
    return {
        "question": q,
        "steps": [{"hint": "先算苹果一共有多少个？", "answer": str(total)},
                  {"hint": "再平均分给 %d 个班，每班分到多少个？" % classes,
                   "answer": str(each)}],
        "answers": [{"label": "每班（个）", "value": str(each)}],
        "answer_display": "每班分到 %d 个" % each,
        "solution": ["思路：先用乘法求出总个数，再平均分（除法）。",
                     "一共：%d × %d = %d（个），每班：%d ÷ %d = %d（个）。"
                     "答：每班分到 %d 个。" % (boxes, per, total, total, classes, each, each)],
    }


# ---------- 四年级补充 ----------

def _w4_bignum():
    """大数组成（四上认识更大的数，易错：万级与个级混淆）"""
    w = random.randint(2, 99)
    g = random.randint(1, 9999)
    num = w * 10000 + g
    q = "一个数由 %d 个万和 %d 个一组成，这个数是多少？" % (w, g)
    return {
        "question": q,
        "steps": [{"hint": "%d 个万表示多少？" % w, "answer": str(w * 10000)},
                  {"hint": "再加上 %d 个一，这个数是多少？" % g, "answer": str(num)}],
        "answers": [{"label": "这个数", "value": str(num)}],
        "answer_display": "这个数是 %d" % num,
        "solution": ["思路：万级上的数表示多少个万，写数时万级写 %d、个级写 %04d。"
                     % (w, g),
                     "%d 个万是 %d，加上 %d 个一，这个数是 %d。答：这个数是 %d。"
                     % (w, w * 10000, g, num, num)],
    }


def _w4_distrlaw():
    """运算律应用（四上运算律，易错：乘法分配律用错）"""
    a = random.randint(15, 60)
    b = random.randint(5, a // 2)
    c = random.randint(10, 50)
    if random.random() < 0.5:
        total = (a + b) * c
        q = "一套校服中上衣 %d 元、裤子 %d 元。学校给合唱队买了 %d 套，一共要多少元？" \
            % (a, b, c)
        return {
            "question": q,
            "steps": [{"hint": "先算一套校服多少元？", "answer": str(a + b)},
                      {"hint": "再算 %d 套一共多少元？（相当于（%d + %d）× %d）"
                       % (c, a, b, c), "answer": str(total)}],
            "answers": [{"label": "一共（元）", "value": str(total)}],
            "answer_display": "一共要 %d 元" % total,
            "solution": ["思路（乘法分配律）：（上衣 + 裤子）× 套数 = 上衣×套数 + 裤子×套数。",
                         "一套：%d + %d = %d（元），一共：%d × %d = %d（元）。"
                         "答：一共要 %d 元。" % (a, b, a + b, a + b, c, total, total)],
        }
    total = (a + c) * b
    q = ("两块长方形菜地的宽都是 %d 米，一块长 %d 米，另一块长 %d 米。"
         "两块菜地的面积一共是多少平方米？" % (b, a, c))
    return {
        "question": q,
        "steps": [{"hint": "宽相同，两块地可以拼成一个大长方形，长一共是多少米？",
                   "answer": str(a + c)},
                  {"hint": "大长方形的长 × 宽，两块地的面积一共是多少？", "answer": str(total)}],
        "answers": [{"label": "一共（平方米）", "value": str(total)}],
        "answer_display": "一共 %d 平方米" % total,
        "solution": ["思路（易错点）：宽相同时，总面积 =（长 + 长）× 宽，这正是乘法分配律。",
                     "（%d + %d）× %d = %d × %d = %d（平方米）。答：两块菜地的面积一共 %d 平方米。"
                     % (a, c, b, a + c, b, total, total)],
    }


def _w4_triangle():
    """三角形边角（易错：内角和 180 度、等腰两个底角相等）"""
    if random.random() < 0.5:
        a = random.randint(30, 80)
        b = random.randint(25, 180 - a - 20)
        c3 = 180 - a - b
        q = "在一个三角形中，∠1 是 %d 度，∠2 是 %d 度，∠3 是多少度？" % (a, b)
        return {
            "question": q,
            "steps": [{"hint": "三角形的内角和是 180 度，∠3 是多少度？", "answer": str(c3)}],
            "answers": [{"label": "∠3（度）", "value": str(c3)}],
            "answer_display": "∠3 是 %d 度" % c3,
            "solution": ["思路：任意三角形的内角和都是 180 度。",
                         "180 - %d - %d = %d（度）。答：∠3 是 %d 度。" % (a, b, c3, c3)],
        }
    base = random.randint(30, 70)
    top = 180 - 2 * base
    q = "一个等腰三角形的一个底角是 %d 度，它的顶角是多少度？" % base
    return {
        "question": q,
        "steps": [{"hint": "等腰三角形的两个底角相等，两个底角一共是多少度？",
                   "answer": str(2 * base)},
                  {"hint": "顶角 = 180 度 - 两个底角的和，顶角是多少度？", "answer": str(top)}],
        "answers": [{"label": "顶角（度）", "value": str(top)}],
        "answer_display": "顶角是 %d 度" % top,
        "solution": ["思路（易错点）：等腰三角形的两个底角相等，顶角 = 180 - 底角 × 2，"
                     "不要只减一个底角。",
                     "180 - %d × 2 = %d（度）。答：顶角是 %d 度。" % (base, top, top)],
    }


def _w4_decadd():
    """小数加减混合（易错：小数点没对齐）"""
    if random.random() < 0.5:
        money = random.randint(30, 50)
        p1 = random.randint(5, 18) + random.randint(0, 9) / 10.0
        p2 = random.randint(2, 10) + random.randint(0, 9) / 10.0
        total = round(p1 + p2, 1)
        left = round(money - total, 1)
        q = "%s带了 %d 元，买一个笔袋用去 %.1f 元，买一盒彩笔用去 %.1f 元，还剩多少元？" \
            % (_name(), money, p1, p2)
        return {
            "question": q,
            "steps": [{"hint": "先算两种文具一共用去多少元？", "answer": "%.1f" % total},
                      {"hint": "再用带的钱减去用去的，还剩多少元？", "answer": "%.1f" % left}],
            "answers": [{"label": "还剩（元）", "value": "%.1f" % left}],
            "answer_display": "还剩 %.1f 元" % left,
            "solution": ["思路（易错点）：小数加减要把小数点对齐，整数部分的元要补上小数点。",
                         "一共：%.1f + %.1f = %.1f（元），还剩：%d - %.1f = %.1f（元）。"
                         "答：还剩 %.1f 元。" % (p1, p2, total, money, total, left, left)],
        }
    p1 = random.randint(8, 18) + random.randint(0, 9) / 10.0
    d_int = random.randint(1, 5)
    d_dec = random.randint(0, 9)
    while p1 <= d_int + d_dec / 10.0:
        d_dec = random.randint(0, 9)
    diff = d_int + d_dec / 10.0
    p2 = round(p1 - diff, 1)
    total = round(p1 + p2, 1)
    q = "一个笔袋 %.1f 元，比一盒彩笔贵 %.1f 元。一盒彩笔多少元？两样各买一个一共要多少元？" \
        % (p1, diff)
    return {
        "question": q,
        "steps": [{"hint": "笔袋贵、彩笔便宜，一盒彩笔多少元？", "answer": "%.1f" % p2},
                  {"hint": "两样各买一个一共要多少元？", "answer": "%.1f" % total}],
        "answers": [{"label": "彩笔（元）", "value": "%.1f" % p2},
                    {"label": "一共（元）", "value": "%.1f" % total}],
        "answer_display": "彩笔 %.1f 元，一共 %.1f 元" % (p2, total),
        "solution": ["思路（易错点）：\"笔袋比彩笔贵\"说明彩笔便宜，求彩笔的价钱用减法。",
                     "彩笔：%.1f - %.1f = %.1f（元），一共：%.1f + %.1f = %.1f（元）。"
                     "答：一盒彩笔 %.1f 元，两样一共 %.1f 元。"
                     % (p1, diff, p2, p1, p2, total, p2, total)],
    }


# ---------- 五年级补充 ----------

def _w5_decdiv():
    """小数除法应用（五上小数除法，易错：商的小数点位置）"""
    n = _name()
    while True:
        cnt = random.choice([5, 10, 20, 25])
        ip = random.randint(1, 9)
        dp = random.randint(0, 9)
        per = ip + dp / 10.0
        total = per * cnt
        if abs(total - round(total)) < 1e-9:
            total = int(round(total))
            break
    q = "%s买了 %d 个苹果，一共重 %d 千克。平均每个苹果重多少千克？" % (n, cnt, total)
    return {
        "question": q,
        "steps": [{"hint": "把 %d 千克平均分成 %d 份，每个苹果重多少千克？" % (total, cnt),
                   "answer": "%.1f" % per}],
        "answers": [{"label": "每个（千克）", "value": "%.1f" % per}],
        "answer_display": "平均每个重 %.1f 千克" % per,
        "solution": ["思路（易错点）：小数除以整数，商的小数点要和被除数的小数点对齐。",
                     "%d ÷ %d = %.1f（千克）。答：平均每个苹果重 %.1f 千克。"
                     % (total, cnt, per, per)],
    }


def _w5_roundtail():
    """进一法与去尾法对比（易错：该进一的去尾、该去尾的进一）"""
    if random.random() < 0.5:
        per = random.randint(4, 12)
        qn = random.randint(3, 9)
        r = random.randint(1, per - 1)
        people = qn * per + r
        need = qn + 1
        q = "%d 名游客乘坐缆车，每辆车限乘 %d 人，至少需要多少辆车？" % (people, per)
        return {
            "question": q,
            "steps": [{"hint": "%d ÷ %d = %d（辆）……%d（人），剩下的 %d 人也要坐车，至少要几辆？"
                       % (people, per, qn, r, r), "answer": str(need)}],
            "answers": [{"label": "至少（辆）", "value": str(need)}],
            "answer_display": "至少需要 %d 辆" % need,
            "solution": ["思路（易错点）：剩下的人也要坐车，车辆数要用\"进一法\"加 1，"
                         "不能把余下的人舍去。",
                         "%d ÷ %d = %d（辆）……%d（人），所以至少要 %d + 1 = %d 辆。"
                         "答：至少需要 %d 辆车。" % (people, per, qn, r, qn, need, need)],
        }
    money10 = random.randint(200, 600)      # 钱数（角）
    price10 = random.randint(35, 99)         # 单价（角）
    cnt = money10 // price10
    left10 = money10 - cnt * price10
    left = left10 / 10.0
    money = money10 / 10.0
    price = price10 / 10.0
    q = "%s有 %.1f 元，每支钢笔 %.1f 元，最多能买几支钢笔？还剩多少元？" \
        % (_name(), money, price)
    return {
        "question": q,
        "steps": [{"hint": "钱数里最多有几个单价（商是几）？", "answer": str(cnt)},
                  {"hint": "剩下的钱不够再买一支（去尾），还剩多少元？", "answer": "%.1f" % left}],
        "answers": [{"label": "最多买（支）", "value": str(cnt)},
                    {"label": "还剩（元）", "value": "%.1f" % left}],
        "answer_display": "最多买 %d 支，还剩 %.1f 元" % (cnt, left),
        "solution": ["思路（易错点）：剩下的钱不够再买一支时要用\"去尾法\"，"
                     "不能进一凑成一支。",
                     "%.1f ÷ %.1f = %d（支）……%.1f（元）。答：最多能买 %d 支，还剩 %.1f 元。"
                     % (money, price, cnt, left, cnt, left)],
    }


def _w5_fracadd():
    """分数加减应用（五下分数加减法，易错：分母不同不能直接相加减）"""
    kind = random.randint(0, 1)
    if kind == 0:
        d = random.randint(4, 12)
        a1 = random.randint(1, d - 2)
        a2 = random.randint(1, d - a1 - 1)
        eaten = a1 + a2
        left = d - eaten
        q = ("一张饼，妈妈吃了它的 %d/%d，爸爸吃了它的 %d/%d。"
             "两人一共吃了这张饼的几分之几？还剩几分之几？" % (a1, d, a2, d))
        return {
            "question": q,
            "steps": [{"hint": "分母相同，分子直接相加，一共吃了几分之几？",
                       "answer": "%d/%d" % (eaten, d)},
                      {"hint": "把整张饼看作 %d/%d，还剩几分之几？" % (d, d),
                       "answer": "%d/%d" % (left, d)}],
            "answers": [{"label": "一共吃了", "value": "%d/%d" % (eaten, d)},
                        {"label": "还剩", "value": "%d/%d" % (left, d)}],
            "answer_display": "一共吃了 %d/%d，还剩 %d/%d" % (eaten, d, left, d),
            "solution": ["思路：分母相同的分数相加减，分母不变、分子相加减。",
                         "%d/%d + %d/%d = %d/%d，%d/%d - %d/%d = %d/%d。"
                         "答：两人一共吃了这张饼的 %d/%d，还剩 %d/%d。"
                         % (a1, d, a2, d, eaten, d, d, d, eaten, d, left, d,
                            eaten, d, left, d)],
        }
    d1 = random.randint(2, 6)
    k = random.choice([2, 3])
    d2 = k * d1
    a1 = random.randint(1, d1 - 1)
    a2 = random.randint(1, d2 - k * a1 - 1)
    s = a1 * k + a2
    left = d2 - s
    q = ("一瓶果汁，哥哥喝了它的 %d/%d，妹妹喝了它的 %d/%d。"
         "两人一共喝了几分之几？瓶里还剩几分之几？" % (a1, d1, a2, d2))
    return {
        "question": q,
        "steps": [{"hint": "先通分：%d/%d = 多少/%d？" % (a1, d1, d2),
                   "answer": "%d/%d" % (a1 * k, d2)},
                  {"hint": "通分后分子相加，两人一共喝了几分之几？", "answer": "%d/%d" % (s, d2)},
                  {"hint": "一瓶果汁看作 %d/%d，还剩几分之几？" % (d2, d2),
                   "answer": "%d/%d" % (left, d2)}],
        "answers": [{"label": "一共喝了", "value": "%d/%d" % (s, d2)},
                    {"label": "还剩", "value": "%d/%d" % (left, d2)}],
        "answer_display": "一共喝了 %d/%d，还剩 %d/%d" % (s, d2, left, d2),
        "solution": ["思路（易错点）：分母不同的分数不能直接相加减，要先通分再算。",
                     "%d/%d = %d/%d，%d/%d + %d/%d = %d/%d，还剩 %d/%d。"
                     "答：两人一共喝了 %d/%d，瓶里还剩 %d/%d。"
                     % (a1, d1, a1 * k, d2, a1 * k, d2, a2, d2, s, d2, left, d2,
                        s, d2, left, d2)],
    }


def _w5_volume():
    """体积与容积（易错：体积单位与容积单位的换算）"""
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    c = random.randint(2, 10)
    v = a * b * c
    if random.random() < 0.5:
        q = ("一个长方体水箱从里面量长 %d 分米、宽 %d 分米、高 %d 分米，"
             "它的容积是多少升？" % (a, b, c))
        return {
            "question": q,
            "steps": [{"hint": "长方体的容积 = 长 × 宽 × 高，是多少立方分米？", "answer": str(v)},
                      {"hint": "1 立方分米 = 1 升，合多少升？", "answer": str(v)}],
            "answers": [{"label": "容积（升）", "value": str(v)}],
            "answer_display": "容积是 %d 升" % v,
            "solution": ["思路（易错点）：求容积要从里面量；1 立方分米 = 1 升。",
                         "%d × %d × %d = %d（立方分米）= %d 升。答：它的容积是 %d 升。"
                         % (a, b, c, v, v, v)],
        }
    q = ("一个长方体纸盒长 %d 分米、宽 %d 分米、高 %d 分米，"
         "它的体积是多少立方分米？合多少立方厘米？" % (a, b, c))
    sqcm = v * 1000
    return {
        "question": q,
        "steps": [{"hint": "长方体的体积 = 长 × 宽 × 高，是多少立方分米？", "answer": str(v)},
                  {"hint": "1 立方分米 = 1000 立方厘米，合多少立方厘米？", "answer": str(sqcm)}],
        "answers": [{"label": "体积（立方分米）", "value": str(v)},
                    {"label": "合（立方厘米）", "value": str(sqcm)}],
        "answer_display": "体积是 %d 立方分米，合 %d 立方厘米" % (v, sqcm),
        "solution": ["思路（易错点）：立方分米与立方厘米之间的进率是 1000，不是 100。",
                     "%d × %d × %d = %d（立方分米），%d × 1000 = %d（立方厘米）。"
                     "答：体积是 %d 立方分米，合 %d 立方厘米。"
                     % (a, b, c, v, v, sqcm, v, sqcm)],
    }


def _w5_displace():
    """排水法（易错：上升部分水的体积就是物体的体积）"""
    base = random.randint(20, 100)
    rise = random.randint(1, 10)
    v = base * rise
    q = ("一个长方体水缸的底面积是 %d 平方厘米，把一块石头完全浸入水中"
         "（水没有溢出），水面上升了 %d 厘米。这块石头的体积是多少立方厘米？" % (base, rise))
    return {
        "question": q,
        "steps": [{"hint": "水面上升部分的水的体积就是石头的体积：底面积 × 上升的高度，"
                   "体积是多少？", "answer": str(v)}],
        "answers": [{"label": "体积（立方厘米）", "value": str(v)}],
        "answer_display": "体积是 %d 立方厘米" % v,
        "solution": ["思路（易错点）：石头浸入水中排开了同样体积的水，"
                     "石头的体积 = 底面积 × 水面上升的高度。",
                     "%d × %d = %d（立方厘米）。答：这块石头的体积是 %d 立方厘米。"
                     % (base, rise, v, v)],
    }


def _w5_equation():
    """列方程应用（五下用方程解决问题，易错：等量关系找错）"""
    n = _name()
    m = _name()
    while m == n:
        m = _name()
    x = random.randint(3, 15)       # 小红的支数（方程的解）
    k = random.randint(2, 5)
    c = random.randint(1, 6)
    a = k * x + c                   # 小明的支数
    q = "%s有 %d 支铅笔，比%s铅笔数的 %d 倍还多 %d 支。%s有多少支铅笔？" \
        % (n, a, m, k, c, m)
    return {
        "question": q,
        "steps": [{"hint": "设%s有 x 支铅笔，列方程：%d × x + %d = %d，x 是多少？"
                   % (m, k, c, a), "answer": str(x)}],
        "answers": [{"label": "铅笔（支）", "value": str(x)}],
        "answer_display": "%s有 %d 支铅笔" % (m, x),
        "solution": ["思路（列方程）：设%s有 x 支铅笔，等量关系是\"%s的铅笔数 × %d + %d = %s的支数\"。"
                     % (m, m, k, c, n),
                     "列方程：%dx + %d = %d，解得 x =（%d - %d）÷ %d = %d。"
                     "答：%s有 %d 支铅笔。"
                     % (k, c, a, a, c, k, x, m, x)],
    }


# ---------- 六年级补充 ----------

def _w6_sqcircle():
    """外方内圆（易错：剩下的部分 = 正方形面积 - 圆面积）"""
    r = random.randint(2, 30)
    side = 2 * r
    sq = side * side
    circle = 3.14 * r * r
    rest = round(sq - circle, 2)
    q = ("在一个边长 %d 厘米的正方形里画一个最大的圆（π 取 3.14）。"
         "正方形去掉圆后剩下四个角，剩下的面积是多少平方厘米？" % side)
    return {
        "question": q,
        "steps": [{"hint": "正方形的面积是多少平方厘米？", "answer": str(sq)},
                  {"hint": "最大的圆的直径等于正方形的边长，半径是 %d 厘米，圆的面积是多少？"
                   % r, "answer": "%.2f" % circle},
                  {"hint": "剩下的面积 = 正方形面积 - 圆面积，剩下多少平方厘米？",
                   "answer": "%.2f" % rest}],
        "answers": [{"label": "剩下（平方厘米）", "value": "%.2f" % rest}],
        "answer_display": "剩下的面积是 %.2f 平方厘米" % rest,
        "solution": ["思路（易错点）：最大的圆的直径等于正方形的边长；"
                     "剩下的面积 = 正方形面积 - 圆面积。",
                     "正方形：%d × %d = %d（平方厘米），圆：3.14 × %d × %d = %.2f（平方厘米），"
                     "剩下：%d - %.2f = %.2f（平方厘米）。答：剩下的面积是 %.2f 平方厘米。"
                     % (side, side, sq, r, r, circle, sq, circle, rest, rest)],
    }


def _w6_pctunit():
    """已知部分求单位\"1\"（易错：单位\"1\"未知时该除算成乘）"""
    t = random.randint(2, 60)
    pct = random.choice([5, 10, 20, 25, 40, 50, 75, 80])
    total = t * 100
    rest = t * pct
    done_pct = 100 - pct
    q = "一辆汽车从甲地开往乙地，已经行驶了全程的 %d%%，离乙地还有 %d 千米。甲、乙两地相距多少千米？" \
        % (done_pct, rest)
    return {
        "question": q,
        "steps": [{"hint": "把全程看作单位\"1\"，已经行驶 %d%%，剩下的占全程的百分之几？"
                   % done_pct, "answer": str(pct)},
                  {"hint": "已知全程的 %d%% 是 %d 千米，单位\"1\"未知用除法，全程是多少千米？"
                   % (pct, rest), "answer": str(total)}],
        "answers": [{"label": "全程（千米）", "value": str(total)}],
        "answer_display": "甲、乙两地相距 %d 千米" % total,
        "solution": ["思路（易错点）：\"已经行驶 %d%%\"说明还剩下 %d%%；"
                     "单位\"1\"（全程）未知时要用除法，不要用乘法。"
                     % (done_pct, pct),
                     "%d ÷ %d%% = %d × 100 ÷ %d = %d（千米）。答：甲、乙两地相距 %d 千米。"
                     % (rest, pct, rest, pct, total, total)],
    }


def _w6_mixfrac():
    """分数混合应用（六上分数混合运算，两步分率）"""
    while True:
        d1 = random.randint(2, 9)
        d2 = random.randint(2, 9)
        # 排除 1/2 + 1/2 = 1（会剩下 0 页）的组合
        if not (d1 == 2 and d2 == 2):
            break
    lcm = d1 * d2 // _gcd(d1, d2)
    pages = lcm * random.randint(2, 20)
    p1 = pages // d1
    p2 = pages // d2
    rest = pages - p1 - p2
    q = ("一本书共 %d 页，第一天读了全书的 1/%d，第二天读了全书的 1/%d，"
         "还剩多少页没有读？" % (pages, d1, d2))
    return {
        "question": q,
        "steps": [{"hint": "第一天读了多少页？", "answer": str(p1)},
                  {"hint": "第二天读了多少页？", "answer": str(p2)},
                  {"hint": "从总页数里去掉两天读的页数，还剩多少页？", "answer": str(rest)}],
        "answers": [{"label": "还剩（页）", "value": str(rest)}],
        "answer_display": "还剩 %d 页" % rest,
        "solution": ["思路：把全书总页数看作单位\"1\"，分别算出两天读的页数，再从总数里去掉。",
                     "第一天：%d ÷ %d = %d（页），第二天：%d ÷ %d = %d（页），"
                     "还剩：%d - %d - %d = %d（页）。答：还剩 %d 页没有读。"
                     % (pages, d1, p1, pages, d2, p2, pages, p1, p2, rest, rest)],
    }


def _w6_cyl():
    """圆柱体积（六下圆柱与圆锥）"""
    if random.random() < 0.5:
        r = random.randint(2, 10)
        h = random.randint(5, 30)
        q = "一个圆柱形水桶，底面半径 %d 厘米，高 %d 厘米，它的体积是多少立方厘米？（π 取 3.14）" \
            % (r, h)
    else:
        d = random.choice([4, 6, 8, 10, 12, 14, 16, 18, 20])
        r = d // 2
        h = random.randint(5, 30)
        q = "一个圆柱形立柱，底面直径 %d 厘米，高 %d 厘米，它的体积是多少立方厘米？（π 取 3.14）" \
            % (d, h)
    base = 3.14 * r * r
    v = 3.14 * r * r * h
    return {
        "question": q,
        "steps": [{"hint": "底面积 = π × 半径 × 半径，底面积是多少平方厘米？",
                   "answer": "%.2f" % base},
                  {"hint": "圆柱体积 = 底面积 × 高，体积是多少立方厘米？", "answer": "%.2f" % v}],
        "answers": [{"label": "体积（立方厘米）", "value": "%.2f" % v}],
        "answer_display": "体积是 %.2f 立方厘米" % v,
        "solution": ["思路：圆柱的体积 = 底面积 × 高。",
                     "底面积：3.14 × %d × %d = %.2f（平方厘米），"
                     "体积：%.2f × %d = %.2f（立方厘米）。答：它的体积是 %.2f 立方厘米。"
                     % (r, r, base, base, h, v, v)],
    }


def _w6_cone():
    """圆锥体积（易错：忘记乘 1/3）"""
    while True:
        r = random.randint(2, 12)
        h = random.randint(3, 24)
        if (r * r * h) % 3 == 0:
            break
    cyl_v = 3.14 * r * r * h
    v = cyl_v / 3
    q = ("一个圆锥形沙堆，底面半径 %d 厘米，高 %d 厘米，"
         "它的体积是多少立方厘米？（π 取 3.14）" % (r, h))
    return {
        "question": q,
        "steps": [{"hint": "先算与它同底等高的圆柱的体积，是多少立方厘米？",
                   "answer": "%.2f" % cyl_v},
                  {"hint": "圆锥体积是同底等高圆柱体积的 1/3，体积是多少立方厘米？",
                   "answer": "%.2f" % v}],
        "answers": [{"label": "体积（立方厘米）", "value": "%.2f" % v}],
        "answer_display": "体积是 %.2f 立方厘米" % v,
        "solution": ["思路（易错点）：圆锥的体积是与它同底等高的圆柱体积的 1/3，"
                     "不要忘除以 3。",
                     "圆柱体积：3.14 × %d × %d × %d = %.2f（立方厘米），"
                     "圆锥体积：%.2f ÷ 3 = %.2f（立方厘米）。答：它的体积是 %.2f 立方厘米。"
                     % (r, r, h, cyl_v, cyl_v, v, v)],
    }


def _w6_prop():
    """正比例与反比例（六下，易错：正反比例判断错）"""
    if random.random() < 0.5:
        # 正比例：单价一定，总价与数量成正比例
        per = random.randint(3, 15)
        k1 = random.randint(2, 6)
        k2 = random.randint(7, 15)
        t1 = per * k1
        t2 = per * k2
        q = "买 %d 千克苹果要 %d 元。照这样计算，买 %d 千克苹果要多少元？" % (k1, t1, k2)
        return {
            "question": q,
            "steps": [{"hint": "单价（总价 ÷ 数量）一定，总价与数量成正比例，单价是多少元？",
                       "answer": str(per)},
                      {"hint": "再算买 %d 千克要多少元？" % k2, "answer": str(t2)}],
            "answers": [{"label": "要付（元）", "value": str(t2)}],
            "answer_display": "要 %d 元" % t2,
            "solution": ["思路：单价一定（比值一定），总价与数量成正比例；"
                         "也可以列比例式：总价 ÷ 数量 = 单价。",
                         "单价：%d ÷ %d = %d（元），总价：%d × %d = %d（元）。"
                         "答：买 %d 千克苹果要 %d 元。" % (t1, k1, per, per, k2, t2, k2, t2)],
        }
    # 反比例：总量一定，每次运量与次数成反比例
    while True:
        a = random.randint(4, 12)
        b = random.randint(5, 20)
        total = a * b
        divs = [d for d in range(4, 17) if d != a and total % d == 0]
        if divs:
            break
    c2 = random.choice(divs)
    days2 = total // c2
    q = ("仓库要运出一批货物，每天运 %d 吨，%d 天正好运完。"
         "如果每天运 %d 吨，多少天可以运完？" % (a, b, c2))
    return {
        "question": q,
        "steps": [{"hint": "货物的总吨数不变：每天运的吨数 × 天数 = 总吨数，总吨数是多少？",
                   "answer": str(total)},
                  {"hint": "每天运 %d 吨时，多少天可以运完？" % c2, "answer": str(days2)}],
        "answers": [{"label": "运完（天）", "value": str(days2)}],
        "answer_display": "%d 天可以运完" % days2,
        "solution": ["思路（易错点）：总吨数一定（乘积一定），每天运的吨数与天数成反比例，"
                     "不是正比例。",
                     "总吨数：%d × %d = %d（吨），天数：%d ÷ %d = %d（天）。"
                     "答：每天运 %d 吨时，%d 天可以运完。" % (a, b, total, total, c2, days2, c2, days2)],
    }


def _w6_scale():
    """比例尺应用（六下比例）"""
    while True:
        cm = random.randint(2, 30)
        sc = random.choice([10000, 20000, 50000, 100000, 200000])
        actual_cm = cm * sc
        if actual_cm % 100000 == 0:
            break
    km = actual_cm // 100000
    q = "在比例尺为 1 : %d 的地图上，量得甲、乙两地的距离是 %d 厘米。甲、乙两地的实际距离是多少千米？" \
        % (sc, cm)
    return {
        "question": q,
        "steps": [{"hint": "实际距离 = 图上距离 × 比例尺的后项，实际是多少厘米？",
                   "answer": str(actual_cm)},
                  {"hint": "把厘米换算成千米：1 千米 = 100000 厘米，实际是多少千米？",
                   "answer": str(km)}],
        "answers": [{"label": "实际距离（千米）", "value": str(km)}],
        "answer_display": "实际距离是 %d 千米" % km,
        "solution": ["思路：比例尺 1 : %d 表示图上 1 厘米代表实际 %d 厘米。"
                     % (sc, sc),
                     "实际距离：%d × %d = %d（厘米）= %d（千米）。答：甲、乙两地的实际距离是 %d 千米。"
                     % (cm, sc, actual_cm, km, km)],
    }


# ================= 常见题模板（标准基础题型，与易错题区分） =================

def _c1_total_std():
    """求总数（常见：直接相加）"""
    n = _name()
    item = random.choice([("铅笔", "支"), ("橡皮", "块"), ("贴纸", "张"), ("糖果", "颗")])
    a = random.randint(2, 15)
    b = random.randint(1, 20 - a)
    total = a + b
    q = "%s有 %d %s，妈妈又给%s买了 %d %s，现在一共有多少%s？" \
        % (n, a, item[0], n, b, item[0], item[0])
    return {
        "question": q,
        "steps": [{"hint": "原有的加上新买的，一共是多少？", "answer": str(total)}],
        "answers": [{"label": "一共（%s）" % item[1], "value": str(total)}],
        "answer_display": "一共有 %d %s" % (total, item[1]),
        "solution": ["思路：求一共用加法。",
                     "%d + %d = %d（%s）。答：现在一共有 %d %s。"
                     % (a, b, total, item[1], total, item[0])],
    }


def _c1_left_std():
    """求剩余（常见：直接相减）"""
    n = _name()
    item = random.choice([("橘子", "个"), ("积木", "块"), ("卡片", "张"), ("气球", "个")])
    a = random.randint(5, 19)
    b = random.randint(1, a - 1)
    left = a - b
    q = "%s原来有 %d %s，送给同学 %d %s，还剩多少%s？" \
        % (n, a, item[0], b, item[0], item[0])
    return {
        "question": q,
        "steps": [{"hint": "送出的要从总数里去掉，还剩多少？", "answer": str(left)}],
        "answers": [{"label": "还剩（%s）" % item[1], "value": str(left)}],
        "answer_display": "还剩 %d %s" % (left, item[1]),
        "solution": ["思路：送走说明数量变少，用减法。",
                     "%d - %d = %d（%s）。答：还剩 %d %s。"
                     % (a, b, left, item[1], left, item[0])],
    }


def _c1_compare_std():
    """比多少（常见：求比一个数多几的数）"""
    n1 = _name()
    n2 = _name()
    while n2 == n1:
        n2 = _name()
    a = random.randint(3, 15)
    b = random.randint(1, 20 - a)
    big = a + b
    q = "%s跳绳跳了 %d 下，%s比%s多跳 %d 下，%s跳了多少下？" % (n1, a, n2, n1, b, n2)
    return {
        "question": q,
        "steps": [{"hint": "比%s多，就用%s的下数加上多的部分。" % (n1, n2),
                   "answer": str(big)}],
        "answers": [{"label": "跳绳（下）", "value": str(big)}],
        "answer_display": "%s跳了 %d 下" % (n2, big),
        "solution": ["思路：求比一个数多几的数用加法。",
                     "%d + %d = %d（下）。答：%s跳了 %d 下。" % (a, b, big, n2, big)],
    }


def _c1_diff_std():
    """比多少（常见：求两数相差多少）"""
    n1 = _name()
    n2 = _name()
    while n2 == n1:
        n2 = _name()
    a = random.randint(6, 20)
    b = random.randint(1, a - 1)
    diff = a - b
    q = "%s有 %d 支铅笔，%s有 %d 支铅笔，%s比%s多几支铅笔？" % (n1, a, n2, b, n1, n2)
    return {
        "question": q,
        "steps": [{"hint": "用多的减去少的，相差多少？", "answer": str(diff)}],
        "answers": [{"label": "多（支）", "value": str(diff)}],
        "answer_display": "%s比%s多 %d 支" % (n1, n2, diff),
        "solution": ["思路：求相差多少，用大数减小数。",
                     "%d - %d = %d（支）。答：%s比%s多 %d 支。"
                     % (a, b, diff, n1, n2, diff)],
    }


def _c1_pay_change():
    """购物找零（常见：付出的钱 - 商品价格）"""
    n = _name()
    price = random.randint(5, 45)
    paid = random.choice([t for t in (50, 100) if t > price] +
                         [t for t in (10, 20, 30, 40) if t > price])
    change = paid - price
    q = "%s买了一个书包花了 %d 元，付给售货员 %d 元，应找回多少元？" % (n, price, paid)
    return {
        "question": q,
        "steps": [{"hint": "付出的钱减去商品的价格，应找回多少元？", "answer": str(change)}],
        "answers": [{"label": "找回（元）", "value": str(change)}],
        "answer_display": "应找回 %d 元" % change,
        "solution": ["思路：找零 = 付出的钱 - 花掉的钱。",
                     "%d - %d = %d（元）。答：应找回 %d 元。" % (paid, price, change, change)],
    }


def _c1_dist_reverse():
    """求原来（常见：用去的 + 剩下的）"""
    n = _name()
    used = random.randint(3, 40)
    left = random.randint(3, 40)
    total = used + left
    q = "%s吃了一些饼干后还剩 %d 块，%s吃了 %d 块。篮子里原来有多少块饼干？" \
        % (n, left, n, used)
    return {
        "question": q,
        "steps": [{"hint": "吃掉的加上剩下的就是原来的，原来有多少块？", "answer": str(total)}],
        "answers": [{"label": "原来（块）", "value": str(total)}],
        "answer_display": "原来有 %d 块" % total,
        "solution": ["思路：求原来用加法：吃掉的 + 剩下的。",
                     "%d + %d = %d（块）。答：篮子里原来有 %d 块饼干。"
                     % (used, left, total, total)],
    }


def _c1_route():
    """连减应用（常见：总长 - 先修 - 后修）"""
    a = random.randint(50, 100)
    b = random.randint(10, a - 20)
    c = random.randint(10, a - b - 5)
    rest = a - b - c
    q = "一条路长 %d 米，第一天修了 %d 米，第二天修了 %d 米，还剩多少米没修？" % (a, b, c)
    return {
        "question": q,
        "steps": [{"hint": "两天一共修了多少米？", "answer": str(b + c)},
                  {"hint": "总长减去已修的，还剩多少米？", "answer": str(rest)}],
        "answers": [{"label": "还剩（米）", "value": str(rest)}],
        "answer_display": "还剩 %d 米没修" % rest,
        "solution": ["思路：从总长里去掉两天修的部分。",
                     "两天共修：%d + %d = %d（米），还剩：%d - %d = %d（米）。"
                     "答：还剩 %d 米没修。" % (b, c, b + c, a, b + c, rest, rest)],
    }


def _c1_twostep_std():
    """加减混合（常见：卖出再运进）"""
    item = random.choice(["牛奶", "饮料", "方便面"])
    a = random.randint(40, 90)
    b = random.randint(10, a - 10)
    c = random.randint(10, 50)
    now = a - b + c
    q = "商店原有 %d 箱%s，卖出 %d 箱，又运进 %d 箱。现在有多少箱%s？" \
        % (a, item, b, c, item)
    return {
        "question": q,
        "steps": [{"hint": "先算卖出后剩多少箱？", "answer": str(a - b)},
                  {"hint": "再加上又运进的，现在有多少箱？", "answer": str(now)}],
        "answers": [{"label": "现在（箱）", "value": str(now)}],
        "answer_display": "现在有 %d 箱" % now,
        "solution": ["思路：卖出用减法，运进用加法，按顺序算。",
                     "%d - %d = %d（箱），%d + %d = %d（箱）。答：现在有 %d 箱%s。"
                     % (a, b, a - b, a - b, c, now, now, item)],
    }


def _c2_mul_mean():
    """乘法含义（常见：每份数 × 份数）"""
    item = random.choice([("橘子", "个"), ("月饼", "块"), ("牛奶", "盒"), ("樱桃", "颗")])
    x = random.randint(2, 9)
    y = random.randint(2, 9)
    total = x * y
    q = "妈妈买了 %d 盘%s，每盘 %d %s，一共买了多少%s？" % (y, item[0], x, item[1], item[0])
    return {
        "question": q,
        "steps": [{"hint": "每盘的个数乘盘数，一共多少？", "answer": str(total)}],
        "answers": [{"label": "一共（%s）" % item[1], "value": str(total)}],
        "answer_display": "一共买了 %d %s" % (total, item[0]),
        "solution": ["思路：求几个相同加数的和，用乘法。",
                     "%d × %d = %d（%s）。答：一共买了 %d %s。"
                     % (x, y, total, item[1], total, item[0])],
    }


def _c2_avg_div():
    """平均分（常见：总数 ÷ 份数）"""
    n = _name()
    item = random.choice([("苹果", "个"), ("糖", "颗"), ("书签", "张")])
    per = random.randint(2, 9)
    people = random.randint(2, 9)
    total = per * people
    q = "%s有 %d %s，平均分给 %d 个小朋友，每人分得几个%s？" \
        % (n, total, item[0], people, item[0])
    return {
        "question": q,
        "steps": [{"hint": "总数除以人数，每人分几个？", "answer": str(per)}],
        "answers": [{"label": "每人（%s）" % item[1], "value": str(per)}],
        "answer_display": "每人分得 %d %s" % (per, item[1]),
        "solution": ["思路：平均分用除法。",
                     "%d ÷ %d = %d（%s）。答：每人分得 %d %s。"
                     % (total, people, per, item[1], per, item[1])],
    }


def _c2_beishu():
    """倍数关系（常见：求一个数的几倍）"""
    item = random.choice([("大熊猫", "只"), ("小白兔", "只"), ("金鱼", "条")])
    a = random.randint(2, 9)
    k = random.randint(2, 9)
    total = a * k
    q = "动物园里有 %d 只猴子，%s的只数是猴子的 %d 倍，%s有多少%s？" \
        % (a, item[0], k, item[0], item[1])
    return {
        "question": q,
        "steps": [{"hint": "求一个数的几倍用乘法，是多少？", "answer": str(total)}],
        "answers": [{"label": "%s（%s）" % (item[0], item[1]), "value": str(total)}],
        "answer_display": "%s有 %d %s" % (item[0], total, item[1]),
        "solution": ["思路：求一个数的几倍是多少，用乘法。",
                     "%d × %d = %d（%s）。答：%s有 %d %s。"
                     % (a, k, total, item[1], item[0], total, item[1])],
    }


def _c2_money_buy():
    """人民币购物（常见：单价 × 数量）"""
    item = random.choice([("笔记本", "本"), ("钢笔", "支"), ("橡皮", "块")])
    price = random.randint(2, 9)
    cnt = random.randint(2, 9)
    total = price * cnt
    q = "一本%s %d 元，买 %d 本一共需要多少元？" % (item[0], price, cnt)
    return {
        "question": q,
        "steps": [{"hint": "单价乘数量，一共多少元？", "answer": str(total)}],
        "answers": [{"label": "一共（元）", "value": str(total)}],
        "answer_display": "一共需要 %d 元" % total,
        "solution": ["思路：总价 = 单价 × 数量。",
                     "%d × %d = %d（元）。答：一共需要 %d 元。" % (price, cnt, total, total)],
    }


def _c2_remain_div():
    """有余数除法（常见：平均分后有余）"""
    n = _name()
    item = random.choice([("气球", "个"), ("纽扣", "颗"), ("贴纸", "张")])
    people = random.randint(3, 8)
    per = random.randint(2, 8)
    rest = random.randint(1, people - 1)
    total = per * people + rest
    q = "%s有 %d %s，平均分给 %d 个小朋友，每人分得几个%s，还剩几个%s？" \
        % (n, total, item[0], people, item[0], item[0])
    return {
        "question": q,
        "steps": [{"hint": "总数除以人数，商和余数各是多少？", "answer": "%d余%d" % (per, rest)}],
        "answers": [{"label": "每人（%s）" % item[1], "value": str(per)},
                    {"label": "还剩（%s）" % item[1], "value": str(rest)}],
        "answer_display": "每人分得 %d %s，还剩 %d %s" % (per, item[1], rest, item[1]),
        "solution": ["思路：平均分用除法，除不尽的部分是余数。",
                     "%d ÷ %d = %d（%s）……%d（%s）。答：每人分得 %d %s，还剩 %d %s。"
                     % (total, people, per, item[1], rest, item[1], per, item[1], rest, item[1])],
    }


def _c2_elapsed_std():
    """经过时间（常见：结束时刻 - 开始时刻）"""
    h1 = random.randint(8, 15)
    m1 = random.randint(0, 59)
    dur = random.randint(20, 120)
    t2 = h1 * 60 + m1 + dur
    h2, m2 = t2 // 60, t2 % 60
    q = "一辆汽车 %d 时 %d 分从甲地出发，%d 时 %d 分到达乙地。路上用了多少分钟？" \
        % (h1, m1, h2, m2)
    return {
        "question": q,
        "steps": [{"hint": "结束时刻减开始时刻，经过多少分钟？", "answer": str(dur)}],
        "answers": [{"label": "经过（分钟）", "value": str(dur)}],
        "answer_display": "路上用了 %d 分钟" % dur,
        "solution": ["思路：经过时间 = 结束时刻 - 开始时刻。",
                     "%d 时 %d 分到 %d 时 %d 分，经过 %d 分钟。答：路上用了 %d 分钟。"
                     % (h1, m1, h2, m2, dur, dur)],
    }


def _c2_len_std():
    """长度应用（常见：比一个数多几）"""
    item = random.choice([("小树", "棵"), ("栏杆", "根")])
    a = random.randint(20, 80)
    b = random.randint(10, 100 - a)
    big = a + b
    q = "一棵%s高 %d 厘米，一棵大树比它高 %d 厘米。大树高多少厘米？" % (item[0], a, b)
    return {
        "question": q,
        "steps": [{"hint": "大树比小树高，用加法计算，高多少厘米？", "answer": str(big)}],
        "answers": [{"label": "大树高（厘米）", "value": str(big)}],
        "answer_display": "大树高 %d 厘米" % big,
        "solution": ["思路：求比一个数多几的数用加法。",
                     "%d + %d = %d（厘米）。答：大树高 %d 厘米。" % (a, b, big, big)],
    }


def _c2_twostep_std():
    """两步应用（常见：卖出又运进）"""
    item = random.choice(["牛奶", "矿泉水", "鸡蛋"])
    a = random.randint(30, 90)
    b = random.randint(10, a - 10)
    c = random.randint(10, 50)
    now = a - b + c
    q = "食堂原有 %d 箱%s，用了 %d 箱，又买来 %d 箱。现在有多少箱%s？" \
        % (a, item, b, c, item)
    return {
        "question": q,
        "steps": [{"hint": "先算用了之后剩多少箱？", "answer": str(a - b)},
                  {"hint": "再加上买来的，现在有多少箱？", "answer": str(now)}],
        "answers": [{"label": "现在（箱）", "value": str(now)}],
        "answer_display": "现在有 %d 箱" % now,
        "solution": ["思路：用了用减法，买来用加法，按顺序计算。",
                     "%d - %d = %d（箱），%d + %d = %d（箱）。答：现在有 %d 箱%s。"
                     % (a, b, a - b, a - b, c, now, now, item)],
    }


def _c3_perimeter_std():
    """周长应用（常见：长方形周长公式）"""
    a = random.randint(5, 30)
    b = random.randint(2, a)
    per = (a + b) * 2
    q = "一个长方形花坛长 %d 米、宽 %d 米。它的周长是多少米？" % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "长方形周长 =（长 + 宽）× 2，是多少米？", "answer": str(per)}],
        "answers": [{"label": "周长（米）", "value": str(per)}],
        "answer_display": "周长是 %d 米" % per,
        "solution": ["思路：长方形周长 =（长 + 宽）× 2。",
                     "(%d + %d) × 2 = %d（米）。答：花坛的周长是 %d 米。" % (a, b, per, per)],
    }


def _c3_elapsed_std():
    """经过时间（常见：上学路上用时）"""
    h1 = random.randint(7, 8)
    m1 = random.randint(0, 55)
    dur = random.randint(10, 50)
    t2 = h1 * 60 + m1 + dur
    h2, m2 = t2 // 60, t2 % 60
    q = "小明上午 %d 时 %d 分从家出发，%d 时 %d 分到校。他从家到学校要走多长时间？" \
        % (h1, m1, h2, m2)
    return {
        "question": q,
        "steps": [{"hint": "结束时刻减开始时刻，要走多少分钟？", "answer": str(dur)}],
        "answers": [{"label": "要走（分钟）", "value": str(dur)}],
        "answer_display": "要走 %d 分钟" % dur,
        "solution": ["思路：经过时间 = 结束时刻 - 开始时刻。",
                     "%d 时 %d 分到 %d 时 %d 分，经过 %d 分钟。答：要走 %d 分钟。"
                     % (h1, m1, h2, m2, dur, dur)],
    }


def _c3_year_std():
    """年月日（常见：经过整月的天数）"""
    m = random.randint(1, 11)
    d = random.randint(1, 20)
    days = _MONTH_DAYS[m - 1]
    q = "从 %d 月 %d 日到 %d 月 %d 日，一共经过了多少天？" % (m, d, m + 1, d)
    return {
        "question": q,
        "steps": [{"hint": "恰好过了一个整月，%d 月有多少天？" % m, "answer": str(days)}],
        "answers": [{"label": "经过（天）", "value": str(days)}],
        "answer_display": "一共经过了 %d 天" % days,
        "solution": ["思路：从 %d 月 %d 日到 %d 月 %d 日恰好是一个整月，天数等于 %d 月的天数。"
                     % (m, d, m + 1, d, m),
                     "%d 月共有 %d 天。答：一共经过了 %d 天。" % (m, days, days)],
    }


def _c3_lcmul_std():
    """连乘应用（常见：每盒 × 每层 × 层数）"""
    item = random.choice([("粉笔", "支"), ("铅笔", "支"), ("瓶盖", "个")])
    x = random.randint(2, 20)
    y = random.randint(2, 6)
    z = random.randint(2, 6)
    total = x * y * z
    q = "一个货架每层放 %d 盒%s，每盒 %d %s，货架共有 %d 层。一共能放多少%s？" \
        % (y, item[0], x, item[1], z, item[0])
    return {
        "question": q,
        "steps": [{"hint": "先算每层放多少%s？" % item[0], "answer": str(x * y)},
                  {"hint": "再乘层数，一共多少%s？" % item[0], "answer": str(total)}],
        "answers": [{"label": "一共（%s）" % item[1], "value": str(total)}],
        "answer_display": "一共能放 %d %s" % (total, item[0]),
        "solution": ["思路：连乘按顺序计算，也可以先算每层的数量。",
                     "每层：%d × %d = %d（%s），一共：%d × %d = %d（%s）。"
                     "答：一共能放 %d %s。"
                     % (x, y, x * y, item[1], x * y, z, total, item[1], total, item[0])],
    }


def _c3_guiyi_std():
    """归一问题（常见：先求单一量再求总数）"""
    n = _name()
    h = random.randint(2, 6)
    per = random.randint(3, 15)
    made = h * per
    days = random.randint(2, 6)
    total = per * days
    q = "%s %d 小时加工了 %d 个零件，照这样计算，%d 小时能加工多少个零件？" \
        % (n, h, made, days)
    return {
        "question": q,
        "steps": [{"hint": "先算每小时加工多少个？", "answer": str(per)},
                  {"hint": "再算 %d 小时加工多少个？" % days, "answer": str(total)}],
        "answers": [{"label": "加工（个）", "value": str(total)}],
        "answer_display": "能加工 %d 个零件" % total,
        "solution": ["思路：先求单一量（每小时加工数），再求总数。",
                     "每小时：%d ÷ %d = %d（个），%d 小时：%d × %d = %d（个）。"
                     "答：%d 小时能加工 %d 个零件。"
                     % (made, h, per, days, per, days, total, days, total)],
    }


def _c3_guizong_std():
    """归总问题（常见：总数不变，先求总数）"""
    per1 = random.randint(4, 8)
    rows1 = random.randint(2, 6)
    total = per1 * rows1
    cands = [p for p in (2, 3, 4, 5, 6, 8) if p != per1 and total % p == 0]
    while not cands:
        per1 = random.randint(4, 8)
        rows1 = random.randint(2, 6)
        total = per1 * rows1
        cands = [p for p in (2, 3, 4, 5, 6, 8) if p != per1 and total % p == 0]
    per2 = random.choice(cands)
    rows2 = total // per2
    q = "同学们做操，每 %d 人一排正好站 %d 排。如果每 %d 人一排，可以站多少排？" \
        % (per1, rows1, per2)
    return {
        "question": q,
        "steps": [{"hint": "先算总人数是多少？", "answer": str(total)},
                  {"hint": "总数不变，每 %d 人一排能站几排？" % per2, "answer": str(rows2)}],
        "answers": [{"label": "站（排）", "value": str(rows2)}],
        "answer_display": "可以站 %d 排" % rows2,
        "solution": ["思路：先求总人数（归总），再按新的每排人数求排数。",
                     "总人数：%d × %d = %d（人），排数：%d ÷ %d = %d（排）。"
                     "答：可以站 %d 排。"
                     % (per1, rows1, total, total, per2, rows2, rows2)],
    }


def _c3_area_std():
    """面积应用（常见：长方形面积公式）"""
    a = random.randint(4, 20)
    b = random.randint(2, a)
    area = a * b
    q = "一块长方形菜地长 %d 米、宽 %d 米。它的面积是多少平方米？" % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "长方形面积 = 长 × 宽，是多少平方米？", "answer": str(area)}],
        "answers": [{"label": "面积（平方米）", "value": str(area)}],
        "answer_display": "面积是 %d 平方米" % area,
        "solution": ["思路：长方形面积 = 长 × 宽。",
                     "%d × %d = %d（平方米）。答：菜地的面积是 %d 平方米。"
                     % (a, b, area, area)],
    }


def _c3_liandiv_std():
    """连除应用（常见：总数 ÷ 箱数 ÷ 层数）"""
    per = random.randint(3, 12)
    z = random.randint(2, 5)
    y = random.randint(2, 5)
    total = per * y * z
    q = "商店运来 %d 瓶饮料，平均装在 %d 个箱子里，每箱平均分成 %d 层。每层放多少瓶？" \
        % (total, y, z)
    return {
        "question": q,
        "steps": [{"hint": "先算每箱放多少瓶？", "answer": str(total // y)},
                  {"hint": "再除以层数，每层放多少瓶？", "answer": str(per)}],
        "answers": [{"label": "每层（瓶）", "value": str(per)}],
        "answer_display": "每层放 %d 瓶" % per,
        "solution": ["思路：连除按顺序计算，也可以先算每箱的数量。",
                     "每箱：%d ÷ %d = %d（瓶），每层：%d ÷ %d = %d（瓶）。"
                     "答：每层放 %d 瓶。" % (total, y, total // y, total // y, z, per, per)],
    }


def _c3_mass_std():
    """质量单位（常见：克与千克的换算）"""
    per = 500
    bags = random.choice([2, 4, 6, 8, 10, 12])
    kg = bags * per // 1000
    q = "一袋食盐重 500 克，妈妈买了 %d 袋，一共重多少千克？" % bags
    return {
        "question": q,
        "steps": [{"hint": "先算一共重多少克？", "answer": str(bags * per)},
                  {"hint": "1000 克 = 1 千克，合多少千克？", "answer": str(kg)}],
        "answers": [{"label": "一共（千克）", "value": str(kg)}],
        "answer_display": "一共重 %d 千克" % kg,
        "solution": ["思路：先求总克数，再换算成千克（1000 克 = 1 千克）。",
                     "%d × %d = %d（克）= %d 千克。答：一共重 %d 千克。"
                     % (per, bags, bags * per, kg, kg)],
    }


def _c4_price_std():
    """单价总价（常见：总价 = 单价 × 数量）"""
    item = random.choice([("钢笔", "支"), ("词典", "本"), ("台灯", "盏")])
    price = random.randint(8, 45)
    cnt = random.randint(2, 9)
    total = price * cnt
    q = "一%s%s %d 元，买 %d %s一共需要多少元？" \
        % (item[1], item[0], price, cnt, item[1])
    return {
        "question": q,
        "steps": [{"hint": "单价乘数量，一共多少元？", "answer": str(total)}],
        "answers": [{"label": "一共（元）", "value": str(total)}],
        "answer_display": "一共需要 %d 元" % total,
        "solution": ["思路：总价 = 单价 × 数量。",
                     "%d × %d = %d（元）。答：一共需要 %d 元。" % (price, cnt, total, total)],
    }


def _c4_speed_std():
    """速度路程（常见：路程 = 速度 × 时间）"""
    v = random.choice([40, 50, 60, 70, 80, 90])
    t = random.randint(2, 8)
    s = v * t
    q = "一辆汽车每小时行驶 %d 千米，行驶了 %d 小时。一共行驶了多少千米？" % (v, t)
    return {
        "question": q,
        "steps": [{"hint": "速度乘时间，一共行驶多少千米？", "answer": str(s)}],
        "answers": [{"label": "行驶（千米）", "value": str(s)}],
        "answer_display": "一共行驶了 %d 千米" % s,
        "solution": ["思路：路程 = 速度 × 时间。",
                     "%d × %d = %d（千米）。答：一共行驶了 %d 千米。" % (v, t, s, s)],
    }


def _c4_bignum_std():
    """大数应用（常见：比一个数多几的万级加法）"""
    a = random.randint(10, 90)
    b = random.randint(5, 60)
    total = a + b
    q = "某图书馆有故事书 %d 万册，科技书比故事书多 %d 万册。科技书有多少万册？两种书一共有多少万册？" \
        % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "科技书比故事书多，用加法，是多少万册？", "answer": str(a + b)},
                  {"hint": "两种书合起来是多少万册？", "answer": str(total + a)}],
        "answers": [{"label": "科技书（万册）", "value": str(a + b)},
                    {"label": "一共（万册）", "value": str(a + b + a)}],
        "answer_display": "科技书 %d 万册，两种书共 %d 万册" % (a + b, a + b + a),
        "solution": ["思路：科技书 = 故事书 + 多出的部分；合计 = 故事书 + 科技书。",
                     "科技书：%d + %d = %d（万册），合计：%d + %d = %d（万册）。"
                     "答：科技书有 %d 万册，两种书共有 %d 万册。"
                     % (a, b, a + b, a, a + b, a + b + a, a + b, a + b + a)],
    }


def _c4_distrlaw_std():
    """运算律应用（常见：一套 × 数量）"""
    top = random.randint(30, 80)
    pants = random.randint(20, top - 10)
    n = random.randint(3, 12)
    total = (top + pants) * n
    q = "一套运动服上衣 %d 元、裤子 %d 元。买 %d 套一共需要多少元？" % (top, pants, n)
    return {
        "question": q,
        "steps": [{"hint": "先算一套多少元？", "answer": str(top + pants)},
                  {"hint": "再乘套数，一共多少元？", "answer": str(total)}],
        "answers": [{"label": "一共（元）", "value": str(total)}],
        "answer_display": "一共需要 %d 元" % total,
        "solution": ["思路：先求一套的单价，再乘数量；也可以用乘法分配律。",
                     "一套：(%d + %d) = %d（元），一共：%d × %d = %d（元）。"
                     "答：一共需要 %d 元。"
                     % (top, pants, top + pants, top + pants, n, total, total)],
    }


def _c4_avg_std():
    """平均数（常见：总数 ÷ 份数）"""
    people = random.choice([4, 5, 6, 8])
    per = random.randint(4, 20)
    total = people * per
    q = "四（1）班 %d 名同学一共收集了 %d 本旧书，平均每人收集多少本？" % (people, total)
    return {
        "question": q,
        "steps": [{"hint": "总数除以人数，平均每人多少本？", "answer": str(per)}],
        "answers": [{"label": "平均（本）", "value": str(per)}],
        "answer_display": "平均每人收集 %d 本" % per,
        "solution": ["思路：平均数 = 总数量 ÷ 总份数。",
                     "%d ÷ %d = %d（本）。答：平均每人收集 %d 本。" % (total, people, per, per)],
    }


def _c4_decimal_buy():
    """小数应用（常见：小数加法购物）"""
    item1 = random.choice([("铅笔", "支"), ("圆珠笔", "支")])
    item2 = random.choice([("橡皮", "块"), ("尺子", "把")])
    p1 = random.randint(5, 20) / 10.0
    p2 = random.randint(5, 20) / 10.0
    total = p1 + p2
    q = "一%s%s 0.%d 元，一%s%s 0.%d 元。买一%s%s和一%s%s一共需要多少元？" \
        % (item1[1], item1[0], int(p1 * 10), item2[1], item2[0], int(p2 * 10),
           item1[1], item1[0], item2[1], item2[0])
    return {
        "question": q,
        "steps": [{"hint": "两个单价相加，一共多少元？", "answer": "%.1f" % total}],
        "answers": [{"label": "一共（元）", "value": "%.1f" % total}],
        "answer_display": "一共需要 %.1f 元" % total,
        "solution": ["思路：小数加法把小数点对齐再相加。",
                     "0.%d + 0.%d = %.1f（元）。答：一共需要 %.1f 元。"
                     % (int(p1 * 10), int(p2 * 10), total, total)],
    }


def _c4_triangle_std():
    """三角形内角和（常见：180° - 两角）"""
    a = random.randint(20, 100)
    b = random.randint(20, 170 - a)
    c = 180 - a - b
    q = "在三角形中，∠1 = %d°，∠2 = %d°。∠3 是多少度？" % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "三角形内角和是 180°，∠3 是多少度？", "answer": str(c)}],
        "answers": [{"label": "∠3（度）", "value": str(c)}],
        "answer_display": "∠3 是 %d°" % c,
        "solution": ["思路：三角形三个内角的和是 180°。",
                     "180° - %d° - %d° = %d°。答：∠3 是 %d°。" % (a, b, c, c)],
    }


def _c4_change_std():
    """小数减法应用（常见：付钱找零）"""
    n = _name()
    price = random.randint(15, 85) / 10.0
    paid = random.choice([10, 20])
    change = paid - price
    q = "%s买了一瓶酸奶，单价 %.1f 元，付了 %d 元，应找回多少元？" \
        % (n, price, paid)
    return {
        "question": q,
        "steps": [{"hint": "付的钱减去单价，应找回多少元？", "answer": "%.1f" % change}],
        "answers": [{"label": "找回（元）", "value": "%.1f" % change}],
        "answer_display": "应找回 %.1f 元" % change,
        "solution": ["思路：找零 = 付出的钱 - 花掉的钱，注意小数点对齐。",
                     "%d - %.1f = %.1f（元）。答：应找回 %.1f 元。"
                     % (paid, price, change, change)],
    }


def _c5_decmul_std():
    """小数乘法应用（常见：单价 × 数量）"""
    price = random.randint(10, 99) / 10.0
    n = random.randint(2, 20)
    total = price * n
    q = "某市自来水每吨 %.1f 元，小明家上月用水 %d 吨。应付水费多少元？" % (price, n)
    return {
        "question": q,
        "steps": [{"hint": "单价乘吨数，应付多少元？", "answer": "%.1f" % total}],
        "answers": [{"label": "水费（元）", "value": "%.1f" % total}],
        "answer_display": "应付水费 %.1f 元" % total,
        "solution": ["思路：总价 = 单价 × 数量。",
                     "%.1f × %d = %.1f（元）。答：应付水费 %.1f 元。"
                     % (price, n, total, total)],
    }


def _c5_decdiv_std():
    """小数除法应用（常见：总数 ÷ 份数）"""
    per10 = random.randint(5, 99)   # 每段长度（以 0.1 米为单位）
    n = random.choice([2, 3, 4, 5, 6, 8, 9, 10])
    while per10 % n != 0:
        per10 = random.randint(5, 99)
    total = per10 / 10.0
    per = per10 / 10.0 / n
    q = "一根绳子长 %.1f 米，平均分成 %d 段。每段长多少米？" % (total, n)
    return {
        "question": q,
        "steps": [{"hint": "总长除以段数，每段多少米？", "answer": "%g" % per}],
        "answers": [{"label": "每段（米）", "value": "%g" % per}],
        "answer_display": "每段长 %g 米" % per,
        "solution": ["思路：平均分用除法，注意小数除法的计算方法。",
                     "%.1f ÷ %d = %g（米）。答：每段长 %g 米。" % (total, n, per, per)],
    }


def _c5_segfee_std():
    """分段计费（常见：出租车起步价 + 超出部分）"""
    base = random.choice([6, 8, 10, 12, 14])
    per_km = random.choice([1, 2, 3])
    km = random.randint(4, 30)
    cost = base + (km - 3) * per_km
    q = "某市出租车起步价 %d 元（3 千米以内），超过 3 千米后每千米 %d 元。王叔叔乘车行了 %d 千米，应付多少元？" \
        % (base, per_km, km)
    return {
        "question": q,
        "steps": [{"hint": "超过 3 千米的部分是多少千米？", "answer": str(km - 3)},
                  {"hint": "起步价加上超出部分，应付多少元？", "answer": str(cost)}],
        "answers": [{"label": "车费（元）", "value": str(cost)}],
        "answer_display": "应付 %d 元" % cost,
        "solution": ["思路：分段计费先分清两段：起步价部分 + 超出部分。",
                     "超出：%d - 3 = %d（千米），%d × %d = %d（元），"
                     "合计：%d + %d = %d（元）。答：应付 %d 元。"
                     % (km, km - 3, km - 3, per_km, (km - 3) * per_km,
                        base, (km - 3) * per_km, cost, cost)],
    }


def _c5_box_std():
    """长方体表面积（常见：完整 6 个面）"""
    a = random.randint(4, 15)
    b = random.randint(2, a)
    c = random.randint(2, 12)
    s = 2 * (a * b + a * c + b * c)
    q = "一个长方体纸盒长 %d 分米、宽 %d 分米、高 %d 分米。做这个纸盒至少需要多少平方分米的纸板？" \
        % (a, b, c)
    return {
        "question": q,
        "steps": [{"hint": "长方体表面积 =（长×宽 + 长×高 + 宽×高）× 2，是多少平方分米？",
                   "answer": str(s)}],
        "answers": [{"label": "纸板（平方分米）", "value": str(s)}],
        "answer_display": "至少需要 %d 平方分米纸板" % s,
        "solution": ["思路：表面积 = 6 个面的面积之和 =（长×宽 + 长×高 + 宽×高）× 2。",
                     "(%d×%d + %d×%d + %d×%d) × 2 = %d（平方分米）。"
                     "答：至少需要 %d 平方分米纸板。"
                     % (a, b, a, c, b, c, s, s)],
    }


def _c5_pool_std():
    """长方体容积（常见：蓄水问题）"""
    a = random.randint(4, 15)
    b = random.randint(2, a)
    c = random.randint(2, 6)
    v = a * b * c
    q = "一个长方体水池从里面量长 %d 米、宽 %d 米、深 %d 米。这个水池最多能蓄水多少立方米？" \
        % (a, b, c)
    return {
        "question": q,
        "steps": [{"hint": "底面积是多少平方米？", "answer": str(a * b)},
                  {"hint": "底面积乘深，最多蓄水多少立方米？", "answer": str(v)}],
        "answers": [{"label": "蓄水（立方米）", "value": str(v)}],
        "answer_display": "最多能蓄水 %d 立方米" % v,
        "solution": ["思路：水池的蓄水量就是它的容积 = 底面积 × 深。",
                     "%d × %d = %d（平方米），%d × %d = %d（立方米）。"
                     "答：最多能蓄水 %d 立方米。"
                     % (a, b, a * b, a * b, c, v, v)],
    }


def _c5_fracadd_std():
    """分数加减应用（常见：通分后求和）"""
    d1 = random.randint(2, 6)
    k = random.choice([2, 3])
    d2 = k * d1
    a1 = random.randint(1, d1 - 1)
    a2 = random.randint(1, d2 - k * a1 - 1)
    s = a1 * k + a2
    q = "一瓶果汁，爸爸喝了它的 %d/%d，妈妈喝了它的 %d/%d。两人一共喝了这瓶果汁的几分之几？" \
        % (a1, d1, a2, d2)
    return {
        "question": q,
        "steps": [{"hint": "先通分：%d/%d = %d/%d。" % (a1, d1, a1 * k, d2),
                   "answer": "%d/%d" % (a1 * k, d2)},
                  {"hint": "通分后分子相加，一共几分之几？", "answer": "%d/%d" % (s, d2)}],
        "answers": [{"label": "一共喝了", "value": "%d/%d" % (s, d2)}],
        "answer_display": "一共喝了 %d/%d" % (s, d2),
        "solution": ["思路：分母不同要先通分，再按同分母分数相加。",
                     "%d/%d = %d/%d，%d/%d + %d/%d = %d/%d。"
                     "答：两人一共喝了这瓶果汁的 %d/%d。"
                     % (a1, d1, a1 * k, d2, a1 * k, d2, a2, d2, s, d2, s, d2)],
    }


def _c5_equation_std():
    """列方程应用（常见：单价未知求单价）"""
    n = _name()
    cnt = random.choice([4, 5, 6, 8])
    per = random.randint(3, 12)
    total = cnt * per
    q = "%s买了 %d 支同样的圆珠笔，一共付了 %d 元。每支圆珠笔多少元？（列方程解答）" \
        % (n, cnt, total)
    return {
        "question": q,
        "steps": [{"hint": "设每支 x 元，列方程：%d × x = %d，x 是多少？" % (cnt, total),
                   "answer": str(per)}],
        "answers": [{"label": "每支（元）", "value": str(per)}],
        "answer_display": "每支圆珠笔 %d 元" % per,
        "solution": ["思路（列方程）：设每支 x 元，等量关系是\"单价 × 数量 = 总价\"。",
                     "列方程：%d × x = %d，解得 x = %d ÷ %d = %d。答：每支圆珠笔 %d 元。"
                     % (cnt, total, total, cnt, per, per)],
    }


def _c6_circle_std():
    """圆的应用（常见：由直径求周长）"""
    d = random.choice(range(2, 61, 2))
    c = 3.14 * d
    q = "一个圆形花坛的直径是 %d 米。它的周长是多少米？（π 取 3.14）" % d
    return {
        "question": q,
        "steps": [{"hint": "圆的周长 = π × 直径，周长是多少米？", "answer": "%.2f" % c}],
        "answers": [{"label": "周长（米）", "value": "%.2f" % c}],
        "answer_display": "周长是 %.2f 米" % c,
        "solution": ["思路：圆的周长 C = πd。",
                     "3.14 × %d = %.2f（米）。答：花坛的周长是 %.2f 米。" % (d, c, c)],
    }


def _c6_ratio_std():
    """按比分配（常见：两部分之比）"""
    a = random.choice([1, 2, 3, 4, 5])
    b = random.choice([2, 3, 4, 5, 6, 7])
    k = random.randint(2, 25)
    total = (a + b) * k
    q = "学校把 %d 本课外书按 %d : %d 分配给五、六年级。五、六年级各分得多少本？" \
        % (total, a, b)
    return {
        "question": q,
        "steps": [{"hint": "总份数是多少份？", "answer": str(a + b)},
                  {"hint": "每份是多少本？", "answer": str(k)}],
        "answers": [{"label": "五年级（本）", "value": str(a * k)},
                    {"label": "六年级（本）", "value": str(b * k)}],
        "answer_display": "五年级分得 %d 本，六年级分得 %d 本" % (a * k, b * k),
        "solution": ["思路：按比分配先求总份数，再求每份数。",
                     "总份数：%d + %d = %d（份），每份：%d ÷ %d = %d（本）。"
                     "五年级：%d × %d = %d（本），六年级：%d × %d = %d（本）。"
                     "答：五年级分得 %d 本，六年级分得 %d 本。"
                     % (a, b, a + b, total, a + b, k, a, k, a * k, b, k, b * k,
                        a * k, b * k)],
    }


def _c6_pct_std():
    """百分数应用（常见：求一个数的百分之几）"""
    pct = random.choice([10, 20, 25, 50])
    unit = random.randint(2, 60)
    total = unit * 100 // pct
    part = unit
    q = "六（1）班有 %d 名同学，其中 %d%% 的同学参加了书法小组。参加书法小组的有多少名同学？" \
        % (total, pct)
    return {
        "question": q,
        "steps": [{"hint": "求一个数的百分之几用乘法，是多少人？", "answer": str(part)}],
        "answers": [{"label": "参加（人）", "value": str(part)}],
        "answer_display": "参加书法小组的有 %d 名同学" % part,
        "solution": ["思路：求一个数的百分之几是多少，用乘法。",
                     "%d × %d%% = %d × %g = %d（名）。答：参加书法小组的有 %d 名同学。"
                     % (total, pct, total, pct / 100.0, part, part)],
    }


def _c6_cyl_std():
    """圆柱体积（常见：容积计算）"""
    r = random.randint(1, 12)
    h = random.randint(2, 25)
    v = 3.14 * r * r * h
    q = "一个圆柱形水杯从里面量底面半径 %d 厘米、高 %d 厘米。它的容积是多少毫升？（π 取 3.14）" \
        % (r, h)
    return {
        "question": q,
        "steps": [{"hint": "底面积是多少平方厘米？", "answer": "%.2f" % (3.14 * r * r)},
                  {"hint": "底面积乘高，容积是多少毫升？", "answer": "%.2f" % v}],
        "answers": [{"label": "容积（毫升）", "value": "%.2f" % v}],
        "answer_display": "容积是 %.2f 毫升" % v,
        "solution": ["思路：圆柱的容积 = 底面积 × 高；1 立方厘米 = 1 毫升。",
                     "底面积：3.14 × %d × %d = %.2f（平方厘米），"
                     "容积：%.2f × %d = %.2f（立方厘米）= %.2f 毫升。"
                     "答：它的容积是 %.2f 毫升。"
                     % (r, r, 3.14 * r * r, 3.14 * r * r, h, v, v, v)],
    }


def _c6_cone_std():
    """圆锥体积（常见：直接套公式）"""
    r = random.randint(1, 12)
    h = random.choice([3, 6, 9, 12, 15, 18])
    v = 3.14 * r * r * h / 3
    q = "一个圆锥形沙堆底面半径 %d 米、高 %d 米。这堆沙的体积是多少立方米？（π 取 3.14）" \
        % (r, h)
    return {
        "question": q,
        "steps": [{"hint": "同底等高圆柱的体积是多少立方米？", "answer": "%.2f" % (3.14 * r * r * h)},
                  {"hint": "圆锥体积是与它等底等高的圆柱的 1/3，是多少立方米？",
                   "answer": "%.2f" % v}],
        "answers": [{"label": "体积（立方米）", "value": "%.2f" % v}],
        "answer_display": "沙堆的体积是 %.2f 立方米" % v,
        "solution": ["思路：圆锥体积 = 底面积 × 高 ÷ 3。",
                     "底面积：3.14 × %d × %d = %.2f（平方米），"
                     "体积：%.2f × %d ÷ 3 = %.2f（立方米）。答：沙堆的体积是 %.2f 立方米。"
                     % (r, r, 3.14 * r * r, 3.14 * r * r, h, v, v)],
    }


def _c6_scale_std():
    """比例尺（常见：由实际距离求图上距离）"""
    km = random.choice(range(2, 61))
    sc = random.choice([100000, 200000, 50000])
    cm = km * 100000 // sc
    while km * 100000 % sc != 0 or cm < 2:
        km = random.choice(range(2, 61))
        cm = km * 100000 // sc
    q = "甲、乙两地相距 %d 千米，画在比例尺为 1 : %d 的地图上。图上距离是多少厘米？" \
        % (km, sc)
    return {
        "question": q,
        "steps": [{"hint": "%d 千米 = 多少厘米？" % km, "answer": str(km * 100000)},
                  {"hint": "实际距离除以比例尺的后项，图上多少厘米？", "answer": str(cm)}],
        "answers": [{"label": "图上距离（厘米）", "value": str(cm)}],
        "answer_display": "图上距离是 %d 厘米" % cm,
        "solution": ["思路：1 千米 = 100000 厘米；图上距离 = 实际距离 ÷ 比例尺的后项。",
                     "%d 千米 = %d 厘米，%d ÷ %d = %d（厘米）。"
                     "答：图上距离是 %d 厘米。"
                     % (km, km * 100000, km * 100000, sc, cm, cm)],
    }


def _c6_prop_std():
    """正比例应用（常见：单一量不变求总价）"""
    cnt = random.randint(2, 9)
    per = random.randint(2, 20)
    paid = cnt * per
    n = random.randint(2, 20)
    total = per * n
    q = "买 %d 本同样的练习本共花 %d 元。照这样计算，买 %d 本要花多少元？" % (cnt, paid, n)
    return {
        "question": q,
        "steps": [{"hint": "先算每本练习本多少元？", "answer": str(per)},
                  {"hint": "再算 %d 本要花多少元？" % n, "answer": str(total)}],
        "answers": [{"label": "要花（元）", "value": str(total)}],
        "answer_display": "买 %d 本要花 %d 元" % (n, total),
        "solution": ["思路：单价不变（成正比例），先求单价再求总价。",
                     "单价：%d ÷ %d = %d（元），总价：%d × %d = %d（元）。"
                     "答：买 %d 本要花 %d 元。"
                     % (paid, cnt, per, per, n, total, n, total)],
    }


def _c1_chain():
    """连加连减（常见：飞走又飞来）"""
    a = random.randint(6, 18)
    b = random.randint(1, a - 1)
    c = random.randint(1, 20 - (a - b))
    now = a - b + c
    q = "树上有 %d 只小鸟，飞走了 %d 只，又飞来了 %d 只。现在树上有多少只小鸟？" \
        % (a, b, c)
    return {
        "question": q,
        "steps": [{"hint": "先算飞走后还剩几只？", "answer": str(a - b)},
                  {"hint": "再加上又飞来的，现在有几只？", "answer": str(now)}],
        "answers": [{"label": "现在（只）", "value": str(now)}],
        "answer_display": "现在树上有 %d 只小鸟" % now,
        "solution": ["思路：飞走用减法，飞来用加法，按从左到右的顺序计算。",
                     "%d - %d = %d（只），%d + %d = %d（只）。答：现在树上有 %d 只小鸟。"
                     % (a, b, a - b, a - b, c, now, now)],
    }


def _c1_fewer():
    """求比一个数少几（常见：回收废品型）"""
    a = random.randint(10, 99)
    b = random.randint(1, a - 1)
    ans = a - b
    q = "一年级同学收集了 %d 个矿泉水瓶，二年级比一年级少收集 %d 个。二年级收集了多少个？" \
        % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "比一年级少，就用一年级的数量减去少的部分。", "answer": str(ans)}],
        "answers": [{"label": "收集（个）", "value": str(ans)}],
        "answer_display": "二年级收集了 %d 个" % ans,
        "solution": ["思路：求比一个数少几的数用减法。",
                     "%d - %d = %d（个）。答：二年级收集了 %d 个。" % (a, b, ans, ans)],
    }


def _c2_muladd_shop():
    """乘加两步应用（常见：买几件同样的再买一件）"""
    k = random.randint(2, 3)
    x = random.randint(3, 9)
    y = random.randint(2, 9)
    total = k * x + y
    q = "妈妈买了 %d 盒酸奶，每盒 %d 元；又买了 1 个面包 %d 元。一共要付多少元？" \
        % (k, x, y)
    return {
        "question": q,
        "steps": [{"hint": "先算 %d 盒酸奶多少元？" % k, "answer": str(k * x)},
                  {"hint": "再加面包的价钱，一共多少元？", "answer": str(total)}],
        "answers": [{"label": "一共（元）", "value": str(total)}],
        "answer_display": "一共要付 %d 元" % total,
        "solution": ["思路：先算酸奶的总价，再加上面包的价钱。",
                     "%d × %d = %d（元），%d + %d = %d（元）。答：一共要付 %d 元。"
                     % (k, x, k * x, k * x, y, total, total)],
    }


def _c2_boat():
    """进一法应用（常见：至少租几条船）"""
    per = random.choice([4, 6, 8])
    boat = random.randint(2, 9)
    rest = random.randint(1, per - 1)
    people = per * boat + rest
    need = boat + 1
    q = "%d 名同学去划船，每条船最多坐 %d 人。至少要租多少条船？" % (people, per)
    return {
        "question": q,
        "steps": [{"hint": "先算坐满需要几条船，还剩几人？",
                   "answer": "%d条剩%d人" % (boat, rest)},
                  {"hint": "剩下的人也要坐船，至少要几条船？", "answer": str(need)}],
        "answers": [{"label": "至少租（条）", "value": str(need)}],
        "answer_display": "至少要租 %d 条船" % need,
        "solution": ["思路：用除法计算，剩下的人数虽然坐不满一条船，也要再租一条。",
                     "%d ÷ %d = %d（条）……%d（人），%d + 1 = %d（条）。"
                     "答：至少要租 %d 条船。"
                     % (people, per, boat, rest, boat, need, need)],
    }


def _c2_threedigit():
    """万以内加法应用（常见：求全长）"""
    a = random.randint(100, 850)
    b = random.randint(50, 999 - a)
    total = a + b
    q = "修一条公路，已经修了 %d 米，还剩 %d 米没修。这条公路全长多少米？" % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "已修的加上没修的，全长多少米？", "answer": str(total)}],
        "answers": [{"label": "全长（米）", "value": str(total)}],
        "answer_display": "这条公路全长 %d 米" % total,
        "solution": ["思路：全长 = 已修的 + 没修的。",
                     "%d + %d = %d（米）。答：这条公路全长 %d 米。" % (a, b, total, total)],
    }


def _c3_odometer():
    """里程表问题（常见：读数差求行程）"""
    a = random.randint(20000, 80000)
    d = random.randint(100, 900)
    b = a + d
    q = "星期一早上，汽车里程表的读数是 %d 千米；星期日晚上，读数是 %d 千米。这辆汽车这一周行驶了多少千米？" \
        % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "用后面的读数减去前面的读数，行驶多少千米？", "answer": str(d)}],
        "answers": [{"label": "行驶（千米）", "value": str(d)}],
        "answer_display": "这一周行驶了 %d 千米" % d,
        "solution": ["思路：这一周行驶的路程 = 后来的读数 - 原来的读数。",
                     "%d - %d = %d（千米）。答：这一周行驶了 %d 千米。" % (b, a, d, d)],
    }


def _c3_twodigit_mul():
    """两位数乘两位数应用（常见：电影院座位）"""
    rows = random.randint(11, 29)
    seats = random.randint(11, 39)
    total = rows * seats
    q = "电影院有 %d 排座位，每排有 %d 个座位。这个电影院一共能坐多少人？" % (rows, seats)
    return {
        "question": q,
        "steps": [{"hint": "排数乘每排座位数，一共能坐多少人？", "answer": str(total)}],
        "answers": [{"label": "能坐（人）", "value": str(total)}],
        "answer_display": "一共能坐 %d 人" % total,
        "solution": ["思路：总人数 = 排数 × 每排座位数。",
                     "%d × %d = %d（人）。答：一共能坐 %d 人。" % (rows, seats, total, total)],
    }


def _c3_brick():
    """铺地砖问题（常见：面积 ÷ 单砖面积）"""
    a = random.randint(3, 9)
    b = random.randint(2, 6)
    total_dm2 = a * b * 100
    cands = [c for c in (4, 5, 8, 10, 16, 20, 25, 40, 50) if total_dm2 % c == 0]
    tile = random.choice(cands)
    cnt = total_dm2 // tile
    q = "客厅地面长 %d 米、宽 %d 米，用面积 %d 平方分米的地砖铺地。一共需要多少块地砖？" \
        % (a, b, tile)
    return {
        "question": q,
        "steps": [{"hint": "先算客厅面积是多少平方米，再换算成平方分米。",
                   "answer": str(total_dm2)},
                  {"hint": "地面面积除以每块砖的面积，需要多少块？", "answer": str(cnt)}],
        "answers": [{"label": "需要（块）", "value": str(cnt)}],
        "answer_display": "一共需要 %d 块地砖" % cnt,
        "solution": ["思路：先统一单位（1 平方米 = 100 平方分米），"
                     "再用地面面积 ÷ 每块砖的面积。",
                     "客厅面积：%d × %d = %d（平方米）= %d 平方分米，"
                     "需要：%d ÷ %d = %d（块）。答：一共需要 %d 块地砖。"
                     % (a, b, a * b, total_dm2, total_dm2, tile, cnt, cnt)],
    }


def _c4_meet():
    """相遇问题（常见：速度和 × 时间）"""
    x = random.choice([40, 45, 50, 55, 60])
    y = random.choice([35, 40, 45, 50, 65])
    t = random.randint(2, 5)
    s = (x + y) * t
    q = "甲、乙两地相距 %d 千米，一辆客车和一辆货车同时从两地相对开出，客车每小时行 %d 千米，货车每小时行 %d 千米。经过几小时两车相遇？" \
        % (s, x, y)
    return {
        "question": q,
        "steps": [{"hint": "两车每小时一共行多少千米（速度和）？", "answer": str(x + y)},
                  {"hint": "路程 ÷ 速度和 = 相遇时间，是多少小时？", "answer": str(t)}],
        "answers": [{"label": "相遇时间（小时）", "value": str(t)}],
        "answer_display": "经过 %d 小时两车相遇" % t,
        "solution": ["思路：相对而行，两车的速度和共同覆盖全程。",
                     "速度和：%d + %d = %d（千米/时），相遇时间：%d ÷ %d = %d（小时）。"
                     "答：经过 %d 小时两车相遇。"
                     % (x, y, x + y, s, x + y, t, t)],
    }


def _c4_mult_3x2():
    """三位数乘两位数应用（常见：整箱运货）"""
    a = random.randint(110, 290)
    b = random.randint(12, 24)
    total = a * b
    q = "水果店运来 %d 箱苹果，每箱重 %d 千克。这些苹果一共重多少千克？" % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "箱数乘每箱的质量，一共重多少千克？", "answer": str(total)}],
        "answers": [{"label": "一共重（千克）", "value": str(total)}],
        "answer_display": "一共重 %d 千克" % total,
        "solution": ["思路：总质量 = 箱数 × 每箱质量。",
                     "%d × %d = %d（千克）。答：一共重 %d 千克。" % (a, b, total, total)],
    }


def _c4_equation_x():
    """列方程应用（常见：部分已知求单价）"""
    n = _name()
    cnt = random.choice([3, 4, 6])
    pen = random.randint(2, 9)
    box = random.randint(10, 30)
    total = cnt * pen + box
    q = "%s买了 %d 支同样的笔和 1 个 %d 元的文具盒，一共付了 %d 元。每支笔多少元？（列方程解答）" \
        % (n, cnt, box, total)
    return {
        "question": q,
        "steps": [{"hint": "设每支笔 x 元，列方程：%d × x + %d = %d，x 是多少？"
                           % (cnt, box, total), "answer": str(pen)}],
        "answers": [{"label": "每支（元）", "value": str(pen)}],
        "answer_display": "每支笔 %d 元" % pen,
        "solution": ["思路（列方程）：设每支笔 x 元，等量关系是\"笔的总价 + 文具盒价钱 = 总付款\"。",
                     "列方程：%d × x + %d = %d，%d × x = %d，x = %d。答：每支笔 %d 元。"
                     % (cnt, box, total, cnt, total - box, pen, pen)],
    }


def _c4_decmul_app():
    """小数乘法应用（常见：单价 × 质量）"""
    price = random.randint(25, 98) / 10.0
    kg = random.randint(2, 9)
    total = price * kg
    q = "妈妈买了 %d 千克苹果，每千克 %.1f 元。一共要付多少元？" % (kg, price)
    return {
        "question": q,
        "steps": [{"hint": "单价乘质量，一共多少元？", "answer": "%.1f" % total}],
        "answers": [{"label": "要付（元）", "value": "%.1f" % total}],
        "answer_display": "一共要付 %.1f 元" % total,
        "solution": ["思路：总价 = 单价 × 数量，注意小数乘法的计算方法。",
                     "%.1f × %d = %.1f（元）。答：一共要付 %.1f 元。"
                     % (price, kg, total, total)],
    }


def _c5_polygon():
    """多边形面积（常见：三角形/梯形面积公式）"""
    if random.random() < 0.5:
        base = random.randint(2, 10) * 2      # 保证底×高为偶数
        h = random.randint(2, 15)
        area = base * h // 2
        q = "一块三角形菜地底 %d 米、高 %d 米。它的面积是多少平方米？" % (base, h)
        formula = "三角形面积 = 底 × 高 ÷ 2"
        calc = "%d × %d ÷ 2 = %d（平方米）。答：菜地的面积是 %d 平方米。" % (base, h, area, area)
    else:
        a = random.randint(4, 20)
        b = random.randint(2, a)
        h = random.randint(2, 10) * 2         # 保证 (上底+下底)×高 为偶数
        area = (a + b) * h // 2
        q = "一块梯形麦田上底 %d 米、下底 %d 米、高 %d 米。它的面积是多少平方米？" % (a, b, h)
        formula = "梯形面积 =（上底 + 下底）× 高 ÷ 2"
        calc = "(%d + %d) × %d ÷ 2 = %d（平方米）。答：麦田的面积是 %d 平方米。" \
               % (a, b, h, area, area)
    return {
        "question": q,
        "steps": [{"hint": "%s，面积是多少平方米？" % formula, "answer": str(area)}],
        "answers": [{"label": "面积（平方米）", "value": str(area)}],
        "answer_display": "面积是 %d 平方米" % area,
        "solution": ["思路：" + formula + "。", calc],
    }


def _c5_frac_of():
    """分数乘法应用（常见：求一个数的几分之几）"""
    c = random.choice([2, 3, 4, 5])
    b = random.randint(1, c - 1)
    k = random.randint(2, 12)
    length = c * k
    used = k * b
    q = "一根钢管长 %d 米，用去了它的 %d/%d。用去了多少米？" % (length, b, c)
    return {
        "question": q,
        "steps": [{"hint": "求一个数的几分之几是多少，用乘法：%d × %d/%d。"
                           % (length, b, c), "answer": str(used)}],
        "answers": [{"label": "用去（米）", "value": str(used)}],
        "answer_display": "用去了 %d 米" % used,
        "solution": ["思路：求一个数的几分之几是多少，用乘法计算。",
                     "%d × %d/%d = %d（米）。答：用去了 %d 米。" % (length, b, c, used, used)],
    }


def _c5_drain():
    """排水法测体积（常见：水面上升部分 = 铁块体积）"""
    a = random.randint(4, 10)
    b = random.randint(2, 6)
    c = random.randint(2, 6)
    d = c + random.randint(1, 5)
    v = a * b * (d - c)
    q = "一个从里面量长 %d 分米、宽 %d 分米的长方体水槽中装有 %d 分米深的水，放入一块铁块（完全浸没）后，水面上升到 %d 分米。这块铁块的体积是多少立方分米？" \
        % (a, b, c, d)
    return {
        "question": q,
        "steps": [{"hint": "水面上升了多少分米？", "answer": str(d - c)},
                  {"hint": "铁块体积 = 上升部分水的体积 = 长 × 宽 × 上升高度。",
                   "answer": str(v)}],
        "answers": [{"label": "铁块体积（立方分米）", "value": str(v)}],
        "answer_display": "铁块的体积是 %d 立方分米" % v,
        "solution": ["思路：铁块完全浸没，排开的水的体积等于铁块体积。",
                     "上升高度：%d - %d = %d（分米），"
                     "铁块体积：%d × %d × %d = %d（立方分米）。"
                     "答：这块铁块的体积是 %d 立方分米。"
                     % (d, c, d - c, a, b, d - c, v, v)],
    }


def _c6_circle_area():
    """圆面积应用（常见：由半径求面积）"""
    r = random.randint(1, 12)
    s = 3.14 * r * r
    q = "一个圆形花坛的半径是 %d 米。它的面积是多少平方米？（π 取 3.14）" % r
    return {
        "question": q,
        "steps": [{"hint": "圆的面积 = π × 半径 × 半径，面积是多少平方米？",
                   "answer": "%.2f" % s}],
        "answers": [{"label": "面积（平方米）", "value": "%.2f" % s}],
        "answer_display": "花坛的面积是 %.2f 平方米" % s,
        "solution": ["思路：圆的面积 S = πr²。",
                     "3.14 × %d × %d = %.2f（平方米）。答：花坛的面积是 %.2f 平方米。"
                     % (r, r, s, s)],
    }


def _c6_passrate():
    """合格率应用（常见：合格率 = 合格数 ÷ 总数 × 100%）"""
    a = random.choice([100, 200, 400, 500, 1000])
    r = random.choice([90, 92, 95, 96, 98])
    b = a * r // 100
    q = "质检员从一批产品中抽检了 %d 件，其中 %d 件合格。这批抽检产品的合格率是多少？" % (a, b)
    return {
        "question": q,
        "steps": [{"hint": "合格率 = 合格件数 ÷ 抽检总数 × 100%，是多少？",
                   "answer": "%d%%" % r}],
        "answers": [{"label": "合格率", "value": "%d%%" % r}],
        "answer_display": "合格率是 %d%%" % r,
        "solution": ["思路：合格率 = 合格件数 ÷ 抽检总数 × 100%。",
                     "%d ÷ %d × 100%% = %d%%。答：合格率是 %d%%。"
                     % (b, a, r, r)],
    }


def _c6_cyl_lateral():
    """圆柱侧面积应用（常见：直接套侧面积公式）"""
    d = random.choice(range(2, 21, 2))
    h = random.randint(3, 20)
    lat = 3.14 * d * h
    q = "一个圆柱的底面直径是 %d 厘米，高是 %d 厘米。它的侧面积是多少平方厘米？（π 取 3.14）" \
        % (d, h)
    return {
        "question": q,
        "steps": [{"hint": "圆柱侧面积 = 底面周长 × 高 = π × 直径 × 高，是多少平方厘米？",
                   "answer": "%.2f" % lat}],
        "answers": [{"label": "侧面积（平方厘米）", "value": "%.2f" % lat}],
        "answer_display": "侧面积是 %.2f 平方厘米" % lat,
        "solution": ["思路：圆柱的侧面沿高展开是长方形，长 = 底面周长，宽 = 高。",
                     "3.14 × %d × %d = %.2f（平方厘米）。答：侧面积是 %.2f 平方厘米。"
                     % (d, h, lat, lat)],
    }


def _c6_inprop():
    """反比例应用（常见：总量不变求次数）"""
    while True:
        d = random.choice([3, 4, 5, 6, 8])
        c1 = random.randint(2, 9)
        total = d * c1
        cands = [x for x in (2, 3, 4, 5, 6, 8, 10) if x != d and total % x == 0]
        if cands:
            b = random.choice(cands)
            break
    times = total // b
    q = "一批货物共 %d 吨，如果每次运 %d 吨，正好运 %d 次。如果每次运 %d 吨，要运多少次？" \
        % (total, d, c1, b)
    return {
        "question": q,
        "steps": [{"hint": "货物总吨数不变：每次运的吨数 × 次数的乘积一定，成什么比例？",
                   "answer": "反比例"},
                  {"hint": "总吨数除以每次运的吨数，要运多少次？", "answer": str(times)}],
        "answers": [{"label": "要运（次）", "value": str(times)}],
        "answer_display": "要运 %d 次" % times,
        "solution": ["思路：货物总吨数一定，每次运的吨数和次数成反比例。",
                     "%d × %d = %d（吨），%d ÷ %d = %d（次）。答：要运 %d 次。"
                     % (d, c1, total, total, b, times, times)],
    }


# 常见题模板池：(函数名, 类型名, 册别)。与易错题池 _BANK_POOL 对应、按册对齐教材。
_COMMON_POOL = {
    1: [(_c1_total_std, "求总数", 1), (_c1_left_std, "求剩余", 1),
        (_c1_compare_std, "比多少", 1), (_c1_diff_std, "比多少", 1),
        (_c1_chain, "连加连减", 1),
        (_c1_pay_change, "购物找零", 2), (_c1_dist_reverse, "求原来", 2),
        (_c1_route, "连减应用", 2), (_c1_twostep_std, "加减混合", 2),
        (_c1_fewer, "求比一个数少几", 2)],
    2: [(_c2_mul_mean, "乘法含义", 1), (_c2_avg_div, "平均分", 1),
        (_c2_beishu, "倍数关系", 1), (_c2_money_buy, "人民币", 1),
        (_c2_muladd_shop, "乘加乘减", 1),
        (_c2_remain_div, "有余数除法", 2), (_c2_elapsed_std, "经过时间", 2),
        (_c2_len_std, "长度应用", 2), (_c2_twostep_std, "两步应用", 2),
        (_c2_boat, "进一法", 2), (_c2_threedigit, "万以内加减", 2)],
    3: [(_c3_perimeter_std, "周长应用", 1), (_c3_elapsed_std, "经过时间", 1),
        (_c3_year_std, "年月日", 1), (_c3_lcmul_std, "连乘应用", 1),
        (_c3_odometer, "里程表", 1),
        (_c3_guiyi_std, "归一问题", 2), (_c3_guizong_std, "归总问题", 2),
        (_c3_area_std, "面积应用", 2), (_c3_liandiv_std, "连除应用", 2),
        (_c3_mass_std, "质量单位", 2), (_c3_twodigit_mul, "两位数乘两位数", 2),
        (_c3_brick, "铺地砖", 2)],
    4: [(_c4_price_std, "单价总价", 1), (_c4_speed_std, "速度路程", 1),
        (_c4_bignum_std, "大数组成", 1), (_c4_distrlaw_std, "运算律应用", 1),
        (_c4_meet, "相遇问题", 1), (_c4_mult_3x2, "三位数乘两位数", 1),
        (_c4_avg_std, "平均数", 2), (_c4_decimal_buy, "小数购物", 2),
        (_c4_triangle_std, "三角形边角", 2), (_c4_change_std, "小数加减混合", 2),
        (_c4_equation_x, "列方程应用", 2), (_c4_decmul_app, "小数乘法应用", 2)],
    5: [(_c5_decmul_std, "小数乘法应用", 1), (_c5_decdiv_std, "小数除法应用", 1),
        (_c5_segfee_std, "分段计费", 1), (_c5_polygon, "多边形面积", 1),
        (_c5_box_std, "长方体", 2), (_c5_pool_std, "体积容积", 2),
        (_c5_fracadd_std, "分数加减应用", 2), (_c5_equation_std, "列方程应用", 2),
        (_c5_frac_of, "分数乘法应用", 2), (_c5_drain, "排水法", 2)],
    6: [(_c6_circle_std, "圆的周长面积", 1), (_c6_ratio_std, "按比分配", 1),
        (_c6_pct_std, "百分率应用", 1), (_c6_circle_area, "圆面积", 1),
        (_c6_passrate, "合格率", 1),
        (_c6_cyl_std, "圆柱体积", 2), (_c6_cone_std, "圆锥体积", 2),
        (_c6_scale_std, "比例尺", 2), (_c6_prop_std, "正反比例", 2),
        (_c6_cyl_lateral, "圆柱侧面积", 2), (_c6_inprop, "反比例应用", 2)],
}


# ================= 模板池与题库生成 =================

# 各年级题库模板池：(函数名, 类型名, 册别) 列表。
# 册别按北师大版教材单元分布划分：1=上册，2=下册。
_BANK_POOL = {
    1: [(_w1_total, "求总数", 1), (_w1_compare, "比多少", 1),
        (_w1_queue, "排队问题", 1), (_w1_left, "求剩余", 1),
        (_w1_part, "求部分数", 1), (_w1_disturb, "多余条件", 1),
        (_w1_reverse, "逆向求原数", 2), (_w1_chain, "连减应用", 2),
        (_w1_pay, "购物付钱", 2), (_w1_bus, "加减混合", 2),
        (_w1_lianadd, "连加应用", 2), (_w1_diffrev, "比多少逆向", 2)],
    2: [(_w2_mul, "乘法含义", 1), (_w2_div, "平均分", 1),
        (_w2_times, "倍的含义", 1), (_w2_judge, "加乘辨析", 1),
        (_w2_money, "人民币", 1), (_w2_muladd, "乘加应用", 1),
        (_w2_mulsub, "乘减应用", 1), (_w2_boat, "租船进一", 2),
        (_w2_time, "经过时间", 2), (_w2_len, "长度单位", 2),
        (_w2_twostep, "两步应用", 2), (_w2_remainder, "有余数除法", 2),
        (_w2_cycle, "周期规律", 2), (_w2_bignum, "万以内数", 2),
        (_w2_tail, "去尾问题", 2)],
    3: [(_w3_perimeter, "周长应用", 1), (_w3_unit_perimeter, "周长单位陷阱", 1),
        (_w3_odometer, "里程表", 1), (_w3_sleep, "经过时间", 1),
        (_w3_lcmul, "连乘应用", 1), (_w3_year, "年月日", 1),
        (_w3_decintro, "小数初步", 1), (_w3_guiyi, "归一问题", 2),
        (_w3_guizong, "归总问题", 2), (_w3_liandiv, "连除应用", 2),
        (_w3_area, "面积应用", 2), (_w3_mass, "质量单位", 2),
        (_w3_fraction, "分数初步", 2), (_w3_areaunit, "面积单位换算", 2),
        (_w3_muldiv, "乘除混合", 2)],
    4: [(_w4_round, "近似数", 1), (_w4_price, "单价总价", 1),
        (_w4_speed, "速度路程", 1), (_w4_negative, "正负数", 1),
        (_w4_plant, "植树问题", 1), (_w4_hediff, "和差问题", 1),
        (_w4_give, "给后相同", 1), (_w4_bignum, "大数组成", 1),
        (_w4_distrlaw, "运算律应用", 1), (_w4_avg, "平均数", 2),
        (_w4_angle, "角度", 2), (_w4_decimal, "小数购物", 2),
        (_w4_triangle, "三角形边角", 2), (_w4_decadd, "小数加减混合", 2)],
    5: [(_w5_segfee, "分段计费", 1), (_w5_lcm, "公倍数应用", 1),
        (_w5_hebei, "和倍问题", 1), (_w5_chabei, "差倍问题", 1),
        (_w5_decmul, "小数乘法应用", 1), (_w5_decdiv, "小数除法应用", 1),
        (_w5_roundtail, "进一去尾", 1), (_w5_box, "长方体", 2),
        (_w5_fracrev, "分数除法逆向", 2), (_w5_fracadd, "分数加减应用", 2),
        (_w5_volume, "体积容积", 2), (_w5_displace, "排水法", 2),
        (_w5_equation, "列方程应用", 2)],
    6: [(_w6_circle, "圆的周长面积", 1), (_w6_ratio, "按比分配", 1),
        (_w6_rate, "百分率应用", 1), (_w6_updown, "涨降价陷阱", 1),
        (_w6_frac_more, "分数应用", 1), (_w6_interest, "利息", 1),
        (_w6_tax, "纳税", 1), (_w6_sqcircle, "外方内圆", 1),
        (_w6_pctunit, "求单位1", 1), (_w6_mixfrac, "分数混合应用", 1),
        (_w5_lcm, "公倍数复习", 2), (_w5_fracrev, "分数除法复习", 2),
        (_w6_cyl, "圆柱体积", 2), (_w6_cone, "圆锥体积", 2),
        (_w6_prop, "正反比例", 2), (_w6_scale, "比例尺", 2)],
}

# 经典模板（word_problems._TEMPLATES）的册别归属：(模板名, 年级) -> 册别
_CLASSIC_VOL = {
    ("乘加购物", 3): 1, ("乘加购物", 4): 2, ("乘加购物", 5): 2, ("乘加购物", 6): 2,
    ("盈亏问题", 3): 1, ("盈亏问题", 4): 2, ("盈亏问题", 5): 2, ("盈亏问题", 6): 2,
    ("相遇行程", 4): 2, ("相遇行程", 5): 2, ("相遇行程", 6): 2,
    ("行程追及", 4): 2, ("行程追及", 5): 2, ("行程追及", 6): 2,
    ("鸡兔同笼", 5): 1, ("鸡兔同笼", 6): 2,
    ("工程问题", 6): 1,
    ("折扣百分数", 6): 2, ("浓度问题", 6): 2, ("利润问题", 6): 2,
}


def generate_bank(grade, count, volume=1, kind="error"):
    """生成应用题题库：题库专项模板 + 经典模板（按年级适用范围、按册别）轮转，题干去重。
    volume：1=上册，2=下册。
    kind：'error'=易错题（默认，与历史行为一致），'common'=常见题。
    返回结构与 generate_word 的题目一致，可直接判题与导出；每题带 kind 字段。
    """
    kind_label = "易错题" if kind != "common" else "常见题"
    if kind == "common":
        pool = [(func, name) for func, name, vol in
                _COMMON_POOL.get(grade, []) if vol == volume]
    else:
        pool = [(func, name) for func, name, vol in _BANK_POOL[grade] if vol == volume]
        for t in _CLASSIC_TEMPLATES:
            if t["lo"] <= grade <= t["hi"] and _CLASSIC_VOL.get((t["name"], grade)) == volume:
                pool.append((lambda f=t["func"], g=grade: f(g), t["name"]))
    if not pool:
        return []
    random.shuffle(pool)

    seen = set()
    problems = []
    idx = 0
    attempts = 0
    # 每册扩到 1000 题后去重难度上升，尝试次数按题量放大
    max_attempts = count * 300
    while len(problems) < count and attempts < max_attempts:
        func, name = pool[idx % len(pool)]
        idx += 1
        attempts += 1
        data = func()
        q = data["question"]
        if q in seen:
            continue
        seen.add(q)
        problems.append({
            "type": "word",
            "grade": grade,
            "kind": kind_label,
            "category": "应用题-" + name,
            "question": q,
            "steps": data["steps"],
            "answer": [a["value"] for a in data["answers"]],
            "answer_labels": [a["label"] for a in data["answers"]],
            "answer_display": data["answer_display"],
            "solution": data["solution"],
            "tolerance": 1e-9,
            "note": "",
        })
    return problems
