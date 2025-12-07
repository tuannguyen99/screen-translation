# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Screen Translator
Run: pyinstaller build.spec
"""

import sys
from PyInstaller.utils.hooks import collect_all

# Collect all dependencies for manga_ocr and transformers
datas = []
binaries = []
hiddenimports = [
    'PIL',
    'PIL._imaging',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtWidgets', 
    'PyQt6.QtGui',
    'winocr',
    'deep_translator',
    'requests',
]

# For manga_ocr (optional - makes exe larger)
# Uncomment if you want manga_ocr included
# tmp_ret = collect_all('manga_ocr')
# datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
# tmp_ret = collect_all('transformers')
# datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.testing',
        'scipy',
        'pandas',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ScreenTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon='icon.ico' if you have one
)
