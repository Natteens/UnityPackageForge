# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, project_root)

block_cipher = None

# Define data files to include
datas = [
    ('ui/icon.ico', 'ui'),
    ('config.ini.example', '.'),
    ('README.md', '.'),
    ('LICENSE.md', '.'),
]

# Define hidden imports (modules that PyInstaller might miss)
hidden_imports = [
    'customtkinter',
    'requests',
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'cryptography.hazmat.primitives.hashes',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'configparser',
    'subprocess',
    'webbrowser',
    'threading',
    'queue',
    'json',
    'base64',
    'platform',
    'getpass',
    'shutil',
    'utils.resource_utils',
    'utils.crypto_utils',
    'utils.version_utils',
    'utils.helpers',
    'config.config_manager',
    'core.github_manager',
    'core.package_generator',
    'ui.ctk_generator_gui',
    'ui.strings',
]

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    name='unity-package-forge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed mode
    disable_windowing_subsystem=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ui/icon.ico',
    version='version_info.txt',  # Will be created by workflow if needed
    manifest='unity_package_forge.manifest',  # Windows manifest
)