import re
import os

def get_current_version():
    """Get current version from CHANGELOG.md with robust parsing"""
    try:
        changelog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CHANGELOG.md')
        if os.path.exists(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Try multiple patterns to find version numbers
                patterns = [
                    r'##\s*\[(\d+\.\d+\.\d+)\]',  # ## [1.2.3]
                    r'#\s*\[(\d+\.\d+\.\d+)\]',   # # [1.2.3] 
                    r'\[(\d+\.\d+\.\d+)\]',       # [1.2.3] anywhere
                    r'v(\d+\.\d+\.\d+)',          # v1.2.3
                    r'(\d+\.\d+\.\d+)'            # 1.2.3 plain
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        version = match.group(1)
                        # Validate it's a proper semantic version
                        if re.match(r'^\d+\.\d+\.\d+$', version):
                            return version
                        
    except Exception as e:
        print(f"Erro ao extrair versão: {e}")
    
    # Fallback: try to get from setup.py or other sources
    try:
        setup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.py')
        if os.path.exists(setup_path):
            with open(setup_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
                if match:
                    return match.group(1)
    except:
        pass
    
    return "1.0.0"

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
