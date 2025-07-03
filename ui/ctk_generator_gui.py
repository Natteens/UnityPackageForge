import os
import threading
from datetime import datetime
from tkinter import filedialog, messagebox, BooleanVar, StringVar, DoubleVar
import customtkinter as ctk
from ui.strings import *
from config.config_manager import ConfigManager
from core.github_manager import GitHubManager
from core.package_generator import PackageGenerator
from utils.helpers import open_folder, validate_package_name
from utils.version_utils import get_current_version, extract_package_name_from_full_name


class PackageGeneratorGUI:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("dark")

        self.root.title(f"Unity Package Forge v{get_current_version()}")
        self.root.geometry("820x680")
        self.root.minsize(800, 650)
        self.root.resizable(True, True)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.config_manager = ConfigManager()
        self.github_manager = GitHubManager(self.config_manager)
        self.package_generator = PackageGenerator(self.config_manager)

        self.package_generator.set_log_callback(self.add_log)
        self.package_generator.set_progress_callback(self.update_progress)

        self.init_variables()
        self.create_ui()
        self.load_ui_values()
        self.setup_bindings()

    def init_variables(self):
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
        self.custom_license_path = StringVar()

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
        self.progress_messages = StringVar(value="Pronto para começar")  # Nova variável para mensagens de progresso
        self.unity_dependencies = {}
        self.selected_dependencies = []
        self.dependency_widgets = {}  # Para armazenar widgets de dependência

        self.display_name.trace('w', self.on_display_name_change)

    def on_display_name_change(self, *args):
        if hasattr(self, 'repo_preview_label'):
            display_name = self.display_name.get()
            if display_name:
                from utils.version_utils import sanitize_name_for_repo
                repo_name = sanitize_name_for_repo(display_name)
                username = self.github_username.get() or "seuusuario"
                self.repo_preview_label.configure(
                    text=f"📋 URL: https://github.com/{username}/{repo_name}.git"
                )
            else:
                self.repo_preview_label.configure(text="📋 URL será gerada automaticamente")

    def create_ui(self):
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_tabs()

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="🚀 Unity Package Forge",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, pady=12)

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Gerador profissional de pacotes Unity com integração GitHub",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        subtitle.grid(row=1, column=0, pady=(0, 8))

    def create_tabs(self):
        self.tab_view = ctk.CTkTabview(self.main_frame, height=550)
        self.tab_view.grid(row=1, column=0, sticky="ew", pady=5)
        self.tab_view.grid_columnconfigure(0, weight=1)

        tabs = [
            ("📦 Pacote", "Pacote"),
            ("⚙️ Configurações", "Configurações"),
            ("🐙 GitHub", "GitHub"),
            ("🔧 Dependências", "Dependências"),
            ("🐛 Debug", "Debug"),
            ("ℹ️ Sobre", "Sobre")
        ]

        for tab_name, tab_key in tabs:
            self.tab_view.add(tab_name)

        self.create_package_tab()
        self.create_config_tab()
        self.create_github_tab()
        self.create_dependencies_tab()
        self.create_debug_tab()
        self.create_about_tab()

    def create_entry_row(self, parent, label, variable, placeholder="", row=0):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=12, pady=4)
        frame.grid_columnconfigure(1, weight=1)

        label_widget = ctk.CTkLabel(
            frame,
            text=label,
            width=140,
            anchor="w",
            font=ctk.CTkFont(size=13),
            height=32
        )
        label_widget.grid(row=0, column=0, sticky="w")

        entry = ctk.CTkEntry(
            frame,
            textvariable=variable,
            placeholder_text=placeholder,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        entry.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        return entry

    def create_package_tab(self):
        tab = self.tab_view.tab("📦 Pacote")
        tab.grid_columnconfigure(0, weight=1)

        main_section = self.create_section(tab, "📋 Informações do Pacote", 0)

        self.create_entry_row(main_section, "🏷️  Nome de Exibição:", self.display_name,
                              placeholder="Meu Incrível Pacote", row=1)

        info_label = ctk.CTkLabel(
            main_section,
            text="💡 Nome usado no repositório GitHub e como base para tudo",
            font=ctk.CTkFont(size=12),
            text_color="orange"
        )
        info_label.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 8))

        self.create_entry_row(main_section, "📝  Descrição:", self.description,
                              placeholder="Uma descrição clara do que o pacote faz...", row=3)

        self.create_entry_row(main_section, "🔖  Versão Inicial:", self.version,
                              placeholder="0.1.0", row=4)

        folder_frame = ctk.CTkFrame(main_section, fg_color="transparent")
        folder_frame.grid(row=5, column=0, sticky="ew", padx=12, pady=4)
        folder_frame.grid_columnconfigure(1, weight=1)

        folder_label = ctk.CTkLabel(folder_frame, text="📁  Pasta de Destino:", width=140, anchor="w")
        folder_label.grid(row=0, column=0, sticky="w")

        entry_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        entry_frame.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        entry_frame.grid_columnconfigure(0, weight=1)

        folder_entry = ctk.CTkEntry(
            entry_frame,
            textvariable=self.folder_path,
            placeholder_text="Selecione a pasta Packages do seu projeto Unity...",
            height=32
        )
        folder_entry.grid(row=0, column=0, sticky="ew")

        folder_btn = ctk.CTkButton(
            entry_frame,
            text="📂",
            width=35,
            height=32,
            command=self.select_folder
        )
        folder_btn.grid(row=0, column=1, padx=(4, 0))

        folder_info = ctk.CTkLabel(
            main_section,
            text="💡 Recomendado: Pasta 'Packages' do seu projeto Unity para teste direto",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        folder_info.grid(row=6, column=0, sticky="w", padx=16, pady=(0, 15))

        license_section = self.create_section(tab, "📄 Licença", 1)

        license_frame = ctk.CTkFrame(license_section, fg_color="transparent")
        license_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        license_frame.grid_columnconfigure(1, weight=1)

        license_label = ctk.CTkLabel(license_frame, text="📄  Tipo:", width=140, anchor="w")
        license_label.grid(row=0, column=0, sticky="w")

        license_combo = ctk.CTkComboBox(
            license_frame,
            values=["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "Unlicense", "Personalizada"],
            variable=self.license_type,
            command=self.on_license_change,
            width=180,
            height=32,
            state="readonly"
        )
        license_combo.grid(row=0, column=1, sticky="w", padx=(4, 0))

        self.custom_license_frame = ctk.CTkFrame(license_section, fg_color="transparent")
        self.custom_license_frame.grid_columnconfigure(0, weight=1)

        custom_entry = ctk.CTkEntry(
            self.custom_license_frame,
            textvariable=self.custom_license_path,
            placeholder_text="Caminho para arquivo de licença...",
            height=32
        )
        custom_entry.grid(row=0, column=0, sticky="ew", padx=(16, 4))

        custom_btn = ctk.CTkButton(
            self.custom_license_frame,
            text="📂",
            width=35,
            height=32,
            command=self.select_license_file
        )
        custom_btn.grid(row=0, column=1)

        structure_section = self.create_section(tab, "🏗️ Estrutura do Pacote", 2)

        checkbox_container = ctk.CTkFrame(structure_section, fg_color="transparent")
        checkbox_container.grid(row=1, column=0, sticky="ew", padx=12, pady=12)

        checkbox_container.grid_columnconfigure(0, weight=1, uniform="checkbox")
        checkbox_container.grid_columnconfigure(1, weight=1, uniform="checkbox")
        checkbox_container.grid_columnconfigure(2, weight=1, uniform="checkbox")

        checkboxes = [
            ("📦  Samples", self.create_samples),
            ("⚡  Runtime", self.create_runtime),
            ("🛠️ Editor", self.create_editor),
            ("🧪  Tests", self.create_tests),
            ("🔧  GitHub Actions", self.create_github)
        ]

        for i, (text, var) in enumerate(checkboxes):
            row_num = i // 3
            col_num = i % 3

            checkbox = ctk.CTkCheckBox(
                checkbox_container,
                text=text,
                variable=var,
                font=ctk.CTkFont(size=13),
                checkbox_width=20,
                checkbox_height=20
            )
            checkbox.grid(row=row_num, column=col_num, sticky="w", padx=(0, 10), pady=8)

        self.create_action_buttons(tab, 3)

    def create_section(self, parent, title, row):
        section = ctk.CTkFrame(parent, corner_radius=8)
        section.grid(row=row, column=0, sticky="ew", pady=6)
        section.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        return section

    def create_action_buttons(self, parent, row):
        button_frame = ctk.CTkFrame(parent, corner_radius=8)
        button_frame.grid(row=row, column=0, sticky="ew", pady=15)
        button_frame.grid_columnconfigure(0, weight=1)

        self.generate_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Gerar Pacote Unity",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            command=self.generate_package
        )
        self.generate_btn.grid(row=0, column=0, sticky="ew", padx=15, pady=12)

        self.progress_bar = ctk.CTkProgressBar(button_frame, variable=self.progress_var)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))

        # Alterado para usar StringVar
        self.status_label = ctk.CTkLabel(
            button_frame,
            textvariable=self.progress_messages,
            font=ctk.CTkFont(size=11),
            wraplength=500  # Permite quebra de linha
        )
        self.status_label.grid(row=2, column=0, pady=(0, 10))

    def on_license_change(self, choice):
        if choice == "Personalizada":
            self.custom_license_frame.grid(row=2, column=0, sticky="ew", pady=(8, 12))
        else:
            self.custom_license_frame.grid_remove()

    def select_license_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo de licença",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            self.custom_license_path.set(file_path)

    def create_config_tab(self):
        tab = self.tab_view.tab("⚙️ Configurações")
        tab.grid_columnconfigure(0, weight=1)

        author_section = self.create_section(tab, "👤 Informações do Autor", 0)

        self.create_entry_row(author_section, "👤 Nome:", self.author_name,
                              placeholder="Seu Nome Completo", row=1)
        self.create_entry_row(author_section, "📧 Email:", self.author_email,
                              placeholder="seu@email.com", row=2)
        self.create_entry_row(author_section, "🌐 URL do Perfil:", self.author_url,
                              placeholder="https://github.com/seuusuario", row=3)

        unity_section = self.create_section(tab, "🎮 Configurações Unity", 1)

        self.create_entry_row(unity_section, "🏢 Prefixo da Empresa:", self.company_prefix,
                              placeholder="com.suaempresa", row=1)

        unity_frame = ctk.CTkFrame(unity_section, fg_color="transparent")
        unity_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=3)
        unity_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(unity_frame, text="🎮 Versão Unity:", width=130, anchor="w").grid(row=0, column=0, sticky="w")

        unity_combo = ctk.CTkComboBox(
            unity_frame,
            values=["2021.3", "2022.3", "2023.1", "2023.2", "2023.3", "6000.0"],
            variable=self.unity_version,
            width=120
        )
        unity_combo.grid(row=0, column=1, sticky="w", padx=(8, 0))

        save_btn = ctk.CTkButton(
            tab,
            text="💾 Salvar Configurações",
            command=self.save_config,
            height=35
        )
        save_btn.grid(row=2, column=0, pady=15)

    def create_github_tab(self):
        tab = self.tab_view.tab("🐙 GitHub")
        tab.grid_columnconfigure(0, weight=1)

        cred_section = self.create_section(tab, "🔑 Credenciais GitHub", 0)

        self.create_entry_row(cred_section, "👤 Usuário:", self.github_username,
                              placeholder="seuusuario", row=1)

        token_frame = ctk.CTkFrame(cred_section, fg_color="transparent")
        token_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=3)
        token_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(token_frame, text="🔑 Token:", width=130, anchor="w").grid(row=0, column=0, sticky="w")

        token_entry_frame = ctk.CTkFrame(token_frame, fg_color="transparent")
        token_entry_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        token_entry_frame.grid_columnconfigure(0, weight=1)

        self.token_entry = ctk.CTkEntry(
            token_entry_frame,
            textvariable=self.github_token,
            placeholder_text="xxx_xxxxxxxxxxxx",
            show="*"
        )
        self.token_entry.grid(row=0, column=0, sticky="ew")

        verify_btn = ctk.CTkButton(
            token_entry_frame,
            text="✅",
            width=35,
            command=self.verify_github_credentials
        )
        verify_btn.grid(row=0, column=1, padx=(4, 0))

        self.github_status_label = ctk.CTkLabel(
            cred_section,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.github_status_label.grid(row=3, column=0, padx=12, pady=8)

        repo_section = self.create_section(tab, "🚀 Criar Repositório", 1)

        create_repo_cb = ctk.CTkCheckBox(
            repo_section,
            text="🚀 Criar repositório no GitHub automaticamente",
            variable=self.create_repo
        )
        create_repo_cb.grid(row=1, column=0, sticky="w", padx=12, pady=8)

        private_cb = ctk.CTkCheckBox(
            repo_section,
            text="🔒 Repositório privado",
            variable=self.repo_private
        )
        private_cb.grid(row=2, column=0, sticky="w", padx=30, pady=4)

        self.repo_preview_label = ctk.CTkLabel(
            repo_section,
            text="📋 URL será gerada automaticamente",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.repo_preview_label.grid(row=3, column=0, sticky="w", padx=12, pady=8)

        instructions_section = self.create_section(tab, "📋 Como obter um Token", 2)

        instructions = """1. Acesse github.com/settings/tokens
2. "Generate new token (classic)"
3. Nome: "Unity Package Forge" 
4. Permissões: repo, workflow
5. Copie o token gerado"""

        instructions_label = ctk.CTkLabel(
            instructions_section,
            text=instructions,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        instructions_label.grid(row=1, column=0, sticky="w", padx=12, pady=10)

    def create_dependencies_tab(self):
        tab = self.tab_view.tab("🔧 Dependências")
        tab.grid_columnconfigure(0, weight=1)

        deps_section = self.create_section(tab, "📦 Dependências Unity", 0)

        main_container = ctk.CTkFrame(deps_section, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        main_container.grid_columnconfigure((0, 1), weight=1)

        left_frame = ctk.CTkFrame(main_container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.grid_columnconfigure(0, weight=1)

        left_title = ctk.CTkLabel(left_frame, text="Dependências Disponíveis", font=ctk.CTkFont(weight="bold"))
        left_title.grid(row=0, column=0, pady=8)

        # Barra de pesquisa
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))
        search_frame.grid_columnconfigure(0, weight=1)

        self.deps_search_var = StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.deps_search_var,
            placeholder_text="🔍 Pesquisar dependências...",
            height=28
        )
        search_entry.grid(row=0, column=0, sticky="ew")
        self.deps_search_var.trace('w', self.filter_dependencies)

        self.deps_scroll = ctk.CTkScrollableFrame(left_frame, height=300)
        self.deps_scroll.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        self.deps_scroll.grid_columnconfigure(0, weight=1)

        right_frame = ctk.CTkFrame(main_container)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.grid_columnconfigure(0, weight=1)

        right_title = ctk.CTkLabel(right_frame, text="Dependências Selecionadas", font=ctk.CTkFont(weight="bold"))
        right_title.grid(row=0, column=0, pady=8)

        self.selected_deps_text = ctk.CTkTextbox(right_frame, height=300, font=ctk.CTkFont(size=10))
        self.selected_deps_text.grid(row=1, column=0, sticky="ew", padx=8, pady=8)

        custom_section = self.create_section(tab, "➕ Dependência Personalizada", 1)

        custom_container = ctk.CTkFrame(custom_section, fg_color="transparent")
        custom_container.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        custom_container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(custom_container, text="Package ID:", width=80).grid(row=0, column=0, sticky="w")

        self.custom_dep_name = StringVar()
        ctk.CTkEntry(
            custom_container,
            textvariable=self.custom_dep_name,
            placeholder_text="com.exemplo.pacote"
        ).grid(row=0, column=1, sticky="ew", padx=(4, 8))

        ctk.CTkLabel(custom_container, text="Versão:", width=50).grid(row=0, column=2, sticky="w")

        self.custom_dep_version = StringVar()
        ctk.CTkEntry(
            custom_container,
            textvariable=self.custom_dep_version,
            placeholder_text="1.0.0",
            width=80
        ).grid(row=0, column=3, sticky="ew", padx=(4, 8))

        ctk.CTkLabel(custom_container, text="Nome:", width=50).grid(row=0, column=4, sticky="w")

        self.custom_dep_display_name = StringVar()
        ctk.CTkEntry(
            custom_container,
            textvariable=self.custom_dep_display_name,
            placeholder_text="Nome Amigável (opcional)",
            width=120
        ).grid(row=0, column=5, sticky="ew", padx=(4, 8))

        add_btn = ctk.CTkButton(
            custom_container,
            text="➕",
            width=40,
            command=self.add_custom_dependency
        )
        add_btn.grid(row=0, column=6, padx=(0, 8))

        remove_btn = ctk.CTkButton(
            custom_container,
            text="🗑️",
            width=40,
            command=self.remove_selected_dependency,
            fg_color="red",
            hover_color="darkred"
        )
        remove_btn.grid(row=0, column=7)

        self.load_all_dependencies()

    def filter_dependencies(self, *args):
        search_term = self.deps_search_var.get().lower()
        for package_id, widget in self.dependency_widgets.items():
            text = widget.info_label.cget("text").lower()
            if search_term in text or search_term in package_id.lower():
                widget.grid()
            else:
                widget.grid_remove()

    def load_all_dependencies(self):
        current_selections = {}
        if hasattr(self, 'dependency_vars'):
            for package_id, var in self.dependency_vars.items():
                current_selections[package_id] = var.get()

        self.dependency_vars = {}
        self.dependency_widgets = {}

        for widget in self.deps_scroll.winfo_children():
            widget.destroy()

        common_deps = [
            ("UI Toolkit", "com.unity.ui", "1.0.0"),
            ("Input System", "com.unity.inputsystem", "1.7.0"),
            ("Addressables", "com.unity.addressables", "1.21.19"),
            ("Cinemachine", "com.unity.cinemachine", "2.9.7"),
            ("Timeline", "com.unity.timeline", "1.7.6"),
            ("Universal RP", "com.unity.render-pipelines.universal", "14.0.9"),
            ("TextMeshPro", "com.unity.textmeshpro", "3.0.6"),
            ("Post Processing", "com.unity.postprocessing", "3.2.2")
        ]

        custom_deps = self.config_manager.get_custom_dependencies()

        all_deps = []

        for name, package_id, version in common_deps:
            custom_info = self.config_manager.get_dependency_info(package_id)
            if custom_info:
                version = custom_info["version"]
                name = custom_info.get("name", name)
            all_deps.append((name, package_id, version, False))

        for package_id, value in custom_deps.items():
            if not any(dep[1] == package_id for dep in common_deps):
                if '|' in value:
                    version, name = value.split('|', 1)
                else:
                    version = value
                    name = package_id.split('.')[-1].title()
                all_deps.append((name, package_id, version, True))

        all_deps.sort(key=lambda x: x[0])

        for i, (name, package_id, version, is_custom) in enumerate(all_deps):
            var = BooleanVar()
            if package_id in current_selections:
                var.set(current_selections[package_id])

            var.trace('w', lambda *args, pid=package_id, v=version: self.update_dependency_preview())
            self.dependency_vars[package_id] = var

            dep_frame = ctk.CTkFrame(self.deps_scroll, fg_color="transparent")
            dep_frame.grid(row=i, column=0, sticky="ew", pady=2)
            dep_frame.grid_columnconfigure(1, weight=1)

            cb = ctk.CTkCheckBox(dep_frame, text="", variable=var, width=20)
            cb.grid(row=0, column=0, sticky="w")

            text_color = "orange" if is_custom else "gray90"
            prefix = "🔧 " if is_custom else ""

            info_label = ctk.CTkLabel(
                dep_frame,
                text=f"{prefix}{name} (v{version})",
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=text_color
            )
            info_label.grid(row=0, column=1, sticky="ew", padx=(8, 0))

            # Armazena o widget para filtragem
            self.dependency_widgets[package_id] = dep_frame
            dep_frame.info_label = info_label  # Para acesso fácil ao texto

        self.update_dependency_preview()
        self.filter_dependencies()  # Aplica filtro atual

    def add_custom_dependency(self):
        package_id = self.custom_dep_name.get().strip()
        version = self.custom_dep_version.get().strip()
        display_name = self.custom_dep_display_name.get().strip()

        if not package_id or not version:
            self.add_log("❌ Package ID e versão são obrigatórios")
            return

        if not self._is_valid_unity_package_id(package_id):
            self.add_log("❌ Package ID inválido. Deve ser uma dependência Unity válida (ex: com.unity.inputsystem)")
            return

        if not self._is_valid_version(version):
            self.add_log("❌ Formato de versão inválido. Use formato x.y.z (ex: 1.0.0)")
            return

        success = self.config_manager.add_custom_dependency(
            package_id,
            version,
            display_name if display_name else None
        )

        if success:
            self.add_log(f"✅ Dependência {package_id} v{version} adicionada/atualizada")

            self.custom_dep_name.set("")
            self.custom_dep_version.set("")
            self.custom_dep_display_name.set("")

            self.load_all_dependencies()
        else:
            self.add_log("❌ Erro ao adicionar dependência")

    def _is_valid_unity_package_id(self, package_id):
        import re

        pattern = r'^(com\.unity\.|com\.[\w-]+\.|org\.[\w-]+\.)[a-z0-9\-\.]+$'

        if not re.match(pattern, package_id):
            return False

        valid_prefixes = [
            'com.unity.',  # Pacotes oficiais Unity
            'com.microsoft.',  # Microsoft packages (Mixed Reality, etc)
            'com.google.',  # Google packages (Firebase, etc)
            'com.facebook.',  # Facebook packages
            'com.valve.',  # Valve packages (OpenVR, etc)
            'com.oculus.',  # Oculus packages
            'com.htc.',  # HTC packages
            'com.autodesk.',  # Autodesk packages
            'com.adobe.',  # Adobe packages
            'org.nuget.',  # NuGet packages
        ]

        return any(package_id.startswith(prefix) for prefix in valid_prefixes)

    def _is_valid_version(self, version):
        import re
        pattern = r'^\d+\.\d+\.\d+(-[\w\.\-]+)?$'
        return bool(re.match(pattern, version))

    def remove_selected_dependency(self):
        selected_deps = []
        custom_deps = self.config_manager.get_custom_dependencies()

        for package_id, var in self.dependency_vars.items():
            if var.get() and package_id in custom_deps:
                selected_deps.append(package_id)

        if not selected_deps:
            self.add_log("⚠️ Selecione uma dependência personalizada (🔧) para remover")
            return

        package_id = selected_deps[0]
        if self.config_manager.remove_custom_dependency(package_id):
            self.add_log(f"🗑️ Dependência {package_id} removida")
            self.load_all_dependencies()
        else:
            self.add_log("❌ Erro ao remover dependência")

    def update_dependency_preview(self):
        if hasattr(self, 'selected_deps_text'):
            selected = []
            for package_id, var in self.dependency_vars.items():
                if var.get():
                    if self._is_valid_unity_package_id(package_id):
                        custom_info = self.config_manager.get_dependency_info(package_id)
                        if custom_info:
                            version = custom_info["version"]
                        else:
                            version = "1.0.0"
                            for name, deps in UNITY_DEPENDENCIES.items():
                                if package_id in deps:
                                    version = deps[package_id]
                                    break

                        selected.append(f'"{package_id}": "{version}"')

            if selected:
                preview_text = "{\n  " + ",\n  ".join(selected) + "\n}"
            else:
                preview_text = "Nenhuma dependência selecionada"

            self.selected_deps_text.delete("1.0", "end")
            self.selected_deps_text.insert("1.0", preview_text)

    def generate_package(self):
        def run_generation():
            try:
                if not self.display_name.get().strip():
                    self.add_log("❌ Nome de exibição é obrigatório")
                    return

                if not self.folder_path.get().strip():
                    self.add_log("❌ Pasta de destino é obrigatória")
                    return

                # Bloquear UI durante a geração
                self.toggle_ui_state(disabled=True)
                self.root.title(f"Unity Package Forge v{get_current_version()} [Gerando...]")

                selected_deps = {}
                for package_id, var in self.dependency_vars.items():
                    if var.get() and self._is_valid_unity_package_id(package_id):
                        custom_info = self.config_manager.get_dependency_info(package_id)
                        if custom_info:
                            version = custom_info["version"]
                        else:
                            version = "1.0.0"
                            for name, deps in UNITY_DEPENDENCIES.items():
                                if package_id in deps:
                                    version = deps[package_id]
                                    break
                        selected_deps[package_id] = version

                package_path = self.package_generator.create_package_structure(
                    base_path=self.folder_path.get(),
                    name=self.display_name.get(),
                    display_name=self.display_name.get(),
                    description=self.description.get(),
                    version=self.version.get(),
                    create_samples=self.create_samples.get(),
                    create_runtime=self.create_runtime.get(),
                    create_editor=self.create_editor.get(),
                    create_tests=self.create_tests.get(),
                    create_github=self.create_github.get(),
                    license_type=self.license_type.get(),
                    unity_dependencies=selected_deps if selected_deps else None
                )

                if self.create_repo.get():
                    if self.github_manager.is_configured():
                        result = self.github_manager.setup_repository_with_semantic_release(
                            package_path=package_path,
                            display_name=self.display_name.get(),
                            description=self.description.get(),
                            private=self.repo_private.get(),
                            initial_version=self.version.get()
                        )

                        if "success" in result:
                            self.add_log(f"✅ {result['message']}")
                            repo_url = self.github_manager.get_repository_url(self.display_name.get())
                            self.add_log(f"📋 URL para Unity: {repo_url}")
                        else:
                            self.add_log(f"❌ Erro no GitHub: {result['error']}")
                    else:
                        self.add_log("⚠️ Credenciais GitHub não configuradas - repositório não criado")

                self.add_log("🎉 Pacote gerado com sucesso!")
                self.update_progress(100, "Concluído!")

                if messagebox.askyesno("Sucesso", "✅ Pacote criado com sucesso!\nDeseja abrir a pasta?"):
                    open_folder(package_path)

            except Exception as e:
                self.add_log(f"❌ Erro crítico: {str(e)}")
                self.update_progress(0, f"Erro: {str(e)}")
            finally:
                # Restaurar estado da UI
                self.toggle_ui_state(disabled=False)
                self.root.title(f"Unity Package Forge v{get_current_version()}")

        threading.Thread(target=run_generation, daemon=True).start()

    def toggle_ui_state(self, disabled=True):
        """Habilita/desabilita elementos da UI durante operações longas"""
        state = "disabled" if disabled else "normal"

        # Desabilitar/Reabilitar abas
        for tab_name in ["📦 Pacote", "⚙️ Configurações", "🐙 GitHub", "🔧 Dependências"]:
            tab = self.tab_view.tab(tab_name)
            for child in tab.winfo_children():
                try:
                    child.configure(state=state)
                except:
                    pass

        # Botão de geração
        if disabled:
            self.generate_btn.configure(state="disabled", text="⏳ Gerando...")
        else:
            self.generate_btn.configure(state="normal", text="🚀 Gerar Pacote Unity")

    def update_progress(self, value, message=""):
        self.progress_var.set(value / 100)
        if message:
            self.progress_messages.set(message)
            self.add_log(message)  # Mostra também no log
        self.root.update_idletasks()  # Força atualização da UI

    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        # Configurar cores baseadas no tipo de mensagem
        if message.startswith("✅") or message.startswith("🎉"):
            tag = "success"
        elif message.startswith("❌"):
            tag = "error"
        elif message.startswith("⚠️"):
            tag = "warning"
        else:
            tag = "info"

        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_entry + "\n", tag)
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def save_log(self):
        content = self.log_text.get("1.0", "end")
        if content.strip():
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.add_log(f"💾 Log salvo em: {filename}")

    def test_connection(self):
        self.add_log("🧪 Testando conexão com GitHub...")
        self.verify_github_credentials_direct()

    def verify_github_credentials_direct(self):
        def verify():
            self.show_loading_indicator(True)
            try:
                temp_github_manager = GitHubManager(self.config_manager)
                temp_github_manager.username = self.github_username.get()
                temp_github_manager.token = self.github_token.get()

                success, message = temp_github_manager.check_credentials()
                self.github_status_label.configure(
                    text=message,
                    text_color="green" if success else "red"
                )
                self.add_log(message)
            finally:
                self.show_loading_indicator(False)

        threading.Thread(target=verify, daemon=True).start()

    def show_loading_indicator(self, show=True):
        """Mostra/oculta indicador de carregamento durante operações longas"""
        if show and not hasattr(self, "loading_indicator"):
            self.loading_indicator = ctk.CTkLabel(
                self.root,
                text="⏳ Processando...",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#2B2B2B",
                corner_radius=10,
                width=200,
                height=50
            )
            self.loading_indicator.place(relx=0.5, rely=0.5, anchor="center")
        elif hasattr(self, "loading_indicator") and not show:
            self.loading_indicator.destroy()
            del self.loading_indicator

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def select_folder(self):
        folder = filedialog.askdirectory(
            title="Selecionar pasta de destino",
            initialdir=self.config_manager.get_value(key='last_directory', default=os.path.expanduser('~'))
        )
        if folder:
            self.folder_path.set(folder)
            self.config_manager.set_value(key='last_directory', value=folder)

    def verify_github_credentials(self):
        def verify():
            self.show_loading_indicator(True)
            try:
                success, message = self.github_manager.check_credentials()
                self.github_status_label.configure(
                    text=message,
                    text_color="green" if success else "red"
                )
                self.add_log(message)
            finally:
                self.show_loading_indicator(False)

        threading.Thread(target=verify, daemon=True).start()

    def save_config(self):
        configs = {
            'author_name': self.author_name.get(),
            'author_email': self.author_email.get(),
            'author_url': self.author_url.get(),
            'company_prefix': self.company_prefix.get(),
            'unity_version': self.unity_version.get()
        }

        for key, value in configs.items():
            self.config_manager.set_value(key=key, value=value)

        self.config_manager.set_value(section='github', key='username', value=self.github_username.get())
        self.config_manager.set_value(section='github', key='token', value=self.github_token.get())

        self.github_manager.username = self.github_username.get()
        self.github_manager.token = self.github_token.get()

        messagebox.showinfo("Sucesso", "✅ Configurações salvas com sucesso!")

    def create_debug_tab(self):
        tab = self.tab_view.tab("🐛 Debug")
        tab.grid_columnconfigure(0, weight=1)

        log_section = self.create_section(tab, "📝 Log de Atividades", 0)

        self.log_text = ctk.CTkTextbox(
            log_section,
            height=350,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.log_text.grid(row=1, column=0, sticky="ew", padx=12, pady=10)
        self.log_text.configure(state="disabled")  # Inicialmente desabilitado

        # Configurar tags para cores
        self.log_text.tag_config("success", foreground="#4CAF50")  # Verde
        self.log_text.tag_config("error", foreground="#F44336")  # Vermelho
        self.log_text.tag_config("warning", foreground="#FF9800")  # Laranja
        self.log_text.tag_config("info", foreground="#64B5F6")  # Azul

        control_frame = ctk.CTkFrame(log_section, fg_color="transparent")
        control_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        control_frame.grid_columnconfigure((0, 1, 2), weight=1)

        clear_btn = ctk.CTkButton(
            control_frame,
            text="🗑️ Limpar",
            command=self.clear_log,
            height=30
        )
        clear_btn.grid(row=0, column=0, padx=4)

        save_log_btn = ctk.CTkButton(
            control_frame,
            text="💾 Salvar",
            command=self.save_log,
            height=30
        )
        save_log_btn.grid(row=0, column=1, padx=4)

        test_btn = ctk.CTkButton(
            control_frame,
            text="🧪 Testar GitHub",
            command=self.test_connection,
            height=30
        )
        test_btn.grid(row=0, column=2, padx=4)

    def create_about_tab(self):
        tab = self.tab_view.tab("ℹ️ Sobre")
        tab.grid_columnconfigure(0, weight=1)

        about_section = self.create_section(tab, f"🚀 Unity Package Forge v{get_current_version()}", 0)

        # Barra de versão/informações
        version_frame = ctk.CTkFrame(about_section, fg_color="#333333")
        version_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=12)

        version_text = f"Versão: {get_current_version()} | Unity: {self.unity_version.get()}"
        version_label = ctk.CTkLabel(
            version_frame,
            text=version_text,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        version_label.pack(pady=5)

        info_text = f"""Unity Package Forge é uma ferramenta profissional para criar pacotes Unity
seguindo as melhores práticas e padrões da indústria.

✨ Funcionalidades:
• Geração automática de estrutura de pacotes
• Integração completa com GitHub
• Assembly Definitions com namespace correto
• Templates de documentação profissionais
• Semantic Release configurado
• Build automático multiplataforma

👨‍💻 Desenvolvido por: Nathan da Silva Miranda"""

        info_label = ctk.CTkLabel(
            about_section,
            text=info_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        info_label.grid(row=1, column=0, sticky="w", padx=15, pady=15)

        # Botões de ação
        actions_frame = ctk.CTkFrame(about_section, fg_color="transparent")
        actions_frame.grid(row=2, column=0, pady=10)

        update_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Verificar Atualizações",
            command=self.check_for_updates,
            width=180
        )
        update_btn.grid(row=0, column=0, padx=10)

        links_section = self.create_section(tab, "🔗 Links Úteis", 1)

        links_frame = ctk.CTkFrame(links_section, fg_color="transparent")
        links_frame.grid(row=1, column=0, padx=12, pady=10)
        links_frame.grid_columnconfigure((0, 1), weight=1)

        github_btn = ctk.CTkButton(
            links_frame,
            text="🐙 GitHub",
            command=lambda: self.open_url("https://github.com/Natteens/UnityPackageForge"),
            height=30,
            width=120
        )
        github_btn.grid(row=0, column=0, padx=4)

        unity_btn = ctk.CTkButton(
            links_frame,
            text="🎮 Unity Docs",
            command=lambda: self.open_url("https://docs.unity3d.com/Manual/upm-ui.html"),
            height=30,
            width=120
        )
        unity_btn.grid(row=0, column=1, padx=4)

    def check_for_updates(self):
        """Simula verificação de atualizações"""
        self.add_log("🔍 Verificando atualizações...")
        # Implementação real iria checar no GitHub
        self.root.after(1500, lambda: self.add_log("✅ Você está na versão mais recente!"))

    def load_ui_values(self):
        self.author_name.set(self.config_manager.get_value(key='author_name', default=''))
        self.author_email.set(self.config_manager.get_value(key='author_email', default=''))
        self.author_url.set(self.config_manager.get_value(key='author_url', default=''))
        self.company_prefix.set(self.config_manager.get_value(key='company_prefix', default='com.company'))
        self.unity_version.set(self.config_manager.get_value(key='unity_version', default='2021.3'))

        self.github_username.set(self.config_manager.get_value(section='github', key='username', default=''))
        self.github_token.set(self.config_manager.get_value(section='github', key='token', default=''))

        last_dir = self.config_manager.get_value(key='last_directory', default='')
        if last_dir and os.path.exists(last_dir):
            self.folder_path.set(last_dir)
        else:
            self.folder_path.set('')

        ctk.set_appearance_mode("dark")

    def setup_bindings(self):
        self.main_frame.bind("<Enter>", self._bind_mousewheel)
        self.main_frame.bind("<Leave>", self._unbind_mousewheel)

        self.author_name.trace('w', self._auto_save_config)
        self.author_email.trace('w', self._auto_save_config)
        self.author_url.trace('w', self._auto_save_config)
        self.company_prefix.trace('w', self._auto_save_config)
        self.unity_version.trace('w', self._auto_save_config)
        self.github_username.trace('w', self._auto_save_github)
        self.github_token.trace('w', self._auto_save_github)

    def _bind_mousewheel(self, event):
        self.main_frame.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.main_frame.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.main_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _auto_save_config(self, *args):
        if hasattr(self, '_auto_save_timer'):
            self.root.after_cancel(self._auto_save_timer)
        self._auto_save_timer = self.root.after(1000, self._do_auto_save_config)  # 1 second delay

    def _auto_save_github(self, *args):
        if hasattr(self, '_auto_save_github_timer'):
            self.root.after_cancel(self._auto_save_github_timer)
        self._auto_save_github_timer = self.root.after(1000, self._do_auto_save_github)  # 1 second delay

    def _do_auto_save_config(self):
        configs = {
            'author_name': self.author_name.get(),
            'author_email': self.author_email.get(),
            'author_url': self.author_url.get(),
            'company_prefix': self.company_prefix.get(),
            'unity_version': self.unity_version.get()
        }

        for key, value in configs.items():
            self.config_manager.set_value(key=key, value=value)

    def _do_auto_save_github(self):
        self.config_manager.set_value(section='github', key='username', value=self.github_username.get())
        self.config_manager.set_value(section='github', key='token', value=self.github_token.get())

        self.github_manager.username = self.github_username.get()
        self.github_manager.token = self.github_token.get()