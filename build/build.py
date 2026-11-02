"""세종빌 홈페이지 생성기 — content/ 의 글 파일과 static/ 을 읽어 _site/ 를 만든다.
깃허브 Actions가 글이 올라올 때마다 자동으로 실행한다."""
import os, shutil, html, re, math, glob, hashlib
import yaml, markdown
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, '_site')
E = html.escape
shutil.rmtree(SITE, ignore_errors=True)
shutil.copytree(os.path.join(ROOT, 'static'), SITE)
shutil.copytree(os.path.join(ROOT, 'admin'), os.path.join(SITE, 'admin'))
os.makedirs(f'{SITE}/files/thumb', exist_ok=True)

def make_thumb(path):
    """목록 카드용 작은 그림. 기존 사진은 t_ 파일이 있고, 새로 올린 사진은 여기서 만든다."""
    name = os.path.basename(path)
    if path.startswith('/files/img/') and os.path.exists(f'{SITE}/files/img/t_{name}'):
        return f'/files/img/t_{name}'
    src = SITE + path
    if not os.path.exists(src): return path
    out = f'/files/thumb/{hashlib.md5(path.encode()).hexdigest()[:12]}.jpg'
    try:
        im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
        ImageOps.fit(im, (640, 480), Image.LANCZOS).save(SITE + out, quality=78, optimize=True)
        return out
    except Exception:
        return path

# 직원이 올린 큰 사진은 홈페이지용으로 줄인다 (원본은 저장소에 그대로 남음)
for f in glob.glob(f'{SITE}/files/uploads/**/*', recursive=True):
    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        try:
            im = ImageOps.exif_transpose(Image.open(f))
            if max(im.size) > 1600 or os.path.getsize(f) > 900_000:
                im.thumbnail((1600, 1600), Image.LANCZOS)
                if f.lower().endswith('.png') and im.mode in ('RGBA', 'P'):
                    im.save(f, optimize=True)
                else:
                    im.convert('RGB').save(f, quality=82, optimize=True, progressive=True, format='JPEG')
        except Exception as e:
            print('사진 줄이기 실패', f, e)

BOARDS = ['notice', 'stories', 'schedule', 'neighbors', 'rights', 'newsletter', 'menu']
P = {}
for key in BOARDS:
    posts = []
    for f in glob.glob(os.path.join(ROOT, 'content', key, '*.md')):
        raw = open(f, encoding='utf8').read()
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', raw, re.S)
        if not m: continue
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get('draft'): continue
        body = m.group(2).strip()
        if not re.search(r'<(p|br|img|div|table)\b', body):
            body = markdown.markdown(body, extensions=['nl2br', 'tables'])
        d = str(fm.get('date', ''))
        files = []
        for x in fm.get('files') or []:
            if isinstance(x, str): x = {'file': x}
            if x and x.get('file'):
                files.append({'file': x['file'], 'name': x.get('name') or os.path.basename(x['file'])})
        imgs = [x for x in (fm.get('images') or []) if x]
        text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', body))).strip()
        posts.append({'id': os.path.splitext(os.path.basename(f))[0], 'title': str(fm.get('title', '제목 없음')),
                      'date': d[:10], 'sort': d, 'body': body, 'text': text[:160], 'images': imgs, 'files': files,
                      'previews': fm.get('previews') or []})
    P[key] = sorted(posts, key=lambda p: p['sort'], reverse=True)
    for n, p in enumerate(reversed(P[key]), 1): p['no'] = n

FORM_ID = 'xnppoaez'  # 폼스프리 양식 ID (예: 'xyzabcd'). 비어 있으면 신청 버튼이 잠김
TEL = '044-864-3015'
ADDR = '세종특별자치시 전의면 양지편길 13-6 (양곡리)'
ACCTS = [('사회복지법인 예일', '농협', '351-0717-260953'), ('사회복지법인 예일', '국민', '455801-04-351341'), ('세종빌', '농협', '419-01-152858')]

ICON = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="i-phone" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></symbol>
<symbol id="i-home" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M3 10.5 12 3l9 7.5V21H3z M9 21v-6h6v6"/></symbol>
<symbol id="i-heart" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/></symbol>
<symbol id="i-hand" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M16 11V5a2 2 0 0 0-4 0v5M12 10V3a2 2 0 0 0-4 0v8M8 10.5V6a2 2 0 0 0-4 0v8a8 8 0 0 0 16 0v-4a2 2 0 0 0-4 0"/></symbol>
<symbol id="i-pin" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/></symbol>
<symbol id="i-arrow" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M7 17 17 7M8 7h9v9"/></symbol>
<symbol id="i-file" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M14 3H6v18h12V7z M14 3v4h4"/></symbol>
</defs></svg>'''

NAV = [
    ('세종빌 소개', '/about/greeting.html', [('인사말', '/about/greeting.html'), ('법인 소개', '/about/corp.html'), ('미션·비전', '/about/vision.html'),
                                        ('연혁', '/about/history.html'), ('조직·현황', '/about/org.html'), ('오시는 길', '/about/location.html')]),
    ('우리의 일상', '/days/services.html', [('주요 서비스', '/days/services.html'), ('일상 이야기', '/board/stories/'), ('금주의 식단', '/board/menu/'), ('주요 일정', '/board/schedule/')]),
    ('입주 안내', '/admission.html', [('입주 조건·절차', '/admission.html')]),
    ('함께하기', '/together/support.html', [('후원 안내', '/together/support.html'), ('자원봉사 안내', '/together/volunteer.html'),
                                       ('아름다운 이웃', '/board/neighbors/'), ('문의하기', '/together/contact.html')]),
    ('알림·정보공개', '/board/notice/', [('공지사항', '/board/notice/'), ('정보공개', '/disclosure.html'), ('인권존중', '/board/rights/'), ('소식지', '/board/newsletter/')]),
]
BOARD_META = {
    'notice': ('공지사항', 4), 'stories': ('일상 이야기', 1), 'menu': ('금주의 식단', 1), 'schedule': ('주요 일정', 1),
    'neighbors': ('아름다운 이웃', 3), 'rights': ('인권존중', 4), 'newsletter': ('소식지', 4),
}

def page(title, body, sec=None, desc='지적장애인 거주시설 세종빌 — 서로를 존중하고 품어주고 사랑하는 행복한 보금자리'):
    menu = ''
    for i, (name, href, subs) in enumerate(NAV):
        cur = ' aria-current="page"' if sec == i else ''
        menu += f'<li><a href="{href}"{cur}>{name}</a><ul>' + ''.join(f'<li><a href="{h}">{n}</a></li>' for n, h in subs) + '</ul></li>'
    t = f'{title} | 세종빌' if title else '세종빌 | 사회복지법인 예일'
    allmenu = ''.join(f'<div class="am-col"><a class="am-h" href="{h}">{n}</a><ul>' + ''.join(f'<li><a href="{sh}">{sn}</a></li>' for sn, sh in subs) + '</ul></div>' for n, h, subs in NAV)
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(t)}</title><meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(t)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="/assets/img/group.jpg">
<link rel="icon" href="/assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script>try{{if(localStorage.getItem('theme')==='dark')document.documentElement.dataset.theme='dark';var f={{xs:.9,s:1,m:1.12,l:1.25,xl:1.4}}[localStorage.getItem('fs')];if(f)document.documentElement.style.setProperty('--fs',f)}}catch(e){{}}</script></head><body>
{ICON}<a class="skip" href="#main">본문 바로가기</a>
<div class="util"><div class="wrap"><span>사회복지법인 예일 · 지적장애인 거주시설 세종빌</span>
<div class="tools"><div class="fsz" role="group" aria-label="글자 크기">글자 <button data-fs="xs" aria-label="작게" style="font-size:.7rem">가</button><button data-fs="s" aria-label="보통">가</button><button data-fs="m" aria-label="크게" style="font-size:.88rem">가</button><button data-fs="l" aria-label="더 크게" style="font-size:.98rem">가</button><button data-fs="xl" aria-label="가장 크게" style="font-size:1.08rem">가</button></div><button class="theme" type="button" aria-pressed="false">🌙 어둡게</button></div></div></div></div>
<header class="gnb"><div class="wrap"><a class="brand" href="/"><img src="/assets/img/logo.png" alt="사회복지법인 예일 세종빌" width="145" height="45"></a>
<button class="burger" aria-label="메뉴 열기" aria-expanded="false"><span></span></button>
<nav aria-label="주 메뉴"><ul class="menu">{menu}</ul></nav>
<a class="btn-call" href="tel:{TEL}"><svg class="ico"><use href="#i-phone"/></svg>{TEL}</a><button class="allmenu-btn" type="button" aria-expanded="false" aria-controls="allmenu"><span class="bars"></span>전체메뉴</button></div>
<div class="allmenu" id="allmenu" hidden><div class="wrap">{allmenu}<button class="allmenu-close" type="button">닫기 ✕</button></div></div></header>
<main id="main">{body}</main>
<footer><div class="wrap relwrap"><div class="relsites"><span>관련 기관</span><a href="https://www.sejong.go.kr" target="_blank" rel="noopener" title="새 창 열림">세종특별자치시청 (감독기관) ↗</a></div></div><div class="wrap"><img src="/assets/img/flogo.png" alt="세종빌" width="135" height="45" style="opacity:.85">
<div><b>세종빌</b> · 시설장 정원용 · 고유번호 307-82-09984<br>{ADDR}<br>TEL {TEL} · FAX 044-864-3016 · yengi363@naver.com<br>
<a href="/privacy.html">개인정보처리방침</a> · <a href="/join.html">직원 회원가입 신청</a> · <a href="/write/">직원 글쓰기</a> · Copyright 세종빌. All rights reserved.</div></div></footer>
<div class="callbar"><a href="tel:{TEL}">📞 전화 문의</a><a href="/about/location.html">오시는 길</a></div>
<script src="/assets/site.js"></script></body></html>'''

