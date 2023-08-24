import logging
from datetime import datetime
from django.core.management import BaseCommand

from data.models import import_dataset

class Command(BaseCommand):
    help = '''
    import a dataset from an XLSX sheet into the database
    '''
    def add_arguments(self, parser):
        parser.add_argument(
            'import_path',
            help='''Provide the path and filename of the source data''',
        )
    
    def handle(self, import_path, **options):
        import_dataset(import_path)
