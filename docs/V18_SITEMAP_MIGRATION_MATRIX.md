# СИНЕРГИЯ V18 — Sitemap + Migration Matrix

Цель: ни один смысловой блок V17 не теряется при переходе к многостраничной архитектуре.

---

# 1. Canonical sitemap

```text
/
├── model/
│   ├── why-synergy/
│   ├── principles/
│   ├── economic-constitution/
│   ├── ownership/
│   ├── value-flow/
│   ├── federation/
│   └── comparisons/
│
├── financial/
│   ├── accounting/
│   ├── money/
│   ├── settlement/
│   ├── bridge/
│   ├── treasury/
│   ├── qe-qt/
│   ├── amm/
│   ├── liquidity/
│   ├── solvency/
│   ├── profit/
│   ├── stress-lab/
│   └── evidence/
│
├── institutions/
│   ├── governance/
│   ├── ai-governance/
│   ├── budget/
│   ├── social-finance/
│   ├── mutual-aid/
│   ├── p2p-credit/
│   ├── debt-clearing/
│   └── anti-pyramid/
│
├── products/
│   ├── growth-os/
│   ├── olga/
│   ├── autopilot/
│   ├── smm/
│   ├── crm/
│   ├── sales/
│   ├── cfo/
│   ├── api-vault/
│   ├── sinergy-finance/
│   ├── metapay/
│   ├── metabroker/
│   ├── midas/
│   ├── midas-lite/
│   ├── ai-trade-terminal/
│   ├── super-app/
│   ├── smm-bot/
│   ├── ai-advert/
│   └── affiliate/
│
├── technology/
│   ├── blockchain/
│   ├── ai/
│   ├── post-quantum/
│   ├── os/
│   ├── network/
│   ├── payments/
│   └── developer/
│
├── research/
│   ├── markets/
│   ├── tokenomics/
│   ├── deep-tech/
│   ├── evidence/
│   └── negative-results/
│
├── knowledge/
│   ├── household-os/
│   ├── investments-russia-2026/
│   ├── banking-practice/
│   ├── top-50-russia/
│   ├── deposits-russia-2026/
│   ├── online-income-2026/
│   ├── anti-crisis-12-months/
│   └── sell-unused-assets/
│
├── explorer/
│   ├── atlas/
│   ├── repos/
│   ├── evidence/
│   ├── glossary/
│   ├── roadmap/
│   ├── changelog/
│   └── status/
│
└── archive/
    ├── growth-os-v7/
    ├── v14/
    ├── v15/
    ├── v16/
    ├── v17/
    ├── legacy-names/
    └── deprecated-experiments/
```

---

# 2. Migration matrix — `index.html`