def write(path, s):
    full = f'{SITE}{path}'
    if full.endswith('/'): full += 'index.html'
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf8').write(s)

def subpage(sec, title, crumb, body, tabs_key=None):
    tabs = ''
    subs = NAV[sec][2]
    if len(subs) > 1:
        tabs = '<nav class="tabs" aria-label="하위 메뉴">' + ''.join(
            f'<a href="{h}"{" aria-current=page" if n == (tabs_key or title) else ""}>{n}</a>' for n, h in subs) + '</nav>'
    return f'''<div class="subvis"><div class="wrap"><div class="crumb">홈 · {NAV[sec][0]} · {crumb}</div><h1>{title}</h1>{tabs}</div></div>
<div class="content"><div class="wrap">{body}</div></div>'''

def accts(cls=''):
    return ''.join(f'<div class="acct"><div><small>{a} · {b}</small><b>{n}</b></div><button class="copy" data-copy="{n}">계좌 복사</button></div>' for a, b, n in ACCTS)

def thumb(p):
    return make_thumb(p['images'][0]) if p['images'] else None

def fmt(d): return d.replace('-', '. ') + '.' if d else ''

def ext(f): return os.path.splitext(f)[1][1:].upper() or 'FILE'

# ---------- 메인 ----------
stories = P['stories'][:9]
def first_img(p):
    for x in p['images']: return x
    for x in p['previews']: return x
    for f in p['files']:
        if os.path.splitext(f['file'])[1].lower() in ('.jpg', '.jpeg', '.png', '.webp'): return f['file']
    return None
def board_slides(key, label, n=2):
    out = []
    for p in P[key]:
        im = first_img(p)
        if im: out.append((label, key, p, im))
        if len(out) >= n: break
    return out
bslides = board_slides('schedule', '주요일정', 1) + board_slides('menu', '금주의 식단', 1) + board_slides('schedule', '주요일정', 2)[1:] + board_slides('menu', '금주의 식단', 2)[1:]
board_html = ''.join(f'''<a class="bs{" on" if i == 0 else ""}" href="/board/{k}/{p["id"]}.html"{" hidden" if i else ""}><div class="bs-img"><img src="{im}" alt="{E(p["title"])}" loading="lazy"></div>
<div class="bs-cap"><span class="chip{" g" if k == "menu" else ""}">{lab}</span><b>{E(p["title"])}</b><time>{p["date"].replace("-", ". ")}.</time></div></a>''' for i, (lab, k, p, im) in enumerate(bslides))
board_panel = f'''<aside class="board" aria-label="알림판" aria-roledescription="carousel">
<div class="board-head"><h3>알림판</h3><div class="bctl"><span class="bcount"><b>1</b> / {len(bslides)}</span><button class="bprev" type="button" aria-label="이전 알림">‹</button><button class="bpause" type="button" aria-label="알림 넘기기 멈춤">❚❚</button><button class="bnext" type="button" aria-label="다음 알림">›</button></div></div>
<div class="board-body">{board_html}</div>
<div class="board-links"><a href="/board/schedule/">일정 전체</a><a href="/board/menu/">식단 전체</a></div></aside>'''
ncards = ''.join(f'''<a class="card" href="/board/neighbors/{p["id"]}.html"><img src="{thumb(p) or "/assets/img/group.jpg"}" alt="" loading="lazy">
<div class="cap"><small>{fmt(p["date"])}</small><b>{E(p["title"])}</b></div></a>''' for p in P['neighbors'][:9])
cards = ''.join(f'''<a class="card" href="/board/stories/{p["id"]}.html"><img src="{thumb(p) or "/assets/img/group.jpg"}" alt="" loading="lazy">
<div class="cap"><small>{fmt(p["date"])}</small><b>{E(p["title"])}</b></div></a>''' for p in stories)
def cat(t):
    for k, c in [('채용', '채용'), ('합격', '채용'), ('예산', '예산'), ('결산', '결산'), ('이사회', '회의'), ('운영위원회', '회의'), ('후원금', '후원'), ('수의계약', '계약'), ('공고', '공고'), ('결과', '공고')]:
        if k in t: return c
    return '알림'
notices = ''.join(f'<li><a href="/board/notice/{p["id"]}.html"><span class="chip{" r" if cat(p["title"]) == "채용" else ""}">{cat(p["title"])}</span><span class="tt">{E(p["title"])}</span><time>{p["date"][5:].replace("-", ".")}</time></a></li>' for p in P['notice'][:5])
DISC_KEYS = [('예산', '예산·결산'), ('결산', '예산·결산'), ('이사회', '회의록'), ('운영위원회', '회의록'), ('후원금', '후원금'), ('수의계약', '계약')]
def disc_cat(t):
    for k, c in DISC_KEYS:
        if k in t: return c
disc = [p for p in P['notice'] if disc_cat(p['title'])]
docs = ''.join(f'<a class="doc" href="/board/notice/{p["id"]}.html"><span class="pdf">{ext(p["files"][0]["file"]) if p["files"] else "글"}</span><div>{E(p["title"][:26])}<small>{disc_cat(p["title"])} · {p["date"]}</small></div></a>' for p in disc[:4])


