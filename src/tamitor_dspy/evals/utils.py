from datetime import datetime, timedelta
from typing import Any


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def normalize_date(value: Any, context: dict[str, Any]) -> Any:
    if not isinstance(value, str):
        return value

    raw = value.strip()
    lowered = raw.lower()

    # Already ISO date
    try:
        datetime.strptime(raw, "%Y-%m-%d")
        return raw
    except ValueError:
        pass

    if lowered not in WEEKDAYS:
        return raw

    current_date_raw = context.get("current_date")
    if not current_date_raw:
        return raw

    current_dt = datetime.fromisoformat(current_date_raw)
    target_weekday = WEEKDAYS[lowered]

    days_ahead = (target_weekday - current_dt.weekday()) % 7

    # "Friday" means the next matching Friday.
    # If today is Friday, interpret as today.
    target_dt = current_dt + timedelta(days=days_ahead)

    return target_dt.date().isoformat()


def normalize_time(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    raw = value.strip().lower().replace(" ", "")

    # Already HH:MM
    try:
        return datetime.strptime(raw, "%H:%M").strftime("%H:%M")
    except ValueError:
        pass

    for fmt in ("%I:%M%p", "%I%p"):
        try:
            return datetime.strptime(raw, fmt).strftime("%H:%M")
        except ValueError:
            continue

    return value


def normalize_arg(key: str, value: Any, context: dict[str, Any]) -> Any:
    if key == "date":
        return normalize_date(value, context)

    if key == "time":
        return normalize_time(value)

    return value