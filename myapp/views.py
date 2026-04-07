# myapp/views.py - FINAL FIXED VERSION
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .decorators import admin_required, patient_required
from .models import (
    Patient, Appointment, Bill,
    UserProfile, MedicalRecord, Doctor, Department, Bed
)

logger = logging.getLogger(__name__)


# =============================================================================
# 🔹 Authentication Views
# =============================================================================

def login_view(request):

    # already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

    # POST only
    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Please fill in all fields")
            return render(request, 'myapp/login.html')

        email = email.strip().lower()

        user_obj = User.objects.filter(email__iexact=email).first()

        if not user_obj:
            messages.error(request, "Invalid email or password")
            return render(request, 'myapp/login.html')

        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return render(request, 'myapp/login.html')

        login(request, user)

        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'patient'}
        )

        if user.is_superuser or profile.role == 'admin':
            return redirect('dashboard')

        elif profile.role == 'doctor':
            return redirect('dashboard')

        else:
            return redirect('patient_dashboard')

    return render(request, 'myapp/login.html')

def signup_view(request):
    """Signup View - Creates Patient by default"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([full_name, email, password, confirm_password]):
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'myapp/signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'myapp/signup.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'myapp/signup.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'myapp/signup.html')

        try:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
            UserProfile.objects.create(user=user, role='patient', phone=phone)
            login(request, user)
            messages.success(request, 'Account created! Welcome to CareFusion.')
            return redirect('patient_dashboard')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'myapp/signup.html')

    return render(request, 'myapp/signup.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# =============================================================================
# 🔹 Admin Dashboard View
# =============================================================================

@login_required
@admin_required
def dashboard(request):
    """Admin Dashboard - Full Access"""
    today = timezone.now().date()

    # Statistics
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(status='available').count()
    occupied_beds = Bed.objects.filter(status='occupied').count()

    total_appointments = Appointment.objects.filter(appointment_date__date=today).count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    total_revenue = Bill.objects.filter(created_at__date=today, paid=True).aggregate(total=Sum('amount'))['total'] or 0

    # Patients
    patients = Patient.objects.select_related('assigned_doctor', 'department').order_by('-created_at')[:10]

    # Appointments
    appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-appointment_date')[:10]

    # Chart Data
    patient_chart_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    patient_chart_data = [Patient.objects.filter(created_at__date=today - timedelta(days=i)).count() for i in range(6, -1, -1)]

    departments = Department.objects.annotate(patient_count=Count('patients')).order_by('-patient_count')[:5]
    dept_chart_labels = [dept.name for dept in departments]
    dept_chart_data = [dept.patient_count for dept in departments]

    # Recent Activities
    recent_activities = []
    for appt in appointments[:5]:
        recent_activities.append({
            'description': f"Appointment {appt.status} for {appt.patient}",
            'icon': 'fa-calendar-check',
            'timestamp': appt.created_at,
            'user': str(appt.doctor) if appt.doctor else 'System',
            'type': 'Appointment'
        })

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'total_revenue': total_revenue,
        'patients': patients,
        'appointments': appointments,
        'patient_chart_labels': patient_chart_labels,
        'patient_chart_data': patient_chart_data,
        'dept_chart_labels': dept_chart_labels,
        'dept_chart_data': dept_chart_data,
        'recent_activities': recent_activities,
        'current_user': request.user,
        'user_role': 'admin',
    }

    return render(request, 'myapp/admin_dashboard.html', context)


# =============================================================================
# 🔹 Patient Dashboard View
# =============================================================================

@login_required
@patient_required
def patient_dashboard(request):
    """Patient Dashboard - ONLY Own Data"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found. Contact admin.')
        return redirect('login')

    # Own Statistics
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).count()

    medical_records_count = MedicalRecord.objects.filter(patient=patient).count()

    pending_bills = Bill.objects.filter(patient=patient, paid=False)
    pending_bills_count = pending_bills.count()
    total_pending_amount = pending_bills.aggregate(total=Sum('amount'))['total'] or 0

    # Next Appointment
    next_appointment = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).select_related('doctor').order_by('appointment_date').first()

    # Recent Data
    recent_appointments = Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-appointment_date')[:5]
    recent_bills = Bill.objects.filter(patient=patient).order_by('-created_at')[:5]
    recent_records = MedicalRecord.objects.filter(patient=patient).select_related('doctor').order_by('-created_at')[:5]

    context = {
        'patient': patient,
        'upcoming_appointments_count': upcoming_appointments,
        'medical_records_count': medical_records_count,
        'pending_bills_count': pending_bills_count,
        'total_pending_amount': total_pending_amount,
        'next_appointment': next_appointment,
        'recent_appointments': recent_appointments,
        'recent_bills': recent_bills,
        'recent_medical_records': recent_records,
        'assigned_doctor_name': str(patient.assigned_doctor) if patient.assigned_doctor else 'Not Assigned',
        'user_role': 'patient',
    }

    return render(request, 'myapp/patient_dashboard.html', context)


