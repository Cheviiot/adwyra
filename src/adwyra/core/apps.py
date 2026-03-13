# -*- coding: utf-8 -*-
"""Сервис загрузки системных приложений.

Получает список всех установленных приложений через Gio.AppInfo и
отслеживает изменения (установка/удаление программ) через Gio.AppInfoMonitor.

Пример:
    from adwyra.core.apps import app_service
    
    # Получить все приложения
    apps = app_service.get_all()
    
    # Подписаться на изменения
    app_service.connect("changed", lambda s: print("Приложения обновились"))
"""

from gi.repository import Gio, GObject


class AppService(GObject.Object):
    """Сервис доступа к системным приложениям.
    
    Кэширует список приложений и автоматически обновляет его
    при установке или удалении программ в системе.
    
    Signals:
        changed(): Список приложений изменился.
    """
    
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self):
        super().__init__()
        self._apps: list[Gio.AppInfo] = []
        self._monitor = Gio.AppInfoMonitor.get()
        self._monitor.connect("changed", self._on_changed)
        self._load()
    
    def _load(self):
        self._apps = [
            app for app in Gio.AppInfo.get_all()
            if app.should_show()
        ]
        self._apps.sort(key=lambda a: (a.get_display_name() or "").lower())
    
    def _on_changed(self, monitor):
        self._load()
        self.emit("changed")
    
    def get_all(self) -> list[Gio.AppInfo]:
        return self._apps


app_service = AppService()
