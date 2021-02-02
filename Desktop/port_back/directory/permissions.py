from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.models import User


class IsSuperUserOrReadOnly(BasePermission):
    """
    The request is superuser as a user, or is a read-only request.
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_superuser
        )


class AgencyPermission(BasePermission):
    """
    Permission to work with the agency.
    """
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return True
        elif request.method in ['POST']:
            return bool(request.user and request.user.type_user in [User.MARAD_CH, User.ADMIN_CH])
        elif request.method in ['PUT', 'PATCH']:
            return bool(request.user and request.user.type_user in [User.MARAD_CH, User.ADMIN_CH, User.HEAD_AGENCY_CH])
        elif request.method in ['DELETE']:
            return bool(request.user and request.user.type_user in [User.MARAD_CH, User.ADMIN_CH])
        return False
