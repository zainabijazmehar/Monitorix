"""
Monitorix
Module: display.icons
Author: Zainab

Description:
Terminal-compatible icon manager for Monitorix.

Design:
- Optimized for Kali Linux terminals
- Compatible with Linux terminals
- Compatible with Windows Terminal
- Uses lightweight Unicode symbols
- Automatic ASCII fallback
- Avoids emoji characters that may render inconsistently
"""

from __future__ import annotations

import os
import sys


# ==============================================================
# UNICODE SUPPORT
# ==============================================================

def supports_unicode() -> bool:
    """
    Detect whether the current terminal can reasonably
    support Unicode characters.
    """

    # ----------------------------------------------------------
    # Windows
    # ----------------------------------------------------------

    if os.name == "nt":

        # Windows Terminal
        if "WT_SESSION" in os.environ:
            return True

        # Modern PowerShell / terminal environments
        if os.environ.get("TERM_PROGRAM"):
            return True

        # UTF-8 capable Windows console
        try:
            encoding = (
                sys.stdout.encoding or ""
            ).lower()

            return "utf" in encoding

        except Exception:
            return False

    # ----------------------------------------------------------
    # Linux / Kali / Unix
    # ----------------------------------------------------------

    try:

        encoding = (
            sys.stdout.encoding or ""
        ).lower()

        return (
            "utf" in encoding
            or
            os.environ.get(
                "LANG",
                "",
            ).lower().find("utf") >= 0
        )

    except Exception:

        return True


# ==============================================================
# KALI / UNIX TERMINAL ICONS
# ==============================================================

UNICODE_ICONS = {

    # ----------------------------------------------------------
    # Branding
    # ----------------------------------------------------------

    "logo": "◆",

    # ----------------------------------------------------------
    # Security
    # ----------------------------------------------------------

    "security": "◇",

    "alert": "!",

    "critical": "✖",

    "warning": "▲",

    "success": "✓",

    # ----------------------------------------------------------
    # System
    # ----------------------------------------------------------

    "online": "●",

    "offline": "○",

    "status": "◆",

    "monitor": "›",

    "database": "▣",

    # ----------------------------------------------------------
    # Discord / Audit
    # ----------------------------------------------------------

    "bot": "◆",

    "message": "»",

    "user": "●",

    "member": "●",

    "channel": "#",

    "server": "■",

    # ----------------------------------------------------------
    # Monitoring
    # ----------------------------------------------------------

    "event": "›",

    "activity": "→",

    "history": "≡",

    "search": "?",

    "filter": "≡",

    # ----------------------------------------------------------
    # Reports / Storage
    # ----------------------------------------------------------

    "report": "▤",

    "backup": "◆",

    "restore": "↻",

    "file": "□",

    # ----------------------------------------------------------
    # Navigation
    # ----------------------------------------------------------

    "arrow": "→",

    "next": "›",

    "back": "‹",

    "bullet": "•",

    # ----------------------------------------------------------
    # Actions
    # ----------------------------------------------------------

    "add": "+",

    "remove": "-",

    "edit": "~",

    "delete": "✖",

    "lock": "#",

    "unlock": "○",

    # ----------------------------------------------------------
    # Terminal
    # ----------------------------------------------------------

    "terminal": "$",

    "command": ">",

    "info": "i",

    "help": "?",

}


# ==============================================================
# ASCII FALLBACK
# ==============================================================

ASCII_ICONS = {

    "logo": "[*]",

    "security": "[SEC]",

    "alert": "[!]",

    "critical": "[X]",

    "warning": "[WARN]",

    "success": "[OK]",

    "online": "[ON]",

    "offline": "[OFF]",

    "status": "[STATUS]",

    "monitor": "[MON]",

    "database": "[DB]",

    "bot": "[BOT]",

    "message": "[MSG]",

    "user": "[USER]",

    "member": "[MEMBER]",

    "channel": "[#]",

    "server": "[SERVER]",

    "event": "[EVENT]",

    "activity": "[ACT]",

    "history": "[HISTORY]",

    "search": "[SEARCH]",

    "filter": "[FILTER]",

    "report": "[REPORT]",

    "backup": "[BACKUP]",

    "restore": "[RESTORE]",

    "file": "[FILE]",

    "arrow": "->",

    "next": ">",

    "back": "<",

    "bullet": "*",

    "add": "+",

    "remove": "-",

    "edit": "~",

    "delete": "[X]",

    "lock": "[LOCK]",

    "unlock": "[OPEN]",

    "terminal": "$",

    "command": ">",

    "info": "[INFO]",

    "help": "[HELP]",

}


# ==============================================================
# ACTIVE ICON SET
# ==============================================================

ICONS = (
    UNICODE_ICONS
    if supports_unicode()
    else ASCII_ICONS
)


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "ICONS",
    "UNICODE_ICONS",
    "ASCII_ICONS",
    "supports_unicode",
]
