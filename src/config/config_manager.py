import configparser
import os


class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config['DEFAULT'] = {
                'last_directory': os.path.expanduser('~'), 
                'author_name': 'Nome Completo',
                'author_email': 'emaildeexemplo@gmail.com', 
                'author_url': 'https://github.com/Natteens',
                'unity_version': '2021.3', 
                'company_prefix': 'com.exemplo',
            }
            self.config['github'] = {'username': '', 'token': ''}
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f: 
            self.config.write(f)
    
    def get_value(self, section='DEFAULT', key=None, default=None):
        try: 
            return self.config[section][key]
        except (KeyError, ValueError): 
            return default
    
    def set_value(self, section='DEFAULT', key=None, value=None):
        if section not in self.config: 
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
