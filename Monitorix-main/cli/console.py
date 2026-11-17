"""
Monitorix
Module: cli.console
Author: Zainab

Description:
Professional SOC-style terminal interface for Monitorix.

Responsibilities:
- Display Monitorix branding
- Display system dashboard
- Provide clean terminal presentation
- Use Kali/Linux/Windows compatible icons
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from display.icons import ICONS
from services.logger import logger


# ==============================================================
# Console
# ==============================================================

console = Console()


# ==============================================================
# Banner
# ==============================================================

def show_banner() -> None:
    """
    Display the main Monitorix branding banner.
    """

    console.print()

    banner = Text()

    banner.append(
        f"{ICONS['logo']} MONITORIX\n",
        style="bold cyan",
    )

    banner.append(
        "DISCORD SECURITY MONITORING PLATFORM\n",
        style="bold white",
    )

    banner.append(
        "REAL-TIME AUDIT & THREAT DETECTION SYSTEM",
        style="dim",
    )

    console.print(
        Panel(
            banner,
            border_style="cyan",
            padding=(1, 4),
        )
    )

    logger.info(
        "Monitorix banner displayed."
    )


# ==============================================================
# System Status
# ==============================================================

def show_dashboard() -> None:
    """
    Display the clean Monitorix startup dashboard.

    The dashboard intentionally avoids large tables.
    Detailed information is available through CLI commands.
    """

    console.print()

    # ----------------------------------------------------------
    # SYSTEM STATUS
    # ----------------------------------------------------------

    status_text = Text()

    status_text.append(
        f"{ICONS['online']} SYSTEM ONLINE\n\n",
        style="bold green",
    )

    status_text.append(
        "All monitoring services are operational.\n",
        style="white",
    )

    status_text.append(
        "Discord event monitoring is ready.",
        style="dim",
    )

    console.print(
        Panel(
            status_text,
            title="SYSTEM STATUS",
            title_align="left",
            border_style="green",
            padding=(1, 2),
        )
    )

    # ----------------------------------------------------------
    # MONITORING
    # ----------------------------------------------------------

    monitoring = Text()

    monitoring.append(
        f"{ICONS['success']} DISCORD MONITORING       ACTIVE\n",
        style="white",
    )

    monitoring.append(
        f"{ICONS['success']} MESSAGE AUDIT            ENABLED\n",
        style="white",
    )

    monitoring.append(
        f"{ICONS['success']} EDITED MESSAGE TRACKING  ENABLED\n",
        style="white",
    )

    monitoring.append(
        f"{ICONS['success']} DELETED MESSAGE TRACKING ENABLED\n",
        style="white",
    )

    monitoring.append(
        f"{ICONS['success']} MEMBER MONITORING        ACTIVE\n",
        style="white",
    )

    monitoring.append(
        f"{ICONS['alert']} SECURITY ALERTS          READY\n",
        style="white",
    )

    monitoring.append(
        f"{ICONS['report']} REPORT ENGINE            READY\n",
        style="white",
    )

    console.print(
        Panel(
            monitoring,
            title="MONITORING SERVICES",
            title_align="left",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    # ----------------------------------------------------------
    # COMMAND HINT
    # ----------------------------------------------------------

    command_hint = Text()

    command_hint.append(
        f"{ICONS['help']} ",
        style="bold cyan",
    )

    command_hint.append(
        "TYPE ",
        style="dim",
    )

    command_hint.append(
        "HELP",
        style="bold white",
    )

    command_hint.append(
        " TO VIEW AVAILABLE COMMANDS",
        style="dim",
    )

    console.print(
        command_hint
    )

    console.print()

    logger.info(
        "SOC dashboard displayed."
    )


# ==============================================================
# Prompt
# ==============================================================

def get_prompt() -> str:
    """
    Return the Monitorix command prompt.
    """

    return (
        f"[bold cyan]"
        f"{ICONS['logo']} MONITORIX>"
        f"[/bold cyan] "
    )


# ==============================================================
# Simple Message Helpers
# ==============================================================

def show_success(message: str) -> None:
    """
    Display a successful operation message.
    """

    console.print(
        f"[green]"
        f"{ICONS['success']} "
        f"{message}"
        f"[/green]"
    )


def show_warning(message: str) -> None:
    """
    Display a warning message.
    """

    console.print(
        f"[yellow]"
        f"{ICONS['warning']} "
        f"{message}"
        f"[/yellow]"
    )


def show_error(message: str) -> None:
    """
    Display an error message.
    """

    console.print(
        f"[red]"
        f"{ICONS['critical']} "
        f"{message}"
        f"[/red]"
    )


def show_info(message: str) -> None:
    """
    Display an informational message.
    """

    console.print(
        f"[cyan]"
        f"{ICONS['info']} "
        f"{message}"
        f"[/cyan]"
    )


# ==============================================================
# Export
# ==============================================================

__all__ = [
    "console",
    "show_banner",
    "show_dashboard",
    "get_prompt",
    "show_success",
    "show_warning",
    "show_error",
    "show_info",
]
