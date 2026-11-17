"""
Monitorix
Module: modules.channel
Author: Zainab

Description:
Discord channel monitoring module.

Responsibilities:
- Track channel creation and deletion
- Store channel metadata
- Provide channel information
- Support CLI and reporting systems
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database.database import database
from services.logger import logger
from utils.helpers import get_utc_timestamp, safe_string


class ChannelMonitor:
    """
    Discord channel monitoring handler.

    Handles channel lifecycle events and storage.
    """

    def __init__(self) -> None:
        logger.info(
            "Channel monitor initialized"
        )

    # ------------------------------------------------------------------

    def register_channel(
        self,
        channel: Any,
    ) -> None:
        """
        Register or update Discord channel.

        Args:
            channel:
                Discord channel object.
        """

        if channel is None:
            return

        channel_id = safe_string(
            getattr(
                channel,
                "id",
                None,
            )
        )

        name = safe_string(
            getattr(
                channel,
                "name",
                "unknown",
            )
        )

        channel_type = safe_string(
            getattr(
                getattr(
                    channel,
                    "type",
                    None,
                ),
                "name",
                "unknown",
            )
        )

        created_at = self._get_created_time(
            channel
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM channels
            WHERE channel_id = ?
            """,
            (
                channel_id,
            ),
        )

        if existing:

            return

        database.insert(
            "channels",
            {
                "channel_id": channel_id,
                "name": name,
                "channel_type": channel_type,
                "created_at": created_at,
            },
        )

        logger.info(
            "Channel registered: %s",
            name,
        )

    # ------------------------------------------------------------------

    def update_channel_name(
        self,
        channel_id: str,
        name: str,
    ) -> None:
        """
        Update channel name.

        Args:
            channel_id:
                Discord channel ID.

            name:
                New channel name.
        """

        database.update(
            "channels",
            {
                "name": name,
            },
            "channel_id = ?",
            (
                channel_id,
            ),
        )

        logger.info(
            "Channel updated: %s",
            channel_id,
        )

    # ------------------------------------------------------------------

    def get_channel(
        self,
        channel_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve channel information.

        Args:
            channel_id:
                Discord channel ID.
        """

        record = database.fetch_one(
            """
            SELECT *
            FROM channels
            WHERE channel_id = ?
            """,
            (
                channel_id,
            ),
        )

        if not record:
            return None

        return dict(record)

    # ------------------------------------------------------------------

    def get_all_channels(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all monitored channels.
        """

        records = database.fetch_all(
            """
            SELECT *
            FROM channels
            ORDER BY id DESC
            """
        )

        return [
            dict(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    def remove_channel(
        self,
        channel_id: str,
    ) -> None:
        """
        Remove deleted channel.

        Args:
            channel_id:
                Discord channel ID.
        """

        database.delete(
            "channels",
            "channel_id = ?",
            (
                channel_id,
            ),
        )

        logger.info(
            "Channel removed: %s",
            channel_id,
        )

    # ------------------------------------------------------------------

    def search_channels(
        self,
        keyword: str,
    ) -> list[dict[str, Any]]:
        """
        Search channels by name.

        Args:
            keyword:
                Search keyword.

        Returns:
            Matching channels.
        """

        records = database.fetch_all(
            """
            SELECT *
            FROM channels
            WHERE name LIKE ?
            ORDER BY name
            """,
            (
                f"%{keyword}%",
            ),
        )

        return [
            dict(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    @staticmethod
    def _get_created_time(
        channel: Any,
    ) -> str:
        """
        Extract channel creation timestamp.
        """

        created = getattr(
            channel,
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
# Global Channel Monitor Instance
# ----------------------------------------------------------------------

channel_monitor = ChannelMonitor()