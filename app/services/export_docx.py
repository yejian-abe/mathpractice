# -*- coding: utf-8 -*-
"""Word 导出（python-docx）：A4 紧凑排版，预留做题空白，空间按题量自适应压缩
- 页眉：日期·年级 + 姓名栏
- 计算题三栏制表位段落（不用表格）；竖式题两栏表格（题干省略"（用竖式计算）"前缀）；解方程、应用题单栏
- 题量少时用标准预留空间；题量多时逐级压缩空白，尽量排入一页
- 多日导出按页分组排版：连续多天在压缩空白后能放进同一页的挤在一页，尽量少用纸
"""
import io
import math
from datetime import datetime

# python-docx 仅桌面端安装（APK 端 requirements 不含），缺失时导出端点返回友好提示
try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

GRADE_NAMES = {1: "一年级", 2: "二年级", 3: "三年级", 4: "四年级",
               5: "五年级", 6: "六年级", 7: "七年级", 8: "八年级", 9: "九年级"}

# 各题型序号标签（用于导出分节标题与答案页）
SECTION_CALC = "一、计算题"
SECTION_VERT = "二、竖式计算（请列竖式计算）"
SECTION_EQ = "二、解方程与化简求值（请写出解答过程）"
SECTION_WORD = "三、应用题（请写出解答过程）"


def _add_para(target, text="", size=12, bold=False, align=None, space_after=6):
    """添加段落并设置中文字体"""
    p = target.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def _blank(target, lines, line_pt=26):
    """预留 n 个固定行高的空白行（约 lines × line_pt 磅高度）"""
    for _ in range(lines):
        p = target.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = Pt(line_pt)


def _no_borders(table):
    """去掉表格边框（用于两栏排版）"""
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "none")
        borders.append(el)
    tbl_pr.append(borders)


def _answer_text(problem):
    """答案页文本"""
    if problem["type"] == "word":
        return problem.get("answer_display", "")
    if problem["type"] == "equation":
        return problem.get("answer_display", "")
    return str(problem.get("answer", ""))


# 预留空白行梯度：(演算区 行数,行高pt) / (竖式区) / (应用题答题区)
# 与 PDF 的空间梯度对应：标准 → 紧凑 → 最小；最后一档用于多日导出挤同一页
_BLANK_LADDERS = [
    ((2, 20), (3, 24), (3, 26)),
    ((2, 17), (3, 19), (3, 19)),
    ((1, 17), (2, 19), (2, 15)),
    ((1, 12), (2, 14), (2, 12)),
]


def _day_height_blanks(problems, blanks):
    """估算一天题集在 Word 中的排版高度（pt），题干按每行约 40 字符折行"""
    (cn, cp), (vn, vp), (wn, wp) = blanks
    calcs = [p for p in problems if p["type"] == "calc"]
    verts = [p for p in problems if p["type"] == "vertical"]
    eqs = [p for p in problems if p["type"] == "equation"]
    words = [p for p in problems if p["type"] == "word"]
    h = 44  # 标题 + 日期说明行
    if calcs:
        h += 24 + (len(calcs) + 2) // 3 * (20 + cn * cp)  # 计算题三栏制表位段落
    if verts:
        h += 24 + (len(verts) + 1) // 2 * (18 + vn * vp)
    h += len(eqs) * (18 + 72)  # 解方程单栏
    if words:
        lines = sum(max(1, math.ceil(len(p.get("question", "")) / 40))
                    for p in words)
        h += 24 + lines * 18 + len(words) * wn * wp
    return h


# 一页可用高度（pt）：A4 高 842 - 上边距（含页眉占用）- 下边距，留少量余量
_AVAIL_PT = 740

# 同一页内天与天之间的分隔间隔（空段 + 段后距）
_DAY_SEP_PT = 24


def _group_height(datasets, blanks):
    """一组（连续若干天）在当前空白梯度下的估算总高度（pt）"""
    h = sum(_day_height_blanks(ds["problems"], blanks) for ds in datasets)
    return h + _DAY_SEP_PT * (len(datasets) - 1)


def _plan_groups(datasets):
    """贪心分页：尽量把连续几天排进同一页（页面尽量少占用）。
    每组从头尝试各空白梯度，取能容纳的最大天数；单日导出等价于按天选梯度。"""
    groups = []
    i, n = 0, len(datasets)
    while i < n:
        best_j, best_blanks = i + 1, None
        for j in range(i + 1, n + 1):
            blanks = next((b for b in _BLANK_LADDERS
                           if _group_height(datasets[i:j], b) <= _AVAIL_PT), None)
            if blanks is None:
                break
            best_j, best_blanks = j, blanks
        if best_blanks is None:
            # 单天连最小空白都放不下：用最小梯度由 Word 自然分页
            best_j, best_blanks = i + 1, _BLANK_LADDERS[-1]
        groups.append((i, best_j, best_blanks))
        i = best_j
    return groups


