# -*- coding: utf-8 -*-
"""Поле поиска.

Активируется по клику, чтобы не захватывать фокус
при открытии окна.
"""

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class SearchBar(Gtk.Box):
    """Контейнер с полем поиска, активируемым по клику."""
    
    __gtype_name__ = "SearchBar"
    
    __gsignals__ = {
        "query-changed": (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }
    
    def __init__(self):
        super().__init__()
        
        self._entry = Gtk.SearchEntry()
        self._entry.set_placeholder_text("Поиск")
        self._entry.set_hexpand(True)
        self._entry.set_focusable(False)
        self._entry.connect("search-changed", self._on_changed)
        self.append(self._entry)
        
        # Включить фокус по клику на весь контейнер
        click = Gtk.GestureClick()
        click.connect("released", self._on_click)
        self.add_controller(click)
    
    def _on_click(self, gesture, n_press, x, y):
        self._entry.set_focusable(True)
        self._entry.grab_focus()
    
    def _on_changed(self, entry):
        self.emit("query-changed", entry.get_text())
    
    def get_text(self):
        return self._entry.get_text()
    
    def set_text(self, text):
        self._entry.set_text(text)
    
    def clear(self):
        self._entry.set_text("")
        self._entry.set_focusable(False)
    
    def set_focusable(self, focusable):
        self._entry.set_focusable(focusable)
    
    def grab_focus(self):
        self._entry.grab_focus()
