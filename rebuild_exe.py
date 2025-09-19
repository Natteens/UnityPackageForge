import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def main():
    print("\n===== Unity Package Forge - Reconstrução do Executável =====")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Verificar se o PyInstaller está instalado
    try:
        import PyInstaller
        print(f"PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("\n❌ PyInstaller não está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller instalado com sucesso.")
    
    # Verificar se o Pillow está instalado
    try:
        import PIL
        print(f"Pillow: {PIL.__version__}")
    except ImportError:
        print("\n❌ Pillow não está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True)
        print("✅ Pillow instalado com sucesso.")
    
    # Verificar se o arquivo .spec existe
    spec_file = "unity_package_forge.spec"
    if not os.path.exists(spec_file):
        print(f"\n❌ Arquivo {spec_file} não encontrado!")
        return 1
    
    # Limpar diretórios de build anteriores
    print("\n🧹 Limpando diretórios de build anteriores...")
    for dir_to_clean in ["build", "dist"]:
        if os.path.exists(dir_to_clean):
            shutil.rmtree(dir_to_clean)
            print(f"  ✓ Diretório {dir_to_clean} removido")
    
    # Executar o PyInstaller
    print("\n🚀 Executando PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--clean", "--noconfirm", "--log-level=INFO"],
        capture_output=True,
        text=True
    )
    
    # Verificar se o PyInstaller foi executado com sucesso
    if result.returncode != 0:
        print(f"\n❌ Erro ao executar PyInstaller:\n{result.stderr}")
        return 1
    
    # Verificar se o executável foi criado
    exe_name = "unity-package-forge.exe" if platform.system() == "Windows" else "unity-package-forge"
    exe_path = Path("dist") / exe_name
    
    if not exe_path.exists():
        print(f"\n❌ Executável {exe_name} não foi criado!")
        print("Saída do PyInstaller:")
        print(result.stdout)
        print("Erros do PyInstaller:")
        print(result.stderr)
        return 1
    
    # Verificar o tamanho do executável
    exe_size = exe_path.stat().st_size / (1024 * 1024)  # Tamanho em MB
    print(f"\n✅ Executável criado com sucesso: {exe_path}")
    print(f"   Tamanho: {exe_size:.2f} MB")
    
    # Verificar se o executável contém a DLL do Python (apenas no Windows)
    if platform.system() == "Windows":
        try:
            import pefile
            pe = pefile.PE(str(exe_path))
            dlls = [imp.dll.decode() for entry in pe.DIRECTORY_ENTRY_IMPORT for imp in entry.imports]
            python_dlls = [dll for dll in dlls if "python" in dll.lower()]
            
            if python_dlls:
                print(f"\n✅ DLLs do Python incluídas no executável: {', '.join(python_dlls)}")
            else:
                print("\n⚠️ Nenhuma DLL do Python encontrada no executável.")
                print("   Isso pode indicar que o executável não está empacotando corretamente as dependências.")
        except ImportError:
            print("\n⚠️ Módulo pefile não está instalado. Não foi possível verificar as DLLs incluídas.")
            print("   Para instalar: pip install pefile")
        except Exception as e:
            print(f"\n⚠️ Não foi possível analisar o executável: {e}")
    
    print("\n✨ Processo de reconstrução concluído!")
    print("   Para testar o executável, execute:")
    if platform.system() == "Windows":
        print(f"   > {exe_path}")
    else:
        print(f"   $ chmod +x {exe_path} && {exe_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())