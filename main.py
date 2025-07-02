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
    required_packages = ['requests', 'customtkinter']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Instalando dependências: {', '.join(missing_packages)}")
        
        import sys
        kwargs = {}
        if sys.platform == "win32":
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages, **kwargs)

def start_gui():
    ctk.set_appearance_mode(APP_APPEARANCE_MODE)
    ctk.set_default_color_theme(APP_COLOR_THEME)

    root = ctk.CTk()
    root.title(f"Unity Package Forge v{get_current_version()}")

    root.geometry(APP_GEOMETRY)
    root.minsize(APP_MIN_SIZE[0], APP_MIN_SIZE[1])

    root.withdraw()

    try:
        icon_path = os.path.join(os.path.dirname(__file__), "ui", "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        print(ERROR_ICON_LOAD.format(error=str(e)))

    app = PackageGeneratorGUI(root)

    def center_and_show():
        root.update_idletasks()

        width = APP_MIN_SIZE[0]
        height = APP_MIN_SIZE[1]

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        x = max(0, x)
        y = max(0, y)

        root.geometry(f"{width}x{height}+{x}+{y}")

        root.deiconify()

    root.after(50, center_and_show)

    root.mainloop()

if __name__ == "__main__":
    try:
        install_dependencies()
        start_gui()
    except Exception as e:
        print(ERROR_APP_INITIALIZATION.format(error=str(e)))
        input(PROMPT_PRESS_ENTER)
