'use strict';
/* mathPractice_tool 前端逻辑：单页多视图（做题 / 练习记录 / 学情 / 导出 / 设置） */

var GRADE_NAMES = { 1: '一年级', 2: '二年级', 3: '三年级', 4: '四年级',
                    5: '五年级', 6: '六年级', 7: '七年级', 8: '八年级', 9: '九年级' };

var TYPE_NAMES = { calc: '计算题', vertical: '竖式计算',
                   equation: '解方程', word: '应用题' };

var VIEWS = ['practice', 'records', 'stats', 'export', 'settings', 'users'];

/* 学期名称（侧边栏全局学期选择器，做题 / 生成导出共用） */
var SEMESTER_NAMES = { '0': '自动（按学期）', '1': '上册', '2': '下册' };

var state = {
  grade: 3,
  date: todayStr(),
  set: null,
  user: localStorage.getItem('mpt_user') || 'default',
  users: [],
  /* 学期：0=自动（按日期），1=上册，2=下册（题库抽题册别） */
  semester: localStorage.getItem('mpt_semester') || '0',
  /* 题库类别：0=易错题+常见题，1=易错题，2=常见题（题库抽题类别） */
  kind: localStorage.getItem('mpt_bank_kind') || '0'
};

/* ---------- 工具 ---------- */

function $(id) { return document.getElementById(id); }

function todayStr() {
  var d = new Date();
  var m = ('0' + (d.getMonth() + 1)).slice(-2);
  var day = ('0' + d.getDate()).slice(-2);
  return d.getFullYear() + '-' + m + '-' + day;
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fetchJSON(url, opts) {
  opts = opts || {};
  opts.headers = opts.headers || { 'Content-Type': 'application/json' };
  return fetch(url, opts).then(function (r) { return r.json(); });
}

/* ---------- 通用分页（前端切片，各列表共用） ---------- */

var PAGERS = {};  // key -> { page, size, items, render }

function pagerItems(key) {
  var p = PAGERS[key];
  var pages = Math.max(1, Math.ceil(p.items.length / p.size));
  if (p.page > pages) p.page = pages;  // 删除/筛选后页码越界时回退
  if (p.page < 1) p.page = 1;
  var start = (p.page - 1) * p.size;
  return p.items.slice(start, start + p.size);
}

/* 页码条：上一页 / 页码（当前页前后各 2 页）/ 下一页 / 总数 */
function pagerHtml(key) {
  var p = PAGERS[key];
  var total = p.items.length;
  var pages = Math.max(1, Math.ceil(total / p.size));
  if (pages <= 1) return '';
  var html = '<div class="pager">';
  html += '<button class="btn btn-sm pager-btn" data-pkey="' + key +
    '" data-page="' + (p.page - 1) + '"' +
    (p.page <= 1 ? ' disabled' : '') + '>上一页</button>';
  var start = Math.max(1, p.page - 2);
  var end = Math.min(pages, start + 4);
  if (start > 1) {
    html += '<button class="btn btn-sm pager-btn" data-pkey="' + key +
      '" data-page="1">1</button><span class="pager-ellipsis">…</span>';
  }
  for (var i = start; i <= end; i++) {
    html += '<button class="btn btn-sm pager-btn' + (i === p.page ? ' primary' : '') +
      '" data-pkey="' + key + '" data-page="' + i + '">' + i + '</button>';
  }
  if (end < pages) {
    html += '<span class="pager-ellipsis">…</span><button class="btn btn-sm pager-btn" data-pkey="' +
      key + '" data-page="' + pages + '">' + pages + '</button>';
  }
  html += '<button class="btn btn-sm pager-btn" data-pkey="' + key +
    '" data-page="' + (p.page + 1) + '"' +
    (p.page >= pages ? ' disabled' : '') + '>下一页</button>';
  html += '<span class="pager-info">共 ' + total + ' 条</span></div>';
  return html;
}

function bindPagerEvents(box) {
  box.querySelectorAll('.pager-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.disabled) return;
      var key = btn.getAttribute('data-pkey');
      PAGERS[key].page = parseInt(btn.getAttribute('data-page'), 10);
      PAGERS[key].render();
    });
  });
}

/* ---------- 视图路由 ---------- */

function route() {
  var hash = (location.hash || '#/practice').replace('#/', '');
  var target = VIEWS.indexOf(hash) >= 0 ? hash : 'practice';
  VIEWS.forEach(function (v) {
    $('view-' + v).classList.toggle('hidden', v !== target);
  });
  var links = document.querySelectorAll('.nav-item');
  links.forEach(function (a) {
    a.classList.toggle('active', a.getAttribute('data-view') === target);
  });
  if (target === 'records') loadRecords();
  if (target === 'stats') loadStats();
}

/* ---------- 做题页 ---------- */

/* ---------- 教材单元出题范围（设置页，按用户×册别记忆） ---------- */

var _unitNames = [];   // 当前册的单元名列表（/api/units 返回）
var _unitSel = [];     // 当前勾选的单元名（默认全选）

/* 当前册别：学期=上/下册时用所选册；"自动"时按日期判断（与服务端规则一致） */
function currentVolume() {
  var s = parseInt(state.semester, 10) || 0;
  if (s === 1 || s === 2) return s;
  var m = new Date().getMonth() + 1;
  return (m >= 9 || m === 1) ? 1 : 2;
}

/* 单元勾选的 localStorage 键：按用户 × 年级 × 册别分别记忆 */
function unitKey() {
  return 'mpt_units_' + state.user + '_G' + state.grade + 'V' + currentVolume();
}

function isAllUnits() {
  return _unitNames.length > 0 && _unitSel.length === _unitNames.length;
}

/* 全选（或全选外的一部分）才作为过滤参数下发；空/全选 = 不限制 */
function unitPayload() {
  if (!_unitNames.length || !_unitSel.length || isAllUnits()) return '';
  return JSON.stringify(_unitSel);
}

function updateUnitCount() {
  var c = $('unit-count-text');
  if (!c) return;
  if (!_unitNames.length) { c.textContent = ''; return; }
  if (!_unitSel.length) {
    c.textContent = '未勾选单元（等同不限制范围）';
  } else if (isAllUnits()) {
    c.textContent = '已选全部 ' + _unitNames.length + ' 个单元（不限范围）';
  } else {
    c.textContent = '已选 ' + _unitSel.length + '/' + _unitNames.length + ' 个单元';
  }
}

function saveUnitSelection() {
  if (!_unitNames.length) return;
  if (_unitSel.length === _unitNames.length) {
    localStorage.removeItem(unitKey());  // 全选 = 默认态，不存
  } else {
    localStorage.setItem(unitKey(), JSON.stringify(_unitSel));
  }
  updateUnitCount();
}

function renderUnitList() {
  var box = $('unit-list');
  if (!box) return;
  if (!_unitNames.length) {
    box.innerHTML = '<p class="tip">该年级暂无教材单元数据（不做单元限制）。</p>';
    updateUnitCount();
    return;
  }
  box.innerHTML = _unitNames.map(function (n) {
    var checked = _unitSel.indexOf(n) >= 0 ? ' checked' : '';
    return '<label class="unit-item"><input type="checkbox" data-unit="' +
      escapeHtml(n) + '"' + checked + '>' + escapeHtml(n) + '</label>';
  }).join('');
  box.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
    cb.addEventListener('change', function () {
      var n = cb.getAttribute('data-unit');
      if (cb.checked) {
        if (_unitSel.indexOf(n) < 0) _unitSel.push(n);
      } else {
        _unitSel = _unitSel.filter(function (x) { return x !== n; });
      }
      saveUnitSelection();
      updateExportLinks();
    });
  });
  updateUnitCount();
}

