from django.shortcuts import render
from .models import Doctor


def search_doctor(request):

    query = request.GET.get('q')

    doctors = Doctor.objects.all()
