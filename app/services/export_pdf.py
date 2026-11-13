# -*- coding: utf-8 -*-
"""PDF 导出（reportlab）：A4 紧凑排版，预留做题空白，空间按题量自适应压缩
- 计算题两栏（9cm × 2）；竖式题两栏（题干省略"（用竖式计算）"前缀）；解方程、应用题单栏
- 题量少时用标准预留空间；题量多时逐级压缩空白，尽量排入一页
- 多日导出按页分组排版：连续多天在压缩空白后能放进同一页的挤在一页，尽量少用纸
- 中文字体：优先注册 Windows 自带 simhei.ttf，失败时退回内置 STSong-Light
"""
import io
import math
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table)

GRADE_NAMES = {1: "一年级", 2: "二年级", 3: "三年级", 4: "四年级",
               5: "五年级", 6: "六年级", 7: "七年级", 8: "八年级", 9: "九年级"}

_FONT = None


def _ensure_font():
    """注册中文字体，返回可用字体名（进程内只注册一次）"""
    global _FONT
    if _FONT:
        return _FONT
    try:
        pdfmetrics.registerFont(TTFont("Hei", r"C:\Windows\Fonts\simhei.ttf"))
        _FONT = "Hei"
    except Exception:
        # 非Windows环境退回内置 CID 字体
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
            _FONT = "STSong-Light"
        except Exception:
            _FONT = "Helvetica"
    return _FONT


def _styles():
    font = _ensure_font()
    return {
        "title": ParagraphStyle("title", fontName=font, fontSize=14,
                                 leading=19, alignment=1, spaceAfter=2),
        "info": ParagraphStyle("info", fontName=font, fontSize=10,
                               leading=14, alignment=1, spaceAfter=6),
        "section": ParagraphStyle("section", fontName=font, fontSize=12,
                                  leading=16, spaceBefore=4, spaceAfter=4),
        "body": ParagraphStyle("body", fontName=font, fontSize=12,
                               leading=17, spaceAfter=2),
        "answer": ParagraphStyle("answer", fontName=font, fontSize=11,
                                 leading=16, spaceAfter=2),
    }


def _answer_text(problem):
    if problem["type"] in ("word", "equation"):
        return problem.get("answer_display", "")
    return str(problem.get("answer", ""))


# 一页可用高度（pt）：A4 高 842 - 上边距 51 - 下边距 37
_AVAIL_PT = 754

# 预留空间梯度（pt）：演算区 / 竖式书写区 / 应用题答题区
# 1cm ≈ 28.35pt；标准 1.2/2.6/2.6cm，紧凑约 0.85/2.0/2.0cm，最小约 0.6/1.6/1.6cm；
# 最后两级用于多日导出：进一步压缩空白，尽量把多天挤进同一页
_PAD_LADDERS = [
    (34, 74, 74),
    (24, 57, 57),
    (17, 45, 45),
    (12, 30, 30),
    (10, 28, 28),
]


def _day_height(problems, pads):
    """估算一天题集排版所需高度（pt），题干按每行约 40 字符折行估算"""
    calc_pad, vert_pad, word_pad = pads
    calcs = [p for p in problems if p["type"] == "calc"]
    verts = [p for p in problems if p["type"] == "vertical"]
    eqs = [p for p in problems if p["type"] == "equation"]
    words = [p for p in problems if p["type"] == "word"]
    h = 41  # 标题 + 日期说明行
    if calcs:
        rows = math.ceil(len(calcs) / 3)  # 计算题三栏排版
        # +6 为表格单元格上下内边距（每行 3pt × 2）
        h += 24 + rows * (19 + calc_pad + 6)
    if verts:
        rows = math.ceil(len(verts) / 2)
        h += 24 + rows * (19 + vert_pad + 6)
    h += len(eqs) * (19 + 62)  # 解方程单栏，约 2.2cm
    if words:
        lines = sum(max(1, math.ceil(len(p.get("question", "")) / 40))
                    for p in words)
        h += 24 + lines * 17 + len(words) * (2 + word_pad)
    return h


# 同一页内天与天之间的分隔间隔（0.6cm）
_DAY_SEP_PT = 17


def _group_height(datasets, pads):
    """一组（连续若干天）在当前空间梯度下的估算总高度（pt）"""
    h = sum(_day_height(ds["problems"], pads) for ds in datasets)
    return h + _DAY_SEP_PT * (len(datasets) - 1)


def _plan_groups(datasets):
    """贪心分页：尽量把连续几天排进同一页（页面尽量少占用）。
    每组从头尝试各空间梯度，取能容纳的最大天数；单日导出等价于按天选梯度。"""
    groups = []
    i, n = 0, len(datasets)
    while i < n:
        best_j, best_pads = i + 1, None
        for j in range(i + 1, n + 1):
            pads = next((p for p in _PAD_LADDERS
                         if _group_height(datasets[i:j], p) <= _AVAIL_PT), None)
            if pads is None:
                break
            best_j, best_pads = j, pads
        if best_pads is None:
            # 单天连最小空间都放不下：用最小梯度由 PDF 自然分页
            best_j, best_pads = i + 1, _PAD_LADDERS[-1]
        groups.append((i, best_j, best_pads))
        i = best_j
    return groups


