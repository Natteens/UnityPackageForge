import os
import sys
import platform
import subprocess
from pathlib import Path
import shutil

def main():
    print("\n===== Unity Package Forge - Diagnóstico do Executável =====")
    print(f"Sistema: {platform.system()} {platform.release()}")
    
    # Verificar o executável
    exe_name = "unity-package-forge-windows.exe" if platform.system() == "Windows" else "unity-package-forge"
    exe_path = None
    
    # Locais possíveis para o executável
    possible_locations = [
        Path(os.getcwd()) / exe_name,
        Path(os.getcwd()) / "dist" / exe_name,
        Path(os.getcwd()).parent / exe_name,
        Path(os.environ.get("USERPROFILE", "")) / "Documents" / "PackageForge" / exe_name if platform.system() == "Windows" else None,
        Path(os.environ.get("HOME", "")) / "Documents" / "PackageForge" / exe_name if platform.system() != "Windows" else None
    ]
    
    # Filtrar locais None
    possible_locations = [loc for loc in possible_locations if loc is not None]
    
    # Verificar cada local
    for loc in possible_locations:
        if loc.exists():
            exe_path = loc
            break
    
    if exe_path is None:
        print(f"\n❌ Executável {exe_name} não encontrado em nenhum local comum.")
        print("Locais verificados:")
        for loc in possible_locations:
            print(f"  - {loc}")
        return 1
    
    print(f"\n✅ Executável encontrado: {exe_path}")
    print(f"   Tamanho: {exe_path.stat().st_size / (1024 * 1024):.2f} MB")
    
    # Verificar a estrutura do executável (apenas no Windows)
    if platform.system() == "Windows":
        try:
            import pefile
            pe = pefile.PE(str(exe_path))
            
            # Verificar se é um executável PyInstaller
            is_pyinstaller = False
            for section in pe.sections:
                if section.Name.startswith(b".pyi"):
                    is_pyinstaller = True
                    break
            
            if is_pyinstaller:
                print("\n✅ Executável criado com PyInstaller")
            else:
                print("\n⚠️ Não parece ser um executável PyInstaller")
            
            # Verificar DLLs importadas
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                print("\nDLLs importadas:")
                python_dlls = []
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = entry.dll.decode()
                    if "python" in dll_name.lower():
                        python_dlls.append(dll_name)
                        print(f"  - {dll_name} (Python)")
                    else:
                        print(f"  - {dll_name}")
                
                if python_dlls:
                    print(f"\n✅ Encontradas {len(python_dlls)} DLLs do Python")
                else:
                    print("\n⚠️ Nenhuma DLL do Python encontrada nas importações")
            else:
                print("\n⚠️ Não foi possível analisar as importações do executável")
        except ImportError:
            print("\n⚠️ Módulo pefile não está instalado. Instalando...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pefile"], check=True)
            print("Módulo pefile instalado. Execute este script novamente.")
            return 0
        except Exception as e:
            print(f"\n⚠️ Erro ao analisar o executável: {e}")
    
    # Verificar diretório _internal
    internal_dir = exe_path.parent / "_internal"
    if internal_dir.exists() and internal_dir.is_dir():
        print(f"\n✅ Diretório _internal encontrado: {internal_dir}")
        
        # Verificar python310.dll
        python_dll = internal_dir / "python310.dll"
        if python_dll.exists():
            print(f"✅ Arquivo python310.dll encontrado: {python_dll}")
            print(f"   Tamanho: {python_dll.stat().st_size / (1024 * 1024):.2f} MB")
        else:
            print(f"❌ Arquivo python310.dll NÃO encontrado em {internal_dir}")
            
            # Listar arquivos no diretório _internal
            print("\nArquivos no diretório _internal:")
            for file in internal_dir.glob("*"):
                if file.is_file():
                    print(f"  - {file.name} ({file.stat().st_size / 1024:.2f} KB)")
    else:
        print(f"\n❌ Diretório _internal NÃO encontrado em {exe_path.parent}")
        
        # Listar diretórios na pasta do executável
        print("\nDiretórios na pasta do executável:")
        for item in exe_path.parent.glob("*"):
            if item.is_dir():
                print(f"  - {item.name}/")
    
    # Verificar permissões do executável
    if platform.system() != "Windows":
        try:
            import stat
            mode = os.stat(exe_path).st_mode
            is_executable = bool(mode & stat.S_IXUSR)
            if is_executable:
                print(f"\n✅ O arquivo {exe_path.name} tem permissão de execução")
            else:
                print(f"\n❌ O arquivo {exe_path.name} NÃO tem permissão de execução")
                print("   Executando: chmod +x {exe_path}")
                os.chmod(exe_path, mode | stat.S_IXUSR)
                print("   Permissão de execução adicionada")
        except Exception as e:
            print(f"\n⚠️ Erro ao verificar permissões: {e}")
    
    print("\n✨ Diagnóstico concluído!")
    print("\nPara reconstruir o executável com todas as dependências embutidas, execute:")
    print(f"   > {sys.executable} rebuild_exe.py")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Erro não tratado: {e}")
        sys.exit(1)