from rest_framework import viewsets
from rest_framework import permissions
from .models import Record
from .serializers import RecordSerializer


class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows records to be viewed.
    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]

