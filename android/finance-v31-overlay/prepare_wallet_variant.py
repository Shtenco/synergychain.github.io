#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

EXCHANGE_PANEL = r'''
        <section class="panel section-card sinergy-exchange" id="sinergyExchange">
          <div class="card-label"><span>ОБМЕН RUB · BYN · CRYPTO</span><span>FREE2EX · BYNEX CONNECTORS</span></div>
          <div class="security-note"><b>NON-CUSTODIAL</b><span>Ключи кошелька не передаются обменнику. Котировка и заявка формируются отдельно; on-chain перевод подписывается только локально после подтверждения пользователя.</span></div>
          <div class="exchange-grid">
            <label>Отдаю<select id="exchangeFrom"><option>RUB</option><option>BYN</option><option>USDT</option><option>BTC</option><option>ETH</option></select></label>
            <label>Получаю<select id="exchangeTo"><option>USDT</option><option>BYN</option><option>RUB</option><option>BTC</option><option>ETH</option></select></label>
            <label>Сумма<input id="exchangeAmount" type="number" min="0" step="any" value="10000"></label>
            <label>Провайдер<select id="exchangeProvider"><option value="auto">Лучший доступный</option><option value="free2ex">FREE2EX API</option><option value="bynex">BYNEX partner connector</option></select></label>
          </div>
          <div class="exchange-actions"><button class="btn primary" id="exchangeQuote">Получить котировку</button><button class="btn ghost" id="exchangeOpenProvider">Открыть провайдера</button></div>
          <div id="exchangeResult" class="exchange-result"><p class="muted">Курс RUB/BYN берётся из официального API НБРБ. Крипто-котировки — из подключенного API белорусского оператора.</p></div>
          <details class="exchange-settings"><summary>Настройки API провайдеров</summary>
            <label>FREE2EX WebREST base URL<input id="free2exBaseUrl" value="https://cryptottlivewebapi.free2ex.net:8443"></label>
            <label>FREE2EX public ticks path<input id="free2exTicksPath" value="/api/v1/public/ticks"></label>
            <label>BYNEX partner endpoint<input id="bynexApiUrl" placeholder="Выдаётся BYNEX по партнёрскому/API-договору"></label>
            <p class="form-note">Секретные API-ключи не сохраняются в WebView. Для реальной торговли нужен серверный прокси/partner backend с KYC/AML и подписью запросов. В приложении оставлены только публичные котировки и безопасный hand-off.</p>
          </details>
        </section>
'''

EXCHANGE_CSS = r'''
<style id="sinergy-wallet-only-style">
  body.wallet-only .route:not([data-page="wallet"]){display:none!important}
  body.wallet-only [data-route]:not([data-route="wallet"]){display:none!important}
  body.wallet-only .sidebar nav{min-height:0}
  body.wallet-only .wallet-page-head h1{letter-spacing:.03em}
  .sinergy-exchange{margin-top:24px}
  .exchange-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}
  .exchange-grid label,.exchange-settings label{display:flex;flex-direction:column;gap:7px;font-size:12px;color:#9db8ad}
  .exchange-grid input,.exchange-grid select,.exchange-settings input{width:100%;background:#071b15;border:1px solid rgba(0,239,115,.2);color:#fff;border-radius:12px;padding:12px}
  .exchange-actions{display:flex;gap:10px;flex-wrap:wrap}
  .exchange-result{margin-top:16px;padding:16px;border-radius:14px;background:rgba(0,239,115,.06);border:1px solid rgba(0,239,115,.16)}
  .exchange-result strong{font-size:24px;display:block;margin:8px 0}
  .exchange-settings{margin-top:16px}.exchange-settings summary{cursor:pointer;color:#00ef73}.exchange-settings label{margin-top:12px}
  .provider-pill{display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:999px;background:#103c2e;color:#5cff9f;font-size:11px;font-weight:700}
  @media(max-width:900px){.exchange-grid{grid-template-columns:1fr 1fr}}
  @media(max-width:560px){.exchange-grid{grid-template-columns:1fr}}
</style>
'''

