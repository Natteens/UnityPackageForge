import re
import os
import sys


def get_current_version():
    try:
        changelog_path = _find_changelog_path()

        if changelog_path and os.path.exists(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()

                patterns = [
                    r'##\s*\[(\d+\.\d+\.\d+)\]',  # ## [1.2.3]
                    r'#\s*\[(\d+\.\d+\.\d+)\]',  # # [1.2.3]
                    r'\[(\d+\.\d+\.\d+)\]',  # [1.2.3] anywhere
                    r'v(\d+\.\d+\.\d+)',  # v1.2.3
                    r'(\d+\.\d+\.\d+)'  # 1.2.3 plain
                ]

                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        version = match.group(1)
                        if re.match(r'^\d+\.\d+\.\d+$', version):
                            print(f"Debug: Versão encontrada no CHANGELOG: {version}")
                            return version

    except Exception as e:
        print(f"Erro ao extrair versão do CHANGELOG: {e}")

    try:
        setup_path = _find_setup_path()
        if setup_path and os.path.exists(setup_path):
            with open(setup_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
                if match:
                    version = match.group(1)
                    print(f"Debug: Versão encontrada no setup.py: {version}")
                    return version
    except Exception as e:
        print(f"Erro ao extrair versão do setup.py: {e}")

    try:
        version_path = _find_version_file()
        if version_path and os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                if re.match(r'^\d+\.\d+\.\d+$', version):
                    print(f"Debug: Versão encontrada no arquivo version.txt: {version}")
                    return version
    except Exception as e:
        print(f"Erro ao ler arquivo de versão: {e}")

    print("Debug: Usando versão padrão 1.0.0")
    return "1.0.0"


def _find_changelog_path():
    possible_paths = []

    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        possible_paths.extend([
            os.path.join(app_dir, 'CHANGELOG.md'),
            os.path.join(app_dir, '..', 'CHANGELOG.md'),
            os.path.join(app_dir, 'resources', 'CHANGELOG.md')
        ])
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        possible_paths.extend([
            os.path.join(project_root, 'CHANGELOG.md'),
            os.path.join(os.path.dirname(project_root), 'CHANGELOG.md')
        ])

    for path in possible_paths:
        if os.path.exists(path):
            print(f"Debug: CHANGELOG encontrado em: {path}")
            return path

    print(f"Debug: CHANGELOG não encontrado. Caminhos testados: {possible_paths}")
    return None


def _find_setup_path():
    possible_paths = []

    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        possible_paths.extend([
            os.path.join(app_dir, 'setup.py'),
            os.path.join(app_dir, '..', 'setup.py')
        ])
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        possible_paths.extend([
            os.path.join(project_root, 'setup.py'),
            os.path.join(os.path.dirname(project_root), 'setup.py')
        ])

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def _find_version_file():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        return os.path.join(app_dir, 'version.txt')
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, 'version.txt')


def create_version_file(version="1.0.0"):
    try:
        version_path = _find_version_file()
        os.makedirs(os.path.dirname(version_path), exist_ok=True)

        with open(version_path, 'w', encoding='utf-8') as f:
            f.write(version)

        print(f"Arquivo de versão criado: {version_path} com versão {version}")
        return True
    except Exception as e:
        print(f"Erro ao criar arquivo de versão: {e}")
        return False


def sanitize_name_for_repo(display_name):
    sanitized = display_name.lower().replace(' ', '-')
    sanitized = re.sub(r'[^a-z0-9\-]', '', sanitized)
    sanitized = re.sub(r'-+', '-', sanitized)
    sanitized = sanitized.strip('-')
    return sanitized


def extract_package_name_from_full_name(full_name):
    if '.' in full_name:
        parts = full_name.split('.')
        return parts[-1]
    return full_name


def get_namespace_from_display_name(display_name):
    namespace = re.sub(r'[^a-zA-Z0-9]', '', display_name)
    if namespace and not namespace[0].isalpha():
        namespace = 'Package' + namespace
    return namespace or 'PackageNamespace'