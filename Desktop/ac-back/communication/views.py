from django.shortcuts import render
from transliterate import translit

# from communication.models import MarinersRecordBooks
from directory.models import BlankStrictReport, Region, City
from sailor.models import Profile
from sailor.document.models import ServiceRecord
from django.db.models import Max
# Create your views here.

