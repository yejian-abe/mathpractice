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
- GET  /api/wrongbook                    错题本列表（首答口径聚合）
- POST /api/wrongbook/tag                错因标记（粗心/不会）
- POST /api/wrongbook/resolve            标记已掌握
- POST /api/wrongbook/practice           举一反三重练题集生成
- POST /api/wrongbook/answer             重练题集判题
- GET  /api/sprint/specials?grade        口算专项列表（按年级过滤）
- POST /api/sprint/start                 开启一局限时挑战（服务端计时）
- POST /api/sprint/submit                限时挑战交卷（校验用时+判分+个人最佳）
- GET  /api/sprint/best?user_id          各专项个人最佳
"""
import json
import re
from datetime import date as _date
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_file

from app import config as config_mod, heartbeat
from app import version as version_mod
from app.services import achievements as achievements_svc
from app.services import bank, daily_set, export_docx, export_pdf, grading, \
    print_bridge, sprint as sprint_svc, stats, users, wrongbook as wrongbook_svc
from app.services import finale as finale_svc
from app.services import papers as papers_svc
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


# 用户 id 白名单：字母/数字/下划线/汉字（CJK 基本区），长度 1-32。
# 点号、空格、路径分隔符等一律不在白名单（防文件名注入/路径遍历）
_USER_ID_RE = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]{1,32}$")


def _user_id_from(value):
    """规范化用户 id：仅允许字母/数字/下划线/汉字（默认用户无题集文件名后缀）"""
    value = (value or "").strip()
    if _USER_ID_RE.match(value):
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


# ---------- 错题本 ----------

@api_bp.route("/wrongbook")
def api_wrongbook():
    """错题列表（首答口径聚合）：grade=0 不限年级；status=open/resolved/all"""
    uid = _user_id_from(request.args.get("user_id"))
    grade = _grade_or_all(request.args.get("grade"))
    status = str(request.args.get("status") or "open")
    items = wrongbook_svc.list_wrong(_data_dir(), uid, grade=grade)
    if status == "open":
        items = [e for e in items if not e["resolved"]]
    elif status == "resolved":
        items = [e for e in items if e["resolved"]]
    return jsonify({"items": items})


@api_bp.route("/wrongbook/tag", methods=["POST"])
def api_wrongbook_tag():
    """错因标记：careless=粗心失误 / unknown=知识点不会 / 空串=取消"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    key = str(body.get("key") or "")
    if not key:
        return jsonify({"error": "缺少错题标识"}), 400
    wrongbook_svc.tag_mistake(_data_dir(), uid, key,
                              str(body.get("tag") or ""))
    return jsonify({"ok": True})


@api_bp.route("/wrongbook/resolve", methods=["POST"])
def api_wrongbook_resolve():
    """标记/取消已掌握（keys 为错题 key 数组）"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    keys = body.get("keys") if isinstance(body.get("keys"), list) else []
    resolved = bool(body.get("resolved", True))
    keys = [str(k) for k in keys if k]
    if not keys:
        return jsonify({"error": "缺少错题标识"}), 400
    wrongbook_svc.mark_resolved(_data_dir(), uid, keys, resolved)
    return jsonify({"ok": True})


@api_bp.route("/wrongbook/practice", methods=["POST"])
def api_wrongbook_practice():
    """举一反三：按错题 key 列表生成重练题集（原题重做 + 同型变式，
    对外隐藏答案，与 /api/daily 同规则）"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    keys = body.get("keys") if isinstance(body.get("keys"), list) else []
    set_id, dataset = wrongbook_svc.build_practice(_data_dir(), uid, keys)
    if dataset is None:
        return jsonify({"error": "未找到可重练的错题"}), 404
    dataset = _public_equation_vars(dataset)
    pub = _public_set(dataset)
    pub["set_id"] = set_id
    return jsonify(pub)


