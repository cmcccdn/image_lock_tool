# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Image Lock Tool background service

block_cipher = None

a = Analysis(
    ['../image_lock/service/lock_service.py'],
    pathex=['..'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'win32timezone',
        'win32serviceutil',
        'win32service',
        'win32event',
        'servicemanager',
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
    name='ImageLockToolService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='../resources/icon.ico',
    uac_admin=True,
)