# ---------- 메인: 소식 탭 / 사진 탭 ----------
def news_kind(key, p):
    if key == 'notice':
        return '정보공개' if disc_cat(p['title']) else '공지사항'
    return {'rights': '인권존중', 'newsletter': '소식지', 'schedule': '주요일정', 'menu': '금주의 식단'}[key]
NEWS_TABS = [('전체', None, '/board/notice/'), ('공지사항', '공지사항', '/board/notice/'), ('정보공개', '정보공개', '/disclosure.html'),
             ('인권존중', '인권존중', '/board/rights/'), ('소식지', '소식지', '/board/newsletter/')]
allnews = sorted([(news_kind(k, p), k, p) for k in ('notice', 'rights', 'newsletter') for p in P[k]], key=lambda x: x[2]['sort'], reverse=True)
def ncard(kind, k, p):
    return (f'<a class="ncard" href="/board/{k}/{p["id"]}.html"><span class="chip{" r" if kind in ("공지사항", "정보공개") else ""}">{kind}</span>'
            f'<b>{E(p["title"])}</b><time>{p["date"].replace("-", ". ")}.</time></a>')
def tabset(name, tabs, panes):
    bar = f'<div class="tabbar" role="tablist" aria-label="{name}">' + ''.join(
        f'<button role="tab" type="button" aria-selected="{"true" if n == 0 else "false"}" data-more="{t[2]}">{t[0]}</button>' for n, t in enumerate(tabs)) + '</div>'
    return bar + ''.join(f'<div class="tp" role="tabpanel"{" hidden" if n else ""}>{pane}</div>' for n, pane in enumerate(panes))
news_panes = []
for label, kind, more in NEWS_TABS:
    items = [x for x in allnews if kind is None or x[0] == kind][:6]
    news_panes.append('<div class="ngrid">' + (''.join(ncard(*x) for x in items) or '<p class="note">아직 글이 없어요.</p>') + '</div>')
news_tabs = tabset('소식 분류', NEWS_TABS, news_panes)
PHOTO_TABS = [('전체', None, '/board/stories/'), ('일상 이야기', 'stories', '/board/stories/'), ('아름다운 이웃', 'neighbors', '/board/neighbors/')]
allphoto = sorted([(k, p) for k in ('stories', 'neighbors') for p in P[k]], key=lambda x: x[1]['sort'], reverse=True)
def pcard(k, p):
    return (f'<a class="card" href="/board/{k}/{p["id"]}.html"><img src="{thumb(p) or "/assets/img/group.jpg"}" alt="" loading="lazy">'
            f'<div class="cap"><small>{BOARD_META[k][0]} · {fmt(p["date"])}</small><b>{E(p["title"])}</b></div></a>')
photo_panes = ['<div class="carousel"><div class="cards row3">' + ''.join([pcard(k, p) for k, p in allphoto if b is None or k == b][:9]) + '</div></div>' for _, b, _ in PHOTO_TABS]
photo_tabs = tabset('사진 분류', PHOTO_TABS, photo_panes)

home = f'''
<section class="hero2"><div class="wrap"><div class="frame slides" aria-roledescription="carousel" aria-label="세종빌 사진"><figure class="sl on"><img class="bg" src="/assets/img/group.jpg" alt="" aria-hidden="true"><img class="fg" src="/assets/img/group.jpg" alt="세종빌 가족 단체사진" style="object-position:center 62%" fetchpriority=high></figure><figure class="sl"><img class="bg" src="/assets/img/poolgroup.jpg" alt="" aria-hidden="true" loading=lazy><img class="fg" src="/assets/img/poolgroup.jpg" alt="여름캠프 단체사진" style="object-position:center 55%" loading=lazy></figure><figure class="sl"><img class="bg" src="/assets/img/hero_pool.jpg" alt="" aria-hidden="true" loading=lazy><img class="fg" src="/assets/img/hero_pool.jpg" alt="여름캠프 물놀이" style="object-position:center 60%" loading=lazy></figure><figure class="sl"><img class="bg" src="/assets/img/bubble.jpg" alt="" aria-hidden="true" loading=lazy><img class="fg" src="/assets/img/bubble.jpg" alt="버블쇼를 보는 세종빌 가족들" style="object-position:center 50%" loading=lazy></figure><div class="sctl"><button class="sprev" type="button" aria-label="이전 사진">‹</button><div class="dots" role="tablist"></div><button class="spause" type="button" aria-label="사진 넘기기 멈춤">❚❚</button><button class="snext" type="button" aria-label="다음 사진">›</button></div>
<div class="glass"><div class="eyebrow">SEJONGVILL · 2003년부터 함께</div>
<h1>서로를 존중하고<br>품어주고 사랑하는<br><em>행복한 보금자리</em></h1>
<p class="lead">세종빌은 이용자 한 분 한 분이 저마다의 속도로 배우고, 쉬고, 웃으며 함께 살아가는 곳입니다.</p>
<div class="cta"><a class="btn red" href="/about/greeting.html">세종빌 둘러보기 <svg class="ico"><use href="#i-arrow"/></svg></a><a class="btn line" href="/together/support.html">후원으로 함께하기</a></div></div>
</div></div></section>
<nav class="quick" aria-label="바로가기"><div class="wrap">
<a href="/admission.html"><div class="qi"><svg class="ico"><use href="#i-home"/></svg></div><div><b>입주 상담</b><small>조건 · 절차 · 서류</small></div></a>
<a href="/together/support.html"><div class="qi"><svg class="ico"><use href="#i-heart"/></svg></div><div><b>후원 안내</b><small>계좌 복사 한 번으로</small></div></a>
<a href="/together/volunteer.html"><div class="qi"><svg class="ico"><use href="#i-hand"/></svg></div><div><b>자원봉사</b><small>신청 · 활동 안내</small></div></a>
<a href="/about/location.html"><div class="qi"><svg class="ico"><use href="#i-pin"/></svg></div><div><b>오시는 길</b><small>전의면 양지편길 13-6</small></div></a>
</div></nav>
<section class="blk"><div class="wrap about">
<div><div class="eyebrow">ABOUT</div><h2 class="t">한 사회라는 숲속에서<br>저마다의 빛깔로 자라는 사람들</h2>
<p>같은 숲, 같은 햇볕 아래에서도 나무마다 자라는 모습은 다릅니다. 세종빌은 이용자 한 분 한 분의 욕구와 속도를 존중하며, 사랑과 봉사·섬김과 나눔으로 사람 중심의 가치를 실현합니다.</p>
<div class="stats"><div><b>2003</b><span>연기사랑마을로 시작</span></div><div><b>30<small>명</small></b><span>함께 사는 이용자</span></div><div><b>22<small>명</small></b><span>함께 일하는 직원</span></div><div><b>2026</b><span>새 단장 완료</span></div></div></div>
<div class="aslides" aria-roledescription="carousel" aria-label="세종빌 일상 사진"><img class="as on" src="/assets/img/museum.jpg" alt="박물관 나들이 단체사진" style="object-position:center 45%" loading="lazy"><img class="as" src="/assets/img/cook.jpg" alt="함께 만든 음식 앞에서" style="object-position:center 40%" loading="lazy"><img class="as" src="/assets/img/sea.jpg" alt="바닷가 나들이" style="object-position:center 60%" loading="lazy"><img class="as" src="/assets/img/pine.jpg" alt="소나무 아래에서" style="object-position:center 50%" loading="lazy"><img class="as" src="/assets/img/lake.jpg" alt="호숫가 산책" style="object-position:center 70%" loading="lazy"><div class="adots" role="tablist"></div></div></div></section>
<section class="blk"><div class="wrap">
<div class="sec-head"><div><div class="eyebrow">NEWS</div><h2 class="t">소식</h2></div><a class="more tabmore" href="/board/notice/">더 보기 <svg class="ico"><use href="#i-arrow"/></svg></a></div>
<div class="newsrow"><div class="newsmain">{news_tabs}</div>{board_panel}</div></div></section>
<section class="blk bg-cream photonews"><div class="wrap">
<div class="sec-head"><div><div class="eyebrow">PHOTO</div><h2 class="t">사진으로 보는 세종빌</h2></div>
<div class="headr"><div class="cnav"><button class="cprev" type="button" aria-label="이전 사진">‹</button><button class="cnext" type="button" aria-label="다음 사진">›</button></div><a class="more tabmore" href="/board/stories/">더 보기 <svg class="ico"><use href="#i-arrow"/></svg></a></div></div>
{photo_tabs}</div></section>
<section class="band"><img src="/assets/img/campgroup.jpg" alt="" loading="lazy" style="object-position:center 45%">
<div class="wrap"><div class="eyebrow" style="color:#ffd9d9">TOGETHER</div><p class="big">같은 숲, 같은 햇볕 아래<br>저마다의 빛깔로</p>
<p style="margin-top:14px;opacity:.9">세종빌 가족들의 꿈과 희망이 가득한 이야기를 만나보세요.</p></div></section>
<div class="wrap"><div class="support">
<div><div class="eyebrow" style="color:#f08a8f">WITH US</div><h2>여러분의 작은 정성이<br>세종빌에 큰 힘이 됩니다</h2><p>재정후원 · 저금통후원 · 1:1 결연후원<br>문의 행정지원팀 {TEL}</p></div>
<div>{accts()}</div></div></div>'''
write('/index.html', page('', home))

