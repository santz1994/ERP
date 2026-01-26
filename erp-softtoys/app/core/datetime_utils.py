"""DateTime utility functions for consistent handling across the API.

Standardizes:
- Timezone: UTC for storage, Asia/Jakarta for display
- Format: ISO 8601 for JSON responses
- Serialization: Custom JSON encoder for datetime objects
"""

import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
from uuid import UUID


# Timezone definitions
UTC_TZ = timezone.utc
JAKARTA_TZ = timezone(timedelta(hours=7))  # UTC+7 (Jakarta time)


def utc_now() -> datetime:
    """Get current time in UTC.
    
    **Returns**:
    - timezone-aware datetime in UTC
    
    **Usage**:
    ```python
    from app.core.datetime_utils import utc_now
    created_at = utc_now()
    ```
    """
    return datetime.now(UTC_TZ)


def to_jakarta_time(dt: datetime) -> datetime:
    """Convert datetime to Jakarta timezone (WIB - UTC+7).
    
    **Parameters**:
    - `dt`: datetime object (can be naive or timezone-aware)
    
    **Returns**:
    - datetime in Asia/Jakarta timezone
    
    **Usage**:
    ```python
    utc_dt = utc_now()
    jakarta_dt = to_jakarta_time(utc_dt)
    print(jakarta_dt)  # 2026-01-27 15:30:00+07:00
    ```
    """
    if dt is None:
        return None
    
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    
    return dt.astimezone(JAKARTA_TZ)


def to_iso_string(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string format.
    
    **Parameters**:
    - `dt`: datetime object
    
    **Returns**:
    - ISO 8601 formatted string (e.g., "2026-01-27T15:30:00+00:00")
    
    **Usage**:
    ```python
    dt = utc_now()
    iso_str = to_iso_string(dt)
    ```
    """
    if dt is None:
        return None
    
    if not isinstance(dt, datetime):
        return str(dt)
    
    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    
    return dt.isoformat()


class DateTimeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and other types.
    
    Handles:
    - datetime objects → ISO 8601 strings
    - Decimal → float
    - UUID → string
    - Enum → value
    - timezone-aware datetimes → ISO format with timezone
    
    **Usage**:
    ```python
    from fastapi.responses import JSONResponse
    from app.core.datetime_utils import DateTimeJSONEncoder
    
    # In FastAPI app configuration:
    app.json_encoder = DateTimeJSONEncoder
    ```
    """
    
    def default(self, obj):  # noqa: A001
        """Encode objects that are not JSON serializable."""
        if isinstance(obj, datetime):
            # Return ISO 8601 format with timezone
            return to_iso_string(obj)
        elif isinstance(obj, Decimal):
            # Convert Decimal to float for JSON
            return float(obj)
        elif isinstance(obj, UUID):
            # Convert UUID to string
            return str(obj)
        elif isinstance(obj, Enum):
            # Convert Enum to its value
            return obj.value
        elif hasattr(obj, 'isoformat'):
            # Handle date objects
            return obj.isoformat()
        
        # Let the base class handle other types
        return super().default(obj)


def format_timestamp(dt: datetime, timezone_display: str = "utc") -> str:
    """Format timestamp for display with optional timezone conversion.
    
    **Parameters**:
    - `dt`: datetime object
    - `timezone_display`: "utc" or "jakarta" (default: "utc")
    
    **Returns**:
    - Formatted datetime string
    
    **Usage**:
    ```python
    dt = utc_now()
    # Display in UTC: "2026-01-27T15:30:00+00:00"
    print(format_timestamp(dt, "utc"))
    # Display in Jakarta: "2026-01-27T22:30:00+07:00"
    print(format_timestamp(dt, "jakarta"))
    ```
    """
    if dt is None:
        return None
    
    if timezone_display == "jakarta":
        dt = to_jakarta_time(dt)
    elif timezone_display != "utc":
        raise ValueError("timezone_display must be 'utc' or 'jakarta'")
    
    return dt.isoformat()


def parse_datetime_string(date_string: str) -> datetime:
    """Parse ISO 8601 datetime string to UTC datetime object.
    
    **Parameters**:
    - `date_string`: ISO 8601 formatted string
    
    **Returns**:
    - timezone-aware datetime in UTC
    
    **Raises**:
    - ValueError if string format is invalid
    
    **Usage**:
    ```python
    dt_str = "2026-01-27T15:30:00Z"
    dt = parse_datetime_string(dt_str)
    ```
    """
    if isinstance(date_string, datetime):
        return date_string
    
    try:
        # Try parsing with timezone
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        try:
            # Try parsing without timezone (assume UTC)
            dt = datetime.fromisoformat(date_string)
            dt = dt.replace(tzinfo=UTC_TZ)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid datetime string format: {date_string}") from e
    
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    else:
        dt = dt.astimezone(UTC_TZ)
    
    return dt


def get_date_range(start_date: datetime, end_date: datetime):
    """Get tuple of start and end dates for date range queries.
    
    **Parameters**:
    - `start_date`: Start of range (datetime or None)
    - `end_date`: End of range (datetime or None)
    
    **Returns**:
    - Tuple of (start_date_utc, end_date_utc)
    
    **Usage**:
    ```python
    start = parse_datetime_string("2026-01-01T00:00:00Z")
    end = parse_datetime_string("2026-01-31T23:59:59Z")
    start_utc, end_utc = get_date_range(start, end)
    
    # Use in query:
    records = db.query(Model).filter(
        Model.created_at >= start_utc,
        Model.created_at <= end_utc
    )
    ```
    """
    if start_date and not isinstance(start_date, datetime):
        start_date = parse_datetime_string(str(start_date))
    
    if end_date and not isinstance(end_date, datetime):
        end_date = parse_datetime_string(str(end_date))
    
    # Ensure UTC
    if start_date and start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=UTC_TZ)
    if end_date and end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=UTC_TZ)
    
    return start_date, end_date
