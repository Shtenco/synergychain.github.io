import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const root=path.resolve(process.env.V18_OFFLINE_ROOT||'release/V18_STANDALONE');
const out=path.resolve('artifacts/v18-offline-smoke');
fs.mkdirSync(out,{recursive:true});
if(!fs.existsSync(path.join(root,'index.html'))) throw new Error(`Standalone index missing: ${root}`);

const routes=[
 ['home','index.html'],['model','model/index.html'],['financial','financial/index.html'],
 ['accounting','financial/accounting.html'],['money','financial/money.html'],['settlement','financial/settlement.html'],
 ['bridge','financial/bridge.html'],['treasury','financial/treasury.html'],['qe','financial/qe-qt.html'],
 ['liquidity','financial/liquidity.html'],['solvency','financial/solvency.html'],['profit','financial/profit.html'],
 ['institutions','institutions/index.html'],['products','products/index.html'],['technology','technology/index.html'],
 ['research','research/index.html'],['tokenomics','research/tokenomics.html'],['knowledge','knowledge/index.html'],
 ['library','knowledge/library.html'],['guide-income','knowledge/guide.html?id=knowledge.income'],
 ['guide-practice','knowledge/guide.html?id=knowledge.practice'],['explorer','explorer/index.html'],
 ['entity-router','explorer/entity.html?id=fin.router'],['entity-token','explorer/entity.html?id=token.syna'],
 ['graph-router','explorer/graph.html?focus=fin.router'],['graph-midas','explorer/graph.html?focus=product.midas'],
 ['evidence','explorer/evidence.html'],['repositories','explorer/repositories.html'],['coverage','explorer/coverage.html'],
 ['archive','archive/index.html']
];

const manifest=JSON.parse(fs.readFileSync(path.join(root,'STANDALONE_MANIFEST.json'),'utf8'));
const covered=new Set(routes.map(([,r])=>r.split('?')[0]));
for(const p of manifest.pages.map(x=>x.path).sort()) if(!covered.has(p)){routes.push([`surface-${p.replace(/[^a-z0-9]+/gi,'-')}`,p]);covered.add(p)}
const screenshotNames=new Set(['home','financial','tokenomics','library','explorer','entity-router','graph-midas','coverage']);

const browser=await chromium.launch({headless:true});
const failures=[];

async function sweep(page){
 await page.evaluate(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const step=Math.max(520,Math.floor(innerHeight*.82));
  const max=Math.max(0,document.documentElement.scrollHeight-innerHeight);
  for(let y=0;y<=max;y+=step){scrollTo(0,Math.min(y,max));await sleep(35)}
  scrollTo(0,max);await sleep(60);scrollTo(0,0);await sleep(100);
 });
}

