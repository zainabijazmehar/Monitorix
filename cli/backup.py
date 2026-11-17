"""
Monitorix
Module: cli.backup
Author: Zainab

Description:
Professional CLI backup and restore commands.

Responsibilities:
- Create database backups
- Display backup information
- Restore database backups
- Validate backup paths
- Provide safe restore confirmation
- Keep backup operations independent from monitoring
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from services.backup import backup_manager
from services.logger import logger


# ==============================================================
# CONSOLE
# ==============================================================

console = Console(
    highlight=False,
    soft_wrap=True,
)


# ==============================================================
# BACKUP COMMAND
# ==============================================================

def backup_command() -> None:
    """
    Create a Monitorix database backup.
    """

    console.print()

    console.print(
        "💾 [bold cyan]CREATING MONITORIX BACKUP[/bold cyan]"
    )

    console.print(
        "─" * 72,
        style="dim",
    )

    try:

        backup_file = (
            backup_manager.create_backup()
        )

        path = Path(
            backup_file
        )

        # ------------------------------------------------------
        # Validate generated file
        # ------------------------------------------------------

        if not path.exists():

            console.print(
                Panel(
                    "🔴 Backup operation completed, "
                    "but the backup file could not be found.",
                    title="BACKUP WARNING",
                    border_style="yellow",
                    padding=(1, 3),
                )
            )

            logger.warning(
                "Backup manager returned a missing file: %s",
                path,
            )

            return

        # ------------------------------------------------------
        # File information
        # ------------------------------------------------------

        size_bytes = path.stat().st_size

        if size_bytes >= 1024 * 1024:

            size = (
                f"{size_bytes / (1024 * 1024):.2f} MB"
            )

        else:

            size = (
                f"{size_bytes / 1024:.2f} KB"
            )

        # ------------------------------------------------------
        # Result
        # ------------------------------------------------------

        console.print(
            Panel(
                "🟢 [bold green]"
                "BACKUP COMPLETED"
                "[/bold green]\n\n"
                "Database backup created successfully.\n\n"
                f"📦 File: [cyan]{path}[/cyan]\n"
                f"📏 Size: [white]{size}[/white]\n"
                "🔐 Status: [green]READY[/green]",
                title="💾 MONITORIX BACKUP",
                border_style="green",
                padding=(1, 3),
            )
        )

        logger.info(
            "Backup created successfully | file=%s | size=%s",
            path,
            size,
        )

    except Exception as error:

        console.print(
            Panel(
                "🔴 [bold red]"
                "BACKUP FAILED"
                "[/bold red]\n\n"
                f"{error}",
                title="ERROR",
                border_style="red",
                padding=(1, 3),
            )
        )

        logger.exception(
            "Backup command failed: %s",
            error,
        )


# ==============================================================
# RESTORE COMMAND
# ==============================================================

def restore_command(
    file_path: str,
) -> None:
    """
    Restore a Monitorix database from a backup.

    Args:
        file_path:
            Path to the backup file.
    """

    console.print()

    # ----------------------------------------------------------
    # Validate argument
    # ----------------------------------------------------------

    if not file_path:

        console.print(
            Panel(
                "⚠️ [yellow]Usage:[/yellow] "
                "restore <backup_file>",
                title="RESTORE",
                border_style="yellow",
                padding=(1, 3),
            )
        )

        return

    path = Path(
        file_path
    ).expanduser()

    if not path.exists():

        console.print(
            Panel(
                "🔴 Backup file was not found.\n\n"
                f"📦 Path: {path}",
                title="RESTORE FAILED",
                border_style="red",
                padding=(1, 3),
            )
        )

        logger.warning(
            "Restore requested for missing file: %s",
            path,
        )

        return

    if not path.is_file():

        console.print(
            Panel(
                "🔴 The specified backup path "
                "is not a file.\n\n"
                f"📦 Path: {path}",
                title="RESTORE FAILED",
                border_style="red",
                padding=(1, 3),
            )
        )

        return

    # ----------------------------------------------------------
    # Confirmation
    # ----------------------------------------------------------

    console.print(
        Panel(
            "⚠️ [bold yellow]"
            "DATABASE RESTORE WARNING"
            "[/bold yellow]\n\n"
            "Restoring a backup may replace current "
            "Monitorix database data.\n\n"
            f"📦 Backup: [cyan]{path}[/cyan]",
            title="♻️ RESTORE",
            border_style="yellow",
            padding=(1, 3),
        )
    )

    confirmation = console.input(
        "[bold yellow]"
        "Continue with restore? [y/N]: "
        "[/bold yellow]"
    ).strip().lower()

    if confirmation not in {
        "y",
        "yes",
    }:

        console.print(
            "ℹ️ Restore cancelled.",
            style="cyan",
        )

        logger.info(
            "Restore operation cancelled by user."
        )

        return

    # ----------------------------------------------------------
    # Restore
    # ----------------------------------------------------------

    try:

        result = (
            backup_manager.restore_backup(
                str(path)
            )
        )

        console.print()

        console.print(
            Panel(
                "🟢 [bold green]"
                "RESTORE COMPLETED"
                "[/bold green]\n\n"
                f"📦 Backup: [cyan]{path}[/cyan]\n"
                f"📊 Status: [green]{result}[/green]",
                title="♻️ MONITORIX RESTORE",
                border_style="green",
                padding=(1, 3),
            )
        )

        logger.info(
            "Restore completed successfully | file=%s",
            path,
        )

    except Exception as error:

        console.print(
            Panel(
                "🔴 [bold red]"
                "RESTORE FAILED"
                "[/bold red]\n\n"
                f"{error}",
                title="ERROR",
                border_style="red",
                padding=(1, 3),
            )
        )

        logger.exception(
            "Restore command failed: %s",
            error,
        )


# ==============================================================
# ALIASES
# ==============================================================

show_backup = backup_command


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "backup_command",
    "restore_command",
    "show_backup",
]