def _append_day(dataset, story, styles, pads):
    """把一天的题集内容（三个分节）追加到 story，预留空间由所在分组决定"""
    grade = dataset["grade"]
    problems = dataset["problems"]
    calc_pad, vert_pad, word_pad = pads

    # ---- 一、计算题（三栏，省纸） ----
    calcs = [p for p in problems if p["type"] == "calc"]
    if calcs:
        story.append(Paragraph("一、计算题（共 %d 题）" % len(calcs), styles["section"]))
        rows = []
        for i in range(0, len(calcs), 3):
            row = []
            for p in calcs[i:i + 3]:
                cell = [Paragraph("%s ______" % escape(p["question"]), styles["body"]),
                        Spacer(1, calc_pad)]
                row.append(cell)
            while len(row) < 3:
                row.append("")
            rows.append(row)
        table = Table(rows, colWidths=[6 * cm, 6 * cm, 6 * cm])
        story.append(table)

    # ---- 二、竖式 / 解方程（竖式两栏，解方程单栏） ----
    slot = [p for p in problems if p["type"] in ("vertical", "equation")]
    if slot:
        if grade <= 6:
            title = "二、竖式计算（共 %d 题，请列竖式计算）" % len(slot)
        else:
            title = "二、解方程与化简求值（共 %d 题，请写出解答过程）" % len(slot)
        story.append(Paragraph(title, styles["section"]))
        verticals = [p for p in slot if p["type"] == "vertical"]
        if verticals:
            # 竖式题两栏排版（标题已说明要求，题干省略"（用竖式计算）"前缀）
            rows = []
            for i in range(0, len(verticals), 2):
                row = []
                for p in verticals[i:i + 2]:
                    q = p["question"].replace("（用竖式计算）", "")
                    cell = [Paragraph("%s ______" % escape(q), styles["body"]),
                            Spacer(1, vert_pad)]
                    row.append(cell)
                while len(row) < 2:
                    row.append("")
                rows.append(row)
            story.append(Table(rows, colWidths=[9 * cm, 9 * cm]))
        for p in slot:
            if p["type"] == "equation":
                story.append(Paragraph("%s ______" % escape(p["question"]), styles["body"]))
                story.append(Spacer(1, 2.2 * cm))

    # ---- 三、应用题（单栏） ----
    words = [p for p in problems if p["type"] == "word"]
    if words:
        story.append(Paragraph("三、应用题（共 %d 题，请写出解答过程）" % len(words), styles["section"]))
        for p in words:
            story.append(Paragraph(escape(p["question"]), styles["body"]))
            story.append(Spacer(1, word_pad))


def export_pdf(datasets, with_answers=False):
    """生成 PDF 文件，返回 (BytesIO, 文件名)
    datasets：题集列表；单日导出传一个元素，多日导出按页分组排版（连续多天可共享一页）
    """
    multi = len(datasets) > 1
    first = datasets[0]
    grade = first["grade"]
    date_str = first["date"]
    grade_name = GRADE_NAMES.get(grade, str(grade))
    styles = _styles()
    font = _ensure_font()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.8 * cm, bottomMargin=1.3 * cm,
        title="每日数学练习 %s" % date_str)

    def _header(canvas, _doc):
        canvas.saveState()
        canvas.setFont(font, 10)
        canvas.drawString(1.5 * cm, A4[1] - 1.1 * cm, "%s  %s" % (date_str, grade_name))
        canvas.drawRightString(A4[0] - 1.5 * cm, A4[1] - 1.1 * cm, "姓名：____________")
        canvas.restoreState()

    story = []
    for gi, (start, end, pads) in enumerate(_plan_groups(datasets)):
        if gi > 0:
            # 分组间强制换页：组内连续多天共享一页，组间另起新页
            story.append(PageBreak())
        for k in range(start, end):
            ds = datasets[k]
            if k > start:
                # 同组内天与天之间留小间隔以省纸
                story.append(Spacer(1, 0.6 * cm))
            g_name = GRADE_NAMES.get(ds["grade"], str(ds["grade"]))
            story.append(Paragraph("每日数学练习", styles["title"]))
            story.append(Paragraph("%s · %s" % (escape(ds["date"]), escape(g_name)),
                                   styles["info"]))
            _append_day(ds, story, styles, pads)

    # ---- 参考答案页（多日时按天分组） ----
    if with_answers:
        story.append(PageBreak())
        story.append(Paragraph("参考答案", styles["title"]))
        for ds in datasets:
            if multi:
                story.append(Paragraph(escape(ds["date"]), styles["section"]))
            for p in ds["problems"]:
                story.append(Paragraph("%s. %s" % (p["id"], escape(_answer_text(p))),
                                        styles["answer"]))

    doc.build(story, onFirstPage=_header, onLaterPages=_header)
    buf.seek(0)
    suffix = "_含答案" if with_answers else ""
    if multi:
        filename = "数学练习_%s至%s_%s%s.pdf" % (
            date_str, datasets[-1]["date"], grade_name, suffix)
    else:
        filename = "数学练习_%s_%s%s.pdf" % (date_str, grade_name, suffix)
    return buf, filename
