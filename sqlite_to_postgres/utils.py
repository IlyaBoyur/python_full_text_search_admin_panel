from datetime import datetime
from zoneinfo import ZoneInfo

from settings import TIMEZONE


def current_datetime() -> datetime:
    tz = ZoneInfo(TIMEZONE)
    return datetime.now(tz=tz)
