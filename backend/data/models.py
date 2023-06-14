from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

from .pleiades import pleiades_fetcher


class Area(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=100)
    area = models.ForeignKey(
        to=Area, null=True, blank=True, on_delete=models.SET_NULL
    )
    region = models.ForeignKey(
        to=Region, null=True, blank=True, on_delete=models.SET_NULL
    )
    coordinates = gismodels.PointField(null=True, blank=True)

    def __str__(self):
        return self.name


class PleiadesPlace(Place):
    pleiades_id = models.IntegerField()

    def fetch_from_pleiades(self):
        # Get Pleiades coordinates (latitude, longitude)
        coordinates = pleiades_fetcher.fetch(self.pleiades_id)['reprPoint']
        # Convert to point (longitude, latitude)
        point = Point(
            float(coordinates[1]), float(coordinates[0])
        )
        self.coordinates = point


class CustomPlace(Place):
    pass
