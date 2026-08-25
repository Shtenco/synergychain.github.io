# SINERGY SMM v3 — product status

The current v3 APK has proven Android/runtime/signing mechanics, but it is **NOT product-release-ready**.

## Reopened blocking gates

- PRODUCT FUNCTION COVERAGE: FAIL / rebuilding
- exact SINERGY-Finance native launcher/resource parity: FAIL / rebuilding

## Why

The recovered historical `smm-v2-clean` source and successful v2.0/v2.1 APK artifacts are demo/preview implementations and do not substantiate the legacy AI-SMM coverage claims. They must not be used as release sources.

A function is considered covered only when all four exist:

1. UI
2. implementation
3. real backend/provider path or real local implementation
4. test

Provider operations use explicit statuses: LOCAL, QUEUED, SENT, CONFIRMED, FAILED, UNSUPPORTED. No fake SENT/CONFIRMED state is allowed.

## Required product groups

AI/content, Autopilot, Calendar, Queue, Archive, Inbox, CRM, Audience, VK, Telegram, Facebook, Instagram, WhatsApp, OK, Zen, Analytics, Files, Jobs, Logs, Integrations, Settings.

## Branding rule

Do not use the current single `finance-launcher.png` placeholder as proof of Finance parity. The release must use the verified SINERGY-Finance Android launcher/adaptive-icon resource set and must prove parity against the Finance reference.

## Merge rule

PR #23 stays draft. Do not merge until the product function gate and exact Finance launcher parity pass, followed by fresh Web E2E, Android emulator, signing and final audit on the rebuilt product.