/* 拉取当前年级×册别的单元列表并恢复该用户勾选；做题/导出前都会先调用，
   保证 units 参数始终与侧边栏的年级、学期一致 */
function loadUnitOptions() {
  var box = $('unit-list');
  if (!box) return Promise.resolve();
  return fetchJSON('/api/units?grade=' + state.grade +
      '&semester=' + (state.semester || '0'))
    .then(function (d) {
      _unitNames = d.units || [];
      var scope = $('unit-scope-text');
      if (scope) {
        scope.textContent = (GRADE_NAMES[state.grade] || state.grade + '年级') +
          (d.volume === 1 ? '上册' : '下册');
      }
      var saved = null;
      try {
        saved = JSON.parse(localStorage.getItem(unitKey()) || 'null');
      } catch (e) { saved = null; }
      if (!Array.isArray(saved)) {
        _unitSel = _unitNames.slice();  // 默认全选（不限制）
      } else {
        _unitSel = saved.filter(function (n) { return _unitNames.indexOf(n) >= 0; });
      }
      renderUnitList();
      updateExportLinks();
    })
    .catch(function () {
      _unitNames = [];
      _unitSel = [];
    });
}

function setAllUnits(all) {
  if (!_unitNames.length) return;
  _unitSel = all ? _unitNames.slice() : [];
  saveUnitSelection();
  renderUnitList();
  updateExportLinks();
}

function loadDaily() {
  var grade = parseInt($('grade-select').value, 10) || 3;
  var date = $('date-input').value || todayStr();
  var semester = parseInt($('semester-select').value, 10) || 0;
  state.grade = grade;
  state.date = date;
  state.semester = semester;
  var kind = $('kind-select').value || '0';
  state.kind = kind;
  // 先刷新单元勾选（跟随年级×学期），再带 units 参数取题
  loadUnitOptions().then(function () {
    var url = '/api/daily?grade=' + grade + '&date=' + date +
      '&semester=' + semester +
      '&kind=' + encodeURIComponent(kind) +
      '&user_id=' + encodeURIComponent(state.user);
    var units = unitPayload();
    if (units) url += '&units=' + encodeURIComponent(units);
    fetchJSON(url).then(function (data) {
      state.set = data;
      renderProblems();
    });
  });
}

function regenerate() {
  if (!confirm('重新生成将删除该日期的题集和作答记录，确定吗？')) return;
  fetchJSON('/api/regenerate', {
    method: 'POST',
    body: JSON.stringify({
      grade: state.grade, date: state.date,
      semester: parseInt(state.semester, 10) || 0,
      kind: state.kind || '0',
      units: unitPayload(),
      user_id: state.user
    })
  }).then(function (data) {
    state.set = data;
    renderProblems();
  });
}

function typeLabel(p) {
  if (p.type === 'calc') return '计';
  if (p.type === 'vertical') return '竖';
  if (p.type === 'equation') return '方';
  return '应';
}

function attemptOf(p) {
  var att = (state.set && state.set.attempts) || {};
  return att[p.id] || null;
}

function renderProblems() {
  var box = $('problem-list');
  box.innerHTML = '';
  renderFocusTip();
  if (!state.set) return;
  state.set.problems.forEach(function (p, idx) {
    box.appendChild(buildCard(p, idx));
  });
  updateProgress();
}

function renderFocusTip() {
  var ft = $('focus-tip');
  if (!ft) return;
  var fc = (state.set && state.set.focus_categories) || [];
  if (fc.length) {
    ft.textContent = '🎯 本套练习侧重薄弱知识点：' + fc.join('、');
    ft.classList.remove('hidden');
  } else {
    ft.classList.add('hidden');
  }
}

function buildCard(p, idx) {
  var att = attemptOf(p);
  var card = document.createElement('div');
  card.className = 'card problem-card';
  card.innerHTML = cardHtml(p, idx, att);
  return card;
}

function cardHtml(p, idx, att) {
  var html = '';
  var noteHtml = p.note ? '<span class="note">' + escapeHtml(p.note) + '</span>' : '';
  var statusHtml = '';
  if (att) {
    statusHtml = att.result && att.result.correct
      ? '<span class="problem-status" style="color:var(--success)">✔</span>'
      : '<span class="problem-status" style="color:var(--danger)">✘</span>';
  }
  var catHtml = p.category
    ? '<span class="cat-tag">' + escapeHtml(p.category) + '</span>'
    : '';
  html += '<div class="problem-head">' +
    '<span class="problem-id">' + typeLabel(p) + '</span>' +
    '<span class="problem-question">' + (idx + 1) + '. ' + escapeHtml(p.question) + noteHtml + '</span>' +
    catHtml + statusHtml + '</div>';

  if (p.type === 'vertical') {
    html += '<div class="vertical-pad"></div>';
  }

  if (p.type === 'word') {
    html += wordBodyHtml(p, att);
  } else if (p.type === 'equation') {
    html += equationBodyHtml(p, att);
  } else {
    html += calcBodyHtml(p, att);
  }

  if (att) html += feedbackHtml(p, att);
  return html;
}

function calcBodyHtml(p, att) {
  var val = att && att.payload ? (att.payload.main || '') : '';
  return '<div class="answer-row">' +
    '<label>答案 <input type="text" class="answer-input" id="input-' + p.id + '" ' +
    'inputmode="decimal" autocomplete="off" value="' + escapeHtml(val) + '"></label></div>';
}

function equationBodyHtml(p, att) {
  var vars = p.answer_vars || ['x'];
  var main = (att && att.payload && att.payload.main) || {};
  var html = '<div class="answer-row">';
  vars.forEach(function (v) {
    html += '<label>' + escapeHtml(v) + ' = ' +
      '<input type="text" class="answer-input" id="input-' + p.id + '-' + v + '" ' +
      'inputmode="decimal" autocomplete="off" value="' + escapeHtml(main[v] || '') + '"></label>';
  });
  html += '</div>';
  return html;
}

function wordBodyHtml(p, att) {
  var labels = p.answer_labels || [];
  var answers = (att && att.payload && att.payload.answers) || [];
  var results = (att && att.result && att.result.answer_results) || null;
  var html = '<div class="steps">';
  labels.forEach(function (label, i) {
    var resHtml = '';
    if (results && results[i]) {
      resHtml = results[i].correct
        ? '<span class="step-result ok">✔</span>'
        : '<span class="step-result wrong">✘</span>';
    }
    html += '<div class="step-row">' +
      '<span class="step-hint">' + escapeHtml(label) + '</span>' +
      '<input type="text" class="answer-input" id="ans-' + p.id + '-' + i + '" ' +
      'inputmode="decimal" autocomplete="off" value="' + escapeHtml(answers[i] || '') + '">' +
      resHtml + '</div>';
  });
  html += '</div>';
  return html;
}

function feedbackHtml(p, att) {
  var r = att && att.result;
  if (!r) return '';
  var html = '';
  if (r.correct) {
    html += '<div class="result-box ok">回答正确！</div>';
  } else {
    // 计算题/竖式/解方程：只提示对错，不直接显示答案
    html += '<div class="result-box wrong">回答错误，再试一次！</div>';
  }
  // 应用题：提交后在解析区展示完整答案、分步解答与思路
  if (p.type === 'word') {
    html += '<div class="solution-box">';
    if (r.answer_display) {
      html += '<h4>答案</h4><p>' + escapeHtml(r.answer_display) + '</p>';
    }
    if (r.steps && r.steps.length) {
      html += '<h4>分步解答</h4>';
      r.steps.forEach(function (s, i) {
        html += '<p>' + (i + 1) + '. ' + escapeHtml(s.hint) +
          '　<b>' + escapeHtml(s.answer) + '</b></p>';
      });
    }
    if (r.solution && r.solution.length) {
      html += '<h4>解题思路</h4>';
      r.solution.forEach(function (line) {
        html += '<p>' + escapeHtml(line) + '</p>';
      });
    }
    html += '</div>';
  }
  return html;
}

