"""
Monitorix
Module: services.reports
Author: Zainab

Description:
Professional monitoring report generator for Monitorix.

Features:
- TXT report generation
- Professional HTML report generation
- Database statistics
- Message audit statistics
- Edited/deleted message tracking
- Member and channel statistics
- Event statistics
- Security alert summary
- Alert severity breakdown
- Recent security alerts
- Automatic reports directory creation
- Timestamped reports
- Windows and Linux compatible
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from database.database import database
from config.settings import settings


# ==============================================================
# LOGGER
# ==============================================================

logger = logging.getLogger(__name__)


# ==============================================================
# REPORT GENERATOR
# ==============================================================

class ReportGenerator:
    """
    Generates professional Monitorix monitoring reports.
    """

    def __init__(
        self,
        database_manager: Any = database,
        reports_directory: str | Path | None = None,
    ) -> None:

        self.database = database_manager

        self.reports_directory = Path(
            reports_directory
            if reports_directory is not None
            else settings.REPORT_DIR
        )

        self.reports_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            "Report generator initialized | directory=%s",
            self.reports_directory.resolve(),
        )

    # ==========================================================
    # DATABASE QUERY HELPERS
    # ==========================================================

    def _safe_query(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> int:
        """
        Execute a COUNT query safely.
        """

        try:

            row = self.database.fetch_one(
                query,
                parameters,
            )

            if row is None:
                return 0

            return int(
                row[0]
            )

        except Exception as error:

            logger.exception(
                "Report statistics query failed: %s",
                error,
            )

            return 0

    # ==========================================================
    # DATABASE STATISTICS
    # ==========================================================

    def get_database_statistics(
        self,
    ) -> dict[str, int]:
        """
        Collect overall database statistics.
        """

        return {

            "messages": self._safe_query(
                "SELECT COUNT(*) FROM messages"
            ),

            "alerts": self._safe_query(
                "SELECT COUNT(*) FROM alerts"
            ),

            "events": self._safe_query(
                "SELECT COUNT(*) FROM events"
            ),

            "members": self._safe_query(
                "SELECT COUNT(*) FROM members"
            ),

            "channels": self._safe_query(
                "SELECT COUNT(*) FROM channels"
            ),

            "servers": self._safe_query(
                "SELECT COUNT(*) FROM servers"
            ),

            "users": self._safe_query(
                """
                SELECT COUNT(DISTINCT user_id)
                FROM messages
                """
            ),
        }

    # ==========================================================
    # MESSAGE STATISTICS
    # ==========================================================

    def get_message_statistics(
        self,
    ) -> dict[str, int]:
        """
        Collect message audit statistics.
        """

        return {

            "total": self._safe_query(
                "SELECT COUNT(*) FROM messages"
            ),

            "edited": self._safe_query(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE edited = 1
                """
            ),

            "deleted": self._safe_query(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE deleted = 1
                """
            ),

            "active": self._safe_query(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE deleted = 0
                """
            ),

            "unique_users": self._safe_query(
                """
                SELECT COUNT(DISTINCT user_id)
                FROM messages
                """
            ),

            "unique_channels": self._safe_query(
                """
                SELECT COUNT(DISTINCT channel_id)
                FROM messages
                """
            ),
        }

    # ==========================================================
    # ALERT STATISTICS
    # ==========================================================

    def get_alert_summary(
        self,
    ) -> dict[str, int]:
        """
        Collect security alert statistics.
        """

        return {

            "total": self._safe_query(
                "SELECT COUNT(*) FROM alerts"
            ),

            "critical": self._safe_query(
                """
                SELECT COUNT(*)
                FROM alerts
                WHERE severity = 'CRITICAL'
                """
            ),

            "warning": self._safe_query(
                """
                SELECT COUNT(*)
                FROM alerts
                WHERE severity = 'WARNING'
                """
            ),

            "info": self._safe_query(
                """
                SELECT COUNT(*)
                FROM alerts
                WHERE severity = 'INFO'
                """
            ),
        }

    # ==========================================================
    # RECENT ALERTS
    # ==========================================================

    def get_recent_alerts(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return recent security alerts.
        """

        try:

            rows = self.database.fetch_all(
                """
                SELECT
                    alert_type,
                    user_id,
                    message,
                    severity,
                    created_at
                FROM alerts
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )

            return [
                dict(row)
                for row in rows
            ]

        except Exception as error:

            logger.exception(
                "Failed loading recent alerts: %s",
                error,
            )

            return []

    # ==========================================================
    # EVENT STATISTICS
    # ==========================================================

    def get_event_statistics(
        self,
    ) -> dict[str, int]:
        """
        Collect monitoring event statistics.
        """

        return {

            "total": self._safe_query(
                "SELECT COUNT(*) FROM events"
            ),

            "messages_created": self._safe_query(
                """
                SELECT COUNT(*)
                FROM events
                WHERE event_type = 'MESSAGE_CREATED'
                """
            ),

            "messages_edited": self._safe_query(
                """
                SELECT COUNT(*)
                FROM events
                WHERE event_type = 'MESSAGE_EDITED'
                """
            ),

            "messages_deleted": self._safe_query(
                """
                SELECT COUNT(*)
                FROM events
                WHERE event_type = 'MESSAGE_DELETED'
                """
            ),

            "members_joined": self._safe_query(
                """
                SELECT COUNT(*)
                FROM events
                WHERE event_type = 'MEMBER_JOIN'
                """
            ),

            "members_left": self._safe_query(
                """
                SELECT COUNT(*)
                FROM events
                WHERE event_type = 'MEMBER_LEAVE'
                """
            ),
        }

    # ==========================================================
    # COLLECT REPORT DATA
    # ==========================================================

    def collect_report_data(
        self,
    ) -> dict[str, Any]:
        """
        Collect all information required for reports.
        """

        generated_at = datetime.now(
            timezone.utc
        ).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        return {

            "generated_at": generated_at,

            "database": (
                self.get_database_statistics()
            ),

            "messages": (
                self.get_message_statistics()
            ),

            "alerts": (
                self.get_alert_summary()
            ),

            "events": (
                self.get_event_statistics()
            ),

            "recent_alerts": (
                self.get_recent_alerts()
            ),
        }

    # ==========================================================
    # TEXT REPORT
    # ==========================================================

    def _build_report_text(
        self,
    ) -> str:
        """
        Build a professional plain-text report.
        """

        data = self.collect_report_data()

        database_stats = data["database"]
        messages = data["messages"]
        alerts = data["alerts"]
        events = data["events"]

        lines = [

            "=" * 72,

            "                         MONITORIX",

            "              DISCORD SECURITY MONITORING",

            "                  AUDIT & THREAT REPORT",

            "=" * 72,

            "",

            f"Generated: {data['generated_at']}",

            "",

            "-" * 72,

            "DATABASE OVERVIEW",

            "-" * 72,

            f"Servers             : {database_stats['servers']}",
            f"Members             : {database_stats['members']}",
            f"Channels            : {database_stats['channels']}",
            f"Unique Users        : {database_stats['users']}",
            f"Messages            : {database_stats['messages']}",
            f"Events              : {database_stats['events']}",
            f"Alerts              : {database_stats['alerts']}",

            "",

            "-" * 72,

            "MESSAGE AUDIT",

            "-" * 72,

            f"Total Messages      : {messages['total']}",
            f"Active Messages     : {messages['active']}",
            f"Edited Messages     : {messages['edited']}",
            f"Deleted Messages    : {messages['deleted']}",
            f"Unique Users        : {messages['unique_users']}",
            f"Unique Channels     : {messages['unique_channels']}",

            "",

            "-" * 72,

            "SECURITY ALERTS",

            "-" * 72,

            f"Total Alerts        : {alerts['total']}",
            f"Critical            : {alerts['critical']}",
            f"Warning             : {alerts['warning']}",
            f"Informational       : {alerts['info']}",

            "",

            "-" * 72,

            "MONITORING EVENTS",

            "-" * 72,

            f"Total Events        : {events['total']}",
            f"Messages Created    : {events['messages_created']}",
            f"Messages Edited    : {events['messages_edited']}",
            f"Messages Deleted   : {events['messages_deleted']}",
            f"Members Joined      : {events['members_joined']}",
            f"Members Left        : {events['members_left']}",

            "",

            "-" * 72,

            "RECENT SECURITY ALERTS",

            "-" * 72,

        ]

        recent_alerts = data["recent_alerts"]

        if not recent_alerts:

            lines.append(
                "No security alerts recorded."
            )

        else:

            for alert in recent_alerts:

                lines.extend(
                    [
                        "",
                        f"[{alert.get('severity', 'INFO')}] "
                        f"{alert.get('alert_type', 'UNKNOWN')}",
                        f"User: {alert.get('user_id') or 'N/A'}",
                        f"Message: {alert.get('message') or 'N/A'}",
                        f"Time: {alert.get('created_at') or 'N/A'}",
                    ]
                )

        lines.extend(
            [
                "",
                "=" * 72,
                "MONITORIX REPORT COMPLETE",
                "=" * 72,
            ]
        )

        return "\n".join(lines)

    # ==========================================================
    # GENERATE TXT
    # ==========================================================

    def generate_txt_report(
        self,
    ) -> Path:
        """
        Generate a TXT monitoring report.
        """

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        report_file = (
            self.reports_directory
            / f"monitorix_report_{timestamp}.txt"
        )

        report_file.write_text(
            self._build_report_text(),
            encoding=settings.REPORT_ENCODING,
        )

        logger.info(
            "TXT report generated: %s",
            report_file,
        )

        return report_file

    # ==========================================================
    # HTML REPORT
    # ==========================================================

    def generate_html_report(
        self,
    ) -> Path:
        """
        Generate a professional HTML monitoring report.
        """

        data = self.collect_report_data()

        database_stats = data["database"]
        messages = data["messages"]
        alerts = data["alerts"]
        events = data["events"]

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        report_file = (
            self.reports_directory
            / f"monitorix_report_{timestamp}.html"
        )

        generated = escape(
            data["generated_at"]
        )

        recent_alerts_html = ""

        for alert in data["recent_alerts"]:

            severity = escape(
                str(
                    alert.get(
                        "severity",
                        "INFO",
                    )
                )
            )

            recent_alerts_html += f"""
            <tr>
                <td>{escape(str(alert.get("alert_type", "UNKNOWN")))}</td>
                <td>{escape(str(alert.get("user_id") or "N/A"))}</td>
                <td>{escape(str(alert.get("message") or "N/A"))}</td>
                <td class="severity">{severity}</td>
                <td>{escape(str(alert.get("created_at") or "N/A"))}</td>
            </tr>
            """

        if not recent_alerts_html:

            recent_alerts_html = """
            <tr>
                <td colspan="5">No security alerts recorded.</td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Monitorix Security Report</title>

<style>

body {{
    margin: 0;
    padding: 0;
    background: #0b1120;
    color: #e5e7eb;
    font-family: Arial, Helvetica, sans-serif;
}}

.container {{
    max-width: 1100px;
    margin: 40px auto;
    padding: 30px;
}}

.header {{
    padding: 30px;
    border: 1px solid #243047;
    border-radius: 12px;
    background: #111827;
}}

.header h1 {{
    margin: 0;
    font-size: 32px;
    letter-spacing: 2px;
}}

.header p {{
    color: #9ca3af;
}}

.section {{
    margin-top: 25px;
}}

.section h2 {{
    font-size: 18px;
    letter-spacing: 1px;
    border-bottom: 1px solid #243047;
    padding-bottom: 10px;
}}

.cards {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
}}

.card {{
    background: #111827;
    border: 1px solid #243047;
    border-radius: 10px;
    padding: 20px;
}}

.card .number {{
    font-size: 28px;
    font-weight: bold;
}}

.card .label {{
    color: #9ca3af;
    margin-top: 5px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: #111827;
    border-radius: 10px;
    overflow: hidden;
}}

th, td {{
    padding: 12px;
    border-bottom: 1px solid #243047;
    text-align: left;
}}

th {{
    color: #9ca3af;
    font-size: 13px;
    text-transform: uppercase;
}}

.severity {{
    font-weight: bold;
}}

.footer {{
    margin-top: 35px;
    padding-top: 20px;
    border-top: 1px solid #243047;
    color: #6b7280;
    font-size: 13px;
}}

</style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>MONITORIX</h1>

        <p>
            DISCORD SECURITY MONITORING
            &amp; AUDIT REPORT
        </p>

        <p>
            Generated: {generated}
        </p>

    </div>


    <div class="section">

        <h2>DATABASE OVERVIEW</h2>

        <div class="cards">

            <div class="card">
                <div class="number">
                    {database_stats["servers"]}
                </div>
                <div class="label">Servers</div>
            </div>

            <div class="card">
                <div class="number">
                    {database_stats["members"]}
                </div>
                <div class="label">Members</div>
            </div>

            <div class="card">
                <div class="number">
                    {database_stats["channels"]}
                </div>
                <div class="label">Channels</div>
            </div>

            <div class="card">
                <div class="number">
                    {database_stats["messages"]}
                </div>
                <div class="label">Messages</div>
            </div>

            <div class="card">
                <div class="number">
                    {database_stats["events"]}
                </div>
                <div class="label">Events</div>
            </div>

            <div class="card">
                <div class="number">
                    {database_stats["alerts"]}
                </div>
                <div class="label">Alerts</div>
            </div>

        </div>

    </div>


    <div class="section">

        <h2>MESSAGE AUDIT</h2>

        <div class="cards">

            <div class="card">
                <div class="number">
                    {messages["total"]}
                </div>
                <div class="label">Total Messages</div>
            </div>

            <div class="card">
                <div class="number">
                    {messages["active"]}
                </div>
                <div class="label">Active</div>
            </div>

            <div class="card">
                <div class="number">
                    {messages["edited"]}
                </div>
                <div class="label">Edited</div>
            </div>

            <div class="card">
                <div class="number">
                    {messages["deleted"]}
                </div>
                <div class="label">Deleted</div>
            </div>

        </div>

    </div>


    <div class="section">

        <h2>SECURITY ALERTS</h2>

        <div class="cards">

            <div class="card">
                <div class="number">
                    {alerts["total"]}
                </div>
                <div class="label">Total</div>
            </div>

            <div class="card">
                <div class="number">
                    {alerts["critical"]}
                </div>
                <div class="label">Critical</div>
            </div>

            <div class="card">
                <div class="number">
                    {alerts["warning"]}
                </div>
                <div class="label">Warning</div>
            </div>

            <div class="card">
                <div class="number">
                    {alerts["info"]}
                </div>
                <div class="label">Informational</div>
            </div>

        </div>

    </div>


    <div class="section">

        <h2>MONITORING EVENTS</h2>

        <table>

            <thead>
                <tr>
                    <th>Event</th>
                    <th>Total</th>
                </tr>
            </thead>

            <tbody>

                <tr>
                    <td>Total Events</td>
                    <td>{events["total"]}</td>
                </tr>

                <tr>
                    <td>Messages Created</td>
                    <td>{events["messages_created"]}</td>
                </tr>

                <tr>
                    <td>Messages Edited</td>
                    <td>{events["messages_edited"]}</td>
                </tr>

                <tr>
                    <td>Messages Deleted</td>
                    <td>{events["messages_deleted"]}</td>
                </tr>

                <tr>
                    <td>Members Joined</td>
                    <td>{events["members_joined"]}</td>
                </tr>

                <tr>
                    <td>Members Left</td>
                    <td>{events["members_left"]}</td>
                </tr>

            </tbody>

        </table>

    </div>


    <div class="section">

        <h2>RECENT SECURITY ALERTS</h2>

        <table>

            <thead>

                <tr>
                    <th>Type</th>
                    <th>User</th>
                    <th>Message</th>
                    <th>Severity</th>
                    <th>Time</th>
                </tr>

            </thead>

            <tbody>

                {recent_alerts_html}

            </tbody>

        </table>

    </div>


    <div class="footer">

        MONITORIX SECURITY MONITORING PLATFORM<br>
        Automated audit report generated by Monitorix.

    </div>

</div>

</body>

</html>
"""

        report_file.write_text(
            html,
            encoding=settings.REPORT_ENCODING,
        )

        logger.info(
            "HTML report generated: %s",
            report_file,
        )

        return report_file


# ==============================================================
# GLOBAL INSTANCE
# ==============================================================

report_generator = ReportGenerator()


# ==============================================================
# EXPORTS
# ==============================================================

__all__ = [
    "ReportGenerator",
    "report_generator",
]
