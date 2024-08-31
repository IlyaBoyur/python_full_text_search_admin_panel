# ETL SQLite -> PostgreSQL

## Технологии
### Python 3.12, sqlite3, psycopg2

## Назначение
Сервис реализует миграцию данных из SQLite в PostgreSQL


### Подготовка
1. Убедиться в наличии файла БД SQLite в текущей системе
1. Поднять БД PostgreSQL 
2. Определить настройки подключения и ETL-скрипта в .env (см. .env.example)

### Запуск
```bash
python load_data.py
```