/* ---------- 统一提交（右上角一次提交全部题目） ---------- */

// 结果鼓励语：全对赞赏 / 错 1 题惋惜 / 错 2 题及以上加油，各 20 条随机取用
var PRAISE_MSGS = [
  '太棒了！全部正确，你就是数学小达人！',
  '满分！你的脑子转得又快又准！',
  '全对！今天的你闪闪发光！',
  '了不起！每一题都难不倒你！',
  '完美满分！继续保持，你是最棒的！',
  '全部答对，老师都要为你鼓掌啦！',
  '真厉害！数学王国的勇士就是你！',
  '满分达成！你的努力都有了回报！',
  '全对！你算得又快又稳，太厉害了！',
  '一次全对，你真是个数学小天才！',
  '漂亮！这套题完全被你征服了！',
  '满分！给你一个大大的赞！',
  '全对！再难的题也挡不住你！',
  '太厉害了，正确率百分之百！',
  '满分！今天的练习完成得非常出色！',
  '全部正确！你的计算功力越来越强了！',
  '全对！坚持这样练，你会越来越优秀！',
  '棒极了！每一题都答得又对又好！',
  '满分！给自己一点掌声吧！',
  '全对！你就是数学课上最亮的星！',
  '太完美了！一题没错，厉害厉害！',
  '全对！今天的你就像开了挂一样！',
  '满分答卷！继续保持这个状态！',
  '全对无误！你的细心和努力都体现在卷面上了！',
  '太出色了！每道题都答得干脆利落！',
  '全对！这就是实力，没有任何侥幸！',
  '了不起！满分就是对你最好的奖励！',
  '全对！数学小博士非你莫属！',
  '满分！你今天的状态简直好到爆棚！',
  '全对无误，稳如泰山，太棒了！',
  '厉害了！这套题在你面前不堪一击！',
  '全对！你用实力证明了勤奋的力量！',
  '满分达成！继续加油，未来可期！',
  '全对！你的大脑今天特别灵光！',
  '太棒了！每一题都答得又准又稳！',
  '满分！你就是同学们学习的榜样！',
  '全对！坚持每天练习，你越来越强了！',
  '完美！这样的成绩值得好好骄傲一下！',
  '全对！数字在你手里特别听话！',
  '满分！今天又是元气满满的一天！',
  '全对无误！你的计算速度和准确度都一流！',
  '太厉害了，一分不差全对！',
  '全对！做题如行云流水，漂亮！',
  '全对！你的努力今天全部兑现了！',
  '满分！这种扎实的感觉真好！',
  '全对！你就是行走的数学小百科！',
  '太棒了！零失误完成今天的挑战！',
  '满分！正确率和速度的双料冠军！',
  '全对！继续保持，胜利属于坚持的人！',
  '满分收官！今天的练习完成得漂亮极了！'
];
var REGRET_MSGS = [
  '只错了一题，真的好可惜，再细心一点就满分啦！',
  '差一点点就全对了，可惜呀，下次一定行！',
  '哎呀，就错这一道，太可惜了，真为你惋惜！',
  '只差一步就满分了，别灰心，你已经很棒了！',
  '就错了一小题，可惜了！检查一下错在哪里吧。',
  '好可惜！离满分只差这一道题的距离。',
  '只错一道题，说明你基本都掌握了，下次冲满分！',
  '可惜啦！如果再检查一遍，这道题一定能做对。',
  '错一题不是坏事，弄懂它你就更强了！',
  '好遗憾呀，就差这一题就全对了！',
  '惋惜！这道题跟你开了个小玩笑，找出原因吧。',
  '只差一题就完美了，有点小可惜哦。',
  '可惜了！你的实力远不止错这一题。',
  '就这一题和你捉迷藏，找到它下次就全对了。',
  '真可惜！其他题都对得特别漂亮。',
  '差一点满分，可惜呀，但这个成绩已经很好了！',
  '只错一题，稳住心态，满分就在下一次！',
  '可惜！粗心小怪兽就打败了你一次。',
  '一道题的遗憾，预示着下一次的满分！',
  '别惋惜太久，搞懂这道题，你就是满分选手！',
  '好可惜！就这一道题挡住了满分之路。',
  '惋惜！不过你离满分真的只差一点点了。',
  '只错一题，说明你很扎实，继续加油！',
  '可惜呀！下次做完记得再检查一遍哦。',
  '好遗憾！就差这一题就能全部答对了。',
  '只错一道，你的水平远比这个成绩高！',
  '惋惜！不过错一题也是进步的机会哦。',
  '可惜了！这道题一定是和你闹别扭了。',
  '就差一点点，真替你感到可惜！',
  '只错一题已经很棒了，下次冲满分！',
  '好可惜！相信你下次一定能全对！',
  '惋惜！不过这样的正确率已经很不错啦。',
  '哎呀，就这一题，可惜可惜！',
  '离满分只有一步之遥，惋惜但不气馁！',
  '只错一题，说明你离完美只差一个习惯。',
  '可惜！不过你已经战胜了绝大多数题目！',
  '好遗憾呀！下次细心一点，满分属于你！',
  '惋惜！把这道题弄懂，你就无敌了。',
  '就错这一题，其他题都答得特别漂亮！',
  '可惜啦！你的实力完全可以做到全对。',
  '只差一题，惋惜之余更要为自己点赞！',
  '好可惜！离满分就差这么一小步。',
  '惋惜！不过失误也是成长路上的小插曲。',
  '就一题之差，下次一定让满分属于你！',
  '可惜呀！相信下一次你不会再给粗心机会了。',
  '只错一道题，整体表现值得表扬！',
  '好遗憾！这道题就当给你提个醒吧。',
  '惋惜！不过你的进步大家都看得见！',
  '差一题满分，已经很优秀了，继续加油！',
  '可惜！只让一道题偷走了你的满分。'
];
var EFFORT_MSGS = [
  '错得有点多，别气馁，还需更加努力练习哦！',
  '这次不太理想，认真订正，继续努力！',
  '错误比较多，把每道错题弄懂，再战一次！',
  '还需加油！多做几遍同类题，你会进步的。',
  '别灰心，错题是最好的老师，逐个击破吧！',
  '今天的正确率不理想，明天继续努力！',
  '基础还要打牢，慢慢来，坚持就是胜利！',
  '错题不可怕，可怕的是不改，加油订正吧！',
  '这道坎有点高，但一步一步爬，一定过得去！',
  '还需要更加努力哦，相信下次会更好！',
  '正确率偏低，把薄弱的知识点多练几遍吧。',
  '别着急，学习就像爬山，坚持就会到山顶！',
  '这次没做好，认真总结，下次一定进步！',
  '多做多练，错题重做一遍，你会越来越强的！',
  '失败是成功之母，从错题里吸取经验吧！',
  '加油！每天进步一点点，积少成多！',
  '练习还不够扎实，再接再厉，别放弃！',
  '正确率有待提高，先把错题搞懂最重要。',
  '不经历错误，怎么能变强？继续努力吧！',
  '今天的挫折是明天的垫脚石，加油向前冲！',
  '错误多了点，但每次订正都是一次进步！',
  '还需更加努力！把不会的知识点逐个攻克！',
  '别灰心，多做几遍错题，你一定会进步！',
  '这次成绩不理想，找到原因才是关键！',
  '加油！正确率会随着练习慢慢提升的！',
  '错题就是你的宝藏，好好挖掘它们吧！',
  '还需努力！每天一点点，滴水也能穿石！',
  '别泄气，学习本来就是一个爬坡的过程！',
  '正确率还不够，先从最基础的题型练起吧！',
  '还需更加努力哦，笨鸟先飞也能成功！',
  '别怕出错，敢于练习就是好的开始！',
  '这次没发挥好，总结经验下次逆袭！',
  '还需要再努力一把，别让题目难倒你！',
  '正确率偏低，建议把错题抄下来重做一遍！',
  '加油！每一个数学高手都是从错题堆里走出来的！',
  '还需努力！今天多练一分钟，明天多一分从容！',
  '别气馁，把每个错题弄明白就是最大的收获！',
  '练习还需要加把劲，相信你能做到！',
  '正确率有待提升，稳扎稳打才能走得更远！',
  '别灰心！把基础打牢，正确率自然会提高！',
  '还需更加努力！动动脑筋，题目并不可怕！',
  '这次错了没关系，关键是弄懂为什么错！',
  '加油！多练几遍同样的题型，你会越做越顺！',
  '还需努力哦！坚持订正错题，你会看到进步！',
  '别放弃！每一次练习都在悄悄地让你变强！',
  '正确率不高，先从计算细心这个习惯开始吧！',
  '还需更加努力！你的潜力还没有发挥出来呢！',
  '别气馁！学习如逆水行舟，坚持就是胜利！',
  '加油！相信下一次练习，你会交出更好的答卷！',
  '还需努力！把今天的错题变成明天的得分点！'
];

