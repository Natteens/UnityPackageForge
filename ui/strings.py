# Licenses
LICENSE_MIT = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "{package}"), to deal
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
SOFTWARE."""

# UI Constants - Interface
APP_TITLE = "Unity Package Forge"
APP_TITLE_WITH_EMOJI = "🚀 Unity Package Forge"
APP_SUBTITLE = "Gerador profissional de pacotes Unity com integração GitHub"
APP_GEOMETRY = "900x850"
APP_MIN_SIZE = (900, 850)
APP_APPEARANCE_MODE = "dark"
APP_COLOR_THEME = "blue"

# Default Values
DEFAULT_VERSION = "0.1.0"
DEFAULT_COMPANY_PREFIX = "com.companyname"
DEFAULT_UNITY_VERSION = "2021.3"
DEFAULT_LICENSE_TYPE = "MIT"
DEFAULT_USERNAME_PLACEHOLDER = "seuusuario"

# Tab Names
TAB_PACKAGE = "📦 Pacote"
TAB_CONFIG = "⚙️ Configurações"
TAB_GITHUB = "🐙 GitHub"
TAB_DEPENDENCIES = "🔧 Dependências"
TAB_DEBUG = "🐛 Debug"
TAB_ABOUT = "ℹ️ Sobre"

# Section Titles
SECTION_PACKAGE_INFO = "📋 Informações do Pacote"
SECTION_PACKAGE_STRUCTURE = "🏗️ Estrutura do Pacote"
SECTION_LICENSE = "📄 Licença"
SECTION_AUTHOR_INFO = "👤 Informações do Autor"
SECTION_UNITY_CONFIG = "🎮 Configurações Unity"
SECTION_GITHUB_CREDENTIALS = "🔑 Credenciais GitHub"
SECTION_CREATE_REPOSITORY = "🚀 Criar Repositório"
SECTION_GITHUB_INSTRUCTIONS = "📋 Como obter um Token"
SECTION_UNITY_DEPENDENCIES = "📦 Dependências Unity"
SECTION_CUSTOM_DEPENDENCY = "➕ Dependência Personalizada"
SECTION_DEBUG_LOG = "📝 Log de Atividades"
SECTION_USEFUL_LINKS = "🔗 Links Úteis"

# Field Labels
LABEL_DISPLAY_NAME = "🏷️ Nome de Exibição:"
LABEL_DESCRIPTION = "📝 Descrição:"
LABEL_VERSION = "🏷️ Versão Inicial:"
LABEL_DESTINATION_FOLDER = "📁 Pasta de Destino:"
LABEL_AUTHOR_NAME = "👤 Nome:"
LABEL_AUTHOR_EMAIL = "📧 Email:"
LABEL_AUTHOR_URL = "🌐 URL do Perfil:"
LABEL_COMPANY_PREFIX = "🏢 Prefixo da Empresa:"
LABEL_UNITY_VERSION = "🎮 Versão Unity:"
LABEL_GITHUB_USERNAME = "👤 Usuário:"
LABEL_GITHUB_TOKEN = "🔑 Token:"
LABEL_LICENSE_TYPE = "Tipo:"
LABEL_PACKAGE_ID = "Package ID:"
LABEL_VERSION_SHORT = "Versão:"

# Placeholders
PLACEHOLDER_DISPLAY_NAME = "Meu Incrível Pacote"
PLACEHOLDER_DESCRIPTION = "Uma descrição clara do que o pacote faz..."
PLACEHOLDER_VERSION = "0.1.0"
PLACEHOLDER_FOLDER = "Selecione a pasta Packages do seu projeto Unity..."
PLACEHOLDER_AUTHOR_NAME = "Seu Nome Completo"
PLACEHOLDER_AUTHOR_EMAIL = "seu@email.com"
PLACEHOLDER_AUTHOR_URL = "https://github.com/seuusuario"
PLACEHOLDER_COMPANY_PREFIX = "com.suaempresa"
PLACEHOLDER_GITHUB_USERNAME = "seuusuario"
PLACEHOLDER_GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
PLACEHOLDER_LICENSE_PATH = "Caminho para arquivo de licença..."
PLACEHOLDER_CUSTOM_DEPENDENCY = "com.exemplo.pacote"
PLACEHOLDER_CUSTOM_VERSION = "1.0.0"

# Info Messages
INFO_DISPLAY_NAME = "💡 Nome usado no repositório GitHub e como base para tudo"
INFO_FOLDER_RECOMMENDATION = "💡 Recomendado: Pasta 'Packages' do seu projeto Unity para teste direto"
INFO_URL_AUTO_GENERATED = "📋 URL será gerada automaticamente"

# Checkbox Options
CHECKBOX_SAMPLES = "📦 Samples"
CHECKBOX_RUNTIME = "⚡ Runtime"
CHECKBOX_EDITOR = "🛠️ Editor"
CHECKBOX_TESTS = "🧪 Tests"
CHECKBOX_GITHUB_ACTIONS = "🐙 GitHub Actions"
CHECKBOX_CREATE_REPO = "🚀 Criar repositório no GitHub automaticamente"
CHECKBOX_PRIVATE_REPO = "🔒 Repositório privado"

# License Types
LICENSE_TYPES = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "Unlicense", "Personalizada"]

# Unity Versions
UNITY_VERSIONS = ["2021.3", "2022.3", "2023.1", "2023.2", "2023.3", "6000.0"]

# Button Texts
BUTTON_GENERATE_PACKAGE = "🚀 Gerar Pacote Unity"
BUTTON_SAVE_CONFIG = "💾 Salvar Configurações"
BUTTON_VERIFY_CREDENTIALS = "✅"
BUTTON_SELECT_FOLDER = "📁"
BUTTON_SELECT_LICENSE = "📂"
BUTTON_ADD_DEPENDENCY = "➕"
BUTTON_CLEAR_LOG = "🗑️ Limpar"
BUTTON_SAVE_LOG = "💾 Salvar"
BUTTON_TEST_GITHUB = "🧪 Testar GitHub"
BUTTON_GITHUB_LINK = "🐙 GitHub"
BUTTON_UNITY_DOCS_LINK = "🎮 Unity Docs"

# Progress Messages
PROGRESS_STARTING = "Iniciando criação do pacote..."
PROGRESS_PACKAGE_JSON = "Arquivo package.json criado..."
PROGRESS_FOLDER_STRUCTURE = "Estrutura de pastas criada..."
PROGRESS_TESTS_CREATED = "Estrutura de testes criada..."
PROGRESS_SAMPLES_CREATED = "Amostras criadas..."
PROGRESS_DOCUMENTATION = "Documentação criada..."
PROGRESS_LICENSE_CREATED = "Licença criada..."
PROGRESS_GITHUB_FILES = "Arquivos GitHub criados..."
PROGRESS_COMPLETED = "Concluído!"
PROGRESS_PACKAGE_SUCCESS = "Pacote criado com sucesso!"

# Log Messages
LOG_DIRECTORY_CREATED = "📁 Diretório principal criado: {path}"
LOG_DIRECTORY_EXISTING = "📁 Utilizando diretório existente: {path}"
LOG_RUNTIME_CREATED = "📁 Pasta Runtime criada com .asmdef"
LOG_EDITOR_CREATED = "📁 Pasta Editor criada com .asmdef"
LOG_TESTS_CREATED = "🧪 Estrutura de testes criada"
LOG_SAMPLES_CREATED = "📦 Estrutura de amostras criada"
LOG_DOCUMENTATION_CREATED = "📝 Documentação criada"
LOG_LICENSE_CREATED = "📄 Licença MIT criada"
LOG_GITHUB_FILES_CREATED = "🔧 Arquivos GitHub criados"
LOG_DEPENDENCY_ADDED = "📦 Dependência adicionada: {name} v{version}"
LOG_PACKAGE_SUCCESS = "✅ Pacote '{name}' criado com sucesso em: {path}"
LOG_LOG_SAVED = "💾 Log salvo em: {filename}"
LOG_TESTING_GITHUB = "🧪 Testando conexão com GitHub..."

# Error Messages
ERROR_DISPLAY_NAME_REQUIRED = "❌ Nome de exibição é obrigatório"
ERROR_FOLDER_REQUIRED = "❌ Pasta de destino é obrigatória"
ERROR_PACKAGE_CREATION = "❌ Erro ao criar pacote: {error}"
ERROR_GITHUB_SETUP = "❌ Erro no GitHub: {error}"
ERROR_APP_INITIALIZATION = "Erro ao inicializar a aplicação: {error}"
ERROR_ICON_LOAD = "Não foi possível carregar o ícone: {error}"
ERROR_VERSION_EXTRACT = "Erro ao extrair versão: {error}"
ERROR_PATH_NOT_EXISTS = "Path does not exist: {path}"

# Success Messages
SUCCESS_CONFIG_SAVED = "✅ Configurações salvas com sucesso!"
SUCCESS_PACKAGE_CREATED = "✅ Pacote criado com sucesso!\nDeseja abrir a pasta?"
SUCCESS_AUTHENTICATED = "Autenticado como {username}"
SUCCESS_REPO_CREATED = "Repositório '{repo_name}' criado e configurado com sucesso!"

# Warning Messages
WARNING_GITHUB_NOT_CONFIGURED = "⚠️ Credenciais GitHub não configuradas - repositório não criado"
WARNING_CREDENTIALS_NOT_SET = "Credenciais não configuradas"

# GitHub Messages
GITHUB_TOKEN_NOT_CONFIGURED = "Token de acesso GitHub não configurado"
GITHUB_REPO_EXISTS = "Repositório '{repo_name}' já existe"
GITHUB_HTTP_ERROR = "Erro HTTP {status}: {text}"
GITHUB_CREATION_ERROR = "Erro ao criar repositório: {error}"
GITHUB_SETUP_ERROR = "Erro na configuração: {error}"
GITHUB_GIT_ERROR = "Erro Git: {error}"

# Instructions
GITHUB_TOKEN_INSTRUCTIONS = """1. Acesse github.com/settings/tokens
2. "Generate new token (classic)"
3. Nome: "Unity Package Forge"
4. Permissões: repo, workflow
5. Copie o token gerado"""

# Dialog Titles
DIALOG_SELECT_FOLDER = "Selecionar pasta de destino"
DIALOG_SELECT_LICENSE = "Selecionar arquivo de licença"
DIALOG_SAVE_LOG = "Salvar Log"
DIALOG_SUCCESS = "Sucesso"
DIALOG_ERROR = "Erro"

# File Types
FILETYPES_LICENSE = [("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
FILETYPES_LOG = [("Log files", "*.log"), ("Text files", "*.txt")]

# URLs
URL_GITHUB_REPO = "https://github.com/Natteens/UnityPackageForge"
URL_UNITY_DOCS = "https://docs.unity3d.com/Manual/upm-ui.html"
URL_GITHUB_TOKENS = "github.com/settings/tokens"

# About Information
ABOUT_VERSION_INFO = """Unity Package Forge é uma ferramenta profissional para criar pacotes Unity
seguindo as melhores práticas e padrões da indústria.

