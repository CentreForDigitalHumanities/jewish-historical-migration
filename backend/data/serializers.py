from rest_framework import serializers

from .models import Language, Record

class PointField(serializers.CharField):
    def to_representation(self, value):
        return {
            "type": "Point",
            "coordinates":value[:2]
        }


class ChoiceField(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.name


class RecordSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source='place.name', allow_null=True)
    area = serializers.CharField(source='place.area.name', allow_null=True)
    region = serializers.CharField(source='place.region.name', allow_null=True)
    coordinates = PointField(source='place.coordinates', allow_null=True)
    category1 = serializers.CharField(source='category1.name', allow_null=True)
    category2 = serializers.CharField(source='category2.name', allow_null=True)
    languages = ChoiceField(many=True)
    scripts = ChoiceField(many=True)
    estimated_centuries = ChoiceField(many=True)
    publication = serializers.CharField(source='publication.name', allow_null=True)

    class Meta:
        model = Record
        geo_field = 'place.coordinates'
        fields = [
            'source', 'languages', 'scripts', 'place_name',
            'area', 'region', 'coordinates', 'category1', 'category2',
            'period', 'estimated_centuries', 'mentioned_placenames',
            'inscriptions_count', 'religious_profession', 'sex_dedicator',
            'sex_deceased', 'symbol', 'comments', 'inscription', 'transcription',
            'publication'
        ]
    
