# -*- coding: utf-8 -*-
"""Страница настроек приложения.

Содержит настройки внешнего вида (тема, размер иконок, количество колонок),
горячие клавиши и системные действия (покинуть сетку).
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, GObject

from ...core import config, keybindings


class PrefsPage(Gtk.Box):
    """Виджет страницы настроек.
    
    Signals:
        back(): Пользователь нажал "Назад".
        show-about(): Открыть страницу "О программе".
        show-hidden(): Открыть список скрытых приложений.
    """
    
    __gtype_name__ = "PrefsPage"
    
    __gsignals__ = {
        "back": (GObject.SignalFlags.RUN_LAST, None, ()),
        "show-about": (GObject.SignalFlags.RUN_LAST, None, ()),
        "show-hidden": (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        
        self._build()
    
    def _build(self):
        # Заголовок с кнопкой назад
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.set_margin_bottom(8)
        
        back_btn = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        back_btn.add_css_class("flat")
        back_btn.add_css_class("dimmed")
        back_btn.connect("clicked", lambda b: self.emit("back"))
        header_box.append(back_btn)
        
        title = Gtk.Label(label="Настройки")
        title.add_css_class("title-2")
        title.set_hexpand(True)
        title.set_halign(Gtk.Align.CENTER)
        header_box.append(title)
        
        # Кнопка About
        about_btn = Gtk.Button.new_from_icon_name("help-about-symbolic")
        about_btn.add_css_class("flat")
        about_btn.add_css_class("dimmed")
        about_btn.set_tooltip_text("О программе")
        about_btn.connect("clicked", lambda b: self.emit("show-about"))
        header_box.append(about_btn)
        
        self.append(header_box)
        
        # Внешний вид
        appearance = Adw.PreferencesGroup()
        appearance.set_title("Внешний вид")
        self.append(appearance)
        
        # Тема
        theme_row = Adw.ComboRow()
        theme_row.set_title("Тема")
        theme_row.set_model(Gtk.StringList.new(["Системная", "Светлая", "Тёмная"]))
        theme_map = {"system": 0, "light": 1, "dark": 2}
        theme_row.set_selected(theme_map.get(config.get("theme"), 0))
        theme_row.connect("notify::selected", self._on_theme_change)
        appearance.add(theme_row)
        
        # Размер иконок
        icon_row = Adw.ComboRow()
        icon_row.set_title("Размер иконок")
        icon_row.set_model(Gtk.StringList.new(["Маленький (56)", "Средний (72)", "Большой (96)"]))
        icon_map = {56: 0, 72: 1, 96: 2}
        icon_row.set_selected(icon_map.get(config.get("icon_size"), 1))
        icon_row.connect("notify::selected", self._on_icon_size_change)
        appearance.add(icon_row)
        
        # Сетка
        grid_group = Adw.PreferencesGroup()
        grid_group.set_title("Сетка")
        self.append(grid_group)
        
        cols_row = Adw.SpinRow.new_with_range(4, 10, 1)
        cols_row.set_title("Колонки")
        cols_row.set_value(config.get("columns"))
        cols_row.connect("notify::value", lambda r, p: config.set("columns", int(r.get_value())))
        grid_group.add(cols_row)
        
        rows_row = Adw.SpinRow.new_with_range(3, 8, 1)
        rows_row.set_title("Строки")
        rows_row.set_value(config.get("rows"))
        rows_row.connect("notify::value", lambda r, p: config.set("rows", int(r.get_value())))
        grid_group.add(rows_row)
        
        # Поведение
        behavior = Adw.PreferencesGroup()
        behavior.set_title("Поведение")
        self.append(behavior)
        
        close_launch = Adw.SwitchRow()
        close_launch.set_title("Закрывать при запуске")
        close_launch.set_active(config.get("close_on_launch"))
        close_launch.connect("notify::active", lambda r, p: config.set("close_on_launch", r.get_active()))
        behavior.add(close_launch)
        
        close_focus = Adw.SwitchRow()
        close_focus.set_title("Закрывать при потере фокуса")
        close_focus.set_active(config.get("close_on_focus_lost"))
        close_focus.connect("notify::active", lambda r, p: config.set("close_on_focus_lost", r.get_active()))
        behavior.add(close_focus)
        
        hide_dock = Adw.SwitchRow()
        hide_dock.set_title("Скрывать закреплённые в Dock")
        hide_dock.set_active(config.get("hide_dock_apps"))
        hide_dock.connect("notify::active", lambda r, p: config.set("hide_dock_apps", r.get_active()))
        behavior.add(hide_dock)
        
        # Строка для перехода к скрытым приложениям
        hidden_row = Adw.ActionRow()
        hidden_row.set_title("Скрытые приложения")
        hidden_row.set_subtitle("Приложения, удалённые из сетки")
        hidden_row.set_activatable(True)
        hidden_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        hidden_row.connect("activated", lambda r: self.emit("show-hidden"))
        behavior.add(hidden_row)
        
        # Горячая клавиша
        hotkey_group = Adw.PreferencesGroup()
        hotkey_group.set_title("Горячая клавиша")
        hotkey_group.set_description("Введите сочетание, например: Super+A, Ctrl+Space")
        self.append(hotkey_group)
        
        # Получить текущую горячую клавишу
        current_hotkey = keybindings.get_current()
        
        self._hotkey_entry = Adw.EntryRow()
        self._hotkey_entry.set_title("Сочетание клавиш")
        self._hotkey_entry.set_text(current_hotkey or "")
        self._hotkey_entry.connect("apply", self._on_hotkey_apply)
        self._hotkey_entry.set_show_apply_button(True)
        
        clear_btn = Gtk.Button.new_from_icon_name("edit-clear-symbolic")
        clear_btn.set_valign(Gtk.Align.CENTER)
        clear_btn.add_css_class("flat")
        clear_btn.add_css_class("dimmed")
        clear_btn.set_tooltip_text("Удалить")
        clear_btn.connect("clicked", self._on_clear_hotkey)
        self._hotkey_entry.add_suffix(clear_btn)
        
        hotkey_group.add(self._hotkey_entry)
    
    def _on_theme_change(self, row, param):
        themes = ["system", "light", "dark"]
        theme = themes[row.get_selected()]
        config.set("theme", theme)
        style = Adw.StyleManager.get_default()
        if theme == "dark":
            style.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif theme == "light":
            style.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style.set_color_scheme(Adw.ColorScheme.DEFAULT)
    
    def _on_icon_size_change(self, row, param):
        sizes = [56, 72, 96]
        config.set("icon_size", sizes[row.get_selected()])
    
    def _on_hotkey_apply(self, entry):
        """Применить введённую горячую клавишу."""
        text = entry.get_text()
        accel = keybindings.normalize(text)
        
        if not accel or not keybindings.validate(accel):
            self._show_entry_error(entry, text)
            return
        
        # Проверить конфликт
        conflict = keybindings.check_conflict(accel)
        if conflict:
            entry.add_css_class("error")
            entry.set_text(f"Занято: {conflict}")
            GLib.timeout_add(2500, lambda: (entry.remove_css_class("error"), entry.set_text(text)) or False)
            return
        
        # Сохраняем
        if keybindings.save(accel):
            label = keybindings.get_label(accel)
            entry.set_text(label or text)
            entry.add_css_class("success")
            GLib.timeout_add(1500, lambda: entry.remove_css_class("success") or False)
        else:
            self._show_entry_error(entry, text)
    
    def _show_entry_error(self, entry, original_text):
        entry.add_css_class("error")
        GLib.timeout_add(2000, lambda: entry.remove_css_class("error") or False)
    
    def _on_clear_hotkey(self, btn):
        """Удалить горячую клавишу."""
        if keybindings.clear():
            self._hotkey_entry.set_text("")
