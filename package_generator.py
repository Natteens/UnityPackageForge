import configparser
import json
import os
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import ttk, filedialog, messagebox, scrolledtext

try: import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"]) 
    import requests

COLORS = {"bg": "#f0f0f0", "fg": "#333333", "text_bg": "#ffffff", "text_fg": "#333333", "accent": "#007BFF", 
          "success": "#28a745", "error": "#dc3545", "warning": "#ffc107", "header_bg": "#e9ecef", 
          "log_bg": "#ffffff", "log_fg": "#333333"}

class GitHubManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.token = self.config.get_value(section='github', key='token', default='')
        self.username = self.config.get_value(section='github', key='username', default='')
    
    def is_configured(self): return bool(self.token and self.username)
    
    def check_credentials(self):
        if not self.is_configured(): return False
        try:
            response = requests.get("https://api.github.com/user", headers={"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"})
            response.raise_for_status()
            return True
        except Exception: return False
    
    def create_repository(self, name, description, private=False, auto_init=False):
        if not self.is_configured(): return {"error": "Token de acesso GitHub não configurado"}
        try:
            response = requests.post("https://api.github.com/user/repos", headers={"Authorization": f"token {self.token}", 
                "Accept": "application/vnd.github.v3+json"}, json={"name": name, "description": description, 
                "private": private, "auto_init": auto_init, "gitignore_template": None, "license_template": None})
            response.raise_for_status()
            return response.json()
        except Exception as e: return {"error": str(e)}
    
    def run_git_command(self, folder_path, command, callback=None):
        def run_command():
            try:
                result = subprocess.run(["git"] + command, cwd=folder_path, stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, text=True, check=True)
                if callback: callback(True, result.stdout)
                return result.stdout
            except subprocess.CalledProcessError as e:
                if callback: callback(False, e.stderr)
                return e.stderr
        threading.Thread(target=run_command).start()

    def setup_repository(self, folder_path, repo_name, repo_url, callback=None):
        steps = [
            (["init"], "Inicializando repositório Git..."),
            (["add", "."], "Adicionando arquivos..."),
            (["commit", "-m", "Initial commit - Unity Package Structure"], "Realizando commit inicial..."),
            (["branch", "-M", "main"], "Configurando branch main..."),
            (["remote", "add", "origin", repo_url], "Adicionando remote origin..."),
            (["push", "-u", "origin", "main"], "Enviando arquivos para o GitHub...")
        ]
        
        def execute_steps(step_index=0):
            if step_index >= len(steps):
                if callback: callback(True, "✅ Repositório configurado com sucesso!", 100)
                return
            
            command, message = steps[step_index]
            progress = int((step_index / len(steps)) * 100)
            if callback: callback(True, message, progress)
            
            def on_command_complete(success, output):
                if success: execute_steps(step_index + 1)
                else: 
                    if callback: callback(False, f"❌ Erro: {output}", progress)
            
            self.run_git_command(folder_path, command, on_command_complete)
        
        execute_steps()

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config['DEFAULT'] = {'last_directory': os.path.expanduser('~'), 'author_name': 'Nathan Miranda',
                'author_email': 'nathanmiranda1102@gmail.com', 'author_url': 'https://github.com/Natteens',
                'unity_version': '2021.3', 'company_prefix': 'com.natteens'}
            self.config['github'] = {'username': '', 'token': ''}
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f: self.config.write(f)
    
    def get_value(self, section='DEFAULT', key=None, default=None):
        try: return self.config[section][key]
        except (KeyError, ValueError): return default
    
    def set_value(self, section='DEFAULT', key=None, value=None):
        if section not in self.config: self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

