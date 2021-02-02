from django.db import models
from django.utils import timezone

from directory.models import NTZ, Course
from sailor.models import DateTimesABC


class ETIRegistry(DateTimesABC):
    institution = models.ForeignKey(NTZ, on_delete=models.CASCADE, related_name='eti_registry')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='eti_registry')
    date_start = models.DateField()
    date_end = models.DateField()
    number_protocol = models.IntegerField()
    is_disable = models.BooleanField(default=False)

    class Meta:
        unique_together = ['institution', 'course', 'date_start', 'date_end', 'number_protocol']

    @property
    def get_full_number_protocol(self):
        return '{}/{}'.format(self.number_protocol, self.date_start.year)


class CertificateRedHistory(DateTimesABC):
    institute = models.ForeignKey(NTZ, on_delete=models.CASCADE, related_name='red_history')
    date_start = models.DateField()
    date_end = models.DateField(null=True)


class TimeForCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    theory_hours = models.FloatField(default=0)
    practice_hours = models.FloatField(default=0)
    examination_hours = models.FloatField(default=0)
    is_continue = models.BooleanField(default=False)

    class Meta:
        unique_together = (('course', 'is_continue'),)

    @property
    def full_time(self):
        return self.theory_hours + self.practice_hours + self.examination_hours
