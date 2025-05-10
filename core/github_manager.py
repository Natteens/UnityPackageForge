import os
import subprocess
import threading
import requests
import webbrowser

class GitHubManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.token = self.config.get_value(section='github', key='token', default='')
        self.username = self.config.get_value(section='github', key='username', default='')

    def is_configured(self):
        return bool(self.token and self.username)

    def check_credentials(self):
        if not self.is_configured():
            return False, "Credenciais não configuradas"
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            response.raise_for_status()
            user_data = response.json()
            return True, f"Autenticado como {user_data.get('login', 'Usuário')}"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    def create_repository(self, name, description, private=False, auto_init=False):
        """
        Cria um repositório no GitHub sem inicialização automática por padrão
        """
        if not self.is_configured():
            return {"error": "Token de acesso GitHub não configurado"}
        try:
            response = requests.post(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": auto_init,  # Mantemos false para evitar conflitos
                    "gitignore_template": None,
                    "license_template": None
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def run_git_command(self, folder_path, command, callback=None):
        """
        Executa comandos Git de forma silenciosa sem abrir janelas
        """
        def run_command():
            try:
                # Configuração para executar sem mostrar janelas no Windows
                startupinfo = None
                if os.name == 'nt':  # Se estiver no Windows
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = 0  # SW_HIDE

                result = subprocess.run(
                    ["git"] + command,
                    cwd=folder_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                    startupinfo=startupinfo  # Evita abrir janelas
                )

                if callback:
                    callback(True, result.stdout)
                return result.stdout
            except subprocess.CalledProcessError as e:
                if callback:
                    callback(False, e.stderr)
                return e.stderr

        # Executa em thread para não bloquear a UI
        threading.Thread(target=run_command).start()

    def setup_repository(self, folder_path, repo_name, repo_url, callback=None):
        """
        Configura o repositório Git local e faz push para o GitHub
        """
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
                if callback:
                    callback(True, "✅ Repositório configurado com sucesso!", 100)
                return

            command, message = steps[step_index]
            progress = int((step_index / len(steps)) * 100)
            if callback:
                callback(True, message, progress)

            def on_command_complete(success, output):
                if success:
                    execute_steps(step_index + 1)
                else:
                    if callback:
                        callback(False, f"❌ Erro: {output}", progress)

            self.run_git_command(folder_path, command, on_command_complete)

        execute_steps()

    def create_and_setup_repository(self, package_folder, package_name, package_description, is_private=False, status_callback=None):
        """
        Processo completo de criação e configuração de repositório com feedback
        """
        # Criar repositório no GitHub
        repo_data = self.create_repository(package_name, package_description, private=is_private)

        if "error" in repo_data:
            if status_callback:
                status_callback(False, f"Erro ao criar repositório: {repo_data['error']}", 0)
            return False, None

        # Obter URLs do repositório
        repo_url = repo_data["clone_url"]
        repo_html_url = repo_data["html_url"]

        if status_callback:
            status_callback(True, f"Repositório criado em GitHub. Configurando Git local...", 30)

        # Configurar repositório local com callback personalizado
        def on_setup_progress(success, message, progress=None):
            if not success:
                if status_callback:
                    status_callback(False, message, progress if progress else 0)
                return

            current_progress = progress if progress else 0
            if status_callback:
                # Ajustando o progresso para 30-100% (30% para criação do repo, 70% para configuração)
                status_callback(True, message, 30 + int(current_progress * 0.7))

            # Quando terminar, abrir o repositório no navegador
            if progress == 100:
                webbrowser.open(repo_html_url)
                if status_callback:
                    status_callback(True, f"✅ Repositório disponível em: {repo_html_url}", 100)

        # Iniciar configuração do repositório
        self.setup_repository(package_folder, package_name, repo_url, on_setup_progress)
        return True, repo_html_url