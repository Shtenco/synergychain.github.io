# СИНЕРГИЯ — полный аудит V17 перед новой архитектурой

Дата аудита: 2026-08-21

Цель этого документа — разобрать существующий портал как систему, а не как набор экранов. Ничего из V17 не считается ненужным автоматически. Сначала фиксируется, что уже существует, где это живёт, что дублируется, что потеряно в навигации и что должно быть сохранено в следующем поколении.

---

# 1. Текущее дерево V17

Публичные поверхности:

1. `index.html` — главный политико-экономический портал.
2. `legacy-growth-os.html` — сохранённый Growth OS.
3. `financial-os-deep.html` — глубокая инженерная ветка Financial OS.
4. `knowledge-hub.html` — household economy / education.
5. `404.html` — redirect/error page.

Документация:

- `README.md` — старый README Growth OS V7.
- `README-V17.md` — описание V17.
- `docs/V17_ARCHITECTURE.md` — архитектурное объяснение V17.
- `docs/V16_TO_V17_CROSSWALK.md` — контроль переноса V16.

Стили:

- критический CSS встроен в HTML;
- `assets/portal-v17.css` — только сокращённое зеркало токенов/базовых стилей, а не полный stylesheet.

CI/CD:

- `.github/workflows/pages.yml` публикует весь репозиторий на GitHub Pages при push в `main`;
- `.github/workflows/split-roboforex-drive.yml` относится к отдельной задаче подготовки архива RoboForex и концептуально не относится к публичному порталу.

---

# 2. `index.html` — что реально находится на главной

Главная — это одновременно landing page, manifesto, Financial OS overview, monetary architecture, policy simulator, social-finance explainer, governance explainer, Growth OS container, module explorer, evidence ledger, repository explorer и roadmap.

## Hero

Содержит:

- тезис «СИНЕРГИЯ — экономика как ОС»;
- три принципа: preserve, mint != profit, separation of rights;
- визуальную карту ядра;
- KPI по модулям, financial planes, repo branches и evidence scale.

## 01 — Политико-экономическая модель

Содержит:

- market signal;
- personal ownership;
- collective capital;
- polycentric/subsidiary governance;
- 12 пунктов Economic Constitution.

## 02 — Financial OS

Содержит пять карточек:

- External Value Plane;
- Settlement & Solvency Plane;
- Internal Monetary Plane;
- Institutional Plane;
- Evidence & Risk control.

## 03 — Деньги и settlement

Содержит:

- `xETH <-> SYUSD`;
- `SettlementRouter`;
- `USDCx`;
- backing invariants;
- Gross / Canonical / Net views;
- formula of Canonical Wealth;
- Source / Liabilities / Solvency / Net-positive checks;
- негативный Base-fork solvency result.

## 04 — AI Treasury / QE-QT

Содержит интерактивные режимы:

- QE;
- Neutral;
- QT.

Фиксирует:

- affordable gradient;
- Treasury-bounded policy;
- mint != canonical profit;
- bridge != value creation;
- external demand must be explicit.

## 05 — Source of Value

Выделены:

- MetaPay;
- MetaBroker + MIDAS;
- AI Services;
- Real Economy;
- External Investment;
- отдельная категория Not Revenue.

## 06 — Social Finance

Содержит:

- debt state transition;
- P2P;
- escrow;
- mutual reserve;
- netting;
- anti-pyramid positive/negative source list.

## 07 — Governance

Содержит цепочку:

`Members/owners -> DAO/councils -> NEXUS/AGI -> smart contracts -> audit/legal`

и правило:

`AI proposes -> DAO authorizes -> contract executes -> ledger proves -> human challenges/exits`.

## 08 — Existing Growth OS

Кратко описывает:

- OLGA AGI;
- Business Autopilot;
- AI SMM;
- AI CRM;
- AI Sales;
- AI CFO;
- API Vault;
- связку Growth OS -> Financial OS.

Также встраивает весь `legacy-growth-os.html` через iframe.

## 09 — Полный атлас экосистемы

Содержит большой JS-массив порядка 80 сущностей в категориях:

- Политэкономия;
- Управление;
- Financial OS;
- Токены;
- Соцфинансы;
- Платежи;
- Рынки;
- Growth OS;
- Приложения;
- AI;
- Blockchain;
- Infrastructure;
- Research;
- Real economy;
- Deep Tech.

Проблема: это индекс без content body. Большинство сущностей не имеют собственных URL, полной истории, схемы потоков, maturity/evidence паспорта, связанных документов и репозиториев.

## 10 — Evidence Ledger

