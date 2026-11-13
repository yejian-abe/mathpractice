# -*- coding: utf-8 -*-
"""REST API 路由
- GET  /api/daily?grade&date&user_id&semester&kind&units  获取/生成当日题集（对外隐藏答案）
- POST /api/regenerate                   重新生成当日题集（semester/kind/units 参数）
- POST /api/submit                       提交答案判题
- GET/POST /api/config                   题量配置
- GET  /api/units?grade&semester         教材单元列表（供设置页单元多选）
- GET  /api/export/pdf|docx              导出文件
- GET  /api/history?user_id             历史题集列表
- GET  /api/records?user_id&grade&date_from&date_to  练习记录列表（分题型正确数）
- GET  /api/records/detail?user_id&date&grade        单次练习详情
- GET/POST/DELETE /api/users             用户管理
- GET  /api/stats?user_id&grade          学情统计（正确率曲线 + 薄弱知识点）
"""
import json
import re
from datetime import date as _date
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_file

from app import config as config_mod, heartbeat
from app.services import bank, daily_set, export_docx, export_pdf, grading, \
    stats, users
from app.services import units as units_svc

api_bp = Blueprint("api", __name__)

# 对外返回题集时需要隐藏的字段（防止孩子通过浏览器开发者工具看答案）
_HIDDEN_FIELDS = ("answer", "solution", "answer_display")


def _data_dir():
    return current_app.config["DATA_DIR"]


def _today():
    return _date.today().isoformat()


def _grade_from(value, default=3):
    try:
        return min(9, max(1, int(value)))
    except (TypeError, ValueError):
        return default


def _grade_or_all(value):
    """练习记录的年级参数：0/空/非法 = 不限定年级（由服务端取最高年级）"""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 0
    return v if 1 <= v <= 9 else 0


def _user_id_from(value):
    """规范化用户 id：仅允许字母/数字/下划线（默认用户无题集文件名后缀）"""
    value = (value or "").strip()
    if re.match(r"^[A-Za-z0-9_]{1,32}$", value):
        return value
    return daily_set.DEFAULT_USER


def _semester_from(value):
    """学期参数：0=自动（按日期判断），1=上册，2=下册；非法值回退自动"""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 0
    return v if v in (1, 2) else 0


def _bank_kind_from(value):
    """题库类别参数：0/all=易错题+常见题，1=易错题，2=常见题；非法值回退全部"""
    v = str(value or "0").strip().lower()
    return {"1": "error", "2": "common"}.get(v, "all")


def _units_from(value):
    """教材单元过滤参数：字符串（JSON 数组）或列表；缺失/空/非法 = 不限制"""
    if value is None or value == "":
        return None
    if isinstance(value, (list, tuple)):
        items = value
    else:
        try:
            items = json.loads(value)
        except (ValueError, TypeError):
            return None
    if not isinstance(items, (list, tuple)):
        return None
    names = []
    for u in items:
        s = str(u).strip()[:40]
        if s and s not in names:
            names.append(s)
    return names or None


def _public_set(dataset):
    """去除答案字段后的题集（保留 attempts 供前端恢复作答状态）"""
    problems = []
    for p in dataset.get("problems", []):
        q = {k: v for k, v in p.items() if k not in _HIDDEN_FIELDS}
        # 应用题：不再下发分步提示（完整步骤仅在提交后的解析中展示），
        # answer_labels（最终答案的标签列表）保留供前端渲染输入框
        if q.get("type") == "word":
            q.pop("steps", None)
        # 解方程题保留 answer_vars 变量名列表（前端据此渲染输入框），
        # 答案值已在隐藏字段中剔除
        problems.append(q)
    public = dict(dataset)
    public["problems"] = problems
    return public


def _public_equation_vars(dataset):
    """给解方程题补上变量名列表（如 ["x"] / ["x","y"] / ["x1","x2"] / ["值"]）"""
    for p in dataset.get("problems", []):
        if p.get("type") == "equation":
            p["answer_vars"] = list((p.get("answer") or {}).keys())
    return dataset


@api_bp.route("/daily")
def api_daily():
    grade = _grade_from(request.args.get("grade"))
    dt = request.args.get("date") or _today()
    uid = _user_id_from(request.args.get("user_id"))
    semester = _semester_from(request.args.get("semester"))
    kind = _bank_kind_from(request.args.get("kind"))
    units = _units_from(request.args.get("units"))
    dataset = daily_set.get_or_create(_data_dir(), dt, grade, uid, semester,
                                      kind, units)
    dataset = _public_equation_vars(dataset)
    return jsonify(_public_set(dataset))