# ---------- 소개 ----------
greet = '''<div class="split"><div class="side"><img src="/assets/img/director.jpg" alt="원장 정원용" loading="lazy"></div><div class="prose">
<p class="quote">안녕하십니까!<br>세종빌 홈페이지를 방문해주셔서 감사합니다.</p>
<p>가끔 산을 오를 때나 숲길을 거닐 때 수많은 꽃과 풀, 나무들을 만날 수가 있습니다. 그 자연과 벗할 때 자람의 정도, 빛깔, 모양새들이 다 조금씩 달라 각자의 자태를 아름답게 드러내고 있는 것을 알 수 있습니다. 같은 숲속에서 같은 토양을 바탕으로 같은 공기 같은 햇볕을 머금고 자라나지만 조금씩 저마다 다르게 자신의 모습을 드러내며 향기들을 내고 있습니다.</p>
<p>저희는 감히 우리 세종빌의 가족들을 한 사회라는 숲속의 사람들 나무라고 말하고 싶습니다. 우리들은 한 사회라는 자그마한 숲속에서 자신들의 빛과 향기를 뿜어내기 위해 오늘도 노력하며 자신들의 꿈을 향해 행복을 위해 공부하고 치료받고 훈련되어 건강하고 아름다운 축복의 숲속에서 행복하게 살아가고 있습니다.</p>
<p>그리고 종사자 모두의 인내와 사랑과 정성을 함께 담아 너랑 나랑 어우러 한마음으로 아름다운 행복한 숲을 이루어 가는데 쉼 없는 정진을 서로가 서로를 응원하여 주시는 여러분의 모두가 자랑스럽습니다.</p>
<p>날마다 시끌벅적 알콩달콩 오순도순 살아가는 우리 세종빌 가족들의 꿈과 희망이 가득한 이 공간을 통해 저희의 삶을 그동안 지켜보시고 동참하여 주신 후원회원님들의 정성으로 보내주신 성원과 변함없으신 사랑으로 아름다운 숲을 이루었습니다. 참 감사합니다.</p>
<p class="sign">원장 정원용 / 세종빌 가족 일동</p></div></div>'''
write('/about/greeting.html', page('인사말', subpage(0, '인사말', '인사말', greet), 0))

corp = '''<div class="split"><div class="side"><img src="/assets/img/chairman.jpg" alt="이사장 정태춘" loading="lazy" style="max-width:220px"></div><div class="prose">
<p class="quote">중증장애인을 위한 사랑의 공동체 세종빌</p>
<p>세종빌 가족 여러분 감사합니다. 입소하신 장애인 가족 여러분을 위해 늘 최선을 다하겠습니다.</p>
<p>하나님의 은혜와 사랑으로 지금까지 축복된 길로 인도하신 무한하신 은총에 먼저 감사드립니다. 오직 작은 믿음으로 감히 부족한 제가 사회복지법인 예일 이사장으로 취임하여 외롭고 소외된 중증장애인들을 모시고 동고동락하며 "施惠與人恩返于己"(남을 잘되게 하면 나도 잘 된다)의 생활지표를 가지고, 무엇보다 전 임직원이 모두 다 솔선수범하는 마음을 아끼지 않는 희생과 봉사정신으로 맡은 바 사명을 다하여 주심으로 오늘까지 세종빌(세종복지원)이 거주장애인과 종사자가 함께 어우러져 행복한 중증장애인 사랑의 공동체로 발전할 수 있었음을 새삼 감사드립니다.</p>
<p>앞으로도 물심양면으로 입소하신 장애인 가족이 평안하고 행복하고 만족할 때까지 최선의 노력을 다하겠습니다.</p>
<p>존경하는 후원 회원님과 사랑하는 임직원 여러분! 아무쪼록 항상 건강하시고 하시는 일마다 번창하시기를 바라며, 언제나 격의 없는 충고와 질타를 주시면 청령하는 자세로 우리 임직원 모두 함께 "주님 사랑, 사람 사랑"의 원훈으로 일치단결하여 세종빌이 21세기 신모델의 최우수 중증장애인시설로 창출하는 데 지혜와 사랑을 함께 모아 더 일하고 더 사랑하고 더 봉사하는 부단한 노력을 경주합시다.</p>
<p>끝으로 후원 회원님의 사랑과 직원 여러분들의 노고에 한번 더 감사드리며 하나님의 은혜와 축복이 함께 하시기를 축원합니다.</p>
<p class="sign">사회복지법인 예일 이사장 정태춘</p>
<h3>설립목적</h3>
<p>장애인복지법의 규정에 의한 장애인복지사업을 수행함으로써 기독교 정신을 바탕으로 사랑과 봉사, 섬김과 나눔으로 소외된 이웃들에게 더 나은 삶의 기회를 제공하고 더 나아가 사회복지 증진과 발전에 기여함을 목적으로 합니다.</p></div></div>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:56px 0 16px">기본현황</h3>
<div class="tbl-scroll"><table class="tb"><tr><th>시설명</th><td>세종빌</td><th>사업종별</th><td>지적장애인 거주시설</td></tr>
<tr><th>소재지</th><td>세종특별자치시 전의면 양지편길 13-6</td><th>설립일자</th><td>2014. 03. 13.</td></tr></table></div>
<div class="grid-cards" style="margin-top:28px">
<div class="box"><h4>재활사업 · 교육사업</h4><p>안락하고 쾌적한 환경을 제공하고 스스로 장애를 극복할 수 있도록 지원합니다. 음악, 미술, 놀이, 취미, 운동 등 다양한 학습·여가활동으로 새로운 능력 개발의 기회를 드립니다.</p></div>
<div class="box"><h4>의료재활사업</h4><p>의료진단, 작업치료 등 의료적 서비스로 결손 기능을 회복하여 퇴행과 변형을 최소화하고 심리적·사회적 안정을 돕습니다.</p></div>
<div class="box"><h4>지역홍보 · 사회참여</h4><p>자원봉사자·후원자와 함께 교육과 훈련에 참여하고, 지역 환경미화와 나눔 행사로 장애인에 대한 인식을 개선합니다.</p></div></div>'''
write('/about/corp.html', page('법인 소개', subpage(0, '법인 소개', '법인 소개', corp), 0))

