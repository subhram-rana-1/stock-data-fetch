from datetime import datetime
from .constants import *


def current_ist_timestamp() -> datetime:
    return datetime.now().astimezone(IST_timezone)


def now_ist() -> time:
    return current_ist_timestamp().time()
