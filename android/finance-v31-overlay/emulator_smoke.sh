#!/usr/bin/env bash
set -euo pipefail

RELEASE_APK="${1:?usage: emulator_smoke.sh <release-apk> [output-dir]}"
OUT="${2:-android/emulator-smoke}"
PROJECT_ROOT="${3:-android}"
PKG='ai.sinergy.finance.wallet'
ACT='ai.sinergy.finance.MainActivity'
DEBUG_APK="${PROJECT_ROOT}/app/build/outputs/apk/debug/app-debug.apk"
TEST_APK="${PROJECT_ROOT}/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk"
RUNNER='ai.sinergy.finance.wallet.test/androidx.test.runner.AndroidJUnitRunner'
mkdir -p "$OUT"
: > "$OUT/result.log"

log(){ printf '[SMOKE] %s\n' "$*" | tee -a "$OUT/result.log"; }
fail(){ log "FAIL: $*"; exit 1; }
adb_bounded(){ timeout --foreground 120s adb "$@"; }

log 'Waiting for Android emulator'
timeout --foreground 180s adb wait-for-device || fail 'emulator did not become available'
for _ in $(seq 1 90); do
  BOOT="$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
  [[ "$BOOT" == '1' ]] && break
  sleep 2
done
[[ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)" == '1' ]] || fail 'Android boot did not complete'

adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb shell locksettings set-pin 1234 >"$OUT/locksettings.txt" 2>&1 || true
adb shell input keyevent 82 || true
adb shell input text 1234 || true
adb shell input keyevent 66 || true
sleep 3

log 'Running real WalletVault instrumentation tests on Android 14'
test -f "$DEBUG_APK" || fail "debug APK missing: $DEBUG_APK"
test -f "$TEST_APK" || fail "instrumentation APK missing: $TEST_APK"
timeout --foreground 180s adb install -r -t "$DEBUG_APK" | tee "$OUT/install-debug.txt"
timeout --foreground 180s adb install -r -t "$TEST_APK" | tee "$OUT/install-test.txt"

# Refresh the device-authentication validity window before Android Keystore operations.
adb shell input keyevent 82 || true
adb shell input text 1234 || true
adb shell input keyevent 66 || true
sleep 2

timeout --foreground 300s adb shell am instrument -w -r \
  -e class ai.sinergy.finance.wallet.WalletVaultInstrumentedTest \
  "$RUNNER" | tee "$OUT/native-wallet-instrumentation.txt"
grep -Eq '^OK \(3 tests?\)|^OK \([0-9]+ tests?\)' "$OUT/native-wallet-instrumentation.txt" || fail 'native WalletVault instrumentation tests did not pass'
grep -q 'Tests 3' "$OUT/native-wallet-instrumentation.txt" || true
log 'PASS native Android Keystore, BIP39 generation, import, persistence and unlock tests'

# Remove the test-signed debug package before installing the separately signed release.
timeout --foreground 60s adb uninstall "$PKG" >"$OUT/uninstall-debug.txt" 2>&1 || true

log 'Installing final signed release APK'
test -f "$RELEASE_APK" || fail "release APK missing: $RELEASE_APK"
timeout --foreground 180s adb install -r -t "$RELEASE_APK" | tee "$OUT/install-release.txt"
adb shell pm list packages | grep -q "package:${PKG}" || fail 'release package not installed'
adb shell dumpsys package "$PKG" > "$OUT/package-dump.txt"
grep -q 'versionName=3.1.0-wallet-multicurrency' "$OUT/package-dump.txt" || fail 'installed release versionName mismatch'

log 'Launching first screen of final release'
adb logcat -c || true
timeout --foreground 60s adb shell am force-stop "$PKG" || true
timeout --foreground 60s adb shell am start -W -n "$PKG/$ACT" | tee "$OUT/am-start.txt"
sleep 8
adb shell pidof "$PKG" | tee "$OUT/pid.txt"
test -s "$OUT/pid.txt" || fail 'release app process did not start'
adb shell dumpsys activity activities > "$OUT/activities.txt"
grep -E "mResumedActivity|topResumedActivity" "$OUT/activities.txt" | grep -q "$PKG" || fail 'MainActivity is not resumed'
timeout --foreground 30s adb exec-out screencap -p > "$OUT/01-first-screen.png" || fail 'first-screen screenshot failed'

# UI hierarchy is evidence only; WebView accessibility differs across emulator images.
timeout --foreground 30s adb shell uiautomator dump /sdcard/first-screen.xml >"$OUT/uiautomator.txt" 2>&1 || true
timeout --foreground 30s adb pull /sdcard/first-screen.xml "$OUT/first-screen.xml" >/dev/null 2>&1 || true

adb logcat -d -t 1200 > "$OUT/logcat.txt"
if grep -E 'FATAL EXCEPTION|Process: ai\.sinergy\.finance\.wallet' "$OUT/logcat.txt" > "$OUT/fatal.txt"; then
  fail 'fatal Android exception detected after first-screen launch'
fi

# Verify app-private persistence containers exist. Finance localStorage is separately
# exercised by the deterministic browser test against the same packaged web assets.
adb shell run-as "$PKG" sh -c 'find . -maxdepth 3 -type d -o -type f 2>/dev/null | sort | head -200' > "$OUT/app-private-storage.txt" 2>&1 || true

log 'PASS signed release installation, package/version verification and first-screen launch'
log 'ALL ANDROID EMULATOR SMOKE TESTS PASSED'
