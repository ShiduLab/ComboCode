from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    bg: str
    panel: str
    panel_alt: str
    text: str
    muted: str
    border: str
    field: str
    accent: str
    accent_hover: str
    selection_text: str


LIGHT = Palette(
    bg='#f4f6f8',
    panel='#ffffff',
    panel_alt='#eef2f6',
    text='#17191c',
    muted='#616873',
    border='#d6dbe1',
    field='#ffffff',
    accent='#0a64ad',
    accent_hover='#084f89',
    selection_text='#ffffff',
)

DARK = Palette(
    bg='#16191d',
    panel='#1f2328',
    panel_alt='#252a30',
    text='#f2f4f7',
    muted='#aab2bd',
    border='#3a4149',
    field='#20252b',
    accent='#3182ce',
    accent_hover='#4c9be8',
    selection_text='#ffffff',
)


def system_prefers_dark() -> bool:
    if sys.platform != 'win32':
        return True
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize',
        )
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        return int(value) == 0
    except Exception:
        return True


def apply_titlebar_mode(root, dark: bool) -> None:
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        from ctypes import wintypes

        root.update_idletasks()
        hwnd = wintypes.HWND(root.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        dwm = ctypes.windll.dwmapi
        for attribute in (20, 19):
            try:
                if dwm.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                    break
            except Exception:
                continue
    except Exception:
        pass


def apply_ttk_theme(root, style, dark: bool) -> Palette:
    palette = DARK if dark else LIGHT

    try:
        style.theme_use('clam')
    except Exception:
        pass

    root.configure(bg=palette.bg)
    root.option_add('*Font', '{Segoe UI} 10')
    root.option_add('*TCombobox*Listbox.font', 'Segoe UI 10')
    root.option_add('*TCombobox*Listbox.background', palette.field)
    root.option_add('*TCombobox*Listbox.foreground', palette.text)
    root.option_add('*TCombobox*Listbox.selectBackground', palette.accent)
    root.option_add('*TCombobox*Listbox.selectForeground', palette.selection_text)

    style.configure('.', background=palette.bg, foreground=palette.text, font=('Segoe UI', 10))
    style.configure('TFrame', background=palette.bg)
    style.configure('Panel.TFrame', background=palette.panel)
    style.configure('Footer.TFrame', background=palette.bg)

    style.configure('TLabel', background=palette.bg, foreground=palette.text)
    style.configure('Panel.TLabel', background=palette.panel, foreground=palette.text)
    style.configure('Muted.TLabel', background=palette.bg, foreground=palette.muted)
    style.configure('PanelMuted.TLabel', background=palette.panel, foreground=palette.muted)
    style.configure('Title.TLabel', background=palette.panel, foreground=palette.text, font=('Segoe UI Semibold', 21))
    style.configure('Section.TLabel', background=palette.panel, foreground=palette.muted, font=('Segoe UI Semibold', 9))

    style.configure(
        'TEntry',
        fieldbackground=palette.field,
        foreground=palette.text,
        insertcolor=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.border,
        darkcolor=palette.border,
        padding=(10, 8),
    )
    style.map(
        'TEntry',
        bordercolor=[('focus', palette.accent)],
        lightcolor=[('focus', palette.accent)],
        darkcolor=[('focus', palette.accent)],
    )

    style.configure('Search.TEntry', font=('Segoe UI', 15), padding=(12, 9))

    style.configure(
        'TCombobox',
        fieldbackground=palette.field,
        background=palette.field,
        foreground=palette.text,
        arrowcolor=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.border,
        darkcolor=palette.border,
        padding=(8, 6),
    )
    style.map(
        'TCombobox',
        fieldbackground=[('readonly', palette.field)],
        foreground=[('readonly', palette.text)],
        selectbackground=[('readonly', palette.field)],
        selectforeground=[('readonly', palette.text)],
        bordercolor=[('focus', palette.accent)],
    )

    style.configure(
        'TButton',
        background=palette.panel_alt,
        foreground=palette.text,
        borderwidth=0,
        focusthickness=1,
        focuscolor=palette.accent,
        padding=(12, 8),
    )
    style.map(
        'TButton',
        background=[('active', palette.border), ('pressed', palette.border), ('disabled', palette.panel_alt)],
        foreground=[('disabled', palette.muted)],
    )
    style.configure(
        'Dropdown.TMenubutton',
        background=palette.field,
        foreground=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.border,
        darkcolor=palette.border,
        relief='flat',
        padding=(10, 7),
        arrowcolor=palette.text,
    )
    style.map(
        'Dropdown.TMenubutton',
        background=[('active', palette.border), ('pressed', palette.border)],
        foreground=[('disabled', palette.muted)],
    )

    style.configure('Compact.TButton', background=palette.field, foreground=palette.muted, padding=(6, 6), font=('Segoe UI Semibold', 13))
    style.map(
        'Compact.TButton',
        background=[('active', palette.border), ('pressed', palette.border)],
        foreground=[('active', palette.text)],
    )
    style.configure('Brand.TLabel', background=palette.bg, foreground=palette.text, font=('Segoe UI Semibold', 10))

    style.configure('Accent.TButton', background=palette.accent, foreground='#ffffff', padding=(13, 8))
    style.map(
        'Accent.TButton',
        background=[('active', palette.accent_hover), ('pressed', palette.accent_hover), ('disabled', palette.panel_alt)],
        foreground=[('disabled', palette.muted)],
    )

    style.configure('TNotebook', background=palette.bg, borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure(
        'TNotebook.Tab',
        background=palette.bg,
        foreground=palette.muted,
        borderwidth=0,
        padding=(16, 9),
        font=('Segoe UI Semibold', 10),
    )
    style.map(
        'TNotebook.Tab',
        background=[('selected', palette.panel)],
        foreground=[('selected', palette.text), ('active', palette.text)],
    )

    style.configure(
        'Treeview',
        background=palette.panel,
        fieldbackground=palette.panel,
        foreground=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.border,
        darkcolor=palette.border,
        rowheight=29,
        relief='flat',
    )
    style.map(
        'Treeview',
        background=[('selected', palette.accent)],
        foreground=[('selected', palette.selection_text)],
    )
    style.configure(
        'Treeview.Heading',
        background=palette.panel_alt,
        foreground=palette.text,
        bordercolor=palette.border,
        lightcolor=palette.border,
        darkcolor=palette.border,
        relief='flat',
        padding=(8, 8),
        font=('Segoe UI Semibold', 9),
    )
    style.map('Treeview.Heading', background=[('active', palette.border)])

    style.configure('TPanedwindow', background=palette.border, sashwidth=6)
    style.configure('TSeparator', background=palette.border)
    style.configure('Vertical.TScrollbar', background=palette.panel_alt, troughcolor=palette.panel, arrowcolor=palette.text)
    style.configure('Horizontal.TScrollbar', background=palette.panel_alt, troughcolor=palette.panel, arrowcolor=palette.text)

    apply_titlebar_mode(root, dark)
    return palette
