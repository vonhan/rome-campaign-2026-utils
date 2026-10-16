# -*- mode: python ; coding: utf-8 -*-

import os

_assets = [("assets/icon.png", "assets")]
if os.path.isfile("assets/Rome_campaign_2026_logo.png"):
    _assets.append(("assets/Rome_campaign_2026_logo.png", "assets"))

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=_assets,
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name="RomeCampaignPDF",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # Avoid UPX-packed bootloaders, which can trigger antivirus heuristics.
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
