import random
import uuid
import psycopg2
from typing import Generator
from contextlib import closing
from psycopg2.extras import execute_batch, _cursor, _connection


def generate_genre_film_work(cursor: _cursor) -> None:
    cursor.execute("SELECT id FROM film_work")
    film_works_ids = (data[0] for data in cursor.fetchall())
    genres = ["comedy", "horror", "action", "drama"]
    print("inserting genres...")
    execute_batch(
        cursor,
        "INSERT INTO genre_film_work (id, film_work_id, genre) VALUES (%s, %s, %s)",
        [
            (str(uuid.uuid4()), film_work_id, random.choice(genres))
            for film_work_id in film_works_ids
        ],
        page_size=5000,
    )
    print("genres inserted")


def generate_person(connection: _connection) -> None:
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM film_work")
    film_works_ids = []
    film_works_ids = [data[0] for data in cursor.fetchall()]

    persons_ids = (str(uuid.uuid4()) for _ in range(600_000))
    print("inserting persons...")
    execute_batch(
        cursor,
        "INSERT INTO person (id) VALUES (%s)",
        [(i,) for i in persons_ids],
        page_size=5000,
    )
    connection.commit()
    print("persons has been inserted")
    print("creating relations...")
    film_work_person_data = []
    for film_work_id in film_works_ids:
        for person_id in random.sample(persons_ids, 5):
            film_work_person_data.append(
                (str(uuid.uuid4()), film_work_id, person_id),
            )
    print("inserting relations...")
    execute_batch(
        cursor,
        "INSERT INTO person_film_work (id, film_work_id, person_id) VALUES (%s, %s, %s)",
        film_work_person_data,
        page_size=5000,
    )
    connection.commit()
    cursor.close()
    print("relations inserted")


def get_db_session() -> Generator[_connection, None, None]:
    with closing(
        psycopg2.connect(
            dbname="movies",
            user="postgres",
            password="postgres",
            host="localhost",
            port=15432,
            options="-c search_path=content",
        )
    ) as connection:
        yield connection


if __name__ == "__main__":
    for conn in get_db_session():
        generate_person(conn)
