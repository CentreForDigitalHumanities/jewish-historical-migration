from rest_framework import serializers

from .models import Record

class PointField(serializers.CharField):
    def to_representation(self, value):
        return {
            "type": "Point",
            "coordinates":value[:2]
        }

class RecordSerializer(serializers.HyperlinkedModelSerializer):
    place_name = serializers.CharField(source='place.name', allow_null=True)
    area = serializers.CharField(source='place.area.name', allow_null=True)
    region = serializers.CharField(source='place.region.name', allow_null=True)
    coordinates = PointField(source='place.coordinates', allow_null=True)

    class Meta:
        model = Record
        geo_field = 'place.coordinates'
        fields = [
            'identifier', 'source', 'language', 'script', 'place_name',
            'area', 'region', 'coordinates',
            'site_type', 'inscription_type', 'period', 'centuries',
            'inscriptions_count', 'religious_profession', 'sex_dedicator',
            'sex_deceased', 'symbol', 'comments', 'inscription', 'transcription'
        ]
    
