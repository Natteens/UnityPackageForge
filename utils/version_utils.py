import re
import os
import sys
import json
from pathlib import Path


def get_current_version():
    """Obtém a versão atual do projeto com melhor tratamento de erros"""
    try:
        # 1. Primeiro tenta ler do version.txt
        version_file = _find_version_file()
        if version_file and os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                if _is_valid_version(version):
                    return version

        # 2. Tenta extrair do CHANGELOG.md
        changelog_path = _find_changelog_path()
        if changelog_path and os.path.exists(changelog_path):
            version = _extract_version_from_changelog(changelog_path)
            if version:
                return version

        # 3. Tenta extrair do setup.py
        setup_path = _find_setup_path()
        if setup_path and os.path.exists(setup_path):
            version = _extract_version_from_setup(setup_path)
            if version:
                return version

        # 4. Tenta extrair do package.json
        package_json_path = _find_package_json_path()
        if package_json_path and os.path.exists(package_json_path):
            version = _extract_version_from_package_json(package_json_path)
            if version:
                return version

    except Exception as e:
        print(f"Erro ao extrair versão: {e}")

    # Fallback para versão padrão
    return "1.0.0"


def _is_valid_version(version):
    """Valida se uma string é uma versão válida no formato semver"""
    if not version:
        return False

    # Padrão semver: major.minor.patch(-prerelease)?
    pattern = r'^(\d+)\.(\d+)\.(\d+)(-[\w\.\-]+)?(\+[\w\.\-]+)?$'
    return bool(re.match(pattern, version.strip()))


def _find_version_file():
    """Localiza o arquivo version.txt"""
    possible_paths = [
        'version.txt',
        '../version.txt',
        '../../version.txt'
    ]

    base_dir = _get_base_directory()
    for path in possible_paths:
        full_path = os.path.join(base_dir, path)
        if os.path.exists(full_path):
            return full_path
    return None


def _find_changelog_path():
    """Localiza o arquivo CHANGELOG.md"""
    base_dir = _get_base_directory()
    possible_paths = [
        'CHANGELOG.md',
        '../CHANGELOG.md',
        '../../CHANGELOG.md'
    ]

    for path in possible_paths:
        full_path = os.path.join(base_dir, path)
        if os.path.exists(full_path):
            return full_path
    return None


def _find_setup_path():
    """Localiza o arquivo setup.py"""
    base_dir = _get_base_directory()
    possible_paths = [
        'setup.py',
        '../setup.py',
        '../../setup.py'
    ]

    for path in possible_paths:
        full_path = os.path.join(base_dir, path)
        if os.path.exists(full_path):
            return full_path
    return None


def _find_package_json_path():
    """Localiza o arquivo package.json"""
    base_dir = _get_base_directory()
    possible_paths = [
        'package.json',
        '../package.json',
        '../../package.json'
    ]

    for path in possible_paths:
        full_path = os.path.join(base_dir, path)
        if os.path.exists(full_path):
            return full_path
    return None


def _get_base_directory():
    """Obtém o diretório base do projeto"""
    if getattr(sys, 'frozen', False):
        # Se for executável
        return os.path.dirname(sys.executable)
    else:
        # Se for código fonte
        current_file = os.path.abspath(__file__)
        return os.path.dirname(os.path.dirname(current_file))


