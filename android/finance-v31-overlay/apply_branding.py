#!/usr/bin/env python3
import argparse
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from finance_investment_overlay import apply_investment_overlay

ANDROID_NS = 'http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID_NS)
A = '{%s}' % ANDROID_NS


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str):
    ensure_dir(path.parent)
    path.write_text(text, encoding='utf-8')


def patch_gradle(gradle: Path, app_id: str, version_name: str, version_code: int):
    text = gradle.read_text(encoding='utf-8')
    text = re.sub(r"applicationId\s+['\"][^'\"]+['\"]", f"applicationId '{app_id}'", text, count=1)
    text = re.sub(r"versionName\s+['\"][^'\"]+['\"]", f"versionName '{version_name}'", text, count=1)
    if re.search(r'\bversionCode\s+\d+', text):
        text = re.sub(r'\bversionCode\s+\d+', f'versionCode {version_code}', text, count=1)
    else:
        text = text.replace('defaultConfig {', f'defaultConfig {{\n        versionCode {version_code}', 1)
    gradle.write_text(text, encoding='utf-8')


def remove_existing_app_name(strings_file: Path):
    if not strings_file.exists():
        return
    text = strings_file.read_text(encoding='utf-8')
    text, count = re.subn(r'\s*<string\s+name=["\']app_name["\'][^>]*>.*?</string>', '', text, count=1, flags=re.S)
    if count:
        strings_file.write_text(text, encoding='utf-8')


def patch_manifest(manifest: Path, label: str):
    tree = ET.parse(manifest)
    root = tree.getroot()
    app = root.find('application')
    if app is None:
        raise RuntimeError('AndroidManifest.xml has no <application>')
    old_theme = app.get(A + 'theme') or '@android:style/Theme.Material.Light.NoActionBar'
    app.set(A + 'label', '@string/app_name')
    app.set(A + 'icon', '@mipmap/ic_launcher')
    app.set(A + 'roundIcon', '@mipmap/ic_launcher_round')
    app.set(A + 'theme', '@style/Theme.Sinergy.Starting')
    for activity in app.findall('activity') + app.findall('activity-alias'):
        if activity.get(A + 'name', '').endswith('MainActivity'):
            activity.set(A + 'label', '@string/app_name')
            activity.set(A + 'icon', '@mipmap/ic_launcher')
            activity.set(A + 'roundIcon', '@mipmap/ic_launcher_round')
            activity.set(A + 'theme', '@style/Theme.Sinergy.Starting')
    perms = {p.get(A + 'name') for p in root.findall('uses-permission')}
    if 'android.permission.INTERNET' not in perms:
        permission = ET.Element('uses-permission')
        permission.set(A + 'name', 'android.permission.INTERNET')
        root.insert(0, permission)
    tree.write(manifest, encoding='utf-8', xml_declaration=True)
    return old_theme


def style_parent(theme_ref: str) -> str:
    if theme_ref.startswith('@style/'):
        return theme_ref[len('@style/'):]
    if theme_ref.startswith('@android:style/'):
        return theme_ref
    return '@android:style/Theme.Material.Light.NoActionBar'


