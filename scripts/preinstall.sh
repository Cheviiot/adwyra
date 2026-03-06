#!/bin/bash
# Скрипт удаления старых файлов перед обновлением
# Запускается как root

# Удаляем старый Python модуль чтобы избежать конфликтов
rm -rf /usr/lib/adwyra 2>/dev/null || true

# Обновляем кэш иконок если присутствует
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
fi

exit 0
