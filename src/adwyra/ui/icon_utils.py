# -*- coding: utf-8 -*-
"""Утилиты для работы с иконками."""

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, Gio, GdkPixbuf


def icon_needs_rounding(gicon: Gio.Icon, size: int) -> bool:
    """Определяет, нужно ли скруглять иконку.
    
    Проверяет угловые пиксели на прозрачность.
    Если углы непрозрачны — иконка квадратная, нужно скруглить.
    """
    if not gicon:
        return False
    
    try:
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        
        # Получаем иконку из темы
        icon_paintable = theme.lookup_by_gicon(
            gicon, size, 1, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.FORCE_REGULAR
        )
        if not icon_paintable:
            return False
        
        # Получаем путь к файлу
        icon_file = icon_paintable.get_file()
        if not icon_file:
            return False
        
        path = icon_file.get_path()
        if not path:
            return False
        
        # SVG иконки обычно современные с прозрачностью
        if path.endswith('.svg'):
            return False
        
        # Загружаем pixbuf
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
        if not pixbuf or not pixbuf.get_has_alpha():
            # Нет альфа-канала — точно квадратная
            return True
        
        width = pixbuf.get_width()
        height = pixbuf.get_height()
        rowstride = pixbuf.get_rowstride()
        pixels = pixbuf.get_pixels()
        n_channels = pixbuf.get_n_channels()
        
        if n_channels < 4:
            return True  # Нет альфа-канала
        
        # Проверяем угловые области (5x5 пикселей)
        corner_size = min(5, width // 4, height // 4)
        opaque_corners = 0
        total_checked = 0
        
        # Угловые координаты
        corners = [
            (0, 0),                          # верхний левый
            (width - corner_size, 0),        # верхний правый
            (0, height - corner_size),       # нижний левый
            (width - corner_size, height - corner_size)  # нижний правый
        ]
        
        for cx, cy in corners:
            for dy in range(corner_size):
                for dx in range(corner_size):
                    x = cx + dx
                    y = cy + dy
                    if 0 <= x < width and 0 <= y < height:
                        idx = y * rowstride + x * n_channels + 3  # альфа-канал
                        if idx < len(pixels):
                            alpha = pixels[idx]
                            total_checked += 1
                            if alpha > 200:  # Почти непрозрачный
                                opaque_corners += 1
        
        # Если больше 70% угловых пикселей непрозрачны — скруглять
        if total_checked > 0:
            return opaque_corners / total_checked > 0.7
        
        return False
        
    except Exception:
        return False
