"""
Monitorix
Module: services.backup
Author: Zainab

Description:
Production-ready SQLite backup and restore service.

Responsibilities:
- Create database backups
- Restore database backups safely
- List available backups
- Delete backups
- Validate backup files
- Maintain backup service logging
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from config.settings import settings
from services.logger import logger


# ==============================================================
# BACKUP MANAGER
# ==============================================================

class BackupManager:
    """
    Monitorix database backup manager.
    """

    def __init__(self) -> None:

        self.backup_dir = Path(
            getattr(
                settings,
                "BACKUP_DIR",
                "backups",
            )
        )

        self.backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            "Backup service initialized."
        )

    # ==========================================================
    # CREATE BACKUP
    # ==========================================================

    def create_backup(self) -> Path:
        """
        Create a copy of the Monitorix SQLite database.

        Returns:
            Path to the created backup.

        Raises:
            FileNotFoundError:
                If the database does not exist.
            OSError:
                If the backup cannot be created.
        """

        database_path = Path(
            settings.DATABASE_PATH
        )

        if not database_path.exists():

            raise FileNotFoundError(
                f"Monitorix database not found: "
                f"{database_path}"
            )

        if not database_path.is_file():

            raise OSError(
                f"Database path is not a file: "
                f"{database_path}"
            )

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        backup_file = (
            self.backup_dir
            / f"monitorix_backup_{timestamp}.db"
        )

        try:

            shutil.copy2(
                database_path,
                backup_file,
            )

            logger.info(
                "Database backup created: %s",
                backup_file,
            )

            return backup_file

        except OSError as error:

            logger.exception(
                "Database backup failed: %s",
                error,
            )

            raise

    # ==========================================================
    # RESTORE BACKUP
    # ==========================================================

    def restore_backup(
        self,
        backup_file: Path | str,
    ) -> str:
        """
        Restore a Monitorix database from a backup.

        Args:
            backup_file:
                Path to the backup database.

        Returns:
            Success message.

        Raises:
            FileNotFoundError:
                If the backup does not exist.
            ValueError:
                If the supplied path is invalid.
            OSError:
                If restoration fails.
        """

        backup_path = Path(
            backup_file
        ).expanduser()

        if not backup_path.exists():

            raise FileNotFoundError(
                f"Backup file does not exist: "
                f"{backup_path}"
            )

        if not backup_path.is_file():

            raise ValueError(
                f"Backup path is not a file: "
                f"{backup_path}"
            )

        if backup_path.suffix.lower() != ".db":

            raise ValueError(
                "Invalid backup format. "
                "Monitorix requires a .db backup."
            )

        database_path = Path(
            settings.DATABASE_PATH
        )

        database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            shutil.copy2(
                backup_path,
                database_path,
            )

            logger.warning(
                "Database restored from backup: %s",
                backup_path,
            )

            return (
                "Database restored successfully"
            )

        except OSError as error:

            logger.exception(
                "Database restore failed: %s",
                error,
            )

            raise

    # ==========================================================
    # LIST BACKUPS
    # ==========================================================

    def list_backups(self) -> list[Path]:
        """
        Return available Monitorix database backups.

        Returns:
            Backups sorted newest first.
        """

        try:

            backups = sorted(
                (
                    path
                    for path in self.backup_dir.glob(
                        "monitorix_backup_*.db"
                    )
                    if path.is_file()
                ),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )

            logger.info(
                "Backup list requested | count=%s",
                len(backups),
            )

            return backups

        except OSError as error:

            logger.exception(
                "Unable to list backups: %s",
                error,
            )

            return []

    # ==========================================================
    # DELETE BACKUP
    # ==========================================================

    def delete_backup(
        self,
        backup_file: Path | str,
    ) -> bool:
        """
        Delete a specific backup file.

        Returns:
            True if deleted, False if not found.
        """

        backup_path = Path(
            backup_file
        ).expanduser()

        if not backup_path.exists():

            logger.warning(
                "Backup deletion requested for "
                "missing file: %s",
                backup_path,
            )

            return False

        if not backup_path.is_file():

            logger.warning(
                "Backup deletion rejected; "
                "path is not a file: %s",
                backup_path,
            )

            return False

        try:

            backup_path.unlink()

            logger.info(
                "Backup deleted: %s",
                backup_path,
            )

            return True

        except OSError as error:

            logger.exception(
                "Backup deletion failed: %s",
                error,
            )

            raise


# ==============================================================
# GLOBAL INSTANCE
# ==============================================================

backup_manager = BackupManager()


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "BackupManager",
    "backup_manager",
]
