# Adwyra

**Лаунчер приложений для Linux в стиле macOS Launchpad**

<p>
  <img src="https://img.shields.io/badge/GTK-4.0-green?style=flat-square" alt="GTK 4">
  <img src="https://img.shields.io/badge/Libadwaita-1.0-blue?style=flat-square" alt="Libadwaita">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/License-GPL--3.0-red?style=flat-square" alt="License">
</p>

## Возможности

- 🎯 Сетка всех приложений с иконками
- ⭐ Закрепление избранных (ПКМ)
- 🔍 Мгновенный поиск
- 🎨 Нативный стиль GNOME/Adwaita
- ⌨️ Горячие клавиши: `Ctrl+F`, `Esc`
- 🪟 Авто-закрытие при потере фокуса

## Установка

```bash
# Stapler (рекомендуется)
stplr repo add adwyra https://github.com/cheviiot/adwyra.git
stplr refresh && stplr install adwyra

# Или вручную
git clone https://github.com/cheviiot/adwyra.git && cd adwyra
./src/adwyra-launcher
```

<details>
<summary>Зависимости</summary>

| Дистрибутив | Команда |
|-------------|---------|
| Debian/Ubuntu | `sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1` |
| Fedora | `sudo dnf install python3-gobject gtk4 libadwaita` |
| Arch | `sudo pacman -S python-gobject gtk4 libadwaita` |
| ALT Linux | `sudo apt-get install python3-module-pygobject3 libgtk4 libadwaita` |

</details>

## Использование

```bash
adwyra
```

| Клавиша | Действие |
|---------|----------|
| `Ctrl+F` | Поиск |
| `Esc` | Закрыть |
| `ПКМ` | Закрепить/Открепить |

## Лицензия

[GPL-3.0-or-later](LICENSE)
