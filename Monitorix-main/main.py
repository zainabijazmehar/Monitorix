"""
Monitorix
Main Application Entry Point

Author: Zainab

Description:
Starts and manages the Monitorix SOC Monitoring Platform.

Responsibilities:
- Initialize database
- Initialize report engine
- Start Discord monitoring
- Start CLI console
- Coordinate application lifecycle
- Perform graceful shutdown
"""

from __future__ import annotations

import asyncio

from cli.cli import CLIApplication
from core.bot import monitorix_bot
from database.database import DatabaseManager
import services.reports as reports
from services.logger import logger


class MonitorixApplication:
    """
    Main Monitorix application controller.
    """

    def __init__(self) -> None:
        self.running: bool = False
        self.database: DatabaseManager | None = None

        # Attach the real Discord.py bot to the CLI.
        self.cli_application = CLIApplication(
            monitorix_bot.bot
        )

        logger.info(
            "Monitorix application created."
        )

    # ==========================================================
    # Initialization
    # ==========================================================

    async def initialize(self) -> None:
        """
        Initialize all Monitorix services.
        """

        logger.info(
            "Initializing Monitorix services..."
        )

        try:

            # --------------------------------------------------
            # Database
            # --------------------------------------------------

            self.database = DatabaseManager()

            logger.info(
                "Database service initialized."
            )

            # --------------------------------------------------
            # Report Engine
            # --------------------------------------------------

            reports.report_generator = (
                reports.ReportGenerator(
                    self.database
                )
            )

            logger.info(
                "Report service initialized."
            )

            # --------------------------------------------------
            # Application State
            # --------------------------------------------------

            self.running = True

            logger.info(
                "Monitorix initialization completed successfully."
            )

        except Exception as error:

            logger.exception(
                "Monitorix initialization failed: %s",
                error,
            )

            raise

    # ==========================================================
    # Run
    # ==========================================================

    async def run(self) -> None:
        """
        Start Monitorix services and run the application.
        """

        await self.initialize()

        logger.info(
            "Starting Monitorix services..."
        )

        bot_task: asyncio.Task | None = None
        cli_task: asyncio.Task | None = None

        try:

            # --------------------------------------------------
            # Discord Bot
            # --------------------------------------------------

            bot_task = asyncio.create_task(
                monitorix_bot.start()
            )

            logger.info(
                "Discord monitoring task started."
            )

            # --------------------------------------------------
            # CLI
            # --------------------------------------------------

            cli_task = asyncio.create_task(
                self.cli_application.start()
            )

            logger.info(
                "CLI monitoring task started."
            )

            # --------------------------------------------------
            # Run Both Services
            # --------------------------------------------------

            await asyncio.gather(
                bot_task,
                cli_task,
            )

        except asyncio.CancelledError:

            logger.info(
                "Monitorix tasks cancelled."
            )

            raise

        except Exception as error:

            logger.exception(
                "Monitorix runtime error: %s",
                error,
            )

            raise

        finally:

            await self.shutdown()

    # ==========================================================
    # Shutdown
    # ==========================================================

    async def shutdown(self) -> None:
        """
        Gracefully stop all Monitorix services.
        """

        if not self.running and self.database is None:
            return

        logger.info(
            "Shutting down Monitorix..."
        )

        # ------------------------------------------------------
        # Stop CLI
        # ------------------------------------------------------

        try:

            self.cli_application.shutdown()

        except Exception:

            logger.exception(
                "Failed to stop CLI application."
            )

        # ------------------------------------------------------
        # Stop Discord Bot
        # ------------------------------------------------------

        try:

            if not monitorix_bot.bot.is_closed():

                await monitorix_bot.close()

                logger.info(
                    "Discord bot stopped."
                )

        except Exception:

            logger.exception(
                "Failed to stop Discord bot."
            )

        # ------------------------------------------------------
        # Close Database
        # ------------------------------------------------------

        try:

            if self.database is not None:

                self.database.close()

                logger.info(
                    "Database connection closed."
                )

        except Exception:

            logger.exception(
                "Failed to close database."
            )

        # ------------------------------------------------------
        # Final State
        # ------------------------------------------------------

        self.running = False

        logger.info(
            "Monitorix stopped successfully."
        )


# ==============================================================
# Main Function
# ==============================================================

async def main() -> None:
    """
    Application entry point.
    """

    application = MonitorixApplication()

    try:

        await application.run()

    except KeyboardInterrupt:

        logger.info(
            "Keyboard interrupt received."
        )

        await application.shutdown()

    except asyncio.CancelledError:

        logger.info(
            "Monitorix execution cancelled."
        )

        await application.shutdown()

    except Exception as error:

        logger.exception(
            "Fatal Monitorix error: %s",
            error,
        )

        await application.shutdown()


# ==============================================================
# Entry Point
# ==============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        pass