vision = '''<div class="grid-cards" style="margin-top:0">
<div class="box" style="background:var(--ink);color:#fff"><div class="eyebrow" style="color:#f08a8f">MISSION</div><p style="color:#fff;font-family:var(--serif);font-size:1.5rem;line-height:1.5;margin-top:10px;font-weight:700">사랑과 봉사, 섬김과 나눔으로<br>사람 중심의 가치 실현</p></div>
<div class="box"><div class="eyebrow">VISION</div><p style="font-family:var(--serif);font-size:1.5rem;line-height:1.5;margin-top:10px;font-weight:700;color:var(--ink)">2030년까지 전국 장애인 거주시설<br>5% 선도시설</p></div></div>
<div class="grid-cards">
<div class="box"><span class="num">01</span><h4>네트워크 활성화</h4><p>지역사회 네트워크 허브기관</p></div>
<div class="box"><span class="num">02</span><h4>시설 브랜드 강화</h4><p>전문성에 기반한 특화사업 개발</p></div>
<div class="box"><span class="num">03</span><h4>운영 시스템 구축</h4><p>과학적 시설경영 시스템 구축, 윤리경영 도입</p></div>
<div class="box"><span class="num">04</span><h4>사회공헌</h4><p>지역사회 기여 실현</p></div></div>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:56px 0 16px">기본운영방침 · 슬로건</h3>
<div class="grid-cards" style="margin-top:0"><div class="box"><h4>함께 만들고 함께 나누는 세종빌</h4><p>기본운영방침</p></div><div class="box"><h4>함께 배려하는 세종빌</h4><p>슬로건</p></div></div>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:56px 0 16px">운영목적 및 목표</h3>
<div class="grid-cards" style="margin-top:0">
<div class="box"><h4>1. 개인의 욕구지향 서비스 지원</h4><p>개별 욕구에 따른 서비스 제공 및 지원<br>사례관리 운영체계에 의한 적합한 지원<br>인적·물적 자원체계 지원을 통한 자립생활 지향</p></div>
<div class="box"><h4>2. 행복한 세상을 꿈꾸는 즐거운 우리집</h4><p>투명하고 효율적인 기관 운영<br>직원의 자질 및 전문성 향상</p></div>
<div class="box"><h4>3. 참여와 소통을 통한 조화와 발전</h4><p>지역사회 참여 및 기여활동 확대</p></div></div>'''
write('/about/vision.html', page('미션·비전', subpage(0, '미션·비전', '미션·비전', vision), 0))

hist = [("2024", [("12", "정태춘 이사장 취임")]), ("2021", [("11", "김종화 이사장 취임"), ("10", "화재안전성능보강 — 드라이비트 교체 (기능보강사업)")]),
        ("2020", [("07", "정원용 원장 취임"), ("01", "‘우리 마음 월클, 너와나의 bicycle’ 프로그램 (세종사회복지공동모금회)")]),
        ("2018", [("06", "지붕·울타리 교체, 상수도 배관 연결 공사 (기능보강사업)")]),
        ("2017", [("09", "사회복지서비스 차량지원사업 (세종사회복지공동모금회)"), ("02", "식당 개보수 환경개선사업 (세종사회복지공동모금회)"), ("01", "실내외 개보수 공사 (기능보강사업)")]),
        ("2016", [("10", "세종복지원 → 세종빌로 명칭 변경")]),
        ("2014", [("09", "연기사랑마을 → 세종복지원으로 명칭 변경 (정원 30명), 사회복지법인 예일로 편입"), ("03", "사회복지법인 예일 설립")]),
        ("2010", [("01", "2층 종합프로그램실 및 강당 증축 (120평)")]), ("2006", [("10", "정원 49명으로 승인")]),
        ("2005", [("10", "시설 개보수 (심야전기)")]), ("2003", [("10", "신고시설 ‘연기사랑마을’ 설치")])]
rows = ''.join(f'<div class="yr"><h3>{y}</h3><ul>' + ''.join(f'<li><span>{m}월</span><div>{t}</div></li>' for m, t in it) + '</ul></div>' for y, it in hist)
write('/about/history.html', page('연혁', subpage(0, '연혁', '연혁', f'<div class="split"><div class="side"><p class="quote">2003년 연기사랑마을에서<br>오늘의 세종빌까지</p><img src="/assets/img/drawing.jpg" alt="" loading="lazy"></div><div>{rows}</div></div>'), 0))

org = '''<img src="/assets/img/org.png" alt="조직도: 시설장 아래 사무국장, 서비스지원부장, 생활재활팀장, 행정지원팀장 등" style="width:100%;max-width:720px;margin:0 auto 48px;background:#fff;border-radius:18px;padding:20px">
<h3 style="font-family:var(--serif);font-size:1.4rem;margin-bottom:16px">직원현황 <span class="note">(총 22명)</span></h3>
<div class="tbl-scroll"><table class="tb"><tr><th>시설장</th><th>사무국장</th><th>사회재활교사</th><th>상담평가요원</th><th>행정팀장</th><th>생활팀장</th><th>생활재활교사</th><th>간호사</th><th>영양사</th><th>조리원</th></tr>
<tr><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>2</td><td>11</td><td>1</td><td>1</td><td>2</td></tr></table></div>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:48px 0 16px">입소현황 <span class="note">(총 30명)</span></h3>
<div class="tbl-scroll"><table class="tb"><tr><th rowspan="2">계</th><th colspan="2">국민기초생활보장수급권자</th><th colspan="2">실비</th></tr><tr><th>무연고</th><th>연고</th><th>무연고</th><th>연고</th></tr>
<tr><td>30</td><td>14</td><td>16</td><td>-</td><td>-</td></tr></table></div>'''
write('/about/org.html', page('조직·현황', subpage(0, '조직·현황', '조직·현황', org), 0))

q = '세종특별자치시 전의면 양지편길 13-6'
loc = f'''<div class="split"><div class="side"><img src="/assets/img/building.png" alt="세종빌 전경" style="aspect-ratio:4/3;object-fit:cover"></div><div>
<p class="quote">세종빌 (구, 세종복지원)</p><p class="lead">{ADDR}</p>
<p style="margin-top:12px">TEL <a href="tel:{TEL}"><b>{TEL}</b></a> · FAX 044-864-3016 · <a href="mailto:yengi363@naver.com">yengi363@naver.com</a></p>
<div class="cta"><a class="btn red" href="https://map.naver.com/p/search/{q}" target="_blank" rel="noopener">네이버 지도에서 보기</a><a class="btn line" href="https://map.kakao.com/?q={q}" target="_blank" rel="noopener">카카오맵에서 보기</a></div>
<div class="grid-cards" style="margin-top:40px">
<div class="box"><h4>서울 방면</h4><p>천안IC → 천안논산고속도로 남풍세IC → 세종시 방향 → 전의 방향 → 세종빌</p></div>
<div class="box"><h4>전라 방면</h4><p>익산IC → 천안논산고속도로 정안IC → 세종시 방향 → 덕학교차로 → 세종빌</p></div>
<div class="box"><h4>경상 방면</h4><p>남세종IC → 세종시 방향 → 미리내로 좌회전 → 덕학교차로 우회전 → 세종빌</p></div></div></div></div>'''
write('/about/location.html', page('오시는 길', subpage(0, '오시는 길', '오시는 길', loc), 0))

