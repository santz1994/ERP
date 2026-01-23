"""Timezone Configuration - WIB (GMT+7)
Ensures all datetime operations use Jakarta timezone.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# WIB Timezone (Western Indonesian Time - Jakarta)
WIB_TZ = ZoneInfo("Asia/Jakarta")
WIB_OFFSET = timedelta(hours=7)


def now_wib() -> datetime:
    """Get current datetime in WIB timezone.

    Returns:
        datetime: Current datetime with WIB timezone

    Example:
        >>> now_wib()
        datetime.datetime(2026, 1, 19, 15, 30, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Jakarta'))

    """
    return datetime.now(WIB_TZ)


def to_wib(dt: datetime) -> datetime:
    """Convert datetime to WIB timezone.

    Args:
        dt: Datetime object (can be naive or aware)

    Returns:
        datetime: Datetime converted to WIB timezone

    Example:
        >>> utc_time = datetime.now(timezone.utc)
        >>> wib_time = to_wib(utc_time)

    """
    if dt.tzinfo is None:
        # Naive datetime, assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(WIB_TZ)


def utc_to_wib(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to WIB.

    Args:
        utc_dt: UTC datetime

    Returns:
        datetime: WIB datetime

    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(WIB_TZ)


def wib_to_utc(wib_dt: datetime) -> datetime:
    """Convert WIB datetime to UTC.

    Args:
        wib_dt: WIB datetime

    Returns:
        datetime: UTC datetime

    """
    if wib_dt.tzinfo is None:
        wib_dt = wib_dt.replace(tzinfo=WIB_TZ)
    return wib_dt.astimezone(timezone.utc)


def format_wib(dt: datetime | None, format: str = "%Y-%m-%d %H:%M:%S WIB") -> str:
    """Format datetime to WIB string.

    Args:
        dt: Datetime object
        format: Format string (default: YYYY-MM-DD HH:MM:SS WIB)

    Returns:
        str: Formatted datetime string

    Example:
        >>> format_wib(now_wib())
        '2026-01-19 15:30:00 WIB'

    """
    if dt is None:
        return ""

    wib_dt = to_wib(dt)
    return wib_dt.strftime(format)


def parse_wib(date_string: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse WIB datetime string.

    Args:
        date_string: Datetime string (e.g., '2026-01-19 15:30:00')
        format: Format string

    Returns:
        datetime: Datetime with WIB timezone

    Example:
        >>> parse_wib('2026-01-19 15:30:00')
        datetime.datetime(2026, 1, 19, 15, 30, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Jakarta'))

    """
    dt = datetime.strptime(date_string, format)
    return dt.replace(tzinfo=WIB_TZ)


def get_shift(dt: datetime | None = None) -> str:
    """Get production shift based on WIB time.

    Shift schedule:
    - Shift 1: 07:00 - 15:00 WIB
    - Shift 2: 15:00 - 23:00 WIB
    - Shift 3: 23:00 - 07:00 WIB (night shift)

    Args:
        dt: Datetime (default: now_wib())

    Returns:
        str: 'Shift 1', 'Shift 2', or 'Shift 3'

    Example:
        >>> get_shift(parse_wib('2026-01-19 10:00:00'))
        'Shift 1'

    """
    dt = now_wib() if dt is None else to_wib(dt)

    hour = dt.hour

    if 7 <= hour < 15:
        return "Shift 1"
    elif 15 <= hour < 23:
        return "Shift 2"
    else:
        return "Shift 3"


def get_work_week(dt: datetime | None = None) -> int:
    """Get ISO work week number.

    Args:
        dt: Datetime (default: now_wib())

    Returns:
        int: ISO week number (1-53)

    Example:
        >>> get_work_week(parse_wib('2026-01-19 10:00:00'))
        4

    """
    dt = now_wib() if dt is None else to_wib(dt)

    return dt.isocalendar()[1]


def get_delivery_week(dt: datetime | None = None, weeks_ahead: int = 4) -> int:
    """Calculate delivery week (current week + offset).

    Args:
        dt: Datetime (default: now_wib())
        weeks_ahead: Number of weeks to add

    Returns:
        int: Delivery week number

    Example:
        >>> get_delivery_week(parse_wib('2026-01-19 10:00:00'), weeks_ahead=4)
        8

    """
    dt = now_wib() if dt is None else to_wib(dt)

    future_dt = dt + timedelta(weeks=weeks_ahead)
    return future_dt.isocalendar()[1]


def is_working_hours(dt: datetime | None = None) -> bool:
    """Check if datetime is within working hours (07:00 - 23:00 WIB).

    Args:
        dt: Datetime (default: now_wib())

    Returns:
        bool: True if within working hours

    """
    dt = now_wib() if dt is None else to_wib(dt)

    hour = dt.hour
    return 7 <= hour < 23


def start_of_day_wib(dt: datetime | None = None) -> datetime:
    """Get start of day (00:00:00) in WIB.

    Args:
        dt: Datetime (default: now_wib())

    Returns:
        datetime: Start of day in WIB

    """
    dt = now_wib() if dt is None else to_wib(dt)

    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day_wib(dt: datetime | None = None) -> datetime:
    """Get end of day (23:59:59) in WIB.

    Args:
        dt: Datetime (default: now_wib())

    Returns:
        datetime: End of day in WIB

    """
    dt = now_wib() if dt is None else to_wib(dt)

    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


# Helper for database datetime storage
def get_db_timestamp() -> datetime:
    """Get timestamp for database storage (UTC)
    PostgreSQL stores timestamps in UTC by default.

    Returns:
        datetime: Current UTC datetime

    """
    return datetime.now(timezone.utc)


def format_for_display(dt: datetime | None) -> str:
    """Format datetime for UI display (WIB).

    Args:
        dt: Datetime from database (UTC)

    Returns:
        str: Formatted WIB string for display

    Example:
        >>> db_time = datetime.now(timezone.utc)
        >>> format_for_display(db_time)
        '19 Jan 2026, 15:30 WIB'

    """
    if dt is None:
        return "-"

    wib_dt = to_wib(dt)
    return wib_dt.strftime("%d %b %Y, %H:%M WIB")
