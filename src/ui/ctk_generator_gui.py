import os
from tkinter import filedialog, BooleanVar, StringVar, DoubleVar
import customtkinter as ctk
from ui.strings import *
from config.config_manager import ConfigManager
from core.github_manager import GitHubManager
from core.package_generator import PackageGenerator
from utils.helpers import open_folder, validate_package_name

class PackageGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unity Package Forge")
        self.root.geometry("700, 650")
        self.root.minsize(700, 650)

        self.config_manager = ConfigManager()
        self.github_manager = GitHubManager(self.config_manager)
        self.package_generator = PackageGenerator(self.config_manager)

        self.package_generator.set_log_callback(self.add_log)
        self.package_generator.set_progress_callback(self.update_progress)

        self.init_variables()
        self.create_scrollable_ui()
        self.load_ui_values()
        self.bind_scroll_events()

    def init_variables(self):
        self.package_name = StringVar()
        self.display_name = StringVar()
        self.description = StringVar()
        self.version = StringVar(value="0.1.0")
        self.folder_path = StringVar()

        self.create_samples = BooleanVar(value=True)
        self.create_runtime = BooleanVar(value=True)
        self.create_editor = BooleanVar(value=True)
        self.create_tests = BooleanVar(value=True)
        self.create_github = BooleanVar(value=True)
        self.license_type = StringVar(value="MIT")

        self.create_repo = BooleanVar(value=False)
        self.repo_private = BooleanVar(value=False)

        self.author_name = StringVar()
        self.author_email = StringVar()
        self.author_url = StringVar()
        self.company_prefix = StringVar(value="com.companyname")
        self.unity_version = StringVar(value="2021.3")

        self.github_username = StringVar()
        self.github_token = StringVar()
        self.progress_var = DoubleVar()

    def create_scrollable_ui(self):
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.create_header()
        self.create_tabs()
        self.create_theme_button()

    def bind_scroll_events(self):
        self.main_frame.bind("<Enter>", lambda _: self.main_frame.bind_all("<MouseWheel>", self.on_mousewheel))
        self.main_frame.bind("<Leave>", lambda _: self.main_frame.unbind_all("<MouseWheel>"))

    def on_mousewheel(self, event):
        self.main_frame._parent_canvas.yview_scroll(-1*(event.delta//120), "units")

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            header_frame,
            text="Unity Package Forge",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=5)

    def create_theme_button(self):
        self.theme_button = ctk.CTkButton(
            self.root,
            text="☀️" if ctk.get_appearance_mode() == "Dark" else "🌙",
            width=30,
            height=30,
            corner_radius=8,
            command=self.toggle_theme
        )
        self.theme_button.place(relx=0.98, rely=0.02, anchor="ne")

    def create_tabs(self):
        self.tab_view = ctk.CTkTabview(self.main_frame, width=750)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        tabs = ["Pacote", "Configurações", "GitHub", "Debug", "Sobre"]
        for tab in tabs:
            self.tab_view.add(tab)

        self.create_package_tab()
        self.create_config_tab()
        self.create_github_tab()
        self.create_debug_tab()
        self.create_about_tab()

    def toggle_theme(self):
        new_mode = "Dark" if ctk.get_appearance_mode() == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self.theme_button.configure(text="☀️" if new_mode == "Light" else "🌙")
        self.config_manager.set_value(key='dark_mode', value=str(new_mode == "Dark"))

    def create_package_tab(self):
        tab = self.tab_view.tab("Pacote")
        self.create_form_section(tab, PACKAGE_FRAME_TITLE, [
            (PACKAGE_NAME_LABEL, self.package_name, PACKAGE_NAME_PLACEHOLDER),
            (DISPLAY_NAME_LABEL, self.display_name, DISPLAY_NAME_PLACEHOLDER),
            (DESCRIPTION_LABEL, self.description, DESCRIPTION_PLACEHOLDER),
            (VERSION_LABEL, self.version, ""),
            (FOLDER_LABEL, self.folder_path, "", self.select_folder)
        ])

        self.create_structure_section(tab)
        self.create_github_section(tab)
        self.create_action_buttons(tab)

    def create_form_section(self, parent, title, fields):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=5)

        for label, var, placeholder, *command in fields:
            row = ctk.CTkFrame(frame)
            row.pack(fill="x", padx=5, pady=2)

            ctk.CTkLabel(row, text=label, width=120).pack(side="left")

            if command:
                entry_frame = ctk.CTkFrame(row, fg_color="transparent")
                entry_frame.pack(side="left", fill="x", expand=True)

                ctk.CTkEntry(
                    entry_frame,
                    textvariable=var,
                    placeholder_text=placeholder
                ).pack(side="left", fill="x", expand=True)

                ctk.CTkButton(
                    entry_frame,
                    text=SELECT_FOLDER_BUTTON,
                    width=80,
                    command=command[0]
                ).pack(side="right", padx=5)
            else:
                ctk.CTkEntry(
                    row,
                    textvariable=var,
                    placeholder_text=placeholder
                ).pack(side="left", fill="x", expand=True)

    def create_structure_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text=STRUCTURE_FRAME_TITLE, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=5)

        options_frame = ctk.CTkFrame(frame)
        options_frame.pack(fill="x", padx=5, pady=5)

        checkboxes = [
            (self.create_samples, CREATE_SAMPLES_LABEL),
            (self.create_runtime, CREATE_RUNTIME_LABEL),
            (self.create_editor, CREATE_EDITOR_LABEL),
            (self.create_tests, CREATE_TESTS_LABEL),
            (self.create_github, CREATE_GITHUB_LABEL)
        ]

        for i, (var, text) in enumerate(checkboxes):
            ctk.CTkCheckBox(
                options_frame,
                text=text,
                variable=var
            ).grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)

        license_frame = ctk.CTkFrame(options_frame)
        license_frame.grid(row=2, column=1, sticky="w")
        ctk.CTkLabel(license_frame, text=LICENSE_LABEL).pack(side="left")
        ctk.CTkOptionMenu(
            license_frame,
            variable=self.license_type,
            values=["MIT", "Apache-2.0", "GPL-3.0", "None"]
        ).pack(side="left")

    def create_github_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text=GITHUB_FRAME_TITLE, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=5)

        options_frame = ctk.CTkFrame(frame)
        options_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkCheckBox(
            options_frame,
            text=CREATE_REPO_LABEL,
            variable=self.create_repo
        ).pack(side="left", padx=5)

        visibility_frame = ctk.CTkFrame(options_frame)
        visibility_frame.pack(side="left", padx=10)
        ctk.CTkLabel(visibility_frame, text=REPO_VISIBILITY_LABEL).pack(side="left")
        ctk.CTkRadioButton(visibility_frame, text=PUBLIC_OPTION, variable=self.repo_private, value=False).pack(side="left")
        ctk.CTkRadioButton(visibility_frame, text=PRIVATE_OPTION, variable=self.repo_private, value=True).pack(side="left")

    def create_action_buttons(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=10)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=5)

        ctk.CTkButton(
            btn_frame,
            text=GENERATE_BUTTON,
            command=self.generate_package,
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text=OPEN_FOLDER_BUTTON,
            command=lambda: open_folder(self.folder_path.get()),
            width=120
        ).pack(side="left", padx=5)

        self.progress_bar = ctk.CTkProgressBar(frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)

        self.progress_label = ctk.CTkLabel(frame, text="")
        self.progress_label.pack()

    def create_config_tab(self):
        tab = self.tab_view.tab("Configurações")
        self.create_config_form(tab)
        self.create_save_button(tab)

    def create_config_form(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        fields = [
            (AUTHOR_NAME_LABEL, self.author_name),
            (AUTHOR_EMAIL_LABEL, self.author_email),
            (AUTHOR_URL_LABEL, self.author_url),
            (COMPANY_PREFIX_LABEL, self.company_prefix),
            (UNITY_VERSION_LABEL, self.unity_version)
        ]

        for i, (label, var) in enumerate(fields):
            row = ctk.CTkFrame(frame)
            row.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(row, text=label, width=140).pack(side="left")
            ctk.CTkEntry(row, textvariable=var).pack(side="left", fill="x", expand=True)

    def create_save_button(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(
            btn_frame,
            text=SAVE_CONFIG_BUTTON,
            command=self.save_config,
            width=120
        ).pack()

    def create_github_tab(self):
        tab = self.tab_view.tab("GitHub")
        self.create_github_form(tab)
        self.create_verify_button(tab)
        self.create_instructions(tab)

    def create_github_form(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        fields = [
            (GITHUB_USERNAME_LABEL, self.github_username),
            (GITHUB_TOKEN_LABEL, self.github_token)
        ]

        for label, var in fields:
            row = ctk.CTkFrame(frame)
            row.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(row, text=label, width=120).pack(side="left")
            entry = ctk.CTkEntry(row, textvariable=var)
            if "Token" in label:
                entry.configure(show="*")
            entry.pack(side="left", fill="x", expand=True)

    def create_verify_button(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(
            btn_frame,
            text=GITHUB_VERIFY_BUTTON,
            command=self.verify_github_credentials,
            width=120
        ).pack()

    def create_instructions(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        textbox = ctk.CTkTextbox(frame, wrap="word")
        textbox.insert("1.0", GITHUB_INSTRUCTIONS)
        textbox.configure(state="disabled")
        textbox.pack(fill="both", expand=True)

    def create_debug_tab(self):
        tab = self.tab_view.tab("Debug")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.debug_log_text = ctk.CTkTextbox(frame, wrap="word")
        self.debug_log_text.pack(fill="both", expand=True)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=5)
        ctk.CTkButton(
            btn_frame,
            text="Limpar Logs",
            command=self.clear_logs
        ).pack(side="right")

    def create_about_tab(self):
        tab = self.tab_view.tab("Sobre")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        textbox = ctk.CTkTextbox(frame, wrap="word")
        textbox.insert("1.0", ABOUT_TEXT)
        textbox.configure(state="disabled")
        textbox.pack(fill="both", expand=True)
    
    def load_ui_values(self):
        """Carrega valores salvos das configurações"""
        # Valores da aba de configuração
        author_name = self.config_manager.get_value(key='author_name', default='')
        author_email = self.config_manager.get_value(key='author_email', default='')
        author_url = self.config_manager.get_value(key='author_url', default='')
        company_prefix = self.config_manager.get_value(key='company_prefix', default='com.companyname')
        unity_version = self.config_manager.get_value(key='unity_version', default='2021.3')
        
        self.author_name.set(author_name if author_name is not None else '')
        self.author_email.set(author_email if author_email is not None else '')
        self.author_url.set(author_url if author_url is not None else '')
        self.company_prefix.set(company_prefix if company_prefix is not None else 'com.companyname')
        self.unity_version.set(unity_version if unity_version is not None else '2021.3')
        
        # Valores de GitHub
        github_username = self.config_manager.get_value(section='github', key='username', default='')
        github_token = self.config_manager.get_value(section='github', key='token', default='')
        
        self.github_username.set(github_username if github_username is not None else '')
        self.github_token.set(github_token if github_token is not None else '')
        
        # Configuração de tema
        dark_mode_value = self.config_manager.get_value(key='dark_mode', default='False')
        is_dark_mode = dark_mode_value.lower() == 'true' if dark_mode_value is not None else False
        ctk.set_appearance_mode("dark" if is_dark_mode else "light")
        self.theme_button.configure(text="☀️" if is_dark_mode else "🌙")
    
    def select_folder(self):
        """Abre um diálogo para selecionar a pasta onde o pacote será criado"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def save_config(self):
        """Salva as configurações atuais"""
        # Salva os valores dos campos
        self.config_manager.set_value(key='author_name', value=self.author_name.get())
        self.config_manager.set_value(key='author_email', value=self.author_email.get())
        self.config_manager.set_value(key='author_url', value=self.author_url.get())
        self.config_manager.set_value(key='company_prefix', value=self.company_prefix.get())
        self.config_manager.set_value(key='unity_version', value=self.unity_version.get())
        
        self.config_manager.set_value(section='github', key='username', value=self.github_username.get())
        self.config_manager.set_value(section='github', key='token', value=self.github_token.get())
        
        self.add_log("Configurações salvas com sucesso!")
    
    def verify_github_credentials(self):
        """Verifica se as credenciais do GitHub são válidas"""
        self.add_log("Verificando credenciais do GitHub...")
        
        # Atualiza os valores no gerenciador do GitHub
        self.github_manager.username = self.github_username.get()
        self.github_manager.token = self.github_token.get()
        
        # Verifica as credenciais
        result = self.github_manager.check_credentials()
        # Garante que o resultado seja uma tupla, mesmo que a função antiga seja chamada
        if isinstance(result, tuple) and len(result) == 2:
            is_valid, message = result
        else:
            # Compatibilidade com versão antiga que retornava apenas bool
            is_valid = result
            message = "Sucesso!" if is_valid else "Falha na autenticação"
        
        if is_valid:
            self.add_log(f"Credenciais válidas! {message}")
        else:
            self.add_log(f"Erro ao verificar credenciais: {message}")
    
    def add_log(self, message):
        """Adiciona uma mensagem ao log de debug
        
        Args:
            message: A mensagem a ser adicionada
        """
        self.debug_log_text.configure(state="normal")
        self.debug_log_text.insert("end", f"{message}\n")
        self.debug_log_text.see("end")
        self.debug_log_text.configure(state="disabled")
        print(message)  # Também mostra no console para debug
    
    def clear_logs(self):
        """Limpa a área de logs"""
        self.debug_log_text.configure(state="normal")
        self.debug_log_text.delete("1.0", "end")
        self.debug_log_text.configure(state="disabled")
    
    def update_progress(self, value, message=""):
        """Atualiza a barra de progresso e o texto de status
        
        Args:
            value: O valor do progresso (0.0 a 1.0)
            message: Mensagem opcional para mostrar
        """
        self.progress_bar.set(value)
        
        if message:
            self.progress_label.configure(text=message)
            self.add_log(message)
    
    def generate_package(self):
        """Gera o pacote do Unity com as configurações atuais"""
        # Validação básica
        if not self.validate_form():
            return
        
        # Loga início do processo
        self.add_log(f"Iniciando geração do pacote: {self.package_name.get()}")
        self.update_progress(0.0, "Iniciando geração...")
        
        try:
            # Define a pasta base
            base_path = self.folder_path.get()
            
            # Cria a estrutura do pacote
            self.package_generator.create_package_structure(
                base_path=base_path,
                name=self.package_name.get(),
                display_name=self.display_name.get(),
                description=self.description.get(),
                create_samples=self.create_samples.get(),
                create_runtime=self.create_runtime.get(),
                create_editor=self.create_editor.get(),
                create_tests=self.create_tests.get(),
                create_github=self.create_github.get(),
                create_license=self.license_type.get()
            )
            
            self.update_progress(0.8, "Pacote criado com sucesso!")
            
            # Se solicitado, inicializa o repositório GitHub
            if self.create_repo.get() and self.github_manager.is_configured():
                self.add_log("Criando repositório no GitHub...")
                
                repo_name = self.package_generator.get_full_package_name(self.package_name.get())
                
                # Cria o repositório no GitHub
                repo_data = self.github_manager.create_repository(
                    name=repo_name,
                    description=self.description.get(),
                    private=self.repo_private.get()
                )
                
                # Se criou o repositório com sucesso
                if repo_data and 'clone_url' in repo_data:
                    self.add_log(f"Repositório criado: {repo_data['html_url']}")
                    
                    # Configura o repositório local e faz o push
                    self.github_manager.setup_repository(
                        folder_path=os.path.join(base_path, repo_name),
                        repo_name=repo_name,
                        repo_url=repo_data['clone_url'],
                        callback=self.handle_setup_progress
                    )
                else:
                    self.add_log("Erro ao criar repositório no GitHub")
            
            self.update_progress(1.0, "Pacote gerado com sucesso!")
        except Exception as e:
            self.add_log(f"Erro ao gerar pacote: {str(e)}")
            self.update_progress(0, "Erro ao gerar pacote")
    
    def handle_setup_progress(self, success, message, progress=None):
        """Manipula o progresso da configuração do git
        
        Args:
            success: Se a operação foi bem-sucedida
            message: A mensagem de status
            progress: O valor de progresso opcional
        """
        if success:
            self.add_log(message)
            if progress is not None:
                # Ajusta o progresso para a faixa de 80% a 100%
                adjusted_progress = 0.8 + (progress * 0.2)
                self.update_progress(adjusted_progress, message)
        else:
            self.add_log(f"Erro: {message}")
    
    def validate_form(self):
        """Valida os campos do formulário antes de gerar o pacote
        
        Returns:
            bool: True se o formulário é válido, False caso contrário
        """
        # Valida nome do pacote
        package_name = self.package_name.get().strip()
        if not package_name:
            self.add_log("Erro: Nome do pacote é obrigatório")
            return False
        
        if not validate_package_name(package_name):
            self.add_log("Erro: Nome do pacote inválido. Use apenas letras minúsculas, números e ponto.")
            return False
        
        # Valida nome de exibição
        display_name = self.display_name.get().strip()
        if not display_name:
            self.add_log("Erro: Nome de exibição é obrigatório")
            return False
        
        # Valida descrição
        description = self.description.get().strip()
        if not description:
            self.add_log("Erro: Descrição é obrigatória")
            return False
        
        # Valida pasta
        folder_path = self.folder_path.get().strip()
        if not folder_path:
            self.add_log("Erro: Selecione uma pasta para o pacote")
            return False
        
        if not os.path.isdir(folder_path):
            self.add_log(f"Erro: A pasta '{folder_path}' não existe ou não é um diretório")
            return False
        
        # Valida configurações de GitHub
        if self.create_repo.get() and not self.github_manager.is_configured():
            self.add_log("Erro: Para criar um repositório no GitHub, configure suas credenciais na aba GitHub")
            return False
        
        return True