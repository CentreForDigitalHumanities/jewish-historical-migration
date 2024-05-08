from pathlib import Path
from typing import Optional

from django.core.management import BaseCommand

from data.geojson import export_geojson

class Command(BaseCommand):
    help = '''
    Export all records to GeoJSON file to plot on a map.
    '''
    def add_arguments(self, parser):
        parser.add_argument(
            '--export_path',
            help='''Path to JSON file to write to''',
            default=None
        )
    
    def handle(self, export_path: Optional[str], **options):
        if export_path is None:
            export_path = Path.cwd() / "features.geojson"
        export_geojson(export_path)
        self.stdout.write(self.style.SUCCESS(f'Features written to {export_path}.'))
