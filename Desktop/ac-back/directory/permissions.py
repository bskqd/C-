from rest_framework.permissions import IsAdminUser


class IsSuperUserEdit(IsAdminUser):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user and request.user.is_superuser
        elif request.method in ['GET']:
            return bool(request.user and request.user.is_authenticated)
