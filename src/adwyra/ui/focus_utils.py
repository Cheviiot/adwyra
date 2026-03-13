# -*- coding: utf-8 -*-
"""Утилиты для работы с фокусом и текстовым вводом.

Предоставляет helper-функции для проверки состояния текстового ввода.
Используется для блокировки навигации интерфейса во время редактирования текста.

Пример:
    from .focus_utils import is_text_input_active
    
    def _on_key(self, ctrl, keyval, keycode, state):
        # Не перехватывать клавиши во время текстового ввода
        if is_text_input_active(self):
            return False
        ...
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


# Типы виджетов, которые считаются текстовым вводом
_EDITABLE_TYPES = (
    Gtk.Entry,
    Gtk.SearchEntry,
    Gtk.Text,
    Gtk.TextView,
    Gtk.EditableLabel,
    Adw.EntryRow,
)


def get_focused_widget(window: Gtk.Window) -> Gtk.Widget | None:
    """Получить виджет с текущим фокусом.
    
    Args:
        window: Окно для проверки.
        
    Returns:
        Виджет с фокусом или None.
    """
    if not window:
        return None
    return window.get_focus()


def is_editable_widget(widget: Gtk.Widget) -> bool:
    """Проверить, является ли виджет редактируемым текстовым полем.
    
    Args:
        widget: Виджет для проверки.
        
    Returns:
        True если виджет поддерживает текстовый ввод.
    """
    if not widget:
        return False
    
    # Проверка по типу
    if isinstance(widget, _EDITABLE_TYPES):
        return True
    
    # Проверка интерфейса Gtk.Editable
    if isinstance(widget, Gtk.Editable):
        return True
    
    # Adw.EntryRow содержит внутренний Entry/Text, проверяем parent
    parent = widget.get_parent()
    while parent:
        if isinstance(parent, Adw.EntryRow):
            return True
        parent = parent.get_parent()
    
    return False


def is_text_input_active(window: Gtk.Window) -> bool:
    """Проверить, активен ли текстовый ввод в окне.
    
    Возвращает True если пользователь сейчас редактирует текст
    в любом текстовом поле (Entry, SearchEntry, TextView, EntryRow и т.д.).
    
    Используйте эту функцию для блокировки:
    - Глобальных горячих клавиш
    - Навигации carousel/pages
    - DnD операций
    - Любых handlers, которые могут конфликтовать с редактированием текста
    
    Args:
        window: Окно для проверки.
        
    Returns:
        True если активен текстовый ввод.
    """
    focused = get_focused_widget(window)
    return is_editable_widget(focused)
