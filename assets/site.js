(function(){
  var root=document.documentElement;
  function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
  // 글자 크기
  var sizes={s:1,m:1.12,l:1.25};
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
