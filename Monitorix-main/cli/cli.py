"""
Monitorix
Module: cli.cli
Author: Zainab

Description:
Professional CLI application controller for Monitorix.

Responsibilities:
- Start Monitorix terminal interface
- Handle CLI commands
- Manage command lifecycle
- Provide clean SOC-style interaction
- Support Kali Linux and Windows terminals
"""

from __future__ import annotations

import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.alerts import alert_command
from cli.console import show_banner, show_dashboard
from cli.status import status_command
from cli.history import history_command
from cli.search import search_command
from cli.reports import reports_command
from cli.backup import backup_command, restore_command
from cli.users import users_command
from cli.channels import channels_command
from cli.messages import messages_command
from display.icons import ICONS
from services.logger import logger


# ==============================================================
# Console
# ==============================================================

console = Console()


# ==============================================================
# CLI Application
# ==============================================================

class CLIApplication:
    """
    Main Monitorix CLI controller.
    """

    def __init__(self, bot=None) -> None:
        """
        Initialize CLI application.

        Args:
            bot:
                Discord.py bot instance.
        """

        self.running: bool = False
        self.bot = bot

        logger.info(
            "Monitorix CLI application initialized."
        )

    # ==========================================================
    # Discord Bot
    # ==========================================================

    def set_bot(self, bot) -> None:
        """
        Attach Discord bot instance to CLI.
        """

        self.bot = bot

        logger.info(
            "Discord bot attached to CLI."
        )

    # ==========================================================
    # Start CLI
    # ==========================================================

    async def start(self) -> None:
        """
        Start Monitorix interactive CLI.
        """

        if self.running:
            return

        self.running = True

        logger.info(
            "Starting Monitorix CLI."
        )

        try:

            # --------------------------------------------------
            # Initial Interface
            # --------------------------------------------------

            show_banner()
            show_dashboard()

            console.print()

            console.print(
                Panel(
                    (
                        f"{ICONS['success']} Monitorix console ready.\n"
                        f"{ICONS['help']} Type 'help' to view commands."
                    ),
                    border_style="cyan",
                    padding=(0, 2),
                )
            )

            # --------------------------------------------------
            # Command Loop
            # --------------------------------------------------

            while self.running:

                try:

                    command = await asyncio.to_thread(
                        input,
                        f"{ICONS['logo']} MONITORIX> ",
                    )

                    command = command.strip()

                    if not command:
                        continue

                    await self.handle_command(command)

                except KeyboardInterrupt:

                    console.print()

                    self.shutdown()

                except EOFError:

                    console.print()

                    self.shutdown()

                except Exception as error:

                    logger.exception(
                        "CLI command loop error: %s",
                        error,
                    )

                    console.print(
                        Panel(
                            (
                                f"[red]{ICONS['critical']} "
                                "Unexpected CLI error[/red]\n\n"
                                f"{error}"
                            ),
                            title="CLI ERROR",
                            border_style="red",
                        )
                    )

        finally:

            self.running = False

            logger.info(
                "Monitorix CLI stopped."
            )

    # ==========================================================
    # Command Handler
    # ==========================================================

    async def handle_command(
        self,
        command: str,
    ) -> None:
        """
        Process a single CLI command.
        """

        command_lower = command.lower().strip()

        # ------------------------------------------------------
        # HELP
        # ------------------------------------------------------

        if command_lower == "help":

            self.show_help()

        # ------------------------------------------------------
        # STATUS
        # ------------------------------------------------------

        elif command_lower == "status":

            status_command()

       # ------------------------------------------------------
       # USERS
       # ------------------------------------------------------
  
        elif command_lower == "users":

           users_command()


       # ------------------------------------------------------
       # CHANNELS
       # ------------------------------------------------------

        elif command_lower == "channels":
  
           channels_command()


       # ------------------------------------------------------
       # MESSAGES
       # ------------------------------------------------------

        elif command_lower == "messages":

           messages_command()

        # ------------------------------------------------------
        # HISTORY
        # ------------------------------------------------------

        elif command_lower == "history":

            if self.bot is None:

                self.show_bot_error()

                return

            await history_command(
                self.bot
            )

        elif command_lower.startswith("history "):

            if self.bot is None:

                self.show_bot_error()

                return

            user_id = command.split(
                maxsplit=1
            )[1].strip()

            if not user_id:

                await history_command(
                    self.bot
                )

                return

            await history_command(
                self.bot,
                user_id,
            )

        # ------------------------------------------------------
        # SEARCH
        # ------------------------------------------------------

        elif command_lower == "search":

            console.print(
                Panel(
                    (
                        f"{ICONS['search']} "
                        "[yellow]Usage:[/yellow] "
                        "search <keyword>"
                    ),
                    title="SEARCH",
                    border_style="yellow",
                )
            )

        elif command_lower.startswith("search "):

            keyword = command.split(
                maxsplit=1
            )[1].strip()

            if keyword:

                search_command(
                    keyword
                )

            else:

                console.print(
                    Panel(
                        (
                            f"{ICONS['search']} "
                            "[yellow]Usage:[/yellow] "
                            "search <keyword>"
                        ),
                        title="SEARCH",
                        border_style="yellow",
                    )
                )

        # ------------------------------------------------------
        # ALERTS
        # ------------------------------------------------------

        elif command_lower == "alert":

            alert_command()

        elif command_lower.startswith("alert "):

            user_id = command.split(
                maxsplit=1
            )[1].strip()

            if user_id:

                alert_command(
                    user_id
                )

            else:

                alert_command()

        # ------------------------------------------------------
        # REPORT
        # ------------------------------------------------------

        elif command_lower in (
            "report",
            "reports",
        ):

            self.run_reports()

        # ------------------------------------------------------
        # BACKUP
        # ------------------------------------------------------

        elif command_lower == "backup":

            backup_command()

        # ------------------------------------------------------
        # RESTORE
        # ------------------------------------------------------

        elif command_lower == "restore":

            console.print(
                Panel(
                    (
                        f"{ICONS['restore']} "
                        "[yellow]Usage:[/yellow] "
                        "restore <backup_file>"
                    ),
                    title="RESTORE",
                    border_style="yellow",
                )
            )

        elif command_lower.startswith("restore "):

            file_path = command.split(
                maxsplit=1
            )[1].strip()

            if file_path:

                restore_command(
                    file_path
                )

            else:

                console.print(
                    Panel(
                        (
                            f"{ICONS['restore']} "
                            "[yellow]Usage:[/yellow] "
                            "restore <backup_file>"
                        ),
                        title="RESTORE",
                        border_style="yellow",
                    )
                )

        # ------------------------------------------------------
        # CLEAR
        # ------------------------------------------------------

        elif command_lower == "clear":

            console.clear()

            show_banner()

            console.print(
                f"{ICONS['success']} "
                "[green]Screen cleared.[/green]"
            )

        # ------------------------------------------------------
        # EXIT
        # ------------------------------------------------------

        elif command_lower in (
            "exit",
            "quit",
        ):

            self.shutdown()

        # ------------------------------------------------------
        # UNKNOWN COMMAND
        # ------------------------------------------------------

        else:

            console.print(
                Panel(
                    (
                        f"{ICONS['warning']} "
                        f"[yellow]Unknown command:[/yellow] "
                        f"{command}\n\n"
                        f"Type [bold]help[/bold] to view "
                        f"available commands."
                    ),
                    title="UNKNOWN COMMAND",
                    border_style="yellow",
                )
            )

    # ==========================================================
    # Help
    # ==========================================================

    def show_help(self) -> None:
        """
        Display available Monitorix commands.
        """

        table = Table(
            title=(
                f"{ICONS['logo']} MONITORIX COMMANDS"
            ),
            border_style="cyan",
            show_lines=False,
        )

        table.add_column(
            "COMMAND",
            style="bold cyan",
            no_wrap=True,
        )

        table.add_column(
            "DESCRIPTION",
            style="white",
        )

        commands = [

            (
                "status",
                "Show system and monitoring status",
            ),

            (
                "history",
                "Show recent message audit history",
            ),

            (
                "history <user_id>",
                "Show activity for a specific member",
            ),

            (
                "search <keyword>",
                "Search messages and security events",
            ),

            (
                "alert",
                "Show recent security alerts",
            ),

            (
                "alert <user_id>",
                "Show security alerts for a member",
            ),

            (
               "users",
               "Show Discord user activity",
            ),

            (
               "channels",
               "Show Discord channel activity",
            ),

            (
               "messages",
               "Show recent monitored messages",
            ),

            (
                "report",
                "Generate monitoring reports",
            ),

            (
                "backup",
                "Create a database backup",
            ),

            (
                "restore <file>",
                "Restore a database backup",
            ),

            (
                "clear",
                "Clear the terminal screen",
            ),

            (
                "help",
                "Show available commands",
            ),

            (
                "exit",
                "Shutdown Monitorix",
            ),
        ]

        for command_name, description in commands:

            table.add_row(
                f"{ICONS['command']} {command_name}",
                description,
            )

        console.print()

        console.print(table)

        console.print()

        logger.info(
            "Help menu displayed."
        )

    # ==========================================================
    # Reports
    # ==========================================================

    def run_reports(self) -> None:
        """
        Generate and display Monitorix reports.
        """

        try:

            reports = (
                reports_command.generate_all()
            )

            panels = (
                reports_command.display(
                    reports
                )
            )

            console.print()

            for panel in panels:

                console.print(panel)

            logger.info(
                "Reports generated from CLI."
            )

        except Exception as error:

            logger.exception(
                "Report generation failed: %s",
                error,
            )

            console.print(
                Panel(
                    (
                        f"[red]{ICONS['critical']} "
                        "Report generation failed[/red]\n\n"
                        f"{error}"
                    ),
                    title="REPORT ERROR",
                    border_style="red",
                )
            )

    # ==========================================================
    # Bot Error
    # ==========================================================

    @staticmethod
    def show_bot_error() -> None:
        """
        Display Discord connection error.
        """

        console.print(
            Panel(
                (
                    f"[red]{ICONS['critical']} "
                    "Discord bot is not connected.[/red]\n\n"
                    "History requires an active Discord "
                    "bot connection."
                ),
                title="DISCORD CONNECTION",
                border_style="red",
            )
        )

    # ==========================================================
    # Shutdown
    # ==========================================================

    def shutdown(self) -> None:
        """
        Shutdown Monitorix CLI.
        """

        if not self.running:
            return

        console.print()

        console.print(
            Panel(
                (
                    f"{ICONS['success']} "
                    "[green]MONITORIX SHUTDOWN[/green]\n\n"
                    "Monitoring console stopped safely."
                ),
                border_style="green",
                padding=(1, 2),
            )
        )

        self.running = False

        logger.info(
            "Monitorix CLI shutdown completed."
        )


# ==============================================================
# Export
# ==============================================================

__all__ = [
    "CLIApplication",
]
