from rest_framework import permissions

from core.models import User


class SentInvitePermissions(permissions.BasePermission):
    """
    Permission for users who can send invitations to agents.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.type_user == User.ADMIN_CH or
                                      request.user.type_user == User.HEAD_AGENCY_CH or
                                      request.user.has_perm('authorization.agent_admin_agency')))
