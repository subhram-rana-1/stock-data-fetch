from datetime import datetime, time, timedelta


time_format_string = "%H:%M:%S"
date_format_string = "%Y-%m-%d"


def to_ist_time(timestamp: datetime) -> time:
    ist = timestamp + timedelta(hours=5, minutes=30)
    return ist.time()


def to_ist_timestamp(timestamp: datetime) -> datetime:
    return timestamp + timedelta(hours=5, minutes=30)
