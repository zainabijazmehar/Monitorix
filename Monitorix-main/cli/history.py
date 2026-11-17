"""
Monitorix
Module: cli.history
Author: Zainab

Description:
Professional Discord message audit history command.

Responsibilities:
- Display message history
- Filter history by member
- Resolve Discord users safely
- Resolve Discord channels safely
- Show edited/deleted message state
- Preserve deleted message content
- Provide clean SOC-style audit output
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database.database import database
from services.logger import logger


# ==============================================================
# CONSOLE
# ==============================================================

console = Console(
    highlight=False,
    soft_wrap=True,
)


# ==============================================================
# CONFIGURATION
# ==============================================================

DEFAULT_LIMIT = 50
MAX_MESSAGE_LENGTH = 55


# ==============================================================
# RESOLVE DISCORD USER
# ==============================================================

async def resolve_user(
    bot: Any,
    user_id: str,
) -> str:
    """
    Resolve a Discord user.

    Resolution order:
    1. Bot cache
    2. Discord API

    Returns a safe fallback when the user cannot be resolved.
    """

    if not user_id:
        return "Unknown User"

    try:
        user = bot.get_user(
            int(user_id)
        )

        if user is not None:
            return (
                getattr(
                    user,
                    "display_name",
                    None,
                )
                or getattr(
                    user,
                    "name",
                    None,
                )
                or f"User ({user_id})"
            )

        user = await bot.fetch_user(
            int(user_id)
        )

        return (
            getattr(
                user,
                "display_name",
                None,
            )
            or getattr(
                user,
                "name",
                None,
            )
            or f"User ({user_id})"
        )

    except Exception as error:

        logger.warning(
            "User resolution failed [%s]: %s",
            user_id,
            error,
        )

        return f"Unknown User ({user_id})"


# ==============================================================
# RESOLVE DISCORD CHANNEL
# ==============================================================

async def resolve_channel(
    bot: Any,
    channel_id: str | None,
) -> str:
    """
    Resolve a Discord channel.

    Resolution order:
    1. Bot cache
    2. Discord API

    Returns a safe fallback when unavailable.
    """

    if not channel_id:
        return "Unknown Channel"

    try:
        channel = bot.get_channel(
            int(channel_id)
        )

        if channel is not None:

            name = getattr(
                channel,
                "name",
                None,
            )

            if name:
                return f"#{name}"

        channel = await bot.fetch_channel(
            int(channel_id)
        )

        name = getattr(
            channel,
            "name",
            None,
        )

        if name:
            return f"#{name}"

        return f"Channel ({channel_id})"

    except Exception as error:

        logger.warning(
            "Channel resolution failed [%s]: %s",
            channel_id,
            error,
        )

        return (
            f"Unknown Channel ({channel_id})"
        )


# ==============================================================
# FORMAT MESSAGE
# ==============================================================

def format_message(
    content: str | None,
) -> str:
    """
    Format message content for terminal display.
    """

    if not content:
        return "[No content]"

    content = str(content).replace(
        "\n",
        " ",
    )

    if len(content) > MAX_MESSAGE_LENGTH:
        return (
            content[: MAX_MESSAGE_LENGTH - 3]
            + "..."
        )

    return content


# ==============================================================
# MESSAGE STATUS
# ==============================================================

def get_message_status(
    message: Any,
) -> tuple[str, str]:
    """
    Return display label and Rich style
    for message audit state.
    """

    if message["deleted"]:
        return (
            "🔴 DELETED",
            "bold red",
        )

    if message["edited"]:
        return (
            "🟡 EDITED",
            "bold yellow",
        )

    return (
        "🟢 ACTIVE",
        "bold green",
    )


# ==============================================================
# HISTORY COMMAND
# ==============================================================

async def history_command(
    bot: Any,
    user_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> None:
    """
    Display Discord message audit history.

    Args:
        bot:
            Active Discord bot instance.

        user_id:
            Optional Discord user ID.

        limit:
            Number of records to display.
    """

    try:

        # ------------------------------------------------------
        # Validate limit
        # ------------------------------------------------------

        limit = max(
            1,
            min(
                int(limit),
                500,
            ),
        )

        # ------------------------------------------------------
        # Query
        # ------------------------------------------------------

        if user_id:

            messages = database.fetch_all(
                """
                SELECT
                    id,
                    message_id,
                    user_id,
                    channel_id,
                    content,
                    created_at,
                    edited,
                    deleted
                FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    str(user_id),
                    limit,
                ),
            )

        else:

            messages = database.fetch_all(
                """
                SELECT
                    id,
                    message_id,
                    user_id,
                    channel_id,
                    content,
                    created_at,
                    edited,
                    deleted
                FROM messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    limit,
                ),
            )

        # ------------------------------------------------------
        # Empty result
        # ------------------------------------------------------

        if not messages:

            title = (
                "📜 USER MESSAGE HISTORY"
                if user_id
                else "📜 MESSAGE AUDIT HISTORY"
            )

            console.print(
                Panel(
                    "No message history found.",
                    title=title,
                    border_style="yellow",
                    padding=(1, 3),
                )
            )

            return

        # ------------------------------------------------------
        # Header
        # ------------------------------------------------------

        console.print()

        if user_id:

            console.print(
                "📜 [bold cyan]USER MESSAGE HISTORY[/bold cyan]"
            )

            console.print(
                f"👤 User ID: [cyan]{user_id}[/cyan]"
            )

        else:

            console.print(
                "📜 [bold cyan]MESSAGE AUDIT HISTORY[/bold cyan]"
            )

        console.print(
            "─" * 110,
            style="dim",
        )

        # ------------------------------------------------------
        # Table
        # ------------------------------------------------------

        table = Table(
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
            expand=True,
            row_styles=[
                "none",
                "dim",
            ],
        )

        table.add_column(
            "USER",
            style="bold white",
            no_wrap=True,
        )

        table.add_column(
            "CHANNEL",
            style="cyan",
            no_wrap=True,
        )

        table.add_column(
            "MESSAGE",
            ratio=3,
        )

        table.add_column(
            "TIME",
            style="dim",
            no_wrap=True,
        )

        table.add_column(
            "STATUS",
            no_wrap=True,
        )

        # ------------------------------------------------------
        # Rows
        # ------------------------------------------------------

        for message in messages:

            username = await resolve_user(
                bot,
                str(message["user_id"]),
            )

            channel = await resolve_channel(
                bot,
                message["channel_id"],
            )

            content = format_message(
                message["content"]
            )

            status, status_style = (
                get_message_status(message)
            )

            table.add_row(
                username,
                channel,
                content,
                str(message["created_at"]),
                f"[{status_style}]{status}[/{status_style}]",
            )

        console.print(table)

        # ------------------------------------------------------
        # Summary
        # ------------------------------------------------------

        total = len(messages)

        deleted = sum(
            1
            for message in messages
            if message["deleted"]
        )

        edited = sum(
            1
            for message in messages
            if message["edited"]
            and not message["deleted"]
        )

        active = total - deleted - edited

        console.print()

        console.print(
            f"📊 Records: [bold white]{total}[/bold white]  "
            f"🟢 Active: [green]{active}[/green]  "
            f"🟡 Edited: [yellow]{edited}[/yellow]  "
            f"🔴 Deleted: [red]{deleted}[/red]"
        )

        console.print()

        logger.info(
            "Message history displayed | user=%s | records=%s",
            user_id or "ALL",
            total,
        )

    except Exception as error:

        console.print()

        console.print(
            Panel(
                f"🔴 [bold red]HISTORY ERROR[/bold red]\n\n"
                f"{error}",
                border_style="red",
                padding=(1, 3),
            )
        )

        logger.exception(
            "History command failed: %s",
            error,
        )


# ==============================================================
# ALIAS
# ==============================================================

show_history = history_command


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "history_command",
    "show_history",
    "resolve_user",
    "resolve_channel",
]