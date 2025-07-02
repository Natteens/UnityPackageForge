import os
import json
import subprocess
from datetime import datetime

from ui.strings import RELEASE_WORKFLOW, RELEASERC_JSON, NODE_PACKAGE_JSON_TEMPLATE


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

    def get_package_json(self, name, display_name, description, version="0.0.1"):
        company_prefix = self.config.get_value(key='company_prefix')
        author_name = self.config.get_value(key='author_name')
        author_email = self.config.get_value(key='author_email')
        author_url = self.config.get_value(key='author_url')
        unity_version = self.config.get_value(key='unity_version')

        return {
            "name": f"{company_prefix}.{name.lower()}",
            "version": version,
            "displayName": display_name,
            "description": description,
            "keywords": ["Unity", "GameDev", name],
            "author": {
                "name": author_name,
                "email": author_email,
                "url": author_url
            },
            "unity": unity_version,
            "samples": [
                {
                    "displayName": "2D Sample",
                    "description": f"Exemplo demonstrando o uso do {display_name} em um jogo 2D.",
                    "path": "Samples~/2D Sample"
                },
                {
                    "displayName": "3D Sample",
                    "description": f"Exemplo demonstrando o uso do {display_name} em um jogo 3D.",
                    "path": "Samples~/3D Sample"
                },
                {
                    "displayName": "Utilities Sample",
                    "description": "Utilitários e prefabs de exemplo para testes e desenvolvimento.",
                    "path": "Samples~/Utilities Sample"
                }
            ],
            "documentationUrl": f"{author_url}/{name}",
            "changelogUrl": f"{author_url}/{name}/blob/main/CHANGELOG.md",
            "licensesUrl": f"{author_url}/{name}/blob/main/LICENSE.md"
        }

    def get_full_package_name(self, name):
        company_prefix = self.config.get_value(key='company_prefix')
        return f"{company_prefix}.{name.lower()}"

    def create_package_structure(self, base_path, name, display_name, description, create_samples=True,
                                 create_runtime=True, create_editor=True, create_tests=True,
                                 create_github=True, create_license="MIT"):
        """
        Cria a estrutura do pacote Unity dentro de uma única pasta com o nome correto do pacote.
        Retorna o caminho completo da pasta criada para operações Git posteriores.
        """
        try:
            # Criar a pasta principal com o nome completo do pacote
            full_package_name = self.get_full_package_name(name)
            package_folder_path = os.path.join(base_path, full_package_name)

            # Verificar se a pasta já existe
            if not os.path.exists(package_folder_path):
                os.makedirs(package_folder_path)
                self.log(f"📁 Diretório principal criado: {package_folder_path}")
            else:
                self.log(f"📁 Utilizando diretório existente: {package_folder_path}")

            self.update_progress(10, "Iniciando criação do pacote...")

            # Criar arquivo package.json
            self._create_file(
                os.path.join(package_folder_path, "package.json"),
                json.dumps(self.get_package_json(name, display_name, description), indent=2)
            )

            self.update_progress(20, "Criando arquivo package.json...")

            # Criar README.md
            readme_content = (
                f"# {display_name}\n\n{description}\n\n## 📥 Instalação\n\n"
                f"Este pacote pode ser instalado através do Unity Package Manager.\n\n"
                f"1. Abra o Package Manager (Window > Package Manager)\n"
                f"2. Clique no botão + e selecione \"Add package from git URL...\"\n"
                f"3. Digite: https://github.com/Natteens/{name}.git\n\n"
                f"## 🚀 Uso\n\n*Documentação em desenvolvimento*\n"
            )
            self._create_file(os.path.join(package_folder_path, "README.md"), readme_content)

            # Criar CHANGELOG.md
            changelog_content = (
                f"# 📝 Changelog\n\nTodos os lançamentos notáveis serão documentados neste arquivo.\n\n"
                f"O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).\n\n"
                f"## [Não lançado]\n\n### Adicionado\n- ✨ Estrutura inicial do pacote\n"
            )
            self._create_file(os.path.join(package_folder_path, "CHANGELOG.md"), changelog_content)

            # Criar arquivo de licença se especificado
            if create_license:
                self._create_license_file(package_folder_path, create_license, name, display_name)
            self.update_progress(30, "Criando arquivos de documentação...")

            # Criar estrutura de código
            if create_runtime:
                self._create_assembly_structure(package_folder_path, name, "Runtime", False)
            if create_editor:
                self._create_assembly_structure(package_folder_path, name, "Editor", True)
            self.update_progress(40, "Criando estrutura de código...")

            # Criar documentação
            docs_path = os.path.join(package_folder_path, "Documentation~")
            os.makedirs(docs_path, exist_ok=True)
            doc_content = (
                f"# 📚 {display_name}\n\n{description}\n\n## 🚀 Início Rápido\n\n*Em desenvolvimento*\n"
            )
            self._create_file(os.path.join(docs_path, "index.md"), doc_content)

            self.update_progress(50, "Criando documentação...")

            # Criar exemplos se solicitado
            if create_samples:
                self._create_samples(package_folder_path, name, display_name)
            self.update_progress(70, "Criando exemplos...")

            # Criar testes se solicitado
            if create_tests:
                self._create_tests(package_folder_path, name)
            self.update_progress(80, "Criando estrutura de testes...")

            # Criar arquivos do GitHub se solicitado
            if create_github:
                self._create_github_files(package_folder_path)

            # Salvar o último diretório usado
            self.config.set_value(key='last_directory', value=base_path)

            self.update_progress(100, "✅ Pacote criado com sucesso!")
            self.log("✅ Pacote criado com sucesso!")

            # Retornar o caminho da pasta do pacote para operações Git
            return package_folder_path

        except Exception as e:
            self.update_progress(100, f"❌ Erro: {str(e)}")
            self.log(f"❌ Erro ao criar pacote: {str(e)}")
            return None

    def _create_file(self, path, content):
        """Cria um arquivo garantindo que o diretório pai exista"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.log(f"📄 Arquivo criado: {os.path.basename(path)}")

    def _create_assembly_structure(self, base_path, package_name, folder_type, is_editor):
        """Cria a estrutura de assembly do Unity para Runtime ou Editor"""
        folder_path = os.path.join(base_path, folder_type)
        os.makedirs(folder_path, exist_ok=True)

        company_prefix = self.config.get_value(key='company_prefix')
        assembly_name = f"{company_prefix}.{package_name.lower()}" + (".editor" if is_editor else "")

        asmdef = {
            "name": assembly_name,
            "rootNamespace": f"Natteens.{package_name}",
            "references": []
        }

        if is_editor:
            asmdef["references"].append(f"{company_prefix}.{package_name.lower()}")
            asmdef["includePlatforms"] = ["Editor"]

        self._create_file(os.path.join(folder_path, f"{assembly_name}.asmdef"), json.dumps(asmdef, indent=2))

        if is_editor:
            editor_content = (
                f"using UnityEngine;\nusing UnityEditor;\n\nnamespace Natteens.{package_name}\n{{\n"
                f"    /// <summary>\n    /// Editor para {package_name}\n    /// </summary>\n"
                f"    public class {package_name}Editor : Editor\n    {{\n        "
                f"// Implementação futura\n    }}\n}}\n"
            )
            self._create_file(os.path.join(folder_path, f"{package_name}Editor.cs"), editor_content)
        else:
            manager_content = (
                f"using UnityEngine;\n\nnamespace Natteens.{package_name}\n{{\n"
                f"    /// <summary>\n    /// Gerenciador principal para {package_name}\n    /// </summary>\n"
                f"    public class {package_name}Manager : MonoBehaviour\n    {{\n        "
                f"// Implementação futura\n    }}\n}}\n"
            )
            self._create_file(os.path.join(folder_path, f"{package_name}Manager.cs"), manager_content)

    def _create_license_file(self, base_path, license_type, name, display_name):
        """Cria arquivo de licença apropriado"""
        year = datetime.now().year
        author_name = self.config.get_value(key='author_name')

        if license_type == "MIT":
            content = (
                f"MIT License\n\nCopyright (c) {year} {author_name}\n\n"
                f"Permission is hereby granted, free of charge, to any person obtaining a copy "
                f"of this software and associated documentation files (the \"{display_name}\"), to deal "
                f"in the Software without restriction, including without limitation the rights "
                f"to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
                f"copies of the Software, and to permit persons to whom the Software is "
                f"furnished to do so, subject to the following conditions:\n\n"
                f"The above copyright notice and this permission notice shall be included in all "
                f"copies or substantial portions of the Software.\n\n"
                f"THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
                f"IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
                f"FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
                f"AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
                f"LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
                f"OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
                f"SOFTWARE."
            )
        else:
            content = f"# Licença\nEste software está licenciado sob os termos da licença {license_type}."

        self._create_file(os.path.join(base_path, "LICENSE.md"), content)

    def _create_samples(self, base_path, name, display_name):
        """Cria pastas e arquivos de exemplos"""
        samples_categories = ["2D Sample", "3D Sample", "Utilities Sample"]
        samples_base = os.path.join(base_path, "Samples~")

        for category in samples_categories:
            category_path = os.path.join(samples_base, category)
            os.makedirs(category_path, exist_ok=True)

            readme_content = (
                f"# {category}\n\nExemplo para o pacote {display_name}.\n\n"
                f"## Como usar\n\n1. Importe este sample pelo Unity Package Manager\n"
                f"2. Abra a cena de exemplo\n3. Play\n"
            )
            self._create_file(os.path.join(category_path, "README.md"), readme_content)

            scenes_path = os.path.join(category_path, "Scenes")
            os.makedirs(scenes_path, exist_ok=True)

            self.log(f"📁 Amostra criada: {category}")

    def _create_tests(self, base_path, name):
        """Cria estrutura de testes"""
        tests_path = os.path.join(base_path, "Tests")
        os.makedirs(tests_path, exist_ok=True)

        test_types = ["Editor", "Runtime"]
        company_prefix = self.config.get_value(key='company_prefix')

        for test_type in test_types:
            test_folder = os.path.join(tests_path, test_type)
            os.makedirs(test_folder, exist_ok=True)

            asmdef_name = f"{company_prefix}.{name.lower()}.{test_type.lower()}.tests"
            asmdef = {
                "name": asmdef_name,
                "rootNamespace": f"Natteens.{name}.Tests",
                "references": [
                    "UnityEngine.TestRunner",
                    "UnityEditor.TestRunner",
                    f"{company_prefix}.{name.lower()}"
                ],
                "includePlatforms": [test_type] if test_type == "Editor" else [],
                "excludePlatforms": [],
                "defineConstraints": ["UNITY_INCLUDE_TESTS"],
                "precompiledReferences": ["nunit.framework.dll"]
            }

            if test_type == "Editor":
                asmdef["references"].append(f"{company_prefix}.{name.lower()}.editor")

            self._create_file(os.path.join(test_folder, f"{asmdef_name}.asmdef"), json.dumps(asmdef, indent=2))

            test_class_content = (
                f"using System.Collections;\nusing System.Collections.Generic;\nusing NUnit.Framework;\n"
                f"using UnityEngine;\nusing UnityEngine.TestTools;\nusing Natteens.{name};\n\n"
                f"namespace Natteens.{name}.Tests\n{{\n    public class {name}Test{test_type}\n    {{\n        "
                f"[Test]\n        public void {name}SimpleTest()\n        {{\n            "
                f"// Arrange\n            // Act\n            // Assert\n            "
                f"Assert.Pass(\"Teste passou!\");\n        }}\n    }}\n}}\n"
            )
            self._create_file(os.path.join(test_folder, f"{name}Test{test_type}.cs"), test_class_content)

        self.log(f"📁 Testes criados: {tests_path}")

    def _create_github_files(self, base_path):
        """Cria arquivos de configuração do GitHub compatíveis com pacotes Unity"""
        github_dir = os.path.join(base_path, ".github")
        workflows_dir = os.path.join(github_dir, "workflows")
        os.makedirs(workflows_dir, exist_ok=True)

        # Criar apenas o arquivo release.yml com o conteúdo da constante RELEASE_WORKFLOW
        self._create_file(os.path.join(workflows_dir, "release.yml"), RELEASE_WORKFLOW)

        # Criar .releaserc.json na raiz do pacote
        self._create_file(os.path.join(base_path, ".releaserc.json"), RELEASERC_JSON)

        # Arquivo .gitignore específico para Unity (removendo exclusão do package-lock.json)
        gitignore_content = (
            "# Unity specific\nLibrary/\nTemp/\nLogs/\nUserSettings/\nobj/\nBuild/\nBuilds/\n"
            ".DS_Store\n*.csproj\n*.unityproj\n*.sln\n*.suo\n*.tmp\n*.user\n*.userprefs\n"
            "*.pidb\n*.booproj\n*.svd\n*.pdb\n*.mdb\n*.opendb\n*.VC.db\n"
            "# IDE\n.vs/\n.idea/\n.vscode/\n"
            "# Node.js\nnode_modules/\n"
        )
        self._create_file(os.path.join(base_path, ".gitignore"), gitignore_content)

        # Criar package.json do Node.js para semantic-release usando o template
        repo_name = os.path.basename(base_path).lower()
        # Obter dados de configuração do usuário 
        author = self.config.get_value(section='user', key='name', default='Autor')
        username = self.config.get_value(section='github', key='username', default='usuario')
        
        node_package_content = NODE_PACKAGE_JSON_TEMPLATE.format(
            repo_name=repo_name,
            description=f"Unity Package: {repo_name}",
            username=username,
            author=author,
            license="MIT"
        )
        
        # Criar arquivo package.json para Node.js na raiz (separado do Unity package.json)
        node_package_path = os.path.join(base_path, "node-package.json")
        self._create_file(node_package_path, node_package_content)
        
        # Mover o arquivo Node.js para package.json temporariamente para gerar o lock file
        unity_package_path = os.path.join(base_path, "package.json")
        temp_unity_package_path = os.path.join(base_path, "unity-package.json")
        
        try:
            # Fazer backup do package.json do Unity se existir
            if os.path.exists(unity_package_path):
                os.rename(unity_package_path, temp_unity_package_path)
            
            # Mover o Node.js package.json para ser o principal
            os.rename(node_package_path, unity_package_path)
            
            # Executar npm install para gerar package-lock.json
            self.log("📦 Gerando package-lock.json...")
            try:
                subprocess.run(['npm', 'install'], cwd=base_path, check=True, 
                             capture_output=True, text=True)
                self.log("✅ package-lock.json gerado com sucesso!")
            except subprocess.CalledProcessError as e:
                self.log(f"⚠️ Aviso: Não foi possível gerar package-lock.json: {e}")
                # Continuar mesmo se npm install falhar
            except FileNotFoundError:
                self.log("⚠️ Aviso: npm não encontrado. package-lock.json não foi gerado.")
            
            # Restaurar o package.json do Unity
            if os.path.exists(temp_unity_package_path):
                os.rename(unity_package_path, node_package_path)
                os.rename(temp_unity_package_path, unity_package_path)
            else:
                # Se não havia package.json do Unity, manter apenas o Node.js
                pass
                
        except Exception as e:
            self.log(f"❌ Erro ao configurar arquivos Node.js: {e}")
            # Restaurar estado original em caso de erro
            if os.path.exists(temp_unity_package_path):
                if os.path.exists(unity_package_path):
                    os.remove(unity_package_path)
                os.rename(temp_unity_package_path, unity_package_path)

        # Adicionar arquivo de configuração para publicação futura no npm/OpenUPM
        npmrc_content = "registry=https://registry.npmjs.org/\n"
        self._create_file(os.path.join(base_path, ".npmrc"), npmrc_content)

        self.log(f"📁 Configuração GitHub criada: {github_dir}")
        self.log("🚀 Configuração para semantic-release criada com sucesso!")