function buildPayload(p) {
  var payload = { problem_id: p.id, grade: state.grade, date: state.date, user_id: state.user };
  if (p.type === 'word') {
    payload.answers = (p.answer_labels || []).map(function (label, i) {
      var el = $('ans-' + p.id + '-' + i);
      return el ? el.value : '';
    });
  } else if (p.type === 'equation') {
    var main = {};
    (p.answer_vars || ['x']).forEach(function (v) {
      var el = $('input-' + p.id + '-' + v);
      main[v] = el ? el.value : '';
    });
    payload.main = main;
  } else {
    var el = $('input-' + p.id);
    payload.main = el ? el.value : '';
  }
  return payload;
}

// 判断一道题的作答情况：'done' 全部填写 / 'partial' 部分填写 / 'empty' 全空
function answerState(p, payload) {
  var vals = [];
  if (p.type === 'word') {
    vals = payload.answers || [];
  } else if (p.type === 'equation') {
    var main = payload.main || {};
    (p.answer_vars || ['x']).forEach(function (v) { vals.push(main[v]); });
  } else {
    vals = [payload.main];
  }
  var filled = 0;
  vals.forEach(function (v) {
    if (v !== undefined && v !== null && String(v).trim() !== '') filled++;
  });
  if (filled === 0) return 'empty';
  return filled === vals.length ? 'done' : 'partial';
}

function openSubmitModal(title, bodyHtml, actions) {
  $('submit-modal-title').textContent = title;
  $('submit-modal-body').innerHTML = bodyHtml;
  var box = $('submit-modal-actions');
  box.innerHTML = '';
  actions.forEach(function (a) {
    var b = document.createElement('button');
    b.className = 'btn ' + (a.cls || '');
    b.textContent = a.text;
    b.addEventListener('click', function () {
      $('submit-modal').classList.add('hidden');
      if (a.fn) a.fn();
    });
    box.appendChild(b);
  });
  $('submit-modal').classList.remove('hidden');
}

function submitAll() {
  if (!state.set || !state.set.problems || !state.set.problems.length) return;
  var problems = state.set.problems;
  var attempts = state.set.attempts || {};
  var unanswered = [];   // 完全没做
  var partial = [];      // 做了一部分
  var pending = [];      // 待提交的题（含未做的，按空答案提交判错）
  problems.forEach(function (p, idx) {
    if (attempts[p.id] && attempts[p.id].result) return;  // 已提交过的不再重复提交
    var payload = buildPayload(p);
    var st = answerState(p, payload);
    if (st === 'empty') unanswered.push(idx + 1);
    if (st === 'partial') partial.push(idx + 1);
    pending.push({ p: p, payload: payload });
  });

  var info = '<p>共 <b>' + problems.length + '</b> 题，本次将提交 <b>' +
    pending.length + '</b> 题。</p>';
  if (unanswered.length) {
    info += '<p class="warn-text">⚠ 还有未作答的题：第 ' +
      unanswered.join('、') + ' 题，未作答将按错误处理。</p>';
  }
  if (partial.length) {
    info += '<p class="warn-text">⚠ 还有未答完的题：第 ' +
      partial.join('、') + ' 题，空着的小问将按错误处理。</p>';
  }
  info += '<p>确定提交吗？</p>';

  openSubmitModal('提交确认', info, [
    { text: '取消', fn: null },
    { text: '确定提交', cls: 'primary', fn: function () { doSubmitAll(pending); } }
  ]);
}

function doSubmitAll(pending) {
  if (!pending.length) { showSubmitResult(); return; }
  var seq = Promise.resolve();
  pending.forEach(function (item) {
    seq = seq.then(function () {
      return fetchJSON('/api/submit', {
        method: 'POST', body: JSON.stringify(item.payload)
      }).then(function (result) {
        if (!state.set.attempts) state.set.attempts = {};
        state.set.attempts[item.p.id] = { payload: item.payload, result: result };
      });
    });
  });
  seq.then(function () {
    renderProblems();
    showSubmitResult();
  }).catch(function () {
    renderProblems();
    openSubmitModal('提交失败', '<p>部分题目提交失败，请检查服务是否正常后重试。</p>',
      [{ text: '好的' }]);
  });
}

function showSubmitResult() {
  var problems = state.set.problems;
  var attempts = state.set.attempts || {};
  var total = 0, wrong = 0;
  problems.forEach(function (p) {
    var att = attempts[p.id];
    if (!att || !att.result) return;
    total++;
    if (!att.result.correct) wrong++;
  });
  if (!total) return;
  var pool;
  if (wrong === 0) {
    pool = PRAISE_MSGS;
  } else if (wrong === 1) {
    pool = REGRET_MSGS;
  } else {
    pool = EFFORT_MSGS;
  }
  var msg = pool[Math.floor(Math.random() * pool.length)];
  var body = '<div class="submit-result">' +
    '<p class="submit-score">答对 <b>' + (total - wrong) + '</b> / ' + total + ' 题</p>' +
    '<p class="submit-msg">' + escapeHtml(msg) + '</p></div>';
  openSubmitModal('练习结果', body, [{ text: '好的', cls: 'primary' }]);
}

function updateProgress() {
  var total = state.set ? state.set.problems.length : 0;
  var attempts = (state.set && state.set.attempts) || {};
  var submitted = 0;
  var correct = 0;
  Object.keys(attempts).forEach(function (k) {
    submitted++;
    if (attempts[k].result && attempts[k].result.correct) correct++;
  });
  var pct = total ? Math.round(submitted / total * 100) : 0;
  $('progress-fill').style.width = pct + '%';
  $('progress-text').textContent = submitted + '/' + total + ' · 正确 ' + correct;
}

/* ---------- 导出页 ---------- */

/* 生成/导出页只读展示年级与学期（跟随侧边栏全局选择，实时更新） */
function updateExportInfo() {
  var g = $('export-grade-text');
  var s = $('export-semester-text');
  if (g) g.textContent = GRADE_NAMES[state.grade] || (state.grade + '年级');
  if (s) s.textContent = SEMESTER_NAMES[state.semester] || '自动（按学期）';
}

