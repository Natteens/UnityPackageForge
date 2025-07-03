import os
import sys
from pathlib import Path

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_config_directory():
    if getattr(sys, 'frozen', False):
        config_dir = os.path.dirname(sys.executable)
    else:
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.dirname(config_dir)
    
    return config_dir


def ensure_config_file_exists(config_file='config.ini'):
    config_path = Path(get_resource_path(config_file))

    if not config_path.exists():
        example_path = Path(get_resource_path('config.ini.example'))
        safe_path = Path(get_resource_path('config.ini.safe'))

        if safe_path.exists():
            with open(safe_path, 'r') as src, open(config_path, 'w') as dest:
                dest.write(src.read())
        elif example_path.exists():
            with open(example_path, 'r') as src, open(config_path, 'w') as dest:
                dest.write(src.read())
        else:
            config_path.touch()

    return str(config_path)

def is_executable():
    return getattr(sys, 'frozen', False)


def get_app_data_directory():
    if is_executable():
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))