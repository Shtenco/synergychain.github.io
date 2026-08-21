import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT=process.cwd();
const V18=path.join(ROOT,'v18');
const errors=[];
const warnings=[];
const fail=(m)=>errors.push(m);
const warn=(m)=>warnings.push(m);
const read=p=>fs.readFileSync(path.join(ROOT,p),'utf8');
const exists=p=>fs.existsSync(path.join(ROOT,p));

function walk(dir, ext=null){
  const out=[];
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,ent.name);
    if(ent.isDirectory()) out.push(...walk(p,ext));
    else if(!ext||p.endsWith(ext)) out.push(p);
  }
  return out;
}
function loadData(files){
  const context={window:{}};vm.createContext(context);
  for(const f of files) vm.runInContext(read(f),context,{filename:f});
  return context.window;
}
const data=loadData(['v18/data/entities.js','v18/data/taxonomy.js','v18/data/edges.js','v18/data/evidence.js','v18/data/repositories.js','v18/data/knowledge.js']);
const entities=data.SINERGY_ENTITIES||[], edges=data.SINERGY_EDGES||[], evidence=data.SINERGY_EVIDENCE||[], repos=data.SINERGY_REPOSITORIES||[], knowledge=data.SINERGY_KNOWLEDGE||[];
const entityIds=new Set();
for(const e of entities){
  if(!e.id) fail('entity without id');
  if(entityIds.has(e.id)) fail(`duplicate entity id: ${e.id}`); entityIds.add(e.id);
  for(const key of ['name','domain','entityType','status','evidence','summary']) if(!e[key]) fail(`${e.id}: missing ${key}`);
  if(e.domain==='Токены') fail(`${e.id}: legacy top-level token domain returned; use Исследования → Tokenomics`);
}
const allowedDomains=new Set(['Модель','Financial OS','Институты','Продукты','Технологии','Исследования','Знания','Архив']);
for(const e of entities) if(!allowedDomains.has(e.domain)) fail(`${e.id}: unknown domain ${e.domain}`);

const edgeTypes=new Set(['depends_on','funds','creates_claim','governed_by','settles_into','evidence_for','supersedes','contradicts']);
for(const x of edges){
  if(!entityIds.has(x.from)) fail(`edge.from unknown: ${x.from}`);
  if(!entityIds.has(x.to)) fail(`edge.to unknown: ${x.to}`);
  if(!edgeTypes.has(x.type)) fail(`edge type unknown: ${x.type}`);
}
const evidenceIds=new Set();
for(const x of evidence){
  if(evidenceIds.has(x.id)) fail(`duplicate evidence id: ${x.id}`); evidenceIds.add(x.id);
  if(!['supports','contradicts','insufficient'].includes(x.status)) fail(`${x.id}: bad evidence status ${x.status}`);
  if(!Array.isArray(x.entities)||!x.entities.length) fail(`${x.id}: no entity binding`);
  for(const id of x.entities||[]) if(!entityIds.has(id)) fail(`${x.id}: unknown entity ${id}`);
}
for(const r of repos){
  if(!r.repo) fail('repository row without repo');
  for(const id of r.entities||[]) if(!entityIds.has(id)) fail(`${r.repo}: unknown entity ${id}`);
}
const knowledgeIds=new Set();
for(const k of knowledge){
  if(knowledgeIds.has(k.id)) fail(`duplicate knowledge id: ${k.id}`);knowledgeIds.add(k.id);
  if(!entityIds.has(k.id)) fail(`knowledge registry id missing from entity registry: ${k.id}`);
  if(!Number.isInteger(k.pages)||k.pages<=0) fail(`${k.id}: invalid pages`);
  if(!Array.isArray(k.chapters)||k.chapters.length<5) fail(`${k.id}: insufficient semantic chapters`);
}

// Validate entity deep links as they resolve from Explorer.
for(const e of entities){
  if(!e.href) continue;
  const resolved=path.normalize(path.join(V18,'explorer',String(e.href).split(/[?#]/)[0]));
  let ok=fs.existsSync(resolved);
  if(ok&&fs.statSync(resolved).isDirectory()) ok=fs.existsSync(path.join(resolved,'index.html'));
  if(!ok) fail(`${e.id}: broken entity href ${e.href}`);
}

// Local href/src integrity across all V18 HTML.
const htmlFiles=walk(V18,'.html');
const attrRe=/(?:href|src)=["']([^"']+)["']/g;
for(const file of htmlFiles){
  const text=fs.readFileSync(file,'utf8');
  let m;
  while((m=attrRe.exec(text))){
    const raw=m[1];
    if(!raw||raw.startsWith('#')||/^(https?:|mailto:|tel:|data:|javascript:)/i.test(raw)) continue;
    const clean=raw.split(/[?#]/)[0]; if(!clean) continue;
    const target=clean.startsWith('/')?path.join(ROOT,clean.replace(/^\//,'')):path.resolve(path.dirname(file),clean);
    let ok=fs.existsSync(target);
    if(ok&&fs.statSync(target).isDirectory()) ok=fs.existsSync(path.join(target,'index.html'));
    if(!ok) fail(`${path.relative(ROOT,file)}: broken local ref ${raw}`);
  }
  if(/target=["']_blank["']/i.test(text)&&!(/rel=["'][^"']*noopener/i.test(text))) warn(`${path.relative(ROOT,file)}: target=_blank without noopener somewhere`);
}

// Secret-like assignments: deliberately narrow to avoid prose false positives.
const secretRe=/(api[_-]?key|private[_-]?key|secret|seed|mnemonic)\s*[:=]\s*["'][A-Za-z0-9_\/+=.-]{16,}["']/ig;
for(const file of walk(V18)){
  if(!/\.(html|js|json|md|css)$/i.test(file)) continue;
  const text=fs.readFileSync(file,'utf8');
  if(secretRe.test(text)) fail(`${path.relative(ROOT,file)}: secret-like assignment detected`);
  secretRe.lastIndex=0;
}

// Shared runtime expectations.
for(const file of htmlFiles){
  const rel=path.relative(ROOT,file).replaceAll('\\','/'),text=fs.readFileSync(file,'utf8');
  if(!text.includes('sinergy-v18.css')) warn(`${rel}: not using shared V18 CSS`);
  if(!text.includes('sinergy-v18.js')) warn(`${rel}: not using shared V18 runtime`);
}

console.log(`V18 entities: ${entities.length}`);
console.log(`V18 edges: ${edges.length}`);
console.log(`V18 evidence artifacts: ${evidence.length}`);
console.log(`V18 repository bindings: ${repos.length}`);
console.log(`V18 knowledge guides: ${knowledge.length}, source pages: ${knowledge.reduce((a,x)=>a+x.pages,0)}`);
console.log(`V18 HTML pages checked: ${htmlFiles.length}`);
for(const w of warnings) console.warn('WARN:',w);
if(errors.length){for(const e of errors) console.error('ERROR:',e);console.error(`FAILED with ${errors.length} error(s)`);process.exit(1)}
console.log('V18 STRUCTURAL VALIDATION: PASS');
