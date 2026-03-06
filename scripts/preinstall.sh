#!/bin/bash
# Скрипт перед установкой/обновлением
# Запускается как root

# Удаляем только __pycache__ для избежания конфликтов
# НЕ удаляем весь /usr/lib/adwyra - файлы перезапишутся
find /usr/lib/adwyra -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

exit 0
