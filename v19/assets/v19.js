(()=>{
 const root=document.documentElement;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
 const guard=document.createElement('style');
 guard.dataset.v19ResponsiveGuard='true';
 guard.textContent=`html,body,.shell{max-width:100%;overflow-x:hidden}.topbar,.nav,.ticker,.hero,.page-hero,.section,.section-head,.grid,.conflict,.flow,.matrix,.quote-stage,.rights-grid,.human-path,.authority-grid,.project-wall,.proof-levels,.evidence-stats,.statement-band,.scale-stack{min-width:0;max-width:100%}.hero>*,.page-hero>*,.section-head>*,.grid>*,.conflict>*,.flow>*,.project-wall>*{min-width:0}.nav{min-width:0;max-width:100%;contain:inline-size}.nav a{flex:0 0 auto}.ticker{width:100%;max-width:100vw;overflow:hidden;contain:inline-size}.ticker-track{max-width:none}.kicker,.eyebrow,.hero h1,.page-hero h1,.section h2,.quote-stage blockquote,.card h3,.conflict-card h3,.matrix b,.statement-copy,.hard-rule-formula,.scale-line b{max-width:100%;overflow-wrap:anywhere;word-break:normal}@media(max-width:760px){.nav{width:calc(100vw - 34px);overflow-x:auto;overflow-y:hidden;overscroll-behavior-inline:contain;scrollbar-width:none}.nav::-webkit-scrollbar{display:none}.kicker,.eyebrow{font-size:8px;letter-spacing:.105em;line-height:1.35}.lead{font-size:17px}}`;
 document.head.appendChild(guard);
 function pointer(e){root.style.setProperty('--mx',`${e.clientX}px`);root.style.setProperty('--my',`${e.clientY}px`)}
 if(!reduced)addEventListener('pointermove',pointer,{passive:true});
 const revealEls=[...document.querySelectorAll('.reveal')];
 if(reduced)revealEls.forEach(el=>el.classList.add('visible'));else{
   const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target)}}),{threshold:.07,rootMargin:'0px 0px -6%'});
   revealEls.forEach((el,i)=>{el.style.transitionDelay=`${Math.min(i%5,4)*38}ms`;io.observe(el)});
 }
 function onScroll(){
   const h=document.documentElement.scrollHeight-innerHeight;
   const p=h>0?scrollY/h*100:0;
   root.style.setProperty('--progress',p.toFixed(3));
   if(reduced)return;
   document.querySelectorAll('.kinetic').forEach((el,i)=>{
     const r=el.getBoundingClientRect();
     const y=clamp((innerHeight/2-r.top)/innerHeight,-1,1);
     el.style.transform=`translate3d(${y*(i%2?8:-8)}px,${y*-6}px,0)`;
   });
   const radar=document.querySelector('.radar-max');
   if(radar){const r=radar.getBoundingClientRect();const k=clamp((innerHeight-r.top)/innerHeight,-1,1);radar.style.transform=`translate3d(0,${k*-8}px,0) rotate(${k*1.2}deg)`}
   document.querySelectorAll('.final-number').forEach(el=>{const r=el.getBoundingClientRect();const k=clamp((innerHeight-r.top)/innerHeight,-1,1);el.style.transform=`translate3d(${k*-10}%,0,0)`});
 }
 addEventListener('scroll',onScroll,{passive:true});onScroll();
 const path=location.pathname;
 document.querySelectorAll('.nav a').forEach(a=>{const href=(a.getAttribute('href')||'').replace('../','').replace('./','');if(href&&path.includes(href))a.classList.add('active')});
 document.querySelectorAll('[data-count]').forEach(el=>{const target=Number(el.dataset.count)||0;if(reduced){el.textContent=target;return}let started=false;const obs=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting||started)return;started=true;const t0=performance.now(),dur=1000;const tick=t=>{const k=Math.min(1,(t-t0)/dur);el.textContent=Math.round(target*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(tick)};requestAnimationFrame(tick);obs.disconnect()}));obs.observe(el)});
 if(!reduced){
   document.querySelectorAll('.btn').forEach(btn=>{
     btn.addEventListener('pointermove',e=>{const r=btn.getBoundingClientRect();const x=(e.clientX-r.left-r.width/2)/r.width;const y=(e.clientY-r.top-r.height/2)/r.height;btn.style.transform=`translate(${x*3}px,${y*2}px) translateY(-2px)`});
     btn.addEventListener('pointerleave',()=>btn.style.transform='');
   });
   document.querySelectorAll('.right-card,.project-big,.project-tile,.authority').forEach(card=>{
     card.addEventListener('pointermove',e=>{const r=card.getBoundingClientRect();const x=(e.clientX-r.left)/r.width*100;const y=(e.clientY-r.top)/r.height*100;card.style.setProperty('--cx',`${x}%`);card.style.setProperty('--cy',`${y}%`)});
   });
 }
 document.querySelectorAll('[data-copy]').forEach(el=>el.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(el.dataset.copy);const old=el.textContent;el.textContent='СКОПИРОВАНО';setTimeout(()=>el.textContent=old,900)}catch{}}));
})();