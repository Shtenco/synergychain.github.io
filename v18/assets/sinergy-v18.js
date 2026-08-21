/* SINERGY V18 shared runtime. No external dependencies. */
(()=>{
  const root=document.documentElement;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const qs=(s,c=document)=>c.querySelector(s), qsa=(s,c=document)=>[...c.querySelectorAll(s)];

  // pointer aura + CSS variables
  if(!reduce){
    addEventListener('pointermove',e=>{
      root.style.setProperty('--mx',e.clientX+'px');
      root.style.setProperty('--my',e.clientY+'px');
    },{passive:true});
    addEventListener('scroll',()=>root.style.setProperty('--scroll',scrollY),{passive:true});
  }

  // reveal
  const reveal=qsa('.reveal');
  if('IntersectionObserver' in window && !reduce){
    const io=new IntersectionObserver(entries=>entries.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12,rootMargin:'0px 0px -5%'});
    reveal.forEach(el=>io.observe(el));
  }else reveal.forEach(el=>el.classList.add('in'));

  // local card light + subtle tilt
  if(!reduce){
    qsa('.card,.domain-card').forEach(card=>{
      card.addEventListener('pointermove',e=>{
        const r=card.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;
        card.style.setProperty('--card-x',x*100+'%'); card.style.setProperty('--card-y',y*100+'%');
        if(card.hasAttribute('data-tilt')) card.style.transform=`perspective(900px) rotateX(${(0.5-y)*5}deg) rotateY(${(x-.5)*7}deg) translateY(-3px)`;
      });
      card.addEventListener('pointerleave',()=>{if(card.hasAttribute('data-tilt')) card.style.transform='';});
    });
  }

  // kinetic text micro-parallax
  if(!reduce){
    qsa('.kinetic').forEach(el=>{
      addEventListener('pointermove',e=>{
        const dx=(e.clientX-innerWidth/2)/innerWidth,dy=(e.clientY-innerHeight/2)/innerHeight;
        el.style.transform=`translate3d(${dx*7}px,${dy*5}px,0)`;
      },{passive:true});
    });
  }

  // canvas flow-field / spiral illusion
  const canvas=qs('#motionCanvas');
  if(canvas && !reduce){
    const ctx=canvas.getContext('2d',{alpha:true}); let w=0,h=0,dpr=1,t=0,raf;
    const resize=()=>{dpr=Math.min(devicePixelRatio||1,1.8);w=innerWidth;h=innerHeight;canvas.width=w*dpr;canvas.height=h*dpr;canvas.style.width=w+'px';canvas.style.height=h+'px';ctx.setTransform(dpr,0,0,dpr,0,0)};
    const draw=()=>{
      t+=0.0032;ctx.clearRect(0,0,w,h);ctx.save();ctx.translate(w*.5,h*.45);
      const min=Math.min(w,h),rings=Math.max(18,Math.floor(min/42));
      for(let j=0;j<rings;j++){
        const r=22+j*22+(Math.sin(t*2+j*.35)+1)*2,alpha=Math.max(.015,.07-j*.0027);
        ctx.beginPath();ctx.strokeStyle=`rgba(0,232,120,${alpha})`;ctx.lineWidth=.75;
        const pts=150;
        for(let i=0;i<=pts;i++){
          const a=i/pts*Math.PI*2; const wob=Math.sin(a*7+t*8+j*.4)*2.2+Math.sin(a*3-t*5)*1.4;
          const rr=r+wob;const x=Math.cos(a+t*(j%2?1:-1)*.22)*rr*1.45;const y=Math.sin(a+t*.15)*rr*.58;
          if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
        }ctx.stroke();
      }
      ctx.rotate(t*.23);ctx.strokeStyle='rgba(141,255,189,.028)';
      for(let i=0;i<34;i++){const a=i/34*Math.PI*2;ctx.beginPath();ctx.moveTo(Math.cos(a)*40,Math.sin(a)*20);ctx.lineTo(Math.cos(a)*min*.82,Math.sin(a)*min*.36);ctx.stroke()}
      ctx.restore();raf=requestAnimationFrame(draw)
    };
    addEventListener('resize',resize);resize();draw();
    document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelAnimationFrame(raf);else draw()});
  }

  // active navigation by pathname
  const here=location.pathname.replace(/\/+$/,'/');
  qsa('.global-nav a').forEach(a=>{
    try{const p=new URL(a.href,location.href).pathname.replace(/\/+$/,'/'); if(p===here || (here.includes('/v18/')&&a.dataset.domain&&here.includes('/'+a.dataset.domain+'/')))a.classList.add('active')}catch{}
  });

  const esc=s=>String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const explorerBase=()=>{
    const p=location.pathname;
    if(p.includes('/v18/explorer/'))return '';
    if(p.includes('/v18/'))return '../explorer/';
    return 'v18/explorer/';
  };
  const passportHref=x=>explorerBase()+`entity.html?id=${encodeURIComponent(x.id)}`;

  // Explorer
  const box=qs('#entityGrid');
  if(box && Array.isArray(window.SINERGY_ENTITIES)){
    const search=qs('#entitySearch'),domain=qs('#domainFilter'),type=qs('#typeFilter'),status=qs('#statusFilter'),count=qs('#entityCount');
    const uniq=k=>[...new Set(SINERGY_ENTITIES.map(x=>x[k]).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'ru'));
    const fill=(el,items,label)=>{if(!el)return;el.innerHTML=`<option value="">${label}</option>`+items.map(x=>`<option>${esc(x)}</option>`).join('')};
    fill(domain,uniq('domain'),'Все домены');fill(type,uniq('entityType'),'Все типы');fill(status,uniq('status'),'Все статусы');
    const render=()=>{
      const q=(search?.value||'').trim().toLowerCase(),d=domain?.value||'',ty=type?.value||'',st=status?.value||'';
      const rows=SINERGY_ENTITIES.filter(x=>(!d||x.domain===d)&&(!ty||x.entityType===ty)&&(!st||x.status===st)&&(!q||Object.values(x).join(' ').toLowerCase().includes(q)));
      if(count)count.textContent=rows.length;
      box.innerHTML=rows.length?rows.map(x=>`<article class="entity-card reveal in"><div class="entity-meta"><span class="tag">${esc(x.domain)}</span><span class="status ${esc(x.status)}">${esc(x.status)}</span><span class="tag">${esc(x.evidence||'L0')}</span></div><h3>${esc(x.name)}</h3><p>${esc(x.summary)}</p><div class="tiny">${esc(x.entityType)} · ${esc(x.moneyRole||'non-monetary')}</div><div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><a class="btn ghost" href="${passportHref(x)}">Паспорт →</a>${x.href?`<a class="btn ghost" href="${esc(x.href)}">Deep page →</a>`:''}</div></article>`).join(''):'<div class="empty">Ничего не найдено.</div>';
    };
    [search,domain,type,status].filter(Boolean).forEach(el=>el.addEventListener(el.tagName==='INPUT'?'input':'change',render));render();
  }

  // copy formula / code blocks on click
  qsa('[data-copy]').forEach(el=>el.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(el.dataset.copy||el.textContent);const old=el.title;el.title='Скопировано';setTimeout(()=>el.title=old,1200)}catch{}}));
})();
