"""
Monitorix
Module: core.monitor
Author: Zainab

Description:
Central monitoring engine.

Responsibilities:
- Start and stop monitoring
- Route Discord events to EventManager
- Maintain monitoring state
- Track engine uptime
- Provide system status
- Provide health information
- Provide monitoring statistics
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from core.events import event_manager
from services.alerts import alert_engine
from services.logger import logger


class MonitorEngine:
    """
    Main Monitorix monitoring engine.

    The engine acts as the bridge between Discord events
    and Monitorix's event/alert processing layers.
    """

    EVENT_HANDLERS: dict[str, str] = {
        "MESSAGE_CREATED": "message_created",
        "MESSAGE_EDITED": "message_edited",
        "MESSAGE_DELETED": "message_deleted",
        "MEMBER_JOINED": "member_join",
        "MEMBER_JOIN": "member_join",
        "MEMBER_LEFT": "member_leave",
        "MEMBER_LEAVE": "member_leave",
        "CHANNEL_CREATED": "channel_created",
        "CHANNEL_DELETED": "channel_deleted",
        "ROLE_CREATED": "role_created",
        "ROLE_UPDATED": "role_updated",
        "WEBHOOK_CREATED": "webhook_created",
    }

    def __init__(self) -> None:
        self.running: bool = False
        self.started_at: str | None = None
        self.stopped_at: str | None = None

        self.events_processed: int = 0
        self.events_failed: int = 0

        self.last_event_type: str | None = None
        self.last_event_at: str | None = None

        logger.info(
            "Monitor engine initialized."
        )

    # ==============================================================
    # START
    # ==============================================================

    def start(self) -> None:
        """
        Start the Monitorix monitoring engine.
        """

        if self.running:
            logger.debug(
                "Monitor engine is already running."
            )
            return

        self.running = True
        self.started_at = self.timestamp()
        self.stopped_at = None

        logger.info(
            "Monitorix monitoring engine started."
        )

    # ==============================================================
    # STOP
    # ==============================================================

    def stop(self) -> None:
        """
        Stop the Monitorix monitoring engine.
        """

        if not self.running:
            logger.debug(
                "Monitor engine is already stopped."
            )
            return

        self.running = False
        self.stopped_at = self.timestamp()

        logger.info(
            "Monitorix monitoring engine stopped."
        )

    # ==============================================================
    # PROCESS EVENT
    # ==============================================================

    def process_event(
        self,
        event_type: str,
        data: Any,
    ) -> bool:
        """
        Process and route a monitoring event.

        Args:
            event_type:
                Monitorix event name.

            data:
                Discord event payload.

        Returns:
            True when the event is successfully routed.
        """

        if not self.running:
            logger.warning(
                "Event '%s' received while monitor is stopped.",
                event_type,
            )
            return False

        normalized_event = (
            str(event_type)
            .strip()
            .upper()
        )

        self.last_event_type = normalized_event
        self.last_event_at = self.timestamp()

        logger.info(
            "Processing monitoring event: %s",
            normalized_event,
        )

        try:
            handler_name = self.EVENT_HANDLERS.get(
                normalized_event
            )

            if handler_name is None:
                logger.warning(
                    "Unsupported monitoring event: %s",
                    normalized_event,
                )
                self.events_failed += 1
                return False

            handler: Callable[..., Any] | None = getattr(
                event_manager,
                handler_name,
                None,
            )

            if handler is None:
                logger.error(
                    "Event handler '%s' is not available.",
                    handler_name,
                )
                self.events_failed += 1
                return False

            handler(data)

            self.events_processed += 1

            logger.info(
                "Event processed successfully: %s",
                normalized_event,
            )

            return True

        except Exception as error:
            self.events_failed += 1

            logger.exception(
                "Event processing failed [%s]: %s",
                normalized_event,
                error,
            )

            return False

    # ==============================================================
    # DISCORD EVENT ALIASES
    # ==============================================================

    def message_created(
        self,
        message: Any,
    ) -> bool:
        """
        Direct message-created event entry point.
        """

        return self.process_event(
            "MESSAGE_CREATED",
            message,
        )

    # ==============================================================

    def message_edited(
        self,
        before: Any,
        after: Any,
    ) -> bool:
        """
        Direct message-edited event entry point.
        """

        if not self.running:
            return False

        try:
            event_manager.message_edited(
                before,
                after,
            )

            self.events_processed += 1
            self.last_event_type = "MESSAGE_EDITED"
            self.last_event_at = self.timestamp()

            return True

        except Exception as error:
            self.events_failed += 1

            logger.exception(
                "Message edit processing failed: %s",
                error,
            )

            return False

    # ==============================================================

    def message_deleted(
        self,
        message: Any,
    ) -> bool:
        """
        Direct message-deleted event entry point.
        """

        return self.process_event(
            "MESSAGE_DELETED",
            message,
        )

    # ==============================================================
    # STATUS
    # ==============================================================

    def status(self) -> dict[str, Any]:
        """
        Return detailed monitoring engine status.
        """

        return {
            "engine": (
                "ONLINE"
                if self.running
                else "OFFLINE"
            ),
            "started": self.started_at,
            "stopped": self.stopped_at,
            "last_event": self.last_event_type,
            "last_event_at": self.last_event_at,
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "modules": {
                "Discord Monitoring": (
                    "ACTIVE"
                    if self.running
                    else "STOPPED"
                ),
                "Message Audit": (
                    "ACTIVE"
                    if self.running
                    else "STOPPED"
                ),
                "Member Monitoring": (
                    "ACTIVE"
                    if self.running
                    else "STOPPED"
                ),
                "Channel Monitoring": (
                    "ACTIVE"
                    if self.running
                    else "STOPPED"
                ),
                "Role Monitoring": (
                    "ACTIVE"
                    if self.running
                    else "STOPPED"
                ),
                "Webhook Monitoring": (
                    "ACTIVE"
                    if self.running
                    else "STOPPED"
                ),
                "Security Alerts": (
                    "ACTIVE"
                    if self.running
                    else "STOPPED"
                ),
            },
        }

    # ==============================================================
    # HEALTH
    # ==============================================================

    def health(self) -> dict[str, str]:
        """
        Return current Monitorix health state.
        """

        if not self.running:
            return {
                "status": "STOPPED",
                "timestamp": self.timestamp(),
            }

        if self.events_failed > 0:
            return {
                "status": "DEGRADED",
                "timestamp": self.timestamp(),
            }

        return {
            "status": "HEALTHY",
            "timestamp": self.timestamp(),
        }

    # ==============================================================
    # STATISTICS
    # ==============================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return monitoring engine statistics.
        """

        return {
            "running": self.running,
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "last_event": self.last_event_type,
            "last_event_at": self.last_event_at,
        }

    # ==============================================================
    # RESET STATISTICS
    # ==============================================================

    def reset_statistics(self) -> None:
        """
        Reset runtime event counters.

        Database audit history is NOT deleted.
        """

        self.events_processed = 0
        self.events_failed = 0

        logger.info(
            "Monitor runtime statistics reset."
        )

    # ==============================================================
    # TIMESTAMP
    # ==============================================================

    @staticmethod
    def timestamp() -> str:
        """
        Return current UTC timestamp.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()


# ==============================================================
# GLOBAL INSTANCE
# ==============================================================

monitor_engine = MonitorEngine()
