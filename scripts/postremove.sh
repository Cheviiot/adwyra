#!/bin/bash
# Скрипт после удаления
# Запускается как root
#
# ВАЖНО: При обновлении этот скрипт запускается ПОСЛЕ установки новой версии!
# Поэтому НЕ удаляем файлы — rpm сам управляет ими.
# Удаляем только если пакет полностью удалён (не обновлён).

# $1 = 0 означает полное удаление, $1 > 0 означает обновление
if [ "${1:-0}" -eq 0 ]; then
    # Полное удаление — очищаем всё
    rm -rf /usr/lib/adwyra 2>/dev/null || true
fi

# Обновляем кэш иконок
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -q /usr/share/icons/hicolor 2>/dev/null || true
fi

# Обновляем desktop базу данных
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

exit 0
