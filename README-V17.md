# СИНЕРГИЯ V17 — Preserve + Unify Rebuild

V17 исправляет главный архитектурный дефект V15/V16: новая политико-экономическая модель больше не заменяет существующий сайт и продукты.

## Открывать отсюда

- [`index.html`](./index.html) — единый политико-экономический портал, self-contained CSS/JS.
- [`legacy-growth-os.html`](./legacy-growth-os.html) — **байт-в-байт сохранённый предыдущий Growth OS**.
- [`financial-os-deep.html`](./financial-os-deep.html) — глубокая инженерная архитектура Financial OS: Base bridge, timer-QE, flash batch, prefunded settlement, atomic credit LP.
- [`knowledge-hub.html`](./knowledge-hub.html) — образовательный / household-economy слой SINERGY.
- [`docs/V17_ARCHITECTURE.md`](./docs/V17_ARCHITECTURE.md) — системная архитектура.
- [`docs/V16_TO_V17_CROSSWALK.md`](./docs/V16_TO_V17_CROSSWALK.md) — контрольный список: куда перенесён каждый смысловой блок V16.
- [`assets/portal-v17.css`](./assets/portal-v17.css) — development style mirror. Production-critical CSS встроен непосредственно в `index.html`.

## Главный принцип

**Существующее сохраняется буквально, новое добавляется сверху как canonical navigation / economic layer.**

Старый Growth OS не переписывается и не удаляется. Он хранится отдельной страницей и встроен в новый портал через iframe. Одновременно его основные приложения каталогизированы внутри общей экономической карты:

- OLGA AGI;
- Business Autopilot;
- AI SMM;
- AI CRM;
- AI Sales;
- AI CFO;
- API Vault / model routing.

## Что включено из V16

1. Four-plane Financial OS: External Value, Settlement & Solvency, Internal Monetary, Institutional.
2. Two-money architecture: `xETH/SYUSD` отдельно от `USDCx/native USDC`.
3. Invariants:
   - `Supply(xETH) <= verified ETH locked`
   - `Supply(USDCx) <= verified canonical USDC backing`
   - `USDCxOut <= AvailableCanonicalBacking`
4. Consolidated NAV и Liability Registry.
5. QE/QT, ограниченный реальным Treasury / affordable gradient.
6. Canonical Profit Guard и явный External Demand / Solver.
7. Source-of-Funds Gate: mint, MCAP, sync, bridge transport и capital rotation не считаются external revenue.
8. Social Finance / Anti-Pyramid: долг уменьшается только при реальном extinguishment creditor claim.
9. Governance boundary: `AI proposes -> DAO authorizes -> contract executes -> ledger proves -> human challenge/exit`.
10. Evidence Ledger L0-L6 и сохранение отрицательных результатов.
11. Token canon / legacy-name разделение.
12. Source/repository provenance.

Полный V16 crosswalk находится в `docs/V16_TO_V17_CROSSWALK.md`.

## Что добавлено после глубокого восстановления Financial OS

V17 различает раннюю canonical concept architecture и более позднюю engineering branch.

### Canonical concept

- `xETH`
- `SYUSD`
- `USDCx`
- `SettlementRouter`
- canonical backing / liability-adjusted NAV.

### Engineering implementation branch

- `BaseBridgeVault`
- `BaseArbExecutor`
- `BridgeAsset`
- `InternalBridgeEndpoint`
- `TimedQEController`
- backed QE credit
- `FlashBatchExecutor`
- `PrefundedSettlementVault`
- `BaseInventoryCycleAdapter`
- `AtomicCreditLiquidityManager`
- settlement quote / receivable accounting
- flash premium / gas / MEV guards
- atomic temporary credit with `outstandingCreditMint == 0`
- temporary LP timer-QE neutralization
- fork/mainnet deployment gates.

Подробнее: `financial-os-deep.html`.

## Прикладной Knowledge / Household слой

В отдельный слой экосистемы возвращены и организованы образовательные ветки:

- Инвестиции в России 2026 — 73 страницы;
- Практика инвестиций / банков — 112 страниц;
- TOP-50 Россия 2026 — 61 страница;
- Вклады в России 2026 — 78 страниц;
- Интернет-заработок 2026 — 298 страниц;
- Антикризисный план 12 месяцев — 138 страниц;
- Куда продать ненужные вещи — 86 страниц;
- SINERGY Finance как household ledger / Net Worth приложение.

В V17 эти материалы классифицируются как **education / household Financial OS / product layer**, а не смешиваются с protocol treasury или DAO reserves.

## Экосистема, которую индексирует V17

Портал объединяет:

- политэкономию DESOCI / коллективно-децентрализованную модель;
- DEGOV / DAO / budget governance;
- Financial OS;
- SYNA / SYNR / SYNC / USDS token research;
- MetaPay / Synergy Pay;
- MetaBroker;
- MIDAS / market AI;
- OLGA / NEXUS / AI products;
- Growth OS;
- Social Finance / mutual aid / P2P credit replacement;
- SYNERGY AI Blockchain / post-quantum roadmap;
- TURBO OS / infrastructure;
- graph / quantum / computer-vision / arbitrage / macro-liquidity trading research;
- real-economy cells;
- deep-tech R&D;
- education and personal-capital formation.

## Важный бухгалтерский принцип

`Canonical Wealth = ExternalAssets + CanonicalReserves + RealizedExternalPnL - Liabilities - Gas - Ops - MandatoryBuffers`

Внутренний mint/burn, TVL/MCAP uplift и нереализованные marks отображаются отдельно и не подменяют realized canonical surplus.

## Статусы

- `design` — спецификация / институт / правило;
- `prototype` — работающий код/UI, но не обязательно production;
- `experimental` — моделируемая/on-chain/fork ветка с измеримыми ограничениями;
- `research` — R&D, не рекламируется как доказанная production-технология.

## Почему стили больше не должны «пропадать»

Критический CSS и JS **встроены непосредственно в `index.html`**. Поэтому если открыть или скачать только главный HTML, его основной дизайн, atlas, фильтры и QE/QT interaction остаются на месте. Внешний `assets/portal-v17.css` — лишь development mirror, а не runtime-зависимость.
