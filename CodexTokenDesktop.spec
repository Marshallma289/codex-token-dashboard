# -*- mode: python ; coding: utf-8 -*-

import sys

is_macos = sys.platform == 'darwin'
hidden_imports = ['webview', 'webview.platforms.cocoa'] if is_macos else [
    'webview', 'webview.platforms.edgechromium', 'webview.platforms.winforms'
]

a = Analysis(
    ['desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('web', 'web')],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CodexTokenDesktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=None if is_macos else 'assets/app-icon.ico',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CodexTokenDesktop',
)

if is_macos:
    app = BUNDLE(
        coll,
        name='CodexTokenDesktop.app',
        icon=None,
        bundle_identifier='com.marshallma289.codextokendashboard',
        info_plist={
            'CFBundleName': 'Codex Token Dashboard',
            'CFBundleDisplayName': 'Codex Token Dashboard',
            'LSMinimumSystemVersion': '12.0',
            'NSAppTransportSecurity': {'NSAllowsLocalNetworking': True},
        },
    )
