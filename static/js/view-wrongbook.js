/* 错题本页逻辑（依赖 app.js 全局工具：$, fetchJSON, escapeHtml, cardHtml,
   typeLabel, appAlert, openSubmitModal, GRADE_NAMES, TYPE_NAMES, state）
   数据接口：/api/wrongbook、/api/wrongbook/tag、/api/wrongbook/resolve、
             /api/wrongbook/practice、/api/wrongbook/answer */

var wb = {
  items: [],      // 错题列表（服务端聚合返回）
  shown: 0,       // 已渲染条数（分页加载）
  set: null,      // 重练题集（含 attempts）
  originKeys: [], // 当前重练题集对应的错题 key（全对后可一键标记已掌握）
  gradeTouched: false, // 用户是否手动改过年级筛选（false 时默认跟随左侧年级）
  PAGE: 20
};

var WB_TAG_NAMES = { careless: '粗心', unknown: '不会' };

/* ---------- 错题列表 ---------- */

function wbFilters() {
  var g = $('wb-grade'), s = $('wb-status');
  return {
    grade: g ? (parseInt(g.value, 10) || 0) : 0,
    status: s ? s.value : 'open'
  };
}

function loadWrongbook() {
  // 年级筛选默认跟随左侧年级选择（用户手动改过筛选后以手动为准）
  var g = $('wb-grade');
  if (g && !wb.gradeTouched && state.grade >= 1 && state.grade <= 9) {
    g.value = String(state.grade);
  }
  var f = wbFilters();
  return fetchJSON('/api/wrongbook?user_id=' + encodeURIComponent(state.user) +
      '&grade=' + f.grade + '&status=' + encodeURIComponent(f.status))
    .then(function (d) {
      wb.items = d.items || [];
      wb.shown = 0;
      renderWrongList();
    })
    .catch(function () {
      var box = $('wb-list');
      if (box) box.innerHTML = '<p class="tip">加载失败，请点击"刷新"重试</p>';
    });
}

function wbItemHtml(e, idx) {
  var html = '<div class="wb-item">';
  html += '<div class="wb-item-head">' +
    '<span class="wb-date">' + escapeHtml(e.date) + ' · ' +
    escapeHtml(GRADE_NAMES[e.grade] || (e.grade + '年级')) + '</span>' +
    '<span class="cat-tag">' + escapeHtml(TYPE_NAMES[e.type] || e.type) + '</span>';
  if (e.category) {
    html += '<span class="cat-tag">' + escapeHtml(e.category) + '</span>';
  }
  if (e.resolved) {
    // 已掌握：绿色 ✔ + 徽标，与未掌握（红色 ✘）明显区分
    html += '<span class="cat-tag wb-resolved-tag">已掌握</span>' +
      '<span class="problem-status wb-status-ok" title="已掌握">✔</span>';
  } else {
    html += '<span class="problem-status" style="color:var(--danger)">✘</span>';
  }
  html += '</div>';
  html += '<div class="rec-question">' + escapeHtml(e.question) + '</div>';
  if (e.user_answer) {
    html += '<div class="wb-user-answer">我的作答：' + escapeHtml(e.user_answer) + '</div>';
  } else if (Array.isArray(e.sub_results)) {
    html += '<div class="wb-user-answer">我的作答：' +
      e.sub_results.map(function (s) {
        return s.correct ? '✔' : '✘';
      }).join(' ') + '</div>';
  }
  if (e.answer_text) {
    html += '<div class="wb-answer">正确答案：<b>' + escapeHtml(e.answer_text) + '</b></div>';
  } else {
    html += '<div class="wb-locked">🔒 答案次日解锁（防止先看答案再订正）</div>';
  }
  html += '<div class="wb-actions">' +
    '<button class="btn btn-sm wb-tag-btn' + (e.tag === 'careless' ? ' active' : '') +
    '" data-wb-act="tag" data-tag="careless" data-idx="' + idx + '">粗心</button>' +
    '<button class="btn btn-sm wb-tag-btn' + (e.tag === 'unknown' ? ' active' : '') +
    '" data-wb-act="tag" data-tag="unknown" data-idx="' + idx + '">不会</button>' +
    '<button class="btn btn-sm wb-tag-btn' + (e.resolved ? ' active' : '') +
    '" data-wb-act="resolve" data-idx="' + idx + '" title="' +
    (e.resolved ? '点击取消掌握' : '标记为已掌握') + '">已掌握</button>' +
    '<button class="btn btn-sm" data-wb-act="practice" data-idx="' + idx + '">举一反三</button>' +
    '</div>';
  html += '</div>';
  return html;
}

