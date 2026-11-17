"""
Monitorix
Module: utils.permissions
Author: Zainab

Description:
Permission handling utilities for Monitorix.

Responsibilities:
- Manage Discord permission checks
- Validate administrative access
- Provide reusable permission helpers
"""

from __future__ import annotations

from typing import Any

from services.logger import logger


class PermissionManager:
    """
    Central permission management service.

    Used to verify user permissions before
    performing sensitive monitoring actions.
    """

    # Discord administrative permissions
    ADMIN_PERMISSIONS = {
        "administrator",
        "manage_guild",
        "manage_channels",
        "manage_roles",
        "manage_webhooks",
        "view_audit_log",
    }

    # ------------------------------------------------------------------

    def has_permission(
        self,
        member: Any,
        permission: str,
    ) -> bool:
        """
        Check whether a Discord member has permission.

        Args:
            member:
                Discord member object.

            permission:
                Permission name.

        Returns:
            True if permission exists.
        """

        if member is None:
            return False

        permissions = getattr(
            member,
            "guild_permissions",
            None,
        )

        if permissions is None:
            return False

        return bool(
            getattr(
                permissions,
                permission,
                False,
            )
        )

    # ------------------------------------------------------------------

    def is_admin(
        self,
        member: Any,
    ) -> bool:
        """
        Check administrative privileges.

        Args:
            member:
                Discord member object.

        Returns:
            True if member is administrator.
        """

        if member is None:
            return False

        permissions = getattr(
            member,
            "guild_permissions",
            None,
        )

        if permissions is None:
            return False

        if getattr(
            permissions,
            "administrator",
            False,
        ):
            return True

        return self.has_any_permission(
            member,
            self.ADMIN_PERMISSIONS,
        )

    # ------------------------------------------------------------------

    def has_any_permission(
        self,
        member: Any,
        permissions: set[str],
    ) -> bool:
        """
        Check if member has at least one permission.

        Args:
            member:
                Discord member object.

            permissions:
                Permission collection.

        Returns:
            True if any permission matches.
        """

        for permission in permissions:

            if self.has_permission(
                member,
                permission,
            ):
                return True

        return False

    # ------------------------------------------------------------------

    def has_all_permissions(
        self,
        member: Any,
        permissions: set[str],
    ) -> bool:
        """
        Check if member has all required permissions.

        Args:
            member:
                Discord member object.

            permissions:
                Required permissions.

        Returns:
            True if all permissions exist.
        """

        for permission in permissions:

            if not self.has_permission(
                member,
                permission,
            ):
                return False

        return True

    # ------------------------------------------------------------------

    def can_manage_member(
        self,
        executor: Any,
        target: Any,
    ) -> bool:
        """
        Check whether executor can manage target member.

        Discord hierarchy rules are respected.
        """

        if not self.is_admin(executor):
            return False

        if target is None:
            return False

        executor_role = getattr(
            executor,
            "top_role",
            None,
        )

        target_role = getattr(
            target,
            "top_role",
            None,
        )

        if not executor_role or not target_role:
            return True

        return executor_role.position > target_role.position

    # ------------------------------------------------------------------

    def get_permission_summary(
        self,
        member: Any,
    ) -> list[str]:
        """
        Return available important permissions.

        Args:
            member:
                Discord member object.

        Returns:
            List of permissions.
        """

        available: list[str] = []

        for permission in self.ADMIN_PERMISSIONS:

            if self.has_permission(
                member,
                permission,
            ):
                available.append(
                    permission
                )

        logger.debug(
            "Permission summary generated"
        )

        return sorted(
            available
        )


# ----------------------------------------------------------------------
# Global Permission Instance
# ----------------------------------------------------------------------

permission_manager = PermissionManager()