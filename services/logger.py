"""
Monitorix
Module: services.logger
Author: Zainab

Description:
Centralized production logging system for Monitorix.

Responsibilities:
- Application logging
- Security event logging
- File logging
- Clean terminal output
- Rotating log files
- Prevent duplicate handlers
- Consistent log formatting
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ==============================================================
# LOG CONFIGURATION
# ==============================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIR / "monitorix.log"

LOGGER_NAME = "Monitorix"

MAX_LOG_SIZE = 5 * 1024 * 1024
BACKUP_COUNT = 3


# ==============================================================
# FORMATTERS
# ==============================================================

FILE_FORMAT = logging.Formatter(
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CONSOLE_FORMAT = logging.Formatter(
    "%(levelname)s | %(message)s"
)


# ==============================================================
# LOGGER
# ==============================================================

logger = logging.getLogger(
    LOGGER_NAME
)

logger.setLevel(
    logging.INFO
)

logger.propagate = False


# ==============================================================
# HANDLER SETUP
# ==============================================================

def _configure_logger() -> None:
    """
    Configure Monitorix logging handlers.

    File:
        INFO and above

    Terminal:
        WARNING and above

    This keeps the terminal clean while preserving
    detailed information inside monitorix.log.
    """

    if logger.handlers:
        return

    # ----------------------------------------------------------
    # Rotating File Handler
    # ----------------------------------------------------------

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        FILE_FORMAT
    )

    # ----------------------------------------------------------
    # Console Handler
    # ----------------------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        logging.WARNING
    )

    console_handler.setFormatter(
        CONSOLE_FORMAT
    )

    # ----------------------------------------------------------
    # Register handlers
    # ----------------------------------------------------------

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )


# ==============================================================
# INITIALIZE
# ==============================================================

_configure_logger()


# ==============================================================
# LOGGING HELPERS
# ==============================================================

def log_security_event(
    event: str,
    severity: str = "INFO",
) -> None:
    """
    Write a security-related event to the Monitorix log.

    Args:
        event:
            Security event description.

        severity:
            INFO, WARNING, ERROR, or CRITICAL.
    """

    level = (
        str(severity)
        .strip()
        .upper()
    )

    if level == "CRITICAL":
        logger.critical(
            "[SECURITY] %s",
            event,
        )

    elif level == "ERROR":
        logger.error(
            "[SECURITY] %s",
            event,
        )

    elif level == "WARNING":
        logger.warning(
            "[SECURITY] %s",
            event,
        )

    else:
        logger.info(
            "[SECURITY] %s",
            event,
        )


def log_audit_event(
    event: str,
) -> None:
    """
    Write an audit event to the application log.
    """

    logger.info(
        "[AUDIT] %s",
        event,
    )


# ==============================================================
# SHUTDOWN
# ==============================================================

def shutdown_logger() -> None:
    """
    Flush and close all Monitorix logging handlers.

    Useful during clean application shutdown.
    """

    for handler in logger.handlers:

        try:
            handler.flush()
            handler.close()

        except Exception:
            pass

    logger.handlers.clear()


# ==============================================================
# EXPORT
# ==============================================================

__all__ = [
    "logger",
    "log_security_event",
    "log_audit_event",
    "shutdown_logger",
]
