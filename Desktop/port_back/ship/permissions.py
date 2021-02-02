from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from rest_framework import permissions, exceptions

import port_back.constants
from core.models import User
from ship.models import ShipAgentNomination


class AgentForbidden(exceptions.APIException):
    status_code = 423
    default_detail = "You do not have permission to perform this action"


class CheckAgentNominations:
    """
    Check agent nominations
    """
    def check_agent_nominations(self, ship_key, user) -> bool:
        nominations = ShipAgentNomination.objects.filter(
            Q(ship_key=ship_key) &
            Q(status_document_id=port_back.constants.ISSUED) &
            Q(date_verification__gte=datetime.now() - relativedelta(
                months=port_back.constants.VALID_NOMINATION_MONTHS)) &
            (Q(agent__agent__agency=user.get_agency) | Q(agent__head_agency__agency=user.get_agency)))
        if nominations.exists():
            return True
        return False


class AgentNominationPermissions(permissions.BasePermission):
    """
    Permission for statement for provision of interests of the ship
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return bool(request.user and request.user.type_user in
                        [User.ADMIN_CH, User.AGENT_CH, User.HARBOR_WORKER_CH, User.HEAD_AGENCY_CH,
                         User.HARBOR_MASTER_CH])
        elif request.method in ['POST']:
            return bool(request.user and request.user.type_user in [User.AGENT_CH, User.HEAD_AGENCY_CH])
        elif request.method in ['PUT', 'PATCH']:
            return bool(request.user and request.user.type_user in [User.ADMIN_CH, User.HARBOR_WORKER_CH,
                                                                    User.HARBOR_MASTER_CH])
        elif request.method in ['DELETE']:
            return bool(request.user and request.user.type_user in [User.ADMIN_CH])
        return False


class IORequestPermissions(permissions.BasePermission, CheckAgentNominations):
    """
    Permissions for IO request
    """

    def has_permission(self, request, view):
        if request.user and request.user.type_user in [User.AGENT_CH, User.HEAD_AGENCY_CH]:
            ship_pk = view.kwargs.get('ship_pk')
            if ship_pk and not self.check_agent_nominations(view.kwargs['ship_pk'], request.user):
                raise AgentForbidden
        if request.method in ['GET']:
            return True
        elif request.method in ['POST']:
            return bool(request.user and request.user.type_user in [User.AGENT_CH,
                                                                    User.HEAD_AGENCY_CH,
                                                                    User.ADMIN_CH])
        elif request.method in ['PUT', 'PATCH']:
            return bool(request.user and request.user.type_user in [User.ADMIN_CH,
                                                                    User.AGENT_CH,
                                                                    User.HARBOR_WORKER_CH,
                                                                    User.HARBOR_MASTER_CH,
                                                                    User.ACCOUNTANT_CH])
        elif request.method in ['DELETE']:
            return bool(request.user and request.user.type_user in [User.ADMIN_CH])
        return False


class MainInfoPermissions(permissions.BasePermission):
    """
    Permissions for main info of the ship
    """

    def has_permission(self, request, view):
        if request.method in ['GET']:
            return True
        elif request.method in ['POST']:
            return True
        elif request.method in ['PUT', 'PATCH']:
            return True
        elif request.method in ['DELETE']:
            return bool(request.user and request.user.type_user in [User.ADMIN_CH])
        return False

    # def has_object_permission(self, request, view, obj):
    #     is_ban = request.data.get('is_ban', None)
    #     if is_ban is not None and request.user and request.user.type_user not in [User.MARAD_CH, User.ADMIN_CH]:
    #         return False
    #     return True


class ShipStaffPermission(permissions.BasePermission, CheckAgentNominations):

    def has_permission(self, request, view):
        if request.user and request.user.type_user in [User.AGENT_CH, User.HEAD_AGENCY_CH] and \
                not self.check_agent_nominations(view.kwargs['ship_pk'], request.user):
            raise AgentForbidden
        return True
