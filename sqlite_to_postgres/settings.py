import os

from dotenv import load_dotenv

load_dotenv()


SQLITE_DATABASE = os.environ.get("SQLITE_DATABASE", "db.sqlite")

POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_INIT = os.environ.get("POSTGRES_INIT", "")

BULK_SIZE = int(os.environ.get("BULK_SIZE", 1))
