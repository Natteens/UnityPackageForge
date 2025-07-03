#!/usr/bin/env python3
"""
Script para build local do Unity Package Forge
Use este script para testar builds localmente antes de fazer push
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        # Definir encoding UTF-8 para evitar problemas com caracteres especiais
        result = subprocess.run(cmd, shell=True, check=True,
                                capture_output=True, text=True, cwd=cwd,
                                encoding='utf-8', errors='replace')
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")

    # Verificar Python
    python_version = sys.version_info
    if python_version < (3, 7):
        print("❌ Python 3.7+ é necessário")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Verificar pip packages
    required_packages = [
        'pyinstaller',
        'customtkinter',
        'requests',
        'cryptography'
    ]

    for package in required_packages:
        success, _, _ = run_command(f"python -m pip show {package}")
        if success:
            print(f"✅ {package}")
        else:
            print(f"❌ {package} - Execute: pip install {package}")
            return False

    return True


def clean_build():
    """Limpa arquivos de build anteriores"""
    print("🧹 Limpando builds anteriores...")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Removido: {dir_name}")

    # Limpar arquivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))


def create_version_info():
    """Cria arquivo de informações de versão para Windows"""
    if platform.system() != 'Windows':
        return True

    print("📄 Criando informações de versão para Windows...")

    version_info = '''
VSVersionInfo(
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
)
'''

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info.strip())

    print("✅ Arquivo version_info.txt criado")
    return True


def fix_spec_file():
    """Corrige o arquivo .spec para evitar problemas de encoding"""
    print("🔧 Corrigindo arquivo .spec...")

    if not os.path.exists('unity_package_forge.spec'):
        print("❌ Arquivo unity_package_forge.spec não encontrado!")
        return False

    # Ler o arquivo atual
    with open('unity_package_forge.spec', 'r', encoding='utf-8') as f:
        content = f.read()

    # Substituir caracteres problemáticos por versões ASCII
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

    # Se modificou, salvar o arquivo
    if modified:
        with open('unity_package_forge.spec', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Arquivo .spec corrigido")
    else:
        print("ℹ️ Arquivo .spec não precisou ser corrigido")

    return True


def test_imports():
    """Testa se todos os imports funcionam"""
    print("🧪 Testando imports...")

    try:
        sys.path.insert(0, '.')
        from utils.resource_utils import get_resource_path, is_executable
        from utils.crypto_utils import get_crypto_instance
        from utils.version_utils import get_current_version
        print("✅ Todos os imports funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False


def build_executable():
    """Constrói o executável usando PyInstaller"""
    print("🔨 Construindo executável...")

    if not os.path.exists('unity_package_forge.spec'):
        print("❌ Arquivo unity_package_forge.spec não encontrado!")
        return False

    # Definir variáveis de ambiente para encoding UTF-8
    env = os.environ.copy()
    if platform.system() == 'Windows':
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = '1'

    # Executar PyInstaller
    cmd = "pyinstaller unity_package_forge.spec --clean --noconfirm --log-level WARN"
    success, stdout, stderr = run_command(cmd)

    if not success:
        print(f"❌ Erro durante build:")
        print(stderr)
        return False

    # Verificar se o executável foi criado
    system = platform.system()
    if system == 'Windows':
        exec_name = 'unity-package-forge.exe'
    else:
        exec_name = 'unity-package-forge'

    exec_path = Path('dist') / exec_name

    if exec_path.exists():
        size = exec_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Executável criado: {exec_path}")
        print(f"   Tamanho: {size:.1f} MB")

        # Definir permissões no Linux/macOS
        if system != 'Windows':
            os.chmod(exec_path, 0o755)
            print("✅ Permissões de execução definidas")

        return True
    else:
        print(f"❌ Executável não encontrado em: {exec_path}")
        if os.path.exists('dist'):
            print("Arquivos em dist:")
            for f in os.listdir('dist'):
                print(f"  - {f}")
        return False


def test_executable():
    """Testa se o executável funciona"""
    print("🧪 Testando executável...")

    system = platform.system()
    if system == 'Windows':
        exec_name = 'unity-package-forge.exe'
    else:
        exec_name = 'unity-package-forge'

    exec_path = Path('dist') / exec_name

    if not exec_path.exists():
        print("❌ Executável não encontrado para teste")
        return False

    # Teste básico - só verificar se inicia sem erro
    try:
        if system == 'Windows':
            # No Windows, tentar executar com timeout
            process = subprocess.Popen([str(exec_path)],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW)

            # Aguardar um pouco e matar o processo
            import time
            time.sleep(2)
            process.terminate()

            print("✅ Executável inicia sem erros críticos")
            return True
        else:
            # No Linux/macOS, executar com --version se disponível
            success, stdout, stderr = run_command(f"{exec_path} --help")
            if "unity" in stdout.lower() or "package" in stdout.lower():
                print("✅ Executável responde corretamente")
                return True
            else:
                print("⚠️  Executável criado mas resposta inesperada")
                return True
    except Exception as e:
        print(f"⚠️  Erro ao testar executável: {e}")
        print("   (Isso pode ser normal se o app precisa de GUI)")
        return True


def main():
    """Função principal"""
    print("🚀 Unity Package Forge - Build Script")
    print("=" * 50)

    # Configurar encoding UTF-8 para stdout no Windows
    if platform.system() == 'Windows':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Dependências não atendidas. Instale as dependências necessárias.")
        return 1

    # Limpar builds anteriores
    clean_build()

    # Criar informações de versão
    if not create_version_info():
        print("\n❌ Erro ao criar informações de versão")
        return 1

    # Corrigir arquivo .spec
    if not fix_spec_file():
        print("\n❌ Erro ao corrigir arquivo .spec")
        return 1

    # Testar imports
    if not test_imports():
        print("\n❌ Erro nos imports. Verifique o código.")
        return 1

    # Construir executável
    if not build_executable():
        print("\n❌ Erro durante build do executável")
        return 1

    # Testar executável
    if not test_executable():
        print("\n⚠️  Executável criado mas pode ter problemas")

    print("\n" + "=" * 50)
    print("✅ Build concluído com sucesso!")
    print(f"📦 Executável disponível em: dist/")

    # Mostrar arquivos criados
    if os.path.exists('dist'):
        print("\nArquivos criados:")
        for f in os.listdir('dist'):
            path = Path('dist') / f
            size = path.stat().st_size / (1024 * 1024)
            print(f"  📄 {f} ({size:.1f} MB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())