# СИНЕРГИЯ V18 — TOP ARCHITECTURE

Статус: canonical architecture proposal after full V17 audit.

Главная идея V18:

> Сайт должен быть не одной длинной страницей и не каталогом названий, а **операционной картой всей СИНЕРГИИ**, где человек всегда понимает: что это за идея, какой институт отвечает, какие деньги движутся, какой продукт работает, какое доказательство существует и где лежит исходный код.

V18 сохраняет всё V17, но меняет способ организации.

---

# 1. Архитектурный принцип

V18 строится в трёх измерениях одновременно.

## Dimension A — DOMAIN

Где сущность живёт в общей системе:

1. Model / Political Economy
2. Financial OS
3. Institutions & Social Finance
4. Products & Services
5. Technology & Infrastructure
6. Research & Evidence
7. Knowledge & Household Economy
8. Explorer / Provenance

## Dimension B — ENTITY TYPE

Что это вообще такое:

- doctrine
- constitutional rule
- institution
- policy
- protocol
- asset
- reserve
- liability
- product
- application
- AI agent
- infrastructure component
- research program
- experiment
- evidence artifact
- repository
- guide / publication
- historical version

## Dimension C — MATURITY / EVIDENCE

Насколько это доказано:

- L0 Idea
- L1 Formal Model
- L2 Simulation
- L3 Prototype
- L4 Testnet/Fork
- L5 Audited
- L6 Production

Отдельно хранится operational status:

- active
- planned
- experimental
- legacy
- archived
- paused

Это устраняет главную проблему V17: `SYUSD`, `MIDAS`, `DAO`, `TURBO OS`, `LENR` и «Экономическая конституция» больше не выглядят как одинаковые карточки одного типа.

---

# 2. Главная навигация

Глобальная navigation bar должна быть короткой и стабильной.

## Primary navigation

1. **Модель**
2. **Financial OS**
3. **Институты**
4. **Продукты**
5. **Технологии**
6. **Исследования**
7. **Знания**
8. **Explorer**

Справа:

- Global Search
- Status / Evidence
- RU / EN
- GitHub

На mobile — drawer with same hierarchy.

Главное правило: топ-навигация не меняется от версии к версии. Новые продукты добавляются внутрь доменов, а не в глобальный header.

---

# 3. Главная страница `/`

Главная больше не должна содержать всю энциклопедию.

Она отвечает только на 7 вопросов.

## 1. Что такое СИНЕРГИЯ?

Hero:

**СИНЕРГИЯ — коллективно-децентрализованная экономическая операционная система.**

Короткое объяснение:

- market discovery;
- personal ownership;
- collective capital;
- polycentric governance;
- AI coordination;
- verifiable accounting.

CTA by audience:

- Я хочу понять модель
- Я участник / пользователь
- Я предприниматель
- Я инвестор / финансовый специалист
- Я разработчик
- Я исследователь

## 2. System Map

Большая интерактивная карта:

`Households -> Products -> External Value -> Treasury / Settlement -> Institutions -> Reinvestment`

Вокруг:

- AI/NEXUS;
- blockchain;
- markets;
- real economy;
- evidence.

## 3. Eight Domains

8 крупных gateway cards, а не 80 module cards.

## 4. What is real now?

Production / prototype / research summary.

Нельзя заставлять нового пользователя самому фильтровать десятки experimental names.

## 5. Economic invariants

5 hard rules:

- mint != profit;
- bridge != value creation;
- liabilities before distribution;
- reserve floors are not distributable capital;
- right to exit / ownership separation.

## 6. Evidence pulse

Последние simulations / tests / releases / audits / version changes.

## 7. Explore everything

Переход в Explorer.

---

# 4. DOMAIN 01 — `/model/`

Название: **Политико-экономическая модель**.

Это intellectual constitution проекта, не продуктовая страница.

## Routes

### `/model/`
Overview.

### `/model/why-synergy/`
Проблема, которую решает модель:

- fragmentation of ownership;
- concentration of infrastructure;
- weak household capital formation;
- disconnected business automation;
- lack of transparent collective capital;
- poor separation between political promise and accounting reality.

### `/model/principles/`
Core doctrine:

- market signal;
- personal ownership;
- collective infrastructure;
- voluntary participation;
- subsidiarity;
- federation;
- right to exit.

### `/model/economic-constitution/`
12+ constitutional principles.

Каждый принцип имеет:

- short rule;
- rationale;
- protected right;
- prohibited failure mode;
- implementation mapping.

### `/model/ownership/`
Разделение:

