import json

from django.http import HttpResponse, HttpRequest
from rest_framework import viewsets
from rest_framework import permissions

from .geojson import create_geojson
from .models import Record
from .serializers import RecordSerializer


class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows records to be viewed.
    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    # permission_classes = [permissions.IsAuthenticated]


def download_geojson(request: HttpRequest) -> HttpResponse:
    """Download a GeoJSON file containing all existing records."""
    geojson_dict = create_geojson()
    response = HttpResponse(
        content_type="application/geo+json"
    )
    response.content = json.dumps(geojson_dict, indent=4).encode()
    return response

