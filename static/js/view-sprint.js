/* 口算挑战页逻辑（依赖 app.js 全局工具：$, fetchJSON, escapeHtml, appAlert,
   openSubmitModal, GRADE_NAMES, state）
   数据接口：/api/sprint/specials、/api/sprint/start、/api/sprint/submit、
             /api/sprint/best */

var sp = {
  specials: [],   // 当前年级可参与的专项列表
  bests: {},      // 个人最佳：special_id -> {correct,total,elapsed,date}
  set: null,      // 进行中的挑战题集（服务端题集的公开版）
  problems: [],   // 当前题目数组（便于收集作答）
  deadline: 0,    // 倒计时截止时间戳（ms）
  timer: null,    // 倒计时句柄
  submitting: false,
  phase: 'pick',  // pick=选择专项 / run=作答中 / result=结算页
  lastSpecial: null  // 结算页"再来一局"用的专项 id
};

var SP_RING_LEN = 2 * Math.PI * 16;  // 倒计时环周长（r=16）

/* ---------- 专项选择 ---------- */

function loadSprint() {
  // 作答中切走再切回：保持进行中的挑战不被打断
  if (sp.phase === 'run' && sp.set) return;
  var gradeText = $('sp-grade-text');
  if (gradeText) {
    gradeText.textContent = GRADE_NAMES[state.grade] || (state.grade + ' 年级');
  }
  Promise.all([
    fetchJSON('/api/sprint/specials?grade=' + state.grade),
    fetchJSON('/api/sprint/best?user_id=' + encodeURIComponent(state.user))
  ]).then(function (arr) {
    sp.specials = (arr[0] && arr[0].specials) || [];
    sp.bests = (arr[1] && arr[1].bests) || {};
    if (sp.phase !== 'pick') return;  // 期间已开局则不覆盖界面
    renderSpSpecials();
  }).catch(function () {
    var box = $('sp-special-list');
    if (box) box.innerHTML = '<p class="tip">加载失败，请点击"刷新"重试</p>';
  });
}

function spFormatSec(s) {
  s = Math.max(0, Math.round(s));
  var m = Math.floor(s / 60);
  return m + ':' + ('0' + (s % 60)).slice(-2);
}

function renderSpSpecials() {
  var box = $('sp-special-list');
  if (!box) return;
  if (!sp.specials.length) {
    box.innerHTML = '<p class="tip">当前年级暂无口算专项（口算专项覆盖 1-6 年级）</p>';
    return;
  }
  box.innerHTML = sp.specials.map(function (s, idx) {
    var best = sp.bests[s.id];
    var bestHtml = best
      ? '<div class="sp-best">个人最佳：答对 <b>' + best.correct + '</b>/' +
        best.total + ' · 用时 ' + spFormatSec(best.elapsed) + ' · ' +
        escapeHtml(best.date) + '</div>'
      : '<div class="sp-best sp-none">尚未挑战</div>';
    return '<div class="sp-card" data-sp-idx="' + idx + '">' +
      '<h3>' + escapeHtml(s.name) + '</h3>' +
      '<div class="sp-meta">' + s.count + ' 题 · 限时 ' +
      spFormatSec(s.seconds) + '</div>' + bestHtml + '</div>';
  }).join('');
  box.querySelectorAll('.sp-card').forEach(function (card) {
    card.addEventListener('click', function () {
      var s = sp.specials[parseInt(card.getAttribute('data-sp-idx'), 10)];
      if (s) spStart(s.id);
    });
  });
}

function spStart(specialId) {
  sp.lastSpecial = specialId;
  fetchJSON('/api/sprint/start', {
    method: 'POST',
    body: JSON.stringify({ user_id: state.user, grade: state.grade,
                           special_id: specialId })
  }).then(function (d) {
    if (d.error) { appAlert(d.error); return; }
    sp.set = d;
    sp.problems = d.problems || [];
    sp.phase = 'run';
    sp.submitting = false;
    $('sp-pick-box').classList.add('hidden');
    $('sp-result-box').classList.add('hidden');
    $('sp-run-box').classList.remove('hidden');
    $('sp-run-title').textContent = d.special_name || '口算挑战';
    $('sp-run-sub').textContent = d.count + ' 题 · 限时 ' +
      spFormatSec(d.seconds);
    renderSpProblems();
    sp.deadline = Date.now() + (d.seconds || 300) * 1000;
    spTick();
    if (sp.timer) clearInterval(sp.timer);
    sp.timer = setInterval(spTick, 500);
    window.scrollTo(0, 0);
    var first = document.querySelector('#sp-problem-list input');
    if (first) first.focus();
  }).catch(function () { appAlert('开启挑战失败，请重试'); });
}

/* ---------- 作答 ---------- */

function renderSpProblems() {
  var box = $('sp-problem-list');
  if (!box) return;
  box.innerHTML = sp.problems.map(function (p, idx) {
    return '<div class="sp-row">' +
      '<span class="sp-no">' + (idx + 1) + '.</span>' +
      '<span class="sp-question">' + escapeHtml(p.question) + '</span>' +
      '<input type="text" inputmode="decimal" autocomplete="off" ' +
      'id="sp-in-' + p.id + '" data-sp-pid="' + p.id + '">' +
      '</div>';
  }).join('');
  box.querySelectorAll('input').forEach(function (input, i, all) {
    input.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter') {
        ev.preventDefault();
        var next = all[i + 1];
        if (next) next.focus();
      }
    });
    input.addEventListener('input', spUpdateProgress);
  });
  spUpdateProgress();
}

