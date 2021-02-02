from rest_framework import permissions

from core.models import User


class IsUserMarad(permissions.BasePermission):
    """
    Allows access only to user marad.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.type_user == User.MARAD_CH)


class IsHarborMaster(permissions.BasePermission):
    """
    Allows access only to harbor master.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.type_user == User.HARBOR_MASTER_CH)


class IsHarborWorker(permissions.BasePermission):
    """
    Allows access only to harbor worker.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.type_user == User.HARBOR_WORKER_CH)


class IsHeadAgency(permissions.BasePermission):
    """
    Allows access only to head agency.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.type_user == User.HEAD_AGENCY_CH)


class IsAgent(permissions.BasePermission):
    """
    Allows access only to agent.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.type_user == User.AGENT_CH)


class UserPortPermission(permissions.BasePermission):
    """
    Permission to work with the user
    """
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return True
        elif request.method in ['POST']:
            return bool(request.user and request.user.type_user in [User.MARAD_CH, User.ADMIN_CH, User.HEAD_AGENCY_CH,
                                                                    User.HARBOR_MASTER_CH])
        elif request.method in ['PUT', 'PATCH']:
            return bool(request.user and (request.user.type_user in [User.MARAD_CH, User.ADMIN_CH, User.HEAD_AGENCY_CH] or
                                          request.user.has_perm('authorization.agent_admin_agency')))
        elif request.method in ['DELETE']:
            return bool(request.user and request.user.type_user in [User.ADMIN_CH])
        return False

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.type_user == User.MARAD_CH and obj.type_user in [User.AGENT_CH, User.HEAD_AGENCY_CH]:
            return False
        return True
