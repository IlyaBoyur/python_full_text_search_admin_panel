import os

from dotenv import load_dotenv

load_dotenv()

SQLITE_DB_NAME = os.environ.get("SQLITE_PATH", "db.sqlite")
BULK_SIZE = int(os.environ.get("BULK_SIZE", "1"))
