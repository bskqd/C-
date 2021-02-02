from rest_framework import permissions


class PermissionStudentsID(permissions.BasePermission):
    """
    Права для студентческого билета кадета
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('cadets.readStudentsID')
        if request.method in ['POST']:
            return request.user.has_perm('cadets.createStudentsID')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('cadets.writeStudentsID') or request.user.has_perm(
                'cadets.writeStudentsIDStatus')
        if request.method in ['DELETE']:
            return request.user.has_perm('cadets.deleteStudentsID')
        return False
