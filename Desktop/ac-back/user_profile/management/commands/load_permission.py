from django.core.management import BaseCommand
from user_profile.views import SomeDataAPI

class Command(BaseCommand):

    def handle(self, *args, **options):
        perms = SomeDataAPI()
        p = perms.load_perms()
        return 'Permission was  success loaded'
