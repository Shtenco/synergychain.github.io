'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const tests=[];
const test=(name,fn)=>tests.push([name,fn]);

const html=read('app/src/main/assets/www/index.html');
const v22=read('app/src/main/assets/www/js/v22.js');
const wallet=read('app/src/main/assets/www/js/wallet.js');
const gradle=read('app/build.gradle');
const main=read('app/src/main/java/ai/sinergy/finance/MainActivity.java');
const vault=read('app/src/main/java/ai/sinergy/finance/wallet/WalletVault.java');
const bridge=read('app/src/main/java/ai/sinergy/finance/wallet/NativeWalletBridge.java');
const tx=read('app/src/main/java/ai/sinergy/finance/wallet/EvmTransactionService.java');
const aa=read('app/src/main/java/ai/sinergy/finance/wallet/SmartAccountClient.java');
const passkey=read('app/src/main/java/ai/sinergy/finance/wallet/PasskeyManager.java');
const safe=read('app/src/main/java/ai/sinergy/finance/wallet/SafeTreasuryClient.java');

const checks=[
 ['separate package id',()=>assert.match(gradle,/applicationId 'ai\.sinergy\.finance\.crypto'/)],
 ['crypto testnet version',()=>assert.match(gradle,/versionName '3\.0\.0-crypto-testnet'/)],
 ['v22 cascade deletion',()=>assert.match(v22,/function deleteAccount/)],
 ['v22 undo',()=>assert.match(v22,/pushUndo\('Операция удалена'/)],
 ['v22 seed phrase guard',()=>assert.match(v22,/Seed-фразы и приватные ключи вводить запрещено/)],
 ['wallet route',()=>assert.match(html,/data-page="wallet"/)],
 ['wallet script loaded after v22',()=>assert.ok(html.indexOf('js/wallet.js')>html.indexOf('js/v22.js'))],
 ['native bridge registered',()=>assert.match(main,/SinergyWalletNative/)],
 ['keystore used',()=>assert.match(vault,/AndroidKeyStore/)],
 ['strongbox preferred',()=>assert.match(vault,/setIsStrongBoxBacked/)],
 ['AES GCM wrapping',()=>assert.match(vault,/AES\/GCM\/NoPadding/)],
 ['biometric gate',()=>assert.match(bridge,/BiometricPrompt/)],
 ['private key export disabled',()=>assert.match(bridge,/privateKeyExport", false/)],
 ['native transaction signer',()=>assert.match(tx,/TransactionEncoder\.signMessage/)],
 ['ERC20 transfer',()=>assert.match(tx,/prepareErc20/)],
 ['mainnet blocked natively',()=>assert.match(tx,/MAINNET_BLOCKED/)],
 ['only Sepolia Amoy Base Sepolia IDs',()=>{assert.match(tx,/11155111/);assert.match(tx,/80002/);assert.match(tx,/84532/)}],
 ['ERC4337 bundler',()=>{assert.match(aa,/eth_sendUserOperation/);assert.match(aa,/eth_estimateUserOperationGas/)}],
 ['passkey credential manager',()=>{assert.match(passkey,/CreatePublicKeyCredentialRequest/);assert.match(passkey,/GetPublicKeyCredentialOption/)}],
 ['Safe treasury',()=>{assert.match(safe,/getOwners/);assert.match(safe,/getThreshold/);assert.match(safe,/execTransaction/)}],
 ['no secret field in web wallet',()=>assert.doesNotMatch(wallet,/seedPhrase|privateKey/)],
];
for(const item of checks)test(...item);
console.log('TAP version 13');
let failed=0;
for(let i=0;i<tests.length;i++){
  const [name,fn]=tests[i];
  try{fn();console.log(`ok ${i+1} - ${name}`)}catch(e){failed++;console.log(`not ok ${i+1} - ${name}`);console.error(e.stack||e)}
}
console.log(`1..${tests.length}`);
console.log(`# tests ${tests.length}`);
console.log(`# pass ${tests.length-failed}`);
console.log(`# fail ${failed}`);
process.exit(failed?1:0);
