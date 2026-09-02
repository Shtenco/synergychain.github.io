(()=>{
 const responsive=document.createElement('style');
 responsive.dataset.v19ResponsiveGuard='true';
 responsive.textContent=`
 html,body,.shell{max-width:100%;overflow-x:hidden}
 .topbar,.nav,.ticker,.hero,.page-hero,.section,.section-head,.grid,.conflict,.flow,.matrix,.quote-stage{min-width:0;max-width:100%}
 .hero>*,.page-hero>*,.section-head>*,.grid>*,.conflict>*,.flow>*{min-width:0}
 .nav{min-width:0;max-width:100%;contain:inline-size}
 .nav a{flex:0 0 auto}
 .ticker{width:100%;max-width:100vw;overflow:hidden;contain:inline-size}
 .ticker-track{max-width:none}
 .kicker,.eyebrow,.hero h1,.page-hero h1,.section h2,.quote-stage blockquote,.card h3,.conflict-card h3,.matrix b{max-width:100%;overflow-wrap:anywhere;word-break:normal}
 @media(max-width:720px){
   .nav{width:calc(100vw - 34px);overflow-x:auto;overflow-y:hidden;overscroll-behavior-inline:contain;scrollbar-width:none}
   .nav::-webkit-scrollbar{display:none}
   .ticker{overflow:hidden}
   .kicker,.eyebrow{font-size:9px;letter-spacing:.105em;line-height:1.35}
   .hero h1,.page-hero h1{font-size:clamp(44px,13vw,72px);line-height:.88;letter-spacing:-.06em}
   .section h2{font-size:clamp(36px,11.3vw,60px);line-height:.96;letter-spacing:-.045em}
   .quote-stage blockquote{font-size:clamp(34px,10.5vw,56px);line-height:.96}
   .lead{font-size:17px}
   .radar-node{font-size:7px;padding:5px 6px;letter-spacing:.05em}
   .rn2{right:0}.rn4{left:0}
 }
 `;
 document.head.appendChild(responsive);
 const root=document.documentElement;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
 function pointer(e){root.style.setProperty('--mx',`${e.clientX}px`);root.style.setProperty('--my',`${e.clientY}px`)}
 if(!reduced)addEventListener('pointermove',pointer,{passive:true});
 function onScroll(){const h=document.documentElement.scrollHeight-innerHeight;const p=h>0?scrollY/h*100:0;root.style.setProperty('--progress',p.toFixed(3));if(!reduced){document.querySelectorAll('.kinetic').forEach((el,i)=>{const r=el.getBoundingClientRect();const y=clamp((innerHeight/2-r.top)/innerHeight,-1,1);el.style.transform=`translate3d(${y*(i%2?8:-8)}px,${y*-5}px,0)`})}}
 addEventListener('scroll',onScroll,{passive:true});onScroll();
 const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('visible')}),{threshold:.08,rootMargin:'0px 0px -7%'});
 document.querySelectorAll('.reveal').forEach(el=>{if(reduced)el.classList.add('visible');else io.observe(el)});
 const path=location.pathname;
 document.querySelectorAll('.nav a').forEach(a=>{const href=a.getAttribute('href')||'';if(href&&href!=='../'&&path.includes(href.replace('../','').replace('./','')))a.classList.add('active')});
 document.querySelectorAll('[data-count]').forEach(el=>{const target=Number(el.dataset.count)||0;if(reduced){el.textContent=target;return}let started=false;const obs=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting||started)return;started=true;const t0=performance.now(),dur=900;const tick=t=>{const k=Math.min(1,(t-t0)/dur);el.textContent=Math.round(target*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(tick)};requestAnimationFrame(tick);obs.disconnect()}));obs.observe(el)});
 document.querySelectorAll('[data-copy]').forEach(el=>el.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(el.dataset.copy);const old=el.textContent;el.textContent='СКОПИРОВАНО';setTimeout(()=>el.textContent=old,900)}catch{}}));
})();