"""
Monitorix
Module: cli.channels

Description:
Display Discord channel activity statistics.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database.database import database
from services.logger import logger


console = Console()


def channels_command() -> None:
    """
    Display Discord channel activity.
    """

    try:

        channels = database.fetch_all(
            """
            SELECT
                channels.name,
                channels.channel_type,
                COUNT(messages.id) AS total_messages
            FROM channels
            LEFT JOIN messages
            ON channels.channel_id = messages.channel_id
            GROUP BY channels.channel_id
            ORDER BY total_messages DESC
            LIMIT 50
            """
        )

        if not channels:

            console.print(
                Panel(
                    "No channels found.",
                    title="CHANNELS",
                    border_style="yellow",
                )
            )
            return


        table = Table(
            title="MONITORIX CHANNEL ACTIVITY",
            border_style="cyan",
        )

        table.add_column("CHANNEL")
        table.add_column("TYPE")
        table.add_column("MESSAGES")


        for channel in channels:

            table.add_row(
                str(channel["name"]),
                str(channel["channel_type"] or "-"),
                str(channel["total_messages"]),
            )


        console.print(table)

        logger.info(
            "Channel activity displayed."
        )


    except Exception as error:

        console.print(
            Panel(
                f"[red]Channels failed:[/red]\n{error}",
                title="ERROR",
                border_style="red",
            )
        )

        logger.exception(
            "Channels command failed: %s",
            error,
        )


__all__ = [
    "channels_command",
]
