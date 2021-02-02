from copy import deepcopy

from rest_framework import mixins, generics
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet

from communication.models import SailorKeys
from itcs import magic_numbers
from sailor.statement.models import StatementSQC
from sailor.tasks import save_history
from .models import StudentID
from rest_framework import permissions
from .permissions import PermissionStudentsID
from .serializers import StudentIDSerializer


class StudentIDViewset(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, PermissionStudentsID,)
    queryset = StudentID.objects.all()
    serializer_class = StudentIDSerializer

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        status_document = serializer.initial_data['status_document']
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        ser = serializer.save()
        if sailor_qs.students_id:
            sailor_qs.students_id.append(ser.id)
            sailor_qs.save(update_fields=['students_id'])
        else:
            sailor_qs.students_id = [ser.id]
            sailor_qs.save(update_fields=['students_id'])
        if sailor_qs.statement_dkk and status_document == magic_numbers.status_student_id_valid:
            statement_sqc = StatementSQC.objects.filter(
                id__in=sailor_qs.statement_dkk, rank_id__in=[23, 86, 90],
                status_document_id=magic_numbers.CREATED_FROM_PERSONAL_CABINET)
            for statement in statement_sqc:
                statement.is_cadet = True
                statement.save(update_fields=['is_cadet'])

        user = self.request.user.id
        save_history.s(user_id=user, module='StudentID', action_type='create', content_obj=ser, new_obj=ser,
                       serializer=StudentIDSerializer, sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        key = SailorKeys.objects.filter(students_id__overlap=[instance.id]).first()
        if not key:
            raise ValidationError('Sailor does not exists')
        key.students_id.remove(instance.id)
        key.save(update_fields=['students_id'])
        _instance = deepcopy(instance)
        instance.delete()

        save_history.s(user_id=self.request.user.id, module='StudentID', action_type='delete',
                       content_obj=_instance, serializer=StudentIDSerializer,
                       old_obj=_instance, sailor_key_id=key.id).apply_async(serializer='pickle')


class SailorStudentIDViewset(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, PermissionStudentsID,)
    serializer_class = StudentIDSerializer

    def get_queryset(self):
        try:
            sailor = self.kwargs['sailor']
            keys = SailorKeys.objects.get(id=sailor)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        except KeyError:
            raise ValidationError('Sailor empty')
        if keys.students_id:
            return StudentID.objects.filter(id__in=keys.students_id).order_by('-id')
        else:
            return []
