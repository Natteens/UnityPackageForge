import sys
import os
import logging
import customtkinter as ctk
from ui.ctk_generator_gui import PackageGeneratorGUI
from utils.version_utils import get_current_version
from utils.resource_utils import get_resource_path, is_executable
from ui.strings import (
    APP_GEOMETRY, APP_MIN_SIZE, APP_APPEARANCE_MODE, APP_COLOR_THEME,
    ERROR_APP_INITIALIZATION, ERROR_ICON_LOAD, PROMPT_PRESS_ENTER
)

def setup_logging():
    if is_executable():
        log_dir = os.path.dirname(sys.executable)
        log_file = os.path.join(log_dir, 'unity_package_forge.log')
    else:
        log_file = 'unity_package_forge.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def check_dependencies():
    missing_deps = []
    try:
        import requests
    except ImportError:
        missing_deps.append('requests')
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append('customtkinter')
    
    try:
        import cryptography
    except ImportError:
        missing_deps.append('cryptography')
    
    if missing_deps:
        error_msg = f"Dependências críticas não encontradas: {', '.join(missing_deps)}"
        if is_executable():
            error_msg += "\n\nEste executável pode estar corrompido. Faça o download novamente."
        else:
            error_msg += f"\n\nInstale com: pip install {' '.join(missing_deps)}"
        raise ImportError(error_msg)
    
    return True

def start_gui():
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Unity Package Forge v{get_current_version()}")
    logger.info(f"Running as executable: {is_executable()}")
    
    ctk.set_appearance_mode(APP_APPEARANCE_MODE)
    ctk.set_default_color_theme(APP_COLOR_THEME)

    root = ctk.CTk()
    root.title(f"Unity Package Forge v{get_current_version()}")

    root.geometry(APP_GEOMETRY)
    root.minsize(APP_MIN_SIZE[0], APP_MIN_SIZE[1])

    root.withdraw()

    try:
        icon_path = get_resource_path(os.path.join("ui", "icon.ico"))
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
            logger.info(f"Icon loaded from: {icon_path}")
        else:
            logger.warning(f"Icon not found at: {icon_path}")
    except Exception as e:
        logger.error(ERROR_ICON_LOAD.format(error=str(e)))
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

    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error during GUI execution: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    logger = None
    try:
        logger = setup_logging()
        logger.info("Unity Package Forge starting...")
        
        check_dependencies()
        logger.info("All dependencies verified")
        
        start_gui()
        
    except ImportError as e:
        error_msg = f"Erro de dependências: {str(e)}"
        print(error_msg)
        if logger:
            logger.error(error_msg)
        input(PROMPT_PRESS_ENTER)
        sys.exit(1)
        
    except Exception as e:
        error_msg = ERROR_APP_INITIALIZATION.format(error=str(e))
        print(error_msg)
        if logger:
            logger.error(error_msg, exc_info=True)
        input(PROMPT_PRESS_ENTER)
        sys.exit(1)