class PackageGenerator:
    def __init__(self, config_manager):
        self.config = config_manager
        self.log_callback = print
        self.progress_callback = None
    
    def set_log_callback(self, callback): self.log_callback = callback
    def set_progress_callback(self, callback): self.progress_callback = callback
    def log(self, message): 
        if self.log_callback: self.log_callback(message)
    def update_progress(self, value, message=""): 
        if self.progress_callback: self.progress_callback(value, message)
    
    def get_package_json(self, name, display_name, description, version="0.0.1"):
        company_prefix = self.config.get_value(key='company_prefix')
        author_name = self.config.get_value(key='author_name')
        author_email = self.config.get_value(key='author_email')
        author_url = self.config.get_value(key='author_url')
        unity_version = self.config.get_value(key='unity_version')
        
        return {
            "name": f"{company_prefix}.{name.lower()}", "version": version, "displayName": display_name,
            "description": description, "keywords": ["Unity", "GameDev", name],
            "author": {"name": author_name, "email": author_email, "url": author_url},
            "unity": unity_version,
            "samples": [
                {"displayName": "2D Sample", "description": f"Exemplo demonstrando o uso do {display_name} em um jogo 2D.", "path": "Samples~/2D Sample"},
                {"displayName": "3D Sample", "description": f"Exemplo demonstrando o uso do {display_name} em um jogo 3D.", "path": "Samples~/3D Sample"},
                {"displayName": "Utilities Sample", "description": "Utilitários e prefabs de exemplo para testes e desenvolvimento.", "path": "Samples~/Utilities Sample"}
            ],
            "documentationUrl": f"{author_url}/{name}", "changelogUrl": f"{author_url}/{name}/blob/main/CHANGELOG.md",
            "licensesUrl": f"{author_url}/{name}/blob/main/LICENSE.md"
        }
    
    def get_full_package_name(self, name):
        company_prefix = self.config.get_value(key='company_prefix')
        return f"{company_prefix}.{name.lower()}"
    
    def create_package_structure(self, base_path, name, display_name, description, create_samples=True, 
                                create_runtime=True, create_editor=True, create_tests=True,
                                create_github=True, create_license="MIT"):
        try:
            if not os.path.exists(base_path):
                os.makedirs(base_path)
                self.log(f"📁 Diretório principal criado: {base_path}")
            
            self.update_progress(10, "Iniciando criação do pacote...")
            
            self._create_file(os.path.join(base_path, "package.json"), 
                             json.dumps(self.get_package_json(name, display_name, description), indent=2))
            
            self.update_progress(20, "Criando arquivo package.json...")
            
            self._create_file(os.path.join(base_path, "README.md"), 
                f"# {display_name}\n\n{description}\n\n## 📥 Instalação\n\n" +
                f"Este pacote pode ser instalado através do Unity Package Manager.\n\n" +
                f"1. Abra o Package Manager (Window > Package Manager)\n" +
                f"2. Clique no botão + e selecione \"Add package from git URL...\"\n" +
                f"3. Digite: https://github.com/Natteens/{name}.git\n\n" +
                f"## 🚀 Uso\n\n*Documentação em desenvolvimento*\n")
            
            self._create_file(os.path.join(base_path, "CHANGELOG.md"), 
                f"# 📝 Changelog\n\nTodos os lançamentos notáveis serão documentados neste arquivo.\n\n" +
                f"O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).\n\n" +
                f"## [Não lançado]\n\n### Adicionado\n- ✨ Estrutura inicial do pacote\n")

            if create_license: self._create_license_file(base_path, create_license, name, display_name)
            self.update_progress(30, "Criando arquivos de documentação...")

            if create_runtime: self._create_assembly_structure(base_path, name, "Runtime", False)
            if create_editor: self._create_assembly_structure(base_path, name, "Editor", True)
            self.update_progress(40, "Criando estrutura de código...")
            
            docs_path = os.path.join(base_path, "Documentation~")
            os.makedirs(docs_path, exist_ok=True)
            self._create_file(os.path.join(docs_path, "index.md"),
                f"# 📚 {display_name}\n\n{description}\n\n## 🚀 Início Rápido\n\n*Em desenvolvimento*\n")
            
            self.update_progress(50, "Criando documentação...")
            
            if create_samples: self._create_samples(base_path, name, display_name)
            self.update_progress(70, "Criando exemplos...")
            
            if create_tests: self._create_tests(base_path, name)
            self.update_progress(80, "Criando estrutura de testes...")
            
            if create_github: self._create_github_files(base_path)
            
            self.config.set_value(key='last_directory', value=os.path.dirname(base_path))
            
            self.update_progress(100, "✅ Pacote criado com sucesso!")
            self.log("✅ Pacote criado com sucesso!")
            return True
            
        except Exception as e:
            self.update_progress(100, f"❌ Erro: {str(e)}")
            self.log(f"❌ Erro ao criar pacote: {str(e)}")
            return False
    
    def _create_file(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f: f.write(content)
        self.log(f"📄 Arquivo criado: {os.path.basename(path)}")
    
    def _create_assembly_structure(self, base_path, package_name, folder_type, is_editor):
        folder_path = os.path.join(base_path, folder_type)
        os.makedirs(folder_path, exist_ok=True)
        
        company_prefix = self.config.get_value(key='company_prefix')
        assembly_name = f"{company_prefix}.{package_name.lower()}" + (".editor" if is_editor else "")
            
        asmdef = {"name": assembly_name, "rootNamespace": f"Natteens.{package_name}", "references": []}
        
        if is_editor:
            asmdef["references"].append(f"{company_prefix}.{package_name.lower()}")
            asmdef["includePlatforms"] = ["Editor"]
        
        self._create_file(os.path.join(folder_path, f"{assembly_name}.asmdef"), json.dumps(asmdef, indent=2))
        
        if is_editor:
            self._create_file(os.path.join(folder_path, f"{package_name}Editor.cs"),
                f"using UnityEngine;\nusing UnityEditor;\n\nnamespace Natteens.{package_name}\n{{\n" +
                f"    /// <summary>\n    /// Editor para {package_name}\n    /// </summary>\n" +
                f"    public class {package_name}Editor : Editor\n    {{\n        " +
                f"// Implementação futura\n    }}\n}}\n")
        else:
            self._create_file(os.path.join(folder_path, f"{package_name}Manager.cs"),
                f"using UnityEngine;\n\nnamespace Natteens.{package_name}\n{{\n" +
                f"    /// <summary>\n    /// Gerenciador principal para {package_name}\n    /// </summary>\n" +
                f"    public class {package_name}Manager : MonoBehaviour\n    {{\n" +
                f"        private static {package_name}Manager _instance;\n\n" +
                f"        /// <summary>\n        /// Instância singleton do gerenciador\n        /// </summary>\n" +
                f"        public static {package_name}Manager Instance\n        {{\n" +
                f"            get\n            {{\n                if (_instance == null)\n" +
                f"                {{\n                    _instance = FindObjectOfType<{package_name}Manager>();\n" +
                f"                    if (_instance == null)\n                    {{\n" +
                f"                        GameObject go = new GameObject(\"{package_name}Manager\");\n" +
                f"                        _instance = go.AddComponent<{package_name}Manager>();\n" +
                f"                        DontDestroyOnLoad(go);\n                    }}\n" +
                f"                }}\n                return _instance;\n            }}\n        }}\n\n" +
                f"        private void Awake()\n        {{\n            if (_instance != null && _instance != this)\n" +
                f"            {{\n                Destroy(gameObject);\n                return;\n            }}\n\n" +
                f"            _instance = this;\n            DontDestroyOnLoad(gameObject);\n            " +
                f"// Inicialização\n        }}\n    }}\n}}\n")
    
    def _create_samples(self, base_path, name, display_name):
        samples_path = os.path.join(base_path, "Samples~")
        
        sample_dirs = ["2D Sample", "3D Sample", "Utilities Sample"]
        for sample_dir in sample_dirs:
            sample_path = os.path.join(samples_path, sample_dir)
            os.makedirs(sample_path, exist_ok=True)
            self._create_file(os.path.join(sample_path, "README.md"),
                f"# 🎮 {sample_dir}\n\nExemplo para o pacote {display_name}.\n\n" +
                f"## 🚀 Como usar\n\nImporte este exemplo através do Unity Package Manager.\n")
    
    def _create_tests(self, base_path, name):
        tests_path = os.path.join(base_path, "Tests")
        os.makedirs(tests_path, exist_ok=True)
        
        runtime_test_path = os.path.join(tests_path, "Runtime")
        editor_test_path = os.path.join(tests_path, "Editor")
        
        os.makedirs(runtime_test_path, exist_ok=True)
        os.makedirs(editor_test_path, exist_ok=True)
        
        company_prefix = self.config.get_value(key='company_prefix')
        runtime_asmdef = {
            "name": f"{company_prefix}.{name.lower()}.tests", "rootNamespace": f"Natteens.{name}.Tests",
            "references": [f"{company_prefix}.{name.lower()}", "UnityEngine.TestRunner", "UnityEditor.TestRunner"],
            "includePlatforms": [], "excludePlatforms": [], "allowUnsafeCode": False,
            "overrideReferences": True, "precompiledReferences": ["nunit.framework.dll"],
            "autoReferenced": False, "defineConstraints": ["UNITY_INCLUDE_TESTS"],
            "versionDefines": [], "noEngineReferences": False
        }
        
        editor_asmdef = dict(runtime_asmdef)
        editor_asmdef["name"] = f"{company_prefix}.{name.lower()}.editor.tests"
        editor_asmdef["rootNamespace"] = f"Natteens.{name}.Editor.Tests"
        editor_asmdef["references"].append(f"{company_prefix}.{name.lower()}.editor")
        editor_asmdef["includePlatforms"] = ["Editor"]
        
        self._create_file(os.path.join(runtime_test_path, f"{company_prefix}.{name.lower()}.tests.asmdef"),
                         json.dumps(runtime_asmdef, indent=2))
        
        self._create_file(os.path.join(editor_test_path, f"{company_prefix}.{name.lower()}.editor.tests.asmdef"),
                         json.dumps(editor_asmdef, indent=2))
        
        self._create_file(os.path.join(runtime_test_path, f"{name}Tests.cs"),
            f"using System.Collections;\nusing NUnit.Framework;\nusing UnityEngine;\nusing UnityEngine.TestTools;\n" +
            f"using Natteens.{name};\n\nnamespace Natteens.{name}.Tests\n{{\n" +
            f"    public class {name}Tests\n    {{\n" +
            f"        [Test]\n        public void BasicTest()\n        {{\n" +
            f"            // Arrange\n            // Act\n            // Assert\n" +
            f"            Assert.IsTrue(true);\n        }}\n\n" +
            f"        [UnityTest]\n        public IEnumerator AsyncTest()\n        {{\n" +
            f"            // Teste assíncrono\n            yield return null;\n" +
            f"            Assert.IsTrue(true);\n        }}\n    }}\n}}\n")
        
        self._create_file(os.path.join(editor_test_path, f"{name}EditorTests.cs"),
            f"using System.Collections;\nusing NUnit.Framework;\nusing UnityEngine;\nusing UnityEditor;\n" +
            f"using UnityEngine.TestTools;\nusing Natteens.{name};\n\n" +
            f"namespace Natteens.{name}.Editor.Tests\n{{\n" +
            f"    public class {name}EditorTests\n    {{\n" +
            f"        [Test]\n        public void EditorTest()\n        {{\n" +
            f"            // Arrange\n            // Act\n            // Assert\n" +
            f"            Assert.IsTrue(true);\n        }}\n    }}\n}}\n")
    
    def _create_github_files(self, base_path):
        workflows_path = os.path.join(base_path, ".github", "workflows")
        os.makedirs(workflows_path, exist_ok=True)
        
        self._create_file(os.path.join(workflows_path, "release.yml"),
            """name: CI

on:
  push:
    branches:
      - main

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies (no lock)
        run: npm install --no-package-lock

      - name: Release
        uses: cycjimmy/semantic-release-action@v4
        with:
          extra_plugins: |
            @semantic-release/changelog
            @semantic-release/git
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
""")
        
        self._create_file(os.path.join(workflows_path, "test.yml"),
            """name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        
      - name: Setup Unity
        uses: game-ci/unity-test-runner@v2
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          projectPath: .
          testMode: all
          artifactsPath: Test-results
          coveragePath: Coverage-results
          
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: Test results
          path: Test-results
""")
        
        self._create_file(os.path.join(base_path, ".releaserc"),
            json.dumps({
                "branches": ["main"],
                "plugins": [
                    "@semantic-release/commit-analyzer", "@semantic-release/release-notes-generator",
                    "@semantic-release/changelog", ["@semantic-release/npm", {"npmPublish": False}],
                    ["@semantic-release/git", {"assets": ["package.json", "CHANGELOG.md"], 
                     "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"}],
                    "@semantic-release/github"
                ]
            }, indent=2))
        
        self._create_file(os.path.join(base_path, ".gitignore"),
            """# Unity generated
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/

# Unity3D generated meta files
*.pidb.meta
*.pdb.meta
*.mdb.meta

# VS Code
.vscode/

# Visual Studio
.vs/
*.sln
*.csproj
*.suo
*.user
*.userprefs
*.pidb
*.booproj

# Rider
.idea/
*.sln.iml

# Project-specific
node_modules/
package-lock.json
""")
        
    def _create_license_file(self, base_path, license_type, name, display_name):
        year = datetime.now().year
        author_name = self.config.get_value(key='author_name')
        
        if license_type == "MIT":
            license_content = f"""MIT License

Copyright (c) {year} {author_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        elif license_type == "Apache-2.0":
            license_content = f"""                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Copyright (c) {year} {author_name}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
        else: 
            license_content = f"""Copyright (c) {year} {author_name}

Este software e arquivos associados são propriedade de {author_name}.
Todos os direitos reservados.

O uso deste software é restrito e sujeito a termos de licenciamento.
"""
            
        self._create_file(os.path.join(base_path, "LICENSE.md"), license_content)

class PackageGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unity Package Generator")
        self.root.geometry("840x700")
        self.root.resizable(True, True)
        
        self.config_manager = ConfigManager()
        self.package_generator = PackageGenerator(self.config_manager)
        self.package_generator.set_log_callback(self.log)
        self.package_generator.set_progress_callback(self.update_progress)
        self.github_manager = GitHubManager(self.config_manager)
        
        self.package_name_var = tk.StringVar()
        self.display_name_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.output_path_var = tk.StringVar(value=self.config_manager.get_value(key='last_directory'))
        self.create_samples_var = tk.BooleanVar(value=True)
        self.create_runtime_var = tk.BooleanVar(value=True)
        self.create_editor_var = tk.BooleanVar(value=True)
        self.create_tests_var = tk.BooleanVar(value=True)
        self.create_github_var = tk.BooleanVar(value=True)
        self.license_var = tk.StringVar(value="MIT")
        self.create_github_repo_var = tk.BooleanVar(value=False)
        self.repo_private_var = tk.BooleanVar(value=False)
        self.progress_value = tk.DoubleVar(value=0)
        self.progress_text = tk.StringVar(value="")
        
        self.setup_styles()
        self.create_widgets()
        self.check_github_connection()
    
    def setup_styles(self):
        self.style = ttk.Style()
        default_font = ('Arial', 12)
        header_font = ('Arial', 16, 'bold')
        
        self.style.configure('TFrame', background=COLORS["bg"])
        self.style.configure('TLabel', background=COLORS["bg"], foreground=COLORS["fg"], font=default_font)
        
        self.style.configure('TButton', font=default_font, foreground='#000000')
        
        self.style.configure('TCheckbutton', background=COLORS["bg"], foreground=COLORS["fg"], font=default_font)
        self.style.configure('TNotebook', background=COLORS["bg"])
        self.style.configure('TNotebook.Tab', padding=[10, 3], font=default_font)
        
        self.style.configure('Accent.TButton', background=COLORS["accent"], foreground='#000000', font=default_font)
        
        self.style.configure('Title.TLabel', font=header_font)
        self.style.configure('Horizontal.TProgressbar', background=COLORS["accent"])
    
    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="✨ Unity Package Generator", style='Title.TLabel').pack(side=tk.LEFT)
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        basic_frame = ttk.Frame(self.notebook, padding=10)
        github_frame = ttk.Frame(self.notebook, padding=10)
        advanced_frame = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(basic_frame, text="📋 Básico")
        self.notebook.add(github_frame, text="🌐 GitHub")
        self.notebook.add(advanced_frame, text="⚙️ Avançado")
        
        self.create_basic_tab(basic_frame)
        self.create_github_tab(github_frame)
        self.create_advanced_tab(advanced_frame)
        
        progress_frame = ttk.Frame(self.main_frame, padding=(0, 10, 0, 0))
        progress_frame.pack(fill=tk.X, padx=5)
        
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_text)
        self.progress_label.pack(fill=tk.X, side=tk.TOP, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_value, mode="determinate")
        self.progress_bar.pack(fill=tk.X)
        
        log_frame = ttk.LabelFrame(self.main_frame, text="📜 Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, font=('Consolas', 11))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(bg=COLORS["log_bg"], fg=COLORS["log_fg"], state=tk.DISABLED)
        
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(status_frame, text="v2.0.0", anchor=tk.E).pack(side=tk.RIGHT)
    
    def create_basic_tab(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Informações do Pacote", padding=10)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Nome interno:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.package_name_var, width=40, font=('Arial', 12)).grid(
            row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(form_frame, text="Ex: statusforge").grid(row=0, column=2, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Nome de exibição:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.display_name_var, width=40, font=('Arial', 12)).grid(
            row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(form_frame, text="Ex: Status Forge").grid(row=1, column=2, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Descrição:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.description_var, width=40, font=('Arial', 12)).grid(
            row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Pasta base:").grid(row=3, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(form_frame)
        path_frame.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.output_path_var, font=('Arial', 12)).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="📁", width=3, command=self.select_path).pack(side=tk.RIGHT)
        
        form_frame.columnconfigure(1, weight=1)
        
        prefix_frame = ttk.Frame(parent)
        prefix_frame.pack(fill=tk.X, padx=5, pady=10)
        company_prefix = self.config_manager.get_value(key='company_prefix')
        ttk.Label(prefix_frame, text=f"Prefixo da empresa: {company_prefix}").pack(side=tk.LEFT)
        
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(preview_frame, text="Nome completo do pacote:").pack(side=tk.LEFT)
        
        self.preview_name_var = tk.StringVar(value=f"{company_prefix}.nomedopacote")
        ttk.Label(preview_frame, textvariable=self.preview_name_var, font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        
        def update_preview(*args):
            name = self.package_name_var.get().strip().lower()
            if name: self.preview_name_var.set(f"{company_prefix}.{name}")
            else: self.preview_name_var.set(f"{company_prefix}.nomedopacote")
        
        self.package_name_var.trace_add("write", update_preview)
        
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(buttons_frame, text="🚀 Gerar Pacote", command=self.generate_package, 
                  style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="⚙️ Configurações", command=self.show_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="🧹 Limpar", command=self.clear_form).pack(side=tk.RIGHT, padx=5)
    
    def create_github_tab(self, parent):
        github_status_frame = ttk.Frame(parent, padding=5)
        github_status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.github_status_var = tk.StringVar(value="Verificando conexão com GitHub...")
        self.github_status_label = ttk.Label(github_status_frame, textvariable=self.github_status_var)
        self.github_status_label.pack(side=tk.LEFT, pady=5)
        
        ttk.Button(github_status_frame, text="🔄 Configurar GitHub", command=self.configure_github).pack(side=tk.RIGHT)
        
        repo_frame = ttk.LabelFrame(parent, text="Opções de Repositório", padding=10)
        repo_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Checkbutton(repo_frame, text="Criar repositório no GitHub após a geração do pacote", 
                       variable=self.create_github_repo_var).grid(row=0, column=0, sticky=tk.W, pady=5, columnspan=2)
        
        ttk.Checkbutton(repo_frame, text="Repositório privado", 
                       variable=self.repo_private_var).grid(row=1, column=0, sticky=tk.W, pady=5)
    
    def create_advanced_tab(self, parent):
        options_frame = ttk.LabelFrame(parent, text="Componentes a Criar", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Criar exemplos (Samples)", 
                       variable=self.create_samples_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Criar pasta Runtime", 
                       variable=self.create_runtime_var).grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Criar pasta Editor", 
                       variable=self.create_editor_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Criar testes", 
                       variable=self.create_tests_var).grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Criar arquivos GitHub", 
                       variable=self.create_github_var).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        license_frame = ttk.Frame(options_frame)
        license_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(license_frame, text="Licença:").pack(side=tk.LEFT)
        license_combo = ttk.Combobox(license_frame, textvariable=self.license_var, width=15, font=('Arial', 12))
        license_combo['values'] = ('MIT', 'Apache-2.0', 'Proprietária')
        license_combo.pack(side=tk.LEFT, padx=5)
        
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
            
    def select_path(self):
        path = filedialog.askdirectory(initialdir=self.output_path_var.get())
        if path: self.output_path_var.set(path)
    
    def check_github_connection(self):
        def check():
            connected = self.github_manager.check_credentials()
            if connected:
                self.github_status_var.set(f"✅ Conectado ao GitHub como: {self.github_manager.username}")
                self.github_status_label.configure(foreground=COLORS["success"])
            else:
                if self.github_manager.is_configured():
                    self.github_status_var.set("❌ Credenciais do GitHub inválidas. Reconfigure.")
                else:
                    self.github_status_var.set("❌ Não conectado ao GitHub. Configure suas credenciais.")
                self.github_status_label.configure(foreground=COLORS["error"])
        
        threading.Thread(target=check).start()
            
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def update_progress(self, value, message=""):
        self.progress_value.set(value)
        self.progress_text.set(message)
        self.root.update_idletasks()
        
    def validate_form(self):
        if not self.package_name_var.get().strip():
            messagebox.showerror("Erro", "Nome interno do pacote é obrigatório")
            return False
        if not self.display_name_var.get().strip():
            messagebox.showerror("Erro", "Nome de exibição é obrigatório")
            return False
        if not self.description_var.get().strip():
            messagebox.showerror("Erro", "Descrição é obrigatória")
            return False
        if not self.output_path_var.get().strip():
            messagebox.showerror("Erro", "Caminho de saída é obrigatório")
            return False
        if self.create_github_repo_var.get() and not self.github_manager.check_credentials():
            messagebox.showerror("Erro", "Credenciais do GitHub inválidas ou não configuradas")
            return False
        return True
        
    def generate_package(self):
        if not self.validate_form(): return
            
        self.status_var.set("Gerando pacote...")
        self.clear_log()
        self.update_progress(0, "Iniciando geração do pacote...")
        
        try:
            name = self.package_name_var.get().strip()
            display_name = self.display_name_var.get().strip()
            description = self.description_var.get().strip()
            
            full_package_name = self.package_generator.get_full_package_name(name)
            
            base_path = os.path.join(self.output_path_var.get().strip(), full_package_name)
            
            self.log(f"🚀 Iniciando geração do pacote '{display_name}'...")
            self.log(f"📁 Caminho de destino: {base_path}")
            
            if os.path.exists(base_path) and os.listdir(base_path):
                if not messagebox.askyesno("Aviso", f"A pasta '{full_package_name}' já existe. Sobrescrever?"):
                    self.status_var.set("Operação cancelada")
                    return

            repo_url = None
            if self.create_github_repo_var.get():
                self.update_progress(10, "Criando repositório no GitHub...")
                self.log("🌐 Criando repositório no GitHub...")
                
                response = self.github_manager.create_repository(
                    name, description, self.repo_private_var.get(), auto_init=False)
                
                if "error" in response:
                    self.log(f"❌ Erro: {response['error']}")
                    messagebox.showerror("Erro GitHub", f"Não foi possível criar o repositório: {response['error']}")
                    self.status_var.set("Erro ao criar repositório GitHub")
                    return

                repo_url = response["html_url"]
                clone_url = response["clone_url"]
                self.log(f"✅ Repositório criado: {repo_url}")
            
            success = self.package_generator.create_package_structure(
                base_path=base_path, name=name, display_name=display_name, description=description,
                create_samples=self.create_samples_var.get(), create_runtime=self.create_runtime_var.get(),
                create_editor=self.create_editor_var.get(), create_tests=self.create_tests_var.get(),
                create_github=self.create_github_var.get(), create_license=self.license_var.get()
            )
            
            if success:
                self.status_var.set("Pacote gerado com sucesso!")
                
                if self.create_github_repo_var.get() and repo_url:
                    def on_git_progress(success, message, progress=None):
                        self.log("✅ " + message if success else "❌ " + message)
                        if progress is not None:
                            self.update_progress(60 + (progress * 0.4), message)
                            
                        if progress == 100:
                            self.update_progress(100, "✅ Processo concluído!")
                            if messagebox.askyesno("Sucesso", 
                                f"Pacote gerado e enviado para o GitHub!\n\nRepositório: {repo_url}\n\n"
                                f"Deseja abrir o repositório no navegador?"):
                                webbrowser.open(repo_url)
                    
                    self.update_progress(60, "Configurando Git...")
                    self.log("🔄 Configurando repositório Git e enviando para o GitHub...")
                    self.github_manager.setup_repository(base_path, name, clone_url, on_git_progress)
                else:
                    if messagebox.askyesno("Sucesso", "Pacote gerado com sucesso! Deseja abrir a pasta?"):
                        self.open_folder(base_path)
            else:
                self.status_var.set("Erro na geração do pacote")
                
        except Exception as e:
            self.log(f"❌ Erro: {str(e)}")
            self.status_var.set("Erro na geração do pacote")
            messagebox.showerror("Erro", f"Erro ao gerar o pacote: {str(e)}")
    
    def configure_github(self):
        github_window = tk.Toplevel(self.root)
        github_window.title("Configurar GitHub")
        github_window.geometry("500x300")
        github_window.transient(self.root)
        github_window.grab_set()
        
        main_frame = ttk.Frame(github_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        github_username_var = tk.StringVar(value=self.github_manager.username)
        github_token_var = tk.StringVar(value=self.github_manager.token)
        
        ttk.Label(main_frame, text="Configurações do GitHub", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        ttk.Label(main_frame, text="Configure seu token de acesso pessoal do GitHub.", 
                 wraplength=450).pack(pady=(0, 10))
        
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Nome de usuário:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=github_username_var, width=40, font=('Arial', 12)).grid(
            row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Token de Acesso:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=github_token_var, width=40, font=('Arial', 12), show="•").grid(
            row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="🌐 Abrir página de tokens", 
                  command=lambda: webbrowser.open("https://github.com/settings/tokens")).pack(side=tk.LEFT)
        
        def save_github_settings():
            username = github_username_var.get().strip()
            token = github_token_var.get().strip()
            if not username or not token:
                messagebox.showerror("Erro", "Nome de usuário e token são obrigatórios")
                return
            
            self.config_manager.set_value(section='github', key='username', value=username)
            self.config_manager.set_value(section='github', key='token', value=token)
            self.github_manager.username = username
            self.github_manager.token = token
            
            github_window.destroy()
            self.github_status_var.set("Verificando conexão com GitHub...")
            self.check_github_connection()
            messagebox.showinfo("GitHub", "Configurações do GitHub salvas com sucesso!")
            
        ttk.Button(buttons_frame, text="💾 Salvar", command=save_github_settings).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="❌ Cancelar", command=github_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("500x350")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        settings_frame = ttk.Frame(settings_window, padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        author_name_var = tk.StringVar(value=self.config_manager.get_value(key='author_name'))
        author_email_var = tk.StringVar(value=self.config_manager.get_value(key='author_email'))
        author_url_var = tk.StringVar(value=self.config_manager.get_value(key='author_url'))
        unity_version_var = tk.StringVar(value=self.config_manager.get_value(key='unity_version'))
        company_prefix_var = tk.StringVar(value=self.config_manager.get_value(key='company_prefix'))
        
        ttk.Label(settings_frame, text="Nome do Autor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=author_name_var, width=40, font=('Arial', 12)).grid(
            row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Email do Autor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=author_email_var, width=40, font=('Arial', 12)).grid(
            row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="URL do Autor:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=author_url_var, width=40, font=('Arial', 12)).grid(
            row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Versão do Unity:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=unity_version_var, width=40, font=('Arial', 12)).grid(
            row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Prefixo da Empresa:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=company_prefix_var, width=40, font=('Arial', 12)).grid(
            row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
        def save_settings():
            self.config_manager.set_value(key='author_name', value=author_name_var.get())
            self.config_manager.set_value(key='author_email', value=author_email_var.get())
            self.config_manager.set_value(key='author_url', value=author_url_var.get())
            self.config_manager.set_value(key='unity_version', value=unity_version_var.get())
            self.config_manager.set_value(key='company_prefix', value=company_prefix_var.get())
            
            company_prefix = company_prefix_var.get()
            name = self.package_name_var.get().strip().lower()
            if name: self.preview_name_var.set(f"{company_prefix}.{name}")
            else: self.preview_name_var.set(f"{company_prefix}.nomedopacote")
                
            settings_window.destroy()
            messagebox.showinfo("Configurações", "Configurações salvas com sucesso!")
            
        ttk.Button(settings_frame, text="💾 Salvar", command=save_settings).grid(row=5, column=1, sticky=tk.E, pady=10)
        
    def clear_form(self):
        self.package_name_var.set("")
        self.display_name_var.set("")
        self.description_var.set("")
        self.create_github_repo_var.set(False)
        self.repo_private_var.set(False)
        self.clear_log()
        self.status_var.set("Pronto")
        self.update_progress(0, "")
        
    def open_folder(self, path):
        try:
            if os.name == 'nt': os.startfile(path)  # Windows
            elif os.name == 'posix':
                if sys.platform == 'darwin': subprocess.call(["open", path])  # Mac
                else: subprocess.call(["xdg-open", path])  # Linux
        except Exception as e: self.log(f"Erro ao abrir pasta: {e}")


def main():
    root = tk.Tk()
    root.title("Unity Package Generator")
    app = PackageGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()