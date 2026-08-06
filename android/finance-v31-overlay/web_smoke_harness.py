#!/usr/bin/env python3
"""Inject a deterministic browser smoke test into the extracted APK web assets."""

from pathlib import Path
import sys

MOCK = r'''
<script id="sinergy-smoke-native-mock">
(() => {
  const empty = {exists:false,address:'',securityLevel:'TEST_KEYSTORE',strongBoxAvailable:false};
  window.__sinergySmokeWallet = {...empty};
  const ok = (id, value) => setTimeout(() => window.SinergyWallet?.onNativeResult(id, true, JSON.stringify(value)), 5);
  window.Android = window.Android || {getPlatform:()=> 'android-smoke',getVersion:()=> '3.1.0',haptic:()=>{},openExternal:()=>{},exportFile:()=>{}};
  window.SinergyWalletNative = {
    capabilities: () => JSON.stringify({version:'3.1.0',localSigner:true,mnemonicCreate:true,mnemonicImport:true,multicurrencyAccounts:true,privateKeyExport:false}),
    status: id => ok(id, window.__sinergySmokeWallet),
    walletState: id => ok(id, {...window.__sinergySmokeWallet,balance:'0',nonce:'0'}),
    assetBalance: (id,n,t,d,s) => ok(id,{balance:'0',raw:'0',decimals:d,symbol:s||'TOKEN'}),
    createHdWallet: id => {
      window.__sinergySmokeWallet = {exists:true,address:'0x1111111111111111111111111111111111111111',securityLevel:'TEST_KEYSTORE',source:'BIP39_GENERATED',hdPath:"m/44'/60'/0'/0/0",mnemonic:'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about',mnemonicWords:12,backupRequired:true};
      ok(id, window.__sinergySmokeWallet);
    },
    importMnemonic: (id,m,p) => {
      window.__sinergySmokeWallet = {exists:true,address:'0x9858effd232b4033e47d90003d41ec34ecaeda94',securityLevel:'TEST_KEYSTORE',source:'BIP39_IMPORTED',hdPath:"m/44'/60'/0'/0/0",mnemonicWords:String(m||'').trim().split(/\s+/).length,imported:true};
      ok(id, window.__sinergySmokeWallet);
    }
  };
})();
</script>
'''

TEST = r'''
<script id="sinergy-browser-smoke-test">
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const waitFor = async (fn, message, timeout=10000) => {
    const start=Date.now();
    while(Date.now()-start<timeout){ try{if(fn())return;}catch{} await sleep(40); }
    throw new Error(message);
  };
  const finish = (ok, details) => {
    let pre=document.getElementById('sinergySmokeResult');
    if(!pre){pre=document.createElement('pre');pre.id='sinergySmokeResult';document.body.appendChild(pre);}
    pre.textContent=JSON.stringify({ok,...details},null,2);
    document.body.dataset.sinergySmoke=ok?'PASS':'FAIL';
    document.title=ok?'SINERGY_SMOKE_PASS':'SINERGY_SMOKE_FAIL';
  };
  try {
    await waitFor(() => window.SinergyApp?.getState, 'SinergyApp API did not initialize');
    await waitFor(() => document.readyState !== 'loading', 'DOMContentLoaded did not fire');
    await waitFor(() => document.querySelector('#accountForm [name="groupId"]')?.options?.length > 0, 'Finance event bindings/selects did not initialize');
    await waitFor(() => window.SinergyWallet?.onNativeResult, 'Wallet web layer did not initialize');
    await sleep(100);

    const phase=sessionStorage.getItem('sinergySmokePhase')||'reset';
    if(phase==='reset'){
      localStorage.clear();
      sessionStorage.setItem('sinergySmokePhase','create');
      location.reload();
      return;
    }
    if(phase==='create'){
      const createAccount=async(name,currency)=>{
        document.querySelector('[data-route="accounts"]').click();
        document.querySelector('[data-open="accountModal"]').click();
        const form=document.getElementById('accountForm');
        await waitFor(() => form.open !== false || document.getElementById('accountModal').open, 'Account dialog did not open');
        form.elements.name.value=name;
        form.elements.type.value='crypto';
        assert([...form.elements.currency.options].some(o=>o.value===currency),`Missing currency option ${currency}`);
        form.elements.currency.value=currency;
        form.elements.balance.value='1.25';
        form.requestSubmit(form.querySelector('[type="submit"]'));
        await waitFor(() => window.SinergyApp.getState().accounts.some(a=>a.currency===currency&&a.name===name),`Account ${currency} was not created`);
      };
      for(const [name,currency] of [['BTC Wallet','BTC'],['ETH Wallet','ETH'],['SYNA Wallet','SYNA'],['USDT Wallet','USDT']]) await createAccount(name,currency);
      const state=window.SinergyApp.getState();
      for(const code of ['BTC','ETH','SYNA','USDT']) assert(state.accounts.some(a=>a.currency===code),`Account ${code} was not created`);
      document.querySelector('[data-route="analytics"]').click();
      document.querySelector('#analyticsPeriod [data-period="all"]').click();
      await waitFor(() => window.SinergyApp.getState().profile.analyticsPeriod==='all','All-time analytics period failed');
      document.querySelector('#analyticsPeriod [data-period="custom"]').click();
      document.getElementById('analyticsFrom').value='2026-01-01';
      document.getElementById('analyticsTo').value='2026-12-31';
      document.getElementById('applyAnalyticsRange').click();
      await waitFor(() => {
        const p=window.SinergyApp.getState().profile;
        return p.analyticsPeriod==='custom'&&p.analyticsFrom==='2026-01-01'&&p.analyticsTo==='2026-12-31';
      },'Custom analytics range failed');
      assert((localStorage.getItem('sinergy_finance_state_v1')||'').includes('SYNA Wallet'),'Finance state was not written to localStorage');
      sessionStorage.setItem('sinergySmokePhase','verify');
      location.reload();
      return;
    }
    const persisted=window.SinergyApp.getState();
    for(const code of ['BTC','ETH','SYNA','USDT']) assert(persisted.accounts.some(a=>a.currency===code),`Persisted ${code} account missing`);
    document.querySelector('[data-route="wallet"]').click();
    document.getElementById('walletCreate').click();
    await waitFor(()=>document.getElementById('walletBackupModal').open,'Wallet backup dialog did not open');
    const words=[...document.querySelectorAll('#walletSeedGrid b')].map(x=>x.textContent.trim()).filter(Boolean);
    assert(words.length===12,`Expected 12 BIP39 words, got ${words.length}`);
    assert(document.getElementById('walletAddress').textContent.includes('0x1111'),'Generated wallet address was not rendered');
    finish(true,{accounts:persisted.accounts.filter(a=>['BTC','ETH','SYNA','USDT'].includes(a.currency)).map(a=>a.currency),analytics:persisted.profile.analyticsPeriod,localStorage:true,bip39Words:words.length});
  } catch (error) {
    finish(false,{error:String(error?.stack||error)});
  }
})();
</script>
'''


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: web_smoke_harness.py <www-dir>")
    www = Path(sys.argv[1]).resolve()
    index = www / "index.html"
    text = index.read_text(encoding="utf-8")
    marker = '<script src="js/wallet.js"></script>'
    if marker not in text:
        raise RuntimeError("wallet.js script marker not found")
    if 'sinergy-smoke-native-mock' not in text:
        text = text.replace(marker, MOCK + marker + TEST, 1)
    index.write_text(text, encoding="utf-8")
    print("Browser smoke harness injected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
