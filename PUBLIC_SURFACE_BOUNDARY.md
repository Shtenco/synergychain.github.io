# SINERGYCHAIN public surface boundary

This repository remains the public static presentation build for SINERGYCHAIN Growth OS.

## Authority boundary

The public site is not an authoritative source for:

- canonical ledger balances;
- HardNAV or distributable profit;
- payment-provider credentials;
- private runtime state;
- financial authorization;
- AI model authority.

Any financial state displayed publicly should originate from an approved, versioned, digestible public snapshot or API boundary rather than being recreated from token-price assumptions in browser code.

## Deployment boundary

Backend code, databases, API keys, secrets and private runtime data remain outside the public GitHub Pages artifact.

## Historical preservation

Existing static bundles and rendering behavior are preserved. Federation documentation is additive and should not require destructive rewriting of the public site.

## Ownership

- `Shtenco/synergychain` owns the private source/control-plane application;
- `Shtenco/synergy_financial_os` owns canonical financial schemas/constitution;
- this repository owns only the public static presentation surface.
