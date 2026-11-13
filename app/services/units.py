# -*- coding: utf-8 -*-
"""北师大版小学数学教材单元表（1-6 年级 × 上下册共 12 册）与单元出题参数

- 每册单元按教材顺序排列；每个单元可定义三类出题内容：
  calc: 计算题 kind 名（见 generators.arithmetic.CALC_KINDS）
  vert: 竖式题 kind 名（见 generators.arithmetic.VERT_KINDS）
  word: 应用题模板名（题库 category = "应用题-" + 模板名，须与
        word_bank._BANK_POOL / _COMMON_POOL / _CLASSIC_VOL 中的模板名一致）
- 认识类/图形类等不出题的单元不定义 calc/vert/word；仅勾选这类单元时
  由调用方按"更早已学单元补足 → 减量"规则回退
- calc/vert 中的 "*" 表示本册全池（总复习性质），question_specs 会转为不限制
- 7-9 年级（初中）无单元表，不做单元过滤
"""

UNITS = {
    1: {
        1: [  # 一年级上册（2024 新版，5 个编号单元）
            {"name": "生活中的数"},
            {"name": "5以内数加与减",
             "calc": ["add10", "sub10"], "vert": ["v_add10", "v_sub10"],
             "word": ["求总数", "比多少", "求剩余"]},
            {"name": "整理与分类"},
            {"name": "10以内数加与减",
             "calc": ["add10", "sub10"], "vert": ["v_add10", "v_sub10"],
             "word": ["连加连减", "排队问题", "求部分数", "多余条件"]},
            {"name": "有趣的立体图形"},
        ],
        2: [  # 一年级下册（2024 新版，6 个编号单元 + 综合实践）
            {"name": "20以内数与加法",
             "calc": ["carry_add20"], "vert": ["v_carry_add20"]},
            {"name": "图形大变身（一）"},
            {"name": "20以内数与减法",
             "calc": ["borrow_sub20"], "vert": ["v_borrow_sub20"],
             "word": ["比多少逆向", "求比一个数少几"]},
            {"name": "100以内数的认识"},
            {"name": "100以内数加与减（一）",
             "calc": ["add100_nc", "sub100_nb"],
             "vert": ["v_add100_nc", "v_sub100_nb"],
             "word": ["逆向求原数", "连加应用", "连减应用", "加减混合", "求原来"]},
            {"name": "动手做（二）"},
            {"name": "综合实践（欢乐购物）", "word": ["购物付钱", "购物找零"]},
        ],
    },
    2: {
        1: [  # 二年级上册（2024 新版，8 个编号单元 + 综合实践）
            {"name": "100以内数加与减（二）",
             "calc": ["add100_c", "sub100_b"],
             "vert": ["v_add100_c", "v_sub100_b"]},
            {"name": "测量（一）"},
            {"name": "数一数与乘法", "word": ["乘法含义", "加乘辨析"]},
            {"name": "乘法口诀（一）",
             "calc": ["mul_t25"], "word": ["乘加应用", "乘减应用", "乘加乘减"]},
            {"name": "分一分与除法",
             "calc": ["div_t"], "word": ["平均分"]},
            {"name": "图形的运动（一）"},
            {"name": "乘法口诀（二）", "calc": ["mul_t69"]},
            {"name": "乘除法的应用（一）",
             "word": ["倍的含义", "倍数关系"]},
            {"name": "综合实践（欢乐购物）", "word": ["人民币"]},
        ],
        2: [  # 二年级下册（现行版 8 个编号单元 + 数学好玩）
            {"name": "除法（竖式与有余数除法）",
             "calc": ["div_t"], "vert": ["v_div_t"],
             "word": ["有余数除法", "租船进一", "进一法", "去尾问题"]},
            {"name": "方向与位置"},
            {"name": "生活中的大数（万以内数）", "word": ["万以内数"]},
            {"name": "测量（长度单位）", "word": ["长度单位", "长度应用"]},
            {"name": "加与减（三位数笔算）",
             "calc": ["add3", "sub3"], "vert": ["v_add3", "v_sub3"],
             "word": ["万以内加减", "两步应用"]},
            {"name": "认识图形"},
            {"name": "时、分、秒", "word": ["经过时间"]},
            {"name": "调查与记录"},
            {"name": "数学好玩（综合）", "word": ["周期规律"]},
        ],
    },
    3: {
        1: [  # 三年级上册（8 个编号单元）
            {"name": "混合运算", "calc": ["mixed"],
             "word": ["乘加购物", "盈亏问题"]},
            {"name": "观察物体"},
            {"name": "加与减（三位数加减）",
             "calc": ["add3", "sub3"], "vert": ["v_add3", "v_sub3"],
             "word": ["里程表"]},
            {"name": "乘与除（口算乘除）",
             "calc": ["oral_muldiv"], "word": ["连乘应用"]},
            {"name": "周长", "word": ["周长应用", "周长单位陷阱"]},
            {"name": "乘法", "calc": ["mul1"], "vert": ["v_mul1"]},
            {"name": "年、月、日", "word": ["年月日", "经过时间"]},
            {"name": "认识小数", "word": ["小数初步"]},
        ],
        2: [  # 三年级下册（7 个编号单元）
            {"name": "除法（两三位数除以一位数）",
             "calc": ["div1"], "vert": ["v_div1"],
             "word": ["归一问题", "连除应用"]},
            {"name": "图形的运动"},
            {"name": "乘法（两位数乘两位数）",
             "calc": ["mul1", "mul2"], "vert": ["v_mul1", "v_mul2"],
             "word": ["归总问题", "两位数乘两位数", "铺地砖", "乘除混合"]},
            {"name": "千克、克、吨", "word": ["质量单位"]},
            {"name": "面积", "word": ["面积应用", "面积单位换算"]},
            {"name": "认识分数", "word": ["分数初步"]},
            {"name": "数据的整理和表示"},
        ],
    },
    4: {
        1: [  # 四年级上册（8 个编号单元，数学好玩穿插其中）
            {"name": "认识更大的数", "word": ["大数组成", "近似数"]},
            {"name": "线与角"},
            {"name": "乘法",
             "calc": ["mul3"], "vert": ["v_mul3"],
             "word": ["单价总价", "速度路程", "相遇问题", "三位数乘两位数"]},
            {"name": "运算律", "calc": ["simple"], "word": ["运算律应用"]},
            {"name": "方向与位置"},
            {"name": "除法",
             "calc": ["div2"], "vert": ["v_div2"]},
            {"name": "生活中的负数", "word": ["正负数"]},
            {"name": "数学好玩",
             "word": ["植树问题", "和差问题", "给后相同"]},
            {"name": "可能性"},
        ],
        2: [  # 四年级下册（6 个编号单元 + 数学好玩）
            {"name": "小数的意义和加减法",
             "calc": ["dec_add", "dec_sub"],
             "vert": ["v_dec_add", "v_dec_sub"],
             "word": ["小数购物", "小数加减混合"]},
            {"name": "认识三角形和四边形", "word": ["三角形边角", "角度"]},
            {"name": "小数乘法",
             "calc": ["dec_mul_int"], "vert": ["v_dec_mul"],
             "word": ["小数乘法应用"]},
            {"name": "观察物体"},
            {"name": "认识方程", "word": ["列方程应用"]},
            {"name": "数学好玩（综合复习）",
             "word": ["平均数", "乘加购物", "盈亏问题", "相遇行程", "行程追及"]},
        ],
    },
    5: {
        1: [  # 五年级上册（7 个编号单元 + 数学好玩）
            {"name": "小数除法",
             "calc": ["dec_div"], "vert": ["v_dec_div"],
             "word": ["小数除法应用", "分段计费", "进一去尾"]},
            {"name": "轴对称和平移"},
            {"name": "倍数与因数", "word": ["公倍数应用"]},
            {"name": "多边形的面积", "word": ["多边形面积"]},
            {"name": "分数的意义"},
            {"name": "组合图形的面积"},
            {"name": "可能性"},
            {"name": "数学好玩（综合复习）",
             "word": ["和倍问题", "差倍问题", "鸡兔同笼", "小数乘法应用"]},
        ],
        2: [  # 五年级下册（8 个编号单元 + 数学好玩）
            {"name": "分数加减法",
             "calc": ["frac_add_diff"], "word": ["分数加减应用"]},
            {"name": "长方体（一）", "word": ["长方体"]},
            {"name": "分数乘法",
             "calc": ["frac_mul_mix"], "word": ["分数乘法应用"]},
            {"name": "长方体（二）体积与容积", "word": ["体积容积", "排水法"]},
            {"name": "分数除法", "word": ["分数除法逆向"]},
            {"name": "确定位置"},
            {"name": "用方程解决问题", "word": ["列方程应用"]},
            {"name": "数据的表示和分析"},
            {"name": "数学好玩（综合复习）",
             "word": ["乘加购物", "盈亏问题", "相遇行程", "行程追及"]},
        ],
    },
    6: {
        1: [  # 六年级上册（7 个编号单元）
            {"name": "圆", "word": ["圆的周长面积", "圆面积", "外方内圆"]},
            {"name": "分数混合运算", "calc": ["frac_mixed"],
             "word": ["分数应用", "分数混合应用", "求单位1", "工程问题"]},
            {"name": "观察物体"},
            {"name": "百分数", "calc": ["pct_calc"],
             "word": ["百分率应用", "合格率"]},
            {"name": "数据处理"},
            {"name": "比的认识", "word": ["按比分配"]},
            {"name": "百分数的应用",
             "word": ["涨降价陷阱", "利息", "纳税"]},
        ],
        2: [  # 六年级下册（总复习年，计算/竖式不按单元细分）
            {"name": "圆柱与圆锥",
             "word": ["圆柱体积", "圆锥体积", "圆柱侧面积"]},
            {"name": "比例", "word": ["比例尺"]},
            {"name": "图形的运动"},
            {"name": "正比例与反比例", "word": ["正反比例", "反比例应用"]},
            {"name": "总复习",
             "calc": ["*"], "vert": ["*"],
             "word": ["公倍数复习", "分数除法复习", "鸡兔同笼", "折扣百分数",
                      "浓度问题", "利润问题", "乘加购物", "盈亏问题",
                      "相遇行程", "行程追及"]},
        ],
    },
}


