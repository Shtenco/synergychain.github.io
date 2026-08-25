from pathlib import Path

ROOT = Path('/tmp/smm-v31')
app = ROOT / 'android/app/src/main/assets/www/js/app.js'
e2e = ROOT / 'tests/web/e2e.py'

def replace_required(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f'missing patch anchor: {label}')
    return text.replace(old, new, 1)

s = app.read_text()
s = replace_required(
    s,
    "ROUTES=['home','studio','content','inbox','crm','audience','autopilot','channels','analytics','files','integrations','settings']",
    "ROUTES=['home','studio','content','inbox','crm','audience','autopilot','actions','channels','analytics','files','integrations','settings']",
    'actions route registry',
)
s = replace_required(
    s,
    "integrations:renderIntegrations,settings:renderSettings}[r]",
    "integrations:renderIntegrations,settings:renderSettings,actions:()=>window.SMM_ACTIONS?.render?.()}[r]",
    'actions route renderer',
)
s = replace_required(
    s,
    "function actionEsc(s){return esc(String(s??''))}",
    "function actionEsc(s){return String(s??'').replace(/[&<>\\\"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;',\"'\":'&#39;'}[m]))}\nfunction actionCoreState(){try{return window.SinergySMM?.getState?.()||{}}catch{return {}}}\nfunction actionLog(level,message){try{console.log('SINERGY_SMM_ACTION',level,message)}catch{}}",
    'standalone action helpers',
)
for old, new, label in [
    ("log('INFO','ACTION '+a.id+' CONFIRMED local')", "actionLog('INFO','ACTION '+a.id+' CONFIRMED local')", 'local action log'),
    ("const base=(state.backendUrl||'').replace(/\\/$/,'');", "const base=(actionCoreState().backendUrl||'').replace(/\\/$/,'');", 'public backend state'),
    ("log('WARN','ACTION '+a.id+' UNSUPPORTED backend_not_configured')", "actionLog('WARN','ACTION '+a.id+' UNSUPPORTED backend_not_configured')", 'unsupported action log'),
    ("log(data.status==='FAILED'?'WARN':'INFO','ACTION '+a.id+' '+data.status)", "actionLog(data.status==='FAILED'?'WARN':'INFO','ACTION '+a.id+' '+data.status)", 'result action log'),
    ("log('WARN','ACTION '+a.id+' FAILED '+e.message)", "actionLog('WARN','ACTION '+a.id+' FAILED '+e.message)", 'failed action log'),
]:
    s = replace_required(s, old, new, label)
app.write_text(s)

s = e2e.read_text()
s = replace_required(
    s,
    "    dump=page.evaluate('localStorage._dump()')\n    page.set_content(doc(dump),wait_until='domcontentloaded')",
    "    dump=page.evaluate('localStorage._dump()')\n    page.close(); page=ctx.new_page()\n    page.on('pageerror',lambda e: errors.append('PAGEERROR '+str(e)))\n    page.on('console',lambda m: errors.append('CONSOLE '+m.text) if m.type=='error' else None)\n    page.set_content(doc(dump),wait_until='domcontentloaded')",
    'fresh page persistence simulation',
)
s = replace_required(
    s,
    "    # corrupted storage recovery\n    page.set_content(doc({'sinergy_smm_state_v1':'{bad json'}),wait_until='domcontentloaded')",
    "    # corrupted storage recovery on a fresh page, matching Android/WebView restart\n    page.close(); page=ctx.new_page()\n    page.on('pageerror',lambda e: errors.append('PAGEERROR '+str(e)))\n    page.on('console',lambda m: errors.append('CONSOLE '+m.text) if m.type=='error' else None)\n    page.set_content(doc({'sinergy_smm_state_v1':'{bad json'}),wait_until='domcontentloaded')",
    'fresh page corrupted-storage recovery',
)
e2e.write_text(s)

print('POST_BUILDER_FIX_PASS')
