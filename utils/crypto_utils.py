import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SimpleCrypto:
    """Simple encryption utility for sensitive configuration data"""
    
    def __init__(self, machine_key=None):
        """Initialize with a machine-specific key or generate one"""
        if machine_key is None:
            # Use machine-specific data as salt
            machine_key = self._get_machine_key()
        
        self.key = self._derive_key(machine_key)
        self.cipher = Fernet(self.key)
    
    def _get_machine_key(self):
        """Generate a machine-specific key based on system info"""
        try:
            # Try to use machine-specific information
            import platform
            import getpass
            
            machine_info = f"{platform.node()}-{platform.system()}-{getpass.getuser()}"
            return machine_info.encode('utf-8')
        except:
            # Fallback to a default key if system info is not available
            return b"unity-package-forge-default-key"
    
    def _derive_key(self, password):
        """Derive encryption key from password"""
        salt = b"unity_package_forge_salt"  # Static salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, plaintext):
        """Encrypt a string and return base64 encoded result"""
        if not plaintext:
            return ""
        
        try:
            encrypted_data = self.cipher.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception:
            # If encryption fails, return original text (fallback)
            return plaintext
    
    def decrypt(self, encrypted_data):
        """Decrypt base64 encoded data and return original string"""
        if not encrypted_data:
            return ""
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception:
            # If decryption fails, assume it's plain text (backward compatibility)
            return encrypted_data
    
    def is_encrypted(self, data):
        """Check if data appears to be encrypted (base64 encoded and decryptable)"""
        if not data:
            return False
        
        try:
            # Try to decode as base64
            decoded = base64.urlsafe_b64decode(data.encode('utf-8'))
            # Try to decrypt
            self.cipher.decrypt(decoded)
            return True
        except Exception:
            return False


def get_crypto_instance():
    """Get a singleton crypto instance"""
    if not hasattr(get_crypto_instance, '_instance'):
        get_crypto_instance._instance = SimpleCrypto()
    return get_crypto_instance._instance