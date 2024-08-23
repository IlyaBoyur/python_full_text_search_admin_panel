-- Установка расширения для генерации UUID
CREATE EXTENSION "uuid-ossp";
-- Генерация данных в интервале с 1900 по 2021 год с шагом в 1 час. В итоге сгенерируется 1060681 записей
CREATE SCHEMA IF NOT EXISTS content;
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type TEXT not null,
    created_at timestamp with time zone,
    updated_at timestamp with time zones
);
INSERT INTO content.film_work (id, title, type, creation_date, rating)
    SELECT uuid_generate_v4(), 'some name', 'movie', date::DATE, floor(random() * 100)
    FROM generate_series(
        '1900-01-01'::DATE,
        '2021-01-01'::DATE,
        '1 hour'::interval
    ) date;
-- Добавление B-tree индекса для ускорения поиска по полю типа date
CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date);
-- Проверка работы индекса: запрос для получения конкретной записи
EXPLAIN ANALYZE SELECT * FROM content.film_work WHERE
creation_date = '2020-04-01';
-- Проверка работы индекса: запрос по диапазону записей
EXPLAIN ANALYZE SELECT * FROM content.film_work WHERE
creation_date BETWEEN '2020-04-01' AND '2020-09-01';
-- Тест-сравнение размеров таблицы и её индексов
\dt+ content.film_work
\di+ content.film_work_creation_date_idx
\di+ content.film_work_pkey
-- Тест-сравнение времени вставки в таблицу с индексом и без него
\copy (select * from content.film_work) to '/output.csv' with csv;
TRUNCATE content.film_work;
DROP INDEX content.film_work_creation_date_idx;
\timing on
COPY content.film_work FROM '/output.csv' WITH DELIMITER ',' NULL '';
TRUNCATE content.film_work;
CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date);
COPY content.film_work FROM '/output.csv' WITH DELIMITER ',' NULL '';
-- Тест: высокая селективность индекса (плохо)
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre TEXT
);
CREATE INDEX genres_idx ON content.genre_film_work(genre);
-- Индекс не используется - высокая селективность (мало уникальных значений, много выдаваемых строк)
EXPLAIN ANALYSE SELECT * FROM
content.genre_film_work WHERE genre = 'comedy' LIMIT
200;
-- Композитный индекс - из нескольких полей - нельзя добавить одного актера к одному и тому же фильму дважды
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL
);
CREATE UNIQUE INDEX film_work_person ON content.person_film_work
(film_work_id, person_id);
-- Чтобы использовать индекс, нужно составить запрос с ограничением
-- по левой колонке, указанной в индексе film_work_id — композитный
-- индекс начнёт искать данные по лидирующей колонке, то есть слева
-- направо.
-- Запросы используют индекс:
EXPLAIN ANALYSE SELECT * FROM content.person_film_work WHERE film_work_id = 'c2f69a1c-e2c2-4dec-8a01-05e0f6395231';
EXPLAIN ANALYSE SELECT * FROM content.person_film_work 
WHERE film_work_id = 'c2f69a1c-e2c2-4dec-8a01-05e0f6395231' and person_id = 'f162bf63-faaa-4ac6-b62a-332abb435113';
EXPLAIN ANALYSE SELECT * FROM content.person_film_work
WHERE person_id = 'f162bf63-faaa-4ac6-b62a-332abb435113' and film_work_id = 'c2f69a1c-e2c2-4dec-8a01-05e0f6395231';

EXPLAIN ANALYSE SELECT * FROM content.film_work WHERE creation_date = '2020-01-07' AND rating = 88;
EXPLAIN ANALYSE SELECT * FROM content.film_work WHERE creation_date >= '2020-01-07';