# Unity Package Generator

Gerador de pacotes para Unity com integração GitHub.

## 📋 Sobre

O Unity Package Generator é uma ferramenta intuitiva para criar estruturas completas de pacotes Unity com integração ao GitHub. Com uma interface gráfica amigável, você pode gerar facilmente toda a estrutura necessária para um pacote Unity profissional, incluindo arquivos de configuração, documentação e integração com GitHub Actions.

## ✨ Funcionalidades

- 🎯 **Interface gráfica completa** para fácil utilização
- 📁 Cria automaticamente a estrutura de pastas e arquivos recomendada pela Unity
- 🔄 Integração com GitHub (criação de repositório e configuração inicial)
- ⚙️ Gera arquivos de configuração para CI/CD com GitHub Actions
- 📦 Suporte para o formato de pacote UPM (Unity Package Manager)
- 📝 Cria documentação básica e arquivos README
- 🧪 Estrutura para testes (Editor e Runtime)
- 📊 Fluxo de lançamento automático com Semantic Release

## 🛠️ Requisitos

- Windows, macOS ou Linux
- Python 3.6 ou superior
- Git instalado e configurado
- Conexão com a internet (para funcionalidades do GitHub)

## 📥 Instalação

### Executável (Windows)

Baixe o executável mais recente na [página de releases](https://github.com/Natteens/UnityPackageGenerator/releases) e execute-o diretamente.

### A partir do código-fonte

```bash
git clone https://github.com/Natteens/UnityPackageGenerator.git
cd UnityPackageGenerator
pip install -r requirements.txt
python package_generator.py
```

## 🚀 Como usar

1. **Execute o aplicativo**:
   - Se baixou o executável: execute `unity-package-generator.exe`
   - A partir do código-fonte: `python package_generator.py`

2. **Configure o pacote**:
   - Nome interno do pacote (ex: `pacotedeexemplo`)
   - Nome de exibição (ex: `Pacote de Exemplo`)
   - Descrição do pacote
   - Pasta de destino

3. **Configure opções adicionais** (opcionais):
   - Integração com GitHub
   - Componentes a incluir (Runtime, Editor, Samples, Tests)
   - Tipo de licença

4. **Gere o pacote** clicando em "Gerar Pacote"

5. **Personalize suas configurações**:
   - Acesse a aba "Configurações" para definir informações do autor e prefixos da empresa
   - Configure suas credenciais do GitHub na aba "GitHub"

## 📋 Estrutura gerada

O gerador cria a seguinte estrutura de arquivos:

```
company.packagename/
├── .github/
│   └── workflows/
│       ├── release.yml
│       └── test.yml
├── Documentation~/
│   └── index.md
├── Editor/
│   └── company.packagename.editor.asmdef
├── Runtime/
│   └── company.packagename.asmdef
├── Samples~/
│   ├── 2D Sample/
│   ├── 3D Sample/
│   └── Utilities Sample/
├── Tests/
│   ├── Editor/
│   └── Runtime/
├── .gitignore
├── .releaserc
├── CHANGELOG.md
├── LICENSE.md
├── package.json
└── README.md
```

## 🔧 Configurações

### Informações do autor

Configure informações do autor nas configurações:

- Nome do autor
- Email de contato
- URL do autor (GitHub, site pessoal)
- Versão do Unity compatível
- Prefixo da empresa (ex: `com.natteens`)

### Configuração do GitHub

Para usar a integração com GitHub:

1. Crie um token pessoal no GitHub (Settings > Developer Settings > Personal Access Tokens)
2. Conceda permissão ao escopo `repo`
3. Configure seu username e o token no aplicativo

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE.md para detalhes.

---

Desenvolvido por [Natteens](https://github.com/Natteens) para a comunidade de desenvolvimento Unity.
