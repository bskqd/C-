from rest_framework import permissions


class ExperienceNotConventionalPermission(permissions.BasePermission):
    # справка о стаже для неконвенционных профессий

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readExperienceNotConventional')
        if request.method in ['POST']:
            return request.user.has_perm('document.createExperienceNotConventional')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeExperienceNotConventionalStatus') or \
                   request.user.has_perm('document.writeExperienceNotConventional')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteExperience')
        return False


class GraduationDocumentPermission(permissions.BasePermission):
    # внесение информации по образовательным документам

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readGraduation')
        if request.method in ['POST']:
            return request.user.has_perm('document.createGraduation')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeGraduationStatus') or request.user.has_perm(
                'document.writeGraduation')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteGraduation')
        return False


class ProtocolSQCPermission(permissions.BasePermission):
    # простоколы ДКК

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readProtocolSQC')
        if request.method in ['POST']:
            return request.user.has_perm('document.createProtocolSQC')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeProtocolSQCStatus')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteProtocolSQC')
        return False


class CertificatesStatusPermission(permissions.BasePermission):
    # ссертификат НТЗ

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readCertificates') or request.user.has_perm(
                'document.addCertificatesETI')
        if request.method in ['POST']:
            return request.user.has_perm('document.writeCertificatesStatus') or request.user.has_perm(
                'document.addCertificatesETI')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeCertificatesStatus') or request.user.has_perm(
                'document.addCertificatesETI')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.writeCertificatesStatus')
        return False


class ServiceRecordSailorPermission(permissions.BasePermission):
    # послужная книжка моряка

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readRecordBook')
        if request.method in ['POST']:
            return request.user.has_perm('document.createNewRecordBook') or request.user.has_perm(
                'document.createExistRecordBook')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeRecordBookStatus') or request.user.has_perm(
                'document.writeRecordBook')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteRecordBook')
        return False


class ExistServiceRecordSailorPermission(permissions.BasePermission):
    # существующая послужная книжка моряка

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readRecordBook')
        if request.method in ['POST']:
            return request.user.has_perm('document.createExistRecordBook')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeRecordBookStatus') or request.user.has_perm(
                'document.writeRecordBook')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteRecordBook')
        return False


class LineInServiceRecordPermission(permissions.BasePermission):
    # запись в послужной книжке моряка

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readRecordBook')
        if request.method in ['POST']:
            return request.user.has_perm('document.createRecordBookEntry')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeRecordBookEntryStatus') or request.user.has_perm(
                'document.writeRecordBookEntry') or \
                   request.user.has_perm('document.writeExperiencePreVerificationStatus')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteRecordBookEntry')
        return False


class MedicalCertificatePermission(permissions.BasePermission):
    # внесение информации по мед. свидетельствам

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readMedical')
        if request.method in ['POST']:
            return request.user.has_perm('document.createMedical')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeMedicalStatus') or request.user.has_perm(
                'document.writeMedical')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteMedical')
        return False


class QualificationStatusPermission(permissions.BasePermission):
    # квалификационные документы

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readQualification')
        if request.method in ['POST']:
            return request.user.has_perm('document.createQualification') or \
                   request.user.has_perm('document.createExistsQualification')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeQualificationStatus') or request.user.has_perm(
                'document.writeQualification') or \
                   request.user.has_perm('document.writeQualificationPreVerification') or \
                   request.user.has_perm('document.writeQualificationPreVerificationStatus')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteQualification')
        return False


class ExperiencePermission(permissions.BasePermission):
    # справка о стаже

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('document.readExperience')
        if request.method in ['POST']:
            return request.user.has_perm('document.createExperience')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('document.writeExperienceStatus') or request.user.has_perm(
                'document.writeExperience') or request.user.has_perm('document.writeExperiencePreVerificationStatus')
        if request.method in ['DELETE']:
            return request.user.has_perm('document.deleteExperience')
        return False
