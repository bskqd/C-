from rest_framework import permissions


class IsLoggedInUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff


class GenerateServiceRecordBookPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('view_all_documents_applications_protocols')
        if request.method in ['POST']:
            return request.user.has_perm('registration_PKM')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('change_exist_PKM')
        if request.method in ['DELETE']:
            return request.user.has_perm('change_exist_PKM')
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET']:
            return request.user.has_perm('view_all_documents_applications_protocols', obj)
        if request.method in ['POST']:
            return request.user.has_perm('registration_PKM', obj)
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('change_exist_PKM', obj)
        if request.method in ['DELETE']:
            return request.user.has_perm('change_exist_PKM', obj)
        return False