- personal property;
- cooperative property;
- DAO treasury;
- protocol-owned liquidity;
- IP;
- contractual cashflow rights.

### `/model/value-flow/`
Откуда возникает внешняя стоимость и как она проходит по системе.

### `/model/federation/`
Household -> enterprise cell -> DAO -> sector -> federation.

### `/model/comparisons/`
Сравнение не для политической агитации, а для ясности механики:

- classical market capitalism;
- cooperative model;
- central planning;
- platform capitalism;
- DAO economy;
- Synergy model.

Показывать differences по ownership, price discovery, planning scope, exit, data, capital allocation.

---

# 5. DOMAIN 02 — `/financial/`

Название: **SYNERGY Financial OS**.

Это должен быть самый глубокий системный домен.

## `/financial/`
Overview dashboard:

- 4 financial planes;
- canonical balance sheet;
- settlement map;
- policy controls;
- solvency state;
- evidence links.

## `/financial/accounting/`

Canonical accounting.

Subsections:

- Gross TVL;
- canonical assets;
- liabilities;
- reserves;
- realized external P&L;
- unrealized/internal uplift;
- consolidated NAV;
- distribution eligibility.

Hard formula:

`Canonical Wealth = ExternalAssets + CanonicalReserves + RealizedExternalPnL - Liabilities - Gas - Ops - MandatoryBuffers`

## `/financial/money/`

Two-money architecture:

- xETH;
- SYUSD;
- USDCx;
- native USDC;
- aliases / token-generation differences.

## `/financial/settlement/`

- SettlementRouter;
- xReserve / reserve registry;
- bridge settlement;
- canonical payout;
- backing constraints.

## `/financial/bridge/`

Conceptual + engineering layers:

- ETHBridgeVault;
- BaseBridgeVault;
- BridgeAsset;
- InternalBridgeEndpoint;
- quote/ticket model;
- replay/expiry;
- relayers/attestations.

## `/financial/treasury/`

- Canonical Treasury;
- reserve segmentation;
- distribution budget;
- policy budget;
- bridge support;
- retained surplus;
- governance caps.

## `/financial/qe-qt/`

- QE;
- Neutral;
- QT;
- TimedQEController;
- affordable gradient;
- buyback limits;
- backing credit;
- policy lifecycle.

## `/financial/amm/`

- internal xETH/SYUSD AMM;
- external market reference;
- price gradients;
- liquidity effects;
- fees;
- arbitrage boundaries.

## `/financial/liquidity/`

- permanent grid capital;
- flash principal;
- settlement inventory;
- temporary credit LP;
- QE-neutralization;
- capital attribution.

## `/financial/solvency/`

- Bridge Solvency Buffer;
- Liability Registry;
- Source-of-Funds Gate;
- payout eligibility;
- stress thresholds;
- run/redeem scenarios.

## `/financial/profit/`

Canonical Profit Guard.

Every profit route documents:

- external input;
- external output;
- costs;
- liabilities created;
- reserves consumed;
- realized result;
- consolidated result.

## `/financial/stress-lab/`

Unified simulator entry point:

- demand shocks;
- bridge shortfall;
- QT stress;
- fee changes;
- gas/MEV;
- liquidity exhaustion;
- receivable aging;
- governance failures.

## `/financial/evidence/`

All Financial OS simulations and negative tests.

---

# 6. DOMAIN 03 — `/institutions/`

Здесь хранятся rules of collective action.

## `/institutions/`
Overview.

## `/institutions/governance/`

- DEGOV;
- DAO;
- councils;
- delegation;
- quorum;
- recall;
- conflicts;
- emergency powers;
- audit.

## `/institutions/ai-governance/`

`AI proposes -> institution authorizes -> contract executes -> ledger proves -> human challenge/exit`.

NEXUS не является sovereign authority.

## `/institutions/budget/`

- Blockchain Budget;
- milestones;
- escrow;
- budget caps;
- transparent execution.

## `/institutions/social-finance/`
Overview.

## `/institutions/mutual-aid/`

- reserves;
- contribution rules;
- eligibility;
- payout;
- no promised yield from new entrants.

## `/institutions/p2p-credit/`

- funding;
- underwriting;
- creditor claim;
- refinancing;
- servicing;
- default;
- replacement economics.

## `/institutions/debt-clearing/`

- repayment;
- discount;
- netting;
- legal settlement;
- escrow;
- liability extinguishment.

## `/institutions/anti-pyramid/`

Formal source-of-funds tests and prohibited circular funding patterns.

---

# 7. DOMAIN 04 — `/products/`

Это только то, с чем пользователь/клиент непосредственно взаимодействует.

