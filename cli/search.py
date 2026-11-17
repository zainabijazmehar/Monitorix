"""
Monitorix
Module: cli.search
Author: Zainab

Description:
Professional security audit search command.

Responsibilities:
- Search message content
- Search security event details
- Search event types
- Display matching audit records
- Provide result statistics
- Handle empty and invalid searches safely
"""

from __future__ import annotations

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

SEARCH_LIMIT = 50
MAX_TEXT_LENGTH = 60


# ==============================================================
# FORMAT TEXT
# ==============================================================

def _format_text(
    value: object,
    max_length: int = MAX_TEXT_LENGTH,
) -> str:
    """
    Format text safely for terminal output.
    """

    if value is None:
        return "-"

    text = str(value).replace(
        "\n",
        " ",
    )

    if len(text) > max_length:
        return text[: max_length - 3] + "..."

    return text


# ==============================================================
# SEARCH COMMAND
# ==============================================================

def search_command(
    keyword: str,
) -> None:
    """
    Search Monitorix messages and security events.

    Searches:
    - Message content
    - Event details
    - Event type
    """

    keyword = (
        keyword or ""
    ).strip()

    # ----------------------------------------------------------
    # Validate keyword
    # ----------------------------------------------------------

    if not keyword:

        console.print(
            Panel(
                "🔎 [yellow]Usage:[/yellow] "
                "search <keyword>",
                title="SEARCH",
                border_style="yellow",
                padding=(1, 3),
            )
        )

        return

    try:

        # ------------------------------------------------------
        # Search messages
        # ------------------------------------------------------

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
            WHERE content LIKE ? COLLATE NOCASE
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                f"%{keyword}%",
                SEARCH_LIMIT,
            ),
        )

        # ------------------------------------------------------
        # Search events
        # ------------------------------------------------------

        events = database.fetch_all(
            """
            SELECT
                id,
                event_type,
                user_id,
                target_id,
                details,
                created_at
            FROM events
            WHERE
                details LIKE ?
                OR event_type LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                f"%{keyword}%",
                f"%{keyword}%",
                SEARCH_LIMIT,
            ),
        )

        # ------------------------------------------------------
        # No results
        # ------------------------------------------------------

        if not messages and not events:

            console.print()

            console.print(
                Panel(
                    f"🔎 No audit records found for "
                    f"[bold white]'{keyword}'[/bold white].",
                    title="SEARCH RESULTS",
                    border_style="yellow",
                    padding=(1, 3),
                )
            )

            logger.info(
                "Search completed with no results | keyword=%s",
                keyword,
            )

            return

        # ------------------------------------------------------
        # Search Header
        # ------------------------------------------------------

        console.print()

        console.print(
            "🔎 [bold cyan]SECURITY AUDIT SEARCH[/bold cyan]"
        )

        console.print(
            f"Keyword: [bold white]{keyword}[/bold white]"
        )

        console.print(
            "─" * 100,
            style="dim",
        )

        # ------------------------------------------------------
        # Message Results
        # ------------------------------------------------------

        if messages:

            console.print()

            console.print(
                f"💬 [bold cyan]MESSAGE RESULTS[/bold cyan] "
                f"[dim]({len(messages)})[/dim]"
            )

            table = Table(
                border_style="cyan",
                header_style="bold cyan",
                expand=True,
            )

            table.add_column(
                "USER",
                style="white",
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

            for row in messages:

                if row["deleted"]:

                    status = (
                        "[bold red]🔴 DELETED[/bold red]"
                    )

                elif row["edited"]:

                    status = (
                        "[bold yellow]🟡 EDITED[/bold yellow]"
                    )

                else:

                    status = (
                        "[bold green]🟢 ACTIVE[/bold green]"
                    )

                table.add_row(
                    str(row["user_id"]),
                    f"#{row['channel_id']}",
                    _format_text(
                        row["content"]
                    ),
                    str(row["created_at"]),
                    status,
                )

            console.print(table)

        # ------------------------------------------------------
        # Event Results
        # ------------------------------------------------------

        if events:

            console.print()

            console.print(
                f"🚨 [bold magenta]SECURITY EVENT RESULTS[/bold magenta] "
                f"[dim]({len(events)})[/dim]"
            )

            table = Table(
                border_style="magenta",
                header_style="bold magenta",
                expand=True,
            )

            table.add_column(
                "EVENT",
                style="bold yellow",
                no_wrap=True,
            )

            table.add_column(
                "USER",
                style="cyan",
                no_wrap=True,
            )

            table.add_column(
                "TARGET",
                style="white",
                no_wrap=True,
            )

            table.add_column(
                "DETAILS",
                ratio=3,
            )

            table.add_column(
                "TIME",
                style="dim",
                no_wrap=True,
            )

            for row in events:

                table.add_row(
                    _format_text(
                        row["event_type"],
                        30,
                    ),
                    str(
                        row["user_id"]
                        or "-"
                    ),
                    str(
                        row["target_id"]
                        or "-"
                    ),
                    _format_text(
                        row["details"]
                    ),
                    str(row["created_at"]),
                )

            console.print(table)

        # ------------------------------------------------------
        # Summary
        # ------------------------------------------------------

        console.print()

        total = (
            len(messages)
            + len(events)
        )

        console.print(
            "📊 "
            f"Messages: [cyan]{len(messages)}[/cyan]   "
            f"Events: [magenta]{len(events)}[/magenta]   "
            f"Total: [bold white]{total}[/bold white]"
        )

        console.print()

        logger.info(
            "Search executed | keyword=%s | "
            "messages=%s | events=%s",
            keyword,
            len(messages),
            len(events),
        )

    except Exception as error:

        console.print()

        console.print(
            Panel(
                f"🔴 [bold red]SEARCH FAILED[/bold red]\n\n"
                f"{error}",
                title="ERROR",
                border_style="red",
                padding=(1, 3),
            )
        )

        logger.exception(
            "Search command failed: %s",
            error,
        )


# ==============================================================
# ALIAS
# ==============================================================

show_search = search_command


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "search_command",
    "show_search",
]
