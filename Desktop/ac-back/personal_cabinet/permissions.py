from rest_framework.permissions import BasePermission

from communication.models import SailorKeys
from sailor.statement.models import StatementSQC, StatementQualification


class IsDkkStatementOwnerOrAdmin(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        if request.method in ['POST', 'PUT']:
            return request.user.is_authenticated and \
                   SailorKeys.objects.get(user_id=request.user.id).pk == int(request.data.get('sailor', 0))
        if view.name == 'Cancel document':
            return request.user.is_authenticated
        if request.method in ['GET', 'DELETE']:
            try:
                return request.user.id == StatementSQC.objects.get(
                    id=request.parser_context['kwargs']['pk']
                ).author_id
            except Exception:
                return False
        return False


class IsDkkProtocolOwnerOrAdmin(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        if request.method in ['GET']:
            return True
        return False


class IsQualStatementOwnerOrAdmin(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        if request.method in ['POST', 'PUT']:
            return request.user.id and request.user.is_authenticated
        if request.method in ['GET', 'DELETE']:
            try:
                return request.user.id == StatementQualification.objects.get(
                    id=request.parser_context['kwargs']['pk']
                ).author_id
            except Exception:
                return False
        return False


# class IsPhotoOwner