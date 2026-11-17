"""
Monitorix
Module: modules.member
Author: Zainab

Description:
Discord member monitoring module.

Responsibilities:
- Track member join/leave activity
- Store member information
- Update member activity data
- Provide member statistics for CLI and reports
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database.database import database
from services.logger import logger
from utils.helpers import get_utc_timestamp, safe_string


class MemberMonitor:
    """
    Discord member monitoring handler.

    Handles member lifecycle events and data storage.
    """

    def __init__(self) -> None:
        logger.info(
            "Member monitor initialized"
        )

    # ------------------------------------------------------------------

    def register_member(
        self,
        member: Any,
    ) -> None:
        """
        Register or update Discord member.

        Args:
            member:
                Discord member object.
        """

        if member is None:
            return

        user_id = safe_string(
            getattr(
                member,
                "id",
                None,
            )
        )

        username = safe_string(
            getattr(
                member,
                "name",
                "Unknown",
            )
        )

        display_name = safe_string(
            getattr(
                member,
                "display_name",
                username,
            )
        )

        status = safe_string(
            getattr(
                getattr(
                    member,
                    "status",
                    None,
                ),
                "name",
                "offline",
            )
        )

        joined_at = self._get_join_time(
            member
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM members
            WHERE user_id = ?
            """,
            (
                user_id,
            ),
        )

        if existing:

            database.update(
                "members",
                {
                    "username": username,
                    "display_name": display_name,
                    "status": status,
                    "last_activity": get_utc_timestamp(),
                },
                "user_id = ?",
                (
                    user_id,
                ),
            )

        else:

            database.insert(
                "members",
                {
                    "user_id": user_id,
                    "username": username,
                    "display_name": display_name,
                    "status": status,
                    "joined_at": joined_at,
                    "last_activity": get_utc_timestamp(),
                },
            )

        logger.info(
            "Member registered: %s",
            username,
        )

    # ------------------------------------------------------------------

    def update_activity(
        self,
        user_id: str,
    ) -> None:
        """
        Update member last activity timestamp.

        Args:
            user_id:
                Discord user ID.
        """

        database.update(
            "members",
            {
                "last_activity": get_utc_timestamp(),
            },
            "user_id = ?",
            (
                user_id,
            ),
        )

    # ------------------------------------------------------------------

    def get_member(
        self,
        user_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve member information.

        Args:
            user_id:
                Discord user ID.

        Returns:
            Member information.
        """

        record = database.fetch_one(
            """
            SELECT *
            FROM members
            WHERE user_id = ?
            """,
            (
                user_id,
            ),
        )

        if not record:
            return None

        return dict(record)

    # ------------------------------------------------------------------

    def get_member_by_username(
        self,
        username: str,
    ) -> dict[str, Any] | None:
        """
        Find member by username.

        Args:
            username:
                Discord username.
        """

        record = database.fetch_one(
            """
            SELECT *
            FROM members
            WHERE username = ?
            """,
            (
                username,
            ),
        )

        if not record:
            return None

        return dict(record)

    # ------------------------------------------------------------------

    def get_all_members(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all monitored members.
        """

        records = database.fetch_all(
            """
            SELECT *
            FROM members
            ORDER BY id DESC
            """
        )

        return [
            dict(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    def remove_member(
        self,
        user_id: str,
    ) -> None:
        """
        Remove member record.

        Args:
            user_id:
                Discord user ID.
        """

        database.delete(
            "members",
            "user_id = ?",
            (
                user_id,
            ),
        )

        logger.info(
            "Member removed: %s",
            user_id,
        )

    # ------------------------------------------------------------------

    def get_member_statistics(
        self,
        user_id: str,
    ) -> dict[str, int]:
        """
        Return member activity statistics.

        Includes:
        - Total messages
        - Edited messages
        - Deleted messages
        - Alerts
        """

        messages = database.fetch_one(
            """
            SELECT
                COUNT(*) AS total,
                SUM(edited) AS edited,
                SUM(deleted) AS deleted
            FROM messages
            WHERE user_id = ?
            """,
            (
                user_id,
            ),
        )

        alerts = database.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM alerts
            WHERE user_id = ?
            """,
            (
                user_id,
            ),
        )

        return {
            "messages": (
                messages["total"]
                if messages
                else 0
            ),
            "edited_messages": (
                messages["edited"]
                or 0
                if messages
                else 0
            ),
            "deleted_messages": (
                messages["deleted"]
                or 0
                if messages
                else 0
            ),
            "alerts": (
                alerts["total"]
                if alerts
                else 0
            ),
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _get_join_time(
        member: Any,
    ) -> str:
        """
        Extract member join timestamp.
        """

        joined = getattr(
            member,
            "joined_at",
            None,
        )

        if isinstance(
            joined,
            datetime,
        ):
            return joined.isoformat()

        return datetime.now(
            timezone.utc
        ).isoformat()


# ----------------------------------------------------------------------
# Global Member Monitor Instance
# ----------------------------------------------------------------------

member_monitor = MemberMonitor()