@login_required
@patient_required
def patient_appointments(request):
    """Patient View Own Appointments Only"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('login')

    appointments = Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-appointment_date')
    return render(request, 'myapp/patient_appointments.html', {'appointments': appointments, 'patient': patient})


@login_required
@patient_required
def patient_medical_records(request):
    """Patient View Own Medical Records Only"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('login')

    records = MedicalRecord.objects.filter(patient=patient).select_related('doctor').order_by('-created_at')
    return render(request, 'myapp/patient_medical_records.html', {'records': records, 'patient': patient})


@login_required
@patient_required
def patient_bills(request):
    """Patient View Own Bills Only"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('login')

    bills = Bill.objects.filter(patient=patient).order_by('-created_at')
    total_paid = bills.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
    total_unpaid = bills.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'myapp/patient_bills.html', {'bills': bills, 'patient': patient, 'total_paid': total_paid, 'total_unpaid': total_unpaid})


@login_required
@patient_required
def patient_profile(request):
    """Patient Edit Own Profile"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('login')

    if request.method == 'POST':
        patient.phone = request.POST.get('phone', patient.phone)
        patient.address = request.POST.get('address', patient.address)
        patient.emergency_contact = request.POST.get('emergency_contact', patient.emergency_contact)
        patient.blood_group = request.POST.get('blood_group', patient.blood_group)
        patient.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_profile')

    return render(request, 'myapp/patient_profile.html', {'patient': patient})


# =============================================================================
# 🔹 Admin Patient Management Views
# =============================================================================

@login_required
@admin_required
def admin_patient_detail(request, patient_id):
    """Admin View Patient Details"""
    patient = get_object_or_404(Patient, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-appointment_date')
    bills = Bill.objects.filter(patient=patient).order_by('-created_at')
    records = MedicalRecord.objects.filter(patient=patient).select_related('doctor').order_by('-created_at')

    context = {
        'patient': patient,
        'appointments': appointments,
        'bills': bills,
        'records': records,
        'user_role': 'admin',
    }
    return render(request, 'myapp/admin_patient_detail.html', context)


@login_required
@admin_required
def admin_edit_patient(request, patient_id):
    """Admin Edit Patient"""
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        patient.first_name = request.POST.get('first_name', patient.first_name)
        patient.last_name = request.POST.get('last_name', patient.last_name)
        patient.phone = request.POST.get('phone', patient.phone)
        patient.address = request.POST.get('address', patient.address)
        patient.blood_group = request.POST.get('blood_group', patient.blood_group)
        patient.save()
        messages.success(request, 'Patient updated successfully!')
        return redirect('admin_patient_detail', patient_id=patient.id)

    return render(request, 'myapp/admin_edit_patient.html', {'patient': patient})

def edit_patient(request, id):
    return HttpResponse("Edit page")

def delete_patient(request, id):
    return HttpResponse("Delete page")