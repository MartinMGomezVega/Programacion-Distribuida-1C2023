from django.shortcuts import render

from rest_framework import viewsets
# Create your views here.
from .models import Country
from .serializers import CountrySerializer

class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()