def unit_names(grade, volume):
    """返回某册的单元名列表（教材顺序）；7-9 年级或未知册别返回空列表"""
    vol_units = UNITS.get(grade, {}).get(volume)
    return [u["name"] for u in vol_units] if vol_units else []


def _merge(target, items):
    if items:
        target.update(items)


def question_specs(grade, volume, selected):
    """按勾选单元计算出题参数（供 daily_set 精确按单元出题）

    selected: 勾选的单元名列表；None/空 = 不限制
    返回 dict，键为 calc_sel / calc_all / vert_sel / vert_all /
    word_sel / word_all：
    - *_sel：勾选单元对应 kind（或应用题 category）的并集
    - *_all：在 *_sel 基础上并入教材顺序中位于所选单元之前的单元
      （已学过的复习内容，题量不足时补足用）
    - None 表示该题型不限制；空 set 表示勾选的单元不含该题型内容
    - calc/vert 含 "*" 的单元（总复习）直接转为 None（本册全池）
    """
    no_filter = {"calc_sel": None, "calc_all": None, "vert_sel": None,
                 "vert_all": None, "word_sel": None, "word_all": None}
    vol_units = UNITS.get(grade, {}).get(volume)
    if not vol_units or not selected:
        return no_filter
    sel_set = set(selected)
    max_idx = -1
    calc_sel, vert_sel, word_sel = set(), set(), set()
    for i, u in enumerate(vol_units):
        if u.get("name") not in sel_set:
            continue
        max_idx = max(max_idx, i)
        _merge(calc_sel, u.get("calc"))
        _merge(vert_sel, u.get("vert"))
        _merge(word_sel, u.get("word"))
    if max_idx < 0:
        # 勾选的单元名不属于本册（旧数据残留等）→ 不限制
        return no_filter
    calc_all, vert_all, word_all = set(calc_sel), set(vert_sel), set(word_sel)
    for i in range(max_idx):
        u = vol_units[i]
        _merge(calc_all, u.get("calc"))
        _merge(vert_all, u.get("vert"))
        _merge(word_all, u.get("word"))

    # 整册无任何单元定义某题型（如五下/六上竖式为纯复习内容）时，
    # 该题型不做单元限制，避免选中部分单元后竖式题减量为 0
    vol_has_calc = any(u.get("calc") for u in vol_units)
    vol_has_vert = any(u.get("vert") for u in vol_units)

    def _norm_kinds(s, has):
        if not has:
            return None
        if s is None:
            return None
        if "*" in s:
            return None  # 总复习 → 本册全池
        return s

    def _norm_words(s):
        if s is None:
            return None
        return {"应用题-" + w for w in s}

    return {
        "calc_sel": _norm_kinds(calc_sel, vol_has_calc),
        "calc_all": _norm_kinds(calc_all, vol_has_calc),
        "vert_sel": _norm_kinds(vert_sel, vol_has_vert),
        "vert_all": _norm_kinds(vert_all, vol_has_vert),
        "word_sel": _norm_words(word_sel),
        "word_all": _norm_words(word_all),
    }
