#!/usr/bin/env bash
set -euo pipefail

APK="${1:?usage: emulator_smoke.sh <apk> [output-dir]}"
OUT="${2:-android/emulator-smoke}"
PKG='ai.sinergy.finance.wallet'
ACT='ai.sinergy.finance.MainActivity'
mkdir -p "$OUT"

log(){ printf '[SMOKE] %s\n' "$*" | tee -a "$OUT/result.log"; }
fail(){ log "FAIL: $*"; exit 1; }

adb wait-for-device
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb shell locksettings set-pin 1234 >/dev/null 2>&1 || true
adb shell input keyevent 82 || true

log "Installing signed release APK"
adb install -r -t "$APK" | tee "$OUT/install.txt"
adb shell pm list packages | grep -q "package:${PKG}" || fail 'package not installed'

uia_dump(){
  local name="$1"
  adb shell uiautomator dump "/sdcard/${name}.xml" >/dev/null 2>&1 || true
  adb pull "/sdcard/${name}.xml" "$OUT/${name}.xml" >/dev/null 2>&1 || true
}

center_for(){
  local xml="$1" needle="$2" mode="${3:-text}"
  python3 - "$xml" "$needle" "$mode" <<'PY'
import re,sys,xml.etree.ElementTree as ET
p,needle,mode=sys.argv[1:]
try: root=ET.parse(p).getroot()
except Exception: raise SystemExit(2)
n=needle.casefold()
candidates=[]
for e in root.iter('node'):
    text=(e.attrib.get('text','')+' '+e.attrib.get('content-desc','')).strip()
    cls=e.attrib.get('class','')
    ok=(n in text.casefold()) if mode=='text' else (cls==needle)
    if not ok: continue
    m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',e.attrib.get('bounds',''))
    if not m: continue
    x1,y1,x2,y2=map(int,m.groups())
    area=max(0,x2-x1)*max(0,y2-y1)
    clickable=e.attrib.get('clickable')=='true'
    candidates.append((not clickable,-area,(x1+x2)//2,(y1+y2)//2,text,cls))
if not candidates: raise SystemExit(3)
candidates.sort()
_,_,x,y,_,_=candidates[0]
print(f'{x} {y}')
PY
}

tap_text(){
  local xml="$1" needle="$2" xy
  xy="$(center_for "$xml" "$needle" text 2>/dev/null || true)"
  [[ -n "$xy" ]] || return 1
  adb shell input tap $xy
}

tap_class_index(){
  local xml="$1" cls="$2" index="${3:-0}" xy
  xy="$(python3 - "$xml" "$cls" "$index" <<'PY'
import re,sys,xml.etree.ElementTree as ET
p,cls,index=sys.argv[1],sys.argv[2],int(sys.argv[3])
try: root=ET.parse(p).getroot()
except Exception: raise SystemExit(2)
a=[]
for e in root.iter('node'):
  if e.attrib.get('class')!=cls: continue
  m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',e.attrib.get('bounds',''))
  if not m: continue
  x1,y1,x2,y2=map(int,m.groups()); a.append(((x1+x2)//2,(y1+y2)//2))
if index>=len(a): raise SystemExit(3)
print(*a[index])
PY
  2>/dev/null || true)"
  [[ -n "$xy" ]] || return 1
  adb shell input tap $xy
}

launch_app(){
  adb shell am force-stop "$PKG"
  adb shell am start -W -n "$PKG/$ACT" | tee "$OUT/am-start.txt"
  sleep 7
  adb shell pidof "$PKG" >/dev/null || fail 'app process did not start'
  adb shell dumpsys activity activities | grep -E "mResumedActivity|topResumedActivity" | grep -q "$PKG" || fail 'MainActivity is not resumed'
}

authenticate_device(){
  sleep 2
  adb emu finger touch 1 >/dev/null 2>&1 || true
  sleep 2
  uia_dump auth_prompt
  for t in 'Использовать PIN-код' 'Использовать PIN' 'Use PIN' 'PIN'; do
    if tap_text "$OUT/auth_prompt.xml" "$t"; then sleep 1; break; fi
  done
  adb shell input text 1234 >/dev/null 2>&1 || true
  adb shell input keyevent 66 >/dev/null 2>&1 || true
  sleep 5
  adb emu finger touch 1 >/dev/null 2>&1 || true
  sleep 2
}

log "Launching first screen"
adb shell pm clear "$PKG" >/dev/null || true
launch_app
adb exec-out screencap -p > "$OUT/01-first-screen.png"
uia_dump first_screen
if ! grep -Eqi 'SINERGY|КАПИТАЛ|ОБЗОР|Счета' "$OUT/first_screen.xml"; then
  log 'Accessibility dump did not expose WebView text; process/activity launch checks still passed'
fi
if adb logcat -d -t 400 | grep -E 'FATAL EXCEPTION|Process: ai\.sinergy\.finance\.wallet' > "$OUT/fatal.txt"; then
  fail 'fatal Android exception detected after launch'
fi
log "PASS installation and first-screen launch"

log "Opening SINERGY Wallet"
if ! tap_text "$OUT/first_screen.xml" 'SINERGY Wallet'; then
  fail 'SINERGY Wallet navigation element not found in accessibility tree'
fi
sleep 3
uia_dump wallet_page
adb exec-out screencap -p > "$OUT/02-wallet-page.png"
grep -Eqi 'Создать кошелёк|SINERGY WALLET|Кошелёк не создан' "$OUT/wallet_page.xml" || fail 'wallet page did not open'

log "Testing HD wallet creation and BIP39 backup dialog"
tap_text "$OUT/wallet_page.xml" 'Создать кошелёк' || fail 'create-wallet button not found'
authenticate_device
uia_dump wallet_created_secret
if ! grep -Eqi 'СОХРАНИТЕ SEED-ФРАЗУ|SAVE.*SEED|seed-фраз' "$OUT/wallet_created_secret.xml"; then
  cp "$OUT/wallet_created_secret.xml" "$OUT/wallet-create-failure.xml"
  rm -f "$OUT/wallet_created_secret.xml"
  fail 'BIP39 backup dialog did not appear after authentication'
fi
python3 - "$OUT/wallet_created_secret.xml" <<'PY'
import re,sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
words=[]
for e in root.iter('node'):
  t=e.attrib.get('text','').strip()
  if re.fullmatch(r'[a-z]{3,12}',t): words.append(t)
if len(words)<12:
  raise SystemExit(f'only {len(words)} candidate BIP39 words exposed')
print('BIP39 word count check passed without printing words')
PY
rm -f "$OUT/wallet_created_secret.xml"
log "PASS HD wallet creation and 12-word BIP39 generation"

log "Testing BIP39 import on a clean app profile"
adb shell pm clear "$PKG" >/dev/null
launch_app
uia_dump import_first
 tap_text "$OUT/import_first.xml" 'SINERGY Wallet' || fail 'wallet nav missing after reset'
sleep 2
uia_dump import_wallet_page
 tap_text "$OUT/import_wallet_page.xml" 'Импортировать' || fail 'import button not found'
sleep 2
uia_dump import_dialog
if ! tap_text "$OUT/import_dialog.xml" '12 или 24 слова'; then
  tap_class_index "$OUT/import_dialog.xml" 'android.widget.EditText' 0 || fail 'mnemonic input not found'
fi
MN='abandon%sabandon%sabandon%sabandon%sabandon%sabandon%sabandon%sabandon%sabandon%sabandon%sabandon%sabout'
adb shell input text "$MN"
sleep 1
uia_dump import_filled
 tap_text "$OUT/import_filled.xml" 'Импортировать с биометрией' || fail 'mnemonic import submit button not found'
authenticate_device
uia_dump import_done
adb exec-out screencap -p > "$OUT/03-imported-wallet.png"
if ! grep -Eqi 'BIP39_IMPORTED|0x9858|9858effd' "$OUT/import_done.xml"; then
  fail 'imported BIP39 wallet address/source not rendered'
fi
log "PASS BIP39 import and deterministic EVM address rendering"

adb shell run-as "$PKG" ls shared_prefs > "$OUT/shared-prefs-list.txt" 2>&1 || true
adb shell pm clear "$PKG" >/dev/null || true
adb logcat -d -t 800 > "$OUT/logcat.txt"
if grep -E 'FATAL EXCEPTION|Process: ai\.sinergy\.finance\.wallet' "$OUT/logcat.txt" > "$OUT/fatal-final.txt"; then
  fail 'fatal Android exception detected during wallet smoke tests'
fi

log "ALL EMULATOR SMOKE TESTS PASSED"
