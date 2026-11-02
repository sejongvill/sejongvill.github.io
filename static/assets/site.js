(function(){
  var root=document.documentElement;
  function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
  // 글자 크기
  var sizes={xs:.9,s:1,m:1.12,l:1.25,xl:1.4};
  function setFs(k){root.style.setProperty('--fs',sizes[k]||1);document.querySelectorAll('.fsz button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.fs===k)});store('fs',k)}
  setFs(store('fs')||'s');
  document.querySelectorAll('.fsz button').forEach(function(b){b.addEventListener('click',function(){setFs(b.dataset.fs)})});
  // 모바일 메뉴
  var bg=document.querySelector('.burger'),menu=document.querySelector('.menu');
  if(bg)bg.addEventListener('click',function(){var o=menu.classList.toggle('open');bg.setAttribute('aria-expanded',o)});
  // 안내 메시지
  var toast=document.createElement('div');toast.className='toast';toast.setAttribute('role','status');document.body.appendChild(toast);
  function say(t){toast.textContent=t;toast.classList.add('on');clearTimeout(say.t);say.t=setTimeout(function(){toast.classList.remove('on')},1800)}
  // 계좌 복사
  document.querySelectorAll('[data-copy]').forEach(function(b){b.addEventListener('click',function(){
    var v=b.dataset.copy;
    function ok(){say('계좌번호를 복사했어요: '+v)}
    if(navigator.clipboard){navigator.clipboard.writeText(v).then(ok,function(){fallback()})}else fallback();
    function fallback(){var t=document.createElement('textarea');t.value=v;document.body.appendChild(t);t.select();try{document.execCommand('copy');ok()}catch(e){say(v)}t.remove()}
  })});
  // 정보공개 분류
  var fb=document.querySelectorAll('.filter button');
  fb.forEach(function(b){b.addEventListener('click',function(){
    fb.forEach(function(x){x.setAttribute('aria-pressed',x===b)});
    var c=b.dataset.cat;document.querySelectorAll('[data-cat-item]').forEach(function(li){li.hidden=!(c==='all'||li.dataset.catItem===c)});
  })});
})();
(function(){
  var f=document.getElementById('joinform');if(!f||!f.action)return;
  f.addEventListener('submit',function(e){
    e.preventDefault();var m=document.getElementById('joinmsg'),b=f.querySelector('button');
    b.disabled=true;m.textContent='보내는 중…';
    var d=new FormData(f);var gs=[].map.call(f.querySelectorAll('input[name="게시판"]:checked'),function(x){return x.value});
    d.delete('게시판');d.append('게시판',gs.join(', ')||'선택 안 함');
    fetch(f.action,{method:'POST',body:d,headers:{Accept:'application/json'}}).then(function(r){
      if(r.ok){f.reset();m.textContent='신청이 접수되었어요. 사무국장 확인 후 가입 안내 메일을 보내드릴게요.';}
      else{m.textContent='신청을 보내지 못했어요. 잠시 후 다시 시도하거나 사무국(044-864-3015)으로 연락해 주세요.';}
      b.disabled=false;
    }).catch(function(){m.textContent='인터넷 연결을 확인한 뒤 다시 시도해 주세요.';b.disabled=false;});
  });
})();
(function(){ /* 로그인한 직원에게만 수정·삭제 버튼 보이기 */
  var on=false;try{var a=JSON.parse(localStorage.getItem('sv-auth'));var g=JSON.parse(localStorage.getItem('gotrue.user'));on=!!((a&&a.access_token)||(g&&g.token))}catch(e){}
  if(on)document.querySelectorAll('.post-admin').forEach(function(x){x.hidden=false});
})();
(function(){ /* 메인 사진 10초마다 넘기기 */
  var box=document.querySelector('.slides');if(!box)return;
  var imgs=box.querySelectorAll('.sl'),dots=box.querySelector('.dots'),i=0,t;
  imgs.forEach(function(im,k){var b=document.createElement('button');b.setAttribute('role','tab');b.setAttribute('aria-label',(k+1)+'번째 사진');b.onclick=function(){go(k);start()};dots.appendChild(b)});
  var paused=false,pb=box.querySelector('.spause');
  if(box.querySelector('.sprev'))box.querySelector('.sprev').onclick=function(){go(i-1);start()};
  if(box.querySelector('.snext'))box.querySelector('.snext').onclick=function(){go(i+1);start()};
  if(pb)pb.onclick=function(){paused=!paused;pb.textContent=paused?'▶':'❚❚';pb.setAttribute('aria-label',paused?'사진 넘기기 다시 시작':'사진 넘기기 멈춤');start()};
  function go(k){imgs[i].classList.remove('on');i=(k+imgs.length)%imgs.length;imgs[i].classList.add('on');imgs[i].querySelectorAll('img').forEach(function(x){x.loading='eager'});
    dots.querySelectorAll('button').forEach(function(b,n){b.setAttribute('aria-selected',n===i)})}
  function start(){clearInterval(t);if(paused)return;if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return;t=setInterval(function(){go(i+1)},10000)}
  go(0);start();
})();

(function(){ /* 어두운 화면 */
  var b=document.querySelector('.theme');function set(d){document.documentElement.dataset.theme=d?'dark':'';if(b){b.textContent=d?'☀️ 밝게':'🌙 어둡게';b.setAttribute('aria-pressed',d)}try{localStorage.setItem('theme',d?'dark':'light')}catch(e){}}
  var cur=null;try{cur=localStorage.getItem('theme')}catch(e){}set(cur==='dark');
  if(b)b.addEventListener('click',function(){set(document.documentElement.dataset.theme!=='dark')});
})();
(function(){ /* 전체메뉴 */
  var b=document.querySelector('.allmenu-btn'),m=document.getElementById('allmenu');if(!b||!m)return;
  function t(o){m.hidden=!o;b.setAttribute('aria-expanded',o)}
  b.addEventListener('click',function(){t(m.hidden)});m.querySelector('.allmenu-close').addEventListener('click',function(){t(false);b.focus()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!m.hidden){t(false);b.focus()}});
})();
(function(){ /* 카드 넘기기 (보이는 탭 기준) */
  document.querySelectorAll('.cnav').forEach(function(nav){
    var sec=nav.closest('section'),pv=nav.querySelector('.cprev'),nx=nav.querySelector('.cnext');
    function row(){var c=[].filter.call(sec.querySelectorAll('.carousel'),function(x){return !x.closest('[hidden]')})[0];return c&&c.querySelector('.cards')}
    function step(){var r=row(),a=r&&r.children[0];return a?a.getBoundingClientRect().width+22:300}
    function upd(){var r=row();if(!r)return;pv.disabled=r.scrollLeft<5;nx.disabled=r.scrollLeft+r.clientWidth>=r.scrollWidth-5}
    pv.onclick=function(){row().scrollBy({left:-step()*3,behavior:'smooth'})};nx.onclick=function(){row().scrollBy({left:step()*3,behavior:'smooth'})};
    sec.querySelectorAll('.carousel .cards').forEach(function(r){r.addEventListener('scroll',function(){clearTimeout(r._t);r._t=setTimeout(upd,80)})});
    window.addEventListener('resize',upd);sec.addEventListener('tabchange',upd);upd();
  });
})();
(function(){ /* 스크롤하면 떠오르기 */
  if(typeof window.IntersectionObserver!=='function')return;
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  document.documentElement.classList.add('js');
  var sel='.blk .sec-head,.blk .card,.ncard,.panel,.nowcard,.about>div,.about>img,.support,.band .wrap,.box,.yr,.board-list li,.quick a';
  var els=[].slice.call(document.querySelectorAll(sel)).filter(function(e){return !e.closest('.hero2')});
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target)}})},{rootMargin:'0px 0px -8% 0px',threshold:.08});
  els.forEach(function(e){
    var sib=e.parentElement?[].indexOf.call(e.parentElement.children,e):0;
    e.style.transitionDelay=Math.min(sib,5)*90+'ms';e.classList.add('rv');io.observe(e);
  });
})();

