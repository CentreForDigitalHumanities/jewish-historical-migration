from rest_framework import serializers

from .models import Record

class RecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Record
        fields = [
            'identifier', 'source', 'language', 'script', #'place',
            'site_type', 'inscription_type', 'period', 'centuries',
            'inscriptions_count', 'religious_profession', 'sex_dedicator',
            'sex_deceased', 'symbol', 'comments', 'inscription', 'transcription'
        ]
        # depth = 1