from rest_framework import permissions


class ReportProtocolSQCPermission(permissions.BasePermission):
    # просмотр отчета по протоколам ДКК
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.reportProtocolSQC')
        return False


class ReportStatementSQCPermission(permissions.BasePermission):
    # просмотр отчета по заявлениям ДКК
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('statement.readReportApplicationSQC') or \
                   request.user.has_perm('statement.readApplicationSQCCreatedFromPA') or \
                   request.user.has_perm('statement.readApplicationSQCApproved')
        return False


class ReportNTZPermission(permissions.BasePermission):
    # просмотр отчета по НТЗ
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readCertificatesReport')
        return False


class ReportQualificationDocumentPermission(permissions.BasePermission):
    # просмотр отчета по квалификационным документам
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readReportQualificationDocument')
        return False


class ReportEducationDocumentPermission(permissions.BasePermission):
    # просмотр отчета по образовательным документам
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readGraduationReport')
        return False


class ReportListOfFilesPermission(permissions.BasePermission):
    # просмотр списка отчетов сформированных в xlsx файлы
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('reports.readReportListOfFiles')
        return False


class StatementQualDocFromPacketPermission(permissions.BasePermission):
    """
    List of statements qualification documents created from packets
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('reports.readListApplicationFromPacket')
        return False


class ReportStatementETIPermission(permissions.BasePermission):
    """
    List of statements ETI
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('statement.readReportApplicationETI')
        return False


class PaymentsStatementETIPermission(permissions.BasePermission):
    """
    Permission to view information on payment of statements ETI
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('statement.readPaymentsETI')
        return False


class PaymentsBranchOfficePermission(permissions.BasePermission):
    """
    Permission to view information on payment of service center
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('back_office.readPaymentsSC')
        return False


class ReportStatementAdvTrainingPermission(permissions.BasePermission):
    """
    List of statements advanced training
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('statement.readReportApplicationATC')
        return False


class ReportSailorPassportPermission(permissions.BasePermission):
    """
    List of sailor passport
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sailor.readReportSailorPassport')
        return False