@api_bp.route("/wrongbook/answer", methods=["POST"])
def api_wrongbook_answer():
    """重练题集判题：按 set_id 定位重练题集，判分并记录作答"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    set_id = body.get("set_id")
    pid = body.get("problem_id")
    payload = {"main": body.get("main"), "answers": body.get("answers")}
    result = wrongbook_svc.answer_practice(_data_dir(), uid, set_id, pid,
                                           payload)
    if result is None:
        return jsonify({"error": "重练题集不存在或已过期，请重新生成"}), 404
    return jsonify(result)


# ---------- 口算限时挑战 ----------

@api_bp.route("/sprint/specials")
def api_sprint_specials():
    """口算专项列表（按年级过滤，返回各专项题量与限时）"""
    grade = _grade_from(request.args.get("grade"))
    return jsonify({"grade": grade,
                    "specials": sprint_svc.list_specials(grade)})


@api_bp.route("/sprint/start", methods=["POST"])
def api_sprint_start():
    """开启一局限时挑战：服务端生成题集并记录开始时间（对外隐藏答案）"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    grade = _grade_from(body.get("grade"))
    special_id = str(body.get("special_id") or "")
    set_id, dataset = sprint_svc.create_sprint(_data_dir(), uid, grade,
                                               special_id)
    if dataset is None:
        return jsonify({"error": "专项不存在或不适合当前年级"}), 404
    pub = _public_set(dataset)
    pub["set_id"] = set_id
    return jsonify(pub)


@api_bp.route("/sprint/submit", methods=["POST"])
def api_sprint_submit():
    """限时挑战交卷：服务端校验用时后判分，更新个人最佳并返回逐题详情"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    set_id = body.get("set_id")
    answers = body.get("answers") if isinstance(body.get("answers"), list) \
        else []
    result = sprint_svc.submit_sprint(_data_dir(), uid, set_id, answers)
    if result is None:
        return jsonify({"error": "挑战不存在或已过期"}), 404
    if result.get("error"):
        return jsonify(result), 400
    return jsonify(result)


@api_bp.route("/sprint/best")
def api_sprint_best():
    """各专项个人最佳（答对数优先、用时短优先，跨日期保留）"""
    uid = _user_id_from(request.args.get("user_id"))
    return jsonify({"bests": sprint_svc.load_best(_data_dir(), uid)})


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
    """单次练习详情：逐题题干、我的作答与对错（不含正确答案）
    source=day_record 返回当天首次提交的冻结快照（练习记录详情）；
    默认 current 返回当前题集实时结果（导出页打印/预览）"""
    uid = _user_id_from(request.args.get("user_id"))
    grade = _grade_from(request.args.get("grade"))
    dt = request.args.get("date") or _today()
    source = request.args.get("source", "current").strip()
    detail = daily_set.record_detail(_data_dir(), dt, grade, uid,
                                     source=("day_record"
                                             if source == "day_record"
                                             else "current"))
    if detail is None:
        return jsonify({"error": "题集不存在"}), 404
    return jsonify(detail)


@api_bp.route("/summary")
def api_summary():
    """练习汇总（每日一练页顶部）：总共已练习 / 全对 / 连续全对天数"""
    uid = _user_id_from(request.args.get("user_id"))
    return jsonify(daily_set.practice_summary(_data_dir(), uid))


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
    """设备能力与版本：export=桌面导出库可用；print=安卓系统打印可用；
    version=构建日期（前端页头右上角显示 v+该值）
    （前端据 print 显示「打印 / 保存 PDF」，据 export 显示导出文件按钮）"""
    return jsonify({
        "export": bool(export_pdf.PDF_OK and export_docx.DOCX_OK),
        "print": print_bridge.is_available(),
        "version": version_mod.BUILD_DATE,
    })


@api_bp.route("/print", methods=["POST"])
def api_print():
    """调起安卓系统打印：前端先备好打印视图（无答案练习卷），再调本端点
    用 WebView 打印框架把当前页面交给系统打印（对话框内可选"另存为 PDF"）"""
    body = request.get_json(force=True, silent=True) or {}
    job = str(body.get("job_name") or "数学练习").strip()[:40] or "数学练习"
    ok, err = print_bridge.trigger_print(job)
    if not ok:
        return jsonify({"error": "打印调起失败：" + err}), 503
    return jsonify({"ok": True})


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


@api_bp.route("/hint")
def api_hint():
    """难度自适应建议：基于近期正确率与薄弱知识点的规则引擎"""
    uid = _user_id_from(request.args.get("user_id"))
    grade = request.args.get("grade")
    try:
        grade = _grade_from(grade, default=None)
    except Exception:
        grade = None
    return jsonify(stats.difficulty_hint(_data_dir(), uid, grade))


@api_bp.route("/achievements")
def api_achievements():
    """成就徽章列表（复用现有统计实时判定，无落盘存储）"""
    uid = _user_id_from(request.args.get("user_id"))
    return jsonify(achievements_svc.list_achievements(_data_dir(), uid))


@api_bp.route("/heartbeat", methods=["POST"])
def api_heartbeat():
    """页面存活心跳：前端定时上报，页面全部关闭后服务自动退出"""
    heartbeat.record()
    return jsonify({"ok": True})


# ---------- 每周一题（小学思维拓展 / 初中压轴专项，按年级切题库） ----------

def _finale_grade(value):
    """年级参数：缺省/非法 → None（按初中题库处理）"""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return None
    return v if 1 <= v <= 9 else None


@api_bp.route("/finale/current")
def api_finale_current():
    """当前应推送的每周一题：status=active|completed|upcoming|empty
    force=1 未到推送日（周六）时允许提前查看本周题"""
    uid = _user_id_from(request.args.get("user_id"))
    force = request.args.get("force") in ("1", "true", "yes")
    grade = _finale_grade(request.args.get("grade"))
    return jsonify(finale_svc.get_current(_data_dir(), uid, force=force,
                                          grade=grade))


@api_bp.route("/finale/assess", methods=["POST"])
def api_finale_assess():
    """自评三态：done=做出来了 / hint=看了提示做出来 / fail=没做出来"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    qid = (body.get("qid") or "").strip()
    result = (body.get("result") or "").strip()
    grade = _finale_grade(body.get("grade"))
    ok, err = finale_svc.assess(_data_dir(), uid, qid, result, grade=grade)
    if not ok:
        return jsonify({"error": err}), 400
    return jsonify({"ok": True})