function updateExportLinks() {
  var g = state.grade || 3;
  var d = $('export-date').value || todayStr();
  var dTo = $('export-date-to').value || '';
  var a = $('export-answers').checked ? 1 : 0;
  var uid = '&user_id=' + encodeURIComponent(state.user);
  var sem = state.semester || '0';
  // 结束日期晚于起始日期时按多日导出，否则单日
  var range = (dTo && dTo > d) ? '&date_to=' + dTo : '';
  // 单元过滤：仅勾选部分单元时下发（缺失日期按该范围补生成）
  var units = unitPayload();
  var u = units ? '&units=' + encodeURIComponent(units) : '';
  $('link-pdf').href = '/api/export/pdf?grade=' + g + '&date=' + d + range +
    '&semester=' + encodeURIComponent(sem) +
    '&kind=' + encodeURIComponent(state.kind || '0') +
    '&with_answers=' + a + uid + u;
  $('link-docx').href = '/api/export/docx?grade=' + g + '&date=' + d + range +
    '&semester=' + encodeURIComponent(sem) +
    '&kind=' + encodeURIComponent(state.kind || '0') +
    '&with_answers=' + a + uid + u;
}

/* ---------- 导出页：生成列表 / 预览 / 重新生成 ---------- */

function genSetLabel(it) {
  // 形如"二年级上-2026-11-11"
  var gn = GRADE_NAMES[it.grade] || it.grade + '年级';
  return gn + (it.volume === 1 ? '上' : '下') + '-' + it.date;
}

function generateSets() {
  var box = $('gen-list');
  var g = state.grade || 3;
  var d = $('export-date').value || todayStr();
  var dTo = $('export-date-to').value || '';
  var sem = state.semester || '0';
  box.innerHTML = '<p class="tip">生成中…</p>';
  fetchJSON('/api/sets/generate', {
    method: 'POST',
    body: JSON.stringify({
      grade: g, date: d, date_to: dTo, semester: sem,
      kind: state.kind || '0', units: unitPayload(), user_id: state.user,
    }),
  }).then(function (data) {
    if (data.error) { box.innerHTML = ''; alert(data.error); return; }
    if (PAGERS.gen) PAGERS.gen.page = 1;  // 新生成回第一页
    renderGenList(data.items || []);
  });
}

function renderGenList(items) {
  var box = $('gen-list');
  PAGERS.gen = PAGERS.gen || { page: 1, size: 10 };
  if (items !== undefined) PAGERS.gen.items = items;
  PAGERS.gen.render = function () { renderGenList(); };  // 翻页时重用当前 items
  if (!PAGERS.gen.items || !PAGERS.gen.items.length) {
    box.innerHTML = '<p class="tip">未生成任何题集</p>';
    return;
  }
  var html = '<table class="records-table"><thead><tr>' +
    '<th>题集</th><th>操作</th></tr></thead><tbody>';
  pagerItems('gen').forEach(function (it) {
    html += '<tr><td>' + escapeHtml(genSetLabel(it)) + '</td>' +
      '<td><button class="btn primary btn-sm" data-act="preview" data-date="' +
      escapeHtml(it.date) + '" data-grade="' + it.grade + '">预览</button> ' +
      '<button class="btn btn-sm" data-act="regen" data-date="' +
      escapeHtml(it.date) + '" data-grade="' + it.grade + '">重新生成</button>' +
      '</td></tr>';
  });
  html += '</tbody></table>' + pagerHtml('gen');
  box.innerHTML = html;
  bindPagerEvents(box);
  box.querySelectorAll('.records-table tbody button').forEach(function (btn) {
    var date = btn.getAttribute('data-date');
    var grade = parseInt(btn.getAttribute('data-grade'), 10);
    if (btn.getAttribute('data-act') === 'preview') {
      btn.addEventListener('click', function () { previewSet(date, grade); });
    } else {
      btn.addEventListener('click', function () { regenerateSet(btn, date, grade); });
    }
  });
}

/* 预览：弹窗展示该天题目（仅题干，不含答案，防抄答案） */
function previewSet(date, grade) {
  var url = '/api/records/detail?user_id=' + encodeURIComponent(state.user) +
    '&date=' + date + '&grade=' + grade;
  fetchJSON(url).then(function (d) {
    if (d.error) { alert(d.error); return; }
    renderPreviewModal(d);
  });
}

function renderPreviewModal(d) {
  $('record-modal-title').textContent =
    '预览 · ' + (GRADE_NAMES[d.grade] || d.grade + '年级') +
    (d.volume === 1 ? '上' : '下') + '-' + d.date;
  var html = '<p class="rec-summary">共 ' + d.total + ' 题（未含答案，答案见导出文档）</p>';
  (d.problems || []).forEach(function (item, idx) {
    html += '<div class="rec-problem">' +
      '<div class="rec-head">' +
      '<span class="cat-tag">' + escapeHtml(TYPE_NAMES[item.type] || item.type) +
      '</span><span class="rec-index">' + (idx + 1) + '.</span></div>' +
      '<div class="rec-question">' + escapeHtml(item.question) + '</div>' +
      '</div>';
  });
  $('record-modal-body').innerHTML = html;
  $('record-modal').classList.remove('hidden');
}

/* 重新生成单天题集（沿用练习页的 regenerate 接口） */
function regenerateSet(btn, date, grade) {
  btn.disabled = true;
  fetchJSON('/api/regenerate', {
    method: 'POST',
    body: JSON.stringify({
      grade: grade, date: date, user_id: state.user,
      semester: state.semester || '0',
      kind: state.kind || '0',
    }),
  }).then(function (data) {
    btn.disabled = false;
    if (data.error) { alert(data.error); return; }
    btn.textContent = '已重新生成';
    setTimeout(function () { btn.textContent = '重新生成'; }, 1500);
  });
}

/* ---------- 练习记录页 ---------- */

function monthAgoStr() {
  var d = new Date();
  d.setMonth(d.getMonth() - 1);
  var m = ('0' + (d.getMonth() + 1)).slice(-2);
  var day = ('0' + d.getDate()).slice(-2);
  return d.getFullYear() + '-' + m + '-' + day;
}

function volumeName(v) { return v === 1 ? '上册' : '下册'; }

function countText(c) {
  if (!c || !c.total) return '—';
  return c.correct + '/' + c.total;
}

/* 竖式 + 解方程合并计数（练习页中两者共用一个分节） */
function middleCountText(counts) {
  var v = counts.vertical || { correct: 0, total: 0 };
  var e = counts.equation || { correct: 0, total: 0 };
  var total = v.total + e.total;
  if (!total) return '—';
  return (v.correct + e.correct) + '/' + total;
}

function loadRecords() {
  var box = $('records-table');
  if (!box) return;
  var g = $('records-grade').value || '0';
  var from = $('records-from').value || monthAgoStr();
  var to = $('records-to').value || todayStr();
  var url = '/api/records?user_id=' + encodeURIComponent(state.user) +
    '&grade=' + encodeURIComponent(g) +
    '&date_from=' + from + '&date_to=' + to;
  box.innerHTML = '<p class="tip">加载中…</p>';
  fetchJSON(url).then(function (data) {
    if (PAGERS.records) PAGERS.records.page = 1;  // 新筛选回第一页
    renderRecords(data.items || []);
  });
}

