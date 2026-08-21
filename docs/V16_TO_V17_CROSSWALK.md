# V16 → V17 crosswalk

The purpose of this document is to make it impossible to lose a V16 concept silently during future redesigns.

| V16 area | V17 destination | Migration rule |
|---|---|---|
| Hero / doctrine | `index.html` → Political Economy | Preserved and expanded |
| Market + collective capital thesis | Political Economy | Preserved |
| Personal ownership / right to exit | Economic Constitution | Preserved |
| Polycentric governance | Political Economy + Governance | Preserved |
| AI not sovereign | Governance boundary | Preserved |
| Four Financial OS planes | `index.html` → Financial OS | Preserved |
| External Value Plane | Financial OS | Preserved |
| Settlement & Solvency Plane | Financial OS + `financial-os-deep.html` | Expanded |
| Internal Monetary Plane | Money + Policy | Preserved |
| Institutional Plane | Financial OS + Growth OS + value engine | Expanded |
| xETH / external custody | Money + Deep Financial OS | Preserved |
| SYUSD elastic monetary unit | Money + Deep Financial OS | Preserved |
| USDCx reserve-backed settlement | Money + Deep Financial OS | Preserved |
| SettlementRouter | Money | Preserved |
| `Supply(xETH) <= ETH locked` | Money / Architecture docs | Preserved |
| `USDCxOut <= AvailableCanonicalBacking` | Money / Architecture docs | Preserved |
| Gross TVL vs canonical assets | NAV ledger | Preserved |
| Liability-adjusted canonical NAV | NAV ledger | Preserved |
| Unrealized/internal uplift separate | NAV ledger | Preserved |
| Source-of-Funds Gate | Value Engine / module atlas | Preserved |
| Liability Registry | Financial OS / atlas | Preserved |
| Bridge Solvency Buffer | Financial OS / atlas | Preserved |
| Canonical Profit Guard | Financial OS / atlas | Preserved |
| External Demand / Solver | Financial OS / atlas | Preserved |
| AI Treasury Policy Engine | QE/QT section | Preserved |
| Economic Stress Engine | Evidence / atlas | Preserved |
| Affordable gradient | QE/QT + deep engineering | Preserved |
| Treasury-bounded QT / buyback | QE/QT | Preserved |
| Mint ≠ profit | Hero / Policy / Accounting | Preserved |
| Bridge ≠ value creation | Hero / Policy / Accounting | Preserved |
| External demand explicit | Policy / Profit Guard | Preserved |
| Unsafe gradient → reduce/stop | Policy | Preserved |
| Base-fork negative solvency result | NAV / negative evidence | Preserved |
| Social finance | Social Finance | Preserved and expanded |
| Mutual aid fund | Social Finance / atlas | Preserved |
| Anti-pyramid escrow | Social Finance / atlas | Preserved |
| P2P credit replacement | Social Finance / atlas | Preserved |
| Debt clearing / netting | Social Finance / atlas | Preserved |
| Debt burn ≠ claim extinguishment | Social Finance | Preserved |
| Governance ownership/cashflow separation | Governance | Preserved |
| `AI proposes → DAO authorizes → contract executes → ledger proves → human challenge/exit` | Governance | Preserved |
| MetaPay | External value / atlas | Preserved |
| MetaBroker | External value / atlas | Preserved |
| MIDAS | External value / atlas | Preserved |
| AI services | External value + Growth OS | Expanded |
| Real economy revenue | External value + real economy modules | Expanded |
| External investment not profit | Source-of-value | Preserved |
| Token canon SYNA/SYNC/SYNR/USDS | Atlas | Preserved |
| Evidence L0–L6 | Evidence Ledger | Preserved |
| Negative evidence | Evidence Ledger + deep Financial OS | Expanded |
| V14 source memory | Archive / provenance | Preserved conceptually |
| Repository map | Archive / repository map | Preserved and expanded to known 31 repos |
| Growth OS products | Existing Growth OS layer | Added as literal preserved legacy site and functional modules |
| Styles / visual system | Self-contained `index.html` | Fixed: no external critical CSS dependency |

## New engineering layer added after V16

The following recovered/engineering components are intentionally **not folded invisibly into the older names**. They are represented as an implementation branch under the same accounting invariants:

- `BaseBridgeVault`
- `BaseArbExecutor`
- `BridgeAsset`
- `InternalBridgeEndpoint`
- `TimedQEController`
- QE credit backed by canonical Base-side assets
- accrued bridge fees → governance-authorized QE credit
- `FlashBatchExecutor`
- `PrefundedSettlementVault`
- `BaseInventoryCycleAdapter`
- settlement quotes/tickets
- explicit `outstandingReceivable`
- receivable cap and prefunded inventory safety buffer
- `AtomicCreditLiquidityManager`
- temporary `creditMint/creditBurn`
- temporary ADDLP
- pro-rata timer-QE neutralization
- `outstandingCreditMint == 0` end-of-batch invariant
- flash premium/gas/MEV-aware profit guards
- fork/mainnet deployment gates

These components are described in `financial-os-deep.html` rather than being misrepresented as identical to the earlier `SYUSD/USDCx/SettlementRouter` conceptual architecture.
