from datetime import date

from itcs import magic_numbers
from .models import StudentID


def check_cadet_student_ID(students_id, rank_id):
    """Является ли моряк кадетом. Если есть действительный студентческий билет, то является - True, иначе False"""
    student = StudentID.objects.filter(id__in=students_id, status_document_id=magic_numbers.status_student_id_valid)
    return student.exists() and rank_id in [23, 86, 90]

