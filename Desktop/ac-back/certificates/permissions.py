from rest_framework.permissions import BasePermission


class IntegrationNTZPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'PATCH', 'POST', 'PUT']:
            return request.user.has_perm('directory.ETICertificationIntegration')
        return False
