"""Timezone helpers for PocketOJ."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

try:  # Python 3.9+
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - fallback for older Python
    from backports.zoneinfo import ZoneInfo  # type: ignore

IST = ZoneInfo("Asia/Kolkata")
UTC = timezone.utc


def _coerce_datetime(value: Optional[object]) -> Optional[datetime]:
    """Parse value into a timezone-aware UTC datetime."""
    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value
    else:
        value_str = str(value).strip()
        if not value_str:
            return None
        if value_str.endswith('Z'):
            value_str = value_str[:-1] + '+00:00'
        if ' ' in value_str and 'T' not in value_str:
            value_str = value_str.replace(' ', 'T')
        dt = datetime.fromisoformat(value_str)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt


def utc_now() -> datetime:
    """Return current time as timezone-aware UTC datetime."""
    return datetime.now(UTC)


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 format with offset."""
    return utc_now().isoformat()


def to_utc(value: Optional[object]) -> Optional[datetime]:
    """Ensure a value is converted to UTC datetime."""
    return _coerce_datetime(value)


def to_ist(value: Optional[object]) -> Optional[datetime]:
    """Convert a timestamp value to IST timezone."""
    dt_utc = _coerce_datetime(value)
    return dt_utc.astimezone(IST) if dt_utc else None


def to_ist_iso(value: Optional[object]) -> str:
    """Return IST ISO-8601 string for the given timestamp."""
    dt = to_ist(value)
    return dt.isoformat() if dt else ''


def format_ist(value: Optional[object], fmt: str = '%b %d, %Y · %H:%M') -> str:
    """Format timestamp in IST using supplied strftime format."""
    dt = to_ist(value)
    return dt.strftime(fmt) if dt else ''
