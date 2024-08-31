# ETL SQLite -> PostgreSQL

## Технологии
### Python 3.12, sqlite3, psycopg2

## Назначение
Сервис реализует миграцию данных из SQLite в PostgreSQL


### Подготовка
1. Убедиться в наличии файла БД SQLite в текущей системе
1. Поднять БД PostgreSQL 
2. Определить настройки подключения и ETL-скрипта в .env (см. .env.example)

### Установка и запуск
#### Настроить окружение
В папке сервиса:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Запустить ETL
```bash
python load_data.py
```