@api_bp.route("/finale/history")
def api_finale_history():
    """每周一题完成记录（含自评结果）"""
    uid = _user_id_from(request.args.get("user_id"))
    grade = _finale_grade(request.args.get("grade"))
    return jsonify(finale_svc.list_history(_data_dir(), uid, grade=grade))


@api_bp.route("/finale/fig/<name>")
def api_finale_fig(name):
    """压轴题 SVG 示意图（只读，仅允许 finale_figs/ 下真实存在的文件名）"""
    path = finale_svc.fig_path(_data_dir(), name)
    if path is None:
        return jsonify({"error": "配图不存在"}), 404
    return send_file(path, mimetype="image/svg+xml")


# ---------- 真题试卷（四川各地小学 1-6 年级） ----------

@api_bp.route("/papers/list")
def api_papers_list():
    """真题卷列表（不含题目内容），按年级筛选（缺省=全部年级），附当前用户完成状态"""
    uid = _user_id_from(request.args.get("user_id"))
    grade = _grade_or_all(request.args.get("grade"))
    items = []
    for p in papers_svc.load_bank(_data_dir()):
        if grade and p.get("grade") != grade:
            continue
        items.append(papers_svc.paper_meta(p))
    return jsonify({
        "items": items,
        "done": papers_svc.list_done(_data_dir(), uid),
    })


@api_bp.route("/papers/load")
def api_papers_load():
    """试卷内容（客观题隐藏标准答案），附该用户已提交的答卷用于恢复"""
    uid = _user_id_from(request.args.get("user_id"))
    paper_id = (request.args.get("id") or "").strip()
    paper = papers_svc.find_paper(_data_dir(), paper_id)
    if paper is None:
        return jsonify({"error": "试卷不存在"}), 404
    public = papers_svc.paper_meta(paper)
    public["questions"] = [papers_svc.question_public(q)
                           for q in paper.get("questions", [])]
    public["record"] = papers_svc.get_answers_state(_data_dir(), uid, paper_id)
    return jsonify(public)


@api_bp.route("/papers/submit", methods=["POST"])
def api_papers_submit():
    """提交整卷：客观题自动判分，解答题自评三态，合计得分并存档"""
    body = request.get_json(force=True, silent=True) or {}
    uid = _user_id_from(body.get("user_id"))
    paper_id = (body.get("id") or "").strip()
    result, err = papers_svc.submit(_data_dir(), uid, paper_id,
                                    body.get("answers"),
                                    body.get("self_assess"))
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@api_bp.route("/papers/export/pdf")
def api_papers_export_pdf():
    """整卷导出 PDF（可选附参考答案页）；安卓端未打包 reportlab 返回友好提示"""
    if not export_pdf.PDF_OK:
        return jsonify({"error": "本设备暂不支持导出 PDF，请在电脑端使用导出功能"}), 503
    paper_id = (request.args.get("id") or "").strip()
    with_answers = request.args.get("with_answers", "0") in ("1", "true", "yes")
    paper = papers_svc.find_paper(_data_dir(), paper_id)
    if paper is None:
        return jsonify({"error": "试卷不存在"}), 404
    buf, filename = export_pdf.export_paper_pdf(paper, with_answers)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                     download_name=filename)
