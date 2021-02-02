from copy import deepcopy

from rest_framework import serializers

from .models import StudentID
from directory.serializers import (FacultySerializer, EducationFormSerializer, StatusDocumentSerializer,
                                   NZNameSerializer)
from sailor.forModelSerializer import PhotoSerializer
from sailor.models import PhotoProfile
from sailor.tasks import save_history


class StudentIDSerializer(serializers.ModelSerializer):
    """
    Cadet's student ID
    """
    sailor = serializers.IntegerField(write_only=True)
    photo = PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StudentID
        fields = ('id', 'serial', 'number', 'name_nz', 'group', 'education_form', 'faculty', 'date_start', 'date_end',
                  'educ_with_dkk', 'passed_educ_exam', 'status_document', 'sailor', 'photo')

    def create(self, validated_data):
        del validated_data['sailor']
        return StudentID.objects.create(**validated_data)

    def update(self, instance, validated_data):
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='StudentID', action_type='edit',
                       content_obj=instance, serializer=StudentIDSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance):
        response = super(StudentIDSerializer, self).to_representation(instance)
        response['faculty'] = FacultySerializer(instance=instance.faculty).data
        response['education_form'] = EducationFormSerializer(instance=instance.education_form).data
        response['status_document'] = StatusDocumentSerializer(instance=instance.status_document).data
        response['name_nz'] = NZNameSerializer(instance=instance.name_nz).data
        return response


