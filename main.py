import sys
import os
import subprocess
import customtkinter as ctk
from ui.ctk_generator_gui import PackageGeneratorGUI
from utils.version_utils import get_current_version
from ui.strings import (
    APP_GEOMETRY, APP_MIN_SIZE, APP_APPEARANCE_MODE, APP_COLOR_THEME,
    ERROR_APP_INITIALIZATION, ERROR_ICON_LOAD, PROMPT_PRESS_ENTER
)

def install_dependencies():
    """Instala dependências necessárias se não estiverem disponíveis"""
    required_packages = ['requests', 'customtkinter']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Instalando dependências: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)

def start_gui():
    """Inicializa a interface gráfica com configurações otimizadas"""
    ctk.set_appearance_mode(APP_APPEARANCE_MODE)
    ctk.set_default_color_theme(APP_COLOR_THEME)

    root = ctk.CTk()
    root.title(f"Unity Package Forge v{get_current_version()}")

    # Forçar o tamanho da janela primeiro
    root.geometry(APP_GEOMETRY)
    root.minsize(APP_MIN_SIZE[0], APP_MIN_SIZE[1])

    # Retirar da tela primeiro para evitar flicker
    root.withdraw()

    try:
        icon_path = os.path.join(os.path.dirname(__file__), "ui", "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        print(ERROR_ICON_LOAD.format(error=str(e)))

    # Criar a interface
    app = PackageGeneratorGUI(root)

    # Centralizar janela após tudo estar criado
    def center_and_show():
        root.update_idletasks()

        # Obter dimensões reais da janela
        width = APP_MIN_SIZE[0]  # Usar o tamanho definido
        height = APP_MIN_SIZE[1]

        # Obter dimensões da tela
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calcular posição central
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Garantir que não saia da tela
        x = max(0, x)
        y = max(0, y)

        # Aplicar geometria centralizada
        root.geometry(f"{width}x{height}+{x}+{y}")

        # Mostrar a janela centralizada
        root.deiconify()

    # Centralizar após 50ms
    root.after(50, center_and_show)

    root.mainloop()

if __name__ == "__main__":
    try:
        install_dependencies()
        start_gui()
    except Exception as e:
        print(ERROR_APP_INITIALIZATION.format(error=str(e)))
        input(PROMPT_PRESS_ENTER)
