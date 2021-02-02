from rest_framework import permissions


class IsASUser(permissions.BasePermission):
    """
    Пользователь АС
    """

    def has_permission(self, request, view):
        user = request.user
        try:
            if user.userprofile.main_group.exists() or user.is_superuser:
                return True
        except AttributeError:
            return False


class PermissionStatementVerification(permissions.BasePermission):
    """
    Заявления на доступ в личный кабинет
    """
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sms_auth.writeCheckDocuments')
        if request.method in ['POST']:
            return request.user.has_perm('sms_auth.writeCheckDocuments')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('sms_auth.writeCheckDocuments')
        if request.method in ['DELETE']:
            return request.user.has_perm('sms_auth.writeCheckDocuments')
        return False
