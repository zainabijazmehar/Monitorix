"""
Monitorix
Module: database.database
Author: Zainab

Description:
Central SQLite database management layer for Monitorix.

Responsibilities:
- Create and manage SQLite database connection
- Initialize and maintain database schema
- Store Discord servers, members, channels and messages
- Store message edits/deletions and security events
- Store roles and permission information
- Store webhooks and security alerts
- Store security incidents and risk information
- Execute queries safely
- Handle transactions
- Provide reusable database operations
- Support multi-server/guild data isolation

Database:
SQLite
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any, Iterable

from config.settings import settings
from services.logger import logger


class DatabaseManager:
    """
    Production-ready SQLite database manager for Monitorix.

    The database layer is intentionally independent from Discord.py.
    Higher-level services should use this class for persistence.
    """

    ALLOWED_TABLES = {
        "servers",
        "members",
        "channels",
        "messages",
        "events",
        "alerts",
        "roles",
        "webhooks",
        "incidents",
    }

    def __init__(
        self,
        database_path: Path | None = None,
    ) -> None:
        configured_path = (
            database_path
            if database_path is not None
            else settings.DATABASE_PATH
        )

        self.database_path = Path(configured_path)

        self._lock = Lock()
        self.connection: sqlite3.Connection | None = None

        self.initialize()

    # ------------------------------------------------------------------
    # CONNECTION
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Initialize the SQLite database connection and schema.
        """

        try:
            self.database_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.connection = sqlite3.connect(
                str(self.database_path),
                check_same_thread=False,
                timeout=30,
            )

            self.connection.row_factory = sqlite3.Row

            self._configure_sqlite()
            self.create_tables()
            self.create_indexes()

            logger.info(
                "Database initialized successfully: %s",
                self.database_path,
            )

        except sqlite3.Error as error:
            logger.exception(
                "Database initialization failed: %s",
                error,
            )

            if self.connection is not None:
                self.connection.close()

            self.connection = None
            raise

    # ------------------------------------------------------------------

    def _configure_sqlite(self) -> None:
        """
        Apply SQLite runtime configuration.
        """

        if self.connection is None:
            raise RuntimeError(
                "Database connection is not initialized"
            )

        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        self.connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        self.connection.execute(
            "PRAGMA synchronous = NORMAL"
        )

        self.connection.execute(
            "PRAGMA busy_timeout = 30000"
        )

        self.connection.commit()

    # ------------------------------------------------------------------
    # SCHEMA
    # ------------------------------------------------------------------

    def create_tables(self) -> None:
        """
        Create the complete Monitorix database schema.
        """

        queries = (

            # ----------------------------------------------------------
            # SERVERS
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                server_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,

                owner_id TEXT,

                created_at TEXT,
                updated_at TEXT
            )
            """,

            # ----------------------------------------------------------
            # MEMBERS
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',
                user_id TEXT NOT NULL,

                username TEXT NOT NULL,
                display_name TEXT,

                status TEXT DEFAULT 'unknown',

                joined_at TEXT,
                last_activity TEXT,

                created_at TEXT,
                updated_at TEXT,

                UNIQUE (guild_id, user_id),

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE
            )
            """,

            # ----------------------------------------------------------
            # CHANNELS
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',
                channel_id TEXT NOT NULL,

                name TEXT NOT NULL,
                channel_type TEXT,

                created_at TEXT,
                updated_at TEXT,

                UNIQUE (guild_id, channel_id),

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE
            )
            """,

            # ----------------------------------------------------------
            # MESSAGES
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',
                message_id TEXT NOT NULL,

                user_id TEXT NOT NULL,
                channel_id TEXT,

                content TEXT,

                created_at TEXT,
                edited_at TEXT,
                deleted_at TEXT,

                edited INTEGER NOT NULL DEFAULT 0,
                deleted INTEGER NOT NULL DEFAULT 0,

                edit_count INTEGER NOT NULL DEFAULT 0,

                UNIQUE (guild_id, message_id),

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE
            )
            """,

            # ----------------------------------------------------------
            # EVENTS
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',

                event_type TEXT NOT NULL,

                user_id TEXT,
                target_id TEXT,
                channel_id TEXT,

                details TEXT,

                severity TEXT DEFAULT 'INFO',

                risk_score INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL,

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE
            )
            """,

            # ----------------------------------------------------------
            # ALERTS
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',

                alert_type TEXT NOT NULL,

                user_id TEXT,
                channel_id TEXT,
                target_id TEXT,

                message TEXT,

                severity TEXT NOT NULL DEFAULT 'INFO',

                risk_score INTEGER NOT NULL DEFAULT 0,

                status TEXT NOT NULL DEFAULT 'OPEN',

                created_at TEXT NOT NULL,
                acknowledged_at TEXT,
                resolved_at TEXT,

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE
            )
            """,

            # ----------------------------------------------------------
            # ROLES
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',
                role_id TEXT NOT NULL,

                name TEXT NOT NULL,

                permissions TEXT,

                position INTEGER DEFAULT 0,

                managed INTEGER NOT NULL DEFAULT 0,

                created_at TEXT,
                updated_at TEXT,

                UNIQUE (guild_id, role_id),

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE
            )
            """,

            # ----------------------------------------------------------
            # WEBHOOKS
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',
                webhook_id TEXT NOT NULL,

                name TEXT,
                channel_id TEXT,

                creator_id TEXT,

                status TEXT DEFAULT 'ACTIVE',

                created_at TEXT,
                updated_at TEXT,

                UNIQUE (guild_id, webhook_id),

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE
            )
            """,

            # ----------------------------------------------------------
            # SECURITY INCIDENTS
            # ----------------------------------------------------------

            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id TEXT NOT NULL DEFAULT 'global',

                incident_id TEXT NOT NULL UNIQUE,

                title TEXT NOT NULL,
                description TEXT,

                severity TEXT NOT NULL DEFAULT 'INFO',

                risk_score INTEGER NOT NULL DEFAULT 0,

                status TEXT NOT NULL DEFAULT 'OPEN',

                source_event_id INTEGER,

                created_at TEXT NOT NULL,
                acknowledged_at TEXT,
                resolved_at TEXT,

                FOREIGN KEY (guild_id)
                    REFERENCES servers(server_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (source_event_id)
                    REFERENCES events(id)
                    ON DELETE SET NULL
            )
            """,
        )

        with self._lock:
            self._require_connection()

            try:
                cursor = self.connection.cursor()

                for query in queries:
                    cursor.execute(query)

                self.connection.commit()

                logger.info(
                    "Monitorix database schema initialized"
                )

            except sqlite3.Error as error:
                self.connection.rollback()

                logger.exception(
                    "Database schema creation failed: %s",
                    error,
                )

                raise

    # ------------------------------------------------------------------
    # INDEXES
    # ------------------------------------------------------------------

    def create_indexes(self) -> None:
        """
        Create indexes used by history, search, alerts and statistics.
        """

        indexes = (

            """
            CREATE INDEX IF NOT EXISTS
            idx_members_guild
            ON members(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_members_user
            ON members(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_members_activity
            ON members(last_activity)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_channels_guild
            ON channels(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_guild
            ON messages(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_user
            ON messages(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_channel
            ON messages(channel_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_created
            ON messages(created_at)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_deleted
            ON messages(deleted)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_edited
            ON messages(edited)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_events_guild
            ON events(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_events_type
            ON events(event_type)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_events_user
            ON events(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_events_severity
            ON events(severity)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_events_created
            ON events(created_at)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_alerts_guild
            ON alerts(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_alerts_severity
            ON alerts(severity)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_alerts_status
            ON alerts(status)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_alerts_user
            ON alerts(user_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_alerts_created
            ON alerts(created_at)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_roles_guild
            ON roles(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_webhooks_guild
            ON webhooks(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_incidents_guild
            ON incidents(guild_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_incidents_status
            ON incidents(status)
            """,

            """
            CREATE INDEX IF NOT EXISTS
            idx_incidents_severity
            ON incidents(severity)
            """,
        )

        with self._lock:
            self._require_connection()

            try:
                cursor = self.connection.cursor()

                for query in indexes:
                    cursor.execute(query)

                self.connection.commit()

                logger.info(
                    "Monitorix database indexes initialized"
                )

            except sqlite3.Error as error:
                self.connection.rollback()

                logger.exception(
                    "Database index creation failed: %s",
                    error,
                )

                raise

    # ------------------------------------------------------------------
    # QUERY HELPERS
    # ------------------------------------------------------------------

    def execute(
        self,
        query: str,
        parameters: Iterable[Any] = (),
    ) -> sqlite3.Cursor:
        """
        Execute a SQL statement safely.

        Returns:
            sqlite3.Cursor
        """

        with self._lock:
            self._require_connection()

            try:
                cursor = self.connection.cursor()

                cursor.execute(
                    query,
                    tuple(parameters),
                )

                self.connection.commit()

                return cursor

            except sqlite3.Error as error:
                self.connection.rollback()

                logger.exception(
                    "Database query failed: %s",
                    error,
                )

                raise

    # ------------------------------------------------------------------

    def fetch_one(
        self,
        query: str,
        parameters: Iterable[Any] = (),
    ) -> sqlite3.Row | None:
        """
        Execute a SELECT query and return one row.
        """

        cursor = self.execute(
            query,
            parameters,
        )

        return cursor.fetchone()

    # ------------------------------------------------------------------

    def fetch_all(
        self,
        query: str,
        parameters: Iterable[Any] = (),
    ) -> list[sqlite3.Row]:
        """
        Execute a SELECT query and return all rows.
        """

        cursor = self.execute(
            query,
            parameters,
        )

        return cursor.fetchall()

    # ------------------------------------------------------------------

    def insert(
        self,
        table: str,
        data: dict[str, Any],
    ) -> int:
        """
        Insert one record into an approved Monitorix table.

        Returns:
            Inserted row ID.
        """

        self._validate_table(table)

        if not data:
            raise ValueError(
                "Insert data cannot be empty"
            )

        columns = ", ".join(
            data.keys()
        )

        placeholders = ", ".join(
            "?" for _ in data
        )

        query = (
            f"INSERT INTO {table} "
            f"({columns}) "
            f"VALUES ({placeholders})"
        )

        cursor = self.execute(
            query,
            data.values(),
        )

        return int(cursor.lastrowid)

    # ------------------------------------------------------------------

    def update(
        self,
        table: str,
        data: dict[str, Any],
        condition: str,
        parameters: Iterable[Any],
    ) -> None:
        """
        Update records in an approved Monitorix table.
        """

        self._validate_table(table)

        if not data:
            raise ValueError(
                "Update data cannot be empty"
            )

        values = ", ".join(
            f"{key}=?"
            for key in data
        )

        query = (
            f"UPDATE {table} "
            f"SET {values} "
            f"WHERE {condition}"
        )

        self.execute(
            query,
            (
                *data.values(),
                *parameters,
            ),
        )

    # ------------------------------------------------------------------

    def delete(
        self,
        table: str,
        condition: str,
        parameters: Iterable[Any],
    ) -> None:
        """
        Delete records from an approved Monitorix table.
        """

        self._validate_table(table)

        query = (
            f"DELETE FROM {table} "
            f"WHERE {condition}"
        )

        self.execute(
            query,
            parameters,
        )

    # ------------------------------------------------------------------
    # TRANSACTIONS
    # ------------------------------------------------------------------

    def transaction(
        self,
    ):
        """
        Provide a database transaction context.

        Usage:

            with database.transaction():
                ...
        """

        return _DatabaseTransaction(self)

    # ------------------------------------------------------------------
    # DATABASE INFORMATION
    # ------------------------------------------------------------------

    def table_exists(
        self,
        table: str,
    ) -> bool:
        """
        Check whether a table exists.
        """

        self._validate_table(table)

        row = self.fetch_one(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name=?
            """,
            (table,),
        )

        return row is not None

    # ------------------------------------------------------------------

    def count(
        self,
        table: str,
        condition: str | None = None,
        parameters: Iterable[Any] = (),
    ) -> int:
        """
        Return the number of records in a table.

        Optional condition can be used for filtered statistics.
        """

        self._validate_table(table)

        query = f"SELECT COUNT(*) AS total FROM {table}"

        if condition:
            query += f" WHERE {condition}"

        row = self.fetch_one(
            query,
            parameters,
        )

        return int(row["total"]) if row else 0

    # ------------------------------------------------------------------

    def get_database_size(self) -> int:
        """
        Return database file size in bytes.
        """

        try:
            if self.database_path.exists():
                return self.database_path.stat().st_size

        except OSError as error:
            logger.warning(
                "Unable to determine database size: %s",
                error,
            )

        return 0

    # ------------------------------------------------------------------

    def vacuum(self) -> None:
        """
        Optimize the SQLite database.

        VACUUM requires no active transaction.
        """

        with self._lock:
            self._require_connection()

            try:
                self.connection.execute(
                    "VACUUM"
                )

                logger.info(
                    "Database vacuum completed"
                )

            except sqlite3.Error as error:
                logger.exception(
                    "Database vacuum failed: %s",
                    error,
                )

                raise

    # ------------------------------------------------------------------
    # CONNECTION MANAGEMENT
    # ------------------------------------------------------------------

    def close(self) -> None:
        """
        Close the SQLite database connection safely.
        """

        with self._lock:
            if self.connection is not None:

                try:
                    self.connection.commit()
                    self.connection.close()

                finally:
                    self.connection = None

                logger.info(
                    "Database connection closed"
                )

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------

    def _require_connection(self) -> None:
        """
        Ensure the database connection is available.
        """

        if self.connection is None:
            raise RuntimeError(
                "Database connection is not initialized"
            )

    # ------------------------------------------------------------------

    def _validate_table(
        self,
        table: str,
    ) -> None:
        """
        Prevent unsafe dynamic table names.

        Only Monitorix-owned tables are allowed.
        """

        if table not in self.ALLOWED_TABLES:
            raise ValueError(
                f"Unsupported database table: {table}"
            )


class _DatabaseTransaction:
    """
    Internal transaction context manager.
    """

    def __init__(
        self,
        database: DatabaseManager,
    ) -> None:
        self.database = database

    def __enter__(self):
        self.database._lock.acquire()
        self.database._require_connection()

        self.database.connection.execute(
            "BEGIN"
        )

        return self.database.connection

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:

        try:
            if exc_type is None:
                self.database.connection.commit()

            else:
                self.database.connection.rollback()

        finally:
            self.database._lock.release()

        return False


# ----------------------------------------------------------------------
# GLOBAL DATABASE INSTANCE
# ----------------------------------------------------------------------

database = DatabaseManager()
