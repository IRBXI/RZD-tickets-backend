from datetime import datetime


def validate_traincode(s: str):
    if len(s) != 7:
        raise ValueError
    return s


def validate_date(date: str):
    try:
        datetime.strptime(date, "%d.%m.%Y")
    except ValueError as e:
        raise e
    return date


def validate_time(time: str):
    try:
        datetime.strptime(time, "%H:%M")
    except ValueError as e:
        raise e
    return time
