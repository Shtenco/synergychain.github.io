#!/usr/bin/env python3
"""Compile-compatibility fixes for the archived Crypto Layer dependencies.

The original layer targeted earlier AndroidX Credentials/Web3j signatures.
This script preserves behavior while adapting imports and type signatures to
AndroidX Credentials 1.5.0 and Web3j 4.14.0 used by the v3.1 build.
"""

from pathlib import Path
import sys


def replace_required(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new)
    if new in text:
        return text
    raise RuntimeError(f"Expected source fragment missing: {label}")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: fix_android_compat.py <android-main-dir>")

    main_dir = Path(sys.argv[1]).resolve()
    wallet_dir = main_dir / "java" / "ai" / "sinergy" / "finance" / "wallet"

    passkey_path = wallet_dir / "PasskeyManager.java"
    passkey = passkey_path.read_text(encoding="utf-8")
    passkey = replace_required(
        passkey,
        "import androidx.credentials.CreateCredentialException;",
        "import androidx.credentials.exceptions.CreateCredentialException;",
        "CreateCredentialException import",
    )
    passkey = replace_required(
        passkey,
        "import androidx.credentials.GetCredentialException;",
        "import androidx.credentials.exceptions.GetCredentialException;",
        "GetCredentialException import",
    )
    passkey_path.write_text(passkey, encoding="utf-8")

    evm_path = wallet_dir / "EvmTransactionService.java"
    evm = evm_path.read_text(encoding="utf-8")
    evm = replace_required(
        evm,
        "import org.web3j.crypto.WalletUtils;",
        "import org.web3j.crypto.Credentials;",
        "Web3j Credentials import",
    )
    evm = replace_required(
        evm,
        "TransactionEncoder.signMessage(raw, network.chainId.longValueExact(), key.keyPair())",
        "TransactionEncoder.signMessage(raw, network.chainId.longValueExact(), Credentials.create(key.keyPair()))",
        "Web3j transaction signing",
    )
    evm = replace_required(
        evm,
        'if (!WalletUtils.isValidAddress(address == null ? "" : address.trim())) throw new IllegalArgumentException(field + " некорректен");',
        'String candidate = address == null ? "" : address.trim();\n        if (!candidate.matches("(?i)^(0x)?[0-9a-f]{40}$")) throw new IllegalArgumentException(field + " некорректен");',
        "EVM address validation",
    )
    evm_path.write_text(evm, encoding="utf-8")

    safe_path = wallet_dir / "SafeTreasuryClient.java"
    safe = safe_path.read_text(encoding="utf-8")
    safe = replace_required(
        safe,
        "Collections.singletonList(new TypeReference<DynamicArray<Address>>() {})",
        "outputReference(new TypeReference<DynamicArray<Address>>() {})",
        "Safe owners decoder output",
    )
    safe = replace_required(
        safe,
        "Collections.singletonList(new TypeReference<Uint256>() {})",
        "outputReference(new TypeReference<Uint256>() {})",
        "Safe uint decoder output",
    )
    marker = "    private static String encodeNoArgs(String name, TypeReference<?> output) {"
    helper = """    @SuppressWarnings({\"rawtypes\", \"unchecked\"})
    private static List<TypeReference<Type>> outputReference(TypeReference<?> reference) {
        return (List) Collections.singletonList(reference);
    }

"""
    if helper not in safe:
        if marker not in safe:
            raise RuntimeError("Safe output helper insertion point missing")
        safe = safe.replace(marker, helper + marker, 1)
    safe_path.write_text(safe, encoding="utf-8")

    bridge_path = wallet_dir / "NativeWalletBridge.java"
    bridge = bridge_path.read_text(encoding="utf-8")
    method_start = bridge.find("    public void assetBalance(")
    if method_start < 0:
        raise RuntimeError("assetBalance method missing")
    method_end = bridge.find("    @JavascriptInterface", method_start + 8)
    if method_end < 0:
        raise RuntimeError("assetBalance method boundary missing")
    block = bridge[method_start:method_end]
    if "final int requestedDecimals = decimals;" not in block:
        block = replace_required(
            block,
            "    public void assetBalance(String requestId, String networkJson, String tokenAddress, int decimals, String symbol) {\n        run(requestId, () -> {",
            "    public void assetBalance(String requestId, String networkJson, String tokenAddress, int decimals, String symbol) {\n        final int requestedDecimals = decimals;\n        run(requestId, () -> {\n            int effectiveDecimals = requestedDecimals;",
            "assetBalance lambda decimal capture",
        )
    block = block.replace("decimals = 18;", "effectiveDecimals = 18;")
    block = block.replace("if (decimals < 0 || decimals > 36)", "if (effectiveDecimals < 0 || effectiveDecimals > 36)")
    block = block.replace('.put("decimals", decimals)', '.put("decimals", effectiveDecimals)')
    block = block.replace("formatUnits(raw, decimals)", "formatUnits(raw, effectiveDecimals)")
    bridge = bridge[:method_start] + block + bridge[method_end:]
    bridge_path.write_text(bridge, encoding="utf-8")

    print("AndroidX Credentials, Web3j and Java lambda compatibility fixes applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
