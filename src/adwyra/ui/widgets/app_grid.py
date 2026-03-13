# -*- coding: utf-8 -*-
"""Сетка приложений с пагинацией.

Использует Adw.Carousel для переключения страниц
с индикаторами-точками.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk, Gio, GLib, GObject

from ...core import config, folders, favorites
from ..focus_utils import is_text_input_active
from .app_tile import AppTile
from .folder_tile import FolderTile


class AppGrid(Gtk.Box):
    """Сетка приложений с Carousel пагинацией."""
    
    __gtype_name__ = "AppGrid"
    
    __gsignals__ = {
        "app-launched": (GObject.SignalFlags.RUN_LAST, None, ()),
        "folder-open": (GObject.SignalFlags.RUN_LAST, None, (str,)),
        "folder-rename": (GObject.SignalFlags.RUN_LAST, None, (str,)),
        "folder-delete": (GObject.SignalFlags.RUN_LAST, None, (str,)),
        "drag-begin": (GObject.SignalFlags.RUN_LAST, None, ()),
        "drag-end": (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._apps: list[Gio.AppInfo] = []
        self._items: list[tuple] = []  # [("folder", id) | ("app", AppInfo)]
        self._grids: list[Gtk.Grid] = []  # Grid на каждой странице
        self._favorites_handler = None
        self._focus_handler = None
        
        self._build()
        self._favorites_handler = favorites.connect("changed", lambda f: self._populate())
        self.connect("destroy", self._on_destroy)
        self.connect("realize", self._on_realize)
    
    def _on_realize(self, widget):
        """После realize подключаемся к фокусу окна."""
        window = self.get_root()
        if window:
            self._focus_handler = window.connect("notify::focus-widget", self._on_focus_changed)
    
    def _on_focus_changed(self, window, pspec):
        """Обновить состояние carousel при изменении фокуса."""
        text_active = is_text_input_active(window)
        self._carousel.set_allow_mouse_drag(not text_active)
    
    def _on_destroy(self, widget):
        if self._favorites_handler:
            favorites.disconnect(self._favorites_handler)
            self._favorites_handler = None
        # Window handler отключится автоматически при destroy
    
    def _build(self):
        # Carousel
        self._carousel = Adw.Carousel()
        self._carousel.set_allow_scroll_wheel(True)
        self._carousel.set_allow_mouse_drag(True)
        self._carousel.set_vexpand(True)
        self._carousel.set_hexpand(True)
        # НЕ делаем carousel focusable — фокус должен быть на тайлах внутри
        self._carousel.set_focusable(False)
        self._carousel.set_can_focus(False)
        self.append(self._carousel)
        
        # Перехватываем scroll для блокировки при текстовом вводе
        scroll_ctrl = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        scroll_ctrl.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        scroll_ctrl.connect("scroll", self._on_scroll_capture)
        self._carousel.add_controller(scroll_ctrl)
        
        # Индикатор (точки)
        self._dots = Adw.CarouselIndicatorDots()
        self._dots.set_carousel(self._carousel)
        self._dots.set_margin_bottom(8)
        self.append(self._dots)
    
    def _on_scroll_capture(self, ctrl, dx, dy):
        """Перехватить scroll при активном текстовом вводе."""
        window = self.get_root()
        if window and is_text_input_active(window):
            # Поглощаем событие - carousel не переключается
            return True
        return False
    
    def set_apps(self, apps: list[Gio.AppInfo]):
        self._apps = apps
        self._populate()
    
    def _populate(self):
        # Обновляем размер карусели
        self._update_carousel_size()
        
        # Сохраняем текущую позицию
        current_page = int(self._carousel.get_position())
        
        self._dots.set_carousel(None)
        self._grids = []
        
        while self._carousel.get_n_pages() > 0:
            self._carousel.remove(self._carousel.get_nth_page(0))
        
        # Сортировка: закреплённые приложения в начале (в порядке favorites)
        fav_ids = favorites.get_all()
        fav_apps = []
        other_apps = []
        
        app_map = {a.get_id(): a for a in self._apps}
        
        # Сначала закреплённые в их порядке
        for app_id in fav_ids:
            if app_id in app_map:
                fav_apps.append(app_map[app_id])
        
        # Затем остальные
        for app in self._apps:
            if app.get_id() not in fav_ids:
                other_apps.append(app)
        
        # Элементы: папки + закреплённые + остальные
        self._items = []
        for fid in folders.get_ids():
            self._items.append(("folder", fid))
        for app in fav_apps:
            self._items.append(("app", app))
        for app in other_apps:
            self._items.append(("app", app))
        
        # Пагинация
        per_page = config.per_page
        
        page_index = 0
        for start in range(0, max(len(self._items), 1), per_page):
            page_items = self._items[start:start + per_page]
            page = self._create_page(page_items, page_index)
            self._carousel.append(page)
            page_index += 1
        
        self._dots.set_carousel(self._carousel)
        
        # Восстанавливаем позицию (не больше количества страниц)
        n_pages = self._carousel.get_n_pages()
        if n_pages > 0 and current_page > 0:
            target_page = min(current_page, n_pages - 1)
            GLib.idle_add(self._restore_page, target_page)
    
    def _restore_page(self, page_index):
        """Восстановить позицию carousel после загрузки."""
        if page_index < self._carousel.get_n_pages():
            self._carousel.scroll_to(self._carousel.get_nth_page(page_index), False)
        return False
    
    def _create_page(self, items, page_index: int) -> Gtk.Widget:
        cols = config.get("columns")
        rows = config.get("rows")
        
        cell_width, cell_height = config.cell_size
        min_width, min_height = config.grid_size
        
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.set_size_request(min_width, min_height)
        container.set_hexpand(True)
        container.set_vexpand(True)
        
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(8)
        grid.set_row_spacing(8)
        grid.set_margin_start(16)
        grid.set_margin_end(16)
        grid.set_margin_top(12)
        grid.set_margin_bottom(12)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)
        grid.set_size_request(min_width - 32, min_height - 24)
        
        # Заполняем все ячейки placeholder'ами
        for r in range(rows):
            for c in range(cols):
                placeholder = Gtk.Box()
                placeholder.set_size_request(cell_width, cell_height)
                grid.attach(placeholder, c, r, 1, 1)
        
        container.append(grid)
        self._grids.append(grid)
        
        # Добавляем реальные элементы
        for idx, (typ, data) in enumerate(items):
            if typ == "folder":
                tile = FolderTile(data)
                tile.connect("open", lambda t, fid: self.emit("folder-open", fid))
                tile.connect("renamed", lambda t, fid: self.emit("folder-rename", fid))
                tile.connect("deleted", lambda t, fid: self.emit("folder-delete", fid))
            else:
                tile = AppTile(data)
                tile.connect("launched", lambda t: self.emit("app-launched"))
                tile.connect("folder-create", self._on_folder_create)
                tile.connect("fav-moved", self._on_fav_moved)
                tile.connect("drag-begin", lambda t: self.emit("drag-begin"))
                tile.connect("drag-end", lambda t: self.emit("drag-end"))
            
            row = idx // cols
            col = idx % cols
            
            old = grid.get_child_at(col, row)
            if old:
                grid.remove(old)
            grid.attach(tile, col, row, 1, 1)
        
        return container
    
    def _on_folder_create(self, tile, app1: str, app2: str):
        folders.create("Новая папка", [app1, app2])
        self._populate()
    
    def _on_fav_moved(self, tile, moved_app: str, target_app: str):
        """Переместить закреплённое приложение."""
        if favorites.contains(target_app):
            favorites.move(moved_app, target_app)
    
    def _update_carousel_size(self):
        """Обновить минимальный размер карусели."""
        min_width, min_height = config.grid_size
        self._carousel.set_size_request(min_width, min_height)
        self.set_size_request(min_width, min_height + 30)
    
    @property
    def has_items(self) -> bool:
        """Есть ли элементы в сетке."""
        return len(self._items) > 0
    
    def activate_first(self) -> bool:
        """Активировать первый элемент (для Enter из поиска)."""
        if self.has_items and self._grids:
            first = self._grids[0].get_child_at(0, 0)
            if isinstance(first, (AppTile, FolderTile)):
                first.emit("clicked")
                return True
        return False
