"""
Monitorix
Module: utils.validators
Author: Zainab

Description:
Validation utilities for Monitorix.

Responsibilities:
- Validate common application data
- Validate Discord related identifiers
- Validate configuration inputs
- Provide reusable validation methods
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class Validator:
    """
    Central validation service.

    Provides static validation methods
    used across Monitorix modules.
    """

    DISCORD_ID_PATTERN = re.compile(
        r"^[0-9]{17,20}$"
    )

    USERNAME_PATTERN = re.compile(
        r"^[a-zA-Z0-9_.-]{2,32}$"
    )

    URL_PATTERN = re.compile(
        r"^https?://",
        re.IGNORECASE,
    )

    # ------------------------------------------------------------------

    @staticmethod
    def is_valid_discord_id(
        value: str | int | None,
    ) -> bool:
        """
        Validate Discord snowflake ID.

        Args:
            value:
                Discord identifier.

        Returns:
            True if valid.
        """

        if value is None:
            return False

        return bool(
            Validator.DISCORD_ID_PATTERN.match(
                str(value)
            )
        )

    # ------------------------------------------------------------------

    @staticmethod
    def is_valid_username(
        username: str | None,
    ) -> bool:
        """
        Validate Discord username format.
        """

        if not username:
            return False

        return bool(
            Validator.USERNAME_PATTERN.match(
                username
            )
        )

    # ------------------------------------------------------------------

    @staticmethod
    def is_valid_url(
        url: str | None,
    ) -> bool:
        """
        Validate URL format.
        """

        if not url:
            return False

        return bool(
            Validator.URL_PATTERN.match(
                url
            )
        )

    # ------------------------------------------------------------------

    @staticmethod
    def is_safe_path(
        path: str | Path,
        base_directory: Path,
    ) -> bool:
        """
        Prevent unsafe path traversal.

        Args:
            path:
                Requested path.

            base_directory:
                Allowed root directory.

        Returns:
            True if path is inside base directory.
        """

        try:
            target = Path(
                path
            ).resolve()

            base = Path(
                base_directory
            ).resolve()

            return base in target.parents or target == base

        except (
            OSError,
            ValueError,
        ):
            return False

    # ------------------------------------------------------------------

    @staticmethod
    def is_non_empty(
        value: Any,
    ) -> bool:
        """
        Validate non-empty values.
        """

        if value is None:
            return False

        if isinstance(
            value,
            str,
        ):
            return bool(
                value.strip()
            )

        return True

    # ------------------------------------------------------------------

    @staticmethod
    def is_positive_integer(
        value: Any,
    ) -> bool:
        """
        Validate positive integer.
        """

        try:
            return int(value) > 0

        except (
            TypeError,
            ValueError,
        ):
            return False

    # ------------------------------------------------------------------

    @staticmethod
    def validate_required_fields(
        data: dict[str, Any],
        fields: list[str],
    ) -> bool:
        """
        Check required dictionary fields.

        Args:
            data:
                Input dictionary.

            fields:
                Required keys.

        Returns:
            True when all fields exist.
        """

        for field in fields:

            if field not in data:
                return False

            if not Validator.is_non_empty(
                data[field]
            ):
                return False

        return True


# ----------------------------------------------------------------------
# Global Validator Instance
# ----------------------------------------------------------------------

validator = Validator()