function renderRecords(items) {
  var box = $('records-table');
  PAGERS.records = PAGERS.records || { page: 1, size: 10 };
  if (items !== undefined) PAGERS.records.items = items;
  PAGERS.records.render = function () { renderRecords(); };  // 翻页时重用当前 items
  if (!PAGERS.records.items || !PAGERS.records.items.length) {
    box.innerHTML = '<p class="tip">该条件下没有练习记录</p>';
    return;
  }
  var html = '<table class="records-table"><thead><tr>' +
    '<th>日期</th><th>年级</th><th>册别</th><th>计算题</th>' +
    '<th>竖式 / 解方程</th><th>应用题</th><th>操作</th>' +
    '</tr></thead><tbody>';
  pagerItems('records').forEach(function (it) {
    html += '<tr>' +
      '<td>' + escapeHtml(it.date) + '</td>' +
      '<td>' + escapeHtml(GRADE_NAMES[it.grade] || it.grade + '年级') + '</td>' +
      '<td>' + volumeName(it.volume) + '</td>' +
      '<td>' + countText(it.counts && it.counts.calc) + '</td>' +
      '<td>' + middleCountText(it.counts || {}) + '</td>' +
      '<td>' + countText(it.counts && it.counts.word) + '</td>' +
      '<td><button class="btn primary btn-sm" data-date="' + escapeHtml(it.date) +
      '" data-grade="' + it.grade + '">详情</button></td>' +
      '</tr>';
  });
  html += '</tbody></table>' + pagerHtml('records');
  box.innerHTML = html;
  bindPagerEvents(box);
  box.querySelectorAll('.records-table tbody button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      showRecordDetail(btn.getAttribute('data-date'),
                       parseInt(btn.getAttribute('data-grade'), 10));
    });
  });
}

function showRecordDetail(date, grade) {
  var url = '/api/records/detail?user_id=' + encodeURIComponent(state.user) +
    '&date=' + date + '&grade=' + grade;
  fetchJSON(url).then(function (d) {
    if (d.error) { alert(d.error); return; }
    renderRecordModal(d);
  });
}

function recStatusHtml(correct) {
  if (correct === true) return '<span class="rec-status ok">✔ 正确</span>';
  if (correct === false) return '<span class="rec-status wrong">✘ 错误</span>';
  return '<span class="rec-status none">未作答</span>';
}

/* 应用题/解方程：按小问或变量展示逐项作答与对错 */
function recSubAnswersHtml(item) {
  var labels = item.answer_labels || [];
  var sub = item.sub_results || [];
  if (!labels.length && !sub.length) return '';
  var answers = item.user_answer ? item.user_answer.split('；') : [];
  var html = '<div class="rec-sub-list">';
  var n = Math.max(labels.length, sub.length, answers.length);
  for (var i = 0; i < n; i++) {
    var mark = sub[i]
      ? (sub[i].correct ? '<span class="step-result ok">✔</span>'
                        : '<span class="step-result wrong">✘</span>')
      : '';
    html += '<div class="step-row">' +
      '<span class="step-hint">' + escapeHtml(labels[i] || ('第' + (i + 1) + '问')) +
      '</span><span class="rec-ans">' + escapeHtml(answers[i] || '—') + '</span>' +
      mark + '</div>';
  }
  return html + '</div>';
}

function renderRecordModal(d) {
  $('record-modal-title').textContent =
    d.date + ' · ' + (GRADE_NAMES[d.grade] || d.grade + '年级') +
    ' · ' + volumeName(d.volume);
  var html = '<p class="rec-summary">共 ' + d.total + ' 题，答对 <b>' +
    d.correct + '</b> 题</p>';
  (d.problems || []).forEach(function (item, idx) {
    html += '<div class="rec-problem">' +
      '<div class="rec-head">' +
      '<span class="cat-tag">' + escapeHtml(TYPE_NAMES[item.type] || item.type) +
      '</span><span class="rec-index">' + (idx + 1) + '.</span>' +
      recStatusHtml(item.correct) + '</div>' +
      '<div class="rec-question">' + escapeHtml(item.question) + '</div>' +
      '<div class="rec-answer">我的答案：<b>' +
      (item.user_answer ? escapeHtml(item.user_answer) : '未作答') +
      '</b></div>' +
      recSubAnswersHtml(item) +
      '</div>';
  });
  $('record-modal-body').innerHTML = html;
  $('record-modal').classList.remove('hidden');
}

function closeRecordModal() {
  $('record-modal').classList.add('hidden');
}

/* ---------- 设置页 ---------- */

function loadConfig() {
  fetchJSON('/api/config').then(function (cfg) {
    $('cfg-calc').value = cfg.calc_count;
    $('cfg-vertical').value = cfg.vertical_count;
    $('cfg-word').value = cfg.word_count;
  });
}

function saveConfig() {
  fetchJSON('/api/config', {
    method: 'POST',
    body: JSON.stringify({
      calc_count: parseInt($('cfg-calc').value, 10) || 0,
      vertical_count: parseInt($('cfg-vertical').value, 10) || 0,
      word_count: parseInt($('cfg-word').value, 10) || 0
    })
  }).then(function () {
    alert('保存成功。如需当日题集生效，请回到做题页点"重新生成"。');
  });
}

/* ---------- 用户管理 ---------- */

function initUsers() {
  return fetchJSON('/api/users').then(function (list) {
    state.users = list || [];
    // 记录的用户已被删除时回退到默认用户
    if (!state.users.some(function (u) { return u.id === state.user; })) {
      state.user = 'default';
      localStorage.setItem('mpt_user', 'default');
    }
    var sel = $('user-select');
    sel.innerHTML = '';
    state.users.forEach(function (u) {
      var opt = document.createElement('option');
      opt.value = u.id;
      opt.textContent = u.name;
      sel.appendChild(opt);
    });
    sel.value = state.user;
    renderUserManage();
  });
}

/* ---------- 用户与年级 ---------- */

/* 年级按用户记忆（localStorage 键：mpt_grade_{用户id}） */
function userGradeKey() {
  return 'mpt_grade_' + state.user;
}

function loadUserGrade() {
  var g = parseInt(localStorage.getItem(userGradeKey()), 10);
  return (g >= 1 && g <= MAX_GRADE) ? g : 3;
}

/* 把当前用户的年级同步到侧边栏、导出页只读展示与学情页下拉 */
function applyUserGrade() {
  state.grade = loadUserGrade();
  $('grade-select').value = state.grade;
  $('stats-grade').value = state.grade;
  updateExportInfo();
  updateExportLinks();
}

function onGradeChange() {
  state.grade = parseInt($('grade-select').value, 10) || 3;
  localStorage.setItem(userGradeKey(), state.grade);
  $('stats-grade').value = state.grade;
  updateExportInfo();
  updateExportLinks();
  loadDaily();
  loadStats();
}

function onUserChange() {
  state.user = $('user-select').value;
  localStorage.setItem('mpt_user', state.user);
  applyUserGrade();
  loadDaily();
  loadRecords();
  loadStats();
  renderUserManage();
}

function addUser() {
  var name = $('new-user-name').value.trim();
  if (!name) { alert('请输入姓名'); return; }
  fetchJSON('/api/users', { method: 'POST', body: JSON.stringify({ name: name }) })
    .then(function (res) {
      if (res.error) { alert(res.error); return; }
      $('new-user-name').value = '';
      state.user = res.id;
      localStorage.setItem('mpt_user', res.id);
      // 新用户继承当前选中的年级
      localStorage.setItem(userGradeKey(), state.grade);
      initUsers().then(function () {
        loadDaily();
        loadRecords();
      });
    });
}

function deleteUser(u) {
  if (!confirm('确定删除用户「' + u.name + '」吗？其全部练习记录将一并删除！')) return;
  fetchJSON('/api/users', {
    method: 'DELETE',
    body: JSON.stringify({ user_id: u.id })
  }).then(function (res) {
    if (res.error) { alert(res.error); return; }
    if (u.id === state.user) {
      state.user = 'default';
      localStorage.setItem('mpt_user', 'default');
    }
    initUsers().then(function () {
      applyUserGrade();  // 当前用户可能变为默认用户，恢复其年级
      loadDaily();
      loadRecords();
    });
  });
}