✨ Funcionalidades:
• Geração automática de estrutura de pacotes
• Integração completa com GitHub
• Assembly Definitions com namespace correto
• Templates de documentação profissionais
• Semantic Release configurado
• Build automático multiplataforma

🔧 Versão: {version}
📅 Atualizado: {date}
👨‍💻 Desenvolvido por: Nathan da Silva Miranda

🌐 GitHub: github.com/Natteens/UnityPackageForge"""

# Dependencies List Labels
DEPS_AVAILABLE = "Dependências Disponíveis"
DEPS_SELECTED = "Dependências Selecionadas"
DEPS_NONE_SELECTED = "Nenhuma dependência selecionada"

# Status Messages
STATUS_GENERATING = "⏳ Gerando..."
STATUS_IDLE = ""

# Input Prompts
PROMPT_PRESS_ENTER = "Pressione Enter para sair..."

# Templates
README_TEMPLATE = """# {display_name}

{description}

## 📥 Instalação

Este pacote pode ser instalado através do Unity Package Manager usando a URL do Git.

### Via Package Manager (Recomendado)

1. Abra o Package Manager (Window > Package Manager)
2. Clique no botão **+** no canto superior esquerdo
3. Selecione **"Add package from git URL..."**
4. Digite a URL: `https://github.com/Natteens/{repo_name}.git`
5. Clique em **Add**

