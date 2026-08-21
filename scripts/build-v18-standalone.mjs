import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const sourceRoot=path.resolve(process.argv[2]||'v18');
const outRoot=path.resolve(process.argv[3]||'release/V18_STANDALONE');

if(!fs.existsSync(sourceRoot)) throw new Error(`Missing source root: ${sourceRoot}`);
fs.rmSync(outRoot,{recursive:true,force:true});
fs.mkdirSync(outRoot,{recursive:true});

const htmlFiles=[];
function walk(dir){
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,ent.name);
    if(ent.isDirectory()) walk(p);
    else if(ent.isFile()&&ent.name.endsWith('.html')) htmlFiles.push(p);
  }
}
walk(sourceRoot);

const isRemote=s=>/^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i.test(s);
const escScript=s=>s.replace(/<\/script/gi,'<\\/script');
const sha256=b=>crypto.createHash('sha256').update(b).digest('hex');

function resolveLocal(pageFile,ref){
  const clean=ref.split('#')[0].split('?')[0];
  return path.resolve(path.dirname(pageFile),clean);
}

function rewriteDirectoryHref(ref){
  if(!ref||isRemote(ref)||ref.startsWith('mailto:')||ref.startsWith('tel:')||ref.startsWith('javascript:')) return ref;
  const m=ref.match(/^([^?#]*)([?#].*)?$/);
  if(!m) return ref;
  let pathname=m[1],suffix=m[2]||'';
  if(pathname.endsWith('/')) pathname+='index.html';
  return pathname+suffix;
}

const offlineRouter=`<script data-v18-offline-router>(function(){\nconst remote=/^(?:[a-z][a-z0-9+.-]*:|\\/\\/|#)/i;\nfunction fix(a){const raw=a.getAttribute('href');if(!raw||remote.test(raw)||raw.startsWith('mailto:')||raw.startsWith('tel:')||raw.startsWith('javascript:'))return;const m=raw.match(/^([^?#]*)([?#].*)?$/);if(m&&m[1].endsWith('/'))a.setAttribute('href',m[1]+'index.html'+(m[2]||''));}\nfunction scan(root){if(root.nodeType===1&&root.matches?.('a[href]'))fix(root);root.querySelectorAll?.('a[href]').forEach(fix);}\nscan(document);new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(scan))).observe(document.documentElement,{childList:true,subtree:true});\ndocument.documentElement.dataset.v18Offline='standalone';\n})();<\/script>`;

const manifest={format:'sinergy-v18-standalone-v1',builtAt:new Date().toISOString(),sourceRoot:path.relative(process.cwd(),sourceRoot),pages:[]};

for(const src of htmlFiles){
  let html=fs.readFileSync(src,'utf8');
  const rel=path.relative(sourceRoot,src).split(path.sep).join('/');
  const inlined=[];

  html=html.replace(/<link\b([^>]*?)href=["']([^"']+)["']([^>]*?)>/gi,(tag,a,href,b)=>{
    if(isRemote(href)||!href.toLowerCase().split('?')[0].endsWith('.css')) return tag;
    const asset=resolveLocal(src,href);
    if(!fs.existsSync(asset)) throw new Error(`${rel}: missing CSS ${href}`);
    const css=fs.readFileSync(asset,'utf8');
    inlined.push({type:'css',ref:href,bytes:Buffer.byteLength(css),sha256:sha256(css)});
    return `<style data-inline-source="${href.replaceAll('"','&quot;')}">\n${css}\n</style>`;
  });

  html=html.replace(/<script\b([^>]*?)src=["']([^"']+)["']([^>]*)><\/script>/gi,(tag,a,srcRef,b)=>{
    if(isRemote(srcRef)) return tag;
    const asset=resolveLocal(src,srcRef);
    if(!fs.existsSync(asset)) throw new Error(`${rel}: missing JS ${srcRef}`);
    const js=fs.readFileSync(asset,'utf8');
    inlined.push({type:'js',ref:srcRef,bytes:Buffer.byteLength(js),sha256:sha256(js)});
    return `<script data-inline-source="${srcRef.replaceAll('"','&quot;')}">\n${escScript(js)}\n<\/script>`;
  });

  html=html.replace(/(<a\b[^>]*?\bhref=["'])([^"']+)(["'])/gi,(all,prefix,href,quote)=>prefix+rewriteDirectoryHref(href)+quote);

  if(!html.includes('data-v18-offline-router')) html=html.replace(/<\/body>/i,offlineRouter+'\n</body>');

  // A standalone page must not retain local stylesheet/script dependencies.
  const localCss=[...html.matchAll(/<link\b[^>]*href=["']([^"']+)["'][^>]*>/gi)].map(m=>m[1]).filter(x=>!isRemote(x));
  const localScripts=[...html.matchAll(/<script\b[^>]*src=["']([^"']+)["'][^>]*>/gi)].map(m=>m[1]).filter(x=>!isRemote(x));
  if(localCss.length||localScripts.length) throw new Error(`${rel}: residual local assets css=${localCss.join(',')} js=${localScripts.join(',')}`);

  const dst=path.join(outRoot,rel);
  fs.mkdirSync(path.dirname(dst),{recursive:true});
  fs.writeFileSync(dst,html);
  manifest.pages.push({path:rel,bytes:Buffer.byteLength(html),sha256:sha256(html),inlined});
}

// Offline entry points and integrity metadata.
const sums=[];
for(const p of manifest.pages) sums.push(`${p.sha256}  ${p.path}`);
fs.writeFileSync(path.join(outRoot,'STANDALONE_MANIFEST.json'),JSON.stringify(manifest,null,2));
fs.writeFileSync(path.join(outRoot,'SHA256SUMS.txt'),sums.join('\n')+'\n');
fs.writeFileSync(path.join(outRoot,'OPEN_ME.html'),`<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=index.html"><title>SINERGY V18 · OPEN ME</title><p><a href="index.html">Открыть SINERGY V18</a></p>`);
fs.writeFileSync(path.join(outRoot,'README_OFFLINE.txt'),`SINERGY V18 — OFFLINE / STANDALONE BUILD\n\n1. Распакуйте архив полностью.\n2. Откройте OPEN_ME.html или index.html двойным кликом.\n3. Сервер и интернет для CSS/JS не нужны: стили и runtime встроены в каждую HTML-страницу.\n4. Внутренние directory-links переписаны на explicit index.html для file://.\n\nPages: ${manifest.pages.length}\n`);

console.log(`V18 STANDALONE BUILD: PASS (${manifest.pages.length} HTML pages, CSS/JS inlined, file:// links normalized)`);
