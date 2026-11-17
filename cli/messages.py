"""
Monitorix
Module: cli.messages

Description:
Display message statistics.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database.database import database
from services.logger import logger


console = Console()


def messages_command() -> None:
    """
    Display recent monitored messages.
    """

    try:

        messages = database.fetch_all(
            """
            SELECT
                user_id,
                channel_id,
                content,
                created_at,
                edited,
                deleted
            FROM messages
            ORDER BY id DESC
            LIMIT 50
            """
        )


        if not messages:

            console.print(
                Panel(
                    "No messages found.",
                    title="MESSAGES",
                    border_style="yellow",
                )
            )

            return


        table = Table(
            title="MONITORIX MESSAGE AUDIT",
            border_style="cyan",
        )

        table.add_column("USER")
        table.add_column("CHANNEL")
        table.add_column("MESSAGE")
        table.add_column("STATUS")


        for msg in messages:

            if msg["deleted"]:
                status = "DELETED"

            elif msg["edited"]:
                status = "EDITED"

            else:
                status = "ACTIVE"


            content = str(
                msg["content"] or "-"
            )

            if len(content) > 40:
                content = content[:37] + "..."


            table.add_row(
                str(msg["user_id"]),
                str(msg["channel_id"]),
                content,
                status,
            )


        console.print(table)

        logger.info(
            "Messages displayed."
        )


    except Exception as error:

        console.print(
            Panel(
                f"[red]Messages failed:[/red]\n{error}",
                title="ERROR",
                border_style="red",
            )
        )

        logger.exception(
            "Messages command failed: %s",
            error,
        )


__all__ = [
    "messages_command",
]
