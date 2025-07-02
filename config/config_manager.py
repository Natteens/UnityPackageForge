import configparser
import os
from utils.crypto_utils import get_crypto_instance
from utils.resource_utils import ensure_config_file_exists, get_config_directory

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config_file_name = config_file
        self.config_file = ensure_config_file_exists(config_file)
        self.config = configparser.ConfigParser()
        self.crypto = get_crypto_instance()
        self.sensitive_keys = {'token'}
        self.auto_save_enabled = True
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config['DEFAULT'] = {
                'last_directory': os.path.expanduser('~'), 
                'author_name': 'Nome Completo',
                'author_email': 'emaildeexemplo@gmail.com', 
                'author_url': 'https://github.com/seuusuario',
                'unity_version': '2021.3', 
                'company_prefix': 'com.exemplo',
            }
            self.config['github'] = {'username': '', 'token': ''}
            self.config['dependencies'] = {}
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f: 
            self.config.write(f)
    
    def get_value(self, section='DEFAULT', key=None, default=None):
        try: 
            value = self.config[section][key]
            # Decrypt sensitive values
            if key in self.sensitive_keys and value:
                value = self.crypto.decrypt(value)
            return value
        except (KeyError, ValueError): 
            return default
    
    def set_value(self, section='DEFAULT', key=None, value=None):
        if section not in self.config: 
            self.config[section] = {}
        
        if value is not None:
            value = str(value)
        
        if key in self.sensitive_keys and value:
            value = self.crypto.encrypt(value)
        
        self.config[section][key] = value or ''
        
        if self.auto_save_enabled:
            self.save_config()

    def get_custom_dependencies(self):
        if 'dependencies' not in self.config:
            self.config['dependencies'] = {}
            self.save_config()

        valid_deps = {}
        for package_id, value in self.config['dependencies'].items():
            if self._is_valid_unity_package_id(package_id):
                valid_deps[package_id] = value

        return valid_deps

    def _is_valid_unity_package_id(self, package_id):
        import re

        pattern = r'^(com\.unity\.|com\.[\w-]+\.|org\.[\w-]+\.)[a-z0-9\-\.]+$'

        if not re.match(pattern, package_id):
            return False

        valid_prefixes = [
            'com.unity.',           # Pacotes oficiais Unity
            'com.microsoft.',       # Microsoft packages (Mixed Reality, etc)
            'com.google.',          # Google packages (Firebase, etc)
            'com.facebook.',        # Facebook packages
            'com.valve.',           # Valve packages (OpenVR, etc)
            'com.oculus.',          # Oculus packages
            'com.htc.',             # HTC packages
            'com.autodesk.',        # Autodesk packages
            'com.adobe.',           # Adobe packages
            'org.nuget.',           # NuGet packages
        ]

        return any(package_id.startswith(prefix) for prefix in valid_prefixes)

    def clean_invalid_dependencies(self):
        if 'dependencies' not in self.config:
            return

        invalid_keys = []
        for package_id in self.config['dependencies']:
            if not self._is_valid_unity_package_id(package_id):
                invalid_keys.append(package_id)

        for key in invalid_keys:
            del self.config['dependencies'][key]

        if invalid_keys:
            self.save_config()
            print(f"Removidas dependências inválidas: {invalid_keys}")

    def add_custom_dependency(self, package_id, version, name=None):
        if 'dependencies' not in self.config:
            self.config['dependencies'] = {}
        if name:
            self.config['dependencies'][package_id] = f"{version}|{name}"
        else:
            self.config['dependencies'][package_id] = version

        self.save_config()
        return True

    def remove_custom_dependency(self, package_id):
        if 'dependencies' in self.config and package_id in self.config['dependencies']:
            del self.config['dependencies'][package_id]
            self.save_config()
            return True
        return False

    def get_dependency_info(self, package_id):
        if 'dependencies' in self.config and package_id in self.config['dependencies']:
            value = self.config['dependencies'][package_id]
            if '|' in value:
                version, name = value.split('|', 1)
                return {"version": version, "name": name}
            else:
                return {"version": value, "name": package_id.split('.')[-1].title()}
        return None

    def set_auto_save(self, enabled):
        self.auto_save_enabled = enabled
    
    def get_decrypted_value(self, section='DEFAULT', key=None, default=None):
        try:
            value = self.config[section][key]
            if key in self.sensitive_keys and value:
                return self.crypto.decrypt(value)
            return value
        except (KeyError, ValueError):
            return default
