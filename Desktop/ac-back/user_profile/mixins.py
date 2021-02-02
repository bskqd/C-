from django.db.models import Q, F
from django.db.models.fields.json import KeyTextTransform

from user_profile.models import FullUserSailorHistory


class GetAuthorMixin:
    @property
    def _author(self):
        created_at_m = getattr(self, 'created_at')
        author_m = getattr(self, 'author')
        if created_at_m and author_m:
            author = author_m
            datetime_create = created_at_m
        else:
            history = FullUserSailorHistory.objects.select_related('user', 'user__userprofile').filter(
                content_type__model=self._meta.model_name,
                object_id=self.pk, action_type='create').first()
            datetime_create = history.datetime.strftime('%d-%m-%Y %H:%M:%S')
            author = history.user
        if author.username.startswith(('key_', '+380')):
            author_name = 'Створено з кабінету моряка'
        elif hasattr(author, 'userprofile'):
            author_name = f'{author.last_name} {author.first_name} {author.userprofile.middle_name}'
        else:
            author_name = f'{author.last_name} {author.first_name}'
        return {'name': author_name, 'date': datetime_create}

    @property
    def _verificator(self):
        status_document_filtering = {'old_status_document': F('new_status_document')}
        status_filtering = {'old_status': F('new_status')}
        status_line = {'old_status_line': F('new_status_line')}
        annotate = {
            'old_status_document': KeyTextTransform('status_document', 'old_obj_json'),
            'new_status_document': KeyTextTransform('status_document', 'new_obj_json'),
            'old_status': KeyTextTransform('status', 'old_obj_json'),
            'new_status': KeyTextTransform('status', 'new_obj_json'),
            'old_status_line': KeyTextTransform('status_line', 'old_obj_json'),
            'new_status_line': KeyTextTransform('status_line', 'new_obj_json')
        }
        history = FullUserSailorHistory.objects.select_related('user__userprofile', 'user').filter(
            Q(content_type__model=self._meta.model_name) &
            Q(object_id=self.id) &
            Q(action_type='edit')).annotate(**annotate)
        temp_history = history.first()
        if getattr(temp_history, 'old_status_document'):
            history = history.exclude(**status_document_filtering)
        elif getattr(temp_history, 'old_status'):
            history = history.exclude(**status_filtering)
        elif getattr(temp_history, 'old_status_line'):
            history = history.exclude(**status_line)
        history = history.order_by('pk').last()
        author = history.user
        author_name = '{} {} {}'.format(author.last_name, author.first_name, author.userprofile.middle_name)
        return {'name': author_name, 'date': history.datetime.strftime('%d-%m-%Y %H:%M:%S')}

    # def _change_status(self):
    #     ct = ContentType.objects.get(model__iexact=self.__class__.__name__)
    #     history = FullUserSailorHistory.objects.filter(content_type=ct, object_id=self.pk, action_type='edit',
    #                                                   old_obj_json__status_document_id=25).order_by('-datetime').\
    #         first()
    #     author = history.user
    #     return '{} {} {}  -  {}'.format(author.last_name, author.first_name, author.userprofile.middle_name,
    #                                     history.datetime)

# class GetVerficatorMixin:
#     @property
#     def _verificator(self):
#         ct = ContentType.objects.get(model__iexact=self.__class__.__name__)
#         author = FullUserSailorHistory.objects.get(content_type=ct, object_id=self.id, action_type='edit',
#                                                       old_obj_json__status_document__id=34).user
#         return '{} {} {}'.format(author.last_name, author.first_name, author.userprofile.middle_name)