def write_resources(res: Path, label: str, old_theme: str):
    parent = style_parent(old_theme)
    write_text(res / 'values' / 'sinergy_branding.xml', f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{label}</string>
    <color name="sinergy_icon_background">#002C20</color>
    <color name="sinergy_splash_background">#001A13</color>
    <style name="Theme.Sinergy.Starting" parent="{parent}">
        <item name="android:windowBackground">@drawable/sinergy_launch_background</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:colorAccent">#00EF73</item>
        <item name="android:navigationBarColor">#001A13</item>
        <item name="android:statusBarColor">#001A13</item>
        <item name="android:windowLightStatusBar">false</item>
    </style>
</resources>
''')
    write_text(res / 'values-v31' / 'sinergy_branding.xml', f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.Sinergy.Starting" parent="{parent}">
        <item name="android:windowBackground">@drawable/sinergy_launch_background</item>
        <item name="android:windowSplashScreenBackground">@color/sinergy_splash_background</item>
        <item name="android:windowSplashScreenAnimatedIcon">@drawable/sinergy_splash_icon</item>
        <item name="android:windowSplashScreenIconBackgroundColor">@color/sinergy_splash_background</item>
        <item name="android:windowSplashScreenAnimationDuration">350</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:colorAccent">#00EF73</item>
        <item name="android:navigationBarColor">#001A13</item>
        <item name="android:statusBarColor">#001A13</item>
        <item name="android:windowLightStatusBar">false</item>
    </style>
</resources>
''')
    write_text(res / 'drawable' / 'sinergy_launch_background.xml', '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@color/sinergy_splash_background" />
    <item android:gravity="center" android:width="220dp" android:height="220dp">
        <bitmap android:src="@drawable/sinergy_splash" android:gravity="center" />
    </item>
</layer-list>
''')
    write_text(res / 'drawable' / 'sinergy_splash_icon.xml', '''<?xml version="1.0" encoding="utf-8"?>
<inset xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/sinergy_splash"
    android:inset="12%" />
''')
    write_text(res / 'drawable' / 'ic_launcher_foreground.xml', '''<?xml version="1.0" encoding="utf-8"?>
<inset xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/sinergy_logo"
    android:inset="14%" />
''')
    write_text(res / 'drawable' / 'ic_launcher_foreground_round.xml', '''<?xml version="1.0" encoding="utf-8"?>
<inset xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/sinergy_logo"
    android:inset="14%" />
''')
    adaptive = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/sinergy_icon_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
'''
    write_text(res / 'mipmap-anydpi-v26' / 'ic_launcher.xml', adaptive)
    write_text(res / 'mipmap-anydpi-v26' / 'ic_launcher_round.xml', adaptive)


def install_assets(asset_root: Path, res: Path, www: Path):
    if not asset_root.exists():
        raise RuntimeError(f'Branding asset root not found: {asset_root}')
    for src in asset_root.rglob('*'):
        if src.is_file():
            dst = res / src.relative_to(asset_root)
            ensure_dir(dst.parent)
            shutil.copy2(src, dst)
    logo = asset_root / 'drawable-nodpi' / 'sinergy_logo.png'
    if logo.exists():
        ensure_dir(www / 'icons')
        shutil.copy2(logo, www / 'icons' / 'sinergy-logo.png')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('app_dir', type=Path)
    ap.add_argument('--label', required=True)
    ap.add_argument('--application-id', required=True)
    ap.add_argument('--version-name', required=True)
    ap.add_argument('--version-code', type=int, required=True)
    ap.add_argument('--assets', type=Path, required=True)
    args = ap.parse_args()

    app = args.app_dir
    src = app / 'src' / 'main'
    manifest = src / 'AndroidManifest.xml'
    gradle = app / 'build.gradle'
    res = src / 'res'
    www = src / 'assets' / 'www'
    if not manifest.exists() or not gradle.exists():
        raise RuntimeError(f'Invalid Android app directory: {app}')

    patch_gradle(gradle, args.application_id, args.version_name, args.version_code)
    remove_existing_app_name(res / 'values' / 'strings.xml')
    old_theme = patch_manifest(manifest, args.label)
    write_resources(res, args.label, old_theme)
    install_assets(args.assets, res, www)
    apply_investment_overlay(www)

    manifest_text = manifest.read_text(encoding='utf-8')
    gradle_text = gradle.read_text(encoding='utf-8')
    assert '@mipmap/ic_launcher' in manifest_text
    assert '@style/Theme.Sinergy.Starting' in manifest_text
    assert args.label in (res / 'values' / 'sinergy_branding.xml').read_text(encoding='utf-8')
    assert args.application_id in gradle_text
    assert (www / 'js/investments-v4.js').exists()
    print(f'BRANDING_OK label={args.label} applicationId={args.application_id} version={args.version_name} investments=v4')

if __name__ == '__main__':
    main()
