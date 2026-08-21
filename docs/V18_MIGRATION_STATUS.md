# SINERGY V18 — Migration Status

Branch: `portal-v18-top`
Base: `portal-v17-rebuild`

## Principle

V18 is being built **beside** V17. Root V17 pages remain unchanged until V18 passes mapping, link, runtime and visual validation.

Promotion invariant:

```text
unmapped_v17_content == 0
broken_internal_links == 0
critical_runtime_errors == 0
```

## Wave 01 — completed structure

### Shared platform

- `v18/assets/sinergy-v18.css` — one shared visual system.
- `v18/assets/sinergy-v18.js` — one shared motion/explorer runtime.
- `v18/data/entities.js` — canonical entity registry.
- `v18/index.html` — new domain map / portal home.

### Domain pages

- `v18/model/index.html`
- `v18/institutions/index.html`
- `v18/products/index.html`
- `v18/technology/index.html`
- `v18/research/index.html`
- `v18/knowledge/index.html`
- `v18/explorer/index.html`
- `v18/archive/index.html`

### Financial OS — decomposed

- `v18/financial/index.html`
- `v18/financial/accounting.html`
- `v18/financial/money.html`
- `v18/financial/settlement.html`
- `v18/financial/bridge.html`
- `v18/financial/treasury.html`
- `v18/financial/qe-qt.html`
- `v18/financial/liquidity.html`
- `v18/financial/solvency.html`
- `v18/financial/profit.html`

## Visual system implemented

The V18 runtime intentionally avoids external visual libraries.

Effects include:

- moving optical flow-field canvas;
- repeating conic / radial moire fields;
- pseudo-3D perspective grid;
- rotating orbital system map;
- optical tunnel sections;
- pointer aura;
- card-local radial lighting;
- optional perspective tilt;
- kinetic text parallax;
- intersection-based reveal;
- scanline effects;
- responsive mobile fallbacks.

Accessibility invariant:

`prefers-reduced-motion: reduce` disables decorative animation and parallax.

## Content migrated / normalized in Wave 01

### Political economy

- market discovery vs collective infrastructure;
- personal ownership;
- right to exit;
- collective capital;
- polycentric governance;
- subsidiarity;
- Economic Constitution;
- ownership / governance / cashflow / execution separation;
- external inflow vs rotation vs accounting uplift vs realized value.

### Financial OS

- four financial planes;
- consolidated accounting perimeter;
- gross TVL vs canonical assets vs liability-adjusted NAV;
- Liability Registry;
- xETH / SYUSD / USDCx role separation;
- SettlementRouter;
- BaseBridgeVault;
- BridgeAsset / InternalBridgeEndpoint;
- BaseArbExecutor;
- PrefundedSettlementVault;
- settlement tickets / receivables;
- Treasury capital buckets;
- QE/QT policy state machine;
- affordable gradient;
- backed QE credit;
- temporary LP QE neutralization;
- flash vs settlement inventory distinction;
- AtomicCreditLiquidityManager;
- Solvency / Stress Engine;
- Canonical Profit Engine;
- Source-of-Funds Gate;
- External Demand / Solver;
- negative evidence preservation.

### Institutions / social finance

- DEGOV;
- DAO 10+1;
- SOTA DAO research;
- NEXUS bounded authority;
- Blockchain Budget;
- Mutual Aid Fund;
- Anti-Pyramid Escrow;
- P2P Credit Replacement;
- Debt Clearing / Netting;
- debt extinguishment requirement.

### Products

- preserved Growth OS linked by original routes;
- OLGA AGI;
- Business Autopilot;
- AI SMM;
- AI CRM;
- AI Sales;
- AI CFO;
- API Vault;
- SMM BOT / ADVERT / Affiliate;
- SINERGY Finance;
- MetaPay / SINERGY Pay;
- Super App;
- MetaBroker;
- MIDAS;
- AI Trade Terminal.

### Technology

- SYNERGYCHAIN;
- SYNERGY AI Blockchain;
- NEXUS / AGI;
- AI Coder;
- AI Language;
- DeepCompress;
- post-quantum roadmap;
- PQ Messenger;
- TURBO OS;
- TurboMesh;
- payment rails.

### Research

- evidence L0-L6;
- Info Graph Theory;
- graph trading;
- quantum trading;
- computer-vision trading;
- swap/cross-FX arbitrage;
- Global Liquidity Dataminer;
- 3D Bars;
- multithreaded ML trading;
- tokenomics branches;
- agro / recycling / energy / metallurgy;
- cascade ORC;
- LENR;
- graphene/photonics;
- piezo memory;
- BioNeuro;
- HyperVRAM / memory architecture.

### Knowledge / household

- Household Financial OS;
- personal net-worth equation;
- financial ladder;
- investments guide branch;
- banking/practice branch;
- TOP-50 reference branch;
- deposits branch;
- online-income branch;
- anti-crisis plan;
- unused-asset sale guide;
- SINERGY Finance connection.

## Remaining Wave 02 work

### 1. Entity passports

Promote high-value registry entities into generated/full pages with fields:

`id → aliases → domain → entity type → status → evidence → purpose → inputs → outputs → source of funds → liabilities → reserves → governance → dependencies → repositories → evidence → risks → history`.

Priority passports:

- SettlementRouter
- BaseBridgeVault
- PrefundedSettlementVault
- TimedQEController
- AtomicCreditLiquidityManager
- Canonical Treasury
- NEXUS
- DEGOV
- MetaPay
- MetaBroker
- MIDAS
- SINERGY Finance
- Growth OS / OLGA

### 2. Typed dependency graph

Add edges:

- `depends_on`
- `creates_claim`
- `funds`
- `governed_by`
- `settles_into`
- `evidence_for`
- `supersedes`
- `contradicts`

### 3. Repository binding

Attach GitHub repositories to entities rather than showing a flat list.

### 4. Evidence binding

Attach simulations, reports, tests and negative evidence to exact claims/entities.

### 5. Knowledge decomposition

Split large educational branches into stable chapter URLs instead of cards only.

### 6. Token taxonomy cleanup

Move token branches under `Research / Tokenomics` as a subdomain while preserving token entity type and legacy aliases.

### 7. Automated validation

Add CI checks for:

- missing internal href/src targets;
- duplicate entity IDs;
- entity references to unknown dependencies;
- domain taxonomy violations;
- missing evidence/status fields;
- HTML parse/runtime smoke tests;
- `prefers-reduced-motion` presence;
- accidental secret patterns.

### 8. Promotion

Only after validation:

- archive the current root entrypoint;
- promote V18 to root;
- update `404.html`;
- update root `README.md`;
- deploy built static artifact rather than repository root;
- keep V17 URL-accessible.