# ---------- 일상 ----------
svc = '''<p class="lead" style="max-width:760px">세종빌 전체 입주자를 대상으로 건강한 생활 유지와 신변처리 능력 향상, 자립 능력 향상, 정기적인 치료·진료를 통한 건강 증진을 목표로 합니다.</p>
<div class="grid-cards">
<div class="box"><span class="num">01</span><h4>생활재활서비스</h4><p>개별 인지 능력과 특성에 따라 세면, 양치 등 기초생활을 지원하여 건강한 생활을 유지하고 신변처리 능력을 키우도록 돕습니다.</p></div>
<div class="box"><span class="num">02</span><h4>사회·심리재활서비스</h4><p>지역사회 문화체험 등 다양한 외부 프로그램으로 사회 통합을 도모하고 사회 적응 능력을 키웁니다.</p></div>
<div class="box"><span class="num">03</span><h4>교육재활서비스</h4><p>교육의 기회를 제공하여 잠재능력과 소질을 최대한 개발할 수 있도록 지원합니다.</p></div>
<div class="box"><span class="num">04</span><h4>건강 지원 서비스</h4><p>질병의 예방과 치료, 신체 기능의 퇴화 방지와 기능 향상, 맞춤형 식이 제공으로 건강한 삶을 지원합니다.</p></div></div>
<div class="cards" style="margin-top:48px"><div class="card"><img src="/assets/img/meal.jpg" alt="" loading="lazy"></div><div class="card"><img src="/assets/img/soccer.jpg" alt="" loading="lazy"></div><div class="card"><img src="/assets/img/bubble.jpg" alt="" loading="lazy"></div></div>'''
write('/days/services.html', page('주요 서비스', subpage(1, '주요 서비스', '주요 서비스', svc), 1))

# ---------- 입주 ----------
adm = f'''<div class="grid-cards" style="margin-top:0"><div class="box"><h4>입주 조건</h4><p>지적장애인</p></div><div class="box"><h4>입소 상담</h4><p><a href="tel:{TEL}"><b style="font-size:1.3rem;color:var(--red)">☎ {TEL}</b></a></p></div></div>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:48px 0 16px">입주 절차</h3>
<ol class="steps"><li><b>입주 문의</b><span>전화 상담</span></li><li><b>방문 상담</b><span>내방 상담</span></li><li><b>1차 판정회의</b><span>예비거주 여부 결정</span></li>
<li><b>예비거주</b><span>계약서 작성·비용 납부 후 4주간</span></li><li><b>가정방문 상담</b><span>예비거주 종료 후</span></li><li><b>2차 판정회의</b><span>입주 여부 결정</span></li><li><b>입주 및 서비스 지원</b><span>입주계약서 작성</span></li></ol>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:48px 0 16px">입소 시 필요한 서류</h3>
<div class="box"><ol style="padding-left:1.4em;line-height:2;color:var(--ink2)"><li>입소신청서</li><li>입소서약서</li><li>개인정보 수집·이용 동의서</li><li>주민등록등본</li><li>복지카드</li><li>주민등록초본</li><li>가족관계증명서</li><li>건강진단서</li></ol>
<p class="note" style="margin-top:12px">신청서·서약서 양식은 전화로 문의해 주시면 안내해 드립니다.</p></div>'''
write('/admission.html', page('입주 안내', subpage(2, '입주 안내', '입주 조건·절차', adm, '입주 조건·절차'), 2))

# ---------- 함께하기 ----------
sup = f'''<div class="split"><div><p class="quote">여러분의 작은 정성이<br>세종빌에 큰 힘이 됩니다</p><p class="lead">세종빌과 함께하는 사랑나누기에 동참해 주세요.</p>
<div class="light" style="margin-top:28px">{accts()}</div></div>
<div><div class="grid-cards" style="margin-top:0;grid-template-columns:1fr">
<div class="box"><h4>재정후원</h4><p>지적장애인들에게 필요한 재활서비스와 기관 운영에 필요한 사업비를 정기적으로 후원하실 수 있습니다.</p></div>
<div class="box"><h4>저금통후원</h4><p>나눔 저금통에 동전을 모아 전해 주실 수 있습니다. 동전이 할 수 있는 가장 아름다운 일입니다.</p></div>
<div class="box"><h4>결연후원</h4><p>세종빌의 지적장애인과 1:1 결연을 맺어 매월 일정 금액을 후원하실 수 있습니다.</p></div>
<div class="box"><h4>문의 및 상담</h4><p>행정지원팀 TEL <a href="tel:{TEL}"><b>{TEL}</b></a> / FAX 044-864-3016</p></div></div></div></div>'''
write('/together/support.html', page('후원 안내', subpage(3, '후원 안내', '후원 안내', sup), 3))

vol = f'''<p class="quote">작은 손길이 모여 큰 힘이 됩니다</p><p class="lead">세종빌과 함께할 자원봉사자를 모집합니다. 신청은 전화(<a href="tel:{TEL}">{TEL}</a>), 방문, 자원봉사센터를 통해 하실 수 있습니다.</p>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:40px 0 16px">활동 절차</h3>
<ol class="steps"><li><b>신청 접수</b><span>전화·방문·봉사센터</span></li><li><b>교육</b><span>오리엔테이션</span></li><li><b>활동처 배치</b></li><li><b>봉사활동</b></li><li><b>평가</b></li></ol>
<h3 style="font-family:var(--serif);font-size:1.4rem;margin:48px 0 16px">활동 내용</h3>
<div class="grid-cards" style="margin-top:0"><div class="box"><h4>일상생활 보조</h4><p>청소, 식사보조, 목욕, 세탁, 산책보조 등</p></div><div class="box"><h4>생활 지원</h4><p>음식 지원, 김장, 설비 보수, 환경 관리 등</p></div>
<div class="box"><h4>행사 보조</h4><p>나들이, 장애인의 날, 하계캠프, 소풍 등</p></div><div class="box"><h4>프로그램</h4><p>학습지도, 놀이, 보행훈련, 기초 생활지도, 문화체험, 공연 등</p></div></div>
<div class="grid-cards"><div class="box"><h4>활동 원칙</h4><p>활동 가능 시간은 매일 09시~18시입니다. 간편하고 활동적인 복장을 착용하고, 약속한 시간을 지켜 주세요(변경 시 사전 연락). 초등학생은 보호자와 함께 오셔야 하며, 정기 봉사는 주 또는 월 1회 이상 가능해야 합니다. 활동을 마치면 활동일지를 기록합니다.</p></div>
<div class="box"><h4>에티켓</h4><p>이용장애인의 인권과 자기선택권·자기결정권을 존중해 주세요. 무분별한 약속을 하지 않고, 안전을 우선으로 생각합니다. 놀라거나 비판하거나 지시하지 않으며, 항상 일관되게 행동합니다. 해결하기 어려운 문제는 담당교사와 의논하고, 서로 예의를 지키며 존칭어를 사용합니다.</p></div></div>'''
write('/together/volunteer.html', page('자원봉사 안내', subpage(3, '자원봉사 안내', '자원봉사 안내', vol), 3))