EXCHANGE_JS = r'''(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const cfgKey = 'sinergy_wallet_exchange_config_v1';
  const providerLinks = {free2ex:'https://free2ex.ru/', bynex:'https://bynex.io/'};
  const crypto = new Set(['USDT','BTC','ETH']);
  const fiat = new Set(['RUB','BYN']);
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  function loadCfg(){
    try{return JSON.parse(localStorage.getItem(cfgKey)||'{}')}catch{return{}}
  }
  function saveCfg(){
    const cfg={free2exBaseUrl:$('#free2exBaseUrl')?.value.trim(),free2exTicksPath:$('#free2exTicksPath')?.value.trim(),bynexApiUrl:$('#bynexApiUrl')?.value.trim()};
    localStorage.setItem(cfgKey,JSON.stringify(cfg));return cfg;
  }
  function restoreCfg(){const c=loadCfg();for(const k of ['free2exBaseUrl','free2exTicksPath','bynexApiUrl'])if(c[k]&&$('#'+k))$('#'+k).value=c[k]}
  function setResult(html){const n=$('#exchangeResult');if(n)n.innerHTML=html}
  function num(v){const n=Number(v);if(!Number.isFinite(n)||n<=0)throw new Error('Введите положительную сумму');return n}
  async function getRubByn(){
    const r=await fetch('https://api.nbrb.by/exrates/rates/RUB?parammode=2',{headers:{Accept:'application/json'}});
    if(!r.ok)throw new Error('НБРБ: HTTP '+r.status);
    const d=await r.json();
    return {bynPerRub:Number(d.Cur_OfficialRate)/Number(d.Cur_Scale),date:d.Date,source:'НБРБ'};
  }
  function normalizeSymbol(s){return String(s||'').toUpperCase().replace(/[^A-Z0-9]/g,'')}
  function pickTick(ticks, base, quote){
    const wanted=[base+quote,base+'/'+quote,base+'_'+quote,base+'-'+quote].map(normalizeSymbol);
    const all=Array.isArray(ticks)?ticks:(ticks?.Ticks||ticks?.ticks||ticks?.data||ticks?.Result?.Ticks||[]);
    return all.find(t=>wanted.includes(normalizeSymbol(t.Symbol||t.symbol||t.ticker_id||t.id)));
  }
  function priceFromTick(t, side){
    if(!t)return null;
    const bid=Number(t.BestBid?.Price ?? t.bid ?? t.bidPrice ?? t.Bid);
    const ask=Number(t.BestAsk?.Price ?? t.ask ?? t.askPrice ?? t.Ask);
    const last=Number(t.last_price ?? t.lastPrice ?? t.Last ?? t.price);
    const p=side==='buy'?(ask||last||bid):(bid||last||ask);
    return Number.isFinite(p)&&p>0?p:null;
  }
  async function free2exTick(base,quote){
    const c=saveCfg();
    const url=(c.free2exBaseUrl||'').replace(/\/$/,'')+(c.free2exTicksPath||'/api/v1/public/ticks');
    const r=await fetch(url,{headers:{Accept:'application/json'}});
    if(!r.ok)throw new Error('FREE2EX API: HTTP '+r.status);
    const data=await r.json();
    const direct=pickTick(data,base,quote);if(direct){const p=priceFromTick(direct,'sell');if(p)return {price:p,symbol:base+'/'+quote,raw:direct}}
    const inverse=pickTick(data,quote,base);if(inverse){const p=priceFromTick(inverse,'buy');if(p)return {price:1/p,symbol:base+'/'+quote,raw:inverse}}
    throw new Error('FREE2EX: пара '+base+'/'+quote+' не найдена в публичных тиках');
  }
  async function bynexQuote(from,to,amount){
    const c=saveCfg();
    if(!c.bynexApiUrl)throw new Error('BYNEX: публичный partner endpoint не настроен');
    const u=new URL(c.bynexApiUrl);u.searchParams.set('from',from);u.searchParams.set('to',to);u.searchParams.set('amount',String(amount));
    const r=await fetch(u.toString(),{headers:{Accept:'application/json'}});if(!r.ok)throw new Error('BYNEX API: HTTP '+r.status);
    const d=await r.json();const out=Number(d.amountOut??d.result??d.toAmount);if(!Number.isFinite(out))throw new Error('BYNEX: неизвестный формат ответа');
    return {amountOut:out,rate:out/amount,provider:'BYNEX'};
  }
  async function free2exQuote(from,to,amount){
    if(from==='RUB'&&to==='BYN'){const fx=await getRubByn();return {amountOut:amount*fx.bynPerRub,rate:fx.bynPerRub,provider:'НБРБ / FREE2EX route',detail:'Официальный fiat leg'}}
    if(from==='BYN'&&to==='RUB'){const fx=await getRubByn();return {amountOut:amount/fx.bynPerRub,rate:1/fx.bynPerRub,provider:'НБРБ / FREE2EX route',detail:'Официальный fiat leg'}}
    let rubByn=null;
    if(from==='RUB'||to==='RUB')rubByn=await getRubByn();
    let source=from,target=to,sourceAmount=amount;
    if(from==='RUB'){source='BYN';sourceAmount=amount*rubByn.bynPerRub}
    if(to==='RUB')target='BYN';
    let out;
    if(source===target)out=sourceAmount;
    else if(fiat.has(source)&&crypto.has(target)){
      const tick=await free2exTick(target,source);out=sourceAmount/tick.price;
    }else if(crypto.has(source)&&fiat.has(target)){
      const tick=await free2exTick(source,target);out=sourceAmount*tick.price;
    }else if(crypto.has(source)&&crypto.has(target)){
      const tick=await free2exTick(source,target);out=sourceAmount*tick.price;
    }else throw new Error('Маршрут не поддерживается');
    if(to==='RUB')out=out/rubByn.bynPerRub;
    return {amountOut:out,rate:out/amount,provider:'FREE2EX WebREST',detail:'Публичная котировка; исполнение требует KYC/API account'};
  }
  async function quote(){
    try{
      const from=$('#exchangeFrom').value,to=$('#exchangeTo').value,amount=num($('#exchangeAmount').value),pref=$('#exchangeProvider').value;
      if(from===to)throw new Error('Выберите разные активы');
      setResult('<p class="muted">Запрашиваю котировки…</p>');
      let q;
      if(pref==='bynex')q=await bynexQuote(from,to,amount);
      else if(pref==='free2ex')q=await free2exQuote(from,to,amount);
      else{
        try{q=await free2exQuote(from,to,amount)}catch(e){q=await bynexQuote(from,to,amount)}
      }
      setResult(`<span class="provider-pill">${esc(q.provider)}</span><strong>${amount.toLocaleString('ru-RU')} ${from} → ${Number(q.amountOut).toLocaleString('ru-RU',{maximumFractionDigits:8})} ${to}</strong><div>Курс: 1 ${from} = ${Number(q.rate).toLocaleString('ru-RU',{maximumFractionDigits:10})} ${to}</div><p class="form-note">${esc(q.detail||'Перед подтверждением проверьте итоговую комиссию и реквизиты у оператора.')}</p>`);
    }catch(e){setResult(`<b style="color:#ff867f">Котировка недоступна</b><p>${esc(e.message||e)}</p><p class="form-note">Кошелёк продолжает работать некастодиально. Для реального API-исполнения подключите partner credentials через отдельный backend — секреты нельзя хранить внутри APK.</p>`)}
  }
  function openProvider(){
    const p=$('#exchangeProvider').value==='bynex'?'bynex':'free2ex';
    const url=providerLinks[p];
    try{if(window.SinergyWalletNative?.openExternalUrl)window.SinergyWalletNative.openExternalUrl(url);else location.href=url}catch{location.href=url}
  }
  function forceWalletRoute(){
    document.body.classList.add('wallet-only');
    document.querySelectorAll('.route').forEach(x=>x.classList.toggle('active',x.dataset.page==='wallet'));
    document.querySelectorAll('[data-route]').forEach(x=>x.classList.toggle('active',x.dataset.route==='wallet'));
    history.replaceState(null,'','#wallet');
  }
  document.addEventListener('DOMContentLoaded',()=>{
    restoreCfg();forceWalletRoute();
    $('#exchangeQuote')?.addEventListener('click',quote);
    $('#exchangeOpenProvider')?.addEventListener('click',openProvider);
    ['free2exBaseUrl','free2exTicksPath','bynexApiUrl'].forEach(id=>$('#'+id)?.addEventListener('change',saveCfg));
    setTimeout(forceWalletRoute,300);
  });
})();
'''


