#!/usr/bin/env bash
set -euo pipefail

APK_NAME='SINERGY-FINANCE-CRYPTO-v3.0.0-TESTNET.apk'
rm -rf android/app/src android/app/build android/build-diagnostics android/release
mkdir -p android/build-diagnostics android/release
exec > >(tee android/build-diagnostics/ci-build.log) 2>&1

cat android/finance-bundle/sf.tar.xz.b64.part* | base64 -d > /tmp/v1.tar.xz
tar -xJf /tmp/v1.tar.xz -C android/app
cat android/finance-bundle/v2.patch.xz.b64.part* | base64 -d > /tmp/v2.patch.xz
xz -dc /tmp/v2.patch.xz > /tmp/v2.patch
(cd android/app && patch --batch -p1 < /tmp/v2.patch)
rm -rf android/app/src/main
mv android/app/src/finance android/app/src/main
cp android/app/src/main/res/drawable/ic_launcher_foreground.xml android/app/src/main/res/drawable/ic_launcher_foreground_round.xml

V21_PARTS=(
  android/finance-bundle/v21safe.part00 android/finance-bundle/v21safe.part01
  android/finance-bundle/v21safe.part02 android/finance-bundle/v21safe.part03
  android/finance-bundle/v21safe.part04 android/finance-bundle/v21safe.part05
  android/finance-bundle/v21safe.part06a android/finance-bundle/v21safe.part06b
  android/finance-bundle/v21safe.part06c android/finance-bundle/v21safe.part06d
  android/finance-bundle/v21safe.part07 android/finance-bundle/v21safe.part08
  android/finance-bundle/v21safe.part09 android/finance-bundle/v21safe.part10
)
cat "${V21_PARTS[@]}" > /tmp/v21.patch.xz.b64
echo '6f4eeaa4f192d81f5bdd72e5a284f140a829fafdd16d73b38162c780dcd63277  /tmp/v21.patch.xz.b64' | sha256sum -c -
base64 -d /tmp/v21.patch.xz.b64 > /tmp/v21.patch.xz
echo 'f85157a5f31c06a9c464e3914cfe0052e31e7254209af712b33cab05c823f5bf  /tmp/v21.patch.xz' | sha256sum -c -
xz -dc /tmp/v21.patch.xz > /tmp/v21.patch
(cd android/app && patch --batch -p1 < /tmp/v21.patch)

base64 -d android/finance-crypto-patch/v22-supplement.tar.xz.b64 > /tmp/v22.tar.xz
echo '0e22a9bc73d4dbce71433e7212fa02377e7644fbc15a8f2102e13187d770b5e0  /tmp/v22.tar.xz' | sha256sum -c -
tar -xJf /tmp/v22.tar.xz -C android
cat android/finance-crypto-patch/part*.b64 | base64 -d > /tmp/crypto.tar.xz
echo 'f5e8eca8bf2ba63ef700c6b2dcc4f5a36d6e00c5ac26503c0439145090a573ba  /tmp/crypto.tar.xz' | sha256sum -c -
xz -t /tmp/crypto.tar.xz
tar -xJf /tmp/crypto.tar.xz -C android

echo '=== RESTORED JAVA SOURCES ==='
find android/app/src/main/java -type f -name '*.java' -print | sort | tee android/build-diagnostics/java-sources.txt
echo '=== RESTORED WEB ASSETS ==='
find android/app/src/main/assets/www -maxdepth 3 -type f -print | sort | tee android/build-diagnostics/web-assets.txt

require_java() {
  local name="$1"
  local path
  path="$(find android/app/src/main/java -type f -name "${name}.java" -print -quit)"
  if [[ -z "$path" ]]; then
    echo "MISSING JAVA SOURCE: ${name}.java" >&2
    return 1
  fi
  echo "FOUND ${name}: ${path}"
}

for f in WalletVault EvmRpcClient EvmTransactionService ChainIndexer NativeWalletBridge PasskeyManager SafeTreasuryClient SmartAccountClient; do
  require_java "$f"
done

test -f android/app/src/main/assets/www/js/v22.js
test -f android/app/src/main/assets/www/js/wallet.js
grep -R -q "ai.sinergy.finance.crypto" android/app/build.gradle android/app/src/main/AndroidManifest.xml
grep -R -q "3.0.0-crypto-testnet" android/app/build.gradle android/app/src/main/java
grep -R -q 'SinergyWalletNative' android/app/src/main/java
grep -R -q 'MAINNET_BLOCKED' android/app/src/main/java

for js in app v2 v21 v22 wallet finance-core; do
  node --check "android/app/src/main/assets/www/js/${js}.js"
done
(cd android && node tests/run-tests.js) | tee android/build-diagnostics/unit-tests.tap

gradle -p android clean assembleRelease -x lintVitalRelease --stacktrace --warning-mode all 2>&1 | tee android/build-diagnostics/gradle.log
UNSIGNED='android/app/build/outputs/apk/release/app-release-unsigned.apk'
ALIGNED='android/release/app-release-aligned.apk'
FINAL="android/release/${APK_NAME}"
test -f "$UNSIGNED"
PASS="$(openssl rand -hex 24)"
keytool -genkeypair -noprompt -keystore /tmp/sinergy-crypto-testnet.jks \
  -storepass "$PASS" -keypass "$PASS" -alias sinergy-crypto-testnet \
  -keyalg RSA -keysize 4096 -validity 3650 \
  -dname 'CN=SINERGY Finance Crypto Testnet,O=SINERGY,C=KZ'
"$ANDROID_HOME/build-tools/34.0.0/zipalign" -f -p 4 "$UNSIGNED" "$ALIGNED"
"$ANDROID_HOME/build-tools/34.0.0/apksigner" sign \
  --ks /tmp/sinergy-crypto-testnet.jks --ks-key-alias sinergy-crypto-testnet \
  --ks-pass "pass:$PASS" --key-pass "pass:$PASS" \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out "$FINAL" "$ALIGNED"
"$ANDROID_HOME/build-tools/34.0.0/apksigner" verify --verbose --print-certs "$FINAL" | tee android/build-diagnostics/signature.txt
"$ANDROID_HOME/build-tools/34.0.0/zipalign" -c -v 4 "$FINAL" | tee android/build-diagnostics/zipalign.txt
"$ANDROID_HOME/build-tools/34.0.0/aapt" dump badging "$FINAL" | tee android/build-diagnostics/badging.txt
grep -q "package: name='ai.sinergy.finance.crypto'" android/build-diagnostics/badging.txt
grep -q "versionName='3.0.0-crypto-testnet'" android/build-diagnostics/badging.txt
unzip -t "$FINAL" | tee android/build-diagnostics/zip-integrity.txt
unzip -l "$FINAL" | grep 'assets/www/js/v22.js'
unzip -l "$FINAL" | grep 'assets/www/js/wallet.js'
sha256sum "$FINAL" | tee android/release/SHA256SUMS.txt
cp android/build-diagnostics/signature.txt android/release/SIGNATURE-REPORT.txt
cp android/build-diagnostics/badging.txt android/release/APK-BADGING.txt