async function run(label,viewport,reducedMotion='no-preference'){
 const ctx=await browser.newContext({viewport,reducedMotion});
 for(const [name,rel] of routes){
  const page=await ctx.newPage();
  const errs=[]; const reqFails=[];
  page.on('pageerror',e=>errs.push(String(e)));
  page.on('requestfailed',r=>reqFails.push(`${r.method()} ${r.url()} :: ${r.failure()?.errorText||'failed'}`));
  const [pathname,query='']=rel.split('?');
  const url=pathToFileURL(path.join(root,pathname)).href+(query?`?${query}`:'');
  await page.goto(url,{waitUntil:'load',timeout:30000}).catch(e=>failures.push(`${label}/${name}: file navigation ${e}`));
  await page.waitForTimeout(reducedMotion==='reduce'?120:350);
  if(screenshotNames.has(name)&&reducedMotion!=='reduce') await sweep(page);
  const a=await page.evaluate(()=>{
   const viewW=document.documentElement.clientWidth||0;
   const cs=getComputedStyle(document.documentElement),bs=getComputedStyle(document.body);
   const nav=document.querySelector('.topbar');
   const mark=document.querySelector('.brand-mark');
   const canvas=document.querySelector('#motionCanvas');
   const localCss=[...document.querySelectorAll('link[rel="stylesheet"][href]')].map(x=>x.getAttribute('href')).filter(Boolean).filter(x=>!/^https?:|^data:|^\/\//i.test(x));
   const localScripts=[...document.querySelectorAll('script[src]')].map(x=>x.getAttribute('src')).filter(Boolean).filter(x=>!/^https?:|^data:|^\/\//i.test(x));
   const badDirs=[...document.querySelectorAll('a[href]')].map(x=>x.getAttribute('href')).filter(Boolean).filter(x=>!(/^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i.test(x))).filter(x=>(x.split(/[?#]/)[0]||'').endsWith('/')).slice(0,8);
   const offenders=[...document.querySelectorAll('body *')].map(el=>{const r=el.getBoundingClientRect();return {tag:el.tagName.toLowerCase(),cls:String(el.className||'').slice(0,70),right:Math.round(r.right),left:Math.round(r.left)}}).filter(x=>x.right>viewW+8||x.left<-8).slice(0,6);
   const hiddenInViewport=[...document.querySelectorAll('.reveal')].filter(el=>{const r=el.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight&&Number.parseFloat(getComputedStyle(el).opacity)<.5}).length;
   return {
    protocol:location.protocol,offline:document.documentElement.dataset.v18Offline,title:document.title,
    text:(document.body?.innerText||'').trim().length,
    inlineStyles:document.querySelectorAll('style[data-inline-source]').length,
    inlineScripts:document.querySelectorAll('script[data-inline-source]').length,
    localCss,localScripts,badDirs,hiddenInViewport,
    green:cs.getPropertyValue('--green').trim(),bodyBg:bs.backgroundColor,bodyColor:bs.color,
    nav:!!nav,navPos:nav?getComputedStyle(nav).position:'',markBg:mark?getComputedStyle(mark).backgroundImage:'',
    bg:!!document.querySelector('.v18-bg'),canvas:!!canvas,canvasWidth:canvas?.width||0,
    bodyW:document.body?.scrollWidth||0,viewW,offenders,
    guideCount:window.SINERGY_KNOWLEDGE?.length||0,entityCount:window.SINERGY_ENTITIES?.length||0,
    reduced:matchMedia('(prefers-reduced-motion: reduce)').matches
   };
  });
  if(a.protocol!=='file:') failures.push(`${label}/${name}: expected file:, got ${a.protocol}`);
  if(a.offline!=='standalone') failures.push(`${label}/${name}: offline router marker missing`);
  if(a.text<80) failures.push(`${label}/${name}: suspiciously little text ${a.text}`);
  if(!a.nav||!a.bg) failures.push(`${label}/${name}: design shell missing nav=${a.nav} bg=${a.bg}`);
  if(a.inlineStyles<1) failures.push(`${label}/${name}: shared CSS was not inlined`);
  if(a.localCss.length||a.localScripts.length) failures.push(`${label}/${name}: residual local dependencies css=${a.localCss} js=${a.localScripts}`);
  if(!a.green||a.green==='#000000') failures.push(`${label}/${name}: design token --green missing (${a.green})`);
  if(!a.bodyBg||a.bodyBg==='rgba(0, 0, 0, 0)'||a.bodyBg==='transparent') failures.push(`${label}/${name}: body design background missing (${a.bodyBg})`);
  if(a.bodyW>a.viewW+8) failures.push(`${label}/${name}: horizontal overflow ${a.bodyW-a.viewW}px offenders=${JSON.stringify(a.offenders)}`);
  if(a.badDirs.length) failures.push(`${label}/${name}: file:// directory hrefs remain ${JSON.stringify(a.badDirs)}`);
  if(a.hiddenInViewport) failures.push(`${label}/${name}: ${a.hiddenInViewport} reveal element(s) hidden in current viewport`);
  if(name==='library'&&a.guideCount!==7) failures.push(`${label}/${name}: knowledge registry missing (${a.guideCount})`);
  if(name==='entity-router'&&a.entityCount<80) failures.push(`${label}/${name}: entity registry missing (${a.entityCount})`);
  if(reducedMotion==='reduce'&&!a.reduced) failures.push(`${label}/${name}: reduced motion not active`);
  if(errs.length) failures.push(`${label}/${name}: page errors ${errs.join(' | ')}`);
  if(reqFails.length) failures.push(`${label}/${name}: request failures ${reqFails.join(' | ')}`);
  if(screenshotNames.has(name)) await page.screenshot({path:path.join(out,`${label}-${name}.png`),fullPage:true});
  await page.close();
 }
 await ctx.close();
}

await run('file-desktop',{width:1440,height:1000});
await run('file-mobile',{width:390,height:844});
const reduce=await browser.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});
const p=await reduce.newPage();await p.goto(pathToFileURL(path.join(root,'index.html')).href,{waitUntil:'load'});await p.waitForTimeout(120);
const rr=await p.evaluate(()=>({reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,offline:document.documentElement.dataset.v18Offline,green:getComputedStyle(document.documentElement).getPropertyValue('--green').trim(),hidden:[...document.querySelectorAll('.reveal')].filter(el=>Number.parseFloat(getComputedStyle(el).opacity)<.5).length}));
if(!rr.reduced||rr.offline!=='standalone'||!rr.green||rr.hidden) failures.push(`file-reduced-motion failed ${JSON.stringify(rr)}`);
await p.screenshot({path:path.join(out,'file-reduced-motion-home.png'),fullPage:true});await reduce.close();
await browser.close();
if(failures.length){console.error(failures.join('\n'));process.exit(1)}
console.log(`V18 FILE:// STANDALONE SMOKE: PASS (${routes.length} routes × desktop/mobile + reduced motion; ${manifest.pages.length}/${manifest.pages.length} physical HTML surfaces covered)`);
