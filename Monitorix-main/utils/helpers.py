"""
Monitorix
Module: utils.helpers
Author: Zainab

Description:
Common helper utilities used across Monitorix.

Responsibilities:
- Provide reusable utility functions
- Handle formatting operations
- Provide timestamp helpers
- Provide safe data conversion helpers
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def get_utc_timestamp() -> str:
    """
    Return current UTC timestamp.

    Returns:
        ISO formatted UTC datetime.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


def format_datetime(
    value: datetime | str | None,
) -> str:
    """
    Format datetime values for display.

    Args:
        value:
            datetime object or string.

    Returns:
        Human readable datetime.
    """

    if value is None:
        return "N/A"

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(
                value
            )
        except ValueError:
            return value

    return value.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def sanitize_text(
    text: str | None,
    limit: int = 500,
) -> str:
    """
    Clean and limit text content.

    Args:
        text:
            Input text.
        limit:
            Maximum allowed length.

    Returns:
        Sanitized text.
    """

    if not text:
        return ""

    cleaned = (
        text
        .replace("\x00", "")
        .strip()
    )

    if len(cleaned) > limit:
        return (
            cleaned[:limit]
            + "..."
        )

    return cleaned


def ensure_directory(
    path: Path,
) -> Path:
    """
    Create directory if missing.

    Args:
        path:
            Directory path.

    Returns:
        Same path object.
    """

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert value into integer.

    Args:
        value:
            Input value.
        default:
            Fallback value.

    Returns:
        Integer result.
    """

    try:
        return int(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def safe_string(
    value: Any,
    default: str = "",
) -> str:
    """
    Safely convert value into string.

    Args:
        value:
            Input value.
        default:
            Fallback value.

    Returns:
        String result.
    """

    if value is None:
        return default

    return str(value)


def truncate_text(
    text: str,
    length: int = 100,
) -> str:
    """
    Shorten long text for console display.

    Args:
        text:
            Input text.
        length:
            Maximum length.

    Returns:
        Truncated text.
    """

    if len(text) <= length:
        return text

    return (
        text[:length]
        + "..."
    )


def format_bytes(
    size: int,
) -> str:
    """
    Convert bytes into readable format.

    Args:
        size:
            Number of bytes.

    Returns:
        Human readable size.
    """

    units = (
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    )

    value = float(size)

    for unit in units:

        if value < 1024:
            return (
                f"{value:.2f} {unit}"
            )

        value /= 1024

    return (
        f"{value:.2f} PB"
    )