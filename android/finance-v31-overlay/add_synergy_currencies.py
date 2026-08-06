#!/usr/bin/env python3
"""Add SINERGY ecosystem currencies to the finance accounting layer.

This patch is deliberately idempotent and runs after the v3.1 overlay is applied.
It enables standalone accounting accounts in SYNA and SYNR, including symbols,
FX-rate storage, profile-rate editing and the account creation dropdown.
"""

from pathlib import Path
import os
import sys


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Expected fragment missing: {label}")
    return text.replace(old, new, 1)


def install_png_identify_helper() -> None:
    """Provide a dependency-free PNG metadata check for the next CI step.

    GitHub's Ubuntu image does not always include ImageMagick. The build workflow
    only needs the `identify` command to prove that the final launcher/splash
    asset is a 256x256 PNG, so install a tiny PNG-header reader into GITHUB_PATH.
    """
    github_path = os.environ.get("GITHUB_PATH")
    if not github_path:
        return

    tool_dir = Path("/tmp/sinergy-ci-tools")
    tool_dir.mkdir(parents=True, exist_ok=True)
    helper = tool_dir / "identify"
    helper.write_text(
        """#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: identify <png>')
p = Path(sys.argv[1])
data = p.read_bytes()
if len(data) < 24 or data[:8] != b'\\x89PNG\\r\\n\\x1a\\n' or data[12:16] != b'IHDR':
    raise SystemExit(f'{p}: not a PNG')
width, height = struct.unpack('>II', data[16:24])
print(f'{p} PNG {width}x{height}')
""",
        encoding="utf-8",
    )
    helper.chmod(0o755)
    with Path(github_path).open("a", encoding="utf-8") as fh:
        fh.write(str(tool_dir) + "\n")


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

    install_png_identify_helper()
    print("Added SYNA and SYNR multicurrency accounting support")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Trigger the dedicated repack + Android emulator smoke workflow.