def _append_day(dataset, doc, blanks):
    """把一天的题集内容（三个分节）追加到 doc，预留空间由所在分组决定"""
    grade = dataset["grade"]
    problems = dataset["problems"]
    (calc_n, calc_pt), (vert_n, vert_pt), (word_n, word_pt) = blanks

    # ---- 一、计算题（三栏制表位段落，不用表格） ----
    calcs = [p for p in problems if p["type"] == "calc"]
    if calcs:
        _add_para(doc, "%s（共 %d 题）" % (SECTION_CALC, len(calcs)), size=12, bold=True)
        rows = (len(calcs) + 2) // 3
        for ri in range(rows):
            row = calcs[ri * 3:ri * 3 + 3]
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.line_spacing = 1.0
            # 题干行下方预留演算空白（代替表格单元格内的空白行）
            pf.space_after = Pt(calc_n * calc_pt + 4)
            pf.tab_stops.add_tab_stop(Cm(6), WD_TAB_ALIGNMENT.LEFT)
            pf.tab_stops.add_tab_stop(Cm(12), WD_TAB_ALIGNMENT.LEFT)
            run = p.add_run("\t".join(
                "%d. %s ______" % (ri * 3 + k + 1, q["question"])
                for k, q in enumerate(row)))
            run.font.size = Pt(12)
            run.font.name = "宋体"
            run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    # ---- 二、竖式 / 解方程（竖式两栏，解方程单栏） ----
    slot = [p for p in problems if p["type"] in ("vertical", "equation")]
    if slot:
        title = SECTION_VERT if grade <= 6 else SECTION_EQ
        _add_para(doc, "%s（共 %d 题）" % (title, len(slot)), size=12, bold=True)
        verticals = [p for p in slot if p["type"] == "vertical"]
        if verticals:
            # 竖式题两栏排版（标题已说明要求，题干省略"（用竖式计算）"前缀）
            rows = (len(verticals) + 1) // 2
            table = doc.add_table(rows=rows, cols=2)
            _no_borders(table)
            for idx, p in enumerate(verticals):
                cell = table.cell(idx // 2, idx % 2)
                q = p["question"].replace("（用竖式计算）", "")
                _add_para(cell, "%d. %s ______" % (idx + 1, q), space_after=0)
                _blank(cell, vert_n, line_pt=vert_pt)  # 竖式书写区
        for idx, p in enumerate(slot):
            if p["type"] == "equation":
                _add_para(doc, "%d. %s ______" % (idx + 1, p["question"]), space_after=0)
                _blank(doc, 3, line_pt=24)

    # ---- 三、应用题（单栏） ----
    words = [p for p in problems if p["type"] == "word"]
    if words:
        _add_para(doc, "%s（共 %d 题）" % (SECTION_WORD, len(words)), size=12, bold=True)
        for idx, p in enumerate(words):
            _add_para(doc, "%d. %s" % (idx + 1, p["question"]), space_after=0)
            _blank(doc, word_n, line_pt=word_pt)  # 答题区


def export_docx(datasets, with_answers=False):
    """生成 Word 文件，返回 (BytesIO, 文件名)
    datasets：题集列表；单日导出传一个元素，多日导出按页分组排版（连续多天可共享一页）
    """
    multi = len(datasets) > 1
    first = datasets[0]
    grade = first["grade"]
    date_str = first["date"]

    doc = Document()
    # 页边距（紧凑排版，题目尽量排入一页）
    section = doc.sections[0]
    section.top_margin = Cm(1.6)
    section.bottom_margin = Cm(1.3)
    section.left_margin = Cm(1.6)
    section.right_margin = Cm(1.6)
    # 页眉：日期·年级（左） + 姓名（右）
    header = section.header
    hp = header.paragraphs[0]
    hp.text = "%s  %s\t姓名：____________" % (date_str, GRADE_NAMES.get(grade, ""))
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT

    for gi, (start, end, blanks) in enumerate(_plan_groups(datasets)):
        if gi > 0:
            # 分组间强制换页：组内连续多天共享一页，组间另起新页
            doc.add_page_break()
        for k in range(start, end):
            ds = datasets[k]
            if k > start:
                # 同组内天与天之间留空段分隔以省纸
                _add_para(doc, "", size=12, space_after=8)
            # 标题（紧凑：一行主标题 + 一行说明）
            _add_para(doc, "每日数学练习", size=14, bold=True,
                      align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
            _add_para(doc, "%s · %s" % (ds["date"], GRADE_NAMES.get(ds["grade"], "")),
                      size=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
            _append_day(ds, doc, blanks)

    # ---- 参考答案页（多日时按天分组） ----
    if with_answers:
        doc.add_page_break()
        _add_para(doc, "参考答案", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        for ds in datasets:
            if multi:
                _add_para(doc, ds["date"], size=12, bold=True, space_after=4)
            for p in ds["problems"]:
                _add_para(doc, "%s. %s" % (p["id"], _answer_text(p)), size=11, space_after=2)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    suffix = "_含答案" if with_answers else ""
    grade_name = GRADE_NAMES.get(grade, str(grade))
    if multi:
        filename = "数学练习_%s至%s_%s%s.docx" % (
            date_str, datasets[-1]["date"], grade_name, suffix)
    else:
        filename = "数学练习_%s_%s%s.docx" % (date_str, grade_name, suffix)
    return buf, filename
