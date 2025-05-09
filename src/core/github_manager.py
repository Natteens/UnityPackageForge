import subprocess
import threading
import requests


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
                    "auto_init": auto_init, 
                    "gitignore_template": None, 
                    "license_template": None
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e: 
            return {"error": str(e)}
    
    def run_git_command(self, folder_path, command, callback=None):
        def run_command():
            try:
                result = subprocess.run(
                    ["git"] + command, 
                    cwd=folder_path, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    check=True
                )
                if callback: 
                    callback(True, result.stdout)
                return result.stdout
            except subprocess.CalledProcessError as e:
                if callback: 
                    callback(False, e.stderr)
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
