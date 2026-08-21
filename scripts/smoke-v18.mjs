import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const base=process.env.V18_BASE_URL||'http://127.0.0.1:8000/v18/';
const out=path.resolve('artifacts/v18-smoke');fs.mkdirSync(out,{recursive:true});
const routes=[
  ['home',''],['model','model/'],['financial','financial/'],['accounting','financial/accounting.html'],['money','financial/money.html'],['settlement','financial/settlement.html'],['bridge','financial/bridge.html'],['treasury','financial/treasury.html'],['qe','financial/qe-qt.html'],['liquidity','financial/liquidity.html'],['solvency','financial/solvency.html'],['profit','financial/profit.html'],['institutions','institutions/'],['products','products/'],['technology','technology/'],['research','research/'],['tokenomics','research/tokenomics.html'],['knowledge','knowledge/'],['library','knowledge/library.html'],['guide-income','knowledge/guide.html?id=knowledge.income'],['guide-practice','knowledge/guide.html?id=knowledge.practice'],['explorer','explorer/'],['entity-router','explorer/entity.html?id=fin.router'],['entity-token','explorer/entity.html?id=token.syna'],['graph-router','explorer/graph.html?focus=fin.router'],['graph-midas','explorer/graph.html?focus=product.midas'],['evidence','explorer/evidence.html'],['repositories','explorer/repositories.html'],['coverage','explorer/coverage.html'],['archive','archive/']
];
const browser=await chromium.launch({headless:true});
let failures=[];
async function runViewport(label,viewport,reducedMotion='no-preference'){
  const ctx=await browser.newContext({viewport,reducedMotion});
  for(const [name,rel] of routes){
    const page=await ctx.newPage();const errs=[];const reqFails=[];
    page.on('pageerror',e=>errs.push(String(e)));
    page.on('requestfailed',r=>reqFails.push(`${r.method()} ${r.url()} :: ${r.failure()?.errorText||'failed'}`));
    const url=new URL(rel,base).href;
    const res=await page.goto(url,{waitUntil:'networkidle',timeout:30000}).catch(e=>{failures.push(`${label}/${name}: navigation ${e}`);return null});
    if(!res||res.status()>=400) failures.push(`${label}/${name}: HTTP ${res?.status()||'NO_RESPONSE'} ${url}`);
    await page.waitForTimeout(reducedMotion==='reduce'?80:220);
    const audit=await page.evaluate(()=>({
      title:document.title,
      text:(document.body?.innerText||'').trim().length,
      bodyW:document.body?.scrollWidth||0,
      viewW:document.documentElement.clientWidth||0,
      canvas:!!document.querySelector('#motionCanvas'),
      bg:!!document.querySelector('.v18-bg'),
      nav:!!document.querySelector('.topbar'),
      reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,
      entityCount:window.SINERGY_ENTITIES?.length||0,
      guideCount:window.SINERGY_KNOWLEDGE?.length||0
    }));
    if(audit.text<80) failures.push(`${label}/${name}: suspiciously little visible text (${audit.text})`);
    if(!audit.nav) failures.push(`${label}/${name}: missing topbar`);
    if(!audit.bg) failures.push(`${label}/${name}: missing optical background`);
    if(audit.bodyW>audit.viewW+8) failures.push(`${label}/${name}: horizontal overflow ${audit.bodyW-audit.viewW}px`);
    if(reducedMotion==='reduce'&&!audit.reduced) failures.push(`${label}/${name}: reduced-motion emulation not active`);
    if(name==='entity-token'){
      const body=await page.textContent('body');
      if(!body?.includes('Tokenomics')||!body?.includes('Исследования')) failures.push(`${label}/${name}: token taxonomy overlay not visible`);
    }
    if(name==='library'){
      const body=await page.textContent('body');
      if(!body?.includes('846')||audit.guideCount!==7) failures.push(`${label}/${name}: expected 7 guides / 846 pages`);
    }
    if(errs.length) failures.push(`${label}/${name}: page errors: ${errs.join(' | ')}`);
    if(reqFails.length) failures.push(`${label}/${name}: request failures: ${reqFails.join(' | ')}`);
    if(['home','financial','tokenomics','library','explorer','entity-router','graph-midas','coverage'].includes(name)) await page.screenshot({path:path.join(out,`${label}-${name}.png`),fullPage:true});
    await page.close();
  }
  await ctx.close();
}
await runViewport('desktop',{width:1440,height:1000});
await runViewport('mobile',{width:390,height:844});
const reduceCtx=await browser.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});
const reducePage=await reduceCtx.newPage();await reducePage.goto(base,{waitUntil:'networkidle'});const reduceAudit=await reducePage.evaluate(()=>({reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,canvas:!!document.querySelector('#motionCanvas'),canvasPixels:document.querySelector('#motionCanvas')?.width||0}));if(!reduceAudit.reduced)failures.push('reduced-motion: media query false');
await reducePage.screenshot({path:path.join(out,'reduced-motion-home.png'),fullPage:true});await reduceCtx.close();
await browser.close();
if(failures.length){console.error(failures.join('\n'));process.exit(1)}
console.log(`V18 CHROMIUM SMOKE: PASS (${routes.length} routes × desktop/mobile + reduced motion)`);