function renderWrongList() {
  var box = $('wb-list');
  if (!box) return;
  var items = wb.items;
  if (!items.length) {
    box.innerHTML = '<p class="tip">当前筛选条件下没有错题，保持每天练习！</p>';
    $('wb-more-wrap').classList.add('hidden');
    return;
  }
  var slice = items.slice(0, wb.shown + wb.PAGE);
  wb.shown = slice.length;
  box.innerHTML = slice.map(wbItemHtml).join('');
  bindWbItemEvents(box);
  $('wb-more-wrap').classList.toggle('hidden', wb.shown >= items.length);
}

function bindWbItemEvents(box) {
  box.querySelectorAll('button[data-wb-act]').forEach(function (b) {
    b.addEventListener('click', function () {
      var idx = parseInt(b.getAttribute('data-idx'), 10);
      var e = wb.items[idx];
      if (!e) return;
      var act = b.getAttribute('data-wb-act');
      if (act === 'tag') {
        wbTag(e, b.getAttribute('data-tag'));
      } else if (act === 'resolve') {
        wbResolve([e.key], !e.resolved);
      } else if (act === 'practice') {
        wbStartPractice([e.key]);
      }
    });
  });
}

function wbTag(e, tag) {
  var next = e.tag === tag ? '' : tag;  // 再点一次取消标记
  fetchJSON('/api/wrongbook/tag', {
    method: 'POST',
    body: JSON.stringify({ user_id: state.user, key: e.key, tag: next })
  }).then(function () { loadWrongbook(); })
    .catch(function () { appAlert('操作失败，请重试'); });
}

function wbResolve(keys, resolved) {
  fetchJSON('/api/wrongbook/resolve', {
    method: 'POST',
    body: JSON.stringify({ user_id: state.user, keys: keys, resolved: resolved })
  }).then(function () {
    if (wb.set) return;  // 重练页内触发的标记不刷新列表（返回列表时再刷）
    loadWrongbook();
  }).catch(function () { appAlert('操作失败，请重试'); });
}

/* ---------- 举一反三重练 ---------- */

function wbStartPractice(keys) {
  fetchJSON('/api/wrongbook/practice', {
    method: 'POST',
    body: JSON.stringify({ user_id: state.user, keys: keys })
  }).then(function (d) {
    if (d.error) { appAlert(d.error); return; }
    wb.set = d;
    wb.originKeys = d.origin_keys || keys;
    $('wb-list-box').classList.add('hidden');
    $('wb-practice-box').classList.remove('hidden');
    window.scrollTo(0, 0);
    renderWbProblems();
  }).catch(function () { appAlert('生成重练题失败，请重试'); });
}

function renderWbProblems() {
  var set = wb.set;
  if (!set) return;
  $('wb-practice-count').textContent =
    '共 ' + set.problems.length + ' 题（原题重做 + 同型变式）';
  var box = $('wb-problem-list');
  box.innerHTML = '';
  set.problems.forEach(function (p, idx) {
    var att = (set.attempts || {})[p.id] || null;
    var card = document.createElement('div');
    card.className = 'card problem-card';
    card.innerHTML = cardHtml(p, idx, att);
    box.appendChild(card);
  });
  wbUpdateProgress();
}

function wbUpdateProgress() {
  var set = wb.set;
  var attempts = (set && set.attempts) || {};
  var total = set.problems.length, ok = 0, done = 0;
  set.problems.forEach(function (p) {
    var a = attempts[p.id];
    if (a && a.result) {
      done++;
      if (a.result.correct) ok++;
    }
  });
  var fill = $('wb-progress-fill');
  if (fill) fill.style.width = (total ? Math.round(ok * 100 / total) : 0) + '%';
  $('wb-progress-text').textContent = done + '/' + total + ' · 正确 ' + ok;
}

