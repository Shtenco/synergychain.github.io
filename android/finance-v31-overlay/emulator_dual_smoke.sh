#!/usr/bin/env bash
set -euo pipefail

FINANCE_APK="${1:?finance apk path required}"
WALLET_APK="${2:?wallet apk path required}"
OUT_DIR="${3:-android/emulator-smoke}"
mkdir -p "$OUT_DIR"

adb wait-for-device
adb shell input keyevent 82 || true

install_one() {
  local apk="$1" package="$2" label="$3"
  adb install -r "$apk" | tee "$OUT_DIR/${label}-install.txt"
  adb shell pm list packages | tr -d '\r' | grep -qx "package:${package}"
}

launch_one() {
  local package="$1" label="$2"
  local activity
  activity="$(adb shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER "$package" | tr -d '\r' | tail -n 1)"
  test -n "$activity"
  test "$activity" != "No activity found"
  printf '%s\n' "$activity" > "$OUT_DIR/${label}-activity.txt"

  adb shell am force-stop "$package" || true
  adb shell am start -W -n "$activity" | tee "$OUT_DIR/${label}-launch.txt"
  sleep 8
  adb shell pidof "$package" | tr -d '\r' | tee "$OUT_DIR/${label}-pid.txt"
  test -s "$OUT_DIR/${label}-pid.txt"
  adb exec-out screencap -p > "$OUT_DIR/${label}-running.png"
  adb shell dumpsys package "$package" > "$OUT_DIR/${label}-package.txt"
  adb shell dumpsys activity activities > "$OUT_DIR/${label}-activities.txt"
}

# Both APKs must coexist: distinct package IDs are verified before either is launched.
install_one "$FINANCE_APK" ai.sinergy.finance finance
install_one "$WALLET_APK" ai.sinergy.wallet wallet
adb shell pm list packages | tr -d '\r' | grep -qx 'package:ai.sinergy.finance'
adb shell pm list packages | tr -d '\r' | grep -qx 'package:ai.sinergy.wallet'

launch_one ai.sinergy.finance finance
launch_one ai.sinergy.wallet wallet

printf 'PASS Android 14: SINERGY_FINANCE and SINERGY_WALLET install together and launch successfully\n' | tee "$OUT_DIR/result.txt"
