#!/usr/bin/env python3
"""Add SINERGY ecosystem currencies to the finance accounting layer.

This patch is deliberately idempotent and runs after the v3.1 overlay is applied.
It enables standalone accounting accounts in SYNA and SYNR, including symbols,
FX-rate storage, profile-rate editing and the account creation dropdown.
"""

from pathlib import Path
import sys


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Expected fragment missing: {label}")
    return text.replace(old, new, 1)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: add_synergy_currencies.py <android-main-dir>")

    main_dir = Path(sys.argv[1]).resolve()
    app_js_path = main_dir / "assets" / "www" / "js" / "app.js"
    index_path = main_dir / "assets" / "www" / "index.html"

    app_js = app_js_path.read_text(encoding="utf-8")
    app_js = replace_once(
        app_js,
        "POL:'POL'};",
        "POL:'POL',SYNA:'SYNA',SYNR:'SYNR'};",
        "currencySymbols",
    )
    app_js = replace_once(
        app_js,
        "POL:'Polygon'};",
        "POL:'Polygon',SYNA:'Synergy Capital',SYNR:'Synergy Reserve'};",
        "currencyNames",
    )
    app_js = replace_once(
        app_js,
        "POL:110}},",
        "POL:110,SYNA:1,SYNR:1}},",
        "default FX rates",
    )
    app_js_path.write_text(app_js, encoding="utf-8")

    index = index_path.read_text(encoding="utf-8")
    index = replace_once(
        index,
        '<option value="POL">POL</option></select>',
        '<option value="POL">POL</option><option value="SYNA">SYNA · Synergy Capital</option><option value="SYNR">SYNR · Synergy Reserve</option></select>',
        "account currency dropdown",
    )
    index_path.write_text(index, encoding="utf-8")

    print("Added SYNA and SYNR multicurrency accounting support")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
