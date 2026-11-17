"""
Monitorix
Module: modules.webhook
Author: Zainab

Description:
Discord webhook monitoring module.

Responsibilities:
- Track webhook creation and deletion
- Store webhook metadata
- Monitor possible webhook abuse
- Provide webhook information for reports
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database.database import database
from services.logger import logger
from utils.helpers import safe_string


class WebhookMonitor:
    """
    Discord webhook monitoring handler.

    Handles webhook lifecycle events and storage.
    """

    def __init__(self) -> None:
        logger.info(
            "Webhook monitor initialized"
        )

    # ------------------------------------------------------------------

    def register_webhook(
        self,
        webhook: Any,
    ) -> None:
        """
        Register Discord webhook.

        Args:
            webhook:
                Discord webhook object.
        """

        if webhook is None:
            return

        self._ensure_table()

        webhook_id = safe_string(
            getattr(
                webhook,
                "id",
                None,
            )
        )

        name = safe_string(
            getattr(
                webhook,
                "name",
                "unknown",
            )
        )

        channel_id = safe_string(
            getattr(
                getattr(
                    webhook,
                    "channel",
                    None,
                ),
                "id",
                None,
            )
        )

        owner_id = safe_string(
            getattr(
                getattr(
                    webhook,
                    "user",
                    None,
                ),
                "id",
                None,
            )
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM webhooks
            WHERE webhook_id = ?
            """,
            (
                webhook_id,
            ),
        )

        if existing:

            database.update(
                "webhooks",
                {
                    "name": name,
                    "channel_id": channel_id,
                    "owner_id": owner_id,
                },
                "webhook_id = ?",
                (
                    webhook_id,
                ),
            )

            return

        database.insert(
            "webhooks",
            {
                "webhook_id": webhook_id,
                "name": name,
                "channel_id": channel_id,
                "owner_id": owner_id,
                "created_at": self._timestamp(),
            },
        )

        logger.warning(
            "Webhook created: %s",
            name,
        )

    # ------------------------------------------------------------------

    def remove_webhook(
        self,
        webhook_id: str,
    ) -> None:
        """
        Remove deleted webhook.

        Args:
            webhook_id:
                Discord webhook ID.
        """

        self._ensure_table()

        database.delete(
            "webhooks",
            "webhook_id = ?",
            (
                webhook_id,
            ),
        )

        logger.warning(
            "Webhook removed: %s",
            webhook_id,
        )

    # ------------------------------------------------------------------

    def get_webhook(
        self,
        webhook_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve webhook information.

        Args:
            webhook_id:
                Discord webhook ID.
        """

        self._ensure_table()

        record = database.fetch_one(
            """
            SELECT *
            FROM webhooks
            WHERE webhook_id = ?
            """,
            (
                webhook_id,
            ),
        )

        if not record:
            return None

        return dict(record)

    # ------------------------------------------------------------------

    def get_all_webhooks(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all monitored webhooks.
        """

        self._ensure_table()

        records = database.fetch_all(
            """
            SELECT *
            FROM webhooks
            ORDER BY id DESC
            """
        )

        return [
            dict(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    def search_webhooks(
        self,
        keyword: str,
    ) -> list[dict[str, Any]]:
        """
        Search webhook names.

        Args:
            keyword:
                Search keyword.
        """

        self._ensure_table()

        records = database.fetch_all(
            """
            SELECT *
            FROM webhooks
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
    def _ensure_table() -> None:
        """
        Ensure webhook table exists.
        """

        database.execute(
            """
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                channel_id TEXT,
                owner_id TEXT,
                created_at TEXT
            )
            """
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _timestamp() -> str:
        """
        Generate UTC timestamp.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()


# ----------------------------------------------------------------------
# Global Webhook Monitor Instance
# ----------------------------------------------------------------------

webhook_monitor = WebhookMonitor()