def _extract_version_from_changelog(changelog_path):
    """Extrai versão do CHANGELOG.md"""
    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Procura por padrões como [1.0.0] ou ## [1.0.0]
        patterns = [
            r'\[(\d+\.\d+\.\d+(?:-[\w\.\-]+)?)\]',
            r'##\s*\[(\d+\.\d+\.\d+(?:-[\w\.\-]+)?)\]',
            r'###\s*(\d+\.\d+\.\d+(?:-[\w\.\-]+)?)',
            r'v(\d+\.\d+\.\d+(?:-[\w\.\-]+)?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                version = match.group(1)
                if _is_valid_version(version):
                    return version

    except Exception as e:
        print(f"Erro ao ler CHANGELOG.md: {e}")

    return None


def _extract_version_from_setup(setup_path):
    """Extrai versão do setup.py"""
    try:
        with open(setup_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Procura por version="x.y.z" ou version='x.y.z'
        pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        match = re.search(pattern, content)

        if match:
            version = match.group(1)
            if _is_valid_version(version):
                return version

    except Exception as e:
        print(f"Erro ao ler setup.py: {e}")

    return None


def _extract_version_from_package_json(package_json_path):
    """Extrai versão do package.json"""
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'version' in data:
            version = data['version']
            if _is_valid_version(version):
                return version

    except Exception as e:
        print(f"Erro ao ler package.json: {e}")

    return None


def sanitize_name_for_repo(display_name):
    """Converte nome de exibição para nome válido de repositório GitHub"""
    if not display_name:
        return "unity-package"

    # Remove caracteres especiais e espaços
    sanitized = re.sub(r'[^\w\s\-]', '', display_name.strip())

    # Substitui espaços por hífens
    sanitized = re.sub(r'\s+', '-', sanitized)

    # Remove múltiplos hífens
    sanitized = re.sub(r'-+', '-', sanitized)

    # Remove hífens do início e fim
    sanitized = sanitized.strip('-')

    # Converte para minúsculas
    sanitized = sanitized.lower()

    # Garante que não está vazio
    if not sanitized:
        sanitized = "unity-package"

    # Garante que não seja muito longo (GitHub tem limite de 100 chars)
    if len(sanitized) > 80:
        sanitized = sanitized[:80].rstrip('-')

    return sanitized


def get_namespace_from_display_name(display_name):
    """Gera namespace C# a partir do nome de exibição"""
    if not display_name:
        return "UnityPackage"

    # Remove caracteres especiais
    sanitized = re.sub(r'[^\w\s]', '', display_name.strip())

    # Divide por espaços e capitaliza cada palavra
    words = sanitized.split()
    namespace_parts = []

    for word in words:
        if word:
            # Capitaliza primeira letra e mantém o resto
            clean_word = word[0].upper() + word[1:] if len(word) > 1 else word.upper()
            # Remove números do início se existirem
            clean_word = re.sub(r'^[\d]+', '', clean_word)
            if clean_word:
                namespace_parts.append(clean_word)

    if not namespace_parts:
        return "UnityPackage"

    return "".join(namespace_parts)


def extract_package_name_from_full_name(full_name):
    """Extrai nome do pacote removendo prefixos de empresa"""
    if not full_name:
        return "package"

    # Remove prefixos comuns
    prefixes_to_remove = [
        'com.unity.',
        'com.microsoft.',
        'com.google.',
        'com.example.',
        'com.company.',
        'com.',
        'org.',
        'net.',
        'io.'
    ]

    clean_name = full_name.lower()
    for prefix in prefixes_to_remove:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            break

    # Remove caracteres especiais exceto pontos
    clean_name = re.sub(r'[^\w\.]', '', clean_name)

    # Se tem ponto, pega a última parte
    if '.' in clean_name:
        clean_name = clean_name.split('.')[-1]

    return clean_name if clean_name else "package"


def increment_version(version, increment_type='patch'):
    """Incrementa versão seguindo semver"""
    if not _is_valid_version(version):
        return "1.0.0"

    parts = version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if increment_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif increment_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    return f"{major}.{minor}.{patch}"


def compare_versions(version1, version2):
    """Compara duas versões. Retorna -1, 0, ou 1"""
    if not _is_valid_version(version1) or not _is_valid_version(version2):
        return 0

    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]

    for i in range(3):
        if v1_parts[i] < v2_parts[i]:
            return -1
        elif v1_parts[i] > v2_parts[i]:
            return 1

    return 0