function renderUserManage() {
  var box = $('user-manage-list');
  if (!box) return;
  PAGERS.users = PAGERS.users || { page: 1, size: 5 };
  PAGERS.users.items = state.users;
  PAGERS.users.render = renderUserManage;
  box.innerHTML = '';
  pagerItems('users').forEach(function (u) {
    var row = document.createElement('div');
    row.className = 'user-item';
    var label = document.createElement('span');
    label.textContent = u.name +
      (u.id === 'default' ? '（默认）' : '') +
      (u.id === state.user ? ' · 当前' : '');
    row.appendChild(label);
    if (u.id !== 'default') {
      var btn = document.createElement('button');
      btn.className = 'btn danger btn-sm';
      btn.textContent = '删除';
      btn.addEventListener('click', function () { deleteUser(u); });
      row.appendChild(btn);
    }
    box.appendChild(row);
  });
  var wrap = document.createElement('div');
  wrap.innerHTML = pagerHtml('users');
  while (wrap.firstChild) box.appendChild(wrap.firstChild);
  bindPagerEvents(box);
}

/* ---------- 学情页 ---------- */

function loadStats() {
  var box = $('stats-content');
  if (!box) return;
  var g = $('stats-grade').value || state.grade;
  box.innerHTML = '<p class="tip">加载中…</p>';
  fetchJSON('/api/stats?grade=' + g + '&user_id=' +
      encodeURIComponent(state.user) + '&semester=' + state.semester)
    .then(function (d) {
      if (PAGERS.weak) PAGERS.weak.page = 1;  // 新数据回第一页
      if (PAGERS.cats) PAGERS.cats.page = 1;
      renderStats(d);
    });
}

var lastStatsData = null;  // 学情页分页翻页时重渲染用

function statCard(label, value) {
  return '<div class="stat-card"><div class="stat-value">' + escapeHtml(value) +
    '</div><div class="stat-label">' + escapeHtml(label) + '</div></div>';
}

function rateClass(rate) {
  if (rate >= 60) return 'ok';
  if (rate >= 40) return 'mid';
  return 'bad';
}

function barsHtml(rows, withCurve) {
  return rows.map(function (r) {
    return '<div class="bar-row">' +
      '<span class="bar-name">' + escapeHtml(r.name) + '</span>' +
      '<div class="bar"><div class="bar-fill ' + rateClass(r.rate) +
      '" style="width:' + Math.max(1, r.rate) + '%"></div></div>' +
      '<span class="bar-rate">' + r.rate + '%</span>' +
      '<span class="bar-count">' + r.attempts + ' 道</span>' +
      (withCurve ? '<button class="btn btn-xs curve-btn" data-cat="' +
        escapeHtml(r.name) + '" title="查看该知识点的正确率曲线">曲线</button>'
        : '') +
      '</div>';
  }).join('');
}

function curveSvg(daily) {
  var W = 640, H = 240, PL = 36, PB = 28, PT = 12, PR = 10;
  var iw = W - PL - PR, ih = H - PT - PB;
  var n = daily.length;
  var svg = '<svg viewBox="0 0 ' + W + ' ' + H +
    '" class="curve-svg" preserveAspectRatio="xMidYMid meet">';
  // 横向网格线 + y 轴刻度（0-100%）
  [0, 25, 50, 75, 100].forEach(function (v) {
    var y = PT + ih - ih * v / 100;
    svg += '<line x1="' + PL + '" y1="' + y + '" x2="' + (W - PR) +
      '" y2="' + y + '" stroke="#e5e5e5" stroke-width="1"/>';
    svg += '<text x="' + (PL - 6) + '" y="' + (y + 4) +
      '" text-anchor="end" font-size="11" fill="#999">' + v + '</text>';
  });
  // 数据点
  var pts = daily.map(function (d, i) {
    var x = n === 1 ? PL + iw / 2 : PL + iw * i / (n - 1);
    var y = PT + ih - ih * d.rate / 100;
    return [x, y, d];
  });
  svg += '<polyline points="' +
    pts.map(function (p) { return p[0] + ',' + p[1]; }).join(' ') +
    '" fill="none" stroke="var(--primary)" stroke-width="2"/>';
  pts.forEach(function (p) {
    svg += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="3.5" fill="var(--primary)">' +
      '<title>' + p[2].date + '：' + p[2].rate + '%（答对 ' + p[2].correct +
      '/' + p[2].total + '）</title></circle>';
  });
  // x 轴日期标签（最多均匀取 6 个）
  var step = Math.max(1, Math.ceil(n / 6));
  pts.forEach(function (p, i) {
    if (i % step === 0 || i === n - 1) {
      svg += '<text x="' + p[0] + '" y="' + (H - 8) +
        '" text-anchor="middle" font-size="10" fill="#999">' +
        p[2].date.slice(5) + '</text>';
    }
  });
  svg += '</svg>';
  return svg;
}

function renderStats(d) {
  var box = $('stats-content');
  lastStatsData = d;  // 分页翻页时重渲染用
  var s = d.summary;
  if (!s || !s.total) {
    box.innerHTML = '<div class="card"><p class="tip">当前用户在该年级还没有作答记录。做题并提交后，这里会显示正确率曲线和薄弱知识点。</p></div>';
    return;
  }
  PAGERS.weak = PAGERS.weak || { page: 1, size: 8 };
  PAGERS.weak.items = d.weak_points;
  PAGERS.weak.render = function () { renderStats(lastStatsData); };
  PAGERS.cats = PAGERS.cats || { page: 1, size: 8 };
  PAGERS.cats.items = d.by_category;
  PAGERS.cats.render = function () { renderStats(lastStatsData); };
  var html = '';
  // 概览
  html += '<div class="stats-grid">' +
    statCard('累计做题', s.total + ' 道') +
    statCard('答对', s.correct + ' 道') +
    statCard('总正确率', s.rate + '%') +
    statCard('练习天数', d.daily.length + ' 天') +
    '</div>';
  // 正确率曲线（附整个学期查看按钮）
  html += '<div class="card"><div class="card-head-row"><h3>正确率曲线（最近 ' +
    d.daily.length + ' 个练习日）</h3>' +
    '<button id="btn-sem-curve" class="btn btn-sm">整个学期</button></div>' +
    '<div class="chart-box">' + curveSvg(d.daily) + '</div>' +
    '<p class="tip">把鼠标放在曲线上可查看每天的答题情况。</p></div>';
  // 题型正确率（附曲线按钮）
  html += '<div class="card"><div class="card-head-row"><h3>题型正确率</h3>' +
    '<button id="btn-type-curve" class="btn btn-sm">正确率曲线</button></div>' +
    barsHtml(d.by_type.map(function (t) {
      return { name: TYPE_NAMES[t.name] || t.name, rate: t.rate, attempts: t.attempts };
    })) + '</div>';
  // 薄弱知识点（分页）
  html += '<div class="card"><h3>薄弱知识点</h3>';
  if (d.weak_points.length) {
    html += barsHtml(pagerItems('weak').map(function (w) {
      return { name: w.category, rate: w.rate, attempts: w.attempts };
    }));
    html += pagerHtml('weak');
    html += '<p class="tip">下次生成练习时会自动增加这些知识点的题目。</p>';
  } else {
    html += '<p class="tip">暂无薄弱知识点（正确率都在 80% 以上，或部分知识点做题量还不足 5 道）。</p>';
  }
  html += '</div>';
  // 全部知识点正确率（分页，每行附曲线按钮）
  html += '<div class="card"><h3>知识点正确率</h3>' +
    (d.by_category.length
      ? barsHtml(pagerItems('cats').map(function (c) {
          return { name: c.name, rate: c.rate, attempts: c.attempts };
        }), true) + pagerHtml('cats')
      : '<p class="tip">暂无数据</p>') +
    '</div>';
  box.innerHTML = html;
  bindPagerEvents(box);
  // 曲线按钮：整个学期 / 题型曲线 / 逐知识点曲线（翻页重渲染后需重新绑定）
  var semBtn = $('btn-sem-curve');
  if (semBtn) semBtn.addEventListener('click', showSemesterCurve);
  var typeBtn = $('btn-type-curve');
  if (typeBtn) typeBtn.addEventListener('click', showTypeCurves);
  box.querySelectorAll('.curve-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      showCatCurve(btn.getAttribute('data-cat'));
    });
  });
}

