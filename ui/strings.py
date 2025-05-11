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

# Templates
README_TEMPLATE = """# {display_name}

{description}

## 📥 Instalação

Este pacote pode ser instalado através do Unity Package Manager.

1. Abra o Package Manager (Window > Package Manager)
2. Clique no botão + e selecione "Add package from git URL..."
3. Digite: https://github.com/Natteens/{name}.git

## 🚀 Uso

*Documentação em desenvolvimento*
"""

CHANGELOG_TEMPLATE = """# 📝 Changelog

Todos os lançamentos notáveis serão documentados neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Não lançado]

### Adicionado
- ✨ Estrutura inicial do pacote
"""

DOCUMENTATION_TEMPLATE = """# 📚 {display_name}

{description}

## 🚀 Início Rápido

*Em desenvolvimento*
"""

SAMPLE_README_TEMPLATE = """# {category}

Exemplo para o pacote {display_name}.

## Como usar

1. Importe este sample pelo Unity Package Manager
2. Abra a cena de exemplo
3. Play
"""

GITIGNORE_TEMPLATE = """# Unity specific
Library/
Temp/
Logs/
UserSettings/
obj/
Build/
Builds/
.DS_Store
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

# IDE
.vs/
.idea/
.vscode/

# Node.js
node_modules/
package-lock.json
"""

# UI Strings
APP_TITLE = "Unity Package Generator"
TAB_PACKAGE = "Pacote"
TAB_CONFIG = "Configurações"
TAB_GITHUB = "GitHub"
TAB_DEBUG = "Debug"
TAB_ABOUT = "Sobre"

PACKAGE_FRAME_TITLE = "Configurações do Pacote"
PACKAGE_NAME_LABEL = "Nome do Pacote:"
PACKAGE_NAME_PLACEHOLDER = "MeuPacote"
DISPLAY_NAME_LABEL = "Nome de Exibição:"
DISPLAY_NAME_PLACEHOLDER = "Meu Pacote"
DESCRIPTION_LABEL = "Descrição:"
DESCRIPTION_PLACEHOLDER = "Uma descrição do que o pacote faz..."
VERSION_LABEL = "Versão:"
FOLDER_LABEL = "Pasta de Destino:"

STRUCTURE_FRAME_TITLE = "Estrutura do Pacote"
CREATE_SAMPLES_LABEL = "Criar Samples"
CREATE_RUNTIME_LABEL = "Criar Assembly Runtime"
CREATE_EDITOR_LABEL = "Criar Assembly Editor"
CREATE_TESTS_LABEL = "Criar Tests"
CREATE_GITHUB_LABEL = "Criar config GitHub"
LICENSE_LABEL = "Licença:"

GITHUB_FRAME_TITLE = "Integração com GitHub"
CREATE_REPO_LABEL = "Criar repositório GitHub"
REPO_VISIBILITY_LABEL = "Visibilidade:"
PUBLIC_OPTION = "Público"
PRIVATE_OPTION = "Privado"

GENERATE_BUTTON = "Gerar Pacote"
SELECT_FOLDER_BUTTON = "Selecionar"
OPEN_FOLDER_BUTTON = "Abrir Pasta"

CONFIG_TITLE = "Configurações do Aplicativo"
AUTHOR_NAME_LABEL = "Nome do Autor:"
AUTHOR_EMAIL_LABEL = "Email do Autor:"
AUTHOR_URL_LABEL = "URL do Autor:"
COMPANY_PREFIX_LABEL = "Prefixo da Empresa:"
UNITY_VERSION_LABEL = "Versão do Unity:"
SAVE_CONFIG_BUTTON = "Salvar Configurações"

GITHUB_CONFIG_TITLE = "Configurações do GitHub"
GITHUB_USERNAME_LABEL = "Usuário GitHub:"
GITHUB_TOKEN_LABEL = "Token de Acesso:"
GITHUB_VERIFY_BUTTON = "Verificar Credenciais"
GITHUB_INSTRUCTIONS = """Para gerar um token de acesso pessoal:
1. Acesse as configurações do GitHub
2. Developer settings > Personal access tokens > Generate new token
3. Marque as permissões: repo, workflow
4. Copie o token gerado e cole aqui"""

ABOUT_TITLE = "Sobre o Aplicativo"
ABOUT_TEXT = """Unity Package Generator v1.0

Desenvolvido para facilitar a criação de pacotes Unity seguindo
as melhores práticas de estrutura.

© 2023 Nathan da Silva Miranda
"""

# Messages
SUCCESS_MESSAGE = "✅ Pacote criado com sucesso!"
ERROR_MESSAGE_PREFIX = "❌ Erro: "
CREDENTIALS_VALID = "✅ Credenciais válidas!"
CREDENTIALS_INVALID = "❌ Credenciais inválidas!"
CONFIG_SAVED = "✅ Configurações salvas com sucesso!"
REPO_SUCCESS = "✅ Repositório criado com sucesso!"
REPO_ERROR_PREFIX = "❌ Erro ao criar repositório: "

# NOVOS TEMPLATES PARA SEMANTIC RELEASE

# Template para arquivo .releaserc.json
RELEASERC_JSON = """{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    ["@semantic-release/npm", { "npmPublish": false }],
    ["@semantic-release/git", {
      "assets": ["package.json", "CHANGELOG.md"],
      "message": "chore(release): ${nextRelease.version} [skip ci]\\n\\n${nextRelease.notes}"
    }],
    "@semantic-release/github"
  ]
}"""

# Template atualizado para o workflow de release
RELEASE_WORKFLOW = """name: release

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
          # Removido cache para evitar erro por falta de lockfile

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
"""

# Templates para arquivos de configuração do Semantic Release