contact = f'''<div class="grid-cards" style="margin-top:0">
<div class="box"><h4>전화</h4><p><a href="tel:{TEL}"><b style="font-size:1.3rem;color:var(--red)">{TEL}</b></a><br>평일 09:00~18:00</p></div>
<div class="box"><h4>팩스</h4><p><b style="font-size:1.3rem">044-864-3016</b></p></div>
<div class="box"><h4>이메일</h4><p><a href="mailto:yengi363@naver.com"><b style="font-size:1.15rem">yengi363@naver.com</b></a></p></div></div>
<p class="note" style="margin-top:24px">입주·후원·자원봉사 등 궁금한 점은 전화나 이메일로 편하게 문의해 주세요.</p>'''
write('/together/contact.html', page('문의하기', subpage(3, '문의하기', '문의하기', contact), 3))

write('/privacy.html', page('개인정보처리방침', subpage(4, '개인정보처리방침', '개인정보처리방침', '''<div class="prose"><p>세종빌 홈페이지는 회원가입이나 별도의 개인정보 입력 기능을 운영하지 않으며, 방문자의 개인정보를 수집하지 않습니다.</p>
<p>전화·이메일로 문의하시면서 알려주신 정보는 문의 응대 목적으로만 이용하며, 목적이 끝나면 지체 없이 파기합니다.</p>
<p>홈페이지에 게시하는 이용자 사진은 본인 또는 보호자의 동의를 받아 게시하며, 게시 중단을 원하시면 연락 주시는 즉시 삭제합니다.</p>
<p>개인정보 관련 문의: 세종빌 사무국 044-864-3015 · yengi363@naver.com</p></div>''', '공지사항'), 4))

# ---------- 게시판 ----------
SECS = {'stories': 1, 'menu': 1, 'schedule': 1, 'neighbors': 3, 'notice': 4, 'rights': 4, 'newsletter': 4}
PER = 12
for key, posts in P.items():
    name, sec = BOARD_META[key]
    gallery = key in ('stories', 'neighbors', 'rights', 'newsletter')
    pages = max(1, math.ceil(len(posts) / PER))
    for pg in range(1, pages + 1):
        chunk = posts[(pg - 1) * PER: pg * PER]
        if gallery:
            inner = '<div class="cards">' + ''.join(f'''<a class="card" href="/board/{key}/{p["id"]}.html"><img src="{thumb(p) or "/assets/img/logo.png"}" alt="" loading="lazy"><div class="cap"><small>{fmt(p["date"])}</small><b>{E(p["title"])}</b></div></a>''' for p in chunk) + '</div>'
        else:
            inner = '<ul class="board-list">' + ''.join(f'''<li><a href="/board/{key}/{p["id"]}.html"><span class="no">{p["no"]}</span><span class="tt">{E(p["title"])}</span>{'<span class="att">첨부</span>' if p["files"] else ''}<time>{p["date"]}</time></a></li>''' for p in chunk) + '</ul>'
        if pages > 1:
            inner += '<nav class="pager" aria-label="페이지">' + ''.join(
                f'<span aria-current="page">{i}</span>' if i == pg else f'<a href="/board/{key}/{"" if i == 1 else f"page{i}.html"}">{i}</a>' for i in range(1, pages + 1)) + '</nav>'
        top = ''
        if key in ('menu', 'schedule') and pg == 1 and posts:
            lp = posts[0]
            for f in lp['files']:
                fe = os.path.splitext(f['file'])[1].lower()
                src = f['file'] if fe in ('.jpg', '.jpeg', '.png', '.webp') else (lp['previews'][0] if lp['previews'] else None)
                if src:
                    top = f'<h2 class="t" style="font-size:1.5rem;margin:0 0 14px">{"이번 주 식단" if key == "menu" else "이번 달 일정"} · {E(lp["title"])}</h2><a href="{src}" target="_blank" rel="noopener"><img class="att-img" src="{src}" alt="{E(lp["title"])}"></a><p class="note" style="margin:-4px 0 40px">그림을 누르면 크게 볼 수 있어요.</p>'
                    break
            if not top and lp['images']:
                src = lp['images'][0]
                top = f'<h2 class="t" style="font-size:1.5rem;margin:0 0 14px">{"이번 주 식단" if key == "menu" else "이번 달 일정"} · {E(lp["title"])}</h2><a href="{src}" target="_blank" rel="noopener"><img class="att-img" src="{src}" alt="{E(lp["title"])}"></a><p class="note" style="margin:-4px 0 40px">그림을 누르면 크게 볼 수 있어요.</p>'
        inner = top + f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;gap:12px"><p class="note">전체 {len(posts)}건</p><a class="btn line writebtn" href="/write/?b={key}">✏️ 글쓰기</a></div>' + inner
        write(f'/board/{key}/' + ('' if pg == 1 else f'page{pg}.html'), page(name, subpage(sec, name, name, inner), sec))
    for i, p in enumerate(posts):
        imgs = ''
        inline = set(re.findall(r'src="([^"]+)"', p['body']))
        g = [x for x in p['images'] if x not in inline]
        if g:
            imgs = '<div class="post-imgs">' + ''.join(f'<a href="{x}" target="_blank" rel="noopener"><img src="{x}" alt="" loading="lazy"></a>' for x in g) + '</div>'
        show = ''
        for f in p['files']:
            fe = os.path.splitext(f['file'])[1].lower()
            if fe in ('.jpg', '.jpeg', '.png', '.gif'):
                show += f'<a href="{f["file"]}" target="_blank" rel="noopener"><img class="att-img" src="{f["file"]}" alt="{E(p["title"])}" loading="lazy"></a>'
        for pv in p['previews']:
            show += f'<a href="{pv}" target="_blank" rel="noopener"><img class="att-img" src="{pv}" alt="{E(p["title"])}" loading="lazy"></a>'
        files = ''
        if p['files']:
            files = '<ul class="files">' + ''.join(f'<li><a href="{f["file"]}" download><svg class="ico"><use href="#i-file"/></svg>{E(f["name"])}</a></li>' for f in p['files']) + '</ul>'
        prev_ = posts[i + 1] if i + 1 < len(posts) else None
        next_ = posts[i - 1] if i > 0 else None
        nav = '<nav class="post-nav">' + (f'<a href="/board/{key}/{prev_["id"]}.html">← {E(prev_["title"][:24])}</a>' if prev_ else '<span></span>') + \
              f'<a class="more" href="/board/{key}/">목록</a>' + (f'<a href="/board/{key}/{next_["id"]}.html">{E(next_["title"][:24])} →</a>' if next_ else '<span></span>') + '</nav>'
        admin_bar = f'<div class="post-admin" hidden><a class="btn line writebtn" href="/write/?b={key}&amp;edit={p["id"]}">✏️ 수정·삭제</a></div>'
        body = admin_bar + f'<article><header class="post-head"><h2>{E(p["title"])}</h2><time datetime="{p["date"]}">{fmt(p["date"])}</time></header>{show}{imgs}<div class="prose" style="max-width:none">{p["body"]}</div>{files}{nav}</article>'
        write(f'/board/{key}/{p["id"]}.html', page(p['title'], subpage(sec, name, name, body), sec, desc=p['text'][:120] or name))

