import os
import sys
import subprocess
import webbrowser

def open_folder(path):
    if os.path.exists(path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            # Hide subprocess window on Windows (doesn't apply to macOS but keeping consistent structure)
            kwargs = {}
            if sys.platform == "win32":
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            subprocess.run(['open', path], **kwargs)
        else:  # Linux
            # Hide subprocess window on Windows (doesn't apply to Linux but keeping consistent structure)
            kwargs = {}
            if sys.platform == "win32":
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            subprocess.run(['xdg-open', path], **kwargs)
    else:
        print(f"Path does not exist: {path}")


def validate_package_name(name):
    # Verificar se o nome é vazio
    if not name:
        return False
    
    # Deve começar com uma letra
    if not name[0].isalpha():
        return False
    
    # Verificar caracteres permitidos
    for char in name:
        if not (char.isalnum() or char == '_' or char == '.'):
            return False
    
    # Verificar se não há pontos consecutivos
    if '..' in name:
        return False
    
    # Verificar se não termina com ponto
    if name.endswith('.'):
        return False
    
    return True


def validate_version(version):
    parts = version.split('.')
    if len(parts) < 2 or len(parts) > 3:
        return False
    
    try:
        for part in parts:
            int(part)
        return True
    except ValueError:
        return False


def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def check_dependency(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def install_dependency(module_name):
    try:
        # Hide CMD window on Windows
        kwargs = {}
        if sys.platform == "win32":
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name], **kwargs)
        return True
    except subprocess.CalledProcessError:
        return False