| Current V17 block | New canonical route | Rule |
|---|---|---|
| Hero | `/` | Rewrite as concise system gateway, preserve thesis |
| Political Economy 01 | `/model/` | Expand into multiple pages |
| Market principle | `/model/principles/` | Preserve |
| Personal ownership | `/model/ownership/` | Expand |
| Collective capital | `/model/principles/` + `/model/value-flow/` | Expand |
| Polycentric governance | `/model/federation/` + `/institutions/governance/` | Split by doctrine/institution |
| Economic Constitution | `/model/economic-constitution/` | Full first-class page |
| Financial OS 02 | `/financial/` | Gateway only |
| External Value Plane | `/model/value-flow/` + `/financial/accounting/` | Cross-link |
| Settlement & Solvency Plane | `/financial/settlement/`, `/financial/solvency/` | Split |
| Internal Monetary Plane | `/financial/money/`, `/financial/qe-qt/`, `/financial/amm/` | Split |
| Institutional Plane | `/institutions/` + `/products/` | Split |
| Evidence & Risk | `/financial/stress-lab/` + `/explorer/evidence/` | Split |
| Money 03 | `/financial/money/` | Expand |
| xETH | entity page under financial money | Preserve |
| SYUSD | entity page under financial money | Preserve |
| USDCx | entity page under settlement | Preserve |
| SettlementRouter | `/financial/settlement/` + entity page | Preserve |
| Gross/Canonical/Net ledger | `/financial/accounting/` | Expand |
| Canonical Wealth formula | `/financial/accounting/` | Preserve |
| Solvency checks | `/financial/solvency/` | Expand |
| Base-fork negative test | `/research/negative-results/` + `/financial/evidence/` | Preserve as evidence object |
| Policy 04 | `/financial/qe-qt/` | Expand interactive lab |
| QE | `/financial/qe-qt/#qe` | Preserve |
| Neutral | `/financial/qe-qt/#neutral` | Preserve |
| QT | `/financial/qe-qt/#qt` | Preserve |
| Affordable gradient | `/financial/qe-qt/` + `/financial/solvency/` | Preserve |
| Source of Value 05 | `/model/value-flow/` | Become full value-flow map |
| MetaPay | `/products/metapay/` | Product page |
| MetaBroker | `/products/metabroker/` | Product page |
| MIDAS | `/products/midas/` | Product page |
| AI Services | `/products/` | Product group |
| Real Economy | `/research/` or future `/economy/production/` | Keep as research until operational |
| External Investment | `/financial/accounting/` | Explain capital != profit |
| Not Revenue | `/financial/accounting/` + glossary | Preserve |
| Social Finance 06 | `/institutions/social-finance/` | Gateway |
| P2P | `/institutions/p2p-credit/` | Expand |
| Escrow | `/institutions/social-finance/` + entity page | Expand |
| Mutual reserve | `/institutions/mutual-aid/` | Expand |
| Debt netting | `/institutions/debt-clearing/` | Expand |
| Anti-pyramid | `/institutions/anti-pyramid/` | Full formal page |
| Governance 07 | `/institutions/governance/` | Expand |
| NEXUS role | `/institutions/ai-governance/` + `/technology/ai/` | Split governance vs technology |
| Growth OS 08 | `/products/growth-os/` | Canonical product gateway |
| embedded legacy iframe | `/archive/growth-os-v7/` | Preserve, no auto-load on home |
| Atlas 09 | `/explorer/atlas/` | Data-driven entity explorer |
| Evidence 10 | `/explorer/evidence/` | Global registry |
| Repository map 11 | `/explorer/repos/` | Enrich entity mappings |
| Source memory | `/archive/` + `/explorer/changelog/` | Preserve provenance |
| Roadmap 12 | `/explorer/roadmap/` | Expand |

---

# 3. Migration matrix — `legacy-growth-os.html`

| Current hash route | Canonical V18 route | Preservation |
|---|---|---|
| `#home` | `/products/growth-os/` | Rebuild as gateway; preserve original archive |
| `#olga` | `/products/olga/` | Reuse demo logic |
| `#autopilot` | `/products/autopilot/` | Reuse workflow/demo |
| `#smm` | `/products/smm/` | Reuse demo |
| `#crm` | `/products/crm/` | Reuse demo |
| `#sales` | `/products/sales/` | Reuse demo |
| `#cfo` | `/products/cfo/` | Reuse calculator/demo |
| `#vault` | `/products/api-vault/` | Reuse public-safe demo |
| original file | `/archive/growth-os-v7/` | Immutable preserved copy |

Shared concepts move to reusable content/components:

- Growth Cycle;
- Safety Gate;
- Collective Intelligence;
- Recursive Memory;
- model routing;
- CFO feedback loop.

---

# 4. Migration matrix — `financial-os-deep.html`

| Current chapter | Canonical V18 destination |
|---|---|
| 01 Two Design Generations | `/financial/architecture/` section inside `/financial/` + history block |
| xETH/SYUSD/USDCx concept | `/financial/money/` |
| BridgeAsset/BaseBridgeVault | `/financial/bridge/` |
| 02 Base Mainnet Plane | `/financial/bridge/` + `/financial/settlement/` |
| BaseArbExecutor | `/financial/liquidity/` or dedicated entity page |
| PrefundedSettlementVault | `/financial/settlement/` |
| BaseInventoryCycleAdapter | `/financial/settlement/` |
| 03 Why Prefunding Exists | `/financial/settlement/prefunding/` section |
| 04 Settlement Ticket Model | `/financial/settlement/` lifecycle |
| 05 Internal Atomic Credit LP | `/financial/liquidity/` |
| AtomicCreditLiquidityManager | dedicated entity page |
| temporary QE neutralization | `/financial/liquidity/` + evidence |
| 06 Timer QE and Backed Credit | `/financial/qe-qt/` |
| accruedFees -> QE credit | `/financial/treasury/` + `/financial/qe-qt/` |
| 07 Flash Batch Profit Guards | `/financial/profit/` |
| 08 Accounting Separation | `/financial/accounting/` + `/financial/liquidity/` |
| 09 Negative Evidence | `/research/negative-results/` |
| 10 Mainnet Gate | `/technology/developer/` + `/financial/evidence/` |

