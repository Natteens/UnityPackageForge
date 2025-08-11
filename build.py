#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# Configuração de encoding para Windows
if platform.system() == 'Windows':
    import locale
    try:
        # Força UTF-8 no Windows
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


def safe_print(message):
    """Print seguro que funciona em qualquer terminal"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(clean_message)


def run_command(cmd, cwd=None, timeout=300):
    """Executa comando com melhor tratamento de erros e timeout"""
    try:
        # Configuração especial para Windows
        kwargs = {
            'shell': True,
            'check': True,
            'capture_output': True,
            'text': True,
            'cwd': cwd,
            'encoding': 'utf-8',
            'errors': 'replace',
            'timeout': timeout
        }

        if platform.system() == "Windows":
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(cmd, **kwargs)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Comando expirou após {timeout}s"
    except subprocess.CalledProcessError as e:
        return False, e.stdout or "", e.stderr or str(e)
    except Exception as e:
        return False, "", str(e)


def validate_environment():
    """Valida o ambiente antes de iniciar o build"""
    safe_print("[OK] Validando ambiente de build...")

    # Executa o validador
    validator_path = Path(__file__).parent / "validate_build.py"
    if validator_path.exists():
        safe_print("Executando validacao completa...")
        success, stdout, stderr = run_command(f"python \"{validator_path}\"")
        if not success:
            safe_print("[X] Validacao falhou:")
            if stderr:
                safe_print(stderr)
            return False
        safe_print("[OK] Validacao concluida com sucesso")
    else:
        safe_print("[!] Validador nao encontrado, prosseguindo com validacao basica...")

    return True


def check_dependencies():
    """Verifica dependências com melhor tratamento"""
    safe_print("[OK] Verificando dependencias...")

    python_version = sys.version_info
    if python_version < (3, 7):
        safe_print("[X] ERRO: Python 3.7+ necessario")
        return False
    safe_print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    required_packages = {
        'pyinstaller': '5.0',
        'customtkinter': '5.2.0',
        'requests': '2.25.0',
        'cryptography': '3.0'
    }

    missing_packages = []
    for package, min_version in required_packages.items():
        success, stdout, stderr = run_command(f"python -m pip show {package}")
        if success:
            safe_print(f"[OK] {package}")
        else:
            missing_packages.append(package)
            safe_print(f"[X] {package} - nao encontrado")

    if missing_packages:
        safe_print(f"\n[X] Instale as dependencias faltantes:")
        safe_print(f"pip install {' '.join(missing_packages)}")
        return False

    return True


def clean_build():
    """Limpa builds anteriores com melhor tratamento"""
    safe_print("[OK] Limpando builds anteriores...")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_cleaned = 0

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                safe_print(f"[OK] Removido: {dir_name}")
                files_cleaned += 1
            except Exception as e:
                safe_print(f"[!] Erro ao remover {dir_name}: {e}")

    # Limpa arquivos .pyc recursivamente
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    files_cleaned += 1
                except Exception:
                    pass

    safe_print(f"[OK] {files_cleaned} itens limpos")
    return True


def ensure_version_consistency():
    """Garante consistência de versões entre arquivos"""
    safe_print("[OK] Verificando consistencia de versoes...")

    # Lê versão do version.txt
    version_file = Path("version.txt")
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            version = f.read().strip()
    else:
        version = "1.0.0"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version)
        safe_print(f"[OK] Criado version.txt com versao {version}")

    safe_print(f"[OK] Versao do projeto: {version}")

    # Atualiza package.json se existir
    package_json = Path("package.json")
    if package_json.exists():
        try:
            import json
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('version') != version:
                data['version'] = version
                with open(package_json, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                safe_print(f"[OK] package.json atualizado para versao {version}")
        except Exception as e:
            safe_print(f"[!] Erro ao atualizar package.json: {e}")

    return version


def create_version_info():
    """Cria informações de versão para Windows"""
    if platform.system() != 'Windows':
        return True

    safe_print("📄 Criando informações de versão para Windows...")

    version = ensure_version_consistency()
    version_parts = version.split('.')
    if len(version_parts) < 4:
        version_parts.extend(['0'] * (4 - len(version_parts)))

    version_info = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({', '.join(version_parts)}),
    prodvers=({', '.join(version_parts)}),
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
            StringStruct('FileDescription', 'Unity Package Forge - Gerador profissional de pacotes Unity'),
            StringStruct('FileVersion', '{version}'),
            StringStruct('InternalName', 'unity-package-forge'),
            StringStruct('LegalCopyright', 'Copyright (c) 2025 Nathan da Silva Miranda'),
            StringStruct('OriginalFilename', 'unity-package-forge.exe'),
            StringStruct('ProductName', 'Unity Package Forge'),
            StringStruct('ProductVersion', '{version}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)'''

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)

    safe_print("✅ Arquivo version_info.txt criado")
    return True


def create_optimized_spec_file():
    """Cria arquivo .spec otimizado e corrigido"""
    safe_print("⚙️ Criando arquivo .spec otimizado...")

    # Verifica quais pastas e arquivos existem
    datas = []

    # Verifica pastas do projeto
    folders_to_check = ['ui', 'utils', 'core', 'config']
    for folder in folders_to_check:
        if os.path.exists(folder):
            datas.append(f"('{folder}', '{folder}')")
            safe_print(f"📁 Pasta {folder} será incluída")

    # Verifica arquivos de configuração
    files_to_check = ['config.ini.example', 'version.txt']
    for file in files_to_check:
        if os.path.exists(file):
            datas.append(f"('{file}', '.')")
            safe_print(f"📄 Arquivo {file} será incluído")

    # Inclui ícone se existir
    icon_path = os.path.join('ui', 'icon.ico')
    icon_line = f"icon='{icon_path}'" if os.path.exists(icon_path) else "icon=None"

    # Inclui version_info se for Windows
    version_line = "version='version_info.txt'" if platform.system() == 'Windows' else "version=None"

    datas_str = ",\n        ".join(datas) if datas else ""

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
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
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
        'webbrowser',
        'platform',
        'getpass',
        'ui.ctk_generator_gui',
        'ui.strings',
        'utils.resource_utils',
        'utils.crypto_utils',
        'utils.version_utils',
        'utils.helpers',
        'core.package_generator',
        'core.github_manager',
        'config.config_manager',
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
        'tkinter.test',
        'test',
        'tests',
        'unittest',
        'doctest',
        'pydoc',
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
    {version_line},
    {icon_line},
)'''

    with open('unity_package_forge.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    safe_print("✅ Arquivo .spec criado/atualizado")
    return True


def test_imports():
    """Testa imports com melhor tratamento de erros"""
    safe_print("[OK] Testando imports...")

    try:
        # Adiciona diretório atual ao path
        sys.path.insert(0, '.')

        # Testa import principal
        import main
        safe_print("[OK] main.py")

        # Testa imports de módulos internos
        modules_to_test = [
            ('utils.resource_utils', 'get_resource_path'),
            ('utils.crypto_utils', 'get_crypto_instance'),
            ('utils.version_utils', 'get_current_version'),
            ('utils.helpers', 'open_folder'),
            ('core.package_generator', 'PackageGenerator'),
            ('core.github_manager', 'GitHubManager'),
            ('config.config_manager', 'ConfigManager'),
            ('ui.ctk_generator_gui', 'PackageGeneratorGUI'),
            ('ui.strings', 'RELEASE_WORKFLOW'),
        ]

        for module_name, item_name in modules_to_test:
            try:
                module = __import__(module_name, fromlist=[item_name])
                getattr(module, item_name)
                safe_print(f"[OK] {module_name}")
            except ImportError as e:
                safe_print(f"[!] {module_name}: {e}")
            except AttributeError as e:
                safe_print(f"[!] {module_name}.{item_name}: {e}")

        safe_print("[OK] Imports principais funcionando")
        return True

    except Exception as e:
        safe_print(f"[X] Erro critico nos imports: {e}")
        return False


def build_executable():
    """Constrói o executável com melhor tratamento"""
    safe_print("[OK] Construindo executavel...")

    if not os.path.exists('unity_package_forge.spec'):
        safe_print("[X] Arquivo unity_package_forge.spec nao encontrado!")
        return False

    # Configura ambiente
    env = os.environ.copy()
    if platform.system() == 'Windows':
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = '1'

    # Comando de build com opções otimizadas
    cmd = [
        "pyinstaller",
        "unity_package_forge.spec",
        "--clean",
        "--noconfirm",
        "--log-level", "WARN"
    ]

    cmd_str = " ".join(cmd)
    safe_print(f"Executando: {cmd_str}")

    success, stdout, stderr = run_command(cmd_str, timeout=600)  # 10 minutos

    if not success:
        safe_print(f"[X] Erro durante build:")
        if stderr:
            safe_print(stderr)
        if stdout:
            safe_print("Stdout:", stdout)
        return False

    # Verifica se executável foi criado
    system = platform.system()
    exec_name = 'unity-package-forge.exe' if system == 'Windows' else 'unity-package-forge'
    exec_path = Path('dist') / exec_name

    if exec_path.exists():
        size = exec_path.stat().st_size / (1024 * 1024)
        safe_print(f"[OK] Executavel criado: {exec_path}")
        safe_print(f"[OK] Tamanho: {size:.1f} MB")

        # Define permissões no Unix
        if system != 'Windows':
            try:
                os.chmod(exec_path, 0o755)
                safe_print("[OK] Permissoes de execucao definidas")
            except Exception as e:
                safe_print(f"[!] Erro ao definir permissoes: {e}")

        return True
    else:
        safe_print(f"[X] Executavel nao encontrado em: {exec_path}")
        if os.path.exists('dist'):
            safe_print("[OK] Arquivos em dist:")
            for f in os.listdir('dist'):
                safe_print(f"  - {f}")
        return False


def create_portable_package():
    """Cria pacote portável com todos os arquivos necessários"""
    safe_print("📦 Criando pacote portável...")

    if not os.path.exists('dist'):
        safe_print("❌ Pasta dist não encontrada")
        return False

    # Cria pasta de distribuição
    package_dir = Path('dist') / 'unity-package-forge-portable'
    package_dir.mkdir(exist_ok=True)

    # Copia executável
    system = platform.system()
    exec_name = 'unity-package-forge.exe' if system == 'Windows' else 'unity-package-forge'
    exec_src = Path('dist') / exec_name

    if exec_src.exists():
        shutil.copy2(exec_src, package_dir / exec_name)
        safe_print(f"✅ Executável copiado")

    # Copia arquivos essenciais
    essential_files = ['README.md', 'LICENSE.md', 'CHANGELOG.md']
    for file_name in essential_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, package_dir / file_name)
            safe_print(f"✅ {file_name} copiado")

    # Cria arquivo de exemplo de configuração
    config_example = package_dir / 'config.ini.example'
    if not config_example.exists() and os.path.exists('config.ini.example'):
        shutil.copy2('config.ini.example', config_example)
        safe_print("✅ config.ini.example copiado")

    safe_print(f"📦 Pacote portável criado em: {package_dir}")
    return True


def post_build_validation():
    """Valida o build após conclusão"""
    safe_print("🔍 Validando build...")

    system = platform.system()
    exec_name = 'unity-package-forge.exe' if system == 'Windows' else 'unity-package-forge'
    exec_path = Path('dist') / exec_name

    if not exec_path.exists():
        safe_print("❌ Executável não encontrado")
        return False

    # Testa se é executável
    if system != 'Windows':
        if not os.access(exec_path, os.X_OK):
            safe_print("❌ Executável sem permissões de execução")
            return False

    safe_print("✅ Build validado com sucesso")
    return True


def main():
    """Função principal do build"""
    safe_print("Unity Package Forge - Build Script Melhorado")
    safe_print("=" * 60)

    # Configura codificação no Windows
    if platform.system() == 'Windows':
        try:
            os.system('chcp 65001 > nul')
        except:
            pass

    # Sequência de build
    build_steps = [
        ("Validacao do ambiente", validate_environment),
        ("Verificacao de dependencias", check_dependencies),
        ("Limpeza de builds anteriores", clean_build),
        ("Garantia de consistencia de versoes", ensure_version_consistency),
        ("Criacao de informacoes de versao", create_version_info),
        ("Criacao de arquivo .spec otimizado", create_optimized_spec_file),
        ("Teste de imports", test_imports),
        ("Build do executavel", build_executable),
        ("Validacao pos-build", post_build_validation),
        ("Criacao de pacote portavel", create_portable_package)
    ]

    failed_steps = []

    for step_name, step_function in build_steps:
        safe_print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            if not step_function():
                failed_steps.append(step_name)
                safe_print(f"[X] Falha em: {step_name}")

                # Para em caso de erro crítico
                if step_name in ["Verificacao de dependencias", "Build do executavel"]:
                    safe_print(f"\n[X] Build interrompido devido a erro critico em: {step_name}")
                    return 1
            else:
                safe_print(f"[OK] Concluido: {step_name}")
        except Exception as e:
            safe_print(f"[X] Erro em {step_name}: {e}")
            failed_steps.append(step_name)

    # Resultado final
    safe_print(f"\n{'='*60}")
    if failed_steps:
        safe_print(f"[!] Build concluido com {len(failed_steps)} problemas:")
        for step in failed_steps:
            safe_print(f"  - {step}")

        if len(failed_steps) <= 2:  # Tolera até 2 problemas menores
            safe_print("\n[OK] Build utilizavel criado (com avisos)")
            return 0
        else:
            safe_print("\n[X] Build falhou devido a muitos problemas")
            return 1
    else:
        safe_print("[OK] Build concluido com sucesso!")

        if os.path.exists('dist'):
            safe_print("\n[OK] Arquivos criados:")
            for f in os.listdir('dist'):
                if os.path.isfile(os.path.join('dist', f)):
                    path = Path('dist') / f
                    size = path.stat().st_size / (1024 * 1024)
                    safe_print(f"  [OK] {f} ({size:.1f} MB)")
                else:
                    safe_print(f"  [OK] {f}/")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        safe_print("\n⏹️ Build interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n💥 Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
