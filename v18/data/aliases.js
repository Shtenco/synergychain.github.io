window.SINERGY_ALIASES = [
{alias:'SYNG',entity:'token.syna',kind:'legacy-ambiguous',note:'Older portal materials used SYNG in token contexts. Treat as historical/ambiguous alias until governance publishes an explicit migration table; do not silently equate balances.'},
{alias:'Sinergy Anchor',entity:'token.syna',kind:'display-name',note:'V4 token naming branch.'},
{alias:'ALTNR',entity:'token.syna',kind:'former-contract-name',note:'Historical contract/comment name associated with the Anchor branch.'},
{alias:'Sinergy Rise',entity:'token.synr',kind:'display-name',note:'V4 token naming branch.'},
{alias:'ALTNP',entity:'token.synr',kind:'former-contract-name',note:'Historical contract/comment name associated with the Rise branch.'},
{alias:'Sinergy Cycle',entity:'token.sync',kind:'display-name',note:'V4/legacy token naming branch.'},
{alias:'ALTNT',entity:'token.sync',kind:'former-contract-name',note:'Historical contract/comment name associated with the Cycle branch.'},
{alias:'SUSD',entity:'fin.syusd',kind:'legacy-concept-name',note:'Some earlier simulators used SUSD for the elastic internal stable unit. V18 canonical conceptual name is SYUSD unless a contract generation explicitly says otherwise.'},
{alias:'Internal Stable',entity:'fin.syusd',kind:'concept-name',note:'Generic descriptive alias used in simulators.'},
{alias:'Canonical Settlement Asset',entity:'fin.usdcx',kind:'concept-name',note:'Reserve-backed settlement representation; explicitly not the same as elastic SYUSD.'},
{alias:'xReserve',entity:'fin.bridgevault',kind:'concept-layer',note:'Earlier V16 settlement diagrams used xReserve / reserve-attestation terminology for the canonical backing layer.'},
{alias:'SINERGY Pay',entity:'product.metapay',kind:'product-alias',note:'Payment-product naming used alongside MetaPay.'},
{alias:'Synergy Pay',entity:'product.metapay',kind:'product-alias',note:'English spelling variant at product layer; underlying infrastructure repository remains tech.pay.'},
{alias:'SHTENCO OS',entity:'tech.turbo',kind:'legacy-product-name',note:'Historical operating-system branding before/alongside TURBO OS.'},
{alias:'TURBO Linux',entity:'tech.turbo',kind:'implementation-repo-name',note:'Repository/implementation branch for the TURBO operating-system roadmap.'},
{alias:'OGAS 2.0',entity:'product.growth',kind:'historical-positioning',note:'Growth OS used OGAS 2.0 as product-positioning language; V18 treats OGAS as an intellectual reference, not a literal continuity claim.'},
{alias:'AGI OLGA',entity:'tech.agi',kind:'technology-name',note:'Technology/repository branch. Distinct from product.olga, which is the user-facing Growth OS application.'},
{alias:'OLGA AGI',entity:'product.olga',kind:'product-name',note:'User-facing Growth OS application; do not silently merge with tech.agi implementation branch.'},
{alias:'AI Blockchain',entity:'tech.chain',kind:'short-name',note:'Short display name for the SYNERGY AI Blockchain technology branch.'},
{alias:'SINERGYCHAIN',entity:'tech.synergychain',kind:'repository/core-name',note:'Core chain/source distribution branch; related to but not automatically identical with every later AI-blockchain implementation.'}
];

window.SINERGY_NON_ALIASES = [
{a:'token.usds',b:'fin.syusd',note:'USDS research branch is not automatically the elastic internal SYUSD unit.'},
{a:'token.usds',b:'fin.usdcx',note:'USDS research branch is not automatically the reserve-backed USDCx settlement representation.'},
{a:'fin.syusd',b:'fin.usdcx',note:'Elastic monetary-policy unit and reserve-backed settlement representation are deliberately separate.'},
{a:'product.olga',b:'tech.agi',note:'Product surface and technology/repository branch are related but distinct entities.'},
{a:'product.metapay',b:'tech.pay',note:'Payment product and payment-infrastructure code branch are distinct layers.'}
];
