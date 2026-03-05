# Contributing to Adwyra

Спасибо за интерес к проекту! 🎉

## Как помочь

### 🐛 Сообщить о баге

1. Проверьте, что баг ещё не был [зарегистрирован](https://github.com/cheviiot/adwyra/issues)
2. Создайте issue с описанием проблемы
3. Укажите версию Python, GTK4, дистрибутив

### 💡 Предложить улучшение

Создайте issue с тегом `enhancement` и опишите вашу идею.

### 🔧 Отправить Pull Request

1. Форкните репозиторий
2. Создайте ветку: `git checkout -b feature/my-feature`
3. Сделайте изменения
4. Проверьте код: `python3 -m py_compile src/adwyra/app.py`
5. Закоммитьте: `git commit -m "Add: описание"`
6. Запушьте: `git push origin feature/my-feature`
7. Откройте Pull Request

## Стиль кода

- Python 3.10+
- PEP 8
- Комментарии на русском или английском
- Docstrings для публичных методов

## Запуск из исходников

```bash
./src/adwyra-launcher
```

## Тестирование

```bash
python3 -m py_compile src/adwyra/app.py
```
