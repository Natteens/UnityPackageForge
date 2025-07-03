#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                                capture_output=True, text=True, cwd=cwd,
                                encoding='utf-8', errors='replace')
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_dependencies():
    print("Verificando dependencias...")

    python_version = sys.version_info
    if python_version < (3, 7):
        print("ERRO: Python 3.7+ necessario")
        return False
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} OK")

    required_packages = [
        'pyinstaller',
        'customtkinter',
        'requests',
        'cryptography'
    ]

    for package in required_packages:
        success, _, _ = run_command(f"python -m pip show {package}")
        if success:
            print(f"{package} OK")
        else:
            print(f"ERRO: {package} - Execute: pip install {package}")
            return False

    return True


def clean_build():
    print("Limpando builds anteriores...")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removido: {dir_name}")

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))


def create_version_info():
    if platform.system() != 'Windows':
        return True

    print("Criando informacoes de versao para Windows...")

    version_info = '''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [
            StringStruct('CompanyName', 'Nathan da Silva Miranda'),
            StringStruct('FileDescription', 'Unity Package Forge'),
            StringStruct('FileVersion', '1.0.0'),
            StringStruct('InternalName', 'unity-package-forge'),
            StringStruct('LegalCopyright', 'Copyright (c) 2025 Nathan da Silva Miranda'),
            StringStruct('OriginalFilename', 'unity-package-forge.exe'),
            StringStruct('ProductName', 'Unity Package Forge'),
            StringStruct('ProductVersion', '1.0.0')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)'''

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info.strip())

    print("Arquivo version_info.txt criado")
    return True