Сюда нельзя складывать protocol primitives или physics R&D.

## Product groups

### Growth OS

`/products/growth-os/`

Routes:

- `/products/olga/`
- `/products/autopilot/`
- `/products/smm/`
- `/products/crm/`
- `/products/sales/`
- `/products/cfo/`
- `/products/api-vault/`

Existing demos из `legacy-growth-os.html` сохраняются.

Migration strategy:

- original legacy page remains immutable in archive;
- each app gets canonical product route;
- shared Growth OS context reused across apps.

### Financial products

- `/products/sinergy-finance/`
- `/products/metapay/`
- `/products/metabroker/`
- `/products/midas/`
- `/products/midas-lite/`
- `/products/ai-trade-terminal/`
- `/products/super-app/`

### Marketing products

- `/products/smm-bot/`
- `/products/ai-advert/`
- `/products/affiliate/`

## Product page contract

Every product page contains:

1. What it does.
2. Who it is for.
3. User workflow.
4. Inputs / outputs.
5. Current status.
6. Pricing/business model if public.
7. Data/privacy model.
8. Dependencies.
9. Related Financial OS value flow.
10. Repository / release / evidence.
11. Known limitations.
12. CTA/demo.

---

# 8. DOMAIN 05 — `/technology/`

Infrastructure only.

## `/technology/blockchain/`

- SYNERGYCHAIN;
- SYNERGY AI Blockchain;
- EVM compatibility;
- bridge architecture;
- node model.

## `/technology/ai/`

- NEXUS;
- AGI OLGA;
- AI Coder;
- AI Language;
- AI Compress / DeepCompress;
- model routing.

## `/technology/post-quantum/`

- account/key migration;
- PQ EVM;
- messenger;
- crypto-agility;
- standards status.

## `/technology/os/`

TURBO OS.

## `/technology/network/`

TurboMesh / federation network.

## `/technology/payments/`

Synergy Pay rails and settlement infrastructure.

## `/technology/developer/`

Developer portal:

- architecture diagrams;
- repositories;
- APIs;
- schemas;
- contracts;
- environments;
- tests;
- release status.

---

# 9. DOMAIN 06 — `/research/`

Research must look deliberately different from product pages.

Research header always shows:

- hypothesis;
- maturity;
- evidence level;
- falsification criteria;
- latest result;
- repository / notebook / artifact.

## Research groups

### `/research/markets/`

- Info Graph Theory;
- AlgoTrading Graph System;
- Quantum Trading MT5;
- Computer Vision Trading;
- Swap Arbitrage;
- Cross Forex Arbitrage;
- Global Liquidity Dataminer;
- 3D Bars;
- Multithreaded ML trading.

### `/research/tokenomics/`

- SYNA;
- SYNR;
- SYNC;
- USDS;
- Triple Non-Inflationary Emission;
- QE/QT experiments.

### `/research/deep-tech/`

- Cascade ORC;
- LENR / Cold Nuclear;
- Graphene / Photonics;
- Piezo Memory;
- BioNeuro;
- HyperVRAM / memory architecture.

### `/research/evidence/`

Cross-project evidence registry.

### `/research/negative-results/`

Failure cases receive first-class pages instead of being hidden in prose.

---

# 10. DOMAIN 07 — `/knowledge/`

Knowledge Hub becomes a real library.

## `/knowledge/`

- search;
- topics;
- jurisdiction;
- publication date;
- audience;
- level;
- format;
- version.

## `/knowledge/household-os/`

Personal Financial OS:

- cashflow;
- reserve;
- debt;
- surplus;
- investments;
- assets;
- net worth.

## Canonical guide routes

- `/knowledge/investments-russia-2026/`
- `/knowledge/banking-practice/`
- `/knowledge/top-50-russia/`
- `/knowledge/deposits-russia-2026/`
- `/knowledge/online-income-2026/`
- `/knowledge/anti-crisis-12-months/`
- `/knowledge/sell-unused-assets/`

Each guide receives:

- table of contents;
- chapter pages;
- update date;
- jurisdiction;
- source references;
- change log;
- relation to SINERGY Finance.

---

# 11. DOMAIN 08 — `/explorer/`

Explorer — системная карта, а не маркетинговая страница.

## `/explorer/atlas/`

Все entities.

Filters:

- domain;
- entity type;
- maturity;
- evidence;
- operational status;
- repository;
- cashflow role;
- canonical / legacy.

## `/explorer/repos/`

31+ repositories.

Каждый repo card:

- mapped entity;
- purpose;
- public/private;
- status;
- default branch;
- last known milestone;
- evidence level;
- related pages.

