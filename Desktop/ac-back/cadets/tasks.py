import itertools

from itcs.celery import celery_app
from communication.models import SailorKeys
from cadets.models import StudentID


@celery_app.task
def clear_students_id():
    list_students_id = list(SailorKeys.objects.filter(students_id__isnull=False).values_list('students_id', flat=True))
    related_student_id = list(itertools.chain.from_iterable(list_students_id))
    StudentID.objects.exclude(id__in=related_student_id).delete()
    return True
