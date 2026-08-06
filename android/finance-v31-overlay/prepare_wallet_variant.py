#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from wallet_v2_overlay import apply_wallet_v2


def patch_gradle(path: Path) -> None:
    text = path.read_text(encoding='utf-8')
    text = re.sub(r"applicationId\s+['\"][^'\"]+['\"]", "applicationId 'ai.sinergy.wallet'", text, count=1)
    text = re.sub(r"versionName\s+['\"][^'\"]+['\"]", "versionName '1.0.0'", text, count=1)
    text = re.sub(r'\bversionCode\s+\d+', 'versionCode 1', text, count=1)
    path.write_text(text, encoding='utf-8')


def patch_label(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<string name="app_name">.*?</string>', '<string name="app_name">SINERGY_WALLET</string>', text, count=1)
    path.write_text(text, encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('app_dir', type=Path)
    args = parser.parse_args()
    app = args.app_dir
    patch_gradle(app / 'build.gradle')
    patch_label(app / 'src/main/res/values/sinergy_branding.xml')
    patch_label(app / 'src/main/res/values-v31/sinergy_branding.xml')
    apply_wallet_v2(app)


if __name__ == '__main__':
    main()
