"""
Monitorix
Module: cli.reports
Author: Zainab

Description:
Professional CLI interface for Monitorix security reports.

Responsibilities:
- Generate TXT security reports
- Generate HTML security reports
- Display report generation status
- Handle report failures safely
- Keep reporting independent from core monitoring
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from services.logger import logger
from services.reports import report_generator


# ==============================================================
# CONSOLE
# ==============================================================

console = Console(
    highlight=False,
    soft_wrap=True,
)


# ==============================================================
# REPORT COMMAND
# ==============================================================

class ReportsCommand:
    """
    CLI command handler for Monitorix reports.
    """

    def __init__(self) -> None:
        logger.info(
            "CLI reports module initialized."
        )

    # ==========================================================
    # Generate Reports
    # ==========================================================

    def generate_all(
        self,
    ) -> dict[str, Any]:
        """
        Generate all supported reports.

        Reporting is intentionally isolated from the core
        monitoring engine. A report failure must not stop
        Monitorix monitoring.

        Returns:
            Dictionary containing successful report paths.
        """

        results: dict[str, Any] = {
            "txt": None,
            "html": None,
            "errors": [],
        }

        if report_generator is None:

            message = (
                "Report generator is not available."
            )

            logger.error(message)

            results["errors"].append(
                message
            )

            return results

        logger.info(
            "Starting Monitorix report generation."
        )

        # ------------------------------------------------------
        # TXT Report
        # ------------------------------------------------------

        try:

            txt_report = (
                report_generator.generate_txt_report()
            )

            results["txt"] = txt_report

            logger.info(
                "TXT report generated successfully: %s",
                txt_report,
            )

        except Exception as error:

            message = (
                f"TXT report generation failed: {error}"
            )

            results["errors"].append(
                message
            )

            logger.exception(
                "TXT report generation failed."
            )

        # ------------------------------------------------------
        # HTML Report
        # ------------------------------------------------------

        try:

            html_report = (
                report_generator.generate_html_report()
            )

            results["html"] = html_report

            logger.info(
                "HTML report generated successfully: %s",
                html_report,
            )

        except Exception as error:

            message = (
                f"HTML report generation failed: {error}"
            )

            results["errors"].append(
                message
            )

            logger.exception(
                "HTML report generation failed."
            )

        logger.info(
            "Monitorix report generation completed."
        )

        return results

    # ==========================================================
    # Display Reports
    # ==========================================================

    def display(
        self,
        reports: dict[str, Any],
    ) -> list[Panel]:
        """
        Build clean Rich panels for generated reports.

        Args:
            reports:
                Result dictionary returned by generate_all().

        Returns:
            List of Rich panels.
        """

        panels: list[Panel] = []

        txt_report = reports.get(
            "txt"
        )

        html_report = reports.get(
            "html"
        )

        errors = reports.get(
            "errors",
            [],
        )

        # ------------------------------------------------------
        # Successful Reports
        # ------------------------------------------------------

        generated: list[str] = []

        if txt_report:

            path = Path(
                txt_report
            )

            if path.exists():

                generated.append(
                    f"📄 TXT REPORT    [green]READY[/green]\n"
                    f"   {path}"
                )

        if html_report:

            path = Path(
                html_report
            )

            if path.exists():

                generated.append(
                    f"🌐 HTML REPORT   [green]READY[/green]\n"
                    f"   {path}"
                )

        # ------------------------------------------------------
        # Success Panel
        # ------------------------------------------------------

        if generated:

            content = (
                "🟢 [bold green]"
                "SECURITY REPORTS GENERATED"
                "[/bold green]\n\n"
                + "\n\n".join(generated)
            )

            panels.append(
                Panel(
                    content,
                    title="📊 MONITORIX REPORTS",
                    border_style="green",
                    padding=(1, 3),
                )
            )

        # ------------------------------------------------------
        # Errors
        # ------------------------------------------------------

        if errors:

            error_text = "\n".join(
                f"🔴 {error}"
                for error in errors
            )

            panels.append(
                Panel(
                    error_text,
                    title="⚠️ REPORT WARNINGS",
                    border_style="yellow",
                    padding=(1, 3),
                )
            )

        # ------------------------------------------------------
        # Nothing Generated
        # ------------------------------------------------------

        if not generated and not errors:

            panels.append(
                Panel(
                    "No report was generated.",
                    title="📊 MONITORIX REPORTS",
                    border_style="yellow",
                    padding=(1, 3),
                )
            )

        return panels

    # ==========================================================
    # Execute Report Command
    # ==========================================================

    def execute(self) -> None:
        """
        Generate and display Monitorix reports.

        This method is provided as a simple command-level
        entry point for the CLI.
        """

        console.print()

        console.print(
            "📊 [bold cyan]"
            "GENERATING SECURITY REPORTS"
            "[/bold cyan]"
        )

        console.print(
            "─" * 72,
            style="dim",
        )

        try:

            reports = self.generate_all()

            panels = self.display(
                reports
            )

            for panel in panels:

                console.print(panel)

        except Exception as error:

            console.print(
                Panel(
                    f"🔴 [bold red]"
                    f"REPORT COMMAND FAILED"
                    f"[/bold red]\n\n"
                    f"{error}",
                    border_style="red",
                    padding=(1, 3),
                )
            )

            logger.exception(
                "Report command failed."
            )


# ==============================================================
# GLOBAL INSTANCE
# ==============================================================

reports_command = ReportsCommand()


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "ReportsCommand",
    "reports_command",
]
