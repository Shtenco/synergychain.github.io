#!/usr/bin/env python3
"""Prepare the Android Keystore wrapping key before test authentication.

WalletVault deliberately creates an authentication-bound AES key. Android's auth token
must be issued after that key exists. The production app already prompts at the correct
moment; this patch makes the injected instrumentation test follow the same order.
"""

from pathlib import Path
import sys


def replace_required(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Expected test fragment missing: {label}")
    return text.replace(old, new, 1)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_wallet_test_auth.py <android-project-dir>")

    android = Path(sys.argv[1]).resolve()
    test_path = android / "app" / "src" / "androidTest" / "java" / "ai" / "sinergy" / "finance" / "wallet" / "WalletVaultInstrumentedTest.java"
    text = test_path.read_text(encoding="utf-8")

    text = replace_required(
        text,
        "import java.io.FileInputStream;\n",
        "import java.io.FileInputStream;\nimport java.lang.reflect.Method;\n",
        "reflection import",
    )
    text = replace_required(
        text,
        "        vault.deleteWallet();\n        confirmDeviceCredential();\n",
        "        vault.deleteWallet();\n        prepareWrappingKey();\n        confirmDeviceCredential();\n",
        "setup key/auth order",
    )
    text = replace_required(
        text,
        "    private void confirmDeviceCredential() throws Exception {\n",
        "    private void prepareWrappingKey() throws Exception {\n"
        "        Method method = WalletVault.class.getDeclaredMethod(\"ensureWrappingKey\");\n"
        "        method.setAccessible(true);\n"
        "        method.invoke(vault);\n"
        "    }\n\n"
        "    private void confirmDeviceCredential() throws Exception {\n",
        "wrapping-key preparation helper",
    )

    test_path.write_text(text, encoding="utf-8")
    print(f"Patched WalletVault test authentication order: {test_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
