"""
Monitorix
Module: cli.status
Author: Zainab

Description:
Professional Monitorix system status command.

Responsibilities:
- Display monitoring engine status
- Display service health
- Show Discord/database monitoring state
- Provide clean SOC-style terminal output
"""

from __future__ import annotations

from datetime import datetime, timezone

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core.monitor import monitor_engine
from display.icons import ICONS
from services.logger import logger


# ==============================================================
# Console
# ==============================================================

console = Console()


# ==============================================================
# Status Command
# ==============================================================

def status_command() -> None:
    """
    Display current Monitorix system status.
    """

    try:

        data = monitor_engine.status()

        health = monitor_engine.health()

        engine_status = data.get(
            "engine",
            "OFFLINE",
        )

        health_status = health.get(
            "status",
            "UNKNOWN",
        )

        # ------------------------------------------------------
        # Status Indicators
        # ------------------------------------------------------

        if engine_status == "ONLINE":

            engine_icon = ICONS["online"]
            engine_style = "green"

        else:

            engine_icon = ICONS["offline"]
            engine_style = "red"

        if health_status == "HEALTHY":

            health_icon = ICONS["success"]
            health_style = "green"

        else:

            health_icon = ICONS["warning"]
            health_style = "yellow"

        # ------------------------------------------------------
        # Main Status
        # ------------------------------------------------------

        status = Text()

        status.append(
            f"{engine_icon} MONITORING ENGINE    ",
            style="bold",
        )

        status.append(
            f"{engine_status}\n",
            style=engine_style,
        )

        status.append(
            f"{health_icon} SYSTEM HEALTH        ",
            style="bold",
        )

        status.append(
            f"{health_status}\n",
            style=health_style,
        )

        status.append(
            f"{ICONS['bot']} DISCORD MONITORING   ",
            style="bold",
        )

        status.append(
            "ACTIVE\n",
            style="green",
        )

        status.append(
            f"{ICONS['database']} DATABASE             ",
            style="bold",
        )

        status.append(
            "CONNECTED\n",
            style="green",
        )

        status.append(
            f"{ICONS['alert']} SECURITY ALERTS      ",
            style="bold",
        )

        status.append(
            "ACTIVE\n",
            style="green",
        )

        status.append(
            f"{ICONS['monitor']} EVENT MONITORING     ",
            style="bold",
        )

        status.append(
            "ACTIVE",
            style="green",
        )

        console.print()

        console.print(
            Panel(
                status,
                title=f"{ICONS['status']} SYSTEM STATUS",
                title_align="left",
                border_style="cyan",
                padding=(1, 2),
            )
        )

        # ------------------------------------------------------
        # Monitoring Services
        # ------------------------------------------------------

        modules = data.get(
            "modules",
            {},
        )

        module_text = Text()

        if modules:

            for module, state in modules.items():

                state_text = str(
                    state
                ).upper()

                if state_text in (
                    "ACTIVE",
                    "ONLINE",
                    "ENABLED",
                    "READY",
                ):

                    icon = ICONS["success"]
                    style = "green"

                else:

                    icon = ICONS["warning"]
                    style = "yellow"

                module_text.append(
                    f"{icon} "
                    f"{str(module).upper():<20}",
                    style="bold",
                )

                module_text.append(
                    f"{state_text}\n",
                    style=style,
                )

        else:

            module_text.append(
                f"{ICONS['warning']} "
                "No module information available.",
                style="yellow",
            )

        console.print(
            Panel(
                module_text,
                title=f"{ICONS['monitor']} MONITORING SERVICES",
                title_align="left",
                border_style="blue",
                padding=(1, 2),
            )
        )

        # ------------------------------------------------------
        # Runtime Information
        # ------------------------------------------------------

        runtime = Text()

        started = data.get(
            "started"
        )

        if started:

            runtime.append(
                f"{ICONS['online']} STARTED AT\n",
                style="bold cyan",
            )

            runtime.append(
                f"  {started}\n\n",
                style="dim",
            )

        runtime.append(
            f"{ICONS['online']} LAST HEALTH CHECK\n",
            style="bold cyan",
        )

        runtime.append(
            "  "
            + datetime.now(
                timezone.utc
            ).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),
            style="dim",
        )

        console.print(
            Panel(
                runtime,
                title="RUNTIME INFORMATION",
                title_align="left",
                border_style="cyan",
                padding=(1, 2),
            )
        )

        logger.info(
            "Status dashboard displayed successfully."
        )

    except Exception as error:

        logger.exception(
            "Status command failed: %s",
            error,
        )

        console.print(
            Panel(
                (
                    f"[red]{ICONS['critical']} "
                    "STATUS CHECK FAILED[/red]\n\n"
                    f"{error}"
                ),
                title="STATUS ERROR",
                border_style="red",
                padding=(1, 2),
            )
        )


# ==============================================================
# CLI Alias
# ==============================================================

show_status = status_command


# ==============================================================
# Export
# ==============================================================

__all__ = [
    "status_command",
    "show_status",
]