## `/explorer/evidence/`

Global evidence registry.

## `/explorer/glossary/`

Canonical definitions.

Особенно:

- profit;
- revenue;
- capital;
- reserve;
- backing;
- liability;
- TVL;
- NAV;
- QE;
- QT;
- bridge;
- settlement;
- DAO;
- collective capital.

## `/explorer/roadmap/`

System roadmap.

## `/explorer/changelog/`

Version history.

## `/explorer/status/`

Current operational matrix.

---

# 12. `/archive/`

Архив — обязательный отдельный слой.

## Routes

- `/archive/growth-os-v7/`
- `/archive/v14/`
- `/archive/v15/`
- `/archive/v16/`
- `/archive/v17/`
- `/archive/legacy-names/`
- `/archive/deprecated-experiments/`

Никакой исторический эксперимент не удаляется.

Но legacy content получает заметный banner:

`ARCHIVED / HISTORICAL — not current canonical specification`.

---

# 13. Новый content model

Главная техническая ошибка V17 — module data хранится как пятиэлементный JS array.

V18 нужен typed content object.

Пример:

```json
{
  "id": "financial.settlement-router",
  "name": "SettlementRouter",
  "slug": "/financial/settlement/router/",
  "domain": "financial",
  "entityType": "protocol",
  "summary": "Converts eligible internal claims into canonical settlement output within verified backing.",
  "status": "experimental",
  "evidenceLevel": "L3",
  "canonical": true,
  "legacyAliases": [],
  "sourceOfFunds": ["canonical settlement reserve"],
  "liabilities": ["eligible redeemable claims"],
  "reserves": ["USDC backing"],
  "governance": "Treasury/DAO policy bounds",
  "ownerBoundary": "protocol",
  "dependencies": ["USDCx", "ReserveRegistry", "LiabilityRegistry"],
  "related": ["SYUSD", "BridgeSolvencyBuffer"],
  "repositories": [],
  "evidence": [],
  "documents": [],
  "lastReviewed": "2026-08-21"
}
```

Every entity page is generated from this model.

---

# 14. Page template for every entity

A universal entity page should use a fixed information hierarchy.

## Header

- Name
- one-line purpose
- domain
- entity type
- maturity
- evidence level
- canonical / legacy

## 1. Why it exists

Problem statement.

## 2. Role in SYNERGY

System position.

## 3. Inputs / outputs

What comes in and what leaves.

## 4. Value / money flow

Source of funds and liabilities.

## 5. Dependencies

Protocols, products, infrastructure.

## 6. Governance / ownership

Who owns, who controls, who can change it.

## 7. Evidence

Tests, simulations, audits, production metrics.

## 8. Failure modes

Known risks and negative evidence.

## 9. Implementation

Repositories, contracts, APIs, documents.

## 10. History

Previous names / versions / migration.

## 11. Related entities

Graph navigation.

---

# 15. Audience journeys

The architecture must support different entry points.

## New visitor

Home -> Model -> System Map -> Evidence -> Explorer.

## Household / participant

Home -> Knowledge -> SINERGY Finance -> Social Finance -> participation rights.

## Entrepreneur

Home -> Products -> Growth OS -> MetaPay -> AI CFO -> External Value Flow.

## Investor / financial specialist

Home -> Financial OS -> Accounting -> Treasury -> Solvency -> Evidence.

## Developer

Home -> Technology -> Developer -> protocol page -> repo -> tests.

## Researcher

Home -> Research -> hypothesis -> evidence -> negative results -> repo/artifact.

## Governance participant

Home -> Institutions -> Economic Constitution -> DAO -> budget -> audit trail.

---

# 16. Search architecture

Global search indexes:

- pages;
- entities;
- docs;
- repositories;
- evidence artifacts;
- guide chapters;
- glossary;
- legacy aliases.

Search result must show entity type and status before snippet.

Example:

`SYUSD — Asset / Experimental / L2`

instead of simply `SYUSD`.

---

# 17. Visual architecture

Current black/white/green language remains.

But domains receive restrained semantic accents:

- Model — white/green;
- Financial — emerald;
- Institutions — cyan/green;
- Products — brighter green;
- Technology — blue-green;
- Research — violet/blue accent;
- Knowledge — warm neutral;
- Archive — gray.

These are navigation cues, not separate brand identities.

## Design system

One source of truth:

- `tokens.css`
- `global.css`
- `components.css`
- `layouts.css`
- domain component styles only where necessary.

No giant duplicate inline stylesheet per page.

Critical CSS can still be inlined automatically at build time.