@api_bp.route("/units")
def api_units():
    """教材单元列表（按年级×学期册别，供设置页单元多选）"""
    grade = _grade_from(request.args.get("grade"))
    semester = _semester_from(request.args.get("semester"))
    volume = semester or bank.current_volume(_today())
    return jsonify({
        "grade": grade,
        "volume": volume,
        "units": units_svc.unit_names(grade, volume),
    })


@api_bp.route("/regenerate", methods=["POST"])
def api_regenerate():
    body = request.get_json(force=True, silent=True) or {}
    grade = _grade_from(body.get("grade"))
    dt = body.get("date") or _today()
    uid = _user_id_from(body.get("user_id"))
    semester = _semester_from(body.get("semester"))
    kind = _bank_kind_from(body.get("kind"))
    units = _units_from(body.get("units"))
    dataset = daily_set.regenerate(_data_dir(), dt, grade, uid, semester, kind,
                                   units)
    dataset = _public_equation_vars(dataset)
    return jsonify(_public_set(dataset))


@api_bp.route("/submit", methods=["POST"])
def api_submit():
    body = request.get_json(force=True, silent=True) or {}
    grade = _grade_from(body.get("grade"))
    dt = body.get("date") or _today()
    uid = _user_id_from(body.get("user_id"))
    pid = body.get("problem_id")

    dataset = daily_set.load_set(_data_dir(), dt, grade, uid)
    if dataset is None:
        return jsonify({"error": "题集不存在，请先获取当日题目"}), 404
    problem = daily_set.find_problem(dataset, pid)
    if problem is None:
        return jsonify({"error": "题目不存在"}), 404

    payload = {"main": body.get("main"), "answers": body.get("answers")}
    result = grading.grade_problem(problem, payload)
    # 记录作答，供刷新后恢复
    attempt = {
        "payload": payload,
        "result": result,
        "at": datetime.now().isoformat(),
    }
    daily_set.update_attempt(_data_dir(), dt, grade, pid, attempt, uid)
    return jsonify(result)


