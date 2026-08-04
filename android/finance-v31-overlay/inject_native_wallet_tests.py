#!/usr/bin/env python3
"""Inject Android instrumentation tests for the native SINERGY wallet vault.

The tests execute inside an Android 14 emulator and exercise the real WalletVault:
Android Keystore encryption, 12-word BIP39 creation, deterministic mnemonic import,
address derivation, encrypted persistence, unlock and mnemonic non-persistence.
"""

from pathlib import Path
import sys

TEST_SOURCE = r'''package ai.sinergy.finance.wallet;

import static org.junit.Assert.*;

import android.content.Context;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.json.JSONObject;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.web3j.crypto.Keys;
import org.web3j.crypto.MnemonicUtils;

@RunWith(AndroidJUnit4.class)
public final class WalletVaultInstrumentedTest {
    private WalletVault vault;

    @Before
    public void setUp() throws Exception {
        Context context = ApplicationProvider.getApplicationContext();
        vault = new WalletVault(context);
        vault.deleteWallet();
    }

    @After
    public void tearDown() throws Exception {
        vault.deleteWallet();
    }

    @Test
    public void createHdWalletGeneratesAndPersistsEncryptedBip39Account() throws Exception {
        JSONObject created = vault.createHdWallet();
        String mnemonic = created.getString("mnemonic");
        String[] words = mnemonic.trim().split("\\s+");

        assertEquals(12, words.length);
        assertTrue(MnemonicUtils.validateMnemonic(mnemonic));
        assertEquals("BIP39_GENERATED", created.getString("source"));
        assertEquals("m/44'/60'/0'/0/0", created.getString("hdPath"));
        assertTrue(created.getBoolean("backupRequired"));
        assertTrue(created.getBoolean("returnedOnce"));
        assertTrue(created.getString("address").matches("0x[0-9a-f]{40}"));

        JSONObject stored = vault.status();
        assertTrue(stored.getBoolean("exists"));
        assertEquals(created.getString("address"), stored.getString("address"));
        assertEquals("BIP39_GENERATED", stored.getString("source"));
        assertFalse(stored.has("mnemonic"));
        assertFalse(stored.getBoolean("mnemonicStored"));
        assertFalse(stored.getBoolean("keyExportable"));

        try (WalletVault.UnlockedKey key = vault.unlock()) {
            String unlockedAddress = "0x" + Keys.getAddress(key.keyPair().getPublicKey());
            assertEquals(created.getString("address"), unlockedAddress);
        }
    }

    @Test
    public void importKnownBip39MnemonicDerivesExpectedEvmAccount() throws Exception {
        String mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about";
        JSONObject imported = vault.importMnemonic(mnemonic, "");

        assertTrue(imported.getBoolean("imported"));
        assertEquals(12, imported.getInt("mnemonicWords"));
        assertEquals("BIP39_IMPORTED", imported.getString("source"));
        assertEquals("m/44'/60'/0'/0/0", imported.getString("hdPath"));
        assertEquals("0x9858effd232b4033e47d90003d41ec34ecaeda94", imported.getString("address"));

        JSONObject stored = vault.status();
        assertEquals(imported.getString("address"), stored.getString("address"));
        assertFalse(stored.has("mnemonic"));
        assertFalse(stored.getBoolean("mnemonicStored"));

        try (WalletVault.UnlockedKey key = vault.unlock()) {
            String unlockedAddress = "0x" + Keys.getAddress(key.keyPair().getPublicKey());
            assertEquals(imported.getString("address"), unlockedAddress);
        }
    }

    @Test
    public void invalidMnemonicIsRejectedWithoutCreatingWallet() throws Exception {
        try {
            vault.importMnemonic("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon", "");
            fail("Invalid BIP39 checksum must be rejected");
        } catch (IllegalArgumentException expected) {
            assertTrue(expected.getMessage().contains("BIP39"));
        }
        assertFalse(vault.exists());
    }
}
'''


def add_once(text: str, marker: str, insertion: str, label: str) -> str:
    if insertion.strip() in text:
        return text
    if marker not in text:
        raise RuntimeError(f"Build marker missing: {label}")
    return text.replace(marker, insertion + marker, 1)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: inject_native_wallet_tests.py <android-project-dir>")

    android = Path(sys.argv[1]).resolve()
    gradle_path = android / "app" / "build.gradle"
    gradle = gradle_path.read_text(encoding="utf-8")

    runner_line = "        testInstrumentationRunner 'androidx.test.runner.AndroidJUnitRunner'\n"
    if "testInstrumentationRunner 'androidx.test.runner.AndroidJUnitRunner'" not in gradle:
        marker = "        versionName '3.1.0-wallet-multicurrency'\n"
        if marker not in gradle:
            raise RuntimeError("versionName insertion point missing")
        gradle = gradle.replace(marker, marker + runner_line, 1)

    deps = """    androidTestImplementation 'androidx.test.ext:junit:1.2.1'\n    androidTestImplementation 'androidx.test:runner:1.6.2'\n    androidTestImplementation 'androidx.test:core:1.6.1'\n"""
    if "androidTestImplementation 'androidx.test.ext:junit:1.2.1'" not in gradle:
        marker = "dependencies {\n"
        if marker not in gradle:
            raise RuntimeError("dependencies block missing")
        gradle = gradle.replace(marker, marker + deps, 1)

    gradle_path.write_text(gradle, encoding="utf-8")

    test_path = android / "app" / "src" / "androidTest" / "java" / "ai" / "sinergy" / "finance" / "wallet" / "WalletVaultInstrumentedTest.java"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(TEST_SOURCE, encoding="utf-8")

    print(f"Injected native wallet instrumentation test: {test_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