/* ---------- 学情正确率曲线弹窗 ---------- */

function openChartModal(title, bodyHtml) {
  $('chart-modal-title').textContent = title;
  $('chart-modal-body').innerHTML = bodyHtml;
  $('chart-modal').classList.remove('hidden');
}

/* 整个学期的正确率曲线（服务端按学期时间窗过滤全部练习日） */
function showSemesterCurve() {
  var d = lastStatsData;
  if (!d) return;
  var list = d.semester_curve || [];
  if (!list.length) {
    openChartModal('正确率曲线 — ' + (d.semester_label || '本学期'),
      '<p class="tip">本学期还没有作答记录。</p>');
    return;
  }
  openChartModal('正确率曲线 — ' + d.semester_label,
    '<div class="chart-box">' + curveSvg(list) + '</div>' +
    '<p class="tip">本学期共 ' + list.length + ' 个练习日；鼠标悬停可查看每天详情。</p>');
}

/* 三条题型曲线一起看 */
function showTypeCurves() {
  var d = lastStatsData;
  if (!d) return;
  var parts = [];
  ['calc', 'vertical', 'equation', 'word'].forEach(function (t) {
    var list = (d.type_daily || {})[t];
    if (list && list.length) {
      parts.push('<h4 class="chart-sub">' + (TYPE_NAMES[t] || t) +
        '</h4><div class="chart-box">' + curveSvg(list) + '</div>');
    }
  });
  if (!parts.length) {
    openChartModal('题型正确率曲线', '<p class="tip">暂无作答记录。</p>');
    return;
  }
  openChartModal('题型正确率曲线（全部练习日）',
    parts.join('') + '<p class="tip">鼠标悬停可查看每天详情。</p>');
}

/* 单个知识点的正确率曲线 */
function showCatCurve(cat) {
  var d = lastStatsData;
  if (!d) return;
  var list = (d.cat_daily || {})[cat];
  if (!list || !list.length) {
    openChartModal('知识点正确率曲线 — ' + cat,
      '<p class="tip">暂无作答记录。</p>');
    return;
  }
  openChartModal('知识点正确率曲线 — ' + cat,
    '<div class="chart-box">' + curveSvg(list) + '</div>' +
    '<p class="tip">共 ' + list.length + ' 个练习日；鼠标悬停可查看每天详情。</p>');
}

/* ---------- 初始化 ---------- */

/* 年级选项上界：当前只开放小学（1-6 年级），初中内容后续再增加 */
var MAX_GRADE = 6;

function initGradeOptions(sel) {
  for (var g = 1; g <= MAX_GRADE; g++) {
    var opt = document.createElement('option');
    opt.value = g;
    opt.textContent = GRADE_NAMES[g];
    sel.appendChild(opt);
  }
}

function onSemesterChange() {
  state.semester = $('semester-select').value;
  localStorage.setItem('mpt_semester', state.semester);
  updateExportInfo();   // 导出页学期为只读展示，跟随侧边栏全局值
  updateExportLinks();
  loadDaily();
}

function onKindChange() {
  state.kind = $('kind-select').value;
  localStorage.setItem('mpt_bank_kind', state.kind);
  updateExportLinks();
  loadDaily();
}

function init() {
  initGradeOptions($('grade-select'));
  initGradeOptions($('stats-grade'));
  initGradeOptions($('records-grade'));
  // 练习记录年级筛选：首项"最高年级（默认）"，grade=0 由服务端取最高年级
  var recSel = $('records-grade');
  var autoOpt = document.createElement('option');
  autoOpt.value = '0';
  autoOpt.textContent = '最高年级（默认）';
  recSel.insertBefore(autoOpt, recSel.firstChild);
  recSel.value = '0';
  // 练习记录默认时间范围：最近 1 个月
  $('records-from').value = monthAgoStr();
  $('records-to').value = todayStr();
  // 学期：侧边栏全局选择器，做题 / 生成导出共用，localStorage 持久化
  $('semester-select').value = state.semester;
  $('btn-generate').addEventListener('click', generateSets);
  $('kind-select').value = state.kind;
  $('date-input').value = state.date;
  $('export-date').value = state.date;
  applyUserGrade();  // 恢复当前用户记忆的年级并同步各下拉
  updateExportInfo();

  // 页面心跳：每 3 秒上报一次服务端；页面全部关闭后服务在超时后自动退出。
  // 心跳必须放在 Web Worker 里：浏览器对后台标签页的主线程定时器有激进节流
  // （后台约 5 分钟后强制降为每分钟 1 次），页面开着也会被看门狗误判退出。
  var HB_MS = 3000;
  function sendHeartbeat() {
    fetch('/api/heartbeat', { method: 'POST' }).catch(function () {});
  }
  try {
    var hbCode = 'function beat(){fetch("' + location.origin +
      '/api/heartbeat",{method:"POST"}).catch(function(){});}' +
      'beat();setInterval(beat,' + HB_MS + ');';
    var hbUrl = URL.createObjectURL(new Blob([hbCode], { type: 'text/javascript' }));
    new Worker(hbUrl);
  } catch (e) {
    sendHeartbeat();
    setInterval(sendHeartbeat, HB_MS);
  }
  // 从后台切回前台时立即补一次心跳（Worker 被浏览器冻结时的兜底）
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) sendHeartbeat();
  });

  $('btn-load').addEventListener('click', loadDaily);
  $('btn-regenerate').addEventListener('click', regenerate);
  $('btn-submit-all').addEventListener('click', submitAll);
  $('submit-modal-close').addEventListener('click', function () {
    $('submit-modal').classList.add('hidden');
  });
  $('chart-modal-close').addEventListener('click', function () {
    $('chart-modal').classList.add('hidden');
  });
  $('submit-modal').addEventListener('click', function (e) {
    if (e.target === $('submit-modal')) $('submit-modal').classList.add('hidden');
  });
  $('btn-save-config').addEventListener('click', saveConfig);
  $('btn-units-all').addEventListener('click', function () { setAllUnits(true); });
  $('btn-units-none').addEventListener('click', function () { setAllUnits(false); });
  $('btn-add-user').addEventListener('click', addUser);
  $('user-select').addEventListener('change', onUserChange);
  $('grade-select').addEventListener('change', onGradeChange);
  $('semester-select').addEventListener('change', onSemesterChange);
  $('kind-select').addEventListener('change', onKindChange);
  $('stats-grade').addEventListener('change', loadStats);
  $('btn-records').addEventListener('click', loadRecords);
  $('record-modal-close').addEventListener('click', closeRecordModal);
  $('record-modal').addEventListener('click', function (e) {
    if (e.target === $('record-modal')) closeRecordModal();  // 点击遮罩关闭
  });
  ['export-date', 'export-date-to', 'export-answers'].forEach(function (id) {
    $(id).addEventListener('change', updateExportLinks);
  });

  window.addEventListener('hashchange', route);
  // 先加载用户列表（可能纠正已删除的当前用户），再加载各页数据
  initUsers().then(function () {
    applyUserGrade();  // 用户被纠正时同步其记忆年级
    route();
    updateExportLinks();
    loadDaily();
    loadConfig();
  });
}

document.addEventListener('DOMContentLoaded', init);
