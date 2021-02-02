from rest_framework import permissions


class StatementServiceRecordPermission(permissions.BasePermission):

    def is_marad(self, request):
        return request.user and hasattr(request.user, 'userprofile') and \
               request.user.userprofile.type_user == request.user.userprofile.MARAD

    def has_permission(self, request, view):
        if request.method in ['GET', 'POST', 'PUT', 'PATCH']:
            return request.user.has_perm('statement.writeApplicationRecordBook') or \
                   request.user.has_perm('statement.readApplicationRecordBook') or \
                   self.is_marad(request)
        return False


class ApplicationSQCPermission(permissions.BasePermission):
    # заявки на ДКК

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('statement.readApplicationSQC')
        if request.method in ['POST']:
            return request.user.has_perm('statement.createApplicationSQC')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('statement.writeApplicationSQCStatus') or \
                   request.user.has_perm('statement.writeApplicationSQCPayment') or \
                   request.user.has_perm('statement.writeApplicationSQCPreVerification') or \
                   request.user.has_perm('statement.writeApplicationSQCStatusRejected')
        if request.method in ['DELETE']:
            return request.user.has_perm('statement.deleteApplicationSQC')
        return False


class QualificationApplicationPermission(permissions.BasePermission):
    # заявки на квалификационные документы
    def is_marad(self, request):
        return request.user and hasattr(request.user, 'userprofile') and \
               request.user.userprofile.type_user == request.user.userprofile.MARAD

    def has_permission(self, request, view):

        if request.method in ['GET']:
            return request.user.has_perm('statement.readQualificationApplication')
        if request.method in ['POST']:
            return request.user.has_perm('statement.createQualificationApplication')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('statement.writeQualificationApplicationStatus') \
                   or request.user.has_perm('statement.writeQualificationApplication') or self.is_marad(request)
        if request.method in ['DELETE']:
            return request.user.has_perm('statement.deleteQualificationApplication')
        return False


class AdvancedTrainingPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['POST']:
            return request.user.has_perm('education.createGraduation') or \
                   request.user.has_perm('statement.createAdvancedTraining')
        return False
