from typing import Callable, List, Optional
import logging

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

import openpyxl

from .pleiades import pleiades_fetcher
from .utils import to_decimal

logger = logging.getLogger(__name__)

SEX_REPLACEMENTS = {
    "Female": "female",
    "Male": "male",
    "Child (Female)": "female-child",
    "Child (Male)": "male-child",
    "Child": "child"
}


def normalize_sex(input_str: str) -> List[str]:
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
        placename = row_dict['placename']
        if placename is None:
            # No placename defined; do not create anything and return None
            return None
        else:
            placename = placename.strip()
        area = region = None
        if row_dict.get('area'):
            areastr = row_dict.get('area').strip()
            area, created = Area.objects.get_or_create(name=areastr)
        if row_dict.get('province-region'):
            regionstr = row_dict.get('province-region').strip()
            region, created = Region.objects.get_or_create(name=regionstr)
        place, created = self.get_or_create(
            name=row_dict['placename'],
            area=area,
            region=region,
        )
        if not created:
            # Data for one place should always be the same, so there
            # is no reason to repeat this process
            return place
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
        place.coordinates = coordinates
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
    records: models.Manager["Record"]

    def __str__(self):
        return self.name

    def fetch_from_pleiades(self) -> Optional[Point]:
        ''' get Pleiades coordinates as a Point, or None if they cannot be 
        determined. '''
        # Pleiades JSON entries contain an attribute reprPoint, which contains
        # the coordinates as an array with first the longitude, then the 
        # latitude (first x, then y). This is the reverse of the order that
        # is shown on the public web pages of Pleiades!
        if not self.pleiades_id:
            return None
        pleiades_info = pleiades_fetcher.fetch(self.pleiades_id)
        if pleiades_info:
            reprpoint = pleiades_info['reprPoint']
            if not reprpoint:
                logger.warning(
                    f"Pleiades object {self.pleiades_id} found but it has no "
                    "coordinates."
                )
                return None
            else:
                # Point expects first x, then y
                return Point(float(reprpoint[0]), float(reprpoint[1]))
        else:
            # Not found
            logger.warning(
                f"Pleiades object {self.pleiades_id} not found."
            )
            return None
    
    def fetch_from_document(self, location_sheet, identifier) -> Optional[Point]:
        ''' return coordinates from sheet with location info:
        latitute in column 4, longitude in column 5
        '''
        coordinates = next(((to_decimal(row[4]), to_decimal(row[5])) for row in location_sheet.values if row[0] == identifier), None)
        if coordinates is not None:
            # Point expects first x (longitude), then y (latitude)
            return Point(coordinates[1], coordinates[0])

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        # Run save also on related records to update their region and area
        for record in self.records.all():
            record.save()

    class Meta:
        ordering = ["name"]
    
class RecordManager(models.Manager):
    def create_record(self, row, place) -> Optional['Record']:
        """ given a row from the input file and a place,
        return a SettlementEvidence instance """
        if row['id'] is None or row['id'] == '':
            logger.warning('Ignoring row with empty id column')
            return None
        record, created = self.get_or_create(
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
    FEMALE = "female"
    MALE = "male"
    FEMALE_CHILD = "female-child"
    MALE_CHILD = "male-child"
    CHILD = "child"
    SEX_CHOICES = [
        ("", "-"),
        (FEMALE, "Female"),
        (MALE, "Male"),
        (FEMALE_CHILD, "Female (child)"),
        (MALE_CHILD, "Male (child)"),
        (CHILD, "Child"),
    ]

    source = models.CharField(max_length=255, unique=True)
    languages = models.ManyToManyField("Language")
    scripts = models.ManyToManyField("Script")
    place = models.ForeignKey(to=Place, null=True, blank=True, on_delete=models.SET_NULL, related_name="records")
    category1 = models.ForeignKey(verbose_name="primary category", to="PrimaryCategory", null=True, blank=True, on_delete=models.SET_NULL)
    category2 = models.ForeignKey(verbose_name="secondary category", to="SecondaryCategory", null=True, blank=True, on_delete=models.SET_NULL)
    period = models.CharField(verbose_name="historical period", max_length=255, blank=True, default='')
    estimated_centuries = models.ManyToManyField("Century", verbose_name="estimated centuries")
    inscriptions_count = models.IntegerField(default=0)
    mentioned_placenames = models.CharField(max_length=255, blank=True, default='')
    religious_profession = models.CharField(max_length=255, blank=True, default='')
    sex_dedicator = models.CharField(verbose_name="sex dedicator", max_length=255, choices=SEX_CHOICES, blank=True, default='')
    sex_deceased = models.CharField(verbose_name="sex deceased", max_length=255, choices=SEX_CHOICES, blank=True, default='')
    symbol = models.CharField(verbose_name="religious symbol", max_length=255, blank=True, default='')
    comments = models.TextField(blank=True, default='')
    inscription = models.TextField(blank=True, default='')
    transcription = models.TextField(blank=True, default='')

    # Non-editable fields for quick lookup
    area = models.CharField(max_length=100, editable=False, null=True)
    region = models.CharField(max_length=100, editable=False, null=True)

    objects = RecordManager()

    def save(self, *args, **kwargs) -> None:
        self.area = str(self.place.area) if self.place else None
        self.region = str(self.place.region) if self.place else None
        return super().save(*args, **kwargs)

    def __str__(self):
        source = self.source if self.source else "(unknown source)"
        name = self.place.name if self.place and self.place.name else "(unknown place)"
        return '{} {}'.format(source, name)


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
        ordering = ["name"]


class PrimaryCategory(BaseChoiceField):
    class Meta:
        verbose_name_plural = "primary categories"
        ordering = ["name"]


class SecondaryCategory(BaseChoiceField):
    class Meta:
        verbose_name_plural = "secondary categories"
        ordering = ["name"]


class Language(BaseChoiceField):
    pass


class Script(BaseChoiceField):
    pass


class Century(BaseChoiceField):
    # The century is represented as a string that might be either a (negative
    # or positive) number or the word "unknown".

    century_number = models.IntegerField(null=True, blank=True, editable=False)
    """The century as a number, for sorting purposes. Automatically generated."""

    @classmethod
    def _to_number(cls, century: str) -> Optional[int]:
        """Return the century as an integer, or None if it is set as
        unknown. Raises ValueError if value is invalid."""
        if century == "unknown":
            return None
        else:
            return int(century)

    def save(self, *args, **kwargs) -> None:
        try:
            number = self._to_number(self.name)
        except ValueError:
            pass
        else:
            self.century_number = number
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.century_number:
            ce_or_bce = "CE" if self.century_number >= 0 else "BCE"
            return f"{abs(self.century_number)} {ce_or_bce}"
        else:
            return self.name
    
    class Meta:
        verbose_name_plural = "centuries"
        ordering = ["century_number"]



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
        if row_dict['source'] is None:
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

    
