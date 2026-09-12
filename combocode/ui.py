from __future__ import annotations

import sys
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

        cats = ['Tutte', *self.kb.categories()]
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
        self.notebook.add(self.search_tab, text='CERCA')
        self.notebook.add(self.all_tab, text='TUTTI')

        self._build_search_tab()
        self._build_all_tab()
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
        ttk.Button(buttons, text='FONTE', command=self.open_source).pack(side='left')

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
        archive_cats = ['Tutte', *self.kb.categories()]
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
        ttk.Button(buttons, text='FONTE', command=self.open_source).pack(side='left')

    def _bind_keys(self):
        self.root.bind('<Control-k>', lambda _e: self.focus_search())
        self.root.bind('<Control-l>', lambda _e: self.focus_search())
        self.root.bind('<Control-Key-1>', lambda _e: self.select_tab(0))
        self.root.bind('<Control-Key-2>', lambda _e: self.select_tab(1))
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
        else:
            self.archive_tree.focus_set()
        self._update_status_for_tab()
        return 'break'

    def _smart_down(self, _event):
        focus = self.root.focus_get()
        if self.notebook.index(self.notebook.select()) == 0:
            if focus != self.search_entry:
                return None
            tree = self.result_tree
        else:
            if focus != self.archive_search:
                return None
            tree = self.archive_tree
        children = tree.get_children()
        if children:
            tree.focus_set()
            first = children[0]
            tree.selection_set(first)
            tree.focus(first)
            return 'break'
        return None

    def focus_search(self):
        if self.notebook.index(self.notebook.select()) == 0:
            entry = self.search_entry
        else:
            entry = self.archive_search
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
        self._update_status_for_tab()

    def _update_status_for_tab(self):
        if self.notebook.index(self.notebook.select()) == 1:
            self.status_var.set(
                f'{len(self.archive_rows)} route · intestazioni cliccabili · Ctrl+1 Cerca · Ctrl+2 Tutti · Invio esegui · Ctrl+C copia.'
            )
        elif self.current_hits:
            self.status_var.set(
                f'{len(self.current_hits)} risultati · Ctrl+2 apre TUTTI · ↓ scegli · Invio route · Ctrl+C copia.'
            )
        else:
            self.status_var.set('Nessun risultato. Prova un sinonimo; Ctrl+2 apre l’intero archivio.')

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
