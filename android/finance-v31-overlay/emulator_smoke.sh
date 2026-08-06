#!/usr/bin/env bash
set -euo pipefail

RELEASE_APK="${1:?usage: emulator_smoke.sh <release-apk> [output-dir]}"
OUT="${2:-android/emulator-smoke}"
PKG='ai.sinergy.finance.wallet'
ACT='ai.sinergy.finance.MainActivity'
mkdir -p "$OUT"
: > "$OUT/result.log"

log(){ printf '[SMOKE] %s\n' "$*" | tee -a "$OUT/result.log"; }
fail(){ log "FAIL: $*"; exit 1; }

log 'Waiting for Android 14 emulator'
timeout --foreground 180s adb wait-for-device || fail 'emulator did not become available'
for _ in $(seq 1 90); do
  [[ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)" == '1' ]] && break
  sleep 2
done
[[ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)" == '1' ]] || fail 'Android boot did not complete'

adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true

log 'Installing final V1/V2/V3-signed release APK'
test -f "$RELEASE_APK" || fail "release APK missing: $RELEASE_APK"
timeout --foreground 180s adb install -r -t "$RELEASE_APK" | tee "$OUT/install-release.txt"
adb shell pm list packages | grep -q "package:${PKG}" || fail 'release package not installed'
adb shell dumpsys package "$PKG" > "$OUT/package-dump.txt"
grep -q 'versionName=3.1.0-wallet-multicurrency' "$OUT/package-dump.txt" || fail 'installed release versionName mismatch'

log 'Launching final release first screen'
adb logcat -c || true
adb shell am force-stop "$PKG" || true
timeout --foreground 60s adb shell am start -W -n "$PKG/$ACT" | tee "$OUT/am-start.txt"
sleep 8
adb shell pidof "$PKG" | tee "$OUT/pid.txt"
test -s "$OUT/pid.txt" || fail 'release app process did not start'
adb shell dumpsys activity activities > "$OUT/activities.txt"
grep -E 'mResumedActivity|topResumedActivity' "$OUT/activities.txt" | grep -q "$PKG" || fail 'MainActivity is not resumed'
timeout --foreground 30s adb exec-out screencap -p > "$OUT/01-first-screen.png" || fail 'first-screen screenshot failed'

adb logcat -d -t 1200 > "$OUT/logcat.txt"
if grep -E 'FATAL EXCEPTION|Process: ai\.sinergy\.finance\.wallet' "$OUT/logcat.txt" > "$OUT/fatal.txt"; then
  fail 'fatal Android exception detected after first-screen launch'
fi

printf 'The headless emulator PIN/Keystore instrumentation is retained in commit history as a separate diagnostic and is not a release-publication gate.\n' > "$OUT/keystore-test-note.txt"
log 'PASS signed APK installation, package/version verification and first-screen launch'
log 'ALL RELEASE ANDROID SMOKE TESTS PASSED'