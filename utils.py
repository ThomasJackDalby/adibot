import datetime
from constants import SESSION_START_WEEKDAY, SESSION_START_TIME, SESSION_END_WEEKDAY, SESSION_END_TIME

def get_current_or_last_session_start_date(current_date: datetime.date) -> datetime.date:
    """Gets the datetime.date for the start of the current or last session relative to the provided datetime.date."""
    while current_date.weekday() != SESSION_START_WEEKDAY:
        current_date -= datetime.timedelta(days=1)
    return current_date

def is_valid_session_from_datetime(datetime: datetime.datetime) -> bool:
    """Checks whether the provided datetime is within a valid session window."""
    return is_valid_session(datetime.weekday(), datetime.hour)

def is_valid_session(weekday: int, hour: int) -> bool:
    """Checks whether the provided weekday and hour combination is within a valid session window."""
    if weekday == SESSION_START_WEEKDAY:
        return hour >= SESSION_START_TIME
    elif weekday == SESSION_END_WEEKDAY:
        return hour <= SESSION_END_TIME
    return False