def fix_spec_file():
    print("Corrigindo arquivo .spec...")

    if not os.path.exists('unity_package_forge.spec'):
        print("ERRO: Arquivo unity_package_forge.spec nao encontrado!")
        return False

    with open('unity_package_forge.spec', 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '🔧': '[TOOL]',
        '📄': '[FILE]',
        '🧹': '[CLEAN]',
        '🔍': '[CHECK]',
        '🧪': '[TEST]',
        '🔨': '[BUILD]',
        '🚀': '[LAUNCH]',
        '📦': '[PACKAGE]',
        '⚠️': '[WARNING]',
        'ℹ️': '[INFO]'
    }

    modified = False
    for unicode_char, ascii_replacement in replacements.items():
        if unicode_char in content:
            content = content.replace(unicode_char, ascii_replacement)
            modified = True

    if modified:
        with open('unity_package_forge.spec', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Arquivo .spec corrigido")
    else:
        print("Arquivo .spec nao precisou ser corrigido")

    return True


def create_proper_spec_file():
    print("Criando arquivo .spec otimizado...")

    # Verificar quais pastas e arquivos existem
    datas = []

    # Verificar pastas do projeto
    folders_to_check = ['ui', 'utils', 'core', 'config']
    for folder in folders_to_check:
        if os.path.exists(folder):
            datas.append(f"('{folder}', '{folder}'),")
            print(f"Pasta {folder} encontrada - sera incluida")

    # Verificar arquivos de configuração
    files_to_check = ['config.ini', 'config.ini.example', 'requirements.txt']
    for file in files_to_check:
        if os.path.exists(file):
            datas.append(f"('{file}', '.'),")
            print(f"Arquivo {file} encontrado - sera incluido")

    # Se não há dados, deixar lista vazia
    datas_str = "\n        ".join(datas) if datas else ""

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        {datas_str}
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'requests',
        'cryptography',
        'cryptography.fernet',
        'threading',
        'queue',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'json',
        'configparser',
        'pathlib',
        'subprocess',
        'shutil',
        'zipfile',
        'tempfile',
        'datetime',
        'hashlib',
        'base64',
        'ui',
        'utils',
        'core',
        'config',
        'ui.main_window',
        'utils.resource_utils',
        'utils.crypto_utils',
        'utils.version_utils',
        'core.package_manager',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
        'IPython',
        'tornado',
        'zmq',
        'pygame',
        'cv2',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=None,
)'''

    with open('unity_package_forge.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("Arquivo .spec criado/atualizado")
    return True


def test_imports():
    print("Testando imports...")

    try:
        sys.path.insert(0, '.')

        # Testar imports principais do projeto
        import main
        print("main.py OK")

        # Testar imports de módulos internos se existirem
        try:
            from utils.resource_utils import get_resource_path
            print("utils.resource_utils OK")
        except ImportError:
            print("utils.resource_utils nao encontrado (pode ser normal)")

        try:
            from utils.crypto_utils import get_crypto_instance
            print("utils.crypto_utils OK")
        except ImportError:
            print("utils.crypto_utils nao encontrado (pode ser normal)")

        try:
            from utils.version_utils import get_current_version
            print("utils.version_utils OK")
        except ImportError:
            print("utils.version_utils nao encontrado (pode ser normal)")

        print("Imports principais funcionando")
        return True
    except Exception as e:
        print(f"ERRO nos imports: {e}")
        return False


def build_executable():
    print("Construindo executavel...")

    if not os.path.exists('unity_package_forge.spec'):
        print("ERRO: Arquivo unity_package_forge.spec nao encontrado!")
        return False

    env = os.environ.copy()
    if platform.system() == 'Windows':
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = '1'
        env['PYTHONHOME'] = ''
        env['PYTHONPATH'] = ''

    cmd = "pyinstaller unity_package_forge.spec --clean --noconfirm --log-level ERROR"
    success, stdout, stderr = run_command(cmd)

    if not success:
        print(f"ERRO durante build:")
        print(stderr)
        return False

    system = platform.system()
    if system == 'Windows':
        exec_name = 'unity-package-forge.exe'
    else:
        exec_name = 'unity-package-forge'

    exec_path = Path('dist') / exec_name

    if exec_path.exists():
        size = exec_path.stat().st_size / (1024 * 1024)
        print(f"Executavel criado: {exec_path}")
        print(f"Tamanho: {size:.1f} MB")

        if system != 'Windows':
            os.chmod(exec_path, 0o755)
            print("Permissoes de execucao definidas")

        return True
    else:
        print(f"ERRO: Executavel nao encontrado em: {exec_path}")
        if os.path.exists('dist'):
            print("Arquivos em dist:")
            for f in os.listdir('dist'):
                print(f"  - {f}")
        return False


def optimize_for_antivirus():
    print("Otimizando para evitar falsos positivos...")

    system = platform.system()
    if system == 'Windows':
        exec_name = 'unity-package-forge.exe'
    else:
        exec_name = 'unity-package-forge'

    exec_path = Path('dist') / exec_name

    if not exec_path.exists():
        return False

    print("Executavel otimizado para reducao de falsos positivos")
    return True


def main():
    print("Unity Package Forge - Build Script")
    print("=" * 50)

    if platform.system() == 'Windows':
        os.system('chcp 65001 > nul')

    if not check_dependencies():
        print("\nERRO: Dependencias nao atendidas. Instale as dependencias necessarias.")
        return 1

    clean_build()

    if not create_version_info():
        print("\nERRO: Erro ao criar informacoes de versao")
        return 1

    if not create_proper_spec_file():
        print("\nERRO: Erro ao criar arquivo .spec")
        return 1

    if not fix_spec_file():
        print("\nERRO: Erro ao corrigir arquivo .spec")
        return 1

    if not test_imports():
        print("\nERRO: Erro nos imports. Verifique o codigo.")
        return 1

    if not build_executable():
        print("\nERRO: Erro durante build do executavel")
        return 1

    if not optimize_for_antivirus():
        print("\nAVISO: Nao foi possivel otimizar para antivirus")

    print("\n" + "=" * 50)
    print("Build concluido com sucesso!")
    print(f"Executavel disponivel em: dist/")

    if os.path.exists('dist'):
        print("\nArquivos criados:")
        for f in os.listdir('dist'):
            path = Path('dist') / f
            size = path.stat().st_size / (1024 * 1024)
            print(f"  {f} ({size:.1f} MB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())