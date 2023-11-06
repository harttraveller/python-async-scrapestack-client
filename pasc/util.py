from datetime import datetime


def compute_timedelta_seconds(start: datetime, end: datetime) -> float:
    "computes the timedelta in seconds between end and start"
    elapsed_timedelta = end - start
    elapsed = elapsed_timedelta.seconds + (elapsed_timedelta.microseconds / 1e6)
    return elapsed
