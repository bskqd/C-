from rest_framework import permissions


class IsAgentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        userprofile = request.user.userprofile
        return request.user.is_superuser or request.user.userprofile.type_user in [userprofile.AGENT]


class IsAgentOrSecretaryOrHeadUser(permissions.BasePermission):
    def has_permission(self, request, view):
        userprofile = request.user.userprofile
        return request.user.is_superuser or request.user.userprofile.type_user in [userprofile.SECRETARY_SERVICE,
                                                                                   userprofile.AGENT,
                                                                                   userprofile.HEAD_AGENT,
                                                                                   userprofile.MARAD]


class IsBackOfficeUser(permissions.BasePermission):
    def has_permission(self, request, view):
        userprofile = request.user.userprofile
        return request.user.is_superuser or userprofile.type_user == userprofile.BACK_OFFICE


class IsPersonalCabinetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.username.startswith(('key_', '+380')) and not hasattr(request.user, 'userprofile')
