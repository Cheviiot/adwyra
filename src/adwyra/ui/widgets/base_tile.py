# -*- coding: utf-8 -*-
"""Базовый тайл приложения.

Содержит общую логику для тайлов приложений.
"""

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, GLib, GObject, Pango

from ...core import config
from ..icon_utils import icon_needs_rounding


class BaseTile(Gtk.Button):
    """Базовый тайл приложения с иконкой и подписью."""
    
    __gtype_name__ = "BaseTile"
    
    __gsignals__ = {
        "launched": (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self, app_info: Gio.AppInfo):
        super().__init__()
        self.app_info = app_info
        self.app_id = app_info.get_id() or ""
        
        self.add_css_class("flat")
        self.connect("clicked", self._launch)
    
    def _build_icon(self, overlay: bool = False) -> Gtk.Widget:
        """Создать иконку приложения.
        
        Args:
            overlay: Если True, возвращает Gtk.Overlay для добавления бейджей.
            
        Returns:
            Виджет с иконкой.
        """
        gicon = self.app_info.get_icon() or Gio.ThemedIcon.new("application-x-executable")
        icon_size = config.get("icon_size")
        
        # Контейнер для закругления
        frame = Gtk.Frame()
        frame.set_halign(Gtk.Align.CENTER)
        frame.set_valign(Gtk.Align.CENTER)
        frame.set_overflow(Gtk.Overflow.HIDDEN)
        
        if icon_needs_rounding(gicon, icon_size):
            frame.add_css_class("icon-frame")
        else:
            frame.add_css_class("icon-frame-no-round")
        
        self._icon = Gtk.Image.new_from_gicon(gicon)
        self._icon.set_pixel_size(icon_size)
        frame.set_child(self._icon)
        
        if overlay:
            icon_overlay = Gtk.Overlay()
            icon_overlay.set_child(frame)
            return icon_overlay
        
        return frame
    
    def _build_label(self, text: str = None) -> Gtk.Label:
        """Создать подпись приложения."""
        display_name = text or self.app_info.get_display_name() or ""
        
        label = Gtk.Label(label=display_name)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_max_width_chars(12)
        label.add_css_class("app-label")
        
        return label
    
    def _setup_context_menu(self, callback):
        """Настроить контекстное меню по правому клику.
        
        Args:
            callback: Функция (gesture, n_press, x, y) для показа меню.
        """
        click = Gtk.GestureClick()
        click.set_button(3)
        click.connect("released", callback)
        self.add_controller(click)
    
    def _show_popover_menu(self, menu: Gio.Menu, group: Gio.SimpleActionGroup, prefix: str):
        """Показать контекстное меню.
        
        Args:
            menu: Модель меню Gio.Menu.
            group: Группа действий.
            prefix: Префикс для действий (например, "tile").
        """
        self.insert_action_group(prefix, group)
        popover = Gtk.PopoverMenu.new_from_model(menu)
        popover.set_parent(self)
        popover.popup()
    
    def _launch(self, btn):
        """Запустить приложение."""
        try:
            self.app_info.launch(None, None)
        except GLib.Error:
            pass
        self.emit("launched")