### Via manifest.json

Adicione a seguinte linha ao arquivo `Packages/manifest.json` do seu projeto:

```json
{{
  "dependencies": {{
    "com.example.{repo_name}": "https://github.com/Natteens/{repo_name}.git"
  }}
}}
```

## 🚀 Como Usar

*Documentação em desenvolvimento*

## 📝 Changelog

Veja o [CHANGELOG.md](CHANGELOG.md) para detalhes sobre mudanças e atualizações.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.
"""

CHANGELOG_TEMPLATE = """# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Não Lançado]

## [0.1.0] - {date}

### Adicionado
- ✨ Estrutura inicial do pacote Unity
- 📦 Configuração do Package Manager
- 📚 Documentação básica
- 🧪 Estrutura de testes
- 📋 Exemplos e amostras

### Mudado
- Nada ainda

### Removido
- Nada ainda

### Corrigido
- Nada ainda

---

Os tipos de mudanças são:
- **Adicionado** para novas funcionalidades
- **Mudado** para mudanças em funcionalidades existentes
- **Depreciado** para funcionalidades que serão removidas em breve
- **Removido** para funcionalidades removidas
- **Corrigido** para correções de bugs
- **Segurança** para vulnerabilidades
"""

# Sample folders info
SAMPLE_FOLDERS_INFO = {
    "Basic": """# {folder} Sample

