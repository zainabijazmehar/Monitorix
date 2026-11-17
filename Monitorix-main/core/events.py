"""
Monitorix
Module: core.events
Author: Zainab

Description:
Central Discord event processing engine.

Responsibilities:
- Process Discord events
- Store audit events
- Track message activity
- Track edited and deleted messages
- Track member activity
- Track channels and roles
- Track webhooks
- Generate security events
- Trigger security alerts
- Maintain member activity timestamps
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from database.database import database
from services.alerts import alert_engine
from services.logger import logger


class EventManager:
    """
    Central event manager for Monitorix.

    This class converts Discord events into persistent
    Monitorix audit/security records.
    """

    def __init__(self) -> None:
        logger.info("Event manager initialized.")

    # ==============================================================
    # MESSAGE EVENTS
    # ==============================================================

    def message_created(
        self,
        message: Any,
    ) -> None:
        """
        Store a newly created Discord message.
        """

        try:
            guild_id = self.guild_id(message)

            if not guild_id:
                logger.warning(
                    "Ignoring message without guild: %s",
                    getattr(message, "id", "unknown"),
                )
                return

            user_id = str(message.author.id)
            channel_id = str(message.channel.id)
            message_id = str(message.id)
            timestamp = self.timestamp()

            # ------------------------------------------------------
            # Ensure server exists
            # ------------------------------------------------------

            self.ensure_server(message.guild)

            # ------------------------------------------------------
            # Store / update member
            # ------------------------------------------------------

            self.upsert_member(
                member=message.author,
                guild_id=guild_id,
                activity_time=timestamp,
            )

            # ------------------------------------------------------
            # Store channel
            # ------------------------------------------------------

            self.upsert_channel(
                channel=message.channel,
                guild_id=guild_id,
            )

            # ------------------------------------------------------
            # Store message
            # ------------------------------------------------------

            database.insert(
                "messages",
                {
                    "guild_id": guild_id,
                    "message_id": message_id,
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "content": message.content,
                    "created_at": timestamp,
                    "edited": 0,
                    "deleted": 0,
                    "edit_count": 0,
                },
            )

            # ------------------------------------------------------
            # Store audit event
            # ------------------------------------------------------

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "MESSAGE_CREATED",
                    "user_id": user_id,
                    "target_id": message_id,
                    "channel_id": channel_id,
                    "details": message.content,
                    "severity": "INFO",
                    "risk_score": 0,
                    "created_at": timestamp,
                },
            )

            logger.info(
                "Message stored | guild=%s user=%s channel=%s message=%s",
                guild_id,
                user_id,
                channel_id,
                message_id,
            )

        except Exception as error:
            logger.exception(
                "Message creation failed: %s",
                error,
            )

    # ==============================================================

    def message_edited(
        self,
        before: Any,
        after: Any,
    ) -> None:
        """
        Track an edited message.

        The original message remains in the database while
        the latest content is stored in the message record.
        """

        try:
            guild_id = self.guild_id(after)

            if not guild_id:
                return

            message_id = str(after.id)
            user_id = str(after.author.id)
            channel_id = str(after.channel.id)
            timestamp = self.timestamp()

            existing = database.fetch_one(
                """
                SELECT edit_count
                FROM messages
                WHERE guild_id=?
                AND message_id=?
                """,
                (
                    guild_id,
                    message_id,
                ),
            )

            current_edit_count = (
                int(existing["edit_count"])
                if existing
                else 0
            )

            database.update(
                "messages",
                {
                    "content": after.content,
                    "edited": 1,
                    "edited_at": timestamp,
                    "edit_count": current_edit_count + 1,
                },
                "guild_id=? AND message_id=?",
                (
                    guild_id,
                    message_id,
                ),
            )

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "MESSAGE_EDITED",
                    "user_id": user_id,
                    "target_id": message_id,
                    "channel_id": channel_id,
                    "details": (
                        f"Before: {getattr(before, 'content', '')}\n"
                        f"After: {after.content}"
                    ),
                    "severity": "INFO",
                    "risk_score": 1,
                    "created_at": timestamp,
                },
            )

            self.upsert_member(
                member=after.author,
                guild_id=guild_id,
                activity_time=timestamp,
            )

            logger.info(
                "Message edited | guild=%s message=%s",
                guild_id,
                message_id,
            )

        except Exception as error:
            logger.exception(
                "Message edit failed: %s",
                error,
            )

    # ==============================================================

    def message_deleted(
        self,
        message: Any,
    ) -> None:
        """
        Track a deleted message.

        Deleted message content remains in the database for
        audit purposes rather than being permanently removed.
        """

        try:
            guild_id = self.guild_id(message)

            if not guild_id:
                return

            message_id = str(message.id)
            user_id = str(message.author.id)
            channel_id = str(message.channel.id)
            timestamp = self.timestamp()

            database.update(
                "messages",
                {
                    "deleted": 1,
                    "deleted_at": timestamp,
                },
                "guild_id=? AND message_id=?",
                (
                    guild_id,
                    message_id,
                ),
            )

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "MESSAGE_DELETED",
                    "user_id": user_id,
                    "target_id": message_id,
                    "channel_id": channel_id,
                    "details": message.content,
                    "severity": "WARNING",
                    "risk_score": 2,
                    "created_at": timestamp,
                },
            )

            # ------------------------------------------------------
            # Security alert
            # ------------------------------------------------------

            alert_engine.create_alert(
                alert_type="MESSAGE_DELETED",
                message=(
                    f"Message deleted in "
                    f"#{getattr(message.channel, 'name', 'unknown')}"
                ),
                severity="WARNING",
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                risk_score=2,
            )

            logger.info(
                "Message deleted | guild=%s message=%s",
                guild_id,
                message_id,
            )

        except Exception as error:
            logger.exception(
                "Message deletion failed: %s",
                error,
            )

    # ==============================================================
    # MEMBER EVENTS
    # ==============================================================

    def member_join(
        self,
        member: Any,
    ) -> None:
        """
        Track a member joining a Discord server.
        """

        try:
            guild_id = self.guild_id(member)

            if not guild_id:
                return

            timestamp = self.timestamp()
            user_id = str(member.id)

            self.ensure_server(member.guild)

            self.upsert_member(
                member=member,
                guild_id=guild_id,
                activity_time=timestamp,
            )

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "MEMBER_JOINED",
                    "user_id": user_id,
                    "target_id": user_id,
                    "details": (
                        f"Member joined: "
                        f"{getattr(member, 'display_name', member.name)}"
                    ),
                    "severity": "INFO",
                    "risk_score": 0,
                    "created_at": timestamp,
                },
            )

            logger.info(
                "Member joined | guild=%s user=%s",
                guild_id,
                user_id,
            )

        except Exception as error:
            logger.exception(
                "Member join failed: %s",
                error,
            )

    # ==============================================================

    def member_leave(
        self,
        member: Any,
    ) -> None:
        """
        Track a member leaving a Discord server.
        """

        try:
            guild_id = self.guild_id(member)

            if not guild_id:
                return

            timestamp = self.timestamp()
            user_id = str(member.id)

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "MEMBER_LEFT",
                    "user_id": user_id,
                    "target_id": user_id,
                    "details": (
                        f"Member left: "
                        f"{getattr(member, 'display_name', member.name)}"
                    ),
                    "severity": "INFO",
                    "risk_score": 0,
                    "created_at": timestamp,
                },
            )

            logger.info(
                "Member left | guild=%s user=%s",
                guild_id,
                user_id,
            )

        except Exception as error:
            logger.exception(
                "Member leave failed: %s",
                error,
            )

    # ==============================================================
    # CHANNEL EVENTS
    # ==============================================================

    def channel_created(
        self,
        channel: Any,
    ) -> None:
        """
        Track a newly created Discord channel.
        """

        try:
            guild_id = self.guild_id(channel)

            if not guild_id:
                return

            timestamp = self.timestamp()

            self.ensure_server(channel.guild)

            self.upsert_channel(
                channel=channel,
                guild_id=guild_id,
            )

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "CHANNEL_CREATED",
                    "user_id": None,
                    "target_id": str(channel.id),
                    "channel_id": str(channel.id),
                    "details": (
                        f"Channel created: "
                        f"#{getattr(channel, 'name', 'unknown')}"
                    ),
                    "severity": "INFO",
                    "risk_score": 3,
                    "created_at": timestamp,
                },
            )

        except Exception as error:
            logger.exception(
                "Channel creation failed: %s",
                error,
            )

    # ==============================================================

    def channel_deleted(
        self,
        channel: Any,
    ) -> None:
        """
        Track a deleted Discord channel.
        """

        try:
            guild_id = self.guild_id(channel)

            if not guild_id:
                return

            timestamp = self.timestamp()

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "CHANNEL_DELETED",
                    "user_id": None,
                    "target_id": str(channel.id),
                    "channel_id": str(channel.id),
                    "details": (
                        f"Channel deleted: "
                        f"#{getattr(channel, 'name', 'unknown')}"
                    ),
                    "severity": "WARNING",
                    "risk_score": 10,
                    "created_at": timestamp,
                },
            )

        except Exception as error:
            logger.exception(
                "Channel deletion failed: %s",
                error,
            )

    # ==============================================================
    # ROLE EVENTS
    # ==============================================================

    def role_created(
        self,
        role: Any,
    ) -> None:
        """
        Track a newly created Discord role.
        """

        try:
            guild_id = self.guild_id(role)

            if not guild_id:
                return

            timestamp = self.timestamp()

            self.upsert_role(
                role=role,
                guild_id=guild_id,
            )

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "ROLE_CREATED",
                    "user_id": None,
                    "target_id": str(role.id),
                    "details": (
                        f"Role created: "
                        f"{getattr(role, 'name', 'unknown')}"
                    ),
                    "severity": "INFO",
                    "risk_score": 5,
                    "created_at": timestamp,
                },
            )

        except Exception as error:
            logger.exception(
                "Role creation failed: %s",
                error,
            )

    # ==============================================================

    def role_updated(
        self,
        before: Any,
        after: Any,
    ) -> None:
        """
        Track role changes and permission changes.
        """

        try:
            guild_id = self.guild_id(after)

            if not guild_id:
                return

            timestamp = self.timestamp()

            self.upsert_role(
                role=after,
                guild_id=guild_id,
            )

            before_permissions = str(
                getattr(
                    getattr(before, "permissions", None),
                    "value",
                    "",
                )
            )

            after_permissions = str(
                getattr(
                    getattr(after, "permissions", None),
                    "value",
                    "",
                )
            )

            permission_changed = (
                before_permissions != after_permissions
            )

            severity = (
                "HIGH"
                if permission_changed
                else "INFO"
            )

            risk_score = (
                20
                if permission_changed
                else 5
            )

            details = (
                f"Role: {getattr(after, 'name', 'unknown')}\n"
                f"Permissions changed: {permission_changed}\n"
                f"Before: {before_permissions}\n"
                f"After: {after_permissions}"
            )

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "ROLE_UPDATED",
                    "user_id": None,
                    "target_id": str(after.id),
                    "details": details,
                    "severity": severity,
                    "risk_score": risk_score,
                    "created_at": timestamp,
                },
            )

            if permission_changed:
                alert_engine.create_alert(
                    alert_type="ROLE_PERMISSION_CHANGED",
                    message=(
                        f"Permissions changed for role "
                        f"'{getattr(after, 'name', 'unknown')}'"
                    ),
                    severity="HIGH",
                    user_id=None,
                    guild_id=guild_id,
                    target_id=str(after.id),
                    risk_score=risk_score,
                )

        except Exception as error:
            logger.exception(
                "Role update failed: %s",
                error,
            )

    # ==============================================================
    # WEBHOOK EVENTS
    # ==============================================================

    def webhook_created(
        self,
        webhook: Any,
    ) -> None:
        """
        Track webhook creation.
        """

        try:
            guild_id = self.guild_id(webhook)

            if not guild_id:
                return

            timestamp = self.timestamp()

            database.insert(
                "webhooks",
                {
                    "guild_id": guild_id,
                    "webhook_id": str(webhook.id),
                    "name": getattr(
                        webhook,
                        "name",
                        None,
                    ),
                    "channel_id": (
                        str(webhook.channel_id)
                        if getattr(
                            webhook,
                            "channel_id",
                            None,
                        )
                        else None
                    ),
                    "creator_id": (
                        str(webhook.user.id)
                        if getattr(
                            webhook,
                            "user",
                            None,
                        )
                        else None
                    ),
                    "status": "ACTIVE",
                    "created_at": timestamp,
                },
            )

            database.insert(
                "events",
                {
                    "guild_id": guild_id,
                    "event_type": "WEBHOOK_CREATED",
                    "user_id": (
                        str(webhook.user.id)
                        if getattr(
                            webhook,
                            "user",
                            None,
                        )
                        else None
                    ),
                    "target_id": str(webhook.id),
                    "details": (
                        f"Webhook created: "
                        f"{getattr(webhook, 'name', 'unknown')}"
                    ),
                    "severity": "HIGH",
                    "risk_score": 15,
                    "created_at": timestamp,
                },
            )

            alert_engine.create_alert(
                alert_type="WEBHOOK_CREATED",
                message=(
                    f"Webhook created: "
                    f"{getattr(webhook, 'name', 'unknown')}"
                ),
                severity="HIGH",
                user_id=(
                    str(webhook.user.id)
                    if getattr(
                        webhook,
                        "user",
                        None,
                    )
                    else None
                ),
                guild_id=guild_id,
                target_id=str(webhook.id),
                risk_score=15,
            )

        except Exception as error:
            logger.exception(
                "Webhook creation failed: %s",
                error,
            )

    # ==============================================================
    # HELPERS
    # ==============================================================

    @staticmethod
    def timestamp() -> str:
        """
        Return the current UTC timestamp.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()

    # ==============================================================

    @staticmethod
    def guild_id(
        obj: Any,
    ) -> str | None:
        """
        Safely extract Discord guild ID from an object.
        """

        guild = getattr(
            obj,
            "guild",
            None,
        )

        if guild is None:
            return None

        guild_id = getattr(
            guild,
            "id",
            None,
        )

        return (
            str(guild_id)
            if guild_id is not None
            else None
        )

    # ==============================================================

    def ensure_server(
        self,
        guild: Any,
    ) -> None:
        """
        Create or update the monitored Discord server record.
        """

        if guild is None:
            return

        guild_id = str(guild.id)
        name = getattr(
            guild,
            "name",
            "Unknown Server",
        )

        owner_id = getattr(
            guild,
            "owner_id",
            None,
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM servers
            WHERE server_id=?
            """,
            (guild_id,),
        )

        timestamp = self.timestamp()

        if existing:
            database.update(
                "servers",
                {
                    "name": name,
                    "owner_id": (
                        str(owner_id)
                        if owner_id is not None
                        else None
                    ),
                    "updated_at": timestamp,
                },
                "server_id=?",
                (guild_id,),
            )

        else:
            database.insert(
                "servers",
                {
                    "server_id": guild_id,
                    "name": name,
                    "owner_id": (
                        str(owner_id)
                        if owner_id is not None
                        else None
                    ),
                    "created_at": timestamp,
                    "updated_at": timestamp,
                },
            )

    # ==============================================================

    def upsert_member(
        self,
        member: Any,
        guild_id: str,
        activity_time: str | None = None,
    ) -> None:
        """
        Insert or update a Discord member.
        """

        user_id = str(member.id)

        username = getattr(
            member,
            "name",
            "Unknown",
        )

        display_name = getattr(
            member,
            "display_name",
            username,
        )

        timestamp = (
            activity_time
            or self.timestamp()
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM members
            WHERE guild_id=?
            AND user_id=?
            """,
            (
                guild_id,
                user_id,
            ),
        )

        if existing:

            database.update(
                "members",
                {
                    "username": username,
                    "display_name": display_name,
                    "status": str(
                        getattr(
                            member,
                            "status",
                            "unknown",
                        )
                    ),
                    "last_activity": timestamp,
                    "updated_at": timestamp,
                },
                "guild_id=? AND user_id=?",
                (
                    guild_id,
                    user_id,
                ),
            )

        else:

            joined_at = getattr(
                member,
                "joined_at",
                None,
            )

            database.insert(
                "members",
                {
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "username": username,
                    "display_name": display_name,
                    "status": str(
                        getattr(
                            member,
                            "status",
                            "unknown",
                        )
                    ),
                    "joined_at": (
                        joined_at.isoformat()
                        if joined_at
                        else timestamp
                    ),
                    "last_activity": timestamp,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                },
            )

    # ==============================================================

    def upsert_channel(
        self,
        channel: Any,
        guild_id: str,
    ) -> None:
        """
        Insert or update a Discord channel.
        """

        channel_id = str(channel.id)

        name = getattr(
            channel,
            "name",
            "unknown",
        )

        channel_type = str(
            getattr(
                channel,
                "type",
                "unknown",
            )
        )

        existing = database.fetch_one(
            """
            SELECT id
            FROM channels
            WHERE guild_id=?
            AND channel_id=?
            """,
            (
                guild_id,
                channel_id,
            ),
        )

        timestamp = self.timestamp()

        if existing:

            database.update(
                "channels",
                {
                    "name": name,
                    "channel_type": channel_type,
                    "updated_at": timestamp,
                },
                "guild_id=? AND channel_id=?",
                (
                    guild_id,
                    channel_id,
                ),
            )

        else:

            database.insert(
                "channels",
                {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "name": name,
                    "channel_type": channel_type,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                },
            )

    # ==============================================================

    def upsert_role(
        self,
        role: Any,
        guild_id: str,
    ) -> None:
        """
        Insert or update a Discord role and its permissions.
        """

        role_id = str(role.id)

        name = getattr(
            role,
            "name",
            "unknown",
        )

        permissions = getattr(
            role,
            "permissions",
            None,
        )

        permission_value = (
            str(
                getattr(
                    permissions,
                    "value",
                    "",
                )
            )
            if permissions
            else ""
        )

        position = int(
            getattr(
                role,
                "position",
                0,
            )
        )

        managed = int(
            bool(
                getattr(
                    role,
                    "managed",
                    False,
                )
            )
        )

        timestamp = self.timestamp()

        existing = database.fetch_one(
            """
            SELECT id
            FROM roles
            WHERE guild_id=?
            AND role_id=?
            """,
            (
                guild_id,
                role_id,
            ),
        )

        if existing:

            database.update(
                "roles",
                {
                    "name": name,
                    "permissions": permission_value,
                    "position": position,
                    "managed": managed,
                    "updated_at": timestamp,
                },
                "guild_id=? AND role_id=?",
                (
                    guild_id,
                    role_id,
                ),
            )

        else:

            database.insert(
                "roles",
                {
                    "guild_id": guild_id,
                    "role_id": role_id,
                    "name": name,
                    "permissions": permission_value,
                    "position": position,
                    "managed": managed,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                },
            )


# ==============================================================
# Global Event Manager
# ==============================================================

event_manager = EventManager()
