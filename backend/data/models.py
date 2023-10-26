from typing import Callable, List, Optional
import uuid
import logging

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

import openpyxl

from .pleiades import PleiadesError, pleiades_fetcher
from .utils import to_decimal

logger = logging.getLogger(__name__)

SEX_REPLACEMENTS = {
    "Female": "female",
    "Male": "male",
    "Child (Female)": "female-child",
    "Child (Male)": "male-child",
    "Child": "child"
}


def normalize_sex(input_str: str) -> list[str]:
    """Normalize data about sex and age and give back as list of strings."""
    # Sex is given such as here: 'Male|Female| Child (Female)| Child (Female)'
    items = input_str.split("|")
    return [SEX_REPLACEMENTS.get(x.strip(), x) for x in items]


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
                    f"Cannot find coordinates for pleiades ID {place.pleiades_id}. "
                    "Taking information from document instead."
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
            if not reprpoint:
                logger.warning(
                    f"Pleiades object {self.pleiades_id} found but it has no "
                    "coordinates."
                )
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
        record.place = place

        # Apply simple string or integer mappings
        record.period = row['period'] or ''
        record.inscriptions_count = row['inscriptions-count'] if isinstance(row['inscriptions-count'], int) else 0
        record.mentioned_placenames = row['mentioned placenames'] or ''
        record.religious_profession = row['mention religious profession'] or ''
        record.symbol = row['mention religious symbol'] or ''
        record.comments = row['comments'] or ''
        record.inscription = row['inscription'] or ''
        record.transcription = row['transcription '] or ''

        sex_dedicator_text = row['sexe dedicator epitaph (male/female/child)']
        if sex_dedicator_text:
            record.sex_dedicator = ', '.join(normalize_sex(sex_dedicator_text))
        sex_deceased_text = row['sexe of deceased (male/female/child)']
        if sex_deceased_text:
            record.sex_deceased = ', '.join(normalize_sex(sex_deceased_text))

        # Apply mappings for which a single objects is selected or created
        category1text = row['category 1']
        if category1text:
            record.category1 = PrimaryCategory.objects.create_record(row['category 1'])
        category2text = row['category 2']
        if category2text:
            record.category2 = SecondaryCategory.objects.create_record(row['category 2'])

        # Same, but with multiple objects
        language_text = row['language']
        if language_text:
            record.languages.set(Language.objects.create_records(
                language_text,
                '|'
            ))
        script_text = row['script']
        if script_text:
            record.scripts.set(Script.objects.create_records(
                script_text,
                '|'
            ))
        centuries_text = row['centuries']
        if centuries_text:
            record.estimated_centuries.set(Century.objects.create_records(
                centuries_text,
                '|',
                (lambda x: '-' + x[:-1] if x.endswith('-') else x)
            ))

        record.save()
        return record

class Record(models.Model):

    def __str__(self):
        source = self.source if self.source else "(unknown source"
        name = self.place.name if self.place and self.place.name else "(unknown place)"
        return '{} {}'.format(source, name)

    identifier = models.IntegerField(default=1)
    source = models.CharField(max_length=255, default='')
    languages = models.ManyToManyField("Language")
    scripts = models.ManyToManyField("Script")
    place = models.ForeignKey(to=Place, null=True, blank=True, on_delete=models.SET_NULL)
    category1 = models.ForeignKey(to="PrimaryCategory", null=True, blank=True, on_delete=models.SET_NULL)
    category2 = models.ForeignKey(to="SecondaryCategory", null=True, blank=True, on_delete=models.SET_NULL)
    period = models.CharField(verbose_name="Historical period", max_length=255, blank=True, default='')
    estimated_centuries = models.ManyToManyField("Century", verbose_name="Estimated century/ies")
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


class ChoiceFieldManager(models.Manager):
    def create_records(
            self, value: str, splitter: str, transformer: Optional[Callable] = None
    ) -> List["BaseChoiceField"]:
        value = str(value)
        entries = value.split(splitter)
        # Return a list of records by applying create_record() to each entry.
        return [self.create_record(x, transformer) for x in entries]

    def create_record(
            self, value: str, transformer: Optional[Callable[[str], str]] = None
    ) -> "BaseChoiceField":
        value = str(value)
        if transformer:
            value = transformer(value)
        value = value.strip()
        record, _ = self.model.objects.get_or_create(name=value)
        record.name = value
        record.save()
        return record


class BaseChoiceField(models.Model):
    name = models.CharField(max_length=255, unique=True)

    objects = ChoiceFieldManager()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class PrimaryCategory(BaseChoiceField):
    pass


class SecondaryCategory(BaseChoiceField):
    pass


class Language(BaseChoiceField):
    pass


class Script(BaseChoiceField):
    pass


class Century(BaseChoiceField):
    pass


def import_dataset(input_file):
    wb = openpyxl.load_workbook(filename=input_file)
    sheet = wb['Data JewishMigration']
    sheet2 = wb['ID settlements without Pleiades']
    source_empty = False
    for index, row in enumerate(sheet.values):
        if index == 0:
            keys = [cell for cell in row if cell]
            continue
        row_dict = {k: row[i] for i, k in enumerate(keys)}
        if row_dict['source'] == None:
            # do not register rows with empty source field
            # if previous row had empty source field too, stop reading
            if source_empty:
                break
            else:
                source_empty = True
                continue
        place = Place.objects.create_place(
            row_dict, sheet2
        )
        Record.objects.create_record(
            row_dict, place
        )

    
