from django.shortcuts import render
from .models import Doctor
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Patient


def search_doctor(request):

    # Get search text
    query = request.GET.get('q')

    # Get all doctors
    doctors = Doctor.objects.all()

    # Search doctor by name or specialization
    if query:

        doctors = doctors.filter(
            user__first_name__icontains=query
        ) | doctors.filter(
            specialization__icontains=query
        )

    # Send data to HTML
    context = {
        'doctors': doctors,
        'query': query
    }

    return render(
        request,
        'search_doctor.html',
        context
    )
@login_required
def patient_profile(request):

    # Get patient of logged-in user
    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    # Check adult or not
    if patient.age >= 18:
        is_adult = True
        age_status = "Adult"
    else:
        is_adult = False
        age_status = "Minor"

    # Context data
    context = {

        'patient': patient,

        'is_adult': is_adult,

        'age_status': age_status,

        'full_name': patient.user.get_full_name(),

        'email': patient.user.email,

        'phone': patient.phone,

        'address': patient.address,

        'blood_group': patient.blood_group,

    }

    return render(
        request,
        'patient_profile.html',
        context
    )