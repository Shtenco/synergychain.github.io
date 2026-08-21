# SINERGY V18 · Knowledge Corpus Status

**Canonical corpus size:** 7 source documents · **846 source pages**.

This document separates three states that must never be conflated:

1. **Indexed** — a guide exists in `v18/data/knowledge.js` with semantic navigation.
2. **Repository-embedded** — source-page payload is physically stored in the GitHub branch and checksum-verifiable there.
3. **Full release corpus** — original source documents and generated full-text packs are included in the release ZIP / Google Drive source package.

As of the green V18 packaging wave, `knowledge.invest` (73 pages) is repository-embedded as byte-verified binary parts under `v18/data/knowledge-content/`. The complete 846-page original corpus is included in the full source release archive. The remaining corpus is not falsely marked repository-embedded until transport and checksum verification are complete.

## Source manifest

| Entity | Source file | Pages | SHA-256 |
|---|---|---:|---|
| `knowledge.invest` | `SINERGY_Invest_Russia_2026_Guide.html` | 73 | `ab6094762c62fbdf8a24cc0f9aed07614ea4a307971565d7a4cd6972aa9f97e6` |
| `knowledge.practice` | `SINERGY_Practical_Investing_Banks_2026_112_pages.html` | 112 | `2fb68242529e493e455619977b78ee6edf0acf46ebe83fc00ebdb4d38b3a9dab` |
| `knowledge.top50` | `SINERGY_TOP50_Russia_Investments_2026.html` | 61 | `7e680ca28591c14d2129aa85d708cfd653962279b7db2157dab72cfa0bbcb6f0` |
| `knowledge.deposits` | `SINERGY Вклады в России 2026.txt` | 78 | `b7a9df92f51fdf3ca2940a973abca749cad13658b179ae51532f112d54a234b0` |
| `knowledge.income` | `SINERGY_Internet_Income_Russia_2026_210plus.html` | 298 | `072e6c9d3b914cf59de11136dce58dcd69648250fcebb28bc4a7dd5ee2a6954d` |
| `knowledge.crisis` | `SINERGY_Anticrisis_12_Months_500K_2026.html` | 138 | `91f299c127a62d7b9c843689d94ecad1883693b8965dd8198440d335570f88ab` |
| `knowledge.assetsale` | `SINERGY_Gde_Prodat_Nenuzhnye_Veshchi_Russia_2026.html` | 86 | `d4cae321e64d3dbc28f59c191f7f841e62e81a2a55bcfb1a41b479a7c37bc7ba` |

**Total:** `73 + 112 + 61 + 78 + 298 + 138 + 86 = 846 pages`.

## Repository-embedded corpus

`v18/data/knowledge-content/invest-russia-2026.part01` … `part06` reconstruct the 73-page investment pack. GitHub blob IDs and expected local blob IDs are identical for every part.

The branch must not claim `FULL TEXT · 846 / 846 VERIFIED` until every remaining source pack is repository-embedded and independently reconstructed in CI.

## Full source release

The release archive is intentionally richer than the GitHub runtime tree. It contains:

- the green V18 source artifact built from the exact CI-passing commit;
- `KNOWLEDGE_ORIGINALS/` with all seven source documents above;
- `KNOWLEDGE_PACKS/` with generated gzip/JSON packs and manifests;
- `FULL_KNOWLEDGE_MANIFEST.json`;
- source and archive checksums.

This preserves all original material now without weakening the evidence standard of the repository/runtime layer.

## Invariant

```text
indexed != repository_embedded != full_release_corpus
```

A UI badge or documentation claim must reflect the exact state, not the intended future state.
