(()=>{
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
