import os
import subprocess
import threading
import requests
import webbrowser
import sys
from utils.version_utils import sanitize_name_for_repo

class GitHubManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.token = self.config.get_value(section='github', key='token', default='')
        self.username = self.config.get_value(section='github', key='username', default='')
    
    def _get_subprocess_kwargs(self):
        """Get subprocess kwargs to hide CMD window on Windows"""
        kwargs = {}
        if sys.platform == "win32":
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return kwargs

    def is_configured(self):
        return bool(self.token and self.username)

    def check_credentials(self):
        if not self.is_configured():
            return False, "Credenciais não configuradas"

        print(f"Debug - Token length: {len(self.token)}")
        print(f"Debug - Username: {self.username}")
        print(f"Debug - Token starts with: {self.token[:10]}..." if len(self.token) > 10 else f"Debug - Full token: {self.token}")

        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "UnityPackageForge/1.0"
                },
                timeout=10
            )

            print(f"Debug - Response status: {response.status_code}")
            print(f"Debug - Response headers: {dict(response.headers)}")

            if response.status_code == 401:
                return False, "Token inválido ou expirado. Verifique se:\n• O token não expirou\n• Tem permissões 'repo' e 'user'\n• Foi copiado corretamente"
            elif response.status_code == 403:
                return False, "Token sem permissões necessárias. Precisa de 'repo' e 'user'"

            response.raise_for_status()
            user_data = response.json()

            # Verificar se o username bate com o do token
            token_username = user_data.get('login', '')
            if self.username.lower() != token_username.lower():
                return False, f"Username não confere: configurado '{self.username}', token é de '{token_username}'"

            return True, f"✅ Autenticado como {token_username}"

        except requests.exceptions.Timeout:
            return False, "Timeout na conexão com GitHub"
        except requests.exceptions.ConnectionError:
            return False, "Erro de conexão. Verifique sua internet"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    def create_repository(self, display_name, description, private=False, auto_init=False):
        if not self.is_configured():
            return {"error": "Token de acesso GitHub não configurado"}

        repo_name = sanitize_name_for_repo(display_name)

        try:
            response = requests.post(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "name": repo_name,
                    "description": description,
                    "private": private,
                    "auto_init": auto_init,
                    "gitignore_template": None,
                    "license_template": None,
                    "homepage": f"https://github.com/{self.username}/{repo_name}",
                    "has_issues": True,
                    "has_projects": True,
                    "has_wiki": True,
                    "has_downloads": True
                },
                timeout=30
            )

            if response.status_code == 201:
                repo_data = response.json()
                return {
                    "success": True,
                    "repo_url": repo_data["html_url"],
                    "clone_url": repo_data["clone_url"],
                    "ssh_url": repo_data["ssh_url"],
                    "repo_name": repo_name
                }
            elif response.status_code == 422:
                return {"error": f"Repositório '{repo_name}' já existe"}
            else:
                return {"error": f"Erro HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            return {"error": f"Erro ao criar repositório: {str(e)}"}

    def setup_repository_with_semantic_release(self, package_path, display_name, description,
                                               private=False, initial_version="0.1.0"):
        try:
            repo_result = self.create_repository(display_name, description, private)
            if "error" in repo_result:
                return repo_result

            repo_name = repo_result["repo_name"]
            repo_url = f"https://github.com/{self.username}/{repo_name}.git"

            os.chdir(package_path)
            
            # Get subprocess kwargs to hide CMD window on Windows
            subprocess_kwargs = self._get_subprocess_kwargs()

            subprocess.run(["git", "init"], check=True, capture_output=True, **subprocess_kwargs)
            subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True, **subprocess_kwargs)
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True, capture_output=True, **subprocess_kwargs)

            try:
                subprocess.run(["git", "config", "user.name"], check=True, capture_output=True, **subprocess_kwargs)
            except subprocess.CalledProcessError:
                author_name = self.config.get_value(key='author_name', default='Author')
                subprocess.run(["git", "config", "user.name", author_name], check=True, capture_output=True, **subprocess_kwargs)

            try:
                subprocess.run(["git", "config", "user.email"], check=True, capture_output=True, **subprocess_kwargs)
            except subprocess.CalledProcessError:
                author_email = self.config.get_value(key='author_email', default='author@example.com')
                subprocess.run(["git", "config", "user.email", author_email], check=True, capture_output=True, **subprocess_kwargs)

            subprocess.run(["git", "add", "."], check=True, capture_output=True, **subprocess_kwargs)

            commit_message = f"chore: initial package structure\n\n- Unity package configuration v{initial_version}\n- Documentation and samples\n- Runtime and Editor assemblies"
            subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, **subprocess_kwargs)

            subprocess.run(["git", "push", "-u", "origin", "main"], check=True, capture_output=True, **subprocess_kwargs)

            self._create_initial_release(repo_name, initial_version, display_name)

            self._setup_branch_protection(repo_name)

            return {
                "success": True,
                "repo_url": f"https://github.com/{self.username}/{repo_name}",
                "clone_url": repo_url,
                "message": f"Repositório '{repo_name}' criado com versão inicial {initial_version}!"
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"Erro Git: {e.stderr.decode() if e.stderr else str(e)}"}
        except Exception as e:
            return {"error": f"Erro na configuração: {str(e)}"}

    def _create_initial_release(self, repo_name, version, display_name):
        try:
            commits_response = requests.get(
                f"https://api.github.com/repos/{self.username}/{repo_name}/commits",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )

            if commits_response.status_code == 200:
                commits = commits_response.json()
                if commits:
                    latest_commit_sha = commits[0]["sha"]

                    tag_response = requests.post(
                        f"https://api.github.com/repos/{self.username}/{repo_name}/git/refs",
                        headers={
                            "Authorization": f"token {self.token}",
                            "Accept": "application/vnd.github.v3+json"
                        },
                        json={
                            "ref": f"refs/tags/v{version}",
                            "sha": latest_commit_sha
                        },
                        timeout=10
                    )

                    if tag_response.status_code in [200, 201]:
                        release_response = requests.post(
                            f"https://api.github.com/repos/{self.username}/{repo_name}/releases",
                            headers={
                                "Authorization": f"token {self.token}",
                                "Accept": "application/vnd.github.v3+json"
                            },
                            json={
                                "tag_name": f"v{version}",
                                "target_commitish": "main",
                                "name": f"v{version}",
                                "body": f"## 🚀 Initial Release\n\n- Unity package configuration\n- Documentation and samples\n- Runtime and Editor assemblies\n- Basic project setup\n\n### Installation\n\nInstall via Unity Package Manager:\n```\nhttps://github.com/{self.username}/{repo_name}.git\n```",
                                "draft": False,
                                "prerelease": False
                            },
                            timeout=10
                        )

                        if release_response.status_code == 201:
                            print(f"✅ Release v{version} criada com sucesso!")
                        else:
                            print(f"⚠️ Erro ao criar release: {release_response.status_code}")

        except Exception as e:
            print(f"⚠️ Erro ao criar release inicial: {e}")

    def _setup_branch_protection(self, repo_name):
        try:
            protection_config = {
                "required_status_checks": None,
                "enforce_admins": False,
                "required_pull_request_reviews": None,
                "restrictions": None,
                "allow_force_pushes": True,
                "allow_deletions": False
            }

            requests.put(
                f"https://api.github.com/repos/{self.username}/{repo_name}/branches/main/protection",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json=protection_config,
                timeout=10
            )
        except Exception:
            pass

    def open_repository(self, display_name):
        repo_name = sanitize_name_for_repo(display_name)
        url = f"https://github.com/{self.username}/{repo_name}"
        webbrowser.open(url)

    def get_repository_url(self, display_name, for_unity=True):
        repo_name = sanitize_name_for_repo(display_name)
        if for_unity:
            return f"https://github.com/{self.username}/{repo_name}.git"
        else:
            return f"https://github.com/{self.username}/{repo_name}"

