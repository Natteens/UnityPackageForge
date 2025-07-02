import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SimpleCrypto:

    def __init__(self, machine_key=None):
        if machine_key is None:
            machine_key = self._get_machine_key()
        
        self.key = self._derive_key(machine_key)
        self.cipher = Fernet(self.key)
    
    def _get_machine_key(self):
        try:
            import platform
            import getpass
            
            machine_info = f"{platform.node()}-{platform.system()}-{getpass.getuser()}"
            return machine_info.encode('utf-8')
        except:
            return b"unity-package-forge-default-key"
    
    def _derive_key(self, password):
        salt = b"unity_package_forge_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, plaintext):
        if not plaintext:
            return ""
        
        try:
            encrypted_data = self.cipher.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception:
            return plaintext
    
    def decrypt(self, encrypted_data):
        if not encrypted_data:
            return ""
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception:
            return encrypted_data
    
    def is_encrypted(self, data):
        if not data:
            return False
        
        try:
            decoded = base64.urlsafe_b64decode(data.encode('utf-8'))
            self.cipher.decrypt(decoded)
            return True
        except Exception:
            return False


def get_crypto_instance():
    if not hasattr(get_crypto_instance, '_instance'):
        get_crypto_instance._instance = SimpleCrypto()
    return get_crypto_instance._instance