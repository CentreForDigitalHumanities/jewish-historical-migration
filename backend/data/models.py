from typing import List, Optional
import uuid
import logging

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

import openpyxl

from .pleiades import PleiadesError, pleiades_fetcher
from .utils import to_decimal

logger = logging.getLogger(__name__)


class Area(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PlaceManager(models.Manager):
    def create_place(self, row_dict, location_sheet):
        if row_dict['placename'] is None:
            # No placename defined; do not create anything and return None
            return None
        area = region = None
        if row_dict.get('area'):
            area, created = Area.objects.get_or_create(name=row_dict['area'])
        if row_dict.get('province-region'):
            region, created = Region.objects.get_or_create(name=row_dict['province-region'])
        place, created = self.get_or_create(
            name=row_dict['placename'],
            area=area,
            region=region,
        )
        place.pleiades_id = row_dict['pleiades'] if isinstance(row_dict['pleiades'], int) else None
        coordinates = None
        if place.pleiades_id:
            coordinates = place.fetch_from_pleiades()
            if not coordinates:
                # Not found in Pleiades. Give a warning and continue
                logger.warning(
                    f"Pleiades ID {place.pleiades_id} not found. Taking "
                    "information from document instead."
                )
        if coordinates is None:
            coordinates = place.fetch_from_document(location_sheet, row_dict['own id '])
        if coordinates and coordinates[0] and coordinates[1]:
            # Convert to point (longitude, latitude)
            point = Point(
                float(coordinates[1]), float(coordinates[0])
            )
            place.coordinates = point
        place.save()
        return place

class Place(models.Model):
    name = models.CharField(max_length=100)
    area = models.ForeignKey(
        to=Area, null=True, blank=True, on_delete=models.SET_NULL
    )
    region = models.ForeignKey(
        to=Region, null=True, blank=True, on_delete=models.SET_NULL
    )
    coordinates = gismodels.PointField(null=True, blank=True)
    pleiades_id = models.IntegerField(null=True, blank=True)
        
    objects = PlaceManager()

    def __str__(self):
        return self.name

    def fetch_from_pleiades(self) -> Optional[List[float]]:
        ''' get Pleiades coordinates (latitude, longitude) '''
        pleiades_info = pleiades_fetcher.fetch(self.pleiades_id)
        if pleiades_info:
            reprpoint = pleiades_info['reprPoint']
            return reprpoint
        else:
            # Not found
            return None
    
    def fetch_from_document(self, location_sheet, identifier):
        ''' return coordinates from sheet with location info:
        latitute in column 4, longitude in column 5
        '''
        return next(((to_decimal(row[4]), to_decimal(row[5])) for row in location_sheet.values if row[0] == identifier), None)
    
class RecordManager(models.Manager):
    def create_record(self, row, place) -> Optional['Record']:
        """ given a row from the input file and a place,
        return a SettlementEvidence instance """
        if row['id'] is None or row['id'] == '':
            logger.warning('Ignoring row with empty id column')
            return None
        record, created = self.get_or_create(
            identifier=row['id'],
            source = row['source']
        )
        record.language = row['language'] or ''
        record.script = row['script'] or ''
        record.place = place
        record.site_type = row['category 1'] or ''
        record.inscription_type = row['category 2'] or ''
        record.period = row['period'] or ''
        record.centuries = row['centuries'] or ''
        record.inscriptions_count = row['inscriptions-count'] if isinstance(row['inscriptions-count'], int) else 0
        record.mentioned_placenames = row['mentioned placenames'] or ''
        record.religious_profession = row['mention religious profession'] or ''
        record.sex_dedicator = row['sexe dedicator epitaph (male/female/child)'] or ''
        record.sex_deceased = row['sexe of deceased (male/female/child)'] or ''
        record.symbol = row['mention religious symbol'] or ''
        record.comments = row['comments'] or ''
        record.inscription = row['inscription'] or ''
        record.transcription = row['transcription '] or ''
        record.save()
        return record

class Record(models.Model):

    def __str__(self):
        source = self.source if self.source else "(unknown source"
        name = self.place.name if self.place and self.place.name else "(unknown place)"
        return '{} {}'.format(source, name)

    identifier = models.IntegerField(default=1)
    source = models.CharField(max_length=255, default='')
    language = models.CharField(max_length=250, blank=True, default='')
    script = models.CharField(max_length=255, blank=True, default='')
    place = models.ForeignKey(to=Place, null=True, blank=True, on_delete=models.SET_NULL)
    site_type = models.CharField(max_length=255, blank=True, default='')
    inscription_type = models.CharField(max_length=255, blank=True, default='')
    period = models.CharField(verbose_name="Historical period", max_length=255, blank=True, default='')
    centuries = models.CharField(verbose_name="Estimated century/ies", max_length=255, blank=True, default='')
    inscriptions_count = models.IntegerField(default=0)
    mentioned_placenames = models.CharField(max_length=255, blank=True, default='')
    religious_profession = models.CharField(max_length=255, blank=True, default='')
    sex_dedicator = models.CharField(max_length=255, blank=True, default='')
    sex_deceased = models.CharField(max_length=255, blank=True, default='')
    symbol = models.CharField(verbose_name="Religious symbol", max_length=255, blank=True, default='')
    comments = models.TextField(blank=True, default='')
    inscription = models.TextField(blank=True, default='')
    transcription = models.TextField(blank=True, default='')

    objects = RecordManager()

    class Meta:
        unique_together = [['identifier', 'source']]

def import_dataset(input_file):
    wb = openpyxl.load_workbook(filename=input_file)
    sheet = wb['Data JewishMigration']
    sheet2 = wb['ID settlements without Pleiades']
    for index, row in enumerate(sheet.values):
        print(index, index>5000)
        if index > 2000:
            break
        if index == 0:
            keys = [cell for cell in row if cell]
            continue
        row_dict = {k: row[i] for i, k in enumerate(keys)}
        if row_dict['source'] == None:
            # do not register rows with empty source field
            continue
        place = Place.objects.create_place(
            row_dict, sheet2
        )
        Record.objects.create_record(
            row_dict, place
        )

    
