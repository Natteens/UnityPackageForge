import os
import json
from datetime import datetime
from utils.version_utils import sanitize_name_for_repo, get_namespace_from_display_name, extract_package_name_from_full_name
from ui.strings import RELEASE_WORKFLOW, RELEASERC_JSON

class PackageGenerator:
    def __init__(self, config_manager):
        self.config = config_manager
        self.log_callback = print
        self.progress_callback = None

    def set_log_callback(self, callback):
        self.log_callback = callback

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def update_progress(self, value, message=""):
        if self.progress_callback:
            self.progress_callback(value, message)

    def get_sanitized_repo_name(self, display_name):
        return sanitize_name_for_repo(display_name)

    def get_package_json(self, name, display_name, description, version="0.1.0", unity_dependencies=None):
        company_prefix = self.config.get_value(key='company_prefix', default='com.example')
        author_name = self.config.get_value(key='author_name', default='Author')
        author_email = self.config.get_value(key='author_email', default='author@example.com')
        author_url = self.config.get_value(key='author_url', default='https://github.com/username')
        unity_version = self.config.get_value(key='unity_version', default='2021.3')

        repo_name = self.get_sanitized_repo_name(display_name)

        package_data = {
            "name": f"{company_prefix}.{extract_package_name_from_full_name(name).lower()}",
            "version": version,
            "displayName": display_name,
            "description": description,
            "keywords": ["Unity", "GameDev", display_name.replace(' ', '')],
            "author": {
                "name": author_name,
                "email": author_email,
                "url": author_url
            },
            "unity": unity_version,
            "documentationUrl": f"{author_url}/{repo_name}",
            "changelogUrl": f"{author_url}/{repo_name}/blob/main/CHANGELOG.md",
            "licensesUrl": f"{author_url}/{repo_name}/blob/main/LICENSE.md"
        }

        if unity_dependencies:
            package_data["dependencies"] = unity_dependencies

        return package_data

    def create_asmdef(self, path, name, display_name, is_editor=False):
        namespace = get_namespace_from_display_name(display_name)

        asmdef_data = {
            "name": name,
            "rootNamespace": namespace,
            "references": [],
            "includePlatforms": [],
            "excludePlatforms": [],
            "allowUnsafeCode": False,
            "overrideReferences": False,
            "precompiledReferences": [],
            "autoReferenced": True,
            "defineConstraints": [],
            "versionDefines": [],
            "noEngineReferences": False
        }

        if is_editor:
            asmdef_data["includePlatforms"] = ["Editor"]

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asmdef_data, f, indent=2)

    def create_package_structure(self, base_path, name, display_name, description, version="0.1.0",
                                create_samples=True, create_runtime=True, create_editor=True,
                                create_tests=True, create_github=True, license_type="MIT",
                                unity_dependencies=None):
        try:
            clean_name = extract_package_name_from_full_name(name)
            repo_name = self.get_sanitized_repo_name(display_name)

            package_folder_path = os.path.join(base_path, repo_name)

            if not os.path.exists(package_folder_path):
                os.makedirs(package_folder_path)
                self.log(f"📁 Diretório principal criado: {package_folder_path}")
            else:
                self.log(f"📁 Utilizando diretório existente: {package_folder_path}")

            self.update_progress(10, "Iniciando criação do pacote...")

            package_json = self.get_package_json(name, display_name, description, version, unity_dependencies)
            self._create_file(
                os.path.join(package_folder_path, "package.json"),
                json.dumps(package_json, indent=2)
            )
            self.update_progress(20, "Arquivo package.json criado...")

            if create_runtime:
                runtime_path = os.path.join(package_folder_path, "Runtime")
                os.makedirs(runtime_path, exist_ok=True)

                asmdef_name = f"{get_namespace_from_display_name(display_name)}"
                self.create_asmdef(
                    os.path.join(runtime_path, f"{asmdef_name}.asmdef"),
                    asmdef_name,
                    display_name
                )
                self.log("📁 Pasta Runtime criada com .asmdef")

            if create_editor:
                editor_path = os.path.join(package_folder_path, "Editor")
                os.makedirs(editor_path, exist_ok=True)

                asmdef_name = f"{get_namespace_from_display_name(display_name)}.Editor"
                self.create_asmdef(
                    os.path.join(editor_path, f"{asmdef_name}.asmdef"),
                    asmdef_name,
                    display_name,
                    is_editor=True
                )
                self.log("📁 Pasta Editor criada com .asmdef")

            self.update_progress(40, "Estrutura de pastas criada...")

            if create_tests:
                self._create_tests_structure(package_folder_path, display_name)
                self.update_progress(50, "Estrutura de testes criada...")

            if create_samples:
                self._create_samples_structure(package_folder_path, display_name)
                self.update_progress(60, "Amostras criadas...")

            self._create_documentation(package_folder_path, display_name, description, repo_name)
            self.update_progress(70, "Documentação criada...")

            if license_type:
                self._create_license(package_folder_path, license_type, display_name)
                self.update_progress(80, "Licença criada...")

            if create_github:
                self._create_github_files(package_folder_path, display_name, version)
                self.update_progress(90, "Arquivos GitHub criados...")

            self.update_progress(100, "Pacote criado com sucesso!")
            self.log(f"✅ Pacote '{display_name}' criado com sucesso em: {package_folder_path}")

            return package_folder_path

        except Exception as e:
            self.log(f"❌ Erro ao criar pacote: {str(e)}")
            raise

    def _create_file(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_tests_structure(self, base_path, display_name):
        tests_path = os.path.join(base_path, "Tests")

        runtime_tests_path = os.path.join(tests_path, "Runtime")
        os.makedirs(runtime_tests_path, exist_ok=True)

        editor_tests_path = os.path.join(tests_path, "Editor")
        os.makedirs(editor_tests_path, exist_ok=True)

        namespace = get_namespace_from_display_name(display_name)

        runtime_asmdef = {
            "name": f"{namespace}.Tests",
            "rootNamespace": namespace,
            "references": [
                "UnityEngine.TestRunner",
                "UnityEditor.TestRunner",
                namespace
            ],
            "includePlatforms": [],
            "excludePlatforms": [],
            "allowUnsafeCode": False,
            "overrideReferences": True,
            "precompiledReferences": [
                "nunit.framework.dll"
            ],
            "autoReferenced": False,
            "defineConstraints": [
                "UNITY_INCLUDE_TESTS"
            ]
        }

        self._create_file(
            os.path.join(runtime_tests_path, f"{namespace}.Tests.asmdef"),
            json.dumps(runtime_asmdef, indent=2)
        )

        editor_asmdef = runtime_asmdef.copy()
        editor_asmdef["name"] = f"{namespace}.Editor.Tests"
        editor_asmdef["rootNamespace"] = namespace
        editor_asmdef["includePlatforms"] = ["Editor"]

        self._create_file(
            os.path.join(editor_tests_path, f"{namespace}.Editor.Tests.asmdef"),
            json.dumps(editor_asmdef, indent=2)
        )

        self.log("🧪 Estrutura de testes criada")

    def _create_samples_structure(self, base_path, display_name):
        from ui.strings import SAMPLE_FOLDERS_INFO

        samples_path = os.path.join(base_path, "Samples~")

        sample_folders = ["Basic", "Advanced", "Utilities"]

        for folder in sample_folders:
            folder_path = os.path.join(samples_path, folder)
            os.makedirs(folder_path, exist_ok=True)

            readme_content = SAMPLE_FOLDERS_INFO.get(folder, "").format(
                display_name=display_name,
                folder=folder
            )

            self._create_file(os.path.join(folder_path, "README.md"), readme_content)

        self.log("📦 Estrutura de amostras criada")

    def _create_documentation(self, base_path, display_name, description, repo_name):
        from ui.strings import README_TEMPLATE, CHANGELOG_TEMPLATE

        readme_content = README_TEMPLATE.format(
            display_name=display_name,
            description=description,
            repo_name=repo_name
        )
        self._create_file(os.path.join(base_path, "README.md"), readme_content)

        changelog_content = CHANGELOG_TEMPLATE.format(
            date=datetime.now().strftime('%Y-%m-%d')
        )
        self._create_file(os.path.join(base_path, "CHANGELOG.md"), changelog_content)

        self.log("📝 Documentação criada")

    def _create_license(self, base_path, license_type, display_name):
        from ui.strings import LICENSE_MIT

        if license_type == "MIT":
            author_name = self.config.get_value(key='author_name', default='Author')
            license_content = LICENSE_MIT.format(
                year=datetime.now().year,
                author=author_name,
                package=display_name
            )
            self._create_file(os.path.join(base_path, "LICENSE.md"), license_content)
            self.log("📄 Licença MIT criada")

    def _create_github_files(self, base_path, display_name, version):
        from ui.strings import RELEASE_WORKFLOW, RELEASERC_JSON, GITIGNORE_UNITY

        github_path = os.path.join(base_path, ".github", "workflows")
        os.makedirs(github_path, exist_ok=True)

        self._create_file(
            os.path.join(github_path, "release.yml"),
            RELEASE_WORKFLOW
        )

        self._create_file(
            os.path.join(base_path, ".releaserc.json"),
            RELEASERC_JSON.format(version=version)
        )

        self._create_file(os.path.join(base_path, ".gitignore"), GITIGNORE_UNITY)

        self.log("🔧 Arquivos GitHub criados")

