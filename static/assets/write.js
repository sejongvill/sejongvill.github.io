/* 세종빌 간편 글쓰기
   - 로그인: DecapBridge(이메일·비밀번호) — 관리 화면(/admin)과 같은 계정
   - 저장: DecapBridge 게이트웨이를 통해 깃허브 저장소에 글 파일과 사진을 한 번에 올림 */
(function () {
  var IDENTITY = 'https://auth.decapbridge.com/sites/4f7f1434-deb1-4975-8034-86cc185eb0b8';
  var GATEWAY = 'https://gateway.decapbridge.com/github';
  var BOARDS = { stories: '일상 이야기', notice: '공지사항', menu: '금주의 식단', schedule: '주요 일정', neighbors: '아름다운 이웃', rights: '인권존중', newsletter: '소식지' };
  var $ = function (s) { return document.querySelector(s); };
  var board = new URLSearchParams(location.search).get('b');
  if (!BOARDS[board]) board = 'stories';
  $('#boardName').textContent = BOARDS[board];
  $('#boardSel').value = board;
  $('#boardSel').addEventListener('change', function () { board = this.value; $('#boardName').textContent = BOARDS[board]; history.replaceState(null, '', '?b=' + board); $('#backLink').href = '/board/' + board + '/'; });
  $('#backLink').href = '/board/' + board + '/';

  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  function msg(t, bad) { var m = $('#wmsg'); m.textContent = t; m.style.color = bad ? 'var(--red)' : ''; }

  /* ---------- 로그인 ---------- */
  function session() {
    var s = store('sv-auth');
    if (s && s.access_token) return s;
    var g = store('gotrue.user');
    if (g && g.token && g.token.access_token) return { access_token: g.token.access_token, refresh_token: g.token.refresh_token, expires_at: g.token.expires_at, email: g.email };
    return null;
  }
  function saveTok(d, email) {
    var s = { access_token: d.access_token, refresh_token: d.refresh_token, expires_at: Date.now() + (d.expires_in || 3600) * 1000, email: email };
    store('sv-auth', s); return s;
  }
  function tokenReq(body) {
    return fetch(IDENTITY + '/token', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(body).toString() })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error_description || j.msg || j.error || '로그인 실패'); return j; }); });
  }
  function token() {
    var s = session();
    if (!s) return Promise.reject(new Error('login'));
    if (s.expires_at && s.expires_at - Date.now() > 60000) return Promise.resolve(s.access_token);
    if (!s.refresh_token) return Promise.reject(new Error('login'));
    return tokenReq({ grant_type: 'refresh_token', refresh_token: s.refresh_token }).then(function (d) { return saveTok(d, s.email).access_token; })
      .catch(function () { store('sv-auth', null); throw new Error('login'); });
  }
  function showState() {
    var s = session();
    $('#loginBox').hidden = !!s;
    $('#writeForm').hidden = !s;
    if (s) $('#who').textContent = (s.email || '직원') + ' 님';
  }
  $('#loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var em = $('#lemail').value.trim(), pw = $('#lpw').value;
    $('#lmsg').textContent = '로그인 중…';
    tokenReq({ grant_type: 'password', username: em, password: pw })
      .then(function (d) { saveTok(d, em); $('#lmsg').textContent = ''; showState(); })
      .catch(function (err) { $('#lmsg').textContent = '로그인하지 못했어요. 이메일과 비밀번호를 확인해 주세요. (' + err.message + ')'; });
  });
  $('#logout').addEventListener('click', function () { store('sv-auth', null); try { localStorage.removeItem('gotrue.user'); } catch (e) {} showState(); });
  showState();

  /* ---------- 사진 고르기·줄이기 ---------- */
  var picked = [];
  function render() {
    var box = $('#thumbs'); box.innerHTML = '';
    picked.forEach(function (p, i) {
      var d = document.createElement('div'); d.className = 'th';
      d.innerHTML = '<img alt=""><button type="button" aria-label="사진 빼기">×</button>' + (i === 0 ? '<span>대표</span>' : '');
      d.querySelector('img').src = p.url;
      d.querySelector('button').onclick = function () { URL.revokeObjectURL(p.url); picked.splice(i, 1); render(); };
      box.appendChild(d);
    });
    $('#pcount').textContent = picked.length ? picked.length + '장 선택됨 (첫 번째 사진이 대표 사진)' : '';
  }
  $('#photos').addEventListener('change', function () {
    [].forEach.call(this.files, function (f) { if (/^image\//.test(f.type) || /\.(heic|heif)$/i.test(f.name)) picked.push({ file: f, url: URL.createObjectURL(f) }); });
    this.value = ''; render();
  });
  function shrink(file) {
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) return file.arrayBuffer().then(function (b) { return { buf: b, ext: (file.name.split('.').pop() || 'jpg').toLowerCase() }; });
    return createImageBitmap(file, { imageOrientation: 'from-image' }).then(function (bmp) {
      var max = 1600, w = bmp.width, h = bmp.height, k = Math.min(1, max / Math.max(w, h));
      var c = document.createElement('canvas'); c.width = Math.round(w * k); c.height = Math.round(h * k);
      c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
      return new Promise(function (res) { c.toBlob(function (b) { b.arrayBuffer().then(function (buf) { res({ buf: buf, ext: 'jpg' }); }); }, 'image/jpeg', 0.84); });
    }).catch(function () { return file.arrayBuffer().then(function (b) { return { buf: b, ext: 'jpg' }; }); });
  }
  function b64(buf) { var s = '', a = new Uint8Array(buf), n = 0x8000; for (var i = 0; i < a.length; i += n) s += String.fromCharCode.apply(null, a.subarray(i, i + n)); return btoa(s); }
  function b64text(t) { return b64(new TextEncoder().encode(t).buffer); }

  /* ---------- 깃허브에 올리기 ---------- */
  function api(path, method, body) {
    return token().then(function (t) {
      return fetch(GATEWAY + path, { method: method || 'GET', headers: { Authorization: 'Bearer ' + t, 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
    }).then(function (r) {
      if (r.status === 401) { store('sv-auth', null); throw new Error('login'); }
      return r.text().then(function (x) { var j = x ? JSON.parse(x) : {}; if (!r.ok) throw new Error((j.message || j.msg || r.status) + ''); return j; });
    });
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function yq(s) { return JSON.stringify(s); }

  $('#writeForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var title = $('#wtitle').value.trim(), body = $('#wbody').value.trim();
    if (!title) { msg('제목을 적어 주세요.', true); return; }
    var btn = $('#wsubmit'); btn.disabled = true;
    var now = new Date(), stamp = '' + now.getFullYear() + pad(now.getMonth() + 1) + pad(now.getDate()) + pad(now.getHours()) + pad(now.getMinutes()) + pad(now.getSeconds());
    var date = now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate()) + ' ' + pad(now.getHours()) + ':' + pad(now.getMinutes());
    var files = [].slice.call($('#attach').files || []);
    var entries = [], imgPaths = [], attPaths = [];
    msg('사진 준비 중… (' + picked.length + '장)');
    var chain = Promise.resolve();
    picked.forEach(function (p, i) {
      chain = chain.then(function () { return shrink(p.file); }).then(function (r) {
        var path = 'files/uploads/' + stamp + '-' + (i + 1) + '.' + r.ext;
        imgPaths.push('/' + path); entries.push({ path: 'static/' + path, content: b64(r.buf) });
        msg('사진 준비 중… ' + (i + 1) + '/' + picked.length);
      });
    });
    files.forEach(function (f, i) {
      chain = chain.then(function () { return f.arrayBuffer(); }).then(function (buf) {
        var ext = (f.name.split('.').pop() || 'bin').toLowerCase(), path = 'files/uploads/' + stamp + '-file' + (i + 1) + '.' + ext;
        attPaths.push({ name: f.name, file: '/' + path }); entries.push({ path: 'static/' + path, content: b64(buf) });
      });
    });
    chain.then(function () {
      var fm = '---\ntitle: ' + yq(title) + '\ndate: ' + date + '\n';
      if (imgPaths.length) fm += 'images:\n' + imgPaths.map(function (x) { return '- ' + x; }).join('\n') + '\n';
      if (attPaths.length) fm += 'files:\n' + attPaths.map(function (x) { return '- name: ' + yq(x.name) + '\n  file: ' + x.file; }).join('\n') + '\n';
      fm += '---\n' + body + '\n';
      entries.push({ path: 'content/' + board + '/' + stamp + '.md', content: b64text(fm) });
      msg('올리는 중… 잠시만 기다려 주세요.');
      // 1) 파일들을 깃허브에 보관 → 2) 한 번에 묶어서 저장
      var blobs = [];
      var c2 = Promise.resolve();
      entries.forEach(function (en, i) {
        c2 = c2.then(function () { return api('/git/blobs', 'POST', { content: en.content, encoding: 'base64' }); })
          .then(function (b) { blobs.push({ path: en.path, mode: '100644', type: 'blob', sha: b.sha }); msg('올리는 중… ' + (i + 1) + '/' + entries.length); });
      });
      return c2.then(function () { return api('/git/refs/heads/main'); })
        .then(function (ref) {
          var head = ref.object.sha;
          return api('/git/commits/' + head).then(function (cm) {
            return api('/git/trees', 'POST', { base_tree: cm.tree.sha, tree: blobs });
          }).then(function (tree) {
            return api('/git/commits', 'POST', { message: BOARDS[board] + ' 새 글: ' + title + ' - ' + ((session() || {}).email || ''), tree: tree.sha, parents: [head] });
          }).then(function (c) { return api('/git/refs/heads/main', 'PATCH', { sha: c.sha }); });
        });
    }).then(function () {
      msg('');
      $('#writeForm').hidden = true; $('#done').hidden = false;
      $('#doneLink').href = '/board/' + board + '/';
      picked = []; render(); $('#writeForm').reset();
    }).catch(function (err) {
      btn.disabled = false;
      if (err.message === 'login') { showState(); msg('로그인이 끝났어요. 다시 로그인한 뒤 올리기를 눌러 주세요. (쓴 내용은 그대로 있어요)', true); $('#writeForm').hidden = false; $('#loginBox').hidden = false; return; }
      msg('올리지 못했어요: ' + err.message + ' — 잠시 후 다시 시도하거나 사무국에 알려 주세요.', true);
    });
  });
  $('#again').addEventListener('click', function () { $('#done').hidden = true; $('#writeForm').hidden = false; $('#wsubmit').disabled = false; });
})();
