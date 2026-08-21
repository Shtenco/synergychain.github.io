# SINERGY V18 — Migration Status

Branch: `portal-v18-top`  
Base: `portal-v17-rebuild`

## Principle

V18 is built **beside** V17. Root V17 remains unchanged until V18 passes content mapping, structural validation and browser visual/runtime smoke tests.

Promotion invariant:

```text
unmapped_v17_content == 0
broken_internal_links == 0
unknown_entity_refs == 0
duplicate_entity_ids == 0
critical_runtime_errors == 0
critical_visual_overflow == 0
```

## Wave 01 — top architecture completed

### Shared platform

- `v18/assets/sinergy-v18.css` — shared visual system.
- `v18/assets/sinergy-v18.js` — shared motion, responsive guard and Explorer runtime.
- `v18/data/entities.js` — canonical entity registry.
- `v18/index.html` — domain map / portal home.

### Nine canonical spaces

1. Model.
2. Financial OS.
3. Institutions.
4. Products.
5. Technology.
6. Research.
7. Knowledge.
8. Explorer.
9. Archive.

### Financial OS decomposition

Dedicated surfaces exist for:

- accounting;
- money;
- settlement;
- bridge;
- treasury;
- QE/QT;
- liquidity;
- solvency;
- canonical profit.

## Wave 02 — knowledge graph / passports completed

### Universal Entity Passport

`v18/explorer/entity.html?id=<entity-id>` creates a passport for every registered entity without duplicating HTML.

It automatically resolves:

- ID / domain / subdomain / entity type;
- status and evidence level;
- system / money role;
- incoming and outgoing typed graph relations;
- supporting / contradicting / insufficient evidence artifacts;
- repository provenance;
- related entities;
- manual deep-page route when one exists.

### Typed Dependency Graph

`v18/data/edges.js` + `v18/explorer/graph.html` support:

- `depends_on`;
- `creates_claim`;
- `funds`;
- `governed_by`;
- `settles_into`;
- `evidence_for`;
- `supersedes`;
- `contradicts`.

Graph Explorer is focus-driven:

`graph.html?focus=<entity-id>`

Any entity can become the center of a 1–2 hop local graph.

### Evidence Registry

`v18/data/evidence.js` records evidence independently from source code presence.

Statuses:

- `supports`;
- `contradicts`;
- `insufficient`.

Negative evidence remains first-class data.

### Repository Registry

`v18/data/repositories.js` binds repositories to exact entity IDs instead of maintaining a flat project list.

### Coverage Dashboard

`v18/explorer/coverage.html` calculates graph / evidence / repository / manual-deep-page coverage by domain and automatically builds a gap queue.

## Wave 03 — Knowledge Library and taxonomy completed

### Canonical Token Taxonomy

Token branches keep stable IDs for provenance but are normalized under:

`Research → Tokenomics`

Current research entities include:

- SYNA;
- SYNR;
- SYNC legacy branch;
- USDS;
- Triple Non-Inflationary Emission research.

`v18/research/tokenomics.html` applies a backing / liability / cashflow / exit accounting gate.

### Knowledge Library

`v18/data/knowledge.js` + `v18/knowledge/library.html` + `v18/knowledge/guide.html?id=...`

Current indexed sources:

- Investments Russia 2026 — 73 pages;
- Practical Investing & Banks 2026 — 112 pages;
- TOP-50 Russia 2026 — 61 pages;
- Deposits Russia 2026 — 78 pages;
- Internet Income 2026 — 298 pages;
- 12-Month Anti-Crisis Plan — 138 pages;
- Sell Unused Assets 2026 — 86 pages.

Total indexed source pages: **846**.

Semantic chapter maps are explicitly an index over source files, not a claim that the generated chapter names reproduce a verbatim original table of contents.

## Deep manual passports already available

High-risk / high-value nodes also have hand-curated deep pages in addition to the universal passport engine, including:

- SettlementRouter;
- BaseBridgeVault;
- TimedQEController;
- PrefundedSettlementVault;
- AtomicCreditLiquidityManager;
- NEXUS;
- DEGOV;
- MetaPay;
- MIDAS;
- SINERGY Finance;
- Growth OS.

## Visual system

V18 uses one shared visual language without external visual libraries:

- moving optical flow-field canvas;
- repeating conic / radial moiré fields;
- pseudo-3D perspective grid;
- rotating orbital maps;
- optical tunnel sections;
- pointer aura;
- card-local lighting and optional perspective tilt;
- kinetic text parallax;
- intersection reveals;
- scanline effects;
- responsive layout guard for long formulas, entity IDs, repository names and graph UI.

Accessibility invariant:

`prefers-reduced-motion: reduce` disables decorative animation/parallax.

## CI / validation

Workflow: `.github/workflows/validate-v18.yml`

### Structural gate

Checks:

- JS syntax;
- duplicate / missing entity IDs;
- canonical domain taxonomy;
- unknown edge endpoints / edge types;
- evidence → entity references;
- repository → entity references;
- Knowledge registry completeness;
- registry deep-page targets;
- literal local `href/src` targets;
- secret-like assignments;
- shared CSS/runtime usage.

A verified run on the V18 branch has already passed this structural gate with:

- 103 entities;
- 50 typed edges;
- graph coverage 45 / 103;
- 17 evidence artifacts covering 34 / 103 entities;
- 31 repository bindings covering 44 / 103 entities;
- 7 knowledge guides / 846 source pages;
- 38 HTML pages checked.

### Chromium visual/runtime gate

The browser job runs desktop + mobile routes plus reduced-motion mode and checks:

- HTTP success;
- page/runtime errors;
- request failures;
- visible content;
- shared visual shell;
- root horizontal overflow;
- token taxonomy rendering;
- Knowledge Library totals;
- representative screenshots.

First real browser run found layout overflow on several pages. The shared responsive guard has been strengthened and the smoke script now reports exact offending DOM elements for any remaining overflow. This gate must be green before root promotion.

## Remaining work after current waves

### Coverage expansion

The system now exposes its own gaps. Next migration target is to increase:

- graph coverage;
- evidence coverage;
- repository coverage;
- manual deep-page coverage for economically/security-critical nodes.

### Full-text Knowledge migration

846 pages are indexed and semantically decomposed, but the original source text is not yet copied chapter-by-chapter into V18. Next waves should migrate full text while retaining source filenames and version stamps.

### Provenance hardening

Add:

- legacy alias registry;
- per-entity changelog/history;
- explicit supersession chains;
- source document bindings beyond GitHub repositories.

### Production promotion

Only after green validation and zero unmapped critical V17 content:

- archive current root entrypoint;
- promote V18 routing to root;
- update `404.html`;
- update root `README.md`;
- deploy a dedicated built/static artifact instead of unrelated repository root files;
- keep V17 permanently URL-accessible.