Este é um exemplo básico para demonstrar o uso do {display_name}.

## Como usar

1. Importe esta amostra através do Package Manager
2. Abra a cena de exemplo
3. Execute para ver o {display_name} em ação

## Arquivos incluídos

- Cenas básicas de exemplo
- Prefabs simples
- Scripts de demonstração básicos
""",
    "Advanced": """# {folder} Sample

Este é um exemplo avançado para demonstrar recursos complexos do {display_name}.

## Como usar

1. Importe esta amostra através do Package Manager
2. Abra a cena de exemplo
3. Execute para ver funcionalidades avançadas

## Arquivos incluídos

- Cenas complexas
- Prefabs avançados
- Scripts com recursos completos
""",
    "Utilities": """# {folder} Sample

Utilitários e helpers para facilitar o uso do {display_name}.

## Como usar

1. Importe esta amostra através do Package Manager
2. Utilize os scripts utilitários em seus projetos
3. Consulte a documentação para detalhes específicos

## Arquivos incluídos

- Scripts utilitários
- Helpers e extensões
- Ferramentas de desenvolvimento
"""
}

# Unity Dependencies - Pacotes Unity comuns
UNITY_DEPENDENCIES = {
    "ui": {
        "com.unity.ui": "1.0.0"
    },
    "inputsystem": {
        "com.unity.inputsystem": "1.7.0"
    },
    "addressables": {
        "com.unity.addressables": "1.21.19"
    },
    "cinemachine": {
        "com.unity.cinemachine": "2.9.7"
    },
    "timeline": {
        "com.unity.timeline": "1.7.6"
    },
    "render-pipelines": {
        "com.unity.render-pipelines.universal": "14.0.9"
    },
    "textmeshpro": {
        "com.unity.textmeshpro": "3.0.6"
    },
    "postprocessing": {
        "com.unity.postprocessing": "3.2.2"
    }
}

# GitHub Workflow para Semantic Release
RELEASE_WORKFLOW = """name: Release

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
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install Semantic Release
        run: npm install -g semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/github @semantic-release/commit-analyzer @semantic-release/release-notes-generator

      - name: Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release
"""

# Configuração do Semantic Release
RELEASERC_JSON = """{{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      {{
        "changelogFile": "CHANGELOG.md"
      }}
    ],
    [
      "@semantic-release/github",
      {{
        "assets": [
          {{
            "path": "package.json",
            "label": "Unity Package Manifest"
          }}
        ]
      }}
    ],
    [
      "@semantic-release/git",
      {{
        "assets": ["package.json", "CHANGELOG.md"],
        "message": "chore(release): ${{nextRelease.version}} [skip ci]\\n\\n${{nextRelease.notes}}"
      }}
    ]
  ]
}}"""

# GitIgnore para Unity
GITIGNORE_UNITY = """# Unity generated files
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/

