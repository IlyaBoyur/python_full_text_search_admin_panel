## Способы загрузки данных в PostgreSQL

### Одиночный INSERT
```sql
INSERT INTO content.temp_table (id, name) VALUES ('ca211dbc-a6c6-44a5-b238-39fa16bbfe6c', 'Иван Иванов');
```
Оптимизация: писать данные в одной транзакции, предварительно отключив опцию
автокоммита.  
Это сильно ускоряет запись данных. Разницы не
будет, если записывать небольшой объём данных. 
Но если количество записей переваливает несколько десятков тысяч, этот
метод потребует больше производительности.


### Синтаксис INSERT для загрузки пачки
```sql
INSERT INTO content.temp_table (id, name)
VALUES
('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Василий Васильевич'),
('2d5c50d0-0bb4-480c-beab-ded6d0760269', 'Пётр Петрович');
```

В отличие от одиночной вставки данных, здесь вставляется сразу
несколько записей в рамках одной транзакции. Если при вставке
произойдёт ошибка, то свойство атомарности записи у транзакций не
допустит частичной вставки.

### UPSERT (INSERT .. ON CONFLICT)
Всё бы ничего, да вот хочется в случае конфликтов как-то их
обрабатывать. Для этого можно использовать механизм UPSERT,
который относительно недавно появился в Postgres.  

Конструкция 1: в случае конфликта проигнорируй строку
```sql
INSERT INTO content.temp_table (id, name)
VALUES ('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Иван Иванов')
ON CONFLICT (id) DO NOTHING;
```
Конструкция 2: в случае конфликта обнови строку
```sql
INSERT INTO content.temp_table (id, name)
VALUES ('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Иван Иванов')
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name;
```
Специальное выражение EXCLUDED содержит данные, 
которые предлагаются для вставки в строку. В этом
случае поле name изменится на Иван Иванов.  
Чаще всего этот механизм можно встретить в ETL-операциях, если
предусмотрено обновление уже существующих данных. В таких
ситуациях, как правило, нужно обновлять уже существующие записи —
как раз здесь очень выручает UPSERT.

Плюсы
+ Делать вставки с возможностью обновления уже существующих
строк.
+ Уменьшить число ошибок при вставках данных.

Минусы
- Вставка происходит медленнее из-за дополнительных действий.
- Поля, участвующие в выражении ON CONFLICT, должны
обязательно быть либо в индексе, либо иметь ограничение на
уникальность.

### \COPY
```sql
BEGIN;
TRUNCATE content.temp_table;
\COPY content.temp_table FROM /path/to/file/content.csv delimiter
',' quote '"' csv header;
COMMIT;
```
Плюсы
+ Cамый быстрый из всех способов загрузки данных в PostgreSQL.
+ Вставка происходит через чтение файла, а не с помощью запросов в БД.
Чаще всего встречается загрузка CSV-файла напрямую в указанную таблицу в БД.

Минусы
- Через COPY данные добавляются к уже существующим, поэтому любая ошибка
дублирования или вставки данных сразу же прерывает выполнение
команды

### Оптимизации загрузки
1. Использовать множество одиночных INSERT в одной транзакции
2. Использовать \COPY
3. Использовать PREPARE
```sql
PREPARE temp_table_insert (uuid, text) AS
INSERT INTO content.temp_table VALUES($1, $2);
TRUNCATE content.temp_table;
\set autocommit off
BEGIN;
EXECUTE temp_table_insert('ca211dbc-a6c6-44a5-
b238-39fa16bbfe6c', 'Иван Иванов');
EXECUTE temp_table_insert('b8531efb-
c49d-4111-803f-725c3abc0f5e', 'Василий Васильевич');
EXECUTE temp_table_insert('2d5c50d0-0bb4-480c-beab-
ded6d0760269', 'Пётр Петрович');
COMMIT;
\set autocommit on

```
4. Удалить индексы, вставить, создать индексы
```sql
CREATE INDEX ... CONCURENTLY;
```
Другие способы описаны подробно в [документации](https://postgrespro.ru/docs/postgrespro/12/populate)


## Способы загрузки данных в PostgreSQL на Python
```bash
pip install psycopg2-binary
```
Устанавливайте именно **psycopg2-binary**. Так вам не придётся
компилировать код, который может иногда не собираться.

```python
import io
import psycopg2

# Подготавливаем DSN (Data Source Name) для подключения к БД Postgres
dsn = {
    "dbname": "movies_database",
    "user": "postgres",
    "password": 1234,
    "host": "127.0.0.1",
    "port": 5432,
}
# Вызываем через контекстный менеджер
# Это позволяет выполнить все операции в одной транзакции
# В конце завершается транзакция (cursor.commit()), 
# закрывается курсор (cursor.close()) и соединение (conn.close())
with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
    # Очищаем таблицу в БД, чтобы загружать данные в пустую таблицу
    cursor.execute("""TRUNCATE content.temp_table""")
    # Одиночный insert
    data = ("ca211dbc-a6c6-44a5-b238-39fa16bbfe6c", "Иван Иванов")
    cursor.execute(
        """INSERT INTO content.temp_table (id, name) VALUES (%s, %s)""",
        data,
    )
# Множественный insert
# Обращаем внимание на подготовку параметров для VALUES через cursor.mogrify
# Это позволяет без опаски передавать параметры на вставку
# mogrify позаботится об экранировании и подстановке нужных типов
# Именно поэтому можно склеить тело запроса с подготовленными параметрами
    data = [
        ("b8531efb-c49d-4111-803f-725c3abc0f5e", "Василий Васильевич"),
        ("2d5c50d0-0bb4-480c-beab-ded6d0760269", "Пётр Петрович"),
    ]
    args = ",".join(cursor.mogrify("(%s, %s)", item).decode() for item in data)
    cursor.execute(f"""
        INSERT INTO content.temp_table (id, name)
        VALUES {args}
        """
    )
# Пример использования UPSERT — обновляем уже существующую запись
    data = ("ca211dbc-a6c6-44a5-b238-39fa16bbfe6c", "Иван Петров")
    cursor.execute(
        """
        INSERT INTO content.temp_table (id, name)
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name
        """,
        data,
    )
    cursor.execute(
        """SELECT name FROM content.temp_table WHERE id = 'ca211dbc-a6c6-44a5-b238-39fa16bbfe6c'"""
    )
    result = cursor.fetchone()
    print("Результат выполнения команды UPSERT ", result)
# Используем команду COPY
# Для работы COPY требуется взять данные из файла или подготовить файловый объект через io.StringIO
    cursor.execute("""TRUNCATE content.temp_table""")
    data = io.StringIO()
    data.write("ca211dbc-a6c6-44a5-b238-39fa16bbfe6c,Михаил Михайлович")
    data.seek(0)
    cursor.copy_from(data, "content.temp_table", sep=",", columns=["id", "name"])
    cursor.execute(
        """SELECT name FROM content.temp_table WHERE id
    = 'ca211dbc-a6c6-44a5-b238-39fa16bbfe6c'"""
    )
    result = cursor.fetchone()
    print("Результат выполнения команды COPY ", result)
```

[Про обычные python-объекты вместо сырых запросов в документации psycopg2](https://www.psycopg.org/docs/advanced.html#adapting-new-python-types-to-sql-syntax)
