import sys
import os
import subprocess
import customtkinter as ctk
from ui.ctk_generator_gui import PackageGeneratorGUI


def start_gui():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()

    try:
        icon_path = os.path.join(os.path.dirname(__file__), "ui", "icon.ico")
        root.iconbitmap(icon_path)
    except Exception:
        pass

    app = PackageGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "customtkinter"])

    start_gui()