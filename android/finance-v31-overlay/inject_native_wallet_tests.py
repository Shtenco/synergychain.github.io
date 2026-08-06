#!/usr/bin/env python3
"""Inject Android instrumentation tests for the native SINERGY wallet vault.

The tests execute inside an Android 14 emulator and exercise the real WalletVault:
Android Keystore encryption, 12-word BIP39 creation, deterministic mnemonic import,
address derivation, encrypted persistence, unlock and mnemonic non-persistence.

Android Keystore authentication is refreshed from the system credential-confirmation
screen immediately before every test. This mirrors the production BiometricPrompt /
DEVICE_CREDENTIAL flow and avoids relying on a stale host-side ADB unlock token.
"""

from pathlib import Path
import sys

TEST_SOURCE = r'''package ai.sinergy.finance.wallet;

import static org.junit.Assert.*;

import android.app.KeyguardManager;
import android.content.Context;
import android.content.Intent;
import android.os.ParcelFileDescriptor;
import android.os.SystemClock;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import org.json.JSONObject;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.web3j.crypto.Keys;
import org.web3j.crypto.MnemonicUtils;

import java.io.FileInputStream;

@RunWith(AndroidJUnit4.class)
public final class WalletVaultInstrumentedTest {
    private Context context;
    private WalletVault vault;

    @Before
    public void setUp() throws Exception {
        context = ApplicationProvider.getApplicationContext();
        vault = new WalletVault(context);
        vault.deleteWallet();
        confirmDeviceCredential();
    }

    @After
    public void tearDown() throws Exception {
        vault.deleteWallet();
    }

    private void confirmDeviceCredential() throws Exception {
        KeyguardManager keyguard = (KeyguardManager) context.getSystemService(Context.KEYGUARD_SERVICE);
        assertNotNull("KeyguardManager unavailable", keyguard);
        assertTrue("Secure device credential was not configured", keyguard.isDeviceSecure());

        Intent confirmation = keyguard.createConfirmDeviceCredentialIntent(
            "SINERGY Wallet test",
            "Confirm Android Keystore access"
        );
        assertNotNull("Credential confirmation intent unavailable", confirmation);
        confirmation.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        context.startActivity(confirmation);

        // Wait until SystemUI has presented the PIN confirmation screen, then enter
        // the PIN configured by emulator_smoke.sh. executeShellCommand output is
        // drained so every input command is completed before the next one begins.
        SystemClock.sleep(1500L);
        shell("input text 1234");
        shell("input keyevent KEYCODE_ENTER");
        SystemClock.sleep(2000L);
    }

    private static void shell(String command) throws Exception {
        ParcelFileDescriptor descriptor = InstrumentationRegistry.getInstrumentation()
            .getUiAutomation()
            .executeShellCommand(command);
        try (FileInputStream input = new FileInputStream(descriptor.getFileDescriptor())) {
            byte[] buffer = new byte[1024];
            while (input.read(buffer) != -1) {
                // Drain the shell pipe so command completion is deterministic.
            }
        } finally {
            descriptor.close();
        }
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
