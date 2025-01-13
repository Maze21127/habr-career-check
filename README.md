# Habr Career Checker

Скрипт, который собирает статистику, когда пользователь последний раз заходил на сайт https://career.habr.com

## Запуск
Необходимо создать файл `habr_cookies.json` с таким содержимым
```json
{
  "remember_user_token": "token"
}
```
Его можно получить после авторизации в браузере из Хранилища (cookies)

## Локальная разработка

Установить зависимости

```bash
poetry install --with dev
 ```

Установить git хуки

```bash
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
poetry run pre-commit install --hook-type pre-push
```

Tests
```python
poetry run pytest .
```