# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Configurações base
project_root = Path(SPEC).parent.absolute()
sys.path.insert(0, str(project_root))

block_cipher = None

# Dados para incluir no executável
datas = []

# Arquivos essenciais
essential_files = [
    ('ui/icon.ico', 'ui'),
    ('config.ini.example', '.'),
    ('README.md', '.'),
    ('LICENSE.md', '.'),
    ('LICENSE', '.'),
]

for src, dst in essential_files:
    src_path = project_root / src
    if src_path.exists():
        datas.append((str(src_path), dst))
        print(f"✅ Including: {src} -> {dst}")
    else:
        print(f"⚠️ Missing: {src}")

# Imports ocultos necessários
hidden_imports = [
    # Core dependencies
    'customtkinter',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',

    # Cryptography
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.backends',

    # Tkinter
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.ttk',
    '_tkinter',

    # Standard library
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
    'pathlib',
    'datetime',
    'uuid',
    'hashlib',
    'tempfile',
    'zipfile',
    'tarfile',

    # Project modules
    'utils',
    'utils.resource_utils',
    'utils.crypto_utils',
    'utils.version_utils',
    'utils.helpers',
    'config',
    'config.config_manager',
    'core',
    'core.github_manager',
    'core.package_generator',
    'ui',
    'ui.ctk_generator_gui',
    'ui.strings',
]

# Módulos para excluir (otimização)
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'cv2',
    'tensorflow',
    'torch',
    'pygame',
    'wx',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
]

print("🔍 Scanning for Python modules...")

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

print("📦 Creating PYZ archive...")

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

print("🔨 Building executable...")

# Configurações do executável
exe_kwargs = {
    'pyz': pyz,
    'a.scripts': a.scripts,
    'a.binaries': a.binaries,
    'a.zipfiles': a.zipfiles,
    'a.datas': a.datas,
    'exclude_binaries': False,
    'name': 'unity-package-forge',
    'debug': False,
    'bootloader_ignore_signals': False,
    'strip': False,
    'upx': True,
    'upx_exclude': [],
    'runtime_tmpdir': None,
    'console': False,  # GUI app, sem console
    'disable_windowed_traceback': False,
    'target_arch': None,
    'codesign_identity': None,
    'entitlements_file': None,
}

# Configurações específicas por OS
if sys.platform.startswith('win'):
    exe_kwargs['icon'] = str(project_root / 'ui' / 'icon.ico') if (project_root / 'ui' / 'icon.ico').exists() else None
    exe_kwargs['version'] = 'version_info.txt' if Path('version_info.txt').exists() else None
    exe_kwargs['manifest'] = str(project_root / 'unity_package_forge.manifest') if (project_root / 'unity_package_forge.manifest').exists() else None
    print(f"🪟 Windows build - Icon: {exe_kwargs['icon']}, Version: {exe_kwargs['version']}")

elif sys.platform.startswith('darwin'):
    exe_kwargs['icon'] = str(project_root / 'ui' / 'icon.icns') if (project_root / 'ui' / 'icon.icns').exists() else None
    print(f"🍎 macOS build - Icon: {exe_kwargs['icon']}")

else:  # Linux
    print("🐧 Linux build")

exe = EXE(**exe_kwargs)

print("✅ Build configuration complete!")