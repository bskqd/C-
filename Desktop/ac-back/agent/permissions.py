from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()

class StatementForAgentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('agent.readAgentApplication')
        if request.method in ['PATCH', 'PUT']:
            return request.user.has_perm('agent.writeAgentApplication')
        if request.method in ['POST']:
            return True
        return False


class IsHeadGroupsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        user: User = request.user
        if not hasattr(user, 'userprofile') and not request.user.is_superuser:
            return False
        return request.user.is_superuser or (user.userprofile.type_user == user.userprofile.HEAD_AGENT)


class IsSecretaryAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        user: User = request.user
        if not hasattr(user, 'userprofile') and not request.user.is_superuser:
            return False
        return request.user.is_superuser or (user.userprofile.type_user == user.userprofile.SECRETARY_SERVICE)


class IsAgentInAgentGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.userprofile.type_user == request.user.userprofile.AGENT
