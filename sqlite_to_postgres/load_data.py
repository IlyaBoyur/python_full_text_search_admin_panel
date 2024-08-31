import contextlib
import itertools
import logging
from dataclasses import asdict, astuple, fields
from typing import Iterable

import sqlite3
import psycopg2
from psycopg2.extensions import connection as _connection, cursor as _cursor
from psycopg2.extras import DictCursor, register_uuid

from settings import (
    BULK_SIZE,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_INIT,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
    SQLITE_DATABASE,
)
from schemas import (
    PersonPg,
    PersonSQLite,
    FilmWorkSQLite,
    GenreSQLite,
    GenrePg,
    FilmWorkPg,
    GenreFilmWorkPg,
    PersonFilmWorkPg,
    PYTHON_2_PG_TYPE_MAPPING,
)
from utils import current_datetime


logger = logging.getLogger(__name__)


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def _extract_film_genres(self, films: list[str]) -> dict[str, list[GenreSQLite]]:
        data = self.connection.execute(
            """SELECT fw.id, GROUP_CONCAT(g.id, ','), GROUP_CONCAT(g.name, ',')
            FROM genre g
            JOIN genre_film_work gfw on g.id == gfw.genre_id
            JOIN film_work fw on gfw.film_work_id == fw.id
            WHERE fw.id in ("""
            + ", ".join("?" for _ in films)
            + """)
            GROUP BY fw.id;""",
            films,
        ).fetchall()
        result = {
            id_: [
                GenreSQLite(genre_id, name)
                for genre_id, name in zip(genre_ids.split(","), genres.split(","))
            ]
            for id_, genre_ids, genres in data
        }
        return result

    def _extract_film_persons(self, films: list[str]) -> dict[str, PersonSQLite]:
        data = self.connection.execute(
            """SELECT p.id, p.full_name
            FROM person p
            JOIN person_film_work pfw on p.id == pfw.person_id
            JOIN film_work fw on pfw.film_work_id == fw.id
            WHERE fw.id in ("""
            + ", ".join("?" for _ in films)
            + """);""",
            films,
        ).fetchall()
        return {id_: PersonSQLite(id_, *record) for id_, *record in data}

    def _extract_film_persons_by_role(
        self, films: list[str], role: str
    ) -> dict[str, list[str]]:
        data = self.connection.execute(
            """SELECT fw.id, GROUP_CONCAT(p.id, ',')
            FROM person p
            JOIN person_film_work pfw on p.id == pfw.person_id
            JOIN film_work fw on pfw.film_work_id == fw.id
            WHERE fw.id in ("""
            + ", ".join("?" for _ in films)
            + """) and pfw.role == ?
            GROUP BY fw.id;""",
            (*films, role),
        ).fetchall()
        return {id_: person_ids.split(",") for id_, person_ids in data}

    def _extract_film_data(self, film_ids: list[str]) -> dict:
        result = {
            "genres": self._extract_film_genres(film_ids),
            "persons": self._extract_film_persons(film_ids),
            "film_actors": self._extract_film_persons_by_role(film_ids, "actor"),
            "film_directors": self._extract_film_persons_by_role(film_ids, "director"),
            "film_writers": self._extract_film_persons_by_role(film_ids, "writer"),
        }
        return result

    def bulk_generator(self, bulk_size: int | None = None):
        with contextlib.closing(self.connection.cursor()) as cursor:
            film_cursor = cursor.execute(
                "SELECT id, title, description, rating, type FROM film_work;"
            )
            while True:
                bulk = film_cursor.fetchmany(size=bulk_size or cursor.arraysize)
                if bulk:
                    films = [FilmWorkSQLite(*record) for record in bulk]
                    result = {
                        "films": films,
                        **self._extract_film_data([film.id for film in films]),
                    }
                    logger.debug("DATA FETCHED: %s", result)
                    yield result
                else:
                    break


class SQLiteToPgTransformer:
    @classmethod
    def transform_films(cls, data: Iterable[FilmWorkSQLite]) -> Iterable[FilmWorkPg]:
        return (
            FilmWorkPg(
                id=record.id,
                title=record.title or "",
                description=record.description or "",
                creation_date=None,
                certificate="",
                file_path="",
                rating=record.rating or 0.0,
                type=record.type,
            )
            for record in data
        )

    @classmethod
    def transform_genres(cls, data: Iterable[GenreSQLite]) -> Iterable[GenrePg]:
        return (GenrePg(**asdict(record)) for record in data)

    @classmethod
    def transform_persons(cls, data: Iterable[PersonSQLite]) -> Iterable[PersonPg]:
        return (PersonPg(**asdict(record)) for record in data)


