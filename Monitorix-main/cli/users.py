"""
Monitorix
Module: cli.users

Description:
Display Discord user activity statistics.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database.database import database
from services.logger import logger


console = Console()


def users_command() -> None:
    """
    Display Discord users activity.
    """

    try:

        users = database.fetch_all(
            """
            SELECT
                members.username,
                members.display_name,
                COUNT(messages.id) AS total_messages
            FROM members
            LEFT JOIN messages
            ON members.user_id = messages.user_id
            GROUP BY members.user_id
            ORDER BY total_messages DESC
            LIMIT 50
            """
        )

        if not users:

            console.print(
                Panel(
                    "No users found.",
                    title="USERS",
                    border_style="yellow",
                )
            )

            return


        table = Table(
            title="MONITORIX USER ACTIVITY",
            border_style="cyan",
        )


        table.add_column(
            "USERNAME",
            style="cyan",
        )

        table.add_column(
            "DISPLAY NAME",
        )

        table.add_column(
            "MESSAGES",
            justify="center",
        )


        for user in users:

            table.add_row(
                str(user["username"]),
                str(user["display_name"] or "-"),
                str(user["total_messages"]),
            )


        console.print()
        console.print(table)
        console.print()


        logger.info(
            "User activity displayed."
        )


    except Exception as error:

        console.print(
            Panel(
                f"[red]Users command failed:[/red]\n\n{error}",
                title="ERROR",
                border_style="red",
            )
        )

        logger.exception(
            "Users command failed: %s",
            error,
        )


__all__ = [
    "users_command",
]
