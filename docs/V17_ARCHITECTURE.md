# V17 Architecture — Preserve + Unify

## 1. Non-destructive migration

V17 is built as a superstructure over the existing SINERGYCHAIN Growth OS.

The existing site is preserved verbatim as `legacy-growth-os.html`. The new `index.html` embeds that page and also exposes its major applications as first-class modules in the unified atlas.

No Growth OS capability is removed from the migration model:

- OLGA AGI
- Business Autopilot
- AI SMM
- AI CRM
- AI Sales
- AI CFO
- API Vault / model routing

## 2. Canonical portal layers

### A. Political economy

- collective-decentralized / collective-market doctrine;
- personal ownership and right to exit;
- polycentric governance and subsidiarity;
- collective capital without automatic collectivization of private assets;
- Economic Constitution.

### B. Financial OS

Four coordinated planes:

1. External Value Plane.
2. Settlement & Solvency Plane.
3. Internal Monetary Plane.
4. Institutional Plane.

Cross-cutting controls:

- Liability Registry;
- Source-of-Funds Gate;
- Canonical Profit Guard;
- Bridge Solvency Buffer;
- Economic Stress Engine;
- Evidence Ledger.

### C. Growth OS

The existing business-automation products become the productive/service layer of the broader economy. Their real customer revenue can enter the External Value Plane and then be consolidated into Treasury/NAV accounting.

### D. Blockchain / infrastructure

- SYNERGYCHAIN;
- SYNERGY AI Blockchain;
- payment rails;
- post-quantum roadmap;
- TURBO OS;
- AI compression and model infrastructure.

### E. Markets and AI capital

- MIDAS;
- MetaBroker;
- AI Trade Terminal;
- graph trading systems;
- macro-liquidity mining;
- quantum / vision / 3D-bar / cross-arbitrage research.

### F. Social finance

- mutual aid reserve;
- escrow;
- P2P credit replacement;
- debt clearing / netting;
- anti-pyramid source-of-funds invariant.

### G. Real economy and deep tech

- agro;
- recycling / circular economy;
- energy;
- metallurgy;
- cascade ORC;
- LENR research;
- graphene/photonics;
- piezo memory;
- BioNeuro;
- experimental memory architectures.

## 3. Money architecture

The internal elastic unit and canonical settlement unit are intentionally separated.

### Internal monetary circuit

`xETH <-> SYUSD`

`xETH` represents externally locked ETH.

Invariant:

`Supply(xETH) <= verified ETH locked`

`SYUSD` is an elastic internal policy unit. QE/QT may change its supply/liquidity state, but internal mint is not canonical revenue.

### Canonical settlement circuit

`SYUSD claim -> SettlementRouter -> USDCx -> burn/proof -> native USDC`

Invariants:

`Supply(USDCx) <= verified canonical USDC backing`

`USDCxOut <= AvailableCanonicalBacking`

This separation prevents monetary-policy issuance from silently becoming an unbacked bridge liability.

## 4. Consolidated accounting

The portal distinguishes:

1. Gross TVL / gross system assets.
2. Externally realizable canonical assets.
3. Liability-adjusted canonical NAV.
4. Unrealized/internal accounting uplift.

Canonical wealth:

`ExternalAssets + CanonicalReserves + RealizedExternalPnL - Liabilities - Gas - Ops - MandatoryBuffers`

Internal price/MCAP/TVL uplift is shown separately.

## 5. QE/QT constraints

The requested monetary gradient is not automatically executable.

Policy sequence:

1. Read external market state.
2. Read Treasury and bridge reserves.
3. Estimate support required by the requested gradient.
4. Compute `affordable_gradient`.
5. Apply only the affordable policy.
6. Clear/route trades.
7. Recalculate liabilities and canonical NAV.
8. Stop/reduce if safety floors fail.

QT/buyback is explicitly capital-consuming and is therefore not treated as a free mirror image of mint.

## 6. Social-finance accounting

A debt is reduced only when the creditor's enforceable claim is actually reduced by repayment, discount, settlement, netting, refinancing, or another economically/legal effective mechanism.

A token burn, rebase, flash loan or internal transfer does not by itself extinguish an external debt.

## 7. Governance boundary

Recommended execution chain:

`AI proposes -> DAO/institution authorizes -> contract executes -> ledger proves -> human/legal challenge and exit remain available`

Ownership, cash-flow rights, governance rights and execution permissions are modeled separately.

## 8. Evidence levels

- L0: idea
- L1: formal model/specification
- L2: simulation
- L3: prototype
- L4: fork/testnet
- L5: audited
- L6: production metrics

Negative results are retained rather than removed, because they define real safety constraints.

## 9. UI architecture

The public `index.html` is intentionally self-contained:

- critical CSS is inline;
- critical JavaScript/data is inline;
- no CDN is required;
- no external stylesheet is required to obtain the intended visual design;
- `legacy-growth-os.html` is the only separate page required to display the literal preserved legacy portal inside the new one.

This fixes the V16 failure mode where downloading `index.html` separately broke relative stylesheet/script references.

## 10. Migration rule

A historical module is not deleted merely because a new canonical structure exists. Instead it receives:

`domain -> role -> maturity -> source of funds -> liabilities -> evidence level -> governance/ownership boundary -> canonical/legacy relationship`

This keeps the whole ecosystem discoverable without treating every historical experiment as production-ready.