class PostgresLoader:
    def __init__(self, connection: _connection) -> None:
        self.connection = connection
        register_uuid()

    def prepare(self) -> None:
        with self.connection.cursor() as cursor:
            self._prepare_film_work_query(cursor)

    def _prepare_film_work_query(self, cursor: _cursor) -> None:
        fw_fields = [f.name for f in fields(FilmWorkPg)]
        fw_poses = (
            f"NULLIF(${pose},'')" if f in ("type",) else f"${pose}"
            for pose, f in enumerate(fw_fields, 1)
        )
        fw_poses = ", ".join(fw_poses)
        fw_updates = ", ".join(
            field + "=EXCLUDED." + field
            for field in fw_fields
            if field not in ["id", "created_at"]
        )
        fw_fields = ", ".join(fw_fields)
        fw_field_types = ", ".join(
            PYTHON_2_PG_TYPE_MAPPING.get(f.type, "unknown") for f in fields(FilmWorkPg)
        )
        query = f"""
            PREPARE film_work_insert ({fw_field_types}) AS
            INSERT INTO content.film_work ({fw_fields})
                        VALUES({fw_poses})
            ON CONFLICT (id)
            DO UPDATE SET {fw_updates};
            """
        cursor.execute(query)

    def _load_film_work(self, cursor: _cursor, films: Iterable[FilmWorkPg]) -> None:
        pose_count = len(fields(FilmWorkPg))
        query = (
            f"EXECUTE film_work_insert({', '.join('%s' for _ in range(pose_count))});"
        )
        for film in films:
            cursor.execute(query, astuple(film))

    def _load_genre(self, cursor: _cursor, genres: Iterable[GenrePg]) -> None:
        data = (astuple(item) for item in genres)
        now = current_datetime().isoformat(sep=" ")
        data = ((*item, now, now) for item in set(data))

        args = ", ".join(
            cursor.mogrify("(%s, %s, %s, %s, %s)", item).decode() for item in data
        )

        cursor.execute(
            f"""
            INSERT INTO content.genre (id, name, description, updated_at, created_at)
            VALUES {args}
            ON CONFLICT (id) DO UPDATE SET 
                name=EXCLUDED.name,
                description=EXCLUDED.description,
                updated_at='{now}';
            """
        )

    def _load_person(self, cursor: _cursor, persons: Iterable[PersonPg]) -> None:
        now = current_datetime().isoformat(sep=" ")
        persons = ((*astuple(item), now, now) for item in persons)

        args = ", ".join(
            cursor.mogrify("(%s, %s, %s, %s)", item).decode() for item in persons
        )
        cursor.execute(
            f"""
            INSERT INTO content.person (id, full_name, updated_at, created_at)
            VALUES {args}
            ON CONFLICT (id) DO UPDATE SET full_name=EXCLUDED.full_name, updated_at='{now}';
            """
        )

    def _load_genre_film_work(
        self, cursor: _cursor, data: Iterable[GenreFilmWorkPg]
    ) -> None:
        data = (astuple(item) for item in data)
        now = current_datetime().isoformat(sep=" ")
        data = ((id_, fw_id, genre_id, now) for fw_id, genre_id, id_ in data)

        args = ", ".join(
            cursor.mogrify("(%s, %s, %s, %s)", item).decode() for item in data
        )
        cursor.execute(
            f"""
            INSERT INTO content.genre_film_work (id, film_work_id, genre_id, created_at)
            VALUES {args}
            ON CONFLICT DO NOTHING; 
            """
        )

    def _load_person_film_work(
        self, cursor: _cursor, data: Iterable[PersonFilmWorkPg]
    ) -> None:
        data = (astuple(item) for item in data)
        now = current_datetime().isoformat(sep=" ")
        data = ((id_, fw_id, p_id, role, now) for fw_id, p_id, role, id_ in data)

        args = ", ".join(
            cursor.mogrify("(%s, %s, %s, %s, %s)", item).decode() for item in data
        )
        cursor.execute(
            f"""
            INSERT INTO content.person_film_work (id, film_work_id, person_id, role, created_at)
            VALUES {args}
            ON CONFLICT DO NOTHING; 
            """
        )

    def bulk_load(self, data: dict[str, dict]) -> None:
        with self.connection.cursor() as cursor:
            films = SQLiteToPgTransformer.transform_films(data["films"])
            self._load_film_work(cursor, films)

            genres = SQLiteToPgTransformer.transform_genres(
                itertools.chain.from_iterable(data["genres"].values())
            )
            self._load_genre(cursor, genres)

            persons = SQLiteToPgTransformer.transform_persons(data["persons"].values())
            self._load_person(cursor, persons)

            genres_data = itertools.chain.from_iterable(
                (
                    GenreFilmWorkPg(film_work_id=fw_id, genre_id=genre.id)
                    for genre in genre_list
                )
                for fw_id, genre_list in data["genres"].items()
            )
            self._load_genre_film_work(cursor, genres_data)

            actors = itertools.chain.from_iterable(
                (PersonFilmWorkPg(fw_id, id_, "actor") for id_ in persons_ids)
                for fw_id, persons_ids in data["film_actors"].items()
            )
            directors = itertools.chain.from_iterable(
                (PersonFilmWorkPg(fw_id, id_, "director") for id_ in persons_ids)
                for fw_id, persons_ids in data["film_directors"].items()
            )
            writers = itertools.chain.from_iterable(
                (PersonFilmWorkPg(fw_id, id_, "writer") for id_ in persons_ids)
                for fw_id, persons_ids in data["film_writers"].items()
            )
            self._load_person_film_work(
                cursor, itertools.chain(actors, directors, writers)
            )


def load_from_sqlite(
    connection: sqlite3.Connection, pg_connection: _connection
) -> None:
    """Основной метод загрузки данных из SQLite в PostgreSQL."""
    postgres_loader = PostgresLoader(pg_connection)
    sqlite_extractor = SQLiteExtractor(connection)

    postgres_loader.prepare()
    for bulk in sqlite_extractor.bulk_generator(bulk_size=BULK_SIZE):
        postgres_loader.bulk_load(bulk)


if __name__ == "__main__":
    import subprocess

    if POSTGRES_INIT:
        subprocess.Popen(
            "psql -U {user} -h {host} -p {port} -d {name} -f {file}".format(
                user=POSTGRES_USER,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                name="postgres",
                file=POSTGRES_INIT,
            ),
            env={"PGPASSWORD": POSTGRES_PASSWORD},
            shell=True,
        ).wait()

    dsl = {
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
    }
    with contextlib.closing(
        sqlite3.connect(SQLITE_DATABASE)
    ) as sqlite_connection, psycopg2.connect(
        **dsl, cursor_factory=DictCursor
    ) as pg_connection:
        load_from_sqlite(sqlite_connection, pg_connection)