(function(){ /* 탭 */
  document.querySelectorAll('.tabbar').forEach(function(tb){
    var sec=tb.closest('section'),bs=tb.querySelectorAll('button'),ps=[].filter.call(tb.parentElement.children,function(x){return x.classList.contains('tp')}),more=sec.querySelector('.tabmore');
    bs.forEach(function(b,i){b.addEventListener('click',function(){
      bs.forEach(function(x,j){x.setAttribute('aria-selected',j===i)});ps.forEach(function(p,j){p.hidden=j!==i});
      if(more&&b.dataset.more)more.href=b.dataset.more;
      ps[i].querySelectorAll('.rv').forEach(function(e){e.classList.add('in')});
      var r=ps[i].querySelector('.cards');if(r)r.scrollLeft=0;sec.dispatchEvent(new Event('tabchange'));
    })});
  });
})();
// 알림판
(function(){
  var b=document.querySelector('.board');if(!b)return;
  var s=[].slice.call(b.querySelectorAll('.bs'));if(s.length<2){var c=b.querySelector('.bctl');if(c)c.hidden=true;return}
  var i=0,n=b.querySelector('.bcount b'),pz=b.querySelector('.bpause'),t=null,
      still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,paused=still;
  function go(k){s[i].hidden=true;s[i].classList.remove('on');i=(k+s.length)%s.length;s[i].hidden=false;s[i].classList.add('on');n.textContent=i+1}
  function run(){clearInterval(t);if(!paused)t=setInterval(function(){go(i+1)},6000)}
  function setP(v){paused=v;pz.textContent=v?'▶':'❚❚';pz.setAttribute('aria-label',v?'알림 넘기기 시작':'알림 넘기기 멈춤');run()}
  b.querySelector('.bprev').addEventListener('click',function(){go(i-1);run()});
  b.querySelector('.bnext').addEventListener('click',function(){go(i+1);run()});
  pz.addEventListener('click',function(){setP(!paused)});
  b.addEventListener('mouseenter',function(){clearInterval(t)});b.addEventListener('mouseleave',run);
  b.addEventListener('focusin',function(){clearInterval(t)});
  setP(paused);
})();
