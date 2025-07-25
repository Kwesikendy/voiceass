# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['myra_installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('myra_hybrid.py', '.'),
        ('download_vosk_model.py', '.'),
    ],
    hiddenimports=[
        'speech_recognition',
        'pyttsx3',
        'requests',
        'tkinter',
        'threading',
        'zipfile',
        'json',
        'win32com.client'
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
    name='MyraVoiceAssistant_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # version='version_info.txt',
    # icon='myra_icon.ico'
)
