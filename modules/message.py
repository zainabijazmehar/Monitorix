"""
Monitorix
Module: modules.message
Author: Zainab

Description:
Discord message monitoring module.

Responsibilities:
- Track message creation
- Track message edits
- Track message deletion
- Store message history
- Provide message search functionality
"""

from __future__ import annotations

from typing import Any

from database.database import database
from services.logger import logger
from utils.helpers import (
    get_utc_timestamp,
    safe_string,
    sanitize_text,
)


class MessageMonitor:
    """
    Discord message monitoring handler.

    Handles message lifecycle events and storage.
    """

    def __init__(self) -> None:
        logger.info(
            "Message monitor initialized"
        )

    # ------------------------------------------------------------------

    def process_message(
        self,
        message: Any,
    ) -> None:
        """
        Store a new Discord message.

        Args:
            message:
                Discord message object.
        """

        if message is None:
            return

        message_id = safe_string(
            getattr(
                message,
                "id",
                None,
            )
        )

        author = getattr(
            message,
            "author",
            None,
        )

        channel = getattr(
            message,
            "channel",
            None,
        )

        user_id = safe_string(
            getattr(
                author,
                "id",
                None,
            )
        )

        channel_id = safe_string(
            getattr(
                channel,
                "id",
                None,
            )
        )

        content = sanitize_text(
            getattr(
                message,
                "content",
                "",
            )
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM messages
            WHERE message_id = ?
            """,
            (
                message_id,
            ),
        )

        if existing:
            return

        database.insert(
            "messages",
            {
                "message_id": message_id,
                "user_id": user_id,
                "channel_id": channel_id,
                "content": content,
                "created_at": get_utc_timestamp(),
                "edited": 0,
                "deleted": 0,
            },
        )

        logger.info(
            "Message stored: %s",
            message_id,
        )

    # ------------------------------------------------------------------

    def process_edit(
        self,
        message: Any,
    ) -> None:
        """
        Track message edit event.

        Args:
            message:
                Edited Discord message.
        """

        if message is None:
            return

        message_id = safe_string(
            getattr(
                message,
                "id",
                None,
            )
        )

        content = sanitize_text(
            getattr(
                message,
                "content",
                "",
            )
        )

        database.update(
            "messages",
            {
                "content": content,
                "edited": 1,
            },
            "message_id = ?",
            (
                message_id,
            ),
        )

        logger.info(
            "Message edited: %s",
            message_id,
        )

    # ------------------------------------------------------------------

    def process_delete(
        self,
        message: Any,
    ) -> None:
        """
        Track message deletion.

        Args:
            message:
                Deleted Discord message.
        """

        if message is None:
            return

        message_id = safe_string(
            getattr(
                message,
                "id",
                None,
            )
        )

        database.update(
            "messages",
            {
                "deleted": 1,
            },
            "message_id = ?",
            (
                message_id,
            ),
        )

        logger.warning(
            "Message deleted: %s",
            message_id,
        )

    # ------------------------------------------------------------------

    def get_message(
        self,
        message_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve message details.

        Args:
            message_id:
                Discord message ID.
        """

        record = database.fetch_one(
            """
            SELECT *
            FROM messages
            WHERE message_id = ?
            """,
            (
                message_id,
            ),
        )

        if not record:
            return None

        return dict(record)

    # ------------------------------------------------------------------

    def get_user_messages(
        self,
        user_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Retrieve user's messages.

        Args:
            user_id:
                Discord user ID.

            limit:
                Maximum results.
        """

        records = database.fetch_all(
            """
            SELECT *
            FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        )

        return [
            dict(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    def search_messages(
        self,
        keyword: str,
    ) -> list[dict[str, Any]]:
        """
        Search messages by keyword.

        Args:
            keyword:
                Search term.
        """

        records = database.fetch_all(
            """
            SELECT *
            FROM messages
            WHERE content LIKE ?
            ORDER BY id DESC
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

    def get_statistics(
        self,
        user_id: str | None = None,
    ) -> dict[str, int]:
        """
        Return message statistics.

        Args:
            user_id:
                Optional user filter.
        """

        if user_id:

            record = database.fetch_one(
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

        else:

            record = database.fetch_one(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(edited) AS edited,
                    SUM(deleted) AS deleted
                FROM messages
                """
            )

        return {
            "total": (
                record["total"]
                if record
                else 0
            ),
            "edited": (
                record["edited"]
                or 0
                if record
                else 0
            ),
            "deleted": (
                record["deleted"]
                or 0
                if record
                else 0
            ),
        }


# ----------------------------------------------------------------------
# Global Message Monitor Instance
# ----------------------------------------------------------------------

message_monitor = MessageMonitor()