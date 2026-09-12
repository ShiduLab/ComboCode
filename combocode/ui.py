from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from pathlib import Path

from .executor import ExecutionError, execute_route
from .exporter import export_goal


class ComboCodeUI:
    def __init__(self, kb, store):
        self.kb = kb
        self.store = store
        self.current_hits = []
        self.current_goal = None
        self.current_route = None

        self.root = tk.Tk()
        self.root.title('ComboCode — ShiduLab')
        self.root.geometry('1050x680')
        self.root.minsize(850, 560)

        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value='Tutte')
        self.status_var = tk.StringVar(value='Scrivi cosa vuoi ottenere.')
        self.favorite_var = tk.StringVar(value='☆ Preferito')

        self._build_ui()
        self._bind_keys()
        self.refresh_results()
        self.search_entry.focus_set()

    def _build_ui(self):
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        top = ttk.Frame(root, padding=(14, 12, 14, 8))
        top.grid(row=0, column=0, sticky='ew')
        top.columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(top, textvariable=self.search_var, font=('Segoe UI', 16))
        self.search_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', lambda _e: self.refresh_results())

        cats = ['Tutte', *self.kb.categories()]
        self.category = ttk.Combobox(top, textvariable=self.category_var, values=cats, state='readonly', width=20)
        self.category.grid(row=0, column=1, sticky='e')
        self.category.bind('<<ComboboxSelected>>', lambda _e: self.refresh_results())

        main = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        main.grid(row=1, column=0, sticky='nsew', padx=14, pady=(0, 8))

        left = ttk.Frame(main, padding=4)
        right = ttk.Frame(main, padding=10)
        main.add(left, weight=2)
        main.add(right, weight=3)

        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self.result_tree = ttk.Treeview(left, columns=('cat',), show='tree headings', selectmode='browse')
        self.result_tree.heading('#0', text='Obiettivo')
        self.result_tree.heading('cat', text='Categoria')
        self.result_tree.column('#0', width=310, anchor='w')
        self.result_tree.column('cat', width=120, anchor='w')
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        yscroll = ttk.Scrollbar(left, orient='vertical', command=self.result_tree.yview)
        yscroll.grid(row=0, column=1, sticky='ns')
        self.result_tree.configure(yscrollcommand=yscroll.set)
        self.result_tree.bind('<<TreeviewSelect>>', self._on_goal_select)
        self.result_tree.bind('<Return>', lambda _e: self.route_tree.focus_set())

        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)

        self.title_label = ttk.Label(right, text='ComboCode', font=('Segoe UI Semibold', 20))
        self.title_label.grid(row=0, column=0, sticky='w')
        self.desc_label = ttk.Label(right, text='Un obiettivo, più route.', wraplength=560, justify='left')
        self.desc_label.grid(row=1, column=0, sticky='ew', pady=(4, 12))

        ttk.Label(right, text='ROUTE DISPONIBILI', font=('Segoe UI Semibold', 9)).grid(row=2, column=0, sticky='w')
        self.route_tree = ttk.Treeview(right, columns=('value', 'safety'), show='headings', selectmode='browse')
        self.route_tree.heading('value', text='Tipo / comando')
        self.route_tree.heading('safety', text='Stato')
        self.route_tree.column('value', width=500, anchor='w')
        self.route_tree.column('safety', width=100, anchor='center')
        self.route_tree.grid(row=3, column=0, sticky='nsew', pady=(4, 10))
        self.route_tree.bind('<<TreeviewSelect>>', self._on_route_select)
        self.route_tree.bind('<Double-1>', lambda _e: self.execute_selected())
        self.route_tree.bind('<Return>', lambda _e: self.execute_selected())

        self.route_detail = ttk.Label(right, text='', wraplength=560, justify='left')
        self.route_detail.grid(row=4, column=0, sticky='ew', pady=(0, 8))

        buttons = ttk.Frame(right)
        buttons.grid(row=5, column=0, sticky='ew')
        self.run_button = ttk.Button(buttons, text='APRI / ESEGUI', command=self.execute_selected)
        self.run_button.pack(side='left')
        ttk.Button(buttons, text='COPIA', command=self.copy_selected).pack(side='left', padx=6)
        ttk.Button(buttons, textvariable=self.favorite_var, command=self.toggle_favorite).pack(side='left')
        ttk.Button(buttons, text='ESPORTA .MD', command=self.export_selected).pack(side='left', padx=6)
        ttk.Button(buttons, text='FONTE', command=self.open_source).pack(side='left')

        status = ttk.Label(root, textvariable=self.status_var, anchor='w', padding=(14, 5, 14, 8))
        status.grid(row=2, column=0, sticky='ew')

    def _bind_keys(self):
        self.root.bind('<Control-k>', lambda _e: self.focus_search())
        self.root.bind('<Control-l>', lambda _e: self.focus_search())
        self.root.bind('<Control-c>', lambda _e: self.copy_selected())
        self.root.bind('<Control-m>', lambda _e: self.export_selected())
        self.root.bind('<Control-f>', lambda _e: self.toggle_favorite())
        self.root.bind('<F1>', lambda _e: self.show_help())
        self.root.bind('<Escape>', lambda _e: self.root.destroy())
        self.root.bind('<Down>', self._smart_down)

    def _smart_down(self, _event):
        if self.root.focus_get() == self.search_entry and self.result_tree.get_children():
            self.result_tree.focus_set()
            first = self.result_tree.get_children()[0]
            self.result_tree.selection_set(first)
            self.result_tree.focus(first)
            return 'break'
        return None

    def focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)
        return 'break'

    def refresh_results(self):
        query = self.search_var.get()
        category = self.category_var.get()
        self.current_hits = self.kb.search(query, category)
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for hit in self.current_hits:
            goal = hit.goal
            star = '★ ' if self.store.is_favorite(goal['id']) else ''
            self.result_tree.insert('', 'end', iid=goal['id'], text=star + goal['name'], values=(goal.get('category', ''),))
        if self.current_hits:
            first = self.current_hits[0].goal['id']
            self.result_tree.selection_set(first)
            self.result_tree.focus(first)
            self._show_goal(self.kb.by_id[first])
            self.status_var.set(f'{len(self.current_hits)} risultati — ↑↓ scegli, Invio route, Ctrl+C copia, Esc chiude.')
        else:
            self._clear_goal()
            self.status_var.set('Nessun risultato. Prova un sinonimo o una stringa di comando.')

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
            self.route_tree.insert('', 'end', iid=str(idx), values=(display, safety))
        if goal.get('routes'):
            self.route_tree.selection_set('0')
            self.route_tree.focus('0')
            self._select_route(0)

    def _clear_goal(self):
        self.current_goal = None
        self.current_route = None
        self.title_label.configure(text='ComboCode')
        self.desc_label.configure(text='Un obiettivo, più route.')
        for item in self.route_tree.get_children():
            self.route_tree.delete(item)
        self.route_detail.configure(text='')

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
        self.route_detail.configure(text=f"{note}\nVerifica: {verified}".strip())
        if self.current_route.get('executable', False) and self.current_route.get('safety') != 'DESTRUCTIVE':
            self.run_button.state(['!disabled'])
        else:
            self.run_button.state(['disabled'])

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
        if self.current_route.get('safety') == 'ELEVATED':
            ok = messagebox.askyesno('ComboCode', 'Questa route può richiedere privilegi amministrativi. Continuare?')
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
            return
        source = self.current_route.get('source')
        if source:
            webbrowser.open(source)
        else:
            messagebox.showinfo('ComboCode', 'Nessuna fonte associata a questa route.')

    def show_help(self):
        messagebox.showinfo(
            'ComboCode — Tastiera',
            'Ctrl+K / Ctrl+L  Cerca\n'
            '↓                  Passa ai risultati\n'
            'Invio              Apri/Esegui route\n'
            'Ctrl+C             Copia route\n'
            'Ctrl+F             Preferito\n'
            'Ctrl+M             Esporta nota Obsidian\n'
            'F1                 Aiuto\n'
            'Esc                Chiudi'
        )

    def run(self):
        self.root.mainloop()
