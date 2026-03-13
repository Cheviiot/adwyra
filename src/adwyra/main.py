# -*- coding: utf-8 -*-
"""Точка входа в приложение Adwyra.

Запуск: python -m adwyra
Или через установленный скрипт: adwyra
"""

import sys
import os

# Все __pycache__ в единую папку ~/.cache/adwyra/pycache
# чтобы не засорять исходники и packaged файлы
sys.pycache_prefix = os.path.join(
    os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
    "adwyra",
    "pycache"
)

from .application import Application


def main():
    """Запустить GTK приложение."""
    app = Application()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
