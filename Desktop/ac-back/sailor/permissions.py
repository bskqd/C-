import rest_framework.exceptions
import rest_framework.status
from rest_framework import permissions

from agent.models import AgentSailor
from communication.models import SailorKeys
from sailor.statement.models import StatementETI, StatementAdvancedTraining
from user_profile.models import UserProfile


class CitizenPassportPermission(permissions.BasePermission):
    # гражданский паспорт

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sailor.readCitizenPassport')
        if request.method in ['POST']:
            return request.user.has_perm('sailor.writeCitizenPassportInfo')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('sailor.writeCitizenPassportInfo')
        if request.method in ['DELETE']:
            return request.user.has_perm('sailor.writeCitizenPassportInfo')
        return False


class SailorPassportPermission(permissions.BasePermission):
    # внесение информации по ПМ

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sailor.readSeafarerPassport')
        if request.method in ['POST']:
            return request.user.has_perm('sailor.createSeafarerPassport')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('sailor.writeSeafarerPassportStatus') or request.user.has_perm(
                'sailor.writeSeafarerPassport')
        if request.method in ['DELETE']:
            return request.user.has_perm('sailor.deleteSeafarerPassport')
        return False


class MainInfoPermission(permissions.BasePermission):
    # редактирование информации

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sailor.readMainInfo')
        if request.method in ['POST']:
            return request.user.has_perm('sailor.createSeafarer')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('sailor.writeMainInfo')
        if request.method in ['DELETE']:
            return request.user.has_perm('sailor.writeMainInfo')
        return False


class MainInfoTypeUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['POST'] or request.user.is_superuser:
            return True
        elif request.user.userprofile.type_user == request.user.userprofile.AGENT:
            agent_sailor_exist = AgentSailor.objects.filter(
                is_disable=False,
                sailor_key=obj._key,
                agent=request.user).exists()
            if not agent_sailor_exist:
                raise AgentForbidden
        elif request.user.userprofile.type_user == request.user.userprofile.ETI_EMPLOYEE:
            key = SailorKeys.objects.get(id=obj._key)
            if not StatementETI.objects.filter(id__in=key.statement_eti,
                                               institution=request.user.userprofile.eti_institution).exists():
                raise AgentForbidden
        return True


class CheckHeadAgentProfile(permissions.BasePermission):

    def check_relationship_head_agent_sailor(self, request, view, sailor_key):
        agent_sailor_exist = AgentSailor.objects.filter(
            is_disable=False,
            sailor_key=sailor_key,
            agent__userprofile__agent_group__in=request.user.userprofile.agent_group.all()).exists()
        return agent_sailor_exist

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['POST', 'PATCH', 'PUT']:
            return True
        sailor_key = obj._key
        return self.check_relationship_head_agent_sailor(request, view, sailor_key)


class CheckHeadAgentGroup(permissions.BasePermission):
    def allow_for_head(self, request, view, sailor_key):
        agent_sailor_exist = AgentSailor.objects.filter(
            is_disable=False,
            sailor_key=sailor_key,
            agent__userprofile__agent_group__in=request.user.userprofile.agent_group.all()).exists()
        return agent_sailor_exist

    def has_permission(self, request, view):
        if request.method in ['POST', 'PATCH', 'PUT']:
            return True
        sailor_key = view.kwargs.get('sailor_pk') or view.kwargs.get('pk')
        if not sailor_key or request.user.is_superuser:
            return True
        up: UserProfile = request.user.userprofile
        if (up.type_user in [up.HEAD_AGENT, up.SECRETARY_SERVICE] and
                not self.allow_for_head(request, view, sailor_key)):
            raise AgentForbidden
        return True


class SearchSailorPermission(permissions.BasePermission):
    # редактирование информации

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sailor.readMainInfo')
        if request.method in ['POST']:
            return request.user.has_perm('sailor.readMainInfo')
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('sailor.readMainInfo')
        if request.method in ['DELETE']:
            return request.user.has_perm('sailor.readMainInfo')
        return False


class AgentForbidden(rest_framework.exceptions.APIException):
    status_code = 418
    default_detail = "You do not have permission to perform this action"


class MaradForbidden(rest_framework.exceptions.APIException):
    status_code = 419
    default_detail = "You do not have permission to perform this action"


class CheckInProcessStatementDKK(permissions.BasePermission):
    """
    Может просматривать раздел "Заявки на дкк в процессе"
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('statement.readApplicationSQCProccess')
        return False


class CheckApprovStatementDKK(permissions.BasePermission):
    """
    Может просматривать раздел "Заявки на дкк схвалени"
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('statement.readApplicationSQCApproved')
        return False


class PostVerificationChangeStatusPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('sailor.writePostVerificationDocuments')
        return False


class RatingPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.has_perm('sailor.ratingSailor')


class CheckAgentPermission(permissions.BasePermission):

    def allow_for_agent(self, request, view, sailor_key):
        if AgentSailor.objects.filter(is_disable=False, sailor_key=sailor_key, agent=request.user).exists():
            return True
        return False

    def allow_for_eti_employee(self, request, view, sailor_key):
        sailor_key = SailorKeys.objects.get(id=sailor_key)
        return StatementETI.objects.filter(id__in=sailor_key.statement_eti,
                                           institution=request.user.userprofile.eti_institution)

    def allow_for_advanced_training(self, request, view, sailor_key):
        sailor_key = SailorKeys.objects.get(id=sailor_key)
        return StatementAdvancedTraining.objects.filter(
            id__in=sailor_key.statement_advanced_training,
            educational_institution=request.user.userprofile.education_institution)

    def has_permission(self, request, view):
        sailor_key = view.kwargs.get('sailor_pk') or view.kwargs.get('pk')
        if request.method in ['POST', 'PATCH', 'PUT'] or not sailor_key or request.user.is_superuser:
            return True
        up: UserProfile = request.user.userprofile if hasattr(request.user, 'userprofile') else None
        if up and up.type_user in [up.AGENT] and not self.allow_for_agent(request, view, sailor_key):
            raise AgentForbidden
        elif up and up.type_user in [up.MARAD] and not self.allow_for_agent(request, view, sailor_key):
            raise MaradForbidden
        elif up and up.type_user == up.ETI_EMPLOYEE and not self.allow_for_eti_employee(request, view, sailor_key):
            raise AgentForbidden
        elif up and up.type_user == up.SECRETARY_ATC and \
                not self.allow_for_advanced_training(request, view, sailor_key):
            raise AgentForbidden
        return True


class AgentInfoViewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('core.readAgentInfo')


class CommentForVerificationDocPermission(permissions.BasePermission):
    """
    Permissions to work with comments to documents in the verification status
    """

    def has_permission(self, request, view):
        if request.method in ['DELETE']:
            return request.user.has_perm('sailor.writeCommentForVerification')
        return True


class MergeSailorPermission(permissions.BasePermission):
    """
    Permissions to merger of sailors
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sailor.mergeSeafarer')
        elif request.method in ['POST']:
            return request.user.has_perm('sailor.mergeSeafarer')
        return False


class CreateNewSailorPassportPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('sailor.createNewSailorPassport')