#!/usr/bin/env bash
set -euo pipefail

FINANCE_APK="${1:?finance apk path required}"
WALLET_APK="${2:?wallet apk path required}"
OUT_DIR="${3:-android/emulator-smoke}"
mkdir -p "$OUT_DIR"

adb wait-for-device

# Wait until Android package services are fully ready. ADB may be online before
# PackageManager can reliably parse/install applications on a fresh emulator.
for _ in $(seq 1 120); do
  if [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ] \
     && adb shell service check package 2>/dev/null | grep -q 'found'; then
    break
  fi
  sleep 2
done
[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = "1" ]
adb shell input keyevent 82 || true

install_one() {
  local apk="$1" package="$2" label="$3"
  local remote="/data/local/tmp/${label}-sinergy-release.apk"

  test -s "$apk"
  unzip -t "$apk" > "$OUT_DIR/${label}-zip-test.txt"
  sha256sum "$apk" | tee "$OUT_DIR/${label}-sha256.txt"

  # Do not use `adb install`: platform-tools 37 may select incremental install,
  # which can fail with INSTALL_PARSE_FAILED_NOT_APK on GitHub emulators even
  # for a valid aligned/signed APK. Push the exact bytes, verify them on-device,
  # then ask PackageManager to install the local file directly.
  adb shell rm -f "$remote"
  adb push "$apk" "$remote" | tee "$OUT_DIR/${label}-push.txt"
  local host_hash device_hash
  host_hash="$(sha256sum "$apk" | awk '{print $1}')"
  device_hash="$(adb shell sha256sum "$remote" | tr -d '\r' | awk '{print $1}')"
  printf 'host=%s\ndevice=%s\n' "$host_hash" "$device_hash" | tee "$OUT_DIR/${label}-transport-hash.txt"
  test "$host_hash" = "$device_hash"

  adb shell pm install -r -t "$remote" | tee "$OUT_DIR/${label}-install.txt"
  grep -qx 'Success' "$OUT_DIR/${label}-install.txt"
  adb shell rm -f "$remote"
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
  grep -Eq 'Status: ok|Complete' "$OUT_DIR/${label}-launch.txt"
  sleep 8
  adb shell pidof "$package" | tr -d '\r' | tee "$OUT_DIR/${label}-pid.txt"
  test -s "$OUT_DIR/${label}-pid.txt"
  adb exec-out screencap -p > "$OUT_DIR/${label}-running.png"
  test -s "$OUT_DIR/${label}-running.png"
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