L0-L6:

- Idea;
- Formal;
- Simulation;
- Prototype;
- Testnet/Fork;
- Audited;
- Production.

Также показаны негативные evidence cards.

## 11 — Source Memory / Repository Map

Содержит:

- 31 repository link;
- V14/V15/V16 provenance summaries;
- recovered Base-fork branch;
- trading research;
- infrastructure / deep-tech branch.

Проблема: repo card не объясняет, к какому продукту, модулю или evidence level относится репозиторий.

## 12 — Roadmap

V17 -> V20:

- preserve/unify;
- executable constitution;
- unified economic simulator;
- public proof dashboard.

### Главный дефект `index.html`

Главная одновременно играет слишком много ролей. Пользователь получает много сильных тезисов, но не получает стабильной mental model сайта. Это приводит к трём проблемам:

1. скролл заменяет архитектуру;
2. atlas заменяет полноценные страницы;
3. важнейшие системы Financial OS и Governance конкурируют на одном уровне с отдельными продуктами и research branches.

---

# 3. `legacy-growth-os.html` — полный разбор

Это не обычная страница, а одностраничное приложение с hash-routing.

Routes:

1. `#home`
2. `#olga`
3. `#autopilot`
4. `#smm`
5. `#crm`
6. `#sales`
7. `#cfo`
8. `#vault`

## Home

- OGAS 2.0 narrative;
- cycle: Goal -> AI agents -> Actions -> CFO control -> Growth;
- OLGA / SMM / CRM+Sales / CFO architecture;
- collective intelligence;
- recursive memory.

## OLGA AGI

- single model;
- sequential chain;
- consensus;
- debate;
- AI department;
- local demo chat;
- memory/router inspector.

## Business Autopilot

- business goal;
- monthly budget;
- target revenue;
- generated SMM/CRM/Sales/CFO plan;
- safety gate for external actions.

## AI SMM

- offer;
- audience;
- channel;
- post draft generation.

## AI CRM

- lead input;
- intent score;
- stage;
- next action.

## AI Sales

- client objection/message;
- product context;
- answer / next step generation.

## AI CFO

- income;
- expense;
- delta;
- margin;
- reserve;
- ad spend;
- advice.

## API Vault

- provider layer;
- free model rotation;
- router / fallback logic;
- public demo without real secrets.

### Сильная сторона

Growth OS уже имеет продуктовую модель «один цикл роста» и интерактивные tools.

### Архитектурная проблема

Он сейчас изолирован как legacy iframe. В новой архитектуре его рабочие product surfaces должны остаться живыми, но быть встроены в общий Product domain через нормальные URLs и cross-links.

---

# 4. `financial-os-deep.html` — полный разбор

10 инженерных глав.

## 01 — Two Design Generations

Разделяет:

- V16 canonical concept: xETH / SYUSD / USDCx;
- engineering branch: BridgeAsset / BaseBridgeVault / Timed QE.

## 02 — Base Mainnet Plane

- BaseBridgeVault;
- BaseArbExecutor;
- PrefundedSettlementVault;
- BaseInventoryCycleAdapter;
- receivable caps.

## 03 — Why Prefunding Exists

Объясняет, что flash liquidity не решает asynchronous cross-chain settlement, и почему требуется реальный working-capital inventory.

## 04 — Settlement Ticket Model

5-step lifecycle:

- quote;
- external cycle;
- prefunded payout;
- internal settlement;
- accounting close.

## 05 — Internal Atomic Credit LP

- creditMint;
- ADDLP;
- QE / settlement;
- removeLP;
- principal burn;
- temporary QE share burn;
- residual -> treasury.

## 06 — Timer QE and Backed Credit

- real Base USDC -> vault -> liability/QE credit -> relay -> availableCredit;
- organic bridge fees -> governance -> future QE credit.

## 07 — Flash Batch Profit Guards

- minProfitGain;
- minNetProfit;
- maxGasPriceWei;
- adapter allowlist;
- quote expiry/replay;
- receivable cap.

## 08 — Accounting Separation

Отделяет:

- grid capital;
- bridge reserve / QE backing;
- flash principal;
- settlement inventory.

## 09 — Negative Evidence

- TVL illusion;
- QT asymmetry;
- temporary LP QE capture.

## 10 — Mainnet Gate

- build/unit;
- fork integration;
- adversarial tests.

### Сильная сторона

Это наиболее инженерно зрелая информационная часть V17: есть components, invariants, failure modes и lifecycle.

### Архитектурная проблема

