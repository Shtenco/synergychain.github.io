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

Dedicated surfaces exist for accounting, money, settlement, bridge, treasury, QE/QT, liquidity, solvency and canonical profit.

## Wave 02 — knowledge graph / passports completed

### Universal Entity Passport

`v18/explorer/entity.html?id=<entity-id>` creates a passport for every registered entity without duplicating HTML.

It automatically resolves identity, domain/subdomain/type, maturity/evidence, money role, incoming/outgoing graph edges, evidence artifacts, repository provenance, related entities and a manual deep route when available.

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

### Evidence / repository / coverage

- `v18/data/evidence.js` records `supports / contradicts / insufficient` independently from code presence.
- `v18/data/repositories.js` binds repositories to exact entity IDs instead of a flat list.
- `v18/explorer/coverage.html` calculates graph/evidence/repository/manual-deep-page coverage by domain and creates a gap queue.

## Wave 03 — Knowledge Library and taxonomy completed

### Canonical Token Taxonomy

Token branches keep stable IDs for provenance but are normalized under:

`Research → Tokenomics`

`v18/research/tokenomics.html` applies a backing / liability / cashflow / exit accounting gate to SYNA, SYNR, SYNC, USDS and Triple Non-Inflationary Emission research.

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

Semantic chapter maps are explicitly an index over source files, not a claim that generated chapter names reproduce a verbatim original table of contents.

## Deep manual passports already available

High-risk / high-value nodes have hand-curated deep pages in addition to the universal passport engine, including SettlementRouter, BaseBridgeVault, TimedQEController, PrefundedSettlementVault, AtomicCreditLiquidityManager, NEXUS, DEGOV, MetaPay, MIDAS, SINERGY Finance and Growth OS.

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

### Structural gate — PASS

The structural job checks JS syntax, entity IDs/schema, taxonomy, graph endpoints/types, evidence/repository bindings, Knowledge completeness, deep/local links, secret-like assignments and shared runtime usage.

Verified structural result:

- **103 entities**;
- **50 typed edges**;
- graph coverage **45 / 103**;
- **17 evidence artifacts** covering **34 / 103** entities;
- **31 repository bindings** covering **44 / 103** entities;
- **7 knowledge guides / 846 source pages**;
- **38 HTML pages** checked;
- structural validation **PASS**.

### Chromium visual/runtime gate — hardening in progress

The first real Chromium pass completed page loading and screenshot generation but rejected several routes because of root horizontal overflow. This was useful failure evidence rather than a hidden layout defect.

The shared runtime now installs a responsive layout guard that:

- clips decorative orbit overflow;
- allows long formulas, entity IDs and repository names to wrap;
- constrains all grid children to `min-width:0`;
- collapses Graph controls and relation rows on small screens;
- preserves local table scrolling instead of creating body overflow.

The smoke test now reports exact offending DOM nodes whenever overflow remains. A new full desktop/mobile/reduced-motion validation run is required after these fixes before visual status can be marked PASS.

## Remaining work after current waves

### Coverage expansion

The system now exposes its own gaps. Next target is to increase graph, evidence, repository and manual deep-page coverage, prioritizing economic/security-critical entities.

### Full-text Knowledge migration

846 pages are indexed and semantically decomposed, but original source text is not yet copied chapter-by-chapter into V18. Next waves should migrate full text while retaining source filenames, versions and citations.

### Provenance hardening

Add legacy alias registry, per-entity changelog/history, explicit supersession chains and source-document bindings beyond GitHub repositories.

### Production promotion

Only after green validation and zero unmapped critical V17 content:

- archive current root entrypoint;
- promote V18 routing to root;
- update `404.html` and root `README.md`;
- deploy a dedicated static artifact instead of unrelated repository root files;
- keep V17 permanently URL-accessible.