/* 与做题页 buildPayload 同构；重练题按 set_id 定位，无需 date/grade 元数据 */
function wbBuildPayload(p) {
  if (p.type === 'word') {
    return { answers: (p.answer_labels || []).map(function (label, i) {
      var el = $('ans-' + p.id + '-' + i);
      return el ? el.value : '';
    }) };
  }
  if (p.type === 'equation') {
    var main = {};
    (p.answer_vars || ['x']).forEach(function (v) {
      var el = $('input-' + p.id + '-' + v);
      main[v] = el ? el.value : '';
    });
    return { main: main };
  }
  var el = $('input-' + p.id);
  return { main: el ? el.value : '' };
}

function wbSubmitAll() {
  var set = wb.set;
  if (!set) return;
  var pending = set.problems.filter(function (p) {
    var a = (set.attempts || {})[p.id];
    return !(a && a.result && a.result.correct);
  });
  var seq = Promise.resolve();
  pending.forEach(function (item) {
    seq = seq.then(function () {
      var payload = wbBuildPayload(item);
      return fetchJSON('/api/wrongbook/answer', {
        method: 'POST',
        body: JSON.stringify({
          user_id: state.user,
          set_id: set.set_id,
          problem_id: item.id,
          main: payload.main,
          answers: payload.answers
        })
      }).then(function (r) {
        if (!r.error) {
          set.attempts[item.id] = { payload: payload, result: r };
        }
      });
    });
  });
  seq.then(function () {
    renderWbProblems();
    wbShowResult();
  });
}

function wbShowResult() {
  var set = wb.set;
  var attempts = set.attempts || {};
  var total = set.problems.length, ok = 0;
  set.problems.forEach(function (p) {
    var a = attempts[p.id];
    if (a && a.result && a.result.correct) ok++;
  });
  var allOk = ok === total && total > 0;
  var html = '<p>重练完成：正确 <b>' + ok + '</b> / ' + total + ' 题。</p>';
  if (allOk && wb.originKeys.length) {
    openSubmitModal('重练结果', html + '<p>全部答对！是否把对应的错题标记为已掌握？</p>', [
      { text: '暂不', fn: null },
      { text: '标记已掌握', cls: 'primary', fn: function () {
        wbResolve(wb.originKeys, true);
        wbBack();
      } }
    ]);
  } else {
    openSubmitModal('重练结果', html, [
      { text: '好的', fn: null }
    ]);
  }
}

function wbBack() {
  wb.set = null;
  $('wb-practice-box').classList.add('hidden');
  $('wb-list-box').classList.remove('hidden');
  loadWrongbook();
}

/* ---------- 页内初始化 ---------- */

function wbInit() {
  var sel = $('wb-grade');
  if (sel) {
    var opt0 = document.createElement('option');
    opt0.value = '0';
    opt0.textContent = '全部年级';
    sel.appendChild(opt0);
    for (var g = 1; g <= 9; g++) {
      var o = document.createElement('option');
      o.value = String(g);
      o.textContent = GRADE_NAMES[g] || (g + '年级');
      sel.appendChild(o);
    }
    sel.addEventListener('change', function () {
      wb.gradeTouched = true;
      loadWrongbook();
    });
  }
  var status = $('wb-status');
  if (status) status.addEventListener('change', loadWrongbook);
  $('btn-wb-refresh').addEventListener('click', loadWrongbook);
  $('btn-wb-more').addEventListener('click', renderWrongList);
  $('btn-wb-practice').addEventListener('click', function () {
    var keys = wb.items.filter(function (e) { return !e.resolved; })
      .slice(0, 5)
      .map(function (e) { return e.key; });
    if (!keys.length) {
      appAlert('当前没有未掌握的错题，太棒了！');
      return;
    }
    wbStartPractice(keys);
  });
  $('btn-wb-submit').addEventListener('click', wbSubmitAll);
  $('btn-wb-back').addEventListener('click', wbBack);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', wbInit);
} else {
  wbInit();
}
