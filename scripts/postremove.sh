#!/bin/bash
# Скрипт после удаления
# Запускается как root

# Удаляем остатки Python модуля
rm -rf /usr/lib/adwyra 2>/dev/null || true

# Обновляем кэш иконок
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
fi

# Обновляем desktop базу данных
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi

exit 0
