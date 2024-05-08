from django.urls import path

from .views import download_geojson

urlpatterns = [
    path('geojson.json', download_geojson)
]