from rest_framework import permissions


class PacketPermission(permissions.BasePermission):
    """
    Права для заяваления на должность
    """
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('back_office.readPacketService')
        if request.method in ['POST']:
            return request.user.has_perm('back_office.createPacketService') \
                   or request.user.has_perm('back_office.readPacketPreview')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('back_office.writePacketService')
        if request.method in ['DELETE']:
            return request.user.has_perm('back_office.deletePacketService')
        return False


class PriceForPositionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('back_office.readPriceForPosition')
        if request.method in ['POST']:
            return request.user.has_perm('back_office.writePriceForPosition')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('back_office.writePriceForPosition')
        if request.method in ['DELETE']:
            return request.user.has_perm('back_office.writePriceForPosition')
        return False


class PriceForCoursePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('back_office.readPriceForPosition')
        if request.method in ['POST']:
            return request.user.has_perm('back_office.writePriceForPosition')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('back_office.writePriceForPosition')
        if request.method in ['DELETE']:
            return request.user.has_perm('back_office.writePriceForPosition')
        return False


class ETIProfitPartPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('back_office.readETIProfitPart')
        if request.method in ['POST']:
            return request.user.has_perm('back_office.writeETIProfitPart')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('back_office.writeETIProfitPart')
        if request.method in ['DELETE']:
            return request.user.has_perm('back_office.writeETIProfitPart')
        return False


class MergeDocumentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('document.merge_education_documents') or \
               request.user.has_perm('document.merge_qualification_documents')