---

# 18. Technical architecture

Recommended stack: **Astro static site generation**.

Why:

- outputs pure static HTML for GitHub Pages;
- content collections fit a large knowledge portal;
- components prevent copy/paste drift;
- excellent SEO;
- supports Markdown/MDX/JSON;
- can keep client JavaScript minimal;
- easy to generate 80+ entity pages from structured data;
- no backend required for public documentation.

## Repository structure

```text
/
├── src/
│   ├── components/
│   │   ├── GlobalHeader.astro
│   │   ├── DomainNav.astro
│   │   ├── EntityHeader.astro
│   │   ├── EvidenceBadge.astro
│   │   ├── StatusBadge.astro
│   │   ├── SystemGraph.astro
│   │   ├── FlowDiagram.astro
│   │   ├── RelatedEntities.astro
│   │   └── SourceLinks.astro
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   ├── DomainLayout.astro
│   │   ├── EntityLayout.astro
│   │   ├── ProductLayout.astro
│   │   ├── ResearchLayout.astro
│   │   └── GuideLayout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── model/
│   │   ├── financial/
│   │   ├── institutions/
│   │   ├── products/
│   │   ├── technology/
│   │   ├── research/
│   │   ├── knowledge/
│   │   ├── explorer/
│   │   └── archive/
│   ├── content/
│   │   ├── entities/
│   │   ├── evidence/
│   │   ├── guides/
│   │   ├── research/
│   │   └── versions/
│   ├── data/
│   │   ├── repositories.json
│   │   ├── aliases.json
│   │   ├── glossary.json
│   │   └── navigation.json
│   └── styles/
│       ├── tokens.css
│       ├── global.css
│       ├── components.css
│       └── layouts.css
├── public/
│   └── archive/
│       └── growth-os-v7/
├── astro.config.mjs
└── package.json
```

---

# 19. Deployment architecture

Current workflow publishes repository root.

V18:

1. checkout;
2. install locked dependencies;
3. validate content schema;
4. check internal links;
5. build static pages;
6. run HTML accessibility/SEO smoke tests;
7. upload only `dist/`;
8. deploy Pages.

PR previews should be generated before merge.

Main branch must not be used as a manual editing surface for generated HTML.

---

# 20. Quality gates

No V18 build is accepted unless all gates pass.

## Content completeness

Every known V17 module has a migration record.

## Link integrity

0 broken internal links.

## Entity integrity

Every canonical entity has:

- domain;
- type;
- status;
- evidence;
- source-of-funds / N/A;
- liabilities / N/A;
- governance boundary;
- source/repo provenance.

## Legacy preservation

Legacy Growth OS checksum remains preserved.

## Design

All domain pages use the same global design system.

## Accessibility

Keyboard navigation, visible focus, semantic headings, contrast, reduced motion.

## Performance

No iframe loaded automatically on homepage.

## Security

No secrets, no private keys, no `.env`, no account tokens in public build.

---

# 21. Migration order

Do not rebuild everything at once.

## Phase 0 — Freeze and map

- freeze V17 archive;
- generate entity inventory;
- generate URL migration map;
- preserve checksums.

## Phase 1 — Skeleton

Build:

- Home;
- eight domains;
- Explorer;
- design system;
- global search;
- entity template.

## Phase 2 — Financial OS

Migrate every V17/V16 Financial OS block first because it has the deepest dependency graph.

## Phase 3 — Products

Split Growth OS into canonical product routes while retaining original archived page.

## Phase 4 — Institutions / Model

Convert manifesto and governance into structured constitutional pages.

## Phase 5 — Knowledge

Turn guide cards into a searchable content library.

## Phase 6 — Technology / Research

Map repositories and evidence to entities.

## Phase 7 — Public proof

Add live/static evidence dashboard and changelog.

---

# 22. Canonical rule for future expansion

No new project gets added to the top menu.

Every new item must answer:

1. Which domain?
2. What entity type?
3. Canonical or legacy?
4. What maturity/status?
5. What evidence level?
6. What source of funds or economic role?
7. What liabilities/reserves?
8. Who controls it?
9. Which repository/source supports it?
10. Which existing entities does it depend on?

Only after this passport exists does the project appear in Explorer and related pages.

---

# 23. Final target

V18 should feel like a combination of:

- economic constitution;
- Bloomberg-style system map;
- protocol documentation;
- product ecosystem;
- research registry;
- knowledge library;
- public evidence explorer.

But the experience stays simple because each audience enters through one clear route.

**The site must become the canonical map of the entire SYNERGY system, not another layer of text on top of the system.**
