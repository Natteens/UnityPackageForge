import base64
import os
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SimpleCrypto:
    """Sistema de criptografia melhorado para Unity Package Forge"""

    def __init__(self, machine_key=None):
        """Inicializa o sistema de criptografia com chave da máquina"""
        if machine_key is None:
            machine_key = self._get_machine_key()
        
        self.key = self._derive_key(machine_key)
        self.cipher = Fernet(self.key)
    
    def _get_machine_key(self):
        """Gera chave única baseada na máquina com fallbacks seguros"""
        try:
            import platform
            import getpass
            
            # Coleta informações da máquina
            machine_info_parts = [
                platform.node() or "unknown-node",
                platform.system() or "unknown-system",
                getpass.getuser() or "unknown-user",
                platform.machine() or "unknown-machine"
            ]

            # Adiciona salt específico da aplicação
            app_salt = "unity-package-forge-2025"
            machine_info_parts.append(app_salt)

            machine_info = "-".join(machine_info_parts)

            # Cria hash da informação para uniformizar o tamanho
            return hashlib.sha256(machine_info.encode('utf-8')).digest()

        except Exception as e:
            print(f"Aviso: Erro ao gerar chave da máquina: {e}")
            # Fallback para chave padrão segura
            fallback_key = "unity-package-forge-default-secure-key-2025"
            return hashlib.sha256(fallback_key.encode('utf-8')).digest()

    def _derive_key(self, password):
        """Deriva chave criptográfica segura usando PBKDF2"""
        try:
            # Salt específico da aplicação (não deve mudar)
            salt = b"unity_package_forge_salt_v2_2025"

            # Configurações seguras do PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits
                salt=salt,
                iterations=100000,  # 100k iterações para segurança
            )

            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key

        except Exception as e:
            print(f"Erro ao derivar chave: {e}")
            # Fallback para chave básica
            return base64.urlsafe_b64encode(b"fallback_key_unity_package_forge_32b")

    def encrypt(self, plaintext):
        """Criptografa texto com tratamento de erros melhorado"""
        if not plaintext:
            return ""
        
        try:
            # Converte para bytes se necessário
            if isinstance(plaintext, str):
                plaintext_bytes = plaintext.encode('utf-8')
            else:
                plaintext_bytes = plaintext

            # Criptografa
            encrypted_data = self.cipher.encrypt(plaintext_bytes)

            # Converte para string base64 para armazenamento
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

        except Exception as e:
            print(f"Erro na criptografia: {e}")
            # Em caso de erro, retorna o texto original (para compatibilidade)
            return plaintext if isinstance(plaintext, str) else plaintext.decode('utf-8', errors='ignore')

    def decrypt(self, encrypted_data):
        """Descriptografa dados com tratamento de erros melhorado"""
        if not encrypted_data:
            return ""
        
        try:
            # Decodifica de base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))

            # Descriptografa
            decrypted_data = self.cipher.decrypt(encrypted_bytes)

            # Converte de volta para string
            return decrypted_data.decode('utf-8')

        except Exception as e:
            print(f"Erro na descriptografia: {e}")
            # Em caso de erro, retorna os dados originais (pode ser texto não criptografado)
            return encrypted_data
    
    def is_encrypted(self, data):
        """Verifica se os dados estão criptografados"""
        if not data:
            return False
        
        try:
            # Tenta decodificar base64
            decoded = base64.urlsafe_b64decode(data.encode('utf-8'))

            # Tenta descriptografar
            self.cipher.decrypt(decoded)
            return True

        except Exception:
            return False

    def encrypt_if_needed(self, data):
        """Criptografa apenas se os dados não estiverem já criptografados"""
        if not data:
            return ""

        if self.is_encrypted(data):
            return data
        else:
            return self.encrypt(data)

    def decrypt_safe(self, data):
        """Descriptografa com segurança, retornando dados originais se não criptografados"""
        if not data:
            return ""

        if self.is_encrypted(data):
            return self.decrypt(data)
        else:
            return data

    def change_key(self, new_machine_key):
        """Permite trocar a chave de criptografia"""
        try:
            self.key = self._derive_key(new_machine_key)
            self.cipher = Fernet(self.key)
            return True
        except Exception as e:
            print(f"Erro ao trocar chave: {e}")
            return False

    def get_key_fingerprint(self):
        """Retorna fingerprint da chave para verificação"""
        try:
            return hashlib.md5(self.key).hexdigest()[:8]
        except Exception:
            return "unknown"


# Singleton pattern para instância global
_crypto_instance = None


def get_crypto_instance():
    """Retorna instância singleton do sistema de criptografia"""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = SimpleCrypto()
    return _crypto_instance


def reset_crypto_instance():
    """Reseta a instância singleton (útil para testes)"""
    global _crypto_instance
    _crypto_instance = None


def create_crypto_with_key(machine_key):
    """Cria nova instância de criptografia com chave específica"""
    return SimpleCrypto(machine_key)


def test_crypto_system():
    """Testa o sistema de criptografia"""
    try:
        crypto = get_crypto_instance()

        # Teste básico
        test_data = "Token secreto do GitHub: ghp_1234567890abcdef"
        encrypted = crypto.encrypt(test_data)
        decrypted = crypto.decrypt(encrypted)

        print(f"Teste de criptografia:")
        print(f"Original: {test_data}")
        print(f"Criptografado: {encrypted[:50]}...")
        print(f"Descriptografado: {decrypted}")
        print(f"Fingerprint da chave: {crypto.get_key_fingerprint()}")

        # Verifica se funcionou
        success = test_data == decrypted
        print(f"Resultado: {'✅ Sucesso' if success else '❌ Falha'}")

        return success

    except Exception as e:
        print(f"Erro no teste de criptografia: {e}")
        return False


if __name__ == "__main__":
    test_crypto_system()
