# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['media_manager_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('media_manager_final.ico', '.'),
        ('media_manager_solid.ico', '.'),
        ('media_manager_windows.ico', '.'),
        ('media_manager_new.ico', '.'),
        ('debug_test.ico', '.'),
        ('windows_solid_*.png', '.'),
        ('media_manager_solid_*.png', '.'),
        ('media_manager_windows_*.png', '.'),
        ('media_manager_new_*.png', '.'),
        ('media_manager_simple_*.png', '.'),
        ('media_manager_*.bmp', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
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
    name='MediaManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='media_manager_final.ico',  # Final multi-size ICO with proper Windows compatibility
    version_file=None,  # Add path to version file if needed
)
