"""
Monitorix
Module: core.bot
Author: Zainab

Description:
Discord bot controller.

Responsibilities:
- Connect Discord API
- Register Discord events
- Start monitoring engine
"""

from __future__ import annotations

import discord
from discord.ext import commands

from config.settings import settings
from core.events import event_manager
from core.monitor import monitor_engine
from services.logger import logger


class MonitorixBot:
    """
    Main Discord bot controller.
    """

    def __init__(self) -> None:

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        self.bot = commands.Bot(
            command_prefix="!",
            intents=intents,
        )

        self.register_events()

        logger.info("Discord bot initialized.")

    # =====================================================
    # Discord Events
    # =====================================================

    def register_events(self) -> None:
        """
        Register Discord event handlers.
        """

        @self.bot.event
        async def on_ready() -> None:

            logger.info(
                "Connected as %s",
                self.bot.user,
            )

            for guild in self.bot.guilds:
                logger.info(
                    "Connected to server: %s",
                    guild.name,
                )

            try:
                monitor_engine.start()
            except Exception:
                logger.exception(
                    "Failed to start monitoring engine."
                )

        @self.bot.event
        async def on_message(
            message: discord.Message,
        ) -> None:

            if message.author.bot:
                return

            try:
                event_manager.message_created(message)
            except Exception:
                logger.exception(
                    "Message event failed."
                )

            await self.bot.process_commands(message)

        @self.bot.event
        async def on_message_delete(
            message: discord.Message,
        ) -> None:

            try:
                event_manager.message_deleted(message)
            except Exception:
                logger.exception(
                    "Message delete event failed."
                )

        @self.bot.event
        async def on_message_edit(
            before: discord.Message,
            after: discord.Message,
        ) -> None:

            try:
                event_manager.message_edited(
                    before,
                    after,
                )
            except Exception:
                logger.exception(
                    "Message edit event failed."
                )

        @self.bot.event
        async def on_member_join(
            member: discord.Member,
        ) -> None:

            try:
                event_manager.member_join(member)
            except Exception:
                logger.exception(
                    "Member join event failed."
                )

        @self.bot.event
        async def on_member_remove(
            member: discord.Member,
        ) -> None:

            try:
                event_manager.member_leave(member)
            except Exception:
                logger.exception(
                    "Member remove event failed."
                )

    # =====================================================
    # Start Bot
    # =====================================================

    async def start(self) -> None:
        """
        Start the Discord bot.
        """

        if not settings.DISCORD_TOKEN:
            raise RuntimeError(
                "Discord token is not configured."
            )

        logger.info("Starting Discord bot...")

        try:
            await self.bot.start(
                settings.DISCORD_TOKEN
            )

        except Exception:
            logger.exception(
                "Discord bot stopped unexpectedly."
            )
            raise

    # =====================================================
    # Shutdown
    # =====================================================

    async def close(self) -> None:
        """
        Shutdown the Discord bot.
        """

        try:
            monitor_engine.stop()
        except Exception:
            logger.exception(
                "Failed to stop monitoring engine."
            )

        try:
            await self.bot.close()
        except Exception:
            logger.exception(
                "Failed to close Discord bot."
            )

        logger.info("Discord bot shutdown completed.")


# =====================================================
# Global Instance
# =====================================================

monitorix_bot = MonitorixBot()