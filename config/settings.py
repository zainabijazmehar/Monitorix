"""
Monitorix
Module: config.settings
Author: Zainab

Description:
Central configuration manager for Monitorix.

Responsibilities:
- Load environment variables
- Manage application paths
- Store application settings
- Configure monitoring behaviour
- Configure alert thresholds
- Configure CLI/dashboard behaviour
- Keep sensitive configuration outside source code
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ==============================================================
# ENVIRONMENT
# ==============================================================

load_dotenv()


# ==============================================================
# BASE DIRECTORY
# ==============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================
# SETTINGS
# ==============================================================

class Settings:
    """
    Global Monitorix configuration.

    Runtime configuration is centralized here so that other
    modules do not need to define their own paths or limits.
    """

    # ==========================================================
    # APPLICATION
    # ==========================================================

    APP_NAME: str = "MONITORIX"
    VERSION: str = "1.0.0"

    DESCRIPTION: str = (
        "Discord Security Monitoring Platform"
    )

    # ==========================================================
    # DISCORD
    # ==========================================================

    DISCORD_TOKEN: str = os.getenv(
        "DISCORD_TOKEN",
        "",
    )

    # ==========================================================
    # DIRECTORIES
    # ==========================================================

    DATABASE_DIR: Path = (
        BASE_DIR / "database"
    )

    REPORT_DIR: Path = (
        BASE_DIR / "reports"
    )

    BACKUP_DIR: Path = (
        BASE_DIR / "backups"
    )

    LOG_DIR: Path = (
        BASE_DIR / "logs"
    )

    DATA_DIR: Path = (
        BASE_DIR / "data"
    )

    # ==========================================================
    # DATABASE
    # ==========================================================

    DATABASE_PATH: Path = (
        DATABASE_DIR / "monitorix.db"
    )

    DATABASE_TIMEOUT: int = 30

    # ==========================================================
    # LOGGING
    # ==========================================================

    LOG_FILE: Path = (
        LOG_DIR / "monitorix.log"
    )

    LOG_LEVEL: str = os.getenv(
        "MONITORIX_LOG_LEVEL",
        "INFO",
    ).upper()

    # Maximum log file size: 5 MB
    LOG_MAX_SIZE: int = 5 * 1024 * 1024

    LOG_BACKUP_COUNT: int = 3

    # ==========================================================
    # REPORTS
    # ==========================================================

    REPORT_ENCODING: str = "utf-8"

    REPORT_FORMAT: str = os.getenv(
        "MONITORIX_REPORT_FORMAT",
        "txt",
    ).lower()

    # ==========================================================
    # BACKUPS
    # ==========================================================

    BACKUP_ENABLED: bool = (
        os.getenv(
            "MONITORIX_BACKUP_ENABLED",
            "true",
        ).lower()
        == "true"
    )

    # ==========================================================
    # MONITORING
    # ==========================================================

    MONITORING_ENABLED: bool = True

    TRACK_MESSAGES: bool = True
    TRACK_MESSAGE_EDITS: bool = True
    TRACK_MESSAGE_DELETIONS: bool = True

    TRACK_MEMBERS: bool = True
    TRACK_CHANNELS: bool = True
    TRACK_ROLES: bool = True
    TRACK_WEBHOOKS: bool = True

    # ==========================================================
    # HISTORY
    # ==========================================================

    HISTORY_DEFAULT_LIMIT: int = 20
    HISTORY_MAX_LIMIT: int = 500

    # ==========================================================
    # ALERTS
    # ==========================================================

    ALERTS_ENABLED: bool = True

    ALERT_DEFAULT_SEVERITY: str = "INFO"

    ALERT_HISTORY_LIMIT: int = 50

    # Risk score threshold at which an event becomes
    # security-relevant.
    RISK_ALERT_THRESHOLD: int = 10

    # ==========================================================
    # SECURITY
    # ==========================================================

    # Risk score range:
    MIN_RISK_SCORE: int = 0
    MAX_RISK_SCORE: int = 100

    # ==========================================================
    # CLI
    # ==========================================================

    CLI_PROMPT: str = "🛡 MONITORIX> "

    CLI_HISTORY_LIMIT: int = 20

    # Unicode/emoji UI is intentionally enabled because
    # Monitorix is primarily intended for modern terminals
    # such as Kali Linux Terminal.
    CLI_EMOJI_ENABLED: bool = True

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    DASHBOARD_ENABLED: bool = True

    DASHBOARD_TITLE: str = "MONITORIX"

    DASHBOARD_TAGLINE: str = (
        "DISCORD SECURITY MONITORING PLATFORM"
    )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def ensure_directories(self) -> None:
        """
        Create required Monitorix directories.
        """

        directories = (
            self.DATABASE_DIR,
            self.REPORT_DIR,
            self.BACKUP_DIR,
            self.LOG_DIR,
            self.DATA_DIR,
        )

        for directory in directories:
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    # ==========================================================

    def validate(self) -> None:
        """
        Validate critical application configuration.

        The Discord token is checked here rather than raising
        during module import, allowing local database/CLI
        operations to work without Discord credentials.
        """

        if self.HISTORY_DEFAULT_LIMIT < 1:
            raise ValueError(
                "HISTORY_DEFAULT_LIMIT must be greater than 0."
            )

        if self.HISTORY_MAX_LIMIT < (
            self.HISTORY_DEFAULT_LIMIT
        ):
            raise ValueError(
                "HISTORY_MAX_LIMIT must be greater than "
                "or equal to HISTORY_DEFAULT_LIMIT."
            )

        if not (
            self.MIN_RISK_SCORE
            <= self.RISK_ALERT_THRESHOLD
            <= self.MAX_RISK_SCORE
        ):
            raise ValueError(
                "RISK_ALERT_THRESHOLD must be between "
                "MIN_RISK_SCORE and MAX_RISK_SCORE."
            )

        if self.LOG_MAX_SIZE <= 0:
            raise ValueError(
                "LOG_MAX_SIZE must be greater than 0."
            )

    # ==========================================================

    @property
    def discord_configured(self) -> bool:
        """
        Return True when a Discord token is configured.
        """

        return bool(
            self.DISCORD_TOKEN.strip()
        )

    # ==========================================================

    def initialize(self) -> None:
        """
        Prepare Monitorix runtime directories and
        validate configuration.
        """

        self.ensure_directories()
        self.validate()


# ==============================================================
# GLOBAL SETTINGS INSTANCE
# ==============================================================

settings = Settings()

settings.initialize()


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "BASE_DIR",
    "Settings",
    "settings",
]
