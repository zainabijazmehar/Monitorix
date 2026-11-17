"""
Monitorix
Module: modules.server
Author: Zainab

Description:
Discord server monitoring module.

Responsibilities:
- Track Discord server information
- Store server metadata
- Handle server related events
- Provide server information for CLI and reports
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database.database import database
from services.logger import logger
from utils.helpers import get_utc_timestamp, safe_string


class ServerMonitor:
    """
    Discord server monitoring handler.

    Manages guild/server related operations.
    """

    def __init__(self) -> None:
        logger.info(
            "Server monitor initialized"
        )

    # ------------------------------------------------------------------

    def register_server(
        self,
        guild: Any,
    ) -> None:
        """
        Store or update Discord server information.

        Args:
            guild:
                Discord guild object.
        """

        if guild is None:
            return

        server_id = safe_string(
            getattr(
                guild,
                "id",
                None,
            )
        )

        name = safe_string(
            getattr(
                guild,
                "name",
                "Unknown",
            )
        )

        owner_id = safe_string(
            getattr(
                guild,
                "owner_id",
                None,
            )
        )

        created_at = self._get_created_time(
            guild
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM servers
            WHERE server_id = ?
            """,
            (
                server_id,
            ),
        )

        if existing:

            database.update(
                "servers",
                {
                    "name": name,
                    "owner_id": owner_id,
                    "updated_at": get_utc_timestamp(),
                },
                "server_id = ?",
                (
                    server_id,
                ),
            )

        else:

            database.insert(
                "servers",
                {
                    "server_id": server_id,
                    "name": name,
                    "owner_id": owner_id,
                    "created_at": created_at,
                    "updated_at": get_utc_timestamp(),
                },
            )

        logger.info(
            "Server registered: %s",
            name,
        )

    # ------------------------------------------------------------------

    def get_server(
        self,
        server_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve server information.

        Args:
            server_id:
                Discord server ID.

        Returns:
            Server data dictionary.
        """

        record = database.fetch_one(
            """
            SELECT *
            FROM servers
            WHERE server_id = ?
            """,
            (
                server_id,
            ),
        )

        if not record:
            return None

        return dict(record)

    # ------------------------------------------------------------------

    def get_all_servers(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all monitored servers.
        """

        records = database.fetch_all(
            """
            SELECT *
            FROM servers
            ORDER BY id DESC
            """
        )

        return [
            dict(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    def remove_server(
        self,
        server_id: str,
    ) -> None:
        """
        Remove server from database.

        Args:
            server_id:
                Discord server ID.
        """

        database.delete(
            "servers",
            "server_id = ?",
            (
                server_id,
            ),
        )

        logger.info(
            "Server removed: %s",
            server_id,
        )

    # ------------------------------------------------------------------

    def get_server_statistics(
        self,
        server_id: str,
    ) -> dict[str, int]:
        """
        Return monitoring statistics.

        Includes:
        - Messages
        - Members
        - Alerts
        """

        message_count = database.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM messages
            WHERE channel_id IN (
                SELECT channel_id
                FROM channels
            )
            """
        )

        member_count = database.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM members
            """
        )

        alert_count = database.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM alerts
            """
        )

        return {
            "messages": (
                message_count["total"]
                if message_count
                else 0
            ),
            "members": (
                member_count["total"]
                if member_count
                else 0
            ),
            "alerts": (
                alert_count["total"]
                if alert_count
                else 0
            ),
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _get_created_time(
        guild: Any,
    ) -> str:
        """
        Extract server creation time.
        """

        created = getattr(
            guild,
            "created_at",
            None,
        )

        if isinstance(
            created,
            datetime,
        ):
            return created.isoformat()

        return datetime.now(
            timezone.utc
        ).isoformat()


# ----------------------------------------------------------------------
# Global Server Monitor Instance
# ----------------------------------------------------------------------

server_monitor = ServerMonitor()