"""
Monitorix
Module: services.alerts
Author: Zainab

Description:
Security alert management engine.

Responsibilities:
- Create and store security alerts
- Validate severity levels
- Track alert lifecycle
- Provide alert statistics
- Filter alerts by server/member/severity
- Calculate security status
- Support SOC dashboard data
- Prevent invalid alert records
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database.database import database
from services.logger import logger


class AlertService:
    """
    Central security alert engine for Monitorix.

    Alerts represent security-relevant activity detected
    by the monitoring system.
    """

    VALID_LEVELS = (
        "CRITICAL",
        "HIGH",
        "WARNING",
        "INFO",
    )

    VALID_STATUSES = (
        "OPEN",
        "ACKNOWLEDGED",
        "RESOLVED",
    )

    def __init__(self) -> None:
        logger.info(
            "Alert engine initialized"
        )

    # ==============================================================
    # CREATE ALERT
    # ==============================================================

    def create_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "INFO",
        user_id: str | None = None,
        guild_id: str | None = None,
        channel_id: str | None = None,
        target_id: str | None = None,
        risk_score: int = 0,
    ) -> int:
        """
        Create and persist a security alert.

        Returns:
            Database alert ID.
        """

        severity = self.normalize_severity(
            severity
        )

        risk_score = self.normalize_risk_score(
            risk_score
        )

        if not alert_type.strip():
            raise ValueError(
                "Alert type cannot be empty"
            )

        if not message.strip():
            raise ValueError(
                "Alert message cannot be empty"
            )

        alert_id = database.insert(
            "alerts",
            {
                "guild_id": guild_id or "global",
                "alert_type": alert_type.strip(),
                "user_id": user_id,
                "channel_id": channel_id,
                "target_id": target_id,
                "message": message.strip(),
                "severity": severity,
                "risk_score": risk_score,
                "status": "OPEN",
                "created_at": self.timestamp(),
            },
        )

        logger.warning(
            "Security alert created | id=%s severity=%s type=%s risk=%s",
            alert_id,
            severity,
            alert_type,
            risk_score,
        )

        return alert_id

    # ==============================================================
    # GET LATEST
    # ==============================================================

    def get_latest(
        self,
        limit: int = 10,
        guild_id: str | None = None,
    ) -> list[Any]:
        """
        Return latest alerts.

        Optional guild_id keeps server data isolated.
        """

        limit = self.normalize_limit(
            limit
        )

        if guild_id:

            return database.fetch_all(
                """
                SELECT *
                FROM alerts
                WHERE guild_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    guild_id,
                    limit,
                ),
            )

        return database.fetch_all(
            """
            SELECT *
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

    # ==============================================================
    # GET OPEN ALERTS
    # ==============================================================

    def get_open(
        self,
        guild_id: str | None = None,
        limit: int = 50,
    ) -> list[Any]:
        """
        Return unresolved alerts.
        """

        limit = self.normalize_limit(
            limit
        )

        if guild_id:

            return database.fetch_all(
                """
                SELECT *
                FROM alerts
                WHERE guild_id=?
                AND status IN ('OPEN', 'ACKNOWLEDGED')
                ORDER BY
                    CASE severity
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'WARNING' THEN 3
                        ELSE 4
                    END,
                    id DESC
                LIMIT ?
                """,
                (
                    guild_id,
                    limit,
                ),
            )

        return database.fetch_all(
            """
            SELECT *
            FROM alerts
            WHERE status IN ('OPEN', 'ACKNOWLEDGED')
            ORDER BY
                CASE severity
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'WARNING' THEN 3
                    ELSE 4
                END,
                id DESC
            LIMIT ?
            """,
            (limit,),
        )

    # ==============================================================
    # GET BY SEVERITY
    # ==============================================================

    def get_by_severity(
        self,
        severity: str,
        guild_id: str | None = None,
        limit: int = 50,
    ) -> list[Any]:
        """
        Return alerts matching a severity level.
        """

        severity = self.normalize_severity(
            severity
        )

        limit = self.normalize_limit(
            limit
        )

        if guild_id:

            return database.fetch_all(
                """
                SELECT *
                FROM alerts
                WHERE guild_id=?
                AND severity=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    guild_id,
                    severity,
                    limit,
                ),
            )

        return database.fetch_all(
            """
            SELECT *
            FROM alerts
            WHERE severity=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                severity,
                limit,
            ),
        )

    # ==============================================================
    # ACKNOWLEDGE ALERT
    # ==============================================================

    def acknowledge(
        self,
        alert_id: int,
    ) -> bool:
        """
        Mark an alert as acknowledged.
        """

        alert = database.fetch_one(
            """
            SELECT id, status
            FROM alerts
            WHERE id=?
            """,
            (alert_id,),
        )

        if not alert:
            return False

        if alert["status"] == "RESOLVED":
            return False

        database.update(
            "alerts",
            {
                "status": "ACKNOWLEDGED",
                "acknowledged_at": self.timestamp(),
            },
            "id=?",
            (alert_id,),
        )

        logger.info(
            "Alert acknowledged | id=%s",
            alert_id,
        )

        return True

    # ==============================================================
    # RESOLVE ALERT
    # ==============================================================

    def resolve(
        self,
        alert_id: int,
    ) -> bool:
        """
        Mark an alert as resolved.
        """

        alert = database.fetch_one(
            """
            SELECT id
            FROM alerts
            WHERE id=?
            """,
            (alert_id,),
        )

        if not alert:
            return False

        database.update(
            "alerts",
            {
                "status": "RESOLVED",
                "resolved_at": self.timestamp(),
            },
            "id=?",
            (alert_id,),
        )

        logger.info(
            "Alert resolved | id=%s",
            alert_id,
        )

        return True

    # ==============================================================
    # STATISTICS
    # ==============================================================

    def statistics(
        self,
        guild_id: str | None = None,
    ) -> dict[str, int]:
        """
        Return alert counts by severity.
        """

        result = {
            "CRITICAL": 0,
            "HIGH": 0,
            "WARNING": 0,
            "INFO": 0,
            "TOTAL": 0,
            "OPEN": 0,
        }

        if guild_id:

            rows = database.fetch_all(
                """
                SELECT severity,
                       COUNT(*) AS total
                FROM alerts
                WHERE guild_id=?
                GROUP BY severity
                """,
                (guild_id,),
            )

            open_row = database.fetch_one(
                """
                SELECT COUNT(*) AS total
                FROM alerts
                WHERE guild_id=?
                AND status IN ('OPEN', 'ACKNOWLEDGED')
                """,
                (guild_id,),
            )

        else:

            rows = database.fetch_all(
                """
                SELECT severity,
                       COUNT(*) AS total
                FROM alerts
                GROUP BY severity
                """
            )

            open_row = database.fetch_one(
                """
                SELECT COUNT(*) AS total
                FROM alerts
                WHERE status IN ('OPEN', 'ACKNOWLEDGED')
                """
            )

        for row in rows:

            level = row["severity"]

            if level in result:
                result[level] = int(
                    row["total"]
                )

        result["TOTAL"] = sum(
            result[level]
            for level in self.VALID_LEVELS
        )

        if open_row:
            result["OPEN"] = int(
                open_row["total"]
            )

        return result

    # ==============================================================
    # DASHBOARD DATA
    # ==============================================================

    def dashboard(
        self,
        guild_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Return structured data for the Monitorix dashboard.
        """

        statistics = self.statistics(
            guild_id
        )

        latest = self.get_latest(
            limit=10,
            guild_id=guild_id,
        )

        open_alerts = self.get_open(
            guild_id=guild_id,
            limit=10,
        )

        return {
            "summary": statistics,
            "latest": [
                dict(alert)
                for alert in latest
            ],
            "open": [
                dict(alert)
                for alert in open_alerts
            ],
            "status": self.security_status(
                statistics
            ),
        }

    # ==============================================================
    # SECURITY STATUS
    # ==============================================================

    @staticmethod
    def security_status(
        statistics: dict[str, int],
    ) -> str:
        """
        Determine overall security status.
        """

        if statistics["CRITICAL"] > 0:
            return "CRITICAL"

        if statistics["HIGH"] > 0:
            return "HIGH_RISK"

        if statistics["WARNING"] > 0:
            return "MONITOR"

        return "NORMAL"

    # ==============================================================
    # CLEAR ALERTS
    # ==============================================================

    def clear_alerts(
        self,
        guild_id: str | None = None,
    ) -> None:
        """
        Remove alerts.

        If guild_id is supplied, only that server's
        alerts are removed.
        """

        if guild_id:

            database.execute(
                """
                DELETE FROM alerts
                WHERE guild_id=?
                """,
                (guild_id,),
            )

            logger.warning(
                "Alerts cleared | guild=%s",
                guild_id,
            )

            return

        database.execute(
            """
            DELETE FROM alerts
            """
        )

        logger.warning(
            "All security alerts cleared"
        )

    # ==============================================================
    # NORMALIZATION
    # ==============================================================

    def normalize_severity(
        self,
        severity: str,
    ) -> str:
        """
        Normalize and validate severity.
        """

        normalized = (
            str(severity)
            .strip()
            .upper()
        )

        if normalized not in self.VALID_LEVELS:
            logger.warning(
                "Invalid severity '%s'; using INFO",
                severity,
            )

            return "INFO"

        return normalized

    # ==============================================================

    @staticmethod
    def normalize_risk_score(
        risk_score: int,
    ) -> int:
        """
        Keep risk score within 0-100.
        """

        try:
            score = int(
                risk_score
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0

        return max(
            0,
            min(
                score,
                100,
            ),
        )

    # ==============================================================

    @staticmethod
    def normalize_limit(
        limit: int,
    ) -> int:
        """
        Keep database result limits safe.
        """

        try:
            value = int(limit)
        except (
            TypeError,
            ValueError,
        ):
            return 10

        return max(
            1,
            min(
                value,
                500,
            ),
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

alert_service = AlertService()

# Used by Monitorix event and monitoring engines.
alert_engine = alert_service