# Asset meta data should only be ignored when the corresponding asset is also ignored
!/[Aa]ssets/**/*.meta

# Uncomment this line if you wish to ignore the asset store tools plugin
# /[Aa]ssets/AssetStoreTools*

# Autogenerated Jetbrains Rider plugin
/[Aa]ssets/Plugins/Editor/JetBrains*

# Visual Studio cache directory
.vs/

# Gradle cache directory
.gradle/

# Autogenerated VS/MD/Consulo solution and project files
ExportedObj/
.consulo/
*.csproj
*.unityproj
*.sln
*.suo
*.tmp
*.user
*.userprefs
*.pidb
*.booproj
*.svd
*.pdb
*.mdb
*.opendb
*.VC.db

# Unity3D generated meta files
*.pidb.meta
*.pdb.meta
*.mdb.meta

# Unity3D generated file on crash reports
sysinfo.txt

# Builds
*.apk
*.aab
*.unitypackage

# Crashlytics generated file
crashlytics-build.properties

# Packed Addressables
/[Aa]ssets/[Aa]ddressable[Aa]ssets[Dd]ata/*/*.bin*

# Temporary auto-generated Android Assets
/[Aa]ssets/[Ss]treamingAssets/aa.meta
/[Aa]ssets/[Ss]treamingAssets/aa/*

# Node modules for semantic release
node_modules/
package-lock.json

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""

# Validation Messages
VALIDATION_PACKAGE_NAME_EMPTY = "Nome do pacote não pode estar vazio"
VALIDATION_PACKAGE_NAME_INVALID = "Nome do pacote contém caracteres inválidos"
VALIDATION_VERSION_INVALID = "Formato de versão inválido (use x.y.z)"
VALIDATION_FOLDER_NOT_EXISTS = "Pasta de destino não existe"
VALIDATION_GITHUB_TOKEN_INVALID = "Token GitHub inválido"
VALIDATION_AUTHOR_EMAIL_INVALID = "Email do autor inválido"

# File Extensions
FILE_EXT_ASMDEF = ".asmdef"
FILE_EXT_CS = ".cs"
FILE_EXT_JSON = ".json"
FILE_EXT_MD = ".md"
FILE_EXT_TXT = ".txt"
FILE_EXT_UNITY = ".unity"
FILE_EXT_PREFAB = ".prefab"
FILE_EXT_MAT = ".mat"

# Folder Names
FOLDER_RUNTIME = "Runtime"
FOLDER_EDITOR = "Editor"
FOLDER_TESTS = "Tests"
FOLDER_SAMPLES = "Samples~"
FOLDER_DOCUMENTATION = "Documentation~"
FOLDER_GITHUB = ".github"
FOLDER_WORKFLOWS = "workflows"

# File Names
FILE_PACKAGE_JSON = "package.json"
FILE_README = "README.md"
FILE_CHANGELOG = "CHANGELOG.md"
FILE_LICENSE = "LICENSE.md"
FILE_GITIGNORE = ".gitignore"
FILE_RELEASERC = ".releaserc.json"
FILE_RELEASE_WORKFLOW = "release.yml"

# Common Unity Package IDs
UNITY_PACKAGE_IDS = {
    "com.unity.ui": "UI Toolkit",
    "com.unity.inputsystem": "Input System",
    "com.unity.addressables": "Addressables",
    "com.unity.cinemachine": "Cinemachine",
    "com.unity.timeline": "Timeline",
    "com.unity.render-pipelines.universal": "Universal RP",
    "com.unity.textmeshpro": "TextMeshPro",
    "com.unity.postprocessing": "Post Processing"
}

# Color Themes
COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_WARNING = "orange"
COLOR_INFO = "blue"
COLOR_GRAY = "gray"

# Font Sizes
FONT_SIZE_TITLE = 24
FONT_SIZE_SUBTITLE = 16
FONT_SIZE_HEADER = 14
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 10
FONT_SIZE_TINY = 8



