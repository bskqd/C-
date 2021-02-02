from django.core.management import BaseCommand

from directory.models import Position, ExperinceForDKK


class Command(BaseCommand):
    def handle(self, *args, **options):
        exp_norms = ExperinceForDKK.objects.filter(experince_descr__isnull=False).distinct('position_id')
        for norm in exp_norms:
            pos = Position.objects.get(id=norm.position_id)
            pos.experience_description = norm.experince_descr
            pos.standarts_text = norm.standarts_text
            pos.save()