def patch_gradle(path: Path):
    text=path.read_text(encoding='utf-8')
    text=re.sub(r"applicationId\s+['\"][^'\"]+['\"]","applicationId 'ai.sinergy.wallet'",text,count=1)
    text=re.sub(r"versionName\s+['\"][^'\"]+['\"]","versionName '1.0.0'",text,count=1)
    text=re.sub(r'\bversionCode\s+\d+','versionCode 1',text,count=1)
    path.write_text(text,encoding='utf-8')


def patch_brand_label(values_file: Path):
    text=values_file.read_text(encoding='utf-8')
    text=re.sub(r'<string name="app_name">.*?</string>','<string name="app_name">SINERGY_WALLET</string>',text,count=1)
    values_file.write_text(text,encoding='utf-8')


def patch_index(index: Path):
    html=index.read_text(encoding='utf-8')
    html=html.replace('<title>SINERGY Finance</title>','<title>SINERGY_WALLET</title>')
    html=html.replace('SINERGY FINANCE','SINERGY_WALLET').replace('SINERGY Finance','SINERGY_WALLET')
    start=html.find('<section class="route" data-page="wallet">')
    if start<0: raise RuntimeError('wallet route not found')
    nxt=html.find('<section class="route"',start+20)
    if nxt<0: raise RuntimeError('next route marker not found')
    html=html[:nxt]+EXCHANGE_PANEL+'\n'+html[nxt:]
    html=html.replace('</head>',EXCHANGE_CSS+'\n</head>',1)
    html=html.replace('</body>','  <script src="js/exchange-belarus.js"></script>\n</body>',1)
    index.write_text(html,encoding='utf-8')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('app_dir',type=Path);args=ap.parse_args()
    app=args.app_dir;www=app/'src/main/assets/www'
    patch_gradle(app/'build.gradle')
    patch_brand_label(app/'src/main/res/values/sinergy_branding.xml')
    patch_brand_label(app/'src/main/res/values-v31/sinergy_branding.xml')
    patch_index(www/'index.html')
    (www/'js/exchange-belarus.js').write_text(EXCHANGE_JS,encoding='utf-8')
    print('WALLET_VARIANT_OK applicationId=ai.sinergy.wallet label=SINERGY_WALLET providers=FREE2EX,BYNEX,NBRB')

if __name__=='__main__': main()
