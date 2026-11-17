"""
Monitorix
Module: cli.alerts
Author: Zainab

Description:
Security alert CLI interface.

Responsibilities:
- Display security alerts
- Filter alerts by user
- Show alert severity
- Show alert timestamps
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database.database import database
from services.logger import logger


console = Console()


# =====================================================
# Alert Command
# =====================================================

def alert_command(user_id: str | None = None) -> None:
    """
    Display recent security alerts.

    Usage:
        alert
        alert <user_id>
    """

    try:

        # -------------------------------------------------
        # Fetch alerts
        # -------------------------------------------------

        if user_id:

            alerts = database.fetch_all(
                """
                SELECT
                    id,
                    alert_type,
                    user_id,
                    message,
                    severity,
                    created_at
                FROM alerts
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 50
                """,
                (user_id,),
            )

        else:

            alerts = database.fetch_all(
                """
                SELECT
                    id,
                    alert_type,
                    user_id,
                    message,
                    severity,
                    created_at
                FROM alerts
                ORDER BY id DESC
                LIMIT 50
                """
            )

        # -------------------------------------------------
        # No alerts
        # -------------------------------------------------

        if not alerts:

            if user_id:
                message = (
                    f"No security alerts found for user "
                    f"{user_id}."
                )
            else:
                message = "No security alerts found."

            console.print(
                Panel(
                    message,
                    title="🚨 SECURITY ALERTS",
                    border_style="yellow",
                )
            )

            return

        # -------------------------------------------------
        # Alert Summary
        # -------------------------------------------------

        critical = 0
        warning = 0
        info = 0

        for alert in alerts:

            severity = str(
                alert["severity"] or "INFO"
            ).upper()

            if severity == "CRITICAL":
                critical += 1

            elif severity == "WARNING":
                warning += 1

            else:
                info += 1

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        filter_text = (
            f"USER: {user_id}"
            if user_id
            else "ALL USERS"
        )

        console.print()

        console.print(
            Panel(
                (
                    "[bold]SECURITY ALERT MONITOR[/bold]\n\n"
                    f"[red]CRITICAL[/red] : {critical}    "
                    f"[yellow]WARNING[/yellow] : {warning}    "
                    f"[cyan]INFO[/cyan] : {info}\n\n"
                    f"[dim]FILTER: {filter_text}[/dim]"
                ),
                title="🚨 MONITORIX ALERTS",
                border_style="red",
            )
        )

        # -------------------------------------------------
        # Alert Table
        # -------------------------------------------------

        table = Table(
            title="Recent Security Alerts",
            border_style="red",
            show_lines=False,
        )

        table.add_column(
            "ID",
            justify="center",
            style="dim",
            no_wrap=True,
        )

        table.add_column(
            "TYPE",
            style="bold",
            no_wrap=True,
        )

        table.add_column(
            "USER",
            style="cyan",
            no_wrap=True,
        )

        table.add_column(
            "MESSAGE",
            max_width=40,
        )

        table.add_column(
            "SEVERITY",
            justify="center",
            no_wrap=True,
        )

        table.add_column(
            "TIME",
            style="dim",
            no_wrap=True,
        )

        # -------------------------------------------------
        # Populate table
        # -------------------------------------------------

        for alert in alerts:

            severity = str(
                alert["severity"] or "INFO"
            ).upper()

            if severity == "CRITICAL":
                severity_display = (
                    "[bold red]CRITICAL[/bold red]"
                )

            elif severity == "WARNING":
                severity_display = (
                    "[bold yellow]WARNING[/bold yellow]"
                )

            else:
                severity_display = (
                    "[cyan]INFO[/cyan]"
                )

            alert_type = str(
                alert["alert_type"] or "UNKNOWN"
            )

            message = str(
                alert["message"] or ""
            )

            if len(message) > 40:
                message = message[:37] + "..."

            user = str(
                alert["user_id"] or "SYSTEM"
            )

            created_at = str(
                alert["created_at"] or ""
            )

            table.add_row(
                str(alert["id"]),
                alert_type,
                user,
                message,
                severity_display,
                created_at,
            )

        console.print(table)

        console.print()

        logger.info(
            "Alert history displayed"
        )

    except Exception as error:

        console.print(
            Panel(
                f"[red]Alert command failed:[/red]\n\n{error}",
                title="ERROR",
                border_style="red",
            )
        )

        logger.exception(
            "Alert command failed: %s",
            error,
        )


# =====================================================
# Alias
# =====================================================

show_alerts = alert_command