function spUpdateProgress() {
  var done = 0;
  sp.problems.forEach(function (p) {
    var el = $('sp-in-' + p.id);
    if (el && el.value.trim() !== '') done++;
  });
  var fill = $('sp-progress-fill');
  var total = sp.problems.length;
  if (fill) fill.style.width = (total ? Math.round(done * 100 / total) : 0) + '%';
  var text = $('sp-progress-text');
  if (text) text.textContent = '已答 ' + done + '/' + total;
}

function spTick() {
  var remain = Math.max(0, (sp.deadline - Date.now()) / 1000);
  var seconds = (sp.set && sp.set.seconds) || 300;
  var ring = $('sp-ring-fg');
  var text = $('sp-time-text');
  if (text) text.textContent = spFormatSec(Math.ceil(remain));
  if (ring) {
    ring.style.strokeDasharray = SP_RING_LEN;
    ring.style.strokeDashoffset = SP_RING_LEN * (1 - remain / seconds);
    ring.classList.toggle('urgent', remain < 30);
  }
  var timerBox = document.querySelector('.sp-timer');
  if (timerBox) timerBox.classList.toggle('urgent', remain < 30);
  if (remain <= 0) spSubmit(true);
}

function spCollect() {
  return sp.problems.map(function (p) {
    var el = $('sp-in-' + p.id);
    return { problem_id: p.id, main: el ? el.value.trim() : '' };
  });
}

function spSubmit(auto) {
  if (!sp.set || sp.submitting) return;
  sp.submitting = true;
  if (sp.timer) { clearInterval(sp.timer); sp.timer = null; }
  fetchJSON('/api/sprint/submit', {
    method: 'POST',
    body: JSON.stringify({ user_id: state.user, set_id: sp.set.set_id,
                           answers: spCollect() })
  }).then(function (r) {
    sp.submitting = false;
    if (r.error === 'expired') {
      appAlert('已超出限时（含网络延迟宽限），本次成绩不计入，请重新挑战');
      spBack();
      return;
    }
    if (r.error === 'already' && r.result) { spShowResult(r.result); return; }
    if (r.error) { appAlert('提交失败：' + r.error); return; }
    spShowResult(r);
  }).catch(function () {
    // 网络异常：恢复倒计时（差 1 秒内归零则给 5 秒缓冲重试交卷）
    sp.submitting = false;
    var remain = (sp.deadline - Date.now()) / 1000;
    if (remain <= 1) sp.deadline = Date.now() + 5000;
    if (!sp.timer) sp.timer = setInterval(spTick, 500);
    appAlert('网络异常，交卷失败请重试');
  });
}

/* ---------- 结算 ---------- */

function spShowResult(r) {
  sp.phase = 'result';
  sp.set = null;
  if (sp.timer) { clearInterval(sp.timer); sp.timer = null; }
  var score = r.score || {};
  var best = r.best || {};
  var html = '<div class="sp-score-main">' +
    '<div class="sp-score-num"><b>' + (score.correct || 0) + '</b> / ' +
    (score.total || 0) + '</div>' +
    '<div class="sp-score-label">答对题数</div></div>';
  html += '<div class="sp-score-meta">用时 ' +
    spFormatSec(score.elapsed || 0) + ' · ' +
    escapeHtml(score.date || '') + '</div>';
  if (r.record) {
    html += '<div class="sp-record">🎉 打破个人最佳！此前纪录：答对 ' +
      (best.correct || 0) + ' 题</div>';
  }
  if (best && best.correct != null) {
    html += '<div class="sp-best-line">个人最佳：答对 <b>' + best.correct +
      '</b>/' + best.total + ' · 用时 ' + spFormatSec(best.elapsed) + '</div>';
  }
  var wrongs = (r.detail || []).filter(function (d) { return !d.correct; });
  if (wrongs.length) {
    html += '<div class="sp-wrong-head">错题回顾（' + wrongs.length + ' 题）</div>';
    html += '<div class="sp-wrongs">' + wrongs.map(function (d) {
      return '<div class="sp-wrong-row"><span class="sp-wrong-q">' +
        escapeHtml(d.question) + '</span>' +
        '<span class="sp-wrong-a">我的答案 ' +
        (d.user_answer ? escapeHtml(d.user_answer) : '（未作答）') +
        ' · 正确 <b>' + escapeHtml(d.answer) + '</b></span></div>';
    }).join('') + '</div>';
  } else {
    html += '<div class="sp-all-ok">全部答对，太棒了！</div>';
  }
  $('sp-result-card').innerHTML = html;
  $('sp-result-detail').classList.add('hidden');  // 错题已并入结算卡
  $('sp-pick-box').classList.add('hidden');
  $('sp-run-box').classList.add('hidden');
  $('sp-result-box').classList.remove('hidden');
  window.scrollTo(0, 0);
}

function spBack() {
  sp.set = null;
  sp.problems = [];
  sp.phase = 'pick';
  if (sp.timer) { clearInterval(sp.timer); sp.timer = null; }
  $('sp-run-box').classList.add('hidden');
  $('sp-result-box').classList.add('hidden');
  $('sp-pick-box').classList.remove('hidden');
  loadSprint();
}

/* ---------- 页内初始化 ---------- */

function spInit() {
  $('btn-sp-refresh').addEventListener('click', function () {
    sp.phase = 'pick';
    loadSprint();
  });
  $('btn-sp-submit').addEventListener('click', function () { spSubmit(false); });
  $('btn-sp-quit').addEventListener('click', function () {
    openSubmitModal('放弃挑战', '<p>确定放弃本次挑战吗？放弃后成绩不计入。</p>', [
      { text: '继续作答', fn: null },
      { text: '放弃', cls: 'danger', fn: spBack }
    ]);
  });
  $('btn-sp-again').addEventListener('click', function () {
    if (sp.lastSpecial) spStart(sp.lastSpecial);
    else spBack();
  });
  $('btn-sp-back').addEventListener('click', spBack);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', spInit);
} else {
  spInit();
}
