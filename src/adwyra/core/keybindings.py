# -*- coding: utf-8 -*-
"""Управление горячими клавишами через GSettings.

Централизованный модуль для работы с GNOME keybindings.
"""

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk, GObject


# GSettings схемы
GSETTINGS_MEDIA_KEYS = "org.gnome.settings-daemon.plugins.media-keys"
GSETTINGS_CUSTOM_KEYBINDING = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"
GSETTINGS_WM = "org.gnome.desktop.wm.keybindings"
GSETTINGS_SHELL = "org.gnome.shell.keybindings"
ADWYRA_KEYBINDING_PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/adwyra/"


class KeybindingsManager(GObject.Object):
    """Менеджер горячих клавиш для Adwyra."""
    
    __gtype_name__ = "KeybindingsManager"
    
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }
    
    def __init__(self):
        super().__init__()
    
    def get_current(self) -> str | None:
        """Получить текущую горячую клавишу из GNOME settings.
        
        Returns:
            Читаемое представление клавиши или None.
        """
        try:
            settings = Gio.Settings.new(GSETTINGS_MEDIA_KEYS)
            customs = settings.get_strv("custom-keybindings")
            for path in customs:
                if "adwyra" in path:
                    custom = Gio.Settings.new_with_path(
                        GSETTINGS_CUSTOM_KEYBINDING,
                        path
                    )
                    binding = custom.get_string("binding")
                    if binding:
                        success, keyval, mods = Gtk.accelerator_parse(binding)
                        if success and keyval:
                            return Gtk.accelerator_get_label(keyval, mods)
                        return binding
        except Exception:
            pass
        return None
    
    def normalize(self, text: str) -> str | None:
        """Преобразовать текст в GTK accelerator формат.
        
        Args:
            text: Текст вида "Super+A" или "<Super>a"
            
        Returns:
            GTK accelerator строка или None при ошибке.
        """
        if not text:
            return None
        text = text.strip()
        
        # Уже в формате GTK <Mod>key
        if text.startswith("<"):
            return text
        
        # Формат Super+A -> <Super>a
        parts = text.split("+")
        if len(parts) < 2:
            return None
        
        mods = []
        key = parts[-1].lower()
        
        for p in parts[:-1]:
            p = p.strip().lower()
            if p in ("super", "mod4"):
                mods.append("<Super>")
            elif p in ("ctrl", "control"):
                mods.append("<Control>")
            elif p in ("alt", "mod1"):
                mods.append("<Alt>")
            elif p == "shift":
                mods.append("<Shift>")
        
        if not mods:
            return None
        
        return "".join(mods) + key
    
    def validate(self, accel: str) -> bool:
        """Проверить валидность accelerator.
        
        Args:
            accel: GTK accelerator строка.
            
        Returns:
            True если валидный.
        """
        success, keyval, _mods = Gtk.accelerator_parse(accel)
        return success and keyval != 0
    
    def check_conflict(self, accel: str) -> str | None:
        """Проверить, занята ли комбинация клавиш системой.
        
        Args:
            accel: GTK accelerator для проверки.
            
        Returns:
            Название конфликтующего шортката или None.
        """
        try:
            settings = Gio.Settings.new(GSETTINGS_MEDIA_KEYS)
            
            # Проверяем стандартные шорткаты
            for key in settings.list_keys():
                try:
                    val = settings.get_value(key)
                    if val.get_type_string() == 's':
                        if val.get_string() == accel:
                            return key.replace("-", " ").title()
                    elif val.get_type_string() == 'as':
                        if accel in val.get_strv():
                            return key.replace("-", " ").title()
                except Exception:
                    pass
            
            # Проверяем custom keybindings (кроме нашего)
            customs = settings.get_strv("custom-keybindings")
            for path in customs:
                if "adwyra" in path:
                    continue
                try:
                    custom = Gio.Settings.new_with_path(
                        GSETTINGS_CUSTOM_KEYBINDING,
                        path
                    )
                    if custom.get_string("binding") == accel:
                        return custom.get_string("name") or "Другой шорткат"
                except Exception:
                    pass
            
            # Проверяем WM keybindings
            try:
                wm = Gio.Settings.new(GSETTINGS_WM)
                for key in wm.list_keys():
                    bindings = wm.get_strv(key)
                    if accel in bindings:
                        return key.replace("-", " ").title()
            except Exception:
                pass
            
            # Проверяем shell keybindings
            try:
                shell = Gio.Settings.new(GSETTINGS_SHELL)
                for key in shell.list_keys():
                    bindings = shell.get_strv(key)
                    if accel in bindings:
                        return key.replace("-", " ").title()
            except Exception:
                pass
                
        except Exception:
            pass
        return None
    
    def save(self, accel: str) -> bool:
        """Сохранить горячую клавишу в GNOME settings.
        
        Args:
            accel: GTK accelerator для сохранения.
            
        Returns:
            True при успехе.
        """
        try:
            settings = Gio.Settings.new(GSETTINGS_MEDIA_KEYS)
            customs = list(settings.get_strv("custom-keybindings"))
            
            # Добавляем путь если его нет
            if ADWYRA_KEYBINDING_PATH not in customs:
                customs.append(ADWYRA_KEYBINDING_PATH)
                settings.set_strv("custom-keybindings", customs)
            
            # Настраиваем шорткат
            custom = Gio.Settings.new_with_path(
                GSETTINGS_CUSTOM_KEYBINDING,
                ADWYRA_KEYBINDING_PATH
            )
            custom.set_string("name", "Adwyra")
            custom.set_string("command", "adwyra --toggle")
            custom.set_string("binding", accel)
            
            Gio.Settings.sync()
            self.emit("changed", accel)
            return True
        except Exception as e:
            print(f"Ошибка сохранения горячей клавиши: {e}")
            return False
    
    def clear(self) -> bool:
        """Удалить горячую клавишу.
        
        Returns:
            True при успехе.
        """
        try:
            settings = Gio.Settings.new(GSETTINGS_MEDIA_KEYS)
            customs = list(settings.get_strv("custom-keybindings"))
            
            if ADWYRA_KEYBINDING_PATH in customs:
                customs.remove(ADWYRA_KEYBINDING_PATH)
                settings.set_strv("custom-keybindings", customs)
                Gio.Settings.sync()
            
            self.emit("changed", "")
            return True
        except Exception as e:
            print(f"Ошибка удаления горячей клавиши: {e}")
            return False
    
    def get_label(self, accel: str) -> str | None:
        """Получить читаемое представление accelerator.
        
        Args:
            accel: GTK accelerator.
            
        Returns:
            Читаемая строка или None.
        """
        success, keyval, mods = Gtk.accelerator_parse(accel)
        if success and keyval:
            return Gtk.accelerator_get_label(keyval, mods)
        return None


# Синглтон
keybindings = KeybindingsManager()
