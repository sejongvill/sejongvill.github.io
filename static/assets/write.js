/* 세종빌 간편 글쓰기·수정·삭제
   - 로그인: DecapBridge(이메일·비밀번호) — 관리 화면(/admin)과 같은 계정
   - 저장: DecapBridge 게이트웨이를 통해 깃허브 저장소에 글 파일과 사진을 한 번에 올림 */
(function () {
  var IDENTITY = 'https://auth.decapbridge.com/sites/4f7f1434-deb1-4975-8034-86cc185eb0b8';
  var GATEWAY = 'https://gateway.decapbridge.com/github';
  var BOARDS = { stories: '일상 이야기', notice: '공지사항', menu: '금주의 식단', schedule: '주요 일정', neighbors: '아름다운 이웃', rights: '인권존중', newsletter: '소식지' };
  var $ = function (s) { return document.querySelector(s); };
  var Q = new URLSearchParams(location.search);
  var board = BOARDS[Q.get('b')] ? Q.get('b') : 'stories';
  var editId = (Q.get('edit') || '').replace(/[^\w.-]/g, '');
  var ADMINS = ["58ef3e465ce4fd46", "cfabcb3c03dd02e3"];   // 관리자 이메일(암호화한 값)
  var editSha = null, keep = {};   // 수정할 때 그대로 둘 항목(날짜, 미리보기 그림)

  function setBoard(b) {
    board = b; $('#boardName').textContent = BOARDS[b]; $('#boardSel').value = b;
    $('#backLink').href = '/board/' + b + '/';
  }
  setBoard(board);
  $('#boardSel').addEventListener('change', function () { setBoard(this.value); if (!editId) history.replaceState(null, '', '?b=' + board); });
  if (editId) { $('#boardSel').disabled = true; $('#modeWord').textContent = '수정'; $('#wsubmit').textContent = '수정 저장하기'; $('#delBtn').hidden = false; }

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
    if (s) { $('#who').textContent = (s.email || '직원') + ' 님'; if (editId && !editSha) loadPost(); }
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

  /* ---------- 깃허브 연결 ---------- */
  function api(path, method, body) {
    return token().then(function (t) {
      return fetch(GATEWAY + path, { method: method || 'GET', headers: { Authorization: 'Bearer ' + t, 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined, cache: 'no-store' });
    }).then(function (r) {
      if (r.status === 401) { store('sv-auth', null); throw new Error('login'); }
      return r.text().then(function (x) { var j = {}; try { j = x ? JSON.parse(x) : {}; } catch (e) {} if (!r.ok) throw new Error((j.message || j.msg || ('오류 ' + r.status)) + ''); return j; });
    });
  }
  function b64(buf) { var s = '', a = new Uint8Array(buf), n = 0x8000; for (var i = 0; i < a.length; i += n) s += String.fromCharCode.apply(null, a.subarray(i, i + n)); return btoa(s); }
  function b64text(t) { return b64(new TextEncoder().encode(t).buffer); }
  function unb64(s) { var bin = atob(s.replace(/\s/g, '')), a = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i); return new TextDecoder().decode(a); }
  function mdPath(id) { return 'content/' + board + '/' + id + '.md'; }

  /* 여러 파일 변경을 한 번에 저장 (sha:null 이면 삭제) */
  function commit(entries, message) {
    var tree = [], chain = Promise.resolve();
    entries.forEach(function (en, i) {
      chain = chain.then(function () {
        if (en.remove) { tree.push({ path: en.path, mode: '100644', type: 'blob', sha: null }); return; }
        return api('/git/blobs', 'POST', { content: en.content, encoding: 'base64' }).then(function (b) {
          tree.push({ path: en.path, mode: '100644', type: 'blob', sha: b.sha }); msg('올리는 중… ' + (i + 1) + '/' + entries.length);
        });
      });
    });
    return chain.then(function () { return api('/git/refs/heads/main'); }).then(function (ref) {
      var head = ref.object.sha;
      return api('/git/commits/' + head)
        .then(function (cm) { return api('/git/trees', 'POST', { base_tree: cm.tree.sha, tree: tree }); })
        .then(function (t) { return api('/git/commits', 'POST', { message: message, tree: t.sha, parents: [head] }); })
        .then(function (c) { return api('/git/refs/heads/main', 'PATCH', { sha: c.sha }); });
    });
  }

  /* ---------- 글 파일 읽기 (수정할 때) ---------- */
  function unq(v) {
    v = (v || '').trim();
    if (v[0] === '"') { try { return JSON.parse(v); } catch (e) { return v.slice(1, -1); } }
    if (v[0] === "'") return v.slice(1, -1).replace(/''/g, "'");
    return v;
  }
  function parseFM(text) {
    var m = text.match(/^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/);
    if (!m) return { data: {}, body: text };
    var data = {}, cur = null, item = null;
    m[1].split('\n').forEach(function (ln) {
      var top = ln.match(/^([A-Za-z_]+):\s*(.*)$/);
      if (top) { cur = top[1]; item = null; data[cur] = top[2] === '' ? [] : (top[2].trim() === '[]' ? [] : unq(top[2])); return; }
      var li = ln.match(/^\s*-\s+(.*)$/);
      if (li && Array.isArray(data[cur])) {
        var kv = li[1].match(/^([A-Za-z_]+):\s*(.*)$/);
        if (kv) { item = {}; item[kv[1]] = unq(kv[2]); data[cur].push(item); } else { item = null; data[cur].push(unq(li[1])); }
        return;
      }
      var sub = ln.match(/^\s+([A-Za-z_]+):\s*(.*)$/);
      if (sub && item) item[sub[1]] = unq(sub[2]);
    });
    return { data: data, body: m[2] };
  }
  function htmlToText(h) {
    if (!/<[a-z][\s\S]*>/i.test(h)) return h.trim();
    var d = document.createElement('div');
    d.innerHTML = h.replace(/<br\s*\/?>/gi, '\n').replace(/<\/p>\s*/gi, '\n\n').replace(/<img[^>]*>/gi, '');
    return (d.textContent || '').replace(/\n{3,}/g, '\n\n').trim();
  }
  function loadPost() {
    msg('글을 불러오는 중…');
    api('/contents/' + mdPath(editId) + '?ref=main').then(function (f) {
      editSha = f.sha;
      var p = parseFM(unb64(f.content || ''));
      $('#wtitle').value = p.data.title || '';
      $('#wbody').value = htmlToText(p.body || '');
      keep = { date: p.data.date, previews: p.data.previews || [], author: p.data.author || '' };
      (p.data.images || []).forEach(function (src) { if (src) picked.push({ old: src, url: src }); });
      (p.data.files || []).forEach(function (x) { if (typeof x === 'string') x = { file: x }; if (x && x.file) oldFiles.push({ name: x.name || x.file.split('/').pop(), file: x.file }); });
      render(); renderFiles(); msg('');
      return who().then(function (id) {
        if (ADMINS.indexOf(id) >= 0 || (keep.author && keep.author === id)) return;
        editSha = null;
        $('#wsubmit').disabled = true; $('#delBtn').hidden = true;
        [].forEach.call($('#writeForm').querySelectorAll('input,textarea,select'), function (x) { if (x.id !== 'logout') x.disabled = true; });
        msg('본인이 쓴 글만 수정·삭제할 수 있어요. 고칠 내용이 있으면 관리자(사무국)에 요청해 주세요.', true);
      });
    }).catch(function (err) {
      if (err.message === 'login') { showState(); return; }
      msg('글을 불러오지 못했어요: ' + err.message, true);
    });
  }

  /* ---------- 사진·첨부파일 ---------- */
  var picked = [], oldFiles = [];
  function render() {
    var box = $('#thumbs'); box.innerHTML = '';
    picked.forEach(function (p, i) {
      var d = document.createElement('div'); d.className = 'th';
      d.innerHTML = '<img alt=""><button type="button" aria-label="사진 빼기">×</button>' + (i === 0 ? '<span>대표</span>' : '');
      d.querySelector('img').src = p.url;
      d.querySelector('button').onclick = function () { if (p.file) URL.revokeObjectURL(p.url); picked.splice(i, 1); render(); };
      box.appendChild(d);
    });
    $('#pcount').textContent = picked.length ? picked.length + '장 (첫 번째 사진이 대표 사진)' : '';
  }
  function renderFiles() {
    var box = $('#oldFiles'); box.innerHTML = '';
    oldFiles.forEach(function (f, i) {
      var li = document.createElement('li');
      li.innerHTML = '<span></span> <button type="button" class="more" style="border:0">빼기</button>';
      li.querySelector('span').textContent = '📎 ' + f.name;
      li.querySelector('button').onclick = function () { oldFiles.splice(i, 1); renderFiles(); };
      box.appendChild(li);
    });
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
  function who() {   // 로그인한 사람의 이메일을 알아볼 수 없게 바꾼 값 (글쓴이 확인용)
    var em = ((session() || {}).email || '').trim().toLowerCase();
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(em)).then(function (b) {
      return [].map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('').slice(0, 16);
    });
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function yq(s) { return JSON.stringify(s); }

  /* ---------- 저장 ---------- */
  $('#writeForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var title = $('#wtitle').value.trim(), body = $('#wbody').value.trim();
    if (!title) { msg('제목을 적어 주세요.', true); return; }
    if (editId && !editSha) { msg('글을 아직 불러오지 못했어요. 잠시 후 다시 눌러 주세요.', true); return; }
    var btn = $('#wsubmit'); btn.disabled = true;
    var now = new Date(), stamp = '' + now.getFullYear() + pad(now.getMonth() + 1) + pad(now.getDate()) + pad(now.getHours()) + pad(now.getMinutes()) + pad(now.getSeconds());
    var id = editId || stamp;
    var date = keep.date || (now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate()) + ' ' + pad(now.getHours()) + ':' + pad(now.getMinutes()));
    var newFiles = [].slice.call($('#attach').files || []);
    var entries = [], imgPaths = [], attPaths = oldFiles.slice();
    msg('사진 준비 중…');
    var chain = Promise.resolve(), n = 0;
    picked.forEach(function (p) {
      if (p.old) { chain = chain.then(function () { imgPaths.push(p.old); }); return; }
      chain = chain.then(function () { return shrink(p.file); }).then(function (r) {
        n++; var path = 'files/uploads/' + stamp + '-' + n + '.' + r.ext;
        imgPaths.push('/' + path); entries.push({ path: 'static/' + path, content: b64(r.buf) });
        msg('사진 준비 중… ' + n + '장');
      });
    });
    newFiles.forEach(function (f, i) {
      chain = chain.then(function () { return f.arrayBuffer(); }).then(function (buf) {
        var ext = (f.name.split('.').pop() || 'bin').toLowerCase(), path = 'files/uploads/' + stamp + '-file' + (i + 1) + '.' + ext;
        attPaths.push({ name: f.name, file: '/' + path }); entries.push({ path: 'static/' + path, content: b64(buf) });
      });
    });
    chain.then(function () { return editId ? keep.author : who(); }).then(function (author) {
      var fm = '---\ntitle: ' + yq(title) + '\ndate: ' + date + '\n';
      if (author) fm += 'author: ' + author + '\n';
      if (imgPaths.length) fm += 'images:\n' + imgPaths.map(function (x) { return '- ' + x; }).join('\n') + '\n';
      if (attPaths.length) fm += 'files:\n' + attPaths.map(function (x) { return '- name: ' + yq(x.name) + '\n  file: ' + x.file; }).join('\n') + '\n';
      if (keep.previews && keep.previews.length) fm += 'previews:\n' + keep.previews.map(function (x) { return '- ' + x; }).join('\n') + '\n';
      fm += '---\n' + body + '\n';
      entries.push({ path: mdPath(id), content: b64text(fm) });
      msg('올리는 중… 잠시만 기다려 주세요.');
      return commit(entries, BOARDS[board] + (editId ? ' 글 수정: ' : ' 새 글: ') + title);
    }).then(function () { finish(editId ? '수정했어요! ✏️' : '올렸어요! 🎉'); })
      .catch(fail);
  });

  /* ---------- 삭제 ---------- */
  $('#delBtn').addEventListener('click', function () {
    if (!editId || !editSha) return;
    if (!confirm('이 글을 삭제할까요? 삭제하면 홈페이지에서 사라져요.')) return;
    $('#delBtn').disabled = true; $('#wsubmit').disabled = true;
    msg('삭제하는 중…');
    commit([{ path: mdPath(editId), remove: true }], BOARDS[board] + ' 글 삭제: ' + $('#wtitle').value.trim())
      .then(function () { finish('삭제했어요.'); }).catch(fail);
  });

  function finish(t) {
    msg(''); $('#writeForm').hidden = true; $('#done').hidden = false;
    $('#doneTitle').textContent = t; $('#doneLink').href = '/board/' + board + '/';
    $('#again').hidden = !!editId;
  }
  function fail(err) {
    $('#wsubmit').disabled = false; $('#delBtn').disabled = false;
    if (err.message === 'login') { showState(); $('#writeForm').hidden = false; $('#loginBox').hidden = false; msg('로그인이 끝났어요. 다시 로그인한 뒤 눌러 주세요. (쓴 내용은 그대로 있어요)', true); return; }
    msg('저장하지 못했어요: ' + err.message + ' — 잠시 후 다시 시도하거나 사무국에 알려 주세요.', true);
  }
  $('#again').addEventListener('click', function () {
    $('#done').hidden = true; $('#writeForm').hidden = false; $('#wsubmit').disabled = false;
    $('#writeForm').reset(); picked = []; oldFiles = []; render(); renderFiles(); setBoard(board);
  });

  showState();
})();