Она существует одной длинной страницей и почти не связана с module atlas, developer routes, contract/repository references, glossary и evidence records. Её нужно превратить в отдельный Financial OS domain с дочерними страницами.

---

# 5. `knowledge-hub.html` — полный разбор

4 раздела.

## 01 — Knowledge Library

9 карточек:

- Инвестиции в России 2026;
- Практика инвестиций и банков;
- TOP-50 Россия;
- Вклады в России;
- Интернет-заработок;
- Антикризисный план;
- Куда продать ненужные вещи;
- SINERGY Finance;
- education bundle.

Проблема: карточки описывают крупные материалы, но не ведут к реальным content pages / chapters / downloads / versions.

## 02 — Household Financial OS

- income;
- expenses;
- cashflow delta;
- debt/reserve;
- investable surplus;
- assets;
- net worth.

## 03 — Financial Ladder

6 ступеней:

- accounting;
- reserve;
- expensive debt reduction;
- income/skills;
- investment capital;
- voluntary productive/collective participation.

## 04 — Content Governance

- jurisdiction/date;
- education != individual advice;
- versioned knowledge.

### Сильная сторона

Правильно ставит домохозяйство ниже protocol layer и отделяет household/product economics от DAO reserves.

### Архитектурная проблема

Knowledge Hub — это каталог без библиотечной навигации, тем, глав, versions и search facets.

---

# 6. `404.html`

Текущий redirect ведёт на `./#home`.

На новом `index.html` canonical hero имеет `#top`, а `#home` относится к hash-router внутри legacy Growth OS.

Следовательно, 404 использует legacy navigation semantics и должен быть заменён нормальной error page с:

- поиском;
- ссылкой на `/`;
- links to main domains;
- optional redirect only after user action, а не meta-refresh.

---

# 7. Документация и deployment debt

## `README.md`

До сих пор описывает `SINERGYCHAIN Growth OS V7`, то есть противоречит V17 как canonical portal.

## `README-V17.md`

Содержательно полезен, но является вторым README и создаёт два competing entry points.

Решение: canonical `README.md` должен описывать текущую архитектуру, а исторические README уходят в `/archive/versions/`.

## CSS

`assets/portal-v17.css` — не полный stylesheet. Название создаёт впечатление runtime source, хотя реальный style source находится inline в `index.html`.

Решение: в следующей версии один настоящий design system source, из которого строятся все страницы.

## GitHub Pages workflow

Deploy публикует весь repository root. Для content portal это допустимо сейчас, но не оптимально после появления source/build system.

Решение: build static output to `/dist`, deploy only `/dist`.

## RoboForex workflow

Не относится к публичному portal build и смешивает data-processing pipeline с website repository.

Решение: вынести в профильный data/trading repo либо минимум отделить от portal CI namespace.

---

# 8. Главные системные проблемы V17

## P0 — Information architecture

80+ сущностей каталогизированы, но большая часть не имеет собственного content object / route.

## P0 — Page responsibilities

`index.html` выполняет слишком много функций.

## P0 — Taxonomy

Смешиваются уровни:

- doctrine;
- institution;
- protocol;
- asset;
- product;
- application;
- research project;
- infrastructure;
- evidence artifact.

Они должны иметь разные entity types.

## P1 — Navigation

Нет audience journeys, breadcrumbs, local subnavigation и related-content graph.

## P1 — Provenance

Repository map не связан entity-to-repo-to-evidence.

## P1 — Knowledge completeness

Large guides представлены только карточками.

## P1 — Legacy integration

Iframe сохраняет legacy UI, но не интегрирует его content model.

## P1 — Version truth

`README.md`, `README-V17.md`, V7, V17 и legacy semantics сосуществуют без единой canonical version policy.

## P2 — SEO / discoverability

Большая доля content hidden in one HTML or JS-generated atlas; individual entities do not have stable URLs and metadata.

## P2 — Maintainability

Critical CSS and a large module dataset embedded in `index.html` complicate systematic growth.

---

# 9. Что обязательно сохраняется

Новая архитектура не имеет права потерять:

- все 12 main portal sections;
- все 8 Growth OS routes;
- все 10 Financial OS Deep chapters;
- все 4 Knowledge Hub sections;
- все module atlas entities;
- все 31 repo references;
- V16 crosswalk;
- evidence scale L0-L6;
- negative evidence;
- legacy Growth OS original page;
- money/solvency invariants;
- household economy;
- social finance;
- research and deep-tech branches;
- version/provenance history.

Следующий документ `V18_TOP_ARCHITECTURE.md` задаёт новую canonical систему, в которую всё перечисленное переносится без удаления.