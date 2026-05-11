# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Image Lock Tool (GUI)

block_cipher = None

a = Analysis(
    ['../gui.py'],
    pathex=['..'],
    binaries=[],
    datas=[
        ('../resources/icon.ico', 'resources'),
        ('../resources/icon.png', 'resources'),
    ],
    hiddenimports=[
        'customtkinter',
        'pystray',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinterdnd2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageLockTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../resources/icon.ico',
    uac_admin=True,
)
