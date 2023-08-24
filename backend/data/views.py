from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from .models import Record
from .serializers import RecordSerializer

class RecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    # permission_classes = [permissions.IsAuthenticated]

