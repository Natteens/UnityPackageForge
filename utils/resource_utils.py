"""
Resource utilities for handling file paths in both development and executable environments.
"""
import os
import sys


def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_config_directory():
    """
    Get the appropriate directory for configuration files
    """
    if getattr(sys, 'frozen', False):
        # Running as executable
        config_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.dirname(config_dir)  # Go up one level from utils
    
    return config_dir


def ensure_config_file_exists(config_file_name):
    """
    Ensure config file exists in the appropriate directory
    """
    config_dir = get_config_directory()
    config_path = os.path.join(config_dir, config_file_name)
    
    if not os.path.exists(config_path):
        # Try to find the example file
        example_path = os.path.join(config_dir, f"{config_file_name}.example")
        if os.path.exists(example_path):
            # Copy example to actual config
            import shutil
            shutil.copy2(example_path, config_path)
    
    return config_path


def is_executable():
    """
    Check if running as executable
    """
    return getattr(sys, 'frozen', False)


def get_app_data_directory():
    """
    Get appropriate directory for application data based on OS
    """
    if is_executable():
        # For executables, use the directory where the executable is located
        return os.path.dirname(sys.executable)
    else:
        # For development, use the project directory
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))