# 정보공개
cats = ['예산·결산', '회의록', '후원금', '계약']
items = ''.join(f'''<li data-cat-item="{disc_cat(p["title"])}"><a href="/board/notice/{p["id"]}.html"><span class="chip">{disc_cat(p["title"])}</span><span class="tt">{E(p["title"])}</span>{'<span class="att">첨부</span>' if p["files"] else ''}<time>{p["date"]}</time></a></li>''' for p in disc)
dbody = f'''<p class="lead" style="margin-bottom:28px">사회복지법인 예일과 세종빌의 예산·결산, 이사회 회의록, 운영위원회 결과, 후원금 사용내역을 공개합니다.</p>
<div class="filter" role="group" aria-label="분류"><button data-cat="all" aria-pressed="true">전체</button>{''.join(f'<button data-cat="{c}" aria-pressed="false">{c}</button>' for c in cats)}</div>
<ul class="board-list">{items}</ul>'''
write('/disclosure.html', page('정보공개', subpage(4, '정보공개', '정보공개', dbody), 4))


# ---------- 직원 회원가입 신청 ----------
boards_ck = ''.join(f'<label class="ck"><input type="checkbox" name="게시판" value="{n}"> {n}</label>' for n in ['일상 이야기', '금주의 식단', '주요 일정', '공지사항', '아름다운 이웃', '인권존중', '소식지'])
action = f'https://formspree.io/f/{FORM_ID}' if FORM_ID else ''
join_body = f'''<div class="split"><div><p class="quote">세종빌 직원이신가요?</p>
<p class="lead">홈페이지에 글을 올리려면 회원가입 신청을 해주세요. 사무국장이 확인한 뒤 <b>가입 안내 메일</b>을 보내드립니다.</p>
<ol class="steps" style="margin-top:28px;grid-template-columns:1fr"><li><b>신청서 작성</b><span>이 화면에서 신청</span></li><li><b>사무국장 승인</b><span>보통 1~2일</span></li>
<li><b>가입 안내 메일 확인</b><span>메일의 링크를 눌러 비밀번호 설정</span></li><li><b>로그인 후 글쓰기</b><span>홈페이지 맨 아래 ‘직원 로그인’</span></li></ol></div>
<form class="box joinform" id="joinform" action="{action}" method="POST">
<label><span>이름 <b class="req">*</b></span><input name="이름" required autocomplete="name"></label>
<label><span>직책 <b class="req">*</b></span><input name="직책" required placeholder="예: 생활재활교사"></label>
<label><span>이메일 <b class="req">*</b></span><input type="email" name="email" required autocomplete="email" placeholder="가입 안내를 받을 이메일"></label>
<fieldset><legend>글을 올릴 게시판</legend><div class="cks">{boards_ck}</div></fieldset>
<label><span>남길 말</span><textarea name="남길 말" rows="3"></textarea></label>
<input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">
<input type="hidden" name="_subject" value="[세종빌 홈페이지] 직원 회원가입 신청">
<label class="ck"><input type="checkbox" required> 가입 처리를 위해 이름·직책·이메일을 사무국장에게 보내는 것에 동의합니다. (가입 처리 후 신청 내용은 보관하지 않습니다)</label>
<button class="btn red" type="submit" {"" if FORM_ID else "disabled"}>회원가입 신청하기</button>
<p class="note" id="joinmsg" role="status">{"" if FORM_ID else "신청 기능을 준비 중입니다. 급하신 분은 사무국(044-864-3015)으로 연락해 주세요."}</p>
</form></div>'''
write('/join.html', page('직원 회원가입 신청', subpage(4, '직원 회원가입 신청', '직원 회원가입 신청', join_body, '없음'), 4))


# ---------- 간편 글쓰기 ----------
board_opts = ''.join(f'<option value="{k}">{v[0]}</option>' for k, v in BOARD_META.items())
write_body = f'''<div style="max-width:760px">
<div id="loginBox" class="box joinform" hidden>
<p class="quote" style="font-size:1.3rem;margin:0">직원 로그인</p>
<p class="note">회원가입 승인 메일을 받고 정한 이메일·비밀번호로 로그인하세요. 한 번 로그인하면 이 기기에서 기억해요.</p>
<form id="loginForm" class="joinform"><label><span>이메일</span><input id="lemail" type="email" required autocomplete="username"></label>
<label><span>비밀번호</span><input id="lpw" type="password" required autocomplete="current-password"></label>
<button class="btn red" type="submit">로그인</button><p class="note" id="lmsg" role="status"></p></form>
<p class="note">아직 계정이 없으면 <a href="/join.html" style="text-decoration:underline">직원 회원가입 신청</a></p></div>
<form id="writeForm" class="box joinform" hidden>
<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><p class="note"><b id="who"></b> · <button type="button" id="logout" style="text-decoration:underline">로그아웃</button></p>
<label style="display:flex;gap:8px;align-items:center;font-weight:600">게시판 <select id="boardSel" style="font:inherit;padding:8px 10px;border-radius:10px;border:1px solid var(--line)">{board_opts}</select></label></div>
<label><span>제목 <b class="req">*</b></span><input id="wtitle" required placeholder="예: 2026. 11. 2.(월) 가을 산책"></label>
<label><span>내용</span><textarea id="wbody" rows="6" placeholder="간단히 적어 주세요. 줄바꿈도 그대로 보여요."></textarea></label>
<div><span style="font-weight:600">사진</span>
<label class="pick"><input id="photos" type="file" accept="image/*" multiple hidden>📷 사진 고르기 (여러 장 한 번에)</label>
<p class="note" id="pcount"></p><div id="thumbs" class="thumbs"></div></div>
<div><span style="font-weight:600">첨부파일 <small class="note">(한글·PDF·엑셀 등, 필요할 때만)</small></span><ul id="oldFiles" style="list-style:none;margin:6px 0"></ul><input id="attach" type="file" multiple style="font:inherit;border:1px solid var(--line);border-radius:10px;padding:10px;width:100%;background:var(--paper)"></div>
<button class="btn red" id="wsubmit" type="submit" style="justify-content:center">올리기</button><button class="btn line" id="delBtn" type="button" hidden style="justify-content:center;color:var(--red);border-color:var(--red)">이 글 삭제</button>
<p class="note" id="wmsg" role="status"></p>
<p class="note">올린 글은 글 화면 위쪽의 <b>수정·삭제</b> 버튼으로 고칠 수 있어요.</p></form>
<div id="done" class="box" hidden style="text-align:center;padding:48px 24px"><p class="quote" style="font-size:1.5rem" id="doneTitle">올렸어요! 🎉</p>
<p class="lead">2~3분 뒤 게시판에 보여요.</p><div class="cta" style="justify-content:center"><a class="btn red" id="doneLink" href="/">게시판으로 가기</a><button class="btn line" id="again" type="button">글 하나 더 쓰기</button></div></div>
<p style="margin-top:20px"><a class="more" id="backLink" href="/">← 게시판으로 돌아가기</a></p></div>
<script src="/assets/write.js"></script>'''
write('/write/index.html', page('글쓰기', f'<div class="subvis"><div class="wrap"><div class="crumb">직원 글쓰기</div><h1><span id="boardName">게시판</span> <span id="modeWord">글쓰기</span></h1></div></div><div class="content"><div class="wrap">{write_body}</div></div>'))

# 404, 기타
write('/404.html', page('페이지를 찾을 수 없어요', '<div class="content"><div class="wrap" style="text-align:center;padding:80px 0"><p class="quote">페이지를 찾을 수 없어요</p><p class="lead">주소가 바뀌었거나 삭제된 페이지입니다.</p><div class="cta" style="justify-content:center"><a class="btn red" href="/">처음으로</a></div></div></div>'))
open(f'{SITE}/.nojekyll', 'w').write('')
open(f'{SITE}/robots.txt', 'w').write('User-agent: *\nAllow: /\n')
print('done', sum(len(v) for v in P.values()), 'posts')
