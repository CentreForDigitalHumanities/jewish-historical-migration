from django.core.management import BaseCommand

import data.models as models


class Command(BaseCommand):
    help = '''
    clear all data (to facilitate debugging)
    '''
    
    def handle(self, **options):
        models.Record.objects.all().delete()
        models.Area.objects.all().delete()
        models.Place.objects.all().delete()
        models.Region.objects.all().delete()
        models.PrimaryCategory.objects.all().delete()
        models.SecondaryCategory.objects.all().delete()
        models.Language.objects.all().delete()
        models.Script.objects.all().delete()
        models.Century.objects.all().delete()
