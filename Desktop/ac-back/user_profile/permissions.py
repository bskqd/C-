from rest_framework import permissions


class IsLoggedInUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff



class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('auth.view_user')
        if request.method in ['POST']:
            return request.user.has_perm('auth.add_user')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('auth.change_user')
        if request.method in ['DELETE']:
            return request.user.has_perm('auth.delete_user')
        return False


class GroupPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('auth.view_group')
        if request.method in ['POST']:
            return request.user.has_perm('auth.add_group')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('auth.change_group')
        if request.method in ['DELETE']:
            return request.user.has_perm('auth.delete_group')
        return False
