from datetime import datetime

from pytz import timezone
from settings import TIMEZONE


def current_datetime() -> datetime:
    tz = timezone(TIMEZONE)
    return tz.localize(datetime.now())
