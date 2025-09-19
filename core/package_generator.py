import os
import json
from datetime import datetime
from utils.version_utils import sanitize_name_for_repo, get_namespace_from_display_name, \
    extract_package_name_from_full_name
from ui.strings import RELEASE_WORKFLOW, RELEASERC_JSON


class PackageGenerator:
    def __init__(self, config_manager):
        self.config = config_manager
        self.log_callback = print
        self.progress_callback = None
        self._reset_state()

    def _reset_state(self):
        """Reseta o estado interno do gerador"""
        self._is_generating = False
        self._current_operation = None

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

    def is_busy(self):
        """Verifica se o gerador está ocupado"""
        return self._is_generating

    def get_package_json(self, name, display_name, description, version="0.1.0", unity_dependencies=None):
        company_prefix = self.config.get_value(key='company_prefix', default='com.example')
        author_name = self.config.get_value(key='author_name', default='Author')
        author_email = self.config.get_value(key='author_email', default='author@example.com')
        author_url = self.config.get_value(key='author_url', default='https://github.com/username')
        unity_version = self.config.get_value(key='unity_version', default='2021.3')

        repo_name = self.get_sanitized_repo_name(display_name)
        
        # Garantir que o nome do pacote seja válido
        package_name = extract_package_name_from_full_name(name).lower()
        if not package_name:
            package_name = display_name.lower().replace(' ', '')
            self.log(f"⚠️ Nome do pacote inválido, usando alternativa: {package_name}")

        # Garantir que a versão seja válida
        if not version or not version.replace('.', '').isdigit():
            version = "0.1.0"
            self.log(f"⚠️ Versão inválida, usando padrão: {version}")

        package_data = {
            "name": f"{company_prefix}.{package_name}",
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

        # Validar o JSON gerado
        try:
            json.dumps(package_data)
        except Exception as e:
            self.log(f"⚠️ Erro ao gerar package.json: {str(e)}. Usando formato simplificado.")
            # Formato simplificado como fallback
            package_data = {
                "name": f"{company_prefix}.{package_name}",
                "version": version,
                "displayName": display_name,
                "description": description
            }

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

        # Validações iniciais
        if not base_path or not os.path.exists(base_path):
            self.log("❌ Caminho base inválido ou inexistente")
            raise ValueError("Caminho base inválido ou inexistente")
            
        if not name or not display_name:
            self.log("❌ Nome do pacote ou nome de exibição não podem estar vazios")
            raise ValueError("Nome do pacote ou nome de exibição não podem estar vazios")
            
        if not description:
            self.log("⚠️ Descrição vazia, usando valor padrão")
            description = f"Um pacote Unity para {display_name}"

        # Reset do estado e marca como ocupado
        self._reset_state()
        self._is_generating = True

        try:
            self._current_operation = "Inicializando"
            self.log(f"🚀 Iniciando criação do pacote '{display_name}'...")

            clean_name = extract_package_name_from_full_name(name)
            repo_name = self.get_sanitized_repo_name(display_name)

            package_folder_path = os.path.join(base_path, repo_name)

            if not os.path.exists(package_folder_path):
                os.makedirs(package_folder_path)
                self.log(f"📁 Diretório principal criado: {package_folder_path}")
            else:
                self.log(f"📁 Utilizando diretório existente: {package_folder_path}")

            self._current_operation = "Criando package.json"
            self.update_progress(10, "Iniciando criação do pacote...")

            package_json = self.get_package_json(name, display_name, description, version, unity_dependencies)
            self._create_file(
                os.path.join(package_folder_path, "package.json"),
                json.dumps(package_json, indent=2)
            )
            self.update_progress(20, "Arquivo package.json criado...")

            if create_runtime:
                self._current_operation = "Criando estrutura Runtime"
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
                self._current_operation = "Criando estrutura Editor"
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
                self._current_operation = "Criando testes"
                self._create_tests_structure(package_folder_path, display_name)
                self.update_progress(50, "Estrutura de testes criada...")

            if create_samples:
                self._current_operation = "Criando samples"
                self._create_samples_structure(package_folder_path, display_name)
                self.update_progress(60, "Amostras criadas...")

            self._current_operation = "Criando documentação"
            self._create_documentation(package_folder_path, display_name, description, repo_name)
            self.update_progress(70, "Documentação criada...")

            if license_type:
                self._current_operation = "Criando licença"
                self._create_license(package_folder_path, license_type, display_name)
                self.update_progress(80, "Licença criada...")

            if create_github:
                self._current_operation = "Criando arquivos GitHub"
                self._create_github_files(package_folder_path, display_name, version)
                self.update_progress(90, "Arquivos GitHub criados...")

            self._current_operation = "Finalizando"
            self.update_progress(100, "Pacote criado com sucesso!")
            self.log(f"✅ Pacote '{display_name}' criado com sucesso em: {package_folder_path}")

            return package_folder_path

        except Exception as e:
            self.log(f"❌ Erro ao criar pacote: {str(e)}")
            self.log(f"❌ Operação atual: {self._current_operation}")
            raise
        finally:
            # IMPORTANTE: Sempre reseta o estado, mesmo em caso de erro
            self._reset_state()
            self.log("🔄 Gerador pronto para nova operação")

    def _create_file(self, path, content):
        try:
            # Garantir que o diretório exista
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
                
            # Verificar se o arquivo já existe e fazer backup se necessário
            if os.path.exists(path):
                self.log(f"⚠️ Arquivo já existe, criando backup: {path}")
                backup_path = f"{path}.bak"
                try:
                    import shutil
                    shutil.copy2(path, backup_path)
                except Exception as backup_error:
                    self.log(f"⚠️ Não foi possível criar backup: {str(backup_error)}")
            
            # Escrever o conteúdo no arquivo
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Verificar se o arquivo foi criado corretamente
            if not os.path.exists(path):
                raise IOError(f"Falha ao verificar a existência do arquivo após criação: {path}")
                
            return True
        except Exception as e:
            self.log(f"❌ Erro ao criar arquivo {path}: {str(e)}")
            raise

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

    def _validate_json_string(self, json_string, file_name):
        """Valida se uma string é um JSON válido"""
        try:
            json.loads(json_string)
            return True
        except json.JSONDecodeError as e:
            self.log(f"❌ Erro de validação JSON em {file_name}: {str(e)}")
            return False
            
    def _create_github_files(self, base_path, display_name, version):
        from ui.strings import RELEASE_WORKFLOW, RELEASERC_JSON, GITIGNORE_UNITY

        github_path = os.path.join(base_path, ".github", "workflows")
        os.makedirs(github_path, exist_ok=True)

        # Validar e criar o arquivo release.yml
        self._create_file(
            os.path.join(github_path, "release.yml"),
            RELEASE_WORKFLOW
        )

        # Validar e criar o arquivo .releaserc.json
        if self._validate_json_string(RELEASERC_JSON, ".releaserc.json"):
            self._create_file(
                os.path.join(base_path, ".releaserc.json"),
                RELEASERC_JSON
            )
        else:
            self.log("⚠️ Usando configuração de release padrão devido a erro de validação")
            default_releaserc = '{"branches":["main"],"plugins":["@semantic-release/commit-analyzer","@semantic-release/release-notes-generator","@semantic-release/github"]}'
            self._create_file(
                os.path.join(base_path, ".releaserc.json"),
                default_releaserc
            )

        # Criar o arquivo .gitignore
        self._create_file(os.path.join(base_path, ".gitignore"), GITIGNORE_UNITY)

        self.log("🔧 Arquivos GitHub criados")