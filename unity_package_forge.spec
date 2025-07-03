# -*- mode: python ; coding: utf-8 -*-

import os
import sys

project_root = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, project_root)

block_cipher = None

datas = []

if os.path.exists('ui/icon.ico'):
    datas.append(('ui/icon.ico', 'ui'))
if os.path.exists('config.ini.example'):
    datas.append(('config.ini.example', '.'))
if os.path.exists('README.md'):
    datas.append(('README.md', '.'))
if os.path.exists('LICENSE.md'):
    datas.append(('LICENSE.md', '.'))
elif os.path.exists('LICENSE'):
    datas.append(('LICENSE', '.'))

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
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ui/icon.ico' if os.path.exists('ui/icon.ico') else None,
)