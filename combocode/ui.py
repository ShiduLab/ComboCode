from __future__ import annotations

import sys
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from pathlib import Path

from .executor import ExecutionError, execute_route
from .exporter import export_goal
from .theme import apply_ttk_theme, system_prefers_dark


class ComboCodeUI:
    def __init__(
        self,
        kb,
        store,
        icon_png: Path | None = None,
        icon_ico: Path | None = None,
        brand_png: Path | None = None,
    ):
        self.kb = kb
        self.store = store
        self.current_hits = []
        self.current_goal = None
        self.current_route = None
        self.archive_rows = []
        self.mine_rows = []
        self.run_buttons = []
        self.archive_sort_col = 'goal'
        self.archive_sort_desc = False
        self.search_sort_col = None
        self.search_sort_desc = False
        self._system_dark = system_prefers_dark()
        self._icon_image = None
        self._brand_image = None
        self._native_icon_handles = []
        self._dropdown_menus = []
        self.icon_ico = icon_ico

        self.root = tk.Tk()
        self.root.title('ComboCode — ShiduLab')
        self.root.geometry('1240x800')
        self.root.minsize(980, 650)
        self.style = ttk.Style(self.root)
        self.palette = apply_ttk_theme(self.root, self.style, self._system_dark)
        self._apply_icon(icon_png, icon_ico)

        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value='Tutte')
        self.archive_query_var = tk.StringVar()
        self.archive_category_var = tk.StringVar(value='Tutte')
        self.archive_type_var = tk.StringVar(value='TUTTI')
        self.status_var = tk.StringVar(value='Scrivi cosa vuoi ottenere.')
        self.favorite_var = tk.StringVar(value='☆ Preferito')
        self.archive_summary_var = tk.StringVar()
        self.archive_detail_var = tk.StringVar()
        self.mine_query_var = tk.StringVar()
        self.mine_summary_var = tk.StringVar()
        self.mine_detail_var = tk.StringVar()

        self._build_ui(brand_png)
        self._bind_keys()
        self.refresh_all_views()
        self.search_entry.focus_set()
        self.root.after(250, self._force_windows_icon)
        self.root.after(1500, self._poll_system_theme)

    def _apply_icon(self, icon_png: Path | None, icon_ico: Path | None):
        try:
            if icon_png and icon_png.exists():
                self._icon_image = tk.PhotoImage(file=str(icon_png))
                self.root.iconphoto(True, self._icon_image)
        except Exception:
            self._icon_image = None
        try:
            if icon_ico and icon_ico.exists():
                self.root.iconbitmap(str(icon_ico))
        except Exception:
            pass

    def _force_windows_icon(self):
        if sys.platform != 'win32' or not self.icon_ico or not self.icon_ico.exists():
            return
        try:
            import ctypes
            from ctypes import wintypes

            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x0010
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1
            user32 = ctypes.windll.user32
            hwnd = wintypes.HWND(self.root.winfo_id())
            wrapper = user32.GetParent(hwnd) or hwnd
            path = str(self.icon_ico)
            small = user32.LoadImageW(None, path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
            big = user32.LoadImageW(None, path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
            if small:
                user32.SendMessageW(wrapper, WM_SETICON, ICON_SMALL, small)
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, small)
                self._native_icon_handles.append(small)
            if big:
                user32.SendMessageW(wrapper, WM_SETICON, ICON_BIG, big)
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, big)
                self._native_icon_handles.append(big)
        except Exception:
            pass

    def _poll_system_theme(self):
        dark = system_prefers_dark()
        if dark != self._system_dark:
            self._system_dark = dark
            self.palette = apply_ttk_theme(self.root, self.style, dark)
            self._retag_trees()
            self._restyle_dropdown_menus()
        self.root.after(1500, self._poll_system_theme)

    def _make_dropdown(self, parent, variable, values, callback, width=18):
        button = ttk.Menubutton(
            parent,
            textvariable=variable,
            style='Dropdown.TMenubutton',
            width=width,
        )
        menu = tk.Menu(button, tearoff=False)
        for value in values:
            menu.add_command(
                label=value,
                command=lambda v=value, var=variable, cb=callback: self._select_dropdown(var, v, cb),
            )
        button.configure(menu=menu)
        self._dropdown_menus.append(menu)
        self._style_dropdown_menu(menu)
        return button

    def _select_dropdown(self, variable, value, callback):
        variable.set(value)
        callback()

    def _style_dropdown_menu(self, menu):
        p = self.palette
        try:
            menu.configure(
                background=p.field,
                foreground=p.text,
                activebackground=p.accent,
                activeforeground=p.selection_text,
                selectcolor=p.accent,
                borderwidth=1,
                relief='solid',
                font=('Segoe UI', 10),
            )
        except Exception:
            pass

    def _restyle_dropdown_menus(self):
        for menu in self._dropdown_menus:
            self._style_dropdown_menu(menu)

    def _build_ui(self, brand_png: Path | None):
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        header = ttk.Frame(root, padding=(16, 14, 16, 8))
        header.grid(row=0, column=0, sticky='ew')
        header.columnconfigure(0, weight=1)

        search_box = ttk.Frame(header)
        search_box.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        search_box.columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(search_box, textvariable=self.search_var, style='Search.TEntry')
        self.search_entry.grid(row=0, column=0, sticky='ew')
        self.search_entry.bind('<KeyRelease>', lambda _e: self.refresh_results())

        self.clear_search_button = ttk.Button(
            search_box, text='×', width=3, style='Compact.TButton', command=self.clear_search
        )
        self.clear_search_button.grid(row=0, column=1, sticky='e', padx=(5, 0))

        cats = ['Tutte', *sorted(set([*self.kb.categories(), 'MIE']), key=str.lower)]
        self.category = self._make_dropdown(
            header,
            self.category_var,
            cats,
            self._on_category_changed,
            width=22,
        )
        self.category.grid(row=0, column=1, sticky='e')

        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=16, pady=(0, 8))
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

        self.search_tab = ttk.Frame(self.notebook, style='Panel.TFrame')
        self.all_tab = ttk.Frame(self.notebook, style='Panel.TFrame')
        self.mine_tab = ttk.Frame(self.notebook, style='Panel.TFrame')
        self.notebook.add(self.search_tab, text='CERCA')
        self.notebook.add(self.all_tab, text='TUTTI')
        self.notebook.add(self.mine_tab, text='MIE')

        self._build_search_tab()
        self._build_all_tab()
        self._build_mine_tab()
        self._build_footer(brand_png)

    def _build_footer(self, brand_png: Path | None):
        footer = ttk.Frame(self.root, style='Footer.TFrame', padding=(14, 4, 14, 10))
        footer.grid(row=2, column=0, sticky='ew')
        footer.columnconfigure(0, weight=1)

        status = ttk.Label(footer, textvariable=self.status_var, style='Muted.TLabel', anchor='w')
        status.grid(row=0, column=0, sticky='sw', padx=(0, 16))

        brand_frame = ttk.Frame(footer, style='Footer.TFrame', cursor='hand2')
        brand_frame.grid(row=0, column=1, sticky='se')
        brand_frame.bind('<Button-1>', lambda _e: webbrowser.open('https://github.com/ShiduLab'))

        brand_img = ttk.Label(brand_frame, style='Muted.TLabel', cursor='hand2')
        brand_img.grid(row=0, column=0, sticky='se', padx=(0, 7))
        brand_img.bind('<Button-1>', lambda _e: webbrowser.open('https://github.com/ShiduLab'))

        try:
            if brand_png and brand_png.exists():
                self._brand_image = tk.PhotoImage(file=str(brand_png))
                brand_img.configure(image=self._brand_image)
            else:
                brand_img.configure(text='☠')
        except Exception:
            brand_img.configure(text='☠')

        brand_text = ttk.Label(
            brand_frame, text='ShiduLab', style='Brand.TLabel', cursor='hand2'
        )
        brand_text.grid(row=0, column=1, sticky='s', pady=(0, 3))
        brand_text.bind('<Button-1>', lambda _e: webbrowser.open('https://github.com/ShiduLab'))

    def _build_search_tab(self):
        tab = self.search_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        main = ttk.Panedwindow(tab, orient=tk.HORIZONTAL)
        main.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)

        left = ttk.Frame(main, style='Panel.TFrame', padding=8)
        right = ttk.Frame(main, style='Panel.TFrame', padding=14)
        main.add(left, weight=2)
        main.add(right, weight=3)

        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self.result_tree = ttk.Treeview(left, columns=('cat',), show='tree headings', selectmode='browse')
        self.result_tree.heading('#0', text='Obiettivo', command=lambda: self.sort_search_results('goal'))
        self.result_tree.heading('cat', text='Categoria', command=lambda: self.sort_search_results('cat'))
        self.result_tree.column('#0', width=345, anchor='w')
        self.result_tree.column('cat', width=145, anchor='w')
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        yscroll = ttk.Scrollbar(left, orient='vertical', command=self.result_tree.yview)
        yscroll.grid(row=0, column=1, sticky='ns')
        self.result_tree.configure(yscrollcommand=yscroll.set)
        self.result_tree.bind('<<TreeviewSelect>>', self._on_goal_select)
        self.result_tree.bind('<Return>', lambda _e: self.route_tree.focus_set())

        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)

        self.title_label = ttk.Label(right, text='ComboCode', style='Title.TLabel')
        self.title_label.grid(row=0, column=0, sticky='w')
        self.desc_label = ttk.Label(right, text='Un obiettivo, più route.', style='Panel.TLabel', wraplength=690, justify='left')
        self.desc_label.grid(row=1, column=0, sticky='ew', pady=(4, 14))

        ttk.Label(right, text='ROUTE DISPONIBILI', style='Section.TLabel').grid(row=2, column=0, sticky='w')
        self.route_tree = ttk.Treeview(right, columns=('value', 'safety'), show='headings', selectmode='browse')
        self.route_tree.heading('value', text='Tipo / comando')
        self.route_tree.heading('safety', text='Stato')
        self.route_tree.column('value', width=620, anchor='w')
        self.route_tree.column('safety', width=120, anchor='center')
        self.route_tree.grid(row=3, column=0, sticky='nsew', pady=(5, 10))
        self.route_tree.bind('<<TreeviewSelect>>', self._on_route_select)
        self.route_tree.bind('<Double-1>', lambda _e: self.execute_selected())
        self.route_tree.bind('<Return>', lambda _e: self.execute_selected())

        self.route_detail = ttk.Label(right, text='', style='PanelMuted.TLabel', wraplength=690, justify='left')
        self.route_detail.grid(row=4, column=0, sticky='ew', pady=(0, 10))

        buttons = ttk.Frame(right, style='Panel.TFrame')
        buttons.grid(row=5, column=0, sticky='ew')
        run_button = ttk.Button(buttons, text='APRI / ESEGUI', style='Accent.TButton', command=self.execute_selected)
        run_button.pack(side='left')
        self.run_buttons.append(run_button)
        ttk.Button(buttons, text='COPIA', command=self.copy_selected).pack(side='left', padx=7)
        ttk.Button(buttons, textvariable=self.favorite_var, command=self.toggle_favorite).pack(side='left')
        ttk.Button(buttons, text='ESPORTA .MD', command=self.export_selected).pack(side='left', padx=7)
        ttk.Button(buttons, text='SALVA NELLE MIE', command=self.duplicate_selected_to_mine).pack(side='left')
        ttk.Button(buttons, text='FONTE', command=self.open_source).pack(side='left', padx=(7, 0))

    def _build_all_tab(self):
        tab = self.all_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        bar = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 8, 8, 8))
        bar.grid(row=0, column=0, sticky='ew')
        bar.columnconfigure(1, weight=1)

        ttk.Label(bar, text='Filtra archivio:', style='Panel.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 6))
        self.archive_search = ttk.Entry(bar, textvariable=self.archive_query_var)
        self.archive_search.grid(row=0, column=1, sticky='ew', padx=(0, 10))
        self.archive_search.bind('<KeyRelease>', lambda _e: self.refresh_archive())

        ttk.Label(bar, text='Tipo:', style='Panel.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        kinds = ['TUTTI', *self.kb.route_kinds()]
        self.archive_type = self._make_dropdown(
            bar,
            self.archive_type_var,
            kinds,
            self.refresh_archive,
            width=12,
        )
        self.archive_type.grid(row=0, column=3, sticky='w', padx=(0, 10))

        ttk.Label(bar, text='Categoria:', style='Panel.TLabel').grid(row=0, column=4, sticky='w', padx=(0, 5))
        archive_cats = ['Tutte', *sorted(set([*self.kb.categories(), 'MIE']), key=str.lower)]
        self.archive_category = self._make_dropdown(
            bar,
            self.archive_category_var,
            archive_cats,
            self.refresh_archive,
            width=19,
        )
        self.archive_category.grid(row=0, column=5, sticky='w', padx=(0, 10))

        ttk.Button(bar, text='AZZERA', command=self.reset_archive_filters).grid(row=0, column=6, sticky='e')

        summary_bar = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 0, 8, 4))
        summary_bar.grid(row=2, column=0, sticky='ew')
        summary_bar.columnconfigure(0, weight=1)
        ttk.Label(summary_bar, textvariable=self.archive_summary_var, style='PanelMuted.TLabel', anchor='e').grid(
            row=0, column=0, sticky='e'
        )

        table_frame = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 0, 8, 4))
        table_frame.grid(row=1, column=0, sticky='nsew')
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.archive_tree = ttk.Treeview(
            table_frame,
            columns=('goal', 'kind', 'value', 'cat', 'safety', 'verified'),
            show='headings',
            selectmode='browse',
        )
        headings = [
            ('goal', 'Obiettivo', 255, 'w'),
            ('kind', 'Tipo', 82, 'center'),
            ('value', 'Comando / combinazione', 390, 'w'),
            ('cat', 'Categoria', 155, 'w'),
            ('safety', 'Sicurezza', 100, 'center'),
            ('verified', 'Verifica', 210, 'w'),
        ]
        for col, title, width, anchor in headings:
            self.archive_tree.heading(col, text=title, command=lambda c=col: self.sort_archive(c))
            self.archive_tree.column(col, width=width, anchor=anchor)
        self.archive_tree.grid(row=0, column=0, sticky='nsew')

        ay = ttk.Scrollbar(table_frame, orient='vertical', command=self.archive_tree.yview)
        ay.grid(row=0, column=1, sticky='ns')
        ax = ttk.Scrollbar(table_frame, orient='horizontal', command=self.archive_tree.xview)
        ax.grid(row=1, column=0, sticky='ew')
        self.archive_tree.configure(yscrollcommand=ay.set, xscrollcommand=ax.set)
        self.archive_tree.bind('<<TreeviewSelect>>', self._on_archive_select)
        self.archive_tree.bind('<Double-1>', lambda _e: self.execute_selected())
        self.archive_tree.bind('<Return>', lambda _e: self.execute_selected())

        detail = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 4, 8, 8))
        detail.grid(row=3, column=0, sticky='ew')
        detail.columnconfigure(0, weight=1)
        ttk.Label(detail, textvariable=self.archive_detail_var, style='PanelMuted.TLabel', wraplength=850, justify='left').grid(
            row=0, column=0, sticky='ew', padx=(0, 10)
        )

        buttons = ttk.Frame(detail, style='Panel.TFrame')
        buttons.grid(row=0, column=1, sticky='e')
        run_button = ttk.Button(buttons, text='APRI / ESEGUI', style='Accent.TButton', command=self.execute_selected)
        run_button.pack(side='left')
        self.run_buttons.append(run_button)
        ttk.Button(buttons, text='COPIA', command=self.copy_selected).pack(side='left', padx=7)
        ttk.Button(buttons, text='SALVA NELLE MIE', command=self.duplicate_selected_to_mine).pack(side='left')
        ttk.Button(buttons, text='FONTE', command=self.open_source).pack(side='left', padx=(7, 0))

    def _build_mine_tab(self):
        tab = self.mine_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        bar = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 8, 8, 8))
        bar.grid(row=0, column=0, sticky='ew')
        bar.columnconfigure(1, weight=1)

        ttk.Label(bar, text='Le mie shortcut:', style='Panel.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 6))
        self.mine_search = ttk.Entry(bar, textvariable=self.mine_query_var)
        self.mine_search.grid(row=0, column=1, sticky='ew', padx=(0, 6))
        self.mine_search.bind('<KeyRelease>', lambda _e: self.refresh_mine())
        ttk.Button(bar, text='×', width=3, style='Compact.TButton', command=self.clear_mine_search).grid(row=0, column=2, padx=(0, 12))
        ttk.Button(bar, text='+ AGGIUNGI SHORTCUT', style='Accent.TButton', command=self.add_user_shortcut).grid(row=0, column=3, padx=(0, 6))
        ttk.Button(bar, text='IMPORTA', command=self.import_user_shortcuts).grid(row=0, column=4, padx=(0, 6))
        ttk.Button(bar, text='ESPORTA', command=self.export_user_shortcuts).grid(row=0, column=5)

        table = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 0, 8, 4))
        table.grid(row=1, column=0, sticky='nsew')
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)

        self.mine_tree = ttk.Treeview(
            table,
            columns=('goal', 'kind', 'value', 'context', 'safety'),
            show='headings',
            selectmode='browse',
        )
        cols = [
            ('goal', 'A cosa serve', 260, 'w'),
            ('kind', 'Tipo', 110, 'center'),
            ('value', 'Tasti / stringa / gesto', 365, 'w'),
            ('context', 'Contesto', 210, 'w'),
            ('safety', 'Sicurezza', 100, 'center'),
        ]
        for col, title, width, align in cols:
            self.mine_tree.heading(col, text=title)
            self.mine_tree.column(col, width=width, anchor=align)
        self.mine_tree.grid(row=0, column=0, sticky='nsew')
        my = ttk.Scrollbar(table, orient='vertical', command=self.mine_tree.yview)
        my.grid(row=0, column=1, sticky='ns')
        mx = ttk.Scrollbar(table, orient='horizontal', command=self.mine_tree.xview)
        mx.grid(row=1, column=0, sticky='ew')
        self.mine_tree.configure(yscrollcommand=my.set, xscrollcommand=mx.set)
        self.mine_tree.bind('<<TreeviewSelect>>', self._on_mine_select)
        self.mine_tree.bind('<Double-1>', lambda _e: self.execute_selected())
        self.mine_tree.bind('<Return>', lambda _e: self.execute_selected())

        lower = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 4, 8, 8))
        lower.grid(row=2, column=0, sticky='ew')
        lower.columnconfigure(0, weight=1)
        ttk.Label(lower, textvariable=self.mine_detail_var, style='PanelMuted.TLabel', wraplength=760, justify='left').grid(
            row=0, column=0, sticky='ew', padx=(0, 10)
        )

        buttons = ttk.Frame(lower, style='Panel.TFrame')
        buttons.grid(row=0, column=1, sticky='e')
        run_button = ttk.Button(buttons, text='APRI / ESEGUI', style='Accent.TButton', command=self.execute_selected)
        run_button.pack(side='left')
        self.run_buttons.append(run_button)
        ttk.Button(buttons, text='COPIA', command=self.copy_selected).pack(side='left', padx=6)
        ttk.Button(buttons, text='MODIFICA', command=self.edit_user_shortcut).pack(side='left')
        ttk.Button(buttons, text='ELIMINA', command=self.delete_user_shortcut).pack(side='left', padx=(6, 0))

        summary = ttk.Frame(tab, style='Panel.TFrame', padding=(8, 0, 8, 8))
        summary.grid(row=3, column=0, sticky='ew')
        summary.columnconfigure(0, weight=1)
        ttk.Label(summary, textvariable=self.mine_summary_var, style='PanelMuted.TLabel', anchor='e').grid(row=0, column=0, sticky='e')

    def clear_mine_search(self):
        self.mine_query_var.set('')
        self.refresh_mine()
        self.mine_search.focus_set()
        return 'break'

    def _route_handler_for_kind(self, kind: str) -> tuple[str, bool]:
        kind = kind.upper()
        mapping = {
            'HOTKEY': ('none', True),
            'MOUSE': ('manual', False),
            'KEY+MOUSE': ('manual', False),
            'RUN': ('cmd_run', True),
            'CMD': ('cmd_keep', True),
            'POWERSHELL': ('powershell', True),
            'URI': ('uri', True),
            'APP': ('start', True),
            'ALTRO': ('manual', False),
        }
        return mapping.get(kind, ('manual', False))

    def _shortcut_form(self, initial: dict | None = None) -> dict | None:
        initial = initial or {}
        initial_route = (initial.get('routes') or [{}])[0]
        dialog = tk.Toplevel(self.root)
        dialog.title('ComboCode — Aggiungi shortcut' if not initial.get('id') else 'ComboCode — Modifica shortcut')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, False)
        try:
            if self.icon_ico and self.icon_ico.exists():
                dialog.iconbitmap(str(self.icon_ico))
        except Exception:
            pass

        frame = ttk.Frame(dialog, padding=18)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.columnconfigure(1, weight=1)

        name_var = tk.StringVar(value=initial.get('name', ''))
        kind_var = tk.StringVar(value=initial_route.get('kind', 'HOTKEY'))
        value_var = tk.StringVar(value=initial_route.get('value', ''))
        context_var = tk.StringVar(value=initial.get('context', ''))
        aliases_var = tk.StringVar(value=', '.join(initial.get('aliases', [])))
        safety_var = tk.StringVar(value=initial_route.get('safety', 'SAFE'))

        ttk.Label(frame, text='A cosa serve', style='Panel.TLabel').grid(row=0, column=0, sticky='w', pady=5, padx=(0, 12))
        name_entry = ttk.Entry(frame, textvariable=name_var, width=55)
        name_entry.grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text='Tipo', style='Panel.TLabel').grid(row=1, column=0, sticky='w', pady=5, padx=(0, 12))
        kind_button = self._make_dropdown(
            frame, kind_var,
            ['HOTKEY', 'MOUSE', 'KEY+MOUSE', 'RUN', 'CMD', 'POWERSHELL', 'URI', 'APP', 'ALTRO'],
            lambda: None, width=20,
        )
        kind_button.grid(row=1, column=1, sticky='w', pady=5)

        ttk.Label(frame, text='Tasti / stringa / gesto', style='Panel.TLabel').grid(row=2, column=0, sticky='w', pady=5, padx=(0, 12))
        value_entry = ttk.Entry(frame, textvariable=value_var)
        value_entry.grid(row=2, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text='Contesto', style='Panel.TLabel').grid(row=3, column=0, sticky='w', pady=5, padx=(0, 12))
        ttk.Entry(frame, textvariable=context_var).grid(row=3, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text='Alias (separati da virgola)', style='Panel.TLabel').grid(row=4, column=0, sticky='w', pady=5, padx=(0, 12))
        ttk.Entry(frame, textvariable=aliases_var).grid(row=4, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text='Sicurezza', style='Panel.TLabel').grid(row=5, column=0, sticky='w', pady=5, padx=(0, 12))
        safety_button = self._make_dropdown(frame, safety_var, ['SAFE', 'ELEVATED', 'DESTRUCTIVE'], lambda: None, width=20)
        safety_button.grid(row=5, column=1, sticky='w', pady=5)

        ttk.Label(frame, text='Note', style='Panel.TLabel').grid(row=6, column=0, sticky='nw', pady=5, padx=(0, 12))
        notes = tk.Text(frame, height=5, width=55, wrap='word')
        notes.grid(row=6, column=1, sticky='ew', pady=5)
        notes.insert('1.0', initial_route.get('note', ''))
        notes.configure(bg=self.palette.field, fg=self.palette.text, insertbackground=self.palette.text, relief='flat', highlightthickness=1, highlightbackground=self.palette.border)

        hint = ttk.Label(
            frame,
            text='Esempi: CTRL + ALT + S · CTRL + WHEEL_UP · control keyboard · ms-settings:display',
            style='PanelMuted.TLabel',
        )
        hint.grid(row=7, column=1, sticky='w', pady=(2, 10))

        result: dict[str, dict | None] = {'goal': None}

        def save():
            name = name_var.get().strip()
            value = value_var.get().strip()
            if not name or not value:
                messagebox.showwarning('ComboCode', 'Compila almeno “A cosa serve” e “Tasti / stringa / gesto”.', parent=dialog)
                return
            kind = kind_var.get().strip().upper()
            handler, executable = self._route_handler_for_kind(kind)
            aliases = [x.strip() for x in aliases_var.get().split(',') if x.strip()]
            context = context_var.get().strip() or 'Generale'
            note = notes.get('1.0', 'end').strip()
            goal = {
                'id': initial.get('id') or f'user.{uuid.uuid4().hex}',
                'name': name,
                'category': 'MIE',
                'context': context,
                'origin': 'user',
                'description': f'Shortcut personale · {context}',
                'aliases': aliases,
                'keywords': ['personale', 'mia', 'shortcut', context, kind, *aliases],
                'platform': 'Personalizzata',
                'routes': [{
                    'kind': kind,
                    'value': value,
                    'handler': handler,
                    'executable': executable,
                    'safety': safety_var.get().strip().upper() or 'SAFE',
                    'verified': 'PERSONALE',
                    'source_label': 'Creata dall’utente',
                    'note': note,
                }],
            }
            result['goal'] = goal
            dialog.destroy()

        actions = ttk.Frame(frame)
        actions.grid(row=8, column=1, sticky='e', pady=(8, 0))
        ttk.Button(actions, text='ANNULLA', command=dialog.destroy).pack(side='right')
        ttk.Button(actions, text='SALVA', style='Accent.TButton', command=save).pack(side='right', padx=(0, 7))

        dialog.protocol('WM_DELETE_WINDOW', dialog.destroy)
        dialog.bind('<Escape>', lambda _e: dialog.destroy())
        name_entry.focus_set()
        dialog.wait_window()
        return result['goal']

    def add_user_shortcut(self):
        goal = self._shortcut_form()
        if not goal:
            return 'break'
        saved = self.store.upsert_user_goal(goal)
        self.kb.upsert_goal(saved)
        self.refresh_all_views()
        self.refresh_mine(select_id=saved['id'])
        self.notebook.select(2)
        self.status_var.set(f"Aggiunta shortcut personale: {saved['name']}")
        return 'break'

    def edit_user_shortcut(self):
        if not self.current_goal or self.current_goal.get('origin') != 'user':
            messagebox.showinfo('ComboCode', 'Seleziona una voce nella pagina MIE.')
            return 'break'
        goal = self._shortcut_form(self.current_goal)
        if not goal:
            return 'break'
        saved = self.store.upsert_user_goal(goal)
        self.kb.upsert_goal(saved)
        self.refresh_all_views()
        self.refresh_mine(select_id=saved['id'])
        self.notebook.select(2)
        self.status_var.set(f"Modificata shortcut personale: {saved['name']}")
        return 'break'

    def delete_user_shortcut(self):
        if not self.current_goal or self.current_goal.get('origin') != 'user':
            messagebox.showinfo('ComboCode', 'Seleziona una voce personale da eliminare.')
            return 'break'
        goal_id = self.current_goal['id']
        name = self.current_goal.get('name', '')
        if not messagebox.askyesno('ComboCode — Elimina', f'Eliminare “{name}” dalle MIE?'):
            return 'break'
        self.store.delete_user_goal(goal_id)
        self.kb.remove_goal(goal_id)
        self.current_goal = None
        self.current_route = None
        self.refresh_all_views()
        self.refresh_mine()
        self.status_var.set(f'Eliminata shortcut personale: {name}')
        return 'break'

    def duplicate_selected_to_mine(self):
        if not self.current_goal or not self.current_route:
            return 'break'
        initial = {
            'name': self.current_goal.get('name', ''),
            'context': self.current_goal.get('context') or self.current_goal.get('category', ''),
            'aliases': list(self.current_goal.get('aliases', [])),
            'routes': [dict(self.current_route)],
        }
        initial['routes'][0]['verified'] = 'PERSONALE'
        initial['routes'][0]['source_label'] = 'Duplicata e personalizzata dall’utente'
        goal = self._shortcut_form(initial)
        if not goal:
            return 'break'
        saved = self.store.upsert_user_goal(goal)
        self.kb.upsert_goal(saved)
        self.refresh_all_views()
        self.refresh_mine(select_id=saved['id'])
        self.notebook.select(2)
        self.status_var.set(f"Salvata nelle MIE: {saved['name']}")
        return 'break'

    def refresh_mine(self, select_id: str | None = None):
        if not hasattr(self, 'mine_tree'):
            return
        query = self.mine_query_var.get().strip().casefold()
        rows = []
        for goal in self.kb.user_goals():
            route = (goal.get('routes') or [{}])[0]
            blob = ' '.join([
                goal.get('name', ''), goal.get('context', ''), goal.get('description', ''),
                ' '.join(goal.get('aliases', [])), route.get('kind', ''), route.get('value', ''), route.get('note', '')
            ]).casefold()
            if query and query not in blob:
                continue
            rows.append((goal, route))
        rows.sort(key=lambda x: (x[0].get('context', '').casefold(), x[0].get('name', '').casefold()))
        self.mine_rows = rows

        for item in self.mine_tree.get_children():
            self.mine_tree.delete(item)
        for idx, (goal, route) in enumerate(rows):
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.mine_tree.insert('', 'end', iid=goal['id'], values=(
                goal.get('name', ''), route.get('kind', ''), route.get('value', ''),
                goal.get('context', ''), route.get('safety', 'SAFE')
            ), tags=(tag,))
        self._retag_tree(self.mine_tree)
        self.mine_summary_var.set(f'{len(rows)} shortcut personali · archivio: {self.store.shortcuts_path}')
        self.mine_detail_var.set('')

        if select_id and self.mine_tree.exists(select_id):
            self.mine_tree.selection_set(select_id)
            self.mine_tree.focus(select_id)
            self._on_mine_select()
        elif rows and self.notebook.index(self.notebook.select()) == 2:
            first = rows[0][0]['id']
            self.mine_tree.selection_set(first)
            self.mine_tree.focus(first)
            self._on_mine_select()
        self._update_status_for_tab()

    def _on_mine_select(self, _event=None):
        sel = self.mine_tree.selection()
        if not sel:
            return
        goal = self.kb.by_id.get(sel[0])
        if not goal:
            return
        route = (goal.get('routes') or [{}])[0]
        self.current_goal = goal
        self.current_route = route
        self.mine_detail_var.set(
            f"{goal.get('name','')} · {goal.get('context','')}\n"
            f"{route.get('note','')} · {route.get('kind','')} · {route.get('value','')}"
        )
        self._sync_run_buttons()

    def export_user_shortcuts(self):
        path = filedialog.asksaveasfilename(
            title='Esporta le MIE shortcut',
            defaultextension='.json',
            initialfile='ComboCode_user_shortcuts.json',
            filetypes=[('JSON', '*.json')],
        )
        if path:
            self.store.export_user_shortcuts(Path(path))
            self.status_var.set(f'MIE esportate: {path}')
        return 'break'

    def import_user_shortcuts(self):
        path = filedialog.askopenfilename(
            title='Importa shortcut personali',
            filetypes=[('JSON', '*.json'), ('Tutti i file', '*.*')],
        )
        if not path:
            return 'break'
        try:
            count = self.store.import_user_shortcuts(Path(path), merge=True)
        except Exception as exc:
            messagebox.showerror('ComboCode', f'Importazione non riuscita:\n{exc}')
            return 'break'
        # sincronizza la KB: rimuove i vecchi user e ricarica il file persistente.
        for goal in list(self.kb.user_goals()):
            self.kb.remove_goal(goal['id'])
        for goal in self.store.load_user_goals():
            self.kb.upsert_goal(goal)
        self.refresh_all_views()
        self.refresh_mine()
        self.status_var.set(f'Importate/aggiornate {count} shortcut personali.')
        return 'break'

    def _bind_keys(self):
        self.root.bind('<Control-k>', lambda _e: self.focus_search())
        self.root.bind('<Control-l>', lambda _e: self.focus_search())
        self.root.bind('<Control-Key-1>', lambda _e: self.select_tab(0))
        self.root.bind('<Control-Key-2>', lambda _e: self.select_tab(1))
        self.root.bind('<Control-Key-3>', lambda _e: self.select_tab(2))
        self.root.bind('<Control-Shift-A>', lambda _e: self.add_user_shortcut())
        self.root.bind('<Control-c>', lambda _e: self.copy_selected())
        self.root.bind('<Control-f>', lambda _e: self.toggle_favorite())
        self.root.bind('<Control-m>', lambda _e: self.export_selected())
        self.root.bind('<F1>', lambda _e: self.show_help())
        self.root.bind('<Escape>', lambda _e: self.root.destroy())
        self.root.bind('<Down>', self._smart_down)

    def select_tab(self, index: int):
        self.notebook.select(index)
        if index == 0:
            self.search_entry.focus_set()
        elif index == 1:
            self.archive_tree.focus_set()
        else:
            self.mine_search.focus_set()
        self._update_status_for_tab()
        return 'break'

    def _smart_down(self, _event):
        focus = self.root.focus_get()
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 0:
            if focus != self.search_entry:
                return None
            tree = self.result_tree
        elif tab_index == 1:
            if focus != self.archive_search:
                return None
            tree = self.archive_tree
        else:
            if focus != self.mine_search:
                return None
            tree = self.mine_tree
        children = tree.get_children()
        if children:
            tree.focus_set()
            first = children[0]
            tree.selection_set(first)
            tree.focus(first)
            return 'break'
        return None

    def focus_search(self):
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 0:
            entry = self.search_entry
        elif tab_index == 1:
            entry = self.archive_search
        else:
            entry = self.mine_search
        entry.focus_set()
        entry.selection_range(0, tk.END)
        return 'break'

    def clear_search(self):
        self.search_var.set('')
        self.search_sort_col = None
        self.search_sort_desc = False
        self.refresh_results()
        self.search_entry.focus_set()
        return 'break'

    def _on_category_changed(self, _event=None):
        if not hasattr(self, 'result_tree'):
            return
        self.refresh_results()

    def sort_search_results(self, column: str):
        if self.search_sort_col == column:
            self.search_sort_desc = not self.search_sort_desc
        else:
            self.search_sort_col = column
            self.search_sort_desc = False
        self.refresh_results()

    def _update_search_headings(self):
        goal_label = 'Obiettivo'
        cat_label = 'Categoria'
        if self.search_sort_col == 'goal':
            goal_label += ' ↓' if self.search_sort_desc else ' ↑'
        elif self.search_sort_col == 'cat':
            cat_label += ' ↓' if self.search_sort_desc else ' ↑'
        self.result_tree.heading('#0', text=goal_label, command=lambda: self.sort_search_results('goal'))
        self.result_tree.heading('cat', text=cat_label, command=lambda: self.sort_search_results('cat'))

    def refresh_all_views(self):
        self.refresh_results()
        self.refresh_archive()
        self.refresh_mine()
        self._update_status_for_tab()

    def refresh_results(self):
        query = self.search_var.get()
        category = self.category_var.get()
        self.current_hits = self.kb.search(query, category)
        if self.search_sort_col == 'goal':
            self.current_hits.sort(
                key=lambda h: h.goal.get('name', '').casefold(),
                reverse=self.search_sort_desc,
            )
        elif self.search_sort_col == 'cat':
            self.current_hits.sort(
                key=lambda h: (
                    h.goal.get('category', '').casefold(),
                    h.goal.get('name', '').casefold(),
                ),
                reverse=self.search_sort_desc,
            )
        self._update_search_headings()
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for idx, hit in enumerate(self.current_hits):
            goal = hit.goal
            star = '★ ' if self.store.is_favorite(goal['id']) else ''
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.result_tree.insert('', 'end', iid=goal['id'], text=star + goal['name'], values=(goal.get('category', ''),), tags=(tag,))
        self._retag_tree(self.result_tree)
        if self.current_hits:
            first = self.current_hits[0].goal['id']
            self.result_tree.selection_set(first)
            self.result_tree.focus(first)
            self._show_goal(self.kb.by_id[first])
        else:
            self._clear_goal()
        self._update_status_for_tab()

    def refresh_archive(self):
        query = self.archive_query_var.get()
        category = self.archive_category_var.get()
        kind = self.archive_type_var.get()
        self.archive_rows = self.kb.route_rows(
            query=query,
            category=category,
            kind=kind,
            sort_by=self.archive_sort_col,
            descending=self.archive_sort_desc,
        )

        for item in self.archive_tree.get_children():
            self.archive_tree.delete(item)

        for idx, row in enumerate(self.archive_rows):
            route = row.route
            goal = row.goal
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.archive_tree.insert(
                '',
                'end',
                iid=str(idx),
                values=(
                    goal.get('name', ''),
                    route.get('kind', ''),
                    route.get('value', ''),
                    goal.get('category', ''),
                    route.get('safety', 'SAFE'),
                    route.get('verified', 'non verificato'),
                ),
                tags=(tag,),
            )

        self._retag_tree(self.archive_tree)
        stats = self.kb.stats()
        showing = len(self.archive_rows)
        sort_arrow = '↓' if self.archive_sort_desc else '↑'
        self.archive_summary_var.set(
            f"{showing} route visualizzate · archivio: {stats['goals']} obiettivi / {stats['routes']} route · "
            f"ordine {self._sort_label(self.archive_sort_col)} {sort_arrow}"
        )
        self.archive_detail_var.set('')
        self._update_archive_headings()
        self._update_status_for_tab()

    def _sort_label(self, col: str) -> str:
        return {
            'goal': 'Obiettivo', 'kind': 'Tipo', 'value': 'Comando', 'cat': 'Categoria',
            'safety': 'Sicurezza', 'verified': 'Verifica'
        }.get(col, col)

    def _update_archive_headings(self):
        labels = {
            'goal': 'Obiettivo', 'kind': 'Tipo', 'value': 'Comando / combinazione', 'cat': 'Categoria',
            'safety': 'Sicurezza', 'verified': 'Verifica'
        }
        for col, label in labels.items():
            marker = ''
            if col == self.archive_sort_col:
                marker = ' ↓' if self.archive_sort_desc else ' ↑'
            self.archive_tree.heading(col, text=label + marker, command=lambda c=col: self.sort_archive(c))

    def sort_archive(self, column: str):
        if self.archive_sort_col == column:
            self.archive_sort_desc = not self.archive_sort_desc
        else:
            self.archive_sort_col = column
            self.archive_sort_desc = False
        self.refresh_archive()

    def reset_archive_filters(self):
        self.archive_query_var.set('')
        self.archive_type_var.set('TUTTI')
        self.archive_category_var.set('Tutte')
        self.archive_sort_col = 'goal'
        self.archive_sort_desc = False
        self.search_sort_col = None
        self.search_sort_desc = False
        self.refresh_archive()
        self.archive_search.focus_set()

    def _retag_trees(self):
        self._retag_tree(self.result_tree)
        self._retag_tree(self.route_tree)
        self._retag_tree(self.archive_tree)
        if hasattr(self, 'mine_tree'):
            self._retag_tree(self.mine_tree)

    def _retag_tree(self, tree):
        p = self.palette
        tree.tag_configure('even', background=p.panel)
        tree.tag_configure('odd', background=p.panel_alt)

    def _on_goal_select(self, _event=None):
        sel = self.result_tree.selection()
        if sel:
            self._show_goal(self.kb.by_id[sel[0]])

    def _show_goal(self, goal):
        self.current_goal = goal
        self.title_label.configure(text=goal['name'])
        self.desc_label.configure(text=goal.get('description', ''))
        self.favorite_var.set('★ Preferito' if self.store.is_favorite(goal['id']) else '☆ Preferito')
        for item in self.route_tree.get_children():
            self.route_tree.delete(item)
        for idx, route in enumerate(goal.get('routes', [])):
            display = f"{route.get('kind','ROUTE')}   {route.get('value','')}"
            safety = route.get('safety', 'SAFE')
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.route_tree.insert('', 'end', iid=str(idx), values=(display, safety), tags=(tag,))
        self._retag_tree(self.route_tree)
        if goal.get('routes'):
            self.route_tree.selection_set('0')
            self.route_tree.focus('0')
            self._select_route(0)
        else:
            self.current_route = None
            self._sync_run_buttons()

    def _clear_goal(self):
        self.current_goal = None
        self.current_route = None
        self.title_label.configure(text='ComboCode')
        self.desc_label.configure(text='Un obiettivo, più route.')
        for item in self.route_tree.get_children():
            self.route_tree.delete(item)
        self.route_detail.configure(text='')
        self.archive_detail_var.set('')
        self._sync_run_buttons()

    def _on_route_select(self, _event=None):
        sel = self.route_tree.selection()
        if sel and self.current_goal:
            self._select_route(int(sel[0]))

    def _select_route(self, idx):
        routes = self.current_goal.get('routes', []) if self.current_goal else []
        if not 0 <= idx < len(routes):
            return
        self.current_route = routes[idx]
        note = self.current_route.get('note', '')
        verified = self.current_route.get('verified', 'non verificato')
        platform = self.current_goal.get('platform', '')
        lines = [note, f'Verifica: {verified}']
        if platform:
            lines.append(f'Compatibilità: {platform}')
        self.route_detail.configure(text='\n'.join(x for x in lines if x).strip())
        self._sync_run_buttons()

    def _on_archive_select(self, _event=None):
        sel = self.archive_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if not 0 <= idx < len(self.archive_rows):
            return
        row = self.archive_rows[idx]
        self.current_goal = row.goal
        self.current_route = row.route
        self.favorite_var.set('★ Preferito' if self.store.is_favorite(row.goal['id']) else '☆ Preferito')
        note = row.route.get('note', '')
        verified = row.route.get('verified', 'non verificato')
        platform = row.goal.get('platform', '')
        self.archive_detail_var.set(
            f"{row.goal.get('name','')} — {row.goal.get('description','')}\n"
            f"{note} · Verifica: {verified} · Compatibilità: {platform}".strip()
        )
        self._sync_run_buttons()

    def _sync_run_buttons(self):
        can_run = bool(self.current_route)
        for button in self.run_buttons:
            if can_run:
                button.state(['!disabled'])
            else:
                button.state(['disabled'])

    def copy_selected(self):
        if not self.current_route:
            return 'break'
        value = self.current_route.get('value', '')
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.status_var.set(f'Copiato: {value}')
        return 'break'

    def execute_selected(self):
        if not self.current_goal or not self.current_route:
            return 'break'
        safety = str(self.current_route.get('safety', 'SAFE')).upper()
        value = self.current_route.get('value', '')
        if safety == 'ELEVATED':
            ok = messagebox.askyesno(
                'ComboCode — Conferma',
                f'Questa route può richiedere privilegi amministrativi.\n\n{value}\n\nEseguire?'
            )
            if not ok:
                return 'break'
        elif safety == 'DESTRUCTIVE':
            ok = messagebox.askyesno(
                'ComboCode — ATTENZIONE',
                f'Questa route può modificare o cancellare dati/configurazioni.\n\n{value}\n\nVuoi eseguirla davvero?'
            )
            if not ok:
                return 'break'
        try:
            execute_route(self.current_route)
            self.store.add_history(self.current_goal['id'])
            self.status_var.set(f"Eseguito: {self.current_route.get('value','')}")
        except ExecutionError as exc:
            messagebox.showinfo('ComboCode', str(exc))
        return 'break'

    def toggle_favorite(self):
        if not self.current_goal:
            return 'break'
        state = self.store.toggle_favorite(self.current_goal['id'])
        self.favorite_var.set('★ Preferito' if state else '☆ Preferito')
        iid = self.current_goal['id']
        if self.result_tree.exists(iid):
            self.result_tree.item(iid, text=('★ ' if state else '') + self.current_goal['name'])
        return 'break'

    def export_selected(self):
        if not self.current_goal:
            return 'break'
        safe_name = ''.join(ch if ch.isalnum() or ch in ' _-' else '_' for ch in self.current_goal['name']).strip()
        path = filedialog.asksaveasfilename(
            title='Esporta nota Obsidian',
            defaultextension='.md',
            initialfile=safe_name + '.md',
            filetypes=[('Markdown', '*.md')],
        )
        if path:
            export_goal(self.current_goal, Path(path))
            self.status_var.set(f'Nota Obsidian esportata: {path}')
        return 'break'

    def open_source(self):
        if not self.current_route:
            return 'break'
        source = (self.current_route.get('source') or '').strip()
        source_label = self.current_route.get('source_label') or source
        if source.startswith('http://') or source.startswith('https://'):
            webbrowser.open(source)
        elif source_label:
            messagebox.showinfo('ComboCode — Fonte', str(source_label))
        else:
            messagebox.showinfo('ComboCode', 'Nessuna fonte associata a questa route.')
        return 'break'

    def _on_tab_changed(self, _event=None):
        if self.notebook.index(self.notebook.select()) == 2 and hasattr(self, 'mine_tree'):
            if not self.mine_tree.selection() and self.mine_tree.get_children():
                first = self.mine_tree.get_children()[0]
                self.mine_tree.selection_set(first)
                self.mine_tree.focus(first)
                self._on_mine_select()
        self._update_status_for_tab()

    def _update_status_for_tab(self):
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 2:
            self.status_var.set(
                f'{len(self.mine_rows)} shortcut personali · Ctrl+Shift+A aggiunge · Ctrl+1 Cerca · Ctrl+2 Tutti · Ctrl+3 Mie.'
            )
        elif tab_index == 1:
            self.status_var.set(
                f'{len(self.archive_rows)} route · intestazioni cliccabili · Ctrl+1 Cerca · Ctrl+2 Tutti · Ctrl+3 Mie · Invio esegui.'
            )
        elif self.current_hits:
            self.status_var.set(
                f'{len(self.current_hits)} risultati · Ctrl+2 TUTTI · Ctrl+3 MIE · ↓ scegli · Invio route · Ctrl+C copia.'
            )
        else:
            self.status_var.set('Nessun risultato. Prova un sinonimo; Ctrl+2 apre TUTTI, Ctrl+3 apre MIE.')

    def show_help(self):
        messagebox.showinfo(
            'ComboCode — Tastiera',
            'Ctrl+K / Ctrl+L  Cerca\n'
            'Ctrl+1             Pagina CERCA\n'
            'Ctrl+2             Pagina TUTTI\n'
            '↓                  Passa dalla ricerca alla lista\n'
            'Invio              Apri/Esegui route selezionata\n'
            'Ctrl+C             Copia route\n'
            'Ctrl+F             Preferito\n'
            'Ctrl+M             Esporta nota Obsidian\n'
            'F1                 Aiuto\n'
            'Esc                Chiudi'
        )

    def run(self):
        self.root.mainloop()
