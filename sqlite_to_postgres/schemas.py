import uuid
from dataclasses import dataclass, field
from datetime import datetime

from types import MappingProxyType
from utils import current_datetime


@dataclass
class GenreSQLite:
    id: str
    name: str


@dataclass
class FilmWorkSQLite:
    id: str
    title: str
    description: str
    rating: float
    type: str = ""


@dataclass
class PersonSQLite:
    id: str
    full_name: str


@dataclass
class FilmWorkPg:
    id: uuid.UUID
    title: str = ""
    description: str = ""
    creation_date: datetime = None
    certificate: str = ""
    file_path: str = ""
    rating: float = 0.0
    type: str | None = None
    created_at: datetime = field(default_factory=current_datetime)
    updated_at: datetime = field(default_factory=current_datetime)


@dataclass
class GenrePg:
    id: uuid.UUID
    name: str
    description: str = ""


@dataclass
class GenreFilmWorkPg:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonPg:
    id: uuid.UUID
    full_name: str


@dataclass
class PersonFilmWorkPg:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


PYTHON_2_PG_TYPE_MAPPING = MappingProxyType(
    {
        int: "integer",
        str: "text",
        uuid.UUID: "uuid",
        float: "float",
        datetime: "timestamp",
        None: "null",
    }
)
