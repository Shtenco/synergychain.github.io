'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const androidRoot = path.resolve(__dirname, '..');
const main = path.join(androidRoot, 'app', 'src', 'main');
const read = (...parts) => fs.readFileSync(path.join(main, ...parts), 'utf8');
const exists = (...parts) => fs.existsSync(path.join(main, ...parts));

const walletVault = () => read('java', 'ai', 'sinergy', 'finance', 'wallet', 'WalletVault.java');
const nativeBridge = () => read('java', 'ai', 'sinergy', 'finance', 'wallet', 'NativeWalletBridge.java');
const evmService = () => read('java', 'ai', 'sinergy', 'finance', 'wallet', 'EvmTransactionService.java');
const smartAccount = () => read('java', 'ai', 'sinergy', 'finance', 'wallet', 'SmartAccountClient.java');
const passkey = () => read('java', 'ai', 'sinergy', 'finance', 'wallet', 'PasskeyManager.java');
const safe = () => read('java', 'ai', 'sinergy', 'finance', 'wallet', 'SafeTreasuryClient.java');
const walletJs = () => read('assets', 'www', 'js', 'wallet.js');

// These checks deliberately validate the exact archived Crypto Layer rather than
// stale product-version assertions from the older v2.1 contract suite.
test('required native Crypto Layer files exist', () => {
  for (const file of [
    ['java','ai','sinergy','finance','wallet','WalletVault.java'],
    ['java','ai','sinergy','finance','wallet','NativeWalletBridge.java'],
    ['java','ai','sinergy','finance','wallet','EvmTransactionService.java'],
    ['java','ai','sinergy','finance','wallet','EvmRpcClient.java'],
    ['java','ai','sinergy','finance','wallet','SmartAccountClient.java'],
    ['java','ai','sinergy','finance','wallet','PasskeyManager.java'],
    ['java','ai','sinergy','finance','wallet','SafeTreasuryClient.java'],
    ['java','ai','sinergy','finance','wallet','ChainIndexer.java'],
    ['assets','www','js','wallet.js'],
    ['assets','www','js','v22.js']
  ]) assert.ok(exists(...file), `missing ${file.join('/')}`);
});

test('wallet vault uses Android Keystore AES-GCM with StrongBox fallback', () => {
  const s = walletVault();
  assert.match(s, /AndroidKeyStore/);
  assert.match(s, /AES\/GCM\/NoPadding/);
  assert.match(s, /StrongBoxUnavailableException/);
  assert.match(s, /setIsStrongBoxBacked\(true\)/);
});

test('native bridge refuses private-key export and requires biometric confirmation', () => {
  const s = nativeBridge();
  assert.match(s, /privateKeyExport["']?\s*,\s*false/);
  assert.match(s, /BiometricPrompt/);
  assert.match(s, /prepareNative/);
  assert.match(s, /prepareErc20/);
});

test('EVM service prepares and signs native and ERC-20 transactions', () => {
  const s = evmService();
  assert.match(s, /prepareNative/);
  assert.match(s, /prepareErc20/);
  assert.match(s, /TransactionEncoder\.signMessage/);
  assert.match(s, /Sign\.signMessage/);
});

test('ERC-4337 smart account client exposes bundler methods', () => {
  const s = smartAccount();
  assert.match(s, /eth_estimateUserOperationGas/);
  assert.match(s, /eth_sendUserOperation/);
});

test('passkey manager uses Android Credential Manager public-key credentials', () => {
  const s = passkey();
  assert.match(s, /CredentialManager/);
  assert.match(s, /CreatePublicKeyCredentialRequest/);
  assert.match(s, /GetPublicKeyCredentialOption/);
  assert.match(s, /PublicKeyCredential/);
});

test('Safe Treasury client is present with transaction operations', () => {
  const s = safe();
  assert.match(s, /SafeTreasuryClient/);
  assert.match(s, /transaction/i);
});

test('wallet web layer exposes send flows and non-exportable security status', () => {
  const s = walletJs();
  assert.match(s, /prepareNative/);
  assert.match(s, /prepareErc20/);
  assert.match(s, /НЕЭКСПОРТИРУЕМЫЙ/);
  assert.match(s, /Android Keystore/);
});

test('Android project is the separate crypto application before v3.1 overlay', () => {
  const gradle = fs.readFileSync(path.join(androidRoot, 'app', 'build.gradle'), 'utf8');
  assert.match(gradle, /applicationId\s+'ai\.sinergy\.finance\.crypto'/);
  assert.match(gradle, /versionName\s+'3\.0\.0-crypto-testnet'/);
});