@api_bp.route("/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        body = request.get_json(force=True, silent=True) or {}
        merged = config_mod.load_config(_data_dir())
        for key in ("calc_count", "vertical_count", "word_count"):
            if key in body:
                try:
                    merged[key] = min(20, max(0, int(body[key])))
                except (TypeError, ValueError):
                    pass
        config_mod.save_config(_data_dir(), merged)
        return jsonify(merged)
    return jsonify(config_mod.load_config(_data_dir()))


@api_bp.route("/export/<fmt>")
def api_export(fmt):
    grade = _grade_from(request.args.get("grade"))
    dt = request.args.get("date") or _today()
    dt_to = (request.args.get("date_to") or "").strip()
    uid = _user_id_from(request.args.get("user_id"))
    with_answers = request.args.get("with_answers", "0") in ("1", "true", "yes")
    semester = _semester_from(request.args.get("semester"))
    kind = _bank_kind_from(request.args.get("kind"))
    units = _units_from(request.args.get("units"))

    datasets = None
    if dt_to and dt_to > dt:
        # 多日导出：范围内缺失日期自动补生成（与单日导出行为一致，
        # 保证导出 N 天就有 N 天的题）
        try:
            d1 = _date.fromisoformat(dt)
            d2 = _date.fromisoformat(dt_to)
        except ValueError:
            return jsonify({"error": "日期格式不正确"}), 400
        if (d2 - d1).days > 62:
            return jsonify({"error": "日期范围过大（最多 62 天）"}), 400
        datasets = []
        cur = d1
        while cur <= d2:
            datasets.append(daily_set.get_or_create(
                _data_dir(), cur.isoformat(), grade, uid, semester, kind,
                units))
            cur = _date.fromordinal(cur.toordinal() + 1)
    else:
        # 单日导出：不存在则自动生成（保持原有行为）
        datasets = [daily_set.get_or_create(_data_dir(), dt, grade, uid,
                                            semester, kind, units)]

    if fmt == "pdf":
        if not export_pdf.PDF_OK:
            return jsonify({"error": "本设备暂不支持导出 PDF，请在电脑端使用导出功能"}), 503
        buf, filename = export_pdf.export_pdf(datasets, with_answers)
        mimetype = "application/pdf"
    elif fmt == "docx":
        if not export_docx.DOCX_OK:
            return jsonify({"error": "本设备暂不支持导出 Word，请在电脑端使用导出功能"}), 503
        buf, filename = export_docx.export_docx(datasets, with_answers)
        mimetype = ("application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document")
    else:
        return jsonify({"error": "不支持的导出格式"}), 400
    return send_file(buf, mimetype=mimetype, as_attachment=True,
                     download_name=filename)


@api_bp.route("/history")
def api_history():
    uid = _user_id_from(request.args.get("user_id"))
    return jsonify(daily_set.list_history(_data_dir(), uid))


# ---------- 练习记录 ----------

@api_bp.route("/records")
def api_records():
    """练习记录列表：时间范围 + 年级筛选，按日期倒序，含各题型正确数"""
    uid = _user_id_from(request.args.get("user_id"))
    grade = _grade_or_all(request.args.get("grade"))
    date_from = (request.args.get("date_from") or "").strip()
    date_to = (request.args.get("date_to") or "").strip()
    return jsonify(daily_set.list_records(_data_dir(), uid, grade,
                                          date_from or None, date_to or None))


@api_bp.route("/records/detail")
def api_record_detail():
    """单次练习详情：逐题题干、我的作答与对错（不含正确答案）"""
    uid = _user_id_from(request.args.get("user_id"))
    grade = _grade_from(request.args.get("grade"))
    dt = request.args.get("date") or _today()
    detail = daily_set.record_detail(_data_dir(), dt, grade, uid)
    if detail is None:
        return jsonify({"error": "题集不存在"}), 404
    return jsonify(detail)


@api_bp.route("/sets/generate", methods=["POST"])
def api_sets_generate():
    """按起止日期批量生成题集（缺失的补生成），返回列表供导出页展示"""
    body = request.get_json(force=True, silent=True) or {}
    grade = _grade_from(body.get("grade"))
    dt = body.get("date") or _today()
    dt_to = (body.get("date_to") or "").strip()
    uid = _user_id_from(body.get("user_id"))
    semester = _semester_from(body.get("semester"))
    kind = _bank_kind_from(body.get("kind"))
    units = _units_from(body.get("units"))
    try:
        d1 = _date.fromisoformat(dt)
        d2 = _date.fromisoformat(dt_to) if dt_to else d1
    except ValueError:
        return jsonify({"error": "日期格式不正确"}), 400
    if d2 < d1:
        d1, d2 = d2, d1
    if (d2 - d1).days > 62:
        return jsonify({"error": "日期范围过大（最多 62 天）"}), 400
    items = []
    cur = d1
    while cur <= d2:
        ds = daily_set.get_or_create(_data_dir(), cur.isoformat(), grade, uid,
                                     semester, kind, units)
        items.append({"date": ds["date"], "grade": ds["grade"],
                      "volume": daily_set.volume_of(ds, semester)})
        cur = _date.fromordinal(cur.toordinal() + 1)
    return jsonify({"items": items})


# ---------- 用户管理 ----------

@api_bp.route("/users", methods=["GET", "POST", "DELETE"])
def api_users():
    if request.method == "POST":
        body = request.get_json(force=True, silent=True) or {}
        user, err = users.create_user(_data_dir(), body.get("name"))
        if err:
            return jsonify({"error": err}), 400
        return jsonify(user)
    if request.method == "DELETE":
        body = request.get_json(force=True, silent=True) or {}
        uid = _user_id_from(body.get("user_id"))
        ok, err = users.delete_user(_data_dir(), uid)
        if not ok:
            return jsonify({"error": err}), 400
        return jsonify({"ok": True})
    return jsonify(users.list_users(_data_dir()))


# ---------- 学情统计 ----------

@api_bp.route("/caps")
def api_caps():
    """设备能力：安卓 APK 端未打包导出库，前端据此隐藏导出按钮"""
    return jsonify({"export": bool(export_pdf.PDF_OK and export_docx.DOCX_OK)})


@api_bp.route("/stats")
def api_stats():
    uid = _user_id_from(request.args.get("user_id"))
    grade = request.args.get("grade")
    try:
        grade = _grade_from(grade, default=None)
    except Exception:
        grade = None
    semester = (request.args.get("semester") or "0")[:2]
    return jsonify(stats.compute_stats(_data_dir(), uid, grade, semester))


@api_bp.route("/heartbeat", methods=["POST"])
def api_heartbeat():
    """页面存活心跳：前端定时上报，页面全部关闭后服务自动退出"""
    heartbeat.record()
    return jsonify({"ok": True})
