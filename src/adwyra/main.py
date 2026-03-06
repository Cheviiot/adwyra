# -*- coding: utf-8 -*-
"""Точка входа."""

import sys
import os

# Все __pycache__ в единую папку
sys.pycache_prefix = os.path.join(
    os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
    "adwyra",
    "pycache"
)

from .application import Application


def main():
    app = Application()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
