"""Time utility helpers."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def to_iso(dt: datetime) -> str:
    """Convert datetime to ISO8601 string."""
    return dt.isoformat()


def elapsed_seconds(start: datetime, end: datetime) -> float:
    """Compute elapsed seconds between start and end."""
    return (end - start).total_seconds()
