from django.shortcuts import render
from .models import Doctor


def search_doctor(request):

    query = request.GET.get('q')

    doctors = Doctor.objects.all()
if query:
        doctors = doctors.filter(
            specialization__icontains=query
        ) | doctors.filter(
            user__first_name__icontains=query
        ) | doctors.filter(
            user__last_name__icontains=query
        )

    context = {
        'doctors': doctors,
        'query': query
    }

    return render(
        request,
        'search_doctor.html',
        context
    )