# -*- coding: utf-8 -*-
"""Управление закреплёнными (избранными) приложениями.

Хранит упорядоченный список ID приложений, которые отображаются
в начале сетки со звёздочкой. Также интегрируется с GNOME Shell Dock
для получения системных избранных.

Файл хранения: ~/.config/adwyra/favorites.json
"""

import json
import os
from gi.repository import GLib, GObject, Gio


def get_gnome_dock_apps() -> set[str]:
    """Получить список приложений, закреплённых в GNOME Shell Dock.
    
    Returns:
        Множество ID приложений (например, {"firefox.desktop", "nautilus.desktop"}).
        Пустое множество, если недоступно.
    """
    try:
        settings = Gio.Settings.new("org.gnome.shell")
        favorites = settings.get_strv("favorite-apps")
        return set(favorites)
    except Exception:
        return set()


class Favorites(GObject.Object):
    """Менеджер избранных приложений Adwyra.
    
    Signals:
        changed(): Список избранных изменился.
    """
    
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self):
        super().__init__()
        self._config_dir = os.path.join(GLib.get_user_config_dir(), "adwyra")
        self._file_path = os.path.join(self._config_dir, "favorites.json")
        self._apps: list[str] = self._load()
    
    def _load(self) -> list[str]:
        """Загрузить список из файла."""
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("apps", [])
            except (json.JSONDecodeError, IOError):
                pass
        return []
    
    def _save(self):
        """Сохранить список и оповестить подписчиков."""
        os.makedirs(self._config_dir, exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump({"apps": self._apps}, f, ensure_ascii=False)
        self.emit("changed")
    
    def get_all(self) -> list[str]:
        """Получить список всех избранных приложений в порядке закрепления."""
        return list(self._apps)
    
    def contains(self, app_id: str) -> bool:
        """Проверить, является ли приложение избранным."""
        return app_id in self._apps
    
    def add(self, app_id: str):
        """Добавить приложение в избранное (в конец списка)."""
        if app_id and app_id not in self._apps:
            self._apps.append(app_id)
            self._save()
    
    def remove(self, app_id: str):
        """Убрать приложение из избранного."""
        if app_id in self._apps:
            self._apps.remove(app_id)
            self._save()
    
    def toggle(self, app_id: str) -> bool:
        """Переключить статус избранного.
        
        Returns:
            True — приложение добавлено в избранное.
            False — приложение убрано из избранного.
        """
        if self.contains(app_id):
            self.remove(app_id)
            return False
        self.add(app_id)
        return True
    
    def move(self, app_id: str, target_id: str | None):
        """Переместить приложение на новую позицию в списке.
        
        Args:
            app_id: ID перемещаемого приложения.
            target_id: ID приложения, рядом с которым разместить. 
                      None — переместить в конец.
        """
        if app_id not in self._apps or app_id == target_id:
            return
        
        if target_id and target_id in self._apps:
            old_index = self._apps.index(app_id)
            self._apps.remove(app_id)
            target_index = self._apps.index(target_id)
            
            # Определяем направление перемещения
            if old_index < target_index + 1:
                # Двигаем вправо → вставляем после target
                self._apps.insert(target_index + 1, app_id)
            else:
                # Двигаем влево → вставляем перед target
                self._apps.insert(target_index, app_id)
        else:
            # target не найден — перемещаем в конец
            self._apps.remove(app_id)
            self._apps.append(app_id)
        
        self._save()


# Глобальный экземпляр
favorites = Favorites()