---

# 5. Migration matrix — `knowledge-hub.html`

| V17 block | V18 route |
|---|---|
| Knowledge Library | `/knowledge/` |
| Инвестиции в России 2026 | `/knowledge/investments-russia-2026/` |
| Практика инвестиций и банков | `/knowledge/banking-practice/` |
| TOP-50 Россия | `/knowledge/top-50-russia/` |
| Вклады | `/knowledge/deposits-russia-2026/` |
| Интернет-заработок | `/knowledge/online-income-2026/` |
| Антикризисный план | `/knowledge/anti-crisis-12-months/` |
| Продажа ненужных вещей | `/knowledge/sell-unused-assets/` |
| SINERGY Finance | `/products/sinergy-finance/` + `/knowledge/household-os/` |
| Education bundle | product/commercial packaging under Products, not protocol docs |
| Household Financial OS | `/knowledge/household-os/` |
| Financial Ladder | `/knowledge/household-os/` |
| Content Governance | `/knowledge/` policy + shared editorial governance docs |

---

# 6. Module atlas migration

All current atlas rows become typed entity records.

## Political Economy

- DESOCI -> `/model/`
- Economic Constitution -> `/model/economic-constitution/`

## Governance

- DEGOV -> `/institutions/governance/`
- DAO 10+1 -> `/research/tokenomics/` or governance research entity
- SOTA DAO -> governance research entity
- Blockchain Budget -> `/institutions/budget/`

## Financial OS

Every Financial OS primitive gets an entity page nested under relevant `/financial/` domain.

## Tokens

SYNA / SYNR / SYNC / USDS move to `/research/tokenomics/` until a governance decision marks a canonical production role.

## Social Finance

Mutual Aid / Anti-Pyramid / P2P / Debt Clearing -> `/institutions/` routes.

## Payments / Markets / Growth OS / Applications

Move to `/products/` if user-facing; supporting rails move to `/technology/`.

## AI

User-facing OLGA -> Products.
Core coordination NEXUS / model infra -> Technology.
Experimental AI language/compression research -> Research/Technology depending maturity.

## Blockchain / Infrastructure

Move to `/technology/`.

## Research

Move to `/research/markets/`.

## Real Economy

Until live production evidence exists, keep as `/research/real-economy/` or add future dedicated productive-economy domain when enough active cells exist.

## Deep Tech

Move to `/research/deep-tech/`.

---

# 7. Repository migration

Current 31 repo links must no longer be a flat list.

Each repository record gets:

```text
repo
 -> entities[]
 -> domain
 -> purpose
 -> visibility
 -> lifecycle status
 -> evidence level
 -> current branch/release
 -> related docs
 -> known limitations
```

Repository Explorer then allows reverse traversal:

`MIDAS -> repos`

and

`repo -> MIDAS entity -> evidence -> product page`.

---

# 8. 404 migration

Current:

`404 -> ./#home`

New:

`404 -> human-readable error page`

Elements:

- query/search field;
- Home;
- Model;
- Financial OS;
- Products;
- Explorer;
- Knowledge;
- no forced meta-refresh.

---

# 9. README migration

Current competing entry points:

- `README.md` -> Growth OS V7;
- `README-V17.md` -> V17 portal.

V18:

- `README.md` = only canonical current architecture/development README;
- historical README copied to `/archive/versions/v7/README.md`;
- V17 README copied to `/archive/versions/v17/README.md`.

---

# 10. Design migration

Current:

- large inline styles in each page;
- small CSS mirror.

V18 source:

```text
styles/
  tokens.css
  global.css
  layouts.css
  components.css
  utilities.css
```

Build can inline critical CSS automatically, but source of truth remains shared.

---

# 11. Content-loss gate

Before V18 can replace V17, generate a machine-readable migration report with:

- `current_source`
- `current_anchor_or_route`
- `target_url`
- `entity_id`
- `migration_status`
- `content_checksum` where applicable
- `notes`

Release condition:

`unmapped_v17_content == 0`

and

`broken_internal_links == 0`.

This is the main anti-regression rule for all future redesigns.
