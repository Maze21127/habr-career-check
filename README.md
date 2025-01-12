# Habr Career Checker

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