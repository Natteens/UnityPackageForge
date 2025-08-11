#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de build para Unity Package Forge
Verifica se todas as dependências e estruturas estão corretas antes do build
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

# Configuração de encoding para Windows
if sys.platform == "win32":
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.utf8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
        except:
            pass

class BuildValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = Path(__file__).parent

        # Configurar stdout para UTF-8 no Windows
        if sys.platform == "win32":
            try:
                import codecs
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
            except:
                pass

    def log_error(self, message):
        """Log de erro com fallback para ASCII"""
        try:
            error_msg = f"❌ ERRO: {message}"
            self.errors.append(error_msg)
            print(error_msg)
        except UnicodeEncodeError:
            error_msg = f"[X] ERRO: {message}"
            self.errors.append(error_msg)
            print(error_msg)

    def log_warning(self, message):
        """Log de aviso com fallback para ASCII"""
        try:
            warning_msg = f"⚠️ AVISO: {message}"
            self.warnings.append(warning_msg)
            print(warning_msg)
        except UnicodeEncodeError:
            warning_msg = f"[!] AVISO: {message}"
            self.warnings.append(warning_msg)
            print(warning_msg)

    def log_success(self, message):
        """Log de sucesso com fallback para ASCII"""
        try:
            print(f"✅ {message}")
        except UnicodeEncodeError:
            print(f"[OK] {message}")

    def safe_print(self, message):
        """Print seguro que funciona em qualquer terminal"""
        try:
            print(message)
        except UnicodeEncodeError:
            # Remove emojis e caracteres especiais
            clean_message = message.encode('ascii', 'ignore').decode('ascii')
            print(clean_message)

    def validate_python_version(self):
        """Valida a versão do Python"""
        self.safe_print("Verificando versao do Python...")
        if sys.version_info < (3, 7):
            self.log_error(f"Python 3.7+ necessario. Atual: {sys.version}")
            return False
        self.log_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True

    def validate_dependencies(self):
        """Valida todas as dependências necessárias"""
        self.safe_print("Verificando dependencias...")

        required_packages = [
            'customtkinter',
            'requests',
            'cryptography',
            'pyinstaller'
        ]

        missing = []
        for package in required_packages:
            try:
                __import__(package)
                self.log_success(f"Dependencia {package} encontrada")
            except ImportError:
                missing.append(package)
                self.log_error(f"Dependencia {package} nao encontrada")

        if missing:
            self.log_error(f"Instale as dependencias: pip install {' '.join(missing)}")
            return False

        return True

    def validate_file_structure(self):
        """Valida a estrutura de arquivos do projeto"""
        self.safe_print("Verificando estrutura de arquivos...")

        required_files = [
            'main.py',
            'requirements.txt',
            'setup.py',
            'version.txt',
            'ui/strings.py',
            'core/package_generator.py',
            'core/github_manager.py',
            'config/config_manager.py',
            'utils/version_utils.py',
            'utils/crypto_utils.py',
            'utils/helpers.py',
            'utils/resource_utils.py'
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                self.log_error(f"Arquivo obrigatório não encontrado: {file_path}")
            else:
                self.log_success(f"Arquivo encontrado: {file_path}")

        return len(missing_files) == 0

    def validate_version_consistency(self):
        """Valida consistência de versões em todos os arquivos"""
        self.safe_print("Verificando consistência de versões...")

        versions = {}

        # Versão do version.txt
        version_file = self.project_root / 'version.txt'
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                versions['version.txt'] = f.read().strip()

        # Versão do setup.py
        setup_file = self.project_root / 'setup.py'
        if setup_file.exists():
            try:
                with open(setup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    import re
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        versions['setup.py'] = match.group(1)
            except Exception:
                pass

        # Versão do package.json
        package_file = self.project_root / 'package.json'
        if package_file.exists():
            try:
                with open(package_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'version' in data:
                        versions['package.json'] = data['version']
            except Exception:
                pass

        # Verificar consistência
        if len(set(versions.values())) > 1:
            self.log_warning("Versões inconsistentes encontradas:")
            for file, version in versions.items():
                print(f"  {file}: {version}")
        else:
            if versions:
                version = list(versions.values())[0]
                self.log_success(f"Todas as versões consistentes: {version}")
            else:
                self.log_warning("Nenhuma versão encontrada nos arquivos")

        return True

    def validate_imports(self):
        """Valida todos os imports do projeto"""
        self.safe_print("Verificando imports do projeto...")

        try:
            # Adiciona o diretório do projeto ao path
            sys.path.insert(0, str(self.project_root))

            # Testa import do main
            import main
            self.log_success("Import do main.py funcionando")

            # Testa imports dos módulos principais
            from ui.ctk_generator_gui import PackageGeneratorGUI
            from core.package_generator import PackageGenerator
            from core.github_manager import GitHubManager
            from config.config_manager import ConfigManager
            from utils.version_utils import get_current_version

            self.log_success("Todos os imports principais funcionando")
            return True

        except ImportError as e:
            self.log_error(f"Erro de import: {e}")
            return False
        except Exception as e:
            self.log_error(f"Erro inesperado nos imports: {e}")
            return False

    def validate_config_files(self):
        """Valida arquivos de configuração"""
        self.safe_print("Verificando arquivos de configuração...")

        # Verifica config.ini.example
        config_example = self.project_root / 'config.ini.example'
        if not config_example.exists():
            self.log_warning("config.ini.example não encontrado")
        else:
            self.log_success("config.ini.example encontrado")

        # Verifica requirements.txt
        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                content = f.read()
                required_deps = ['customtkinter', 'requests', 'cryptography', 'pyinstaller']
                for dep in required_deps:
                    if dep not in content:
                        self.log_warning(f"Dependência {dep} não encontrada em requirements.txt")
                    else:
                        self.log_success(f"Dependência {dep} listada em requirements.txt")
        else:
            self.log_error("requirements.txt não encontrado")

        return True

    def validate_build_script(self):
        """Valida o script de build"""
        self.safe_print("Verificando script de build...")

        build_script = self.project_root / 'build.py'
        if not build_script.exists():
            self.log_error("build.py não encontrado")
            return False

        try:
            # Verifica se o script é executável
            with open(build_script, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verifica funções essenciais
            essential_functions = [
                'check_dependencies',
                'build_executable',
                'create_version_info'
            ]

            for func in essential_functions:
                if f"def {func}" in content:
                    self.log_success(f"Função {func} encontrada no build.py")
                else:
                    self.log_warning(f"Função {func} não encontrada no build.py")

        except Exception as e:
            self.log_error(f"Erro ao validar build.py: {e}")
            return False

        return True

    def run_validation(self):
        """Executa todas as validações"""
        self.safe_print("Iniciando validacao do build...")
        self.safe_print("=" * 50)

        validations = [
            ("Versao do Python", self.validate_python_version),
            ("Dependencias", self.validate_dependencies),
            ("Estrutura de arquivos", self.validate_file_structure),
            ("Consistencia de versoes", self.validate_version_consistency),
            ("Imports do projeto", self.validate_imports),
            ("Arquivos de configuracao", self.validate_config_files),
            ("Script de build", self.validate_build_script)
        ]

        success_count = 0
        for validation_name, validation_func in validations:
            try:
                self.safe_print(f"\nValidando: {validation_name}")
                if validation_func():
                    success_count += 1
                self.safe_print("-" * 30)
            except Exception as e:
                self.log_error(f"Erro durante validacao {validation_name}: {e}")
                self.safe_print("-" * 30)

        self.safe_print("=" * 50)
        self.safe_print(f"Resultado da Validacao:")
        self.safe_print(f"Validacoes bem-sucedidas: {success_count}/{len(validations)}")

        if self.warnings:
            self.safe_print(f"Avisos: {len(self.warnings)}")
            for warning in self.warnings:
                self.safe_print(f"  {warning}")

        if self.errors:
            self.safe_print(f"Erros: {len(self.errors)}")
            for error in self.errors:
                self.safe_print(f"  {error}")
            self.safe_print("\nBuild NAO recomendado devido aos erros acima")
            return False
        else:
            self.safe_print("\nProjeto validado com sucesso! Build pode prosseguir.")
            return True


if __name__ == "__main__":
    validator = BuildValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)
