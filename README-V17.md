# СИНЕРГИЯ V17 — Preserve + Unify Rebuild

V17 исправляет главный архитектурный дефект предыдущих V15/V16: новая политико-экономическая модель больше не заменяет существующий сайт и продукты.

## Главный принцип

**Существующее сохраняется буквально, новое добавляется сверху как canonical navigation / economic layer.**

- `index.html` — новый self-contained политико-экономический портал. Критические CSS и JS встроены прямо в HTML, поэтому файл остаётся оформленным даже при открытии отдельно.
- `legacy-growth-os.html` — точная сохранённая копия прежнего `index.html` Growth OS без переписывания.
- Новый портал встраивает legacy-страницу через iframe и также каталогизирует OLGA AGI, Business Autopilot, AI SMM, AI CRM, AI Sales, AI CFO и API Vault как прикладной слой экономики.

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

## Что дополнено

- единый атлас из политэкономики, Financial OS, токенов, соцфинансов, MetaPay/MetaBroker, MIDAS, Growth OS, NEXUS/AGI, blockchain/infrastructure, market research, real economy и deep-tech R&D;
- карта 31 известных репозиторных веток Shtenco;
- literal preservation старого Growth OS;
- адаптивный дизайн без внешних библиотек/CDN;
- поиск и фильтрация модулей прямо в self-contained `index.html`.

## Важный бухгалтерский принцип

`Canonical Wealth = ExternalAssets + CanonicalReserves + RealizedExternalPnL - Liabilities - Gas - Ops - MandatoryBuffers`

Внутренний mint/burn, TVL/MCAP uplift и нереализованные marks отображаются отдельно и не подменяют realized canonical surplus.

## Статусы

- `design` — спецификация / институт / правило;
- `prototype` — работающий код/UI, но не обязательно production;
- `experimental` — моделируемая/on-chain/fork ветка с измеримыми ограничениями;
- `research` — R&D, не рекламируется как доказанная production-технология.
