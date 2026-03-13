# -*- coding: utf-8 -*-
"""Управление папками приложений.

Папки позволяют группировать приложения в "виртуальные каталоги".
Приложение внутри папки не отображается в основной сетке.

Структура хранения (~/.config/adwyra/folders.json):
    {
        "counter": 5,
        "folders": {
            "folder_1": {"name": "Игры", "apps": ["steam.desktop", "lutris.desktop"]},
            "folder_2": {"name": "Офис", "apps": ["libreoffice-writer.desktop"]}
        }
    }
"""

import json
import os
from gi.repository import GLib, GObject


class Folders(GObject.Object):
    """Менеджер папок приложений.
    
    Signals:
        changed(): Данные папок изменились (создание, удаление, переименование,
                   добавление/удаление приложения).
    """
    
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self):
        super().__init__()
        self._config_dir = os.path.join(GLib.get_user_config_dir(), "adwyra")
        self._file_path = os.path.join(self._config_dir, "folders.json")
        self._data = self._load()
    
    def _load(self) -> dict:
        """Загрузить данные из файла."""
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"folders": {}, "counter": 0}
    
    def _save(self):
        """Сохранить данные и оповестить подписчиков."""
        os.makedirs(self._config_dir, exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        self.emit("changed")
    
    # === Работа с папками ===
    
    def get_ids(self) -> list[str]:
        """Получить список ID всех папок."""
        return list(self._data.get("folders", {}).keys())
    
    def get(self, folder_id: str) -> dict | None:
        """Получить данные папки по ID.
        
        Returns:
            {"name": str, "apps": list[str]} или None если не найдена.
        """
        return self._data.get("folders", {}).get(folder_id)
    
    def create(self, name: str, apps: list[str] | None = None) -> str:
        """Создать новую папку.
        
        Args:
            name: Название папки.
            apps: Начальный список приложений (опционально).
            
        Returns:
            ID созданной папки (например, "folder_5").
        """
        self._data["counter"] = self._data.get("counter", 0) + 1
        folder_id = f"folder_{self._data['counter']}"
        self._data["folders"][folder_id] = {
            "name": name,
            "apps": apps or []
        }
        self._save()
        return folder_id
    
    def rename(self, folder_id: str, name: str):
        """Переименовать папку."""
        folder = self._data["folders"].get(folder_id)
        if folder:
            folder["name"] = name
            self._save()
    
    def delete(self, folder_id: str):
        """Удалить папку. Приложения внутри вернутся в основную сетку."""
        if folder_id in self._data["folders"]:
            del self._data["folders"][folder_id]
            self._save()
    
    # === Работа с приложениями внутри папок ===
    
    def add_app(self, folder_id: str, app_id: str):
        """Добавить приложение в папку."""
        folder = self._data["folders"].get(folder_id)
        if folder and app_id not in folder["apps"]:
            folder["apps"].append(app_id)
            self._save()
    
    def remove_app(self, folder_id: str, app_id: str):
        """Убрать приложение из папки."""
        folder = self._data["folders"].get(folder_id)
        if folder and app_id in folder["apps"]:
            folder["apps"].remove(app_id)
            self._save()
    
    def get_all_app_ids(self) -> set[str]:
        """Получить ID всех приложений, находящихся в любых папках.
        
        Используется для исключения этих приложений из основной сетки.
        """
        result = set()
        for folder in self._data.get("folders", {}).values():
            result.update(folder.get("apps", []))
        return result


# Глобальный экземпляр
folders = Folders()
