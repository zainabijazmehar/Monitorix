"""
Monitorix
Module: modules.role
Author: Zainab

Description:
Discord role monitoring module.

Responsibilities:
- Track role creation and deletion
- Store role metadata
- Provide role information
- Support security monitoring and reporting
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database.database import database
from services.logger import logger
from utils.helpers import safe_string


class RoleMonitor:
    """
    Discord role monitoring handler.

    Handles role lifecycle events and storage.
    """

    def __init__(self) -> None:
        logger.info(
            "Role monitor initialized"
        )

    # ------------------------------------------------------------------

    def register_role(
        self,
        role: Any,
    ) -> None:
        """
        Register Discord role.

        Args:
            role:
                Discord role object.
        """

        if role is None:
            return

        role_id = safe_string(
            getattr(
                role,
                "id",
                None,
            )
        )

        name = safe_string(
            getattr(
                role,
                "name",
                "unknown",
            )
        )

        guild_id = safe_string(
            getattr(
                getattr(
                    role,
                    "guild",
                    None,
                ),
                "id",
                None,
            )
        )

        created_at = self._get_created_time(
            role
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM roles
            WHERE role_id = ?
            """,
            (
                role_id,
            ),
        )

        if existing:

            database.update(
                "roles",
                {
                    "name": name,
                },
                "role_id = ?",
                (
                    role_id,
                ),
            )

            return

        self._ensure_table()

        database.insert(
            "roles",
            {
                "role_id": role_id,
                "guild_id": guild_id,
                "name": name,
                "created_at": created_at,
            },
        )

        logger.info(
            "Role registered: %s",
            name,
        )

    # ------------------------------------------------------------------

    def remove_role(
        self,
        role_id: str,
    ) -> None:
        """
        Remove deleted role.

        Args:
            role_id:
                Discord role ID.
        """

        self._ensure_table()

        database.delete(
            "roles",
            "role_id = ?",
            (
                role_id,
            ),
        )

        logger.info(
            "Role removed: %s",
            role_id,
        )

    # ------------------------------------------------------------------

    def get_role(
        self,
        role_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve role information.
        """

        self._ensure_table()

        record = database.fetch_one(
            """
            SELECT *
            FROM roles
            WHERE role_id = ?
            """,
            (
                role_id,
            ),
        )

        if not record:
            return None

        return dict(record)

    # ------------------------------------------------------------------

    def get_server_roles(
        self,
        guild_id: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieve roles of a server.

        Args:
            guild_id:
                Discord server ID.
        """

        self._ensure_table()

        records = database.fetch_all(
            """
            SELECT *
            FROM roles
            WHERE guild_id = ?
            ORDER BY name
            """,
            (
                guild_id,
            ),
        )

        return [
            dict(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    def search_roles(
        self,
        keyword: str,
    ) -> list[dict[str, Any]]:
        """
        Search roles by name.

        Args:
            keyword:
                Search keyword.
        """

        self._ensure_table()

        records = database.fetch_all(
            """
            SELECT *
            FROM roles
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
        role: Any,
    ) -> str:
        """
        Extract role creation time.
        """

        created = getattr(
            role,
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

    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_table() -> None:
        """
        Ensure roles table exists.

        Required because role support is
        separated from initial database design.
        """

        database.execute(
            """
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id TEXT UNIQUE NOT NULL,
                guild_id TEXT,
                name TEXT NOT NULL,
                created_at TEXT
            )
            """
        )


# ----------------------------------------------------------------------
# Global Role Monitor Instance
# ----------------------------------------------------------------------

role_monitor = RoleMonitor()