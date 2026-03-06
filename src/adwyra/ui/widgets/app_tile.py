# -*- coding: utf-8 -*-
"""Тайл приложения.

Кнопка с иконкой и названием приложения,
поддерживающая drag-drop для создания папок
и перемещения закреплённых приложений.
"""

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, Gio, GLib, GObject, Pango

from ...core import config, favorites, aliases


class AppTile(Gtk.Button):
    """Тайл приложения с иконкой, подписью и drag-drop."""
    
    __gtype_name__ = "AppTile"
    
    __gsignals__ = {
        "launched": (GObject.SignalFlags.RUN_LAST, None, ()),
        "folder-create": (GObject.SignalFlags.RUN_LAST, None, (str, str)),
        "fav-moved": (GObject.SignalFlags.RUN_LAST, None, (str, str)),  # (moved_app, before_app)
        "drag-begin": (GObject.SignalFlags.RUN_LAST, None, ()),
        "drag-end": (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self, app_info: Gio.AppInfo):
        super().__init__()
        self.app_info = app_info
        self.app_id = app_info.get_id() or ""
        self._hover_timeout = None
        self._drop_app_id = None
        
        self.add_css_class("flat")
        
        self._build()
        self._setup_dnd()
        self._setup_menu()
        
        self.connect("clicked", self._launch)
    
    def _build(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_halign(Gtk.Align.CENTER)
        self.set_child(box)
        
        # Контейнер для иконки с индикатором
        icon_overlay = Gtk.Overlay()
        
        # Контейнер для закругления иконки
        icon_frame = Gtk.Frame()
        icon_frame.set_halign(Gtk.Align.CENTER)
        icon_frame.set_valign(Gtk.Align.CENTER)
        icon_frame.add_css_class("icon-frame")
        icon_frame.set_overflow(Gtk.Overflow.HIDDEN)
        
        # Иконка
        self._icon = Gtk.Image.new_from_gicon(
            self.app_info.get_icon() or Gio.ThemedIcon.new("application-x-executable")
        )
        self._icon.set_pixel_size(config.get("icon_size"))
        icon_frame.set_child(self._icon)
        icon_overlay.set_child(icon_frame)
        
        # Индикатор закрепления
        self._pin_badge = Gtk.Image.new_from_icon_name("starred-symbolic")
        self._pin_badge.set_pixel_size(14)
        self._pin_badge.set_halign(Gtk.Align.END)
        self._pin_badge.set_valign(Gtk.Align.START)
        self._pin_badge.add_css_class("pin-badge")
        self._pin_badge.set_visible(favorites.contains(self.app_id))
        icon_overlay.add_overlay(self._pin_badge)
        
        box.append(icon_overlay)
        
        # Название (используем псевдоним если есть)
        original_name = self.app_info.get_display_name() or ""
        display_name = aliases.get_display_name(self.app_id, original_name)
        self._label = Gtk.Label(label=display_name)
        self._label.set_ellipsize(Pango.EllipsizeMode.END)
        self._label.set_width_chars(10)
        self._label.set_max_width_chars(12)
        self._label.set_lines(2)
        self._label.set_wrap(True)
        self._label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self._label.set_justify(Gtk.Justification.CENTER)
        self._label.add_css_class("app-label")
        box.append(self._label)
        
        # Подписка на изменение псевдонима
        aliases.connect("changed", self._on_alias_changed)
    
    def _setup_dnd(self):
        # Drag source
        drag = Gtk.DragSource()
        drag.set_actions(Gdk.DragAction.MOVE)
        drag.connect("prepare", self._on_drag_prepare)
        drag.connect("drag-begin", self._on_drag_begin)
        drag.connect("drag-end", self._on_drag_end)
        self.add_controller(drag)
        
        # Drop target
        drop = Gtk.DropTarget.new(str, Gdk.DragAction.MOVE)
        drop.connect("enter", self._on_drop_enter)
        drop.connect("leave", self._on_drop_leave)
        drop.connect("drop", self._on_drop)
        self.add_controller(drop)
    
    def _on_drag_prepare(self, source, x, y):
        return Gdk.ContentProvider.new_for_value(self.app_id)
    
    def _on_drag_begin(self, source, drag):
        self.emit("drag-begin")
        icon = Gtk.DragIcon.get_for_drag(drag)
        img = Gtk.Image.new_from_gicon(
            self.app_info.get_icon() or Gio.ThemedIcon.new("application-x-executable")
        )
        img.set_pixel_size(config.get("icon_size"))
        icon.set_child(img)
    
    def _on_drag_end(self, source, drag, delete_data):
        self.emit("drag-end")
    
    def _on_drop_enter(self, target, x, y):
        self.add_css_class("drop-hover")
        self._drop_app_id = None
        
        # Получаем app_id из drag для использования в таймере
        drop = target.get_drop()
        if drop:
            def on_read(d, result):
                try:
                    value = d.read_value_finish(result)
                    if isinstance(value, str):
                        self._drop_app_id = value
                except Exception:
                    pass
            drop.read_value_async(str, 0, None, on_read)
        
        # Запускать таймер создания папки только если это приложение не закреплено
        if not favorites.contains(self.app_id):
            self._hover_timeout = GLib.timeout_add(600, self._create_folder_timeout)
        else:
            self._hover_timeout = None
        return Gdk.DragAction.MOVE
    
    def _on_drop_leave(self, target):
        self.remove_css_class("drop-hover")
        if self._hover_timeout:
            GLib.source_remove(self._hover_timeout)
            self._hover_timeout = None
        self._drop_app_id = None
    
    def _create_folder_timeout(self):
        self._hover_timeout = None
        if self._drop_app_id and self._drop_app_id != self.app_id:
            # Не создавать папку если перетаскиваемое приложение закреплено
            if not favorites.contains(self._drop_app_id):
                self.emit("folder-create", self._drop_app_id, self.app_id)
        return False
    
    def _on_drop(self, target, value, x, y):
        self._drop_app_id = value
        self._on_drop_leave(target)
        
        if not value or value == self.app_id:
            return True
        
        # Если перетаскиваемое приложение закреплено - перемещаем позицию
        if favorites.contains(value):
            self.emit("fav-moved", value, self.app_id)
        else:
            # Обычное приложение - создаём папку
            if not favorites.contains(self.app_id):
                self.emit("folder-create", value, self.app_id)
        return True
    
    def _setup_menu(self):
        click = Gtk.GestureClick()
        click.set_button(3)
        click.connect("released", self._show_menu)
        self.add_controller(click)
    
    def _show_menu(self, gesture, n, x, y):
        is_fav = favorites.contains(self.app_id)
        has_alias = aliases.get(self.app_id) is not None
        
        menu = Gio.Menu()
        menu.append("Открепить" if is_fav else "Закрепить", "tile.toggle")
        menu.append("Переименовать", "tile.rename")
        if has_alias:
            menu.append("Сбросить имя", "tile.reset_name")
        
        group = Gio.SimpleActionGroup()
        
        toggle_action = Gio.SimpleAction.new("toggle", None)
        toggle_action.connect("activate", lambda a, p: favorites.toggle(self.app_id))
        group.add_action(toggle_action)
        
        rename_action = Gio.SimpleAction.new("rename", None)
        rename_action.connect("activate", self._show_rename_dialog)
        group.add_action(rename_action)
        
        reset_action = Gio.SimpleAction.new("reset_name", None)
        reset_action.connect("activate", lambda a, p: aliases.remove(self.app_id))
        group.add_action(reset_action)
        
        self.insert_action_group("tile", group)
        
        popover = Gtk.PopoverMenu.new_from_model(menu)
        popover.set_parent(self)
        popover.popup()
    
    def _show_rename_dialog(self, action, param):
        """Показывает диалог переименования приложения."""
        window = self.get_root()
        
        # Блокируем закрытие по потере фокуса
        if hasattr(window, "_has_dialog"):
            window._has_dialog = True
        
        dialog = Gtk.Window()
        dialog.set_transient_for(window)
        dialog.set_modal(True)
        dialog.set_decorated(False)
        dialog.set_resizable(False)
        dialog.add_css_class("compact-dialog")
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        title = Gtk.Label(label="Переименовать")
        title.add_css_class("heading")
        box.append(title)
        
        # Поле ввода
        entry = Gtk.Entry()
        current_alias = aliases.get(self.app_id)
        entry.set_text(current_alias or self.app_info.get_display_name() or "")
        entry.set_width_chars(18)
        box.append(entry)
        
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_margin_top(4)
        
        cancel_btn = Gtk.Button(label="Отмена")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        btn_box.append(cancel_btn)
        
        ok_btn = Gtk.Button(label="Сохранить")
        ok_btn.add_css_class("suggested-action")
        
        def on_ok(b):
            new_name = entry.get_text().strip()
            if new_name:
                aliases.set(self.app_id, new_name)
            dialog.close()
        
        ok_btn.connect("clicked", on_ok)
        entry.connect("activate", on_ok)
        btn_box.append(ok_btn)
        
        box.append(btn_box)
        dialog.set_child(box)
        
        def on_close(w):
            if hasattr(window, "_has_dialog"):
                window._has_dialog = False
            return False
        
        dialog.connect("close-request", on_close)
        dialog.present()
        entry.grab_focus()
    
    def _on_alias_changed(self, aliases_obj, app_id):
        """Обновляет отображаемое имя при изменении псевдонима."""
        if app_id == self.app_id:
            original_name = self.app_info.get_display_name() or ""
            display_name = aliases.get_display_name(self.app_id, original_name)
            self._label.set_label(display_name)
    
    def _launch(self, btn):
        try:
            self.app_info.launch(None, None)
        except GLib.Error:
            pass
        self.emit("launched")
    
    def update_icon_size(self):
        self._icon.set_pixel_size(config.get("icon_size"))
