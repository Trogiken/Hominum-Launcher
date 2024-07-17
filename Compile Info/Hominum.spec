# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\noah\\Documents\\VSCode\\Hominum-Launcher\\Launcher\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\noah\\Documents\\VSCode\\Hominum-Launcher\\Launcher\\assets', 'assets/'), ('C:\\Users\\noah\\Documents\\VSCode\\Hominum-Launcher\\Launcher\\creds', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    'C:\\Users\\noah\\Documents\\VSCode\\Hominum-Launcher\\Compile Info\\splash.jpeg',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(75,35),
    text_size=16,
    text_color='#d9f8f6',
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [],
    exclude_binaries=True,
    name='Hominum',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    uac_admin=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\noah\\Documents\\VSCode\\Hominum-Launcher\\Compile Info\\versionfile.txt',
    icon=['C:\\Users\\noah\\Documents\\VSCode\\Hominum-Launcher\\Compile Info\\ctk.ico'],
    contents_directory='.',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Hominum',
)
