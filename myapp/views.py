import string
from datetime import datetime
from random import random

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from . import models
from .models import (
    User, Hospital, HospitalAdminProfile, Doctor, DoctorSchedule,
    Patient, Appointment, ICUBed, ICUBooking, EmergencyRequest,
    Product, Cart, CartItem, Order, MedicalReport, TestReport,
    Bill, Pharmacy, PharmacyAdmin,
    PharmacyProduct, PharmacyCustomer,  # ← Prescription পরিবর্তে PharmacyPrescription
    PharmacyCart, PharmacyCartItem, PharmacyOrder, Notification, PharmacyOrderItem
)
from .utils import send_doctor_welcome_email_and_notification


# ==================== হেল্পার ফাংশন ====================

def get_user_hospital(user):
    """Get hospital for a user based on their role"""
    if user.is_superuser or user.user_type == 'super_admin':
        return None
    elif hasattr(user, 'patient_profile') and user.patient_profile.hospital:
        return user.patient_profile.hospital
    elif hasattr(user, 'doctor_profile') and user.doctor_profile.hospital:
        return user.doctor_profile.hospital
    elif hasattr(user, 'hospital_admin_profile'):
        return user.hospital_admin_profile.hospital
    return None


def check_hospital_admin(user):
    """Check if user is hospital admin and return hospital"""
    if not hasattr(user, 'hospital_admin_profile'):
        return None, False
    admin_profile = user.hospital_admin_profile
    if not admin_profile.is_active:
        return None, False
    return admin_profile.hospital, True


# ==================== অথেনটিকেশন ভিউস ====================

# myapp/views.py - লগইন ভিউ

def login_view(request):
    """User login page"""

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me') == 'on'

        print(f"Login attempt for: {email_or_username}")

        if not email_or_username or not password:
            messages.error(request, 'Please enter both email/username and password!')
            return render(request, 'myapp/login.html')

        # First try to authenticate with username
        user = authenticate(request, username=email_or_username, password=password)

        # If that fails and input contains @, try to find user by email
        if user is None and '@' in email_or_username:
            try:
                user_obj = User.objects.get(email=email_or_username)
                print(f"Found user by email: {user_obj.username}")
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                print(f"No user found with email: {email_or_username}")

        if user is not None:
            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)

            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')

            # Redirect based on user type
            if user.is_superuser:
                print("Redirecting to admin_dashboard")
                return redirect('admin_dashboard')
            elif hasattr(user, 'hospital_admin_profile') and user.hospital_admin_profile.is_active:
                print("Redirecting to hospital_dashboard")
                return redirect('hospital_dashboard')
            elif hasattr(user, 'doctor_profile'):
                print("Redirecting to doctor_dashboard")
                return redirect('doctor_dashboard')
            elif hasattr(user, 'patient_profile'):
                print("Redirecting to patient_dashboard")
                return redirect('patient_dashboard')
            elif hasattr(user, 'pharmacy_admin_profile') and user.pharmacy_admin_profile.is_active:
                print("Redirecting to pharmacy_dashboard")
                return redirect('pharmacy_dashboard')
            elif hasattr(user, 'pharmacy_customer'):
                print("Redirecting to pharmacy_customer_dashboard")
                return redirect('pharmacy_customer_dashboard')
            else:
                print("Redirecting to patient_dashboard (default)")
                return redirect('patient_dashboard')
        else:
            print(f"Login failed for: {email_or_username}")
            messages.error(request, 'Invalid email/username or password!')

    return render(request, 'myapp/login.html')

# ==================== সাইনআপ ভিউ ====================

# myapp/views.py - সম্পূর্ণ সাইনআপ ভিউ
# myapp/views.py - সাইনআপ ভিউ

def signup_view(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        blood_group = request.POST.get('blood_group', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        terms_accepted = request.POST.get('terms') == 'on'

        # Validation
        errors = []

        if not first_name:
            errors.append('First name is required')
        if not email:
            errors.append('Email is required')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already registered')
        if not phone:
            errors.append('Phone number is required')
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if password != confirm_password:
            errors.append('Passwords do not match')
        if not terms_accepted:
            errors.append('You must accept the terms and conditions')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'myapp/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
            })

        try:
            # Calculate date of birth from age
            current_year = datetime.now().year
            date_of_birth = datetime(current_year - int(age), 1, 1).date()

            # Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='patient',
                phone=phone,
                date_of_birth=date_of_birth,
                blood_group=blood_group
            )

            # ✅ গুরুত্বপূর্ণ: hospital = None রাখুন (সব হাসপাতাল দেখার জন্য)
            patient = Patient.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                date_of_birth=date_of_birth,
                gender=gender,
                blood_group=blood_group,
                hospital=None,  # ← None রাখলে সব হাসপাতাল দেখাবে
                address='',
                is_active=True
            )

            print(f"✅ Patient created: {patient.full_name}")
            print(f"Hospital assigned: {patient.hospital} (None means all hospitals visible)")

            # Login the user
            login(request, user)
            messages.success(request, f'Welcome {first_name}! Your account has been created successfully.')

            return redirect('patient_dashboard')

        except Exception as e:
            print(f"❌ Signup error: {str(e)}")
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'myapp/signup.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
            })

    return render(request, 'myapp/signup.html')

def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def forgot_password(request):
    """Forgot password page"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your email address!')
        else:
            try:
                user = User.objects.get(email=email)
                # Here you would send a password reset email
                messages.success(request, f'A password reset link has been sent to {email}')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address!')

    return render(request, 'myapp/forgot_password.html')


# ==================== সুপার অ্যাডমিন ভিউস ====================

@login_required
def admin_dashboard(request):
    """Super Admin Dashboard"""
    if not request.user.is_superuser:
        messages.error(request, 'Super Admin access required!')
        return redirect('login')

    # ফার্মেসি অ্যাডমিন কাউন্ট
    total_pharmacy_admins = PharmacyAdmin.objects.count()
    active_pharmacy_admins = PharmacyAdmin.objects.filter(is_active=True).count()

    context = {
        'total_hospitals': Hospital.objects.count(),
        'active_hospitals': Hospital.objects.filter(is_active=True).count(),
        'total_hospital_admins': HospitalAdminProfile.objects.count(),
        'active_admins': HospitalAdminProfile.objects.filter(is_active=True).count(),
        'total_pharmacy_admins': total_pharmacy_admins,
        'active_pharmacy_admins': active_pharmacy_admins,
        'total_doctors': Doctor.objects.count(),
        'total_patients': Patient.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_beds': ICUBed.objects.count(),
        'available_beds': ICUBed.objects.filter(is_available=True).count(),
        'today_appointments': Appointment.objects.filter(appointment_date__date=timezone.now().date()).count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'emergency_requests': EmergencyRequest.objects.filter(status='pending').count(),
        'recent_hospitals': Hospital.objects.order_by('-created_at')[:10],
        'recent_admins': HospitalAdminProfile.objects.select_related('user', 'hospital').order_by('-created_at')[:10],
        'total_orders': Order.objects.count(),
        'total_revenue': Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))[
                             'total_amount__sum'] or 0,
    }
    return render(request, 'myapp/admin_dashboard.html', context)

@login_required
def admin_manage_hospitals(request):
    """Super Admin: Manage all hospitals (Create, Edit, Delete, Toggle Status)"""
    if not request.user.is_superuser:
        return redirect('login')

    hospitals = Hospital.objects.all().order_by('-created_at')

    # Search
    search = request.GET.get('search')
    if search:
        hospitals = hospitals.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(address__icontains=search) |
            Q(phone__icontains=search)
        )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            # Add new hospital
            name = request.POST.get('name')
            code = request.POST.get('code')
            address = request.POST.get('address', '')
            phone = request.POST.get('phone', '')
            email = request.POST.get('email', '')

            if not name or not code:
                messages.error(request, 'Hospital name and code are required!')
            elif Hospital.objects.filter(code=code).exists():
                messages.error(request, f'Hospital code "{code}" already exists!')
            else:
                Hospital.objects.create(
                    name=name, code=code, address=address,
                    phone=phone, email=email, is_active=True
                )
                messages.success(request, f'Hospital "{name}" created successfully!')

        elif action == 'edit':
            # Edit hospital
            hospital_id = request.POST.get('hospital_id')
            hospital = get_object_or_404(Hospital, id=hospital_id)
            hospital.name = request.POST.get('name')
            hospital.code = request.POST.get('code')
            hospital.address = request.POST.get('address', '')
            hospital.phone = request.POST.get('phone', '')
            hospital.email = request.POST.get('email', '')

            # Check code uniqueness
            if Hospital.objects.filter(code=hospital.code).exclude(id=hospital_id).exists():
                messages.error(request, f'Hospital code "{hospital.code}" already exists!')
            else:
                hospital.save()
                messages.success(request, f'Hospital "{hospital.name}" updated successfully!')

        elif action == 'toggle':
            # Toggle hospital active status
            hospital_id = request.POST.get('hospital_id')
            hospital = get_object_or_404(Hospital, id=hospital_id)
            hospital.is_active = not hospital.is_active
            hospital.save()
            status = "activated" if hospital.is_active else "deactivated"
            messages.success(request, f'Hospital "{hospital.name}" {status}!')

        elif action == 'delete':
            # Delete hospital
            hospital_id = request.POST.get('hospital_id')
            hospital = get_object_or_404(Hospital, id=hospital_id)

            # Check if hospital has any admin
            if HospitalAdminProfile.objects.filter(hospital=hospital).exists():
                messages.error(request, f'Cannot delete "{hospital.name}" - has hospital admin(s)!')
            else:
                hospital_name = hospital.name
                hospital.delete()
                messages.success(request, f'Hospital "{hospital_name}" deleted successfully!')

        return redirect('admin_manage_hospitals')

    context = {
        'hospitals': hospitals,
        'total_hospitals': hospitals.count(),
        'active_hospitals': hospitals.filter(is_active=True).count(),
        'inactive_hospitals': hospitals.filter(is_active=False).count(),
        'search': search,
    }
    return render(request, 'myapp/admin_manage_hospitals.html', context)


@login_required
def admin_manage_hospital_admins(request):
    """Super Admin: Manage hospital admins (Create, Edit, Toggle, Delete)"""
    if not request.user.is_superuser:
        return redirect('login')

    admins = HospitalAdminProfile.objects.select_related('user', 'hospital').all().order_by('-created_at')

    # Search
    search = request.GET.get('search')
    if search:
        admins = admins.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(hospital__name__icontains=search)
        )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            # Create new hospital admin
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            phone = request.POST.get('phone', '')
            hospital_id = request.POST.get('hospital_id')
            designation = request.POST.get('designation', 'Hospital Admin')

            if password != confirm_password:
                messages.error(request, 'Passwords do not match!')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists!')
            else:
                hospital = get_object_or_404(Hospital, id=hospital_id)

                # Create user
                admin_user = User.objects.create_user(
                    username=username, email=email, password=password,
                    first_name=first_name, last_name=last_name,
                    user_type='hospital_admin', phone=phone
                )
                admin_user.is_staff = True
                admin_user.save()

                # Create hospital admin profile
                HospitalAdminProfile.objects.create(
                    user=admin_user, hospital=hospital,
                    designation=designation, phone=phone, is_active=True
                )
                messages.success(request, f'Hospital Admin "{username}" created for "{hospital.name}"!')

        elif action == 'edit':
            # Edit hospital admin
            admin_id = request.POST.get('admin_id')
            admin = get_object_or_404(HospitalAdminProfile, id=admin_id)
            admin.designation = request.POST.get('designation')
            admin.phone = request.POST.get('phone')
            admin.hospital_id = request.POST.get('hospital_id')
            admin.save()

            # Update user
            user = admin.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.phone = request.POST.get('phone')
            user.save()
            messages.success(request, f'Hospital Admin "{user.username}" updated!')

        elif action == 'toggle':
            # Toggle admin active status
            admin_id = request.POST.get('admin_id')
            admin = get_object_or_404(HospitalAdminProfile, id=admin_id)
            admin.is_active = not admin.is_active
            admin.save()
            status = "activated" if admin.is_active else "deactivated"
            messages.success(request, f'Hospital Admin "{admin.user.username}" {status}!')

        elif action == 'delete':
            # Delete hospital admin
            admin_id = request.POST.get('admin_id')
            admin = get_object_or_404(HospitalAdminProfile, id=admin_id)
            user = admin.user
            admin.delete()
            user.delete()
            messages.success(request, 'Hospital Admin deleted!')

        return redirect('admin_manage_hospital_admins')

    context = {
        'admins': admins,
        'total_admins': admins.count(),
        'active_admins': admins.filter(is_active=True).count(),
        'inactive_admins': admins.filter(is_active=False).count(),
        'hospitals': Hospital.objects.filter(is_active=True),
        'search': search,
    }
    return render(request, 'myapp/admin_manage_hospital_admins.html', context)


@login_required
def admin_hospital_reports(request):
    """Super Admin: View hospital reports summary"""
    if not request.user.is_superuser:
        return redirect('login')

    hospital_summary = []
    for hospital in Hospital.objects.all():
        hospital_summary.append({
            'id': hospital.id,
            'name': hospital.name,
            'code': hospital.code,
            'is_active': hospital.is_active,
            'created_at': hospital.created_at,
            'doctors': Doctor.objects.filter(hospital=hospital).count(),
            'patients': Patient.objects.filter(hospital=hospital).count(),
            'appointments': Appointment.objects.filter(hospital=hospital).count(),
            'beds': ICUBed.objects.filter(hospital=hospital).count(),
            'admin': HospitalAdminProfile.objects.filter(hospital=hospital).first(),
        })

    context = {
        'hospital_summary': hospital_summary,
        'total_hospitals': Hospital.objects.count(),
        'active_hospitals': Hospital.objects.filter(is_active=True).count(),
        'total_admins': HospitalAdminProfile.objects.count(),
        'active_admins': HospitalAdminProfile.objects.filter(is_active=True).count(),
    }
    return render(request, 'myapp/admin_hospital_reports.html', context)


@login_required
def admin_hospital_detail(request, hospital_id):
    """Super Admin: View hospital details (READ ONLY)"""
    if not request.user.is_superuser:
        return redirect('login')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    context = {
        'hospital': hospital,
        'hospital_admin': HospitalAdminProfile.objects.filter(hospital=hospital).first(),
        'doctors_count': Doctor.objects.filter(hospital=hospital).count(),
        'patients_count': Patient.objects.filter(hospital=hospital).count(),
        'appointments_count': Appointment.objects.filter(hospital=hospital).count(),
        'beds_count': ICUBed.objects.filter(hospital=hospital).count(),
        'products_count': Product.objects.filter(hospital=hospital).count(),
    }
    return render(request, 'myapp/admin_hospital_detail.html', context)
# ==================== হাসপাতাল অ্যাডমিন ভিউস ====================

# myapp/views.py - hospital_dashboard ভিউ

@login_required
def hospital_dashboard(request):
    """Hospital Admin Dashboard"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        messages.error(request, 'Access denied. Hospital Admin only!')
        return redirect('login')

    today = timezone.now().date()

    # ✅ সব ইমার্জেন্সি দেখাবে (লোকেশন ফিল্টার ছাড়া)
    emergencies = EmergencyRequest.objects.all()
    pending_emergencies = emergencies.filter(status='pending').count()
    in_transit_emergencies = emergencies.filter(status='in_transit').count()
    completed_emergencies = emergencies.filter(status='completed').count()
    recent_emergencies = emergencies.order_by('-request_time')[:5]

    context = {
        'hospital': hospital,
        'doctors_count': Doctor.objects.filter(hospital=hospital).count(),
        'patients_count': Patient.objects.filter(hospital=hospital).count(),
        'appointments_count': Appointment.objects.filter(hospital=hospital).count(),
        'beds_count': ICUBed.objects.filter(hospital=hospital).count(),
        'available_beds': ICUBed.objects.filter(hospital=hospital, is_available=True).count(),
        'today_appointments': Appointment.objects.filter(hospital=hospital, appointment_date__date=today).count(),
        'pending_appointments': Appointment.objects.filter(hospital=hospital, status='pending').count(),
        'recent_patients': Patient.objects.filter(hospital=hospital).order_by('-id')[:5],
        'recent_appointments': Appointment.objects.filter(hospital=hospital).select_related('patient',
                                                                                            'doctor').order_by('-id')[
                               :5],
        'pending_emergencies': pending_emergencies,
        'in_transit_emergencies': in_transit_emergencies,
        'completed_emergencies': completed_emergencies,
        'recent_emergencies': recent_emergencies,
    }
    return render(request, 'myapp/hospital_dashboard.html', context)

# myapp/views.py

# myapp/views.py - hospital_emergencies ভিউ

@login_required
def hospital_emergencies(request):
    """Hospital Admin: View all emergency requests"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    # ✅ সব ইমার্জেন্সি দেখাবে (লোকেশন ফিল্টার ছাড়া)
    emergencies = EmergencyRequest.objects.all().order_by('-request_time')

    # Statistics
    total = emergencies.count()
    pending = emergencies.filter(status='pending').count()
    in_transit = emergencies.filter(status='in_transit').count()
    completed = emergencies.filter(status='completed').count()

    # Filters
    status_filter = request.GET.get('status')
    if status_filter:
        emergencies = emergencies.filter(status=status_filter)

    priority_filter = request.GET.get('priority')
    if priority_filter:
        emergencies = emergencies.filter(priority=priority_filter)

    if request.method == 'POST':
        emergency_id = request.POST.get('emergency_id')
        status = request.POST.get('status')
        emergency = get_object_or_404(EmergencyRequest, id=emergency_id)
        emergency.status = status
        emergency.save()
        messages.success(request, f'Emergency #{emergency_id} status updated to {status}!')
        return redirect('hospital_emergencies')

    context = {
        'emergencies': emergencies,
        'hospital': hospital,
        'total': total,
        'pending': pending,
        'in_transit': in_transit,
        'completed': completed,
        'current_status': status_filter,
        'current_priority': priority_filter,
    }
    return render(request, 'myapp/hospital_emergencies.html', context)


# views.py - hospital_doctors ভিউ


# views.py - hospital_doctors ভিউ

@login_required
def hospital_doctors(request):
    """Hospital admin - manage doctors"""

    if not hasattr(request.user, 'hospital_admin_profile'):
        messages.error(request, 'Access denied. Hospital admin only!')
        return redirect('dashboard')

    hospital_admin = request.user.hospital_admin_profile
    hospital = hospital_admin.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            try:
                # Get form data
                first_name = request.POST.get('first_name', '').strip()
                last_name = request.POST.get('last_name', '').strip()
                username = request.POST.get('username', '').strip()
                email = request.POST.get('email', '').strip()
                password = request.POST.get('password', '')
                phone = request.POST.get('phone', '')
                specialization = request.POST.get('specialization')
                qualification = request.POST.get('qualification', '')
                experience_years = request.POST.get('experience_years', 0)
                consultation_fee = request.POST.get('consultation_fee', 500)
                bio = request.POST.get('bio', '')
                available_from = request.POST.get('available_from', '09:00')
                available_to = request.POST.get('available_to', '17:00')

                # Validation
                if not first_name or not last_name:
                    messages.error(request, 'First name and last name are required!')
                    return redirect('hospital_doctors')
                if not username:
                    messages.error(request, 'Username is required!')
                    return redirect('hospital_doctors')
                if not email:
                    messages.error(request, 'Email is required!')
                    return redirect('hospital_doctors')
                if not password:
                    messages.error(request, 'Password is required!')
                    return redirect('hospital_doctors')

                # Check if username or email exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, f'Username "{username}" already exists!')
                    return redirect('hospital_doctors')
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'Email "{email}" already exists!')
                    return redirect('hospital_doctors')

                # Create User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    user_type='doctor',
                    is_active=True
                )

                # Create Doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    hospital=hospital,
                    specialization=specialization,
                    qualification=qualification,
                    experience_years=int(experience_years) if experience_years else 0,
                    consultation_fee=float(consultation_fee) if consultation_fee else 500,
                    bio=bio,
                    available_from=available_from,
                    available_to=available_to,
                    is_available=True
                )

                # ========== 📧 ইমেইল এবং নোটিফিকেশন পাঠান ==========
                email_notification_sent = send_doctor_welcome_email_and_notification(doctor, password)

                if email_notification_sent:
                    messages.success(request,
                                     f'✅ Dr. {first_name} {last_name} added successfully! Welcome email sent & notification added to doctor\'s dashboard.')
                else:
                    messages.warning(request,
                                     f'✅ Dr. {first_name} {last_name} added but email could not be sent. Notification added to dashboard.')

                # Create default schedule
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
                for day in weekdays:
                    DoctorSchedule.objects.get_or_create(
                        doctor=doctor,
                        day=day,
                        defaults={
                            'is_available': True,
                            'start_time': available_from,
                            'end_time': available_to,
                            'max_patients': 20,
                            'consultation_duration': 30
                        }
                    )

            except Exception as e:
                messages.error(request, f'Error adding doctor: {str(e)}')

            return redirect('hospital_doctors')

        # Toggle and Delete actions...
        elif action == 'toggle':
            doctor_id = request.POST.get('doctor_id')
            try:
                doctor = Doctor.objects.get(id=doctor_id, hospital=hospital)
                doctor.is_available = not doctor.is_available
                doctor.save()
                status = "available" if doctor.is_available else "unavailable"
                messages.success(request, f'Dr. {doctor.full_name} is now {status}')
            except Doctor.DoesNotExist:
                messages.error(request, 'Doctor not found')
            return redirect('hospital_doctors')

        elif action == 'delete':
            doctor_id = request.POST.get('doctor_id')
            try:
                doctor = Doctor.objects.get(id=doctor_id, hospital=hospital)
                doctor_name = doctor.full_name
                doctor.user.delete()
                messages.success(request, f'Dr. {doctor_name} has been deleted')
            except Doctor.DoesNotExist:
                messages.error(request, 'Doctor not found')
            return redirect('hospital_doctors')

    # GET request
    doctors = Doctor.objects.filter(hospital=hospital).select_related('user')
    available_doctors = doctors.filter(is_available=True).count()
    specializations_count = doctors.values('specialization').distinct().count()

    context = {
        'hospital': hospital,
        'doctors': doctors,
        'available_doctors': available_doctors,
        'specializations_count': specializations_count,
        'specialization_choices': Doctor.SPECIALIZATION_CHOICES,
        'default_start_time': '09:00',
        'default_end_time': '17:00',
    }
    return render(request, 'myapp/hospital_doctors.html', context)


@login_required
def hospital_patients(request):
    """Manage patients of this hospital"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    patients = Patient.objects.filter(hospital=hospital).order_by('-created_at')

    if request.method == 'POST':
        patient = get_object_or_404(Patient, id=request.POST.get('patient_id'), hospital=hospital)
        if request.POST.get('action') == 'delete':
            if patient.user:
                patient.user.delete()
            patient.delete()
            messages.success(request, 'Patient deleted!')
        elif request.POST.get('action') == 'toggle':
            patient.is_active = not patient.is_active
            patient.save()
            messages.success(request, f'Patient {"activated" if patient.is_active else "deactivated"}!')

    return render(request, 'myapp/hospital_patients.html', {'patients': patients, 'hospital': hospital})


@login_required
def hospital_appointments(request):
    """Manage appointments of this hospital"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    appointments = Appointment.objects.filter(hospital=hospital).select_related('patient', 'doctor').order_by(
        '-appointment_date')

    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    search = request.GET.get('search')
    if search:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search) | Q(patient__last_name__icontains=search) |
            Q(doctor__user__first_name__icontains=search) | Q(doctor__user__last_name__icontains=search)
        )

    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=request.POST.get('appointment_id'), hospital=hospital)
        appointment.status = request.POST.get('status')
        appointment.save()
        messages.success(request, f'Appointment #{appointment.id} updated!')
        return redirect('hospital_appointments')

    context = {
        'appointments': appointments, 'hospital': hospital,
        'total': appointments.count(), 'pending': appointments.filter(status='pending').count(),
        'confirmed': appointments.filter(status='confirmed').count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
        'current_status': status_filter, 'search': search,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'myapp/hospital_appointments.html', context)


@login_required
def hospital_beds(request):
    """Manage ICU beds and view bookings of this hospital"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    beds = ICUBed.objects.filter(hospital=hospital).order_by('bed_number')

    # Get all active ICU bookings for this hospital
    active_bookings = ICUBooking.objects.filter(
        hospital=hospital,
        is_active=True
    ).select_related('patient', 'bed').order_by('-admission_date')

    # Get booking history (inactive)
    booking_history = ICUBooking.objects.filter(
        hospital=hospital,
        is_active=False
    ).select_related('patient', 'bed').order_by('-admission_date')[:20]

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            bed_number = request.POST.get('bed_number')
            if ICUBed.objects.filter(bed_number=bed_number, hospital=hospital).exists():
                messages.error(request, 'Bed number already exists!')
            else:
                ICUBed.objects.create(
                    bed_number=bed_number,
                    hospital=hospital,
                    bed_type=request.POST.get('bed_type'),
                    daily_charge=request.POST.get('daily_charge'),
                    equipment=request.POST.get('equipment', ''),
                    is_available=True
                )
                messages.success(request, f'Bed {bed_number} added!')

        elif action == 'toggle':
            bed = get_object_or_404(ICUBed, id=request.POST.get('bed_id'), hospital=hospital)
            bed.is_available = not bed.is_available
            bed.save()
            messages.success(request, f'Bed {bed.bed_number} is now {"available" if bed.is_available else "occupied"}!')

        elif action == 'delete':
            bed = get_object_or_404(ICUBed, id=request.POST.get('bed_id'), hospital=hospital)
            bed.delete()
            messages.success(request, 'Bed deleted!')

        elif action == 'discharge':
            booking_id = request.POST.get('booking_id')
            booking = get_object_or_404(ICUBooking, id=booking_id, hospital=hospital, is_active=True)
            booking.is_active = False
            booking.save()
            bed = booking.bed
            bed.is_available = True
            bed.save()
            messages.success(request, f'Patient {booking.patient_name} discharged from Bed {bed.bed_number}!')

        return redirect('hospital_beds')

    context = {
        'beds': beds,
        'active_bookings': active_bookings,
        'booking_history': booking_history,
        'hospital': hospital,
        'bed_types': ICUBed.BED_TYPES,
        'total_beds': beds.count(),
        'available_beds': beds.filter(is_available=True).count(),
        'occupied_beds': beds.filter(is_available=False).count(),
        'total_active_bookings': active_bookings.count(),
    }
    return render(request, 'myapp/hospital_beds.html', context)

@login_required
def hospital_products(request):
    """Manage pharmacy products of this hospital"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    print(f"Hospital Admin: {request.user.username}")
    print(f"Hospital: {hospital.name} (ID: {hospital.id})")

    products = Product.objects.filter(hospital=hospital).order_by('-id')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('name')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == 'on'

            # Image handling
            image = request.FILES.get('image')

            if name and price and stock:
                product = Product.objects.create(
                    name=name,
                    price=price,
                    stock=stock,
                    description=description,
                    is_active=is_active,
                    hospital=hospital  # ← হাসপাতাল সেট করা গুরুত্বপূর্ণ
                )
                if image:
                    product.image = image
                    product.save()
                print(f"Product created: {product.name} for hospital {hospital.name}")
                messages.success(request, f'Product "{name}" added!')
            else:
                messages.error(request, 'Please fill all required fields!')

        elif action == 'edit':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id, hospital=hospital)
            product.name = request.POST.get('name')
            product.price = request.POST.get('price')
            product.stock = request.POST.get('stock')
            product.description = request.POST.get('description', '')
            product.is_active = request.POST.get('is_active') == 'on'

            image = request.FILES.get('image')
            if image:
                if product.image:
                    product.image.delete()
                product.image = image

            product.save()
            messages.success(request, f'Product "{product.name}" updated!')

        elif action == 'delete':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id, hospital=hospital)
            if product.image:
                product.image.delete()
            product.delete()
            messages.success(request, 'Product deleted!')

        elif action == 'toggle':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id, hospital=hospital)
            product.is_active = not product.is_active
            product.save()
            messages.success(request, 'Product status updated!')

        return redirect('hospital_products')

    return render(request, 'myapp/hospital_products.html', {'products': products, 'hospital': hospital})


@login_required
def hospital_orders(request):
    """View orders from patients of this hospital"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    patients = Patient.objects.filter(hospital=hospital).values_list('user_id', flat=True)
    orders = Order.objects.filter(user_id__in=patients).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders, 'hospital': hospital, 'total': orders.count(),
        'pending': orders.filter(status='pending').count(),
        'confirmed': orders.filter(status='confirmed').count(),
        'delivered': orders.filter(status='delivered').count(),
        'cancelled': orders.filter(status='cancelled').count(),
        'current_status': status_filter, 'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'myapp/hospital_orders.html', context)


@login_required
def hospital_order_detail(request, order_id):
    """View order details"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    patients = Patient.objects.filter(hospital=hospital).values_list('user_id', flat=True)
    order = get_object_or_404(Order, id=order_id, user_id__in=patients)

    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.save()
        messages.success(request, f'Order #{order.order_number} status updated!')

    return render(request, 'myapp/hospital_order_detail.html',
                  {'order': order, 'items': order.items.all(), 'status_choices': Order.STATUS_CHOICES})


@login_required
def hospital_profile(request):
    """View and edit hospital profile"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    admin_profile = request.user.hospital_admin_profile

    if request.method == 'POST':
        hospital.name = request.POST.get('name')
        hospital.address = request.POST.get('address')
        hospital.phone = request.POST.get('phone')
        hospital.email = request.POST.get('email')
        hospital.save()
        admin_profile.designation = request.POST.get('designation', 'Hospital Admin')
        admin_profile.phone = request.POST.get('admin_phone', '')
        admin_profile.save()
        messages.success(request, 'Hospital profile updated!')

    return render(request, 'myapp/hospital_profile.html', {'hospital': hospital, 'admin_profile': admin_profile})


# ==================== পেশন্ট ভিউস ====================

@login_required
def patient_dashboard(request):
    """Patient Dashboard with pharmacy products"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('login')

    patient = request.user.patient_profile
    hospital = patient.hospital
    cart = Cart.objects.filter(user=request.user).first()

    # Get pharmacy products
    from .models import PharmacyProduct
    pharmacy_products = PharmacyProduct.objects.filter(is_active=True, stock__gt=0)[:4]

    # Get ICU bookings
    icu_bookings = ICUBooking.objects.filter(patient=patient).select_related('bed', 'bed__hospital')
    icu_bookings_count = icu_bookings.filter(is_active=True).count()
    recent_icu_bookings = icu_bookings.order_by('-admission_date')[:3]

    # Statistics
    upcoming = Appointment.objects.filter(
        patient=patient, appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).count()

    completed = Appointment.objects.filter(patient=patient, status='completed').count()
    total = Appointment.objects.filter(patient=patient).count()
    total_orders = Order.objects.filter(user=request.user).count()

    # Recent data
    recent_appointments = Appointment.objects.filter(patient=patient).select_related('doctor').order_by(
        '-appointment_date')[:5]

    # Next appointment
    next_appointment = Appointment.objects.filter(
        patient=patient, appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date').first()

    # Fix: cart_items_count using total_items property or fallback
    cart_items_count = 0
    if cart:
        if hasattr(cart, 'total_items'):
            cart_items_count = cart.total_items
        else:
            # Fallback: count items directly
            cart_items_count = CartItem.objects.filter(cart=cart).count()

    context = {
        'patient': patient,
        'hospital': hospital,
        'upcoming_appointments': upcoming,
        'completed_appointments': completed,
        'total_appointments': total,
        'total_orders': total_orders,
        'cart_items_count': cart_items_count,
        'recent_appointments': recent_appointments,
        'next_appointment': next_appointment,
        'pharmacy_products': pharmacy_products,
        'icu_bookings_count': icu_bookings_count,
        'recent_icu_bookings': recent_icu_bookings,
    }
    return render(request, 'myapp/patient_dashboard.html', context)


# myapp/views.py

@login_required
def patient_appointment_detail(request, appointment_id):
    """Patient appointment details view"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied!')
        return redirect('login')

    patient = request.user.patient_profile
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)

    context = {
        'appointment': appointment,
        'patient': patient,
    }
    return render(request, 'myapp/patient_appointment_detail.html', context)


# myapp/views.py - সম্পূর্ণ ফিক্সড পেশন্ট বুক অ্যাপয়েন্টমেন্ট ভিউ

@login_required
def patient_book_appointment(request):
    """Patient book a new appointment"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Only patients can book appointments!')
        return redirect('login')

    patient = request.user.patient_profile

    # Get all available doctors
    doctors = Doctor.objects.filter(is_available=True).select_related('user', 'hospital')

    # Pre-selected doctor from GET parameter
    pre_selected_doctor_id = request.GET.get('doctor')
    selected_doctor = None

    if pre_selected_doctor_id:
        try:
            selected_doctor = doctors.get(id=pre_selected_doctor_id)
        except Doctor.DoesNotExist:
            pass

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        symptoms = request.POST.get('symptoms')

        if not doctor_id:
            messages.error(request, 'Please select a doctor!')
            return redirect('patient_book_appointment')

        if not date or not time:
            messages.error(request, 'Please select date and time!')
            return redirect('patient_book_appointment')

        if not symptoms:
            messages.error(request, 'Please describe your symptoms!')
            return redirect('patient_book_appointment')

        try:
            doctor = get_object_or_404(Doctor, id=int(doctor_id), is_available=True)
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            appointment_datetime = timezone.make_aware(appointment_datetime)

            if appointment_datetime < timezone.now():
                messages.error(request, 'Please select a future date and time!')
                return redirect('patient_book_appointment')

            # Check for duplicate
            if Appointment.objects.filter(patient=patient, doctor=doctor, appointment_date=appointment_datetime,
                                          status__in=['pending', 'confirmed']).exists():
                messages.error(request, 'You already have an appointment at this time!')
                return redirect('patient_book_appointment')

            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                hospital=doctor.hospital,
                appointment_date=appointment_datetime,
                symptoms=symptoms,
                status='pending'
            )

            messages.success(request, f'✓ Appointment booked with Dr. {doctor.full_name} on {date} at {time}')
            return redirect('patient_my_appointments')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('patient_book_appointment')

    context = {
        'doctors': doctors,
        'selected_doctor': selected_doctor,
    }
    return render(request, 'myapp/patient_book_appointment.html', context)

@login_required
def patient_my_appointments(request):
    """View all appointments of the patient"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('login')

    patient = request.user.patient_profile
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-appointment_date')

    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    return render(request, 'myapp/patient_my_appointments.html', {
        'appointments': appointments,
        'total': appointments.count(),
        'pending': appointments.filter(status='pending').count(),
        'confirmed': appointments.filter(status='confirmed').count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
        'current_status': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    })


@login_required
def patient_cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient_profile)
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully!')
    return redirect('patient_my_appointments')


# myapp/views.py - পেশন্ট ডাক্তার লিস্ট ভিউ

# myapp/views.py - পেশন্ট ডাক্তার ভিউ

@login_required
def patient_doctors(request):
    """View all doctors from ALL hospitals (no restriction)"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('login')

    patient = request.user.patient_profile

    # ✅ সব হাসপাতালের ডাক্তার দেখাবে (hospital ফিল্টার নেই)
    doctors = Doctor.objects.filter(is_available=True).select_related('user', 'hospital')

    print(f"Total doctors found: {doctors.count()}")

    # Filter by hospital (if selected)
    hospital_id = request.GET.get('hospital')
    if hospital_id:
        doctors = doctors.filter(hospital_id=hospital_id)

    # Filter by specialization
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization=specialization)

    # Search by name
    search = request.GET.get('search')
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )

    # Get all hospitals for filter
    hospitals = Hospital.objects.filter(is_active=True)

    context = {
        'doctors': doctors,
        'hospitals': hospitals,
        'selected_hospital': hospital_id,
        'specializations': Doctor.SPECIALIZATION_CHOICES,
        'current_specialization': specialization,
        'search': search,
        'total_doctors': doctors.count(),
    }
    return render(request, 'myapp/patient_doctors.html', context)

@login_required
def patient_test_reports(request):
    """View all test reports of the patient"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('login')

    reports = TestReport.objects.filter(patient=request.user.patient_profile).order_by('-report_date')
    return render(request, 'myapp/patient_test_reports.html', {
        'reports': reports,
        'total_reports': reports.count(),
        'pending_reports': reports.filter(status='pending').count(),
        'completed_reports': reports.filter(status='completed').count(),
        'urgent_reports': reports.filter(is_urgent=True).count(),
    })


@login_required
def patient_test_report_detail(request, report_id):
    """View single test report details"""
    report = get_object_or_404(TestReport, id=report_id, patient=request.user.patient_profile)
    return render(request, 'myapp/patient_test_report_detail.html', {'report': report})




# ==================== প্রেসক্রিপশন আপলোড ====================

class Prescription:
    objects = None


@login_required
def pharmacy_upload_prescription(request):
    """Patient upload prescription for medicine order"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('login')

    patient = request.user.patient_profile

    if request.method == 'POST':
        image = request.FILES.get('prescription_image')
        doctor_name = request.POST.get('doctor_name', '')
        notes = request.POST.get('notes', '')

        if not image:
            messages.error(request, 'Please upload a prescription image!')
        else:
            prescription = Prescription.objects.create(
                customer=patient,  # Note: Requires migration
                prescription_image=image,
                doctor_name=doctor_name,
                notes=notes,
                status='pending'
            )
            messages.success(request, f'Prescription #{prescription.id} uploaded successfully!')
            return redirect('pharmacy_prescriptions')

    return render(request, 'myapp/pharmacy_upload_prescription.html')


@login_required
def pharmacy_prescriptions(request):
    """View patient's prescriptions"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('login')

    patient = request.user.patient_profile
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-created_at')

    context = {
        'prescriptions': prescriptions,
        'total': prescriptions.count(),
        'pending': prescriptions.filter(status='pending').count(),
        'verified': prescriptions.filter(status='verified').count(),
    }
    return render(request, 'myapp/pharmacy_prescriptions.html', context)

# myapp/views.py - আইসিইউ বেড ভিউ

# myapp/views.py - পেশন্ট আইসিইউ বেড ভিউস

@login_required
def patient_icu_beds(request):
    """View all ICU beds from ALL hospitals"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('login')

    patient = request.user.patient_profile

    # Get all available ICU beds
    beds = ICUBed.objects.filter(is_available=True).select_related('hospital')

    # Filter by hospital
    hospital_id = request.GET.get('hospital')
    if hospital_id:
        beds = beds.filter(hospital_id=hospital_id)

    # Filter by bed type
    bed_type = request.GET.get('type')
    if bed_type:
        beds = beds.filter(bed_type=bed_type)

    # Get all hospitals for filter
    hospitals = Hospital.objects.filter(is_active=True)

    # Statistics
    total_beds = beds.count()
    available_beds = beds.filter(is_available=True).count()
    occupied_beds = beds.filter(is_available=False).count()

    context = {
        'beds': beds,
        'hospitals': hospitals,
        'selected_hospital': hospital_id,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'bed_types': ICUBed.BED_TYPES,
    }
    return render(request, 'myapp/patient_icu_beds.html', context)


@login_required
def patient_book_icu_bed(request, bed_id):
    """Book an ICU bed"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('login')

    patient = request.user.patient_profile
    bed = get_object_or_404(ICUBed, id=bed_id, is_available=True)

    if request.method == 'POST':
        try:
            expected_discharge = request.POST.get('expected_discharge')
            condition = request.POST.get('condition')

            # Create ICU booking
            booking = ICUBooking.objects.create(
                patient=patient,
                bed=bed,
                hospital=bed.hospital,
                patient_name=patient.full_name,
                patient_age=patient.age,
                contact_number=patient.phone,
                expected_discharge=expected_discharge,
                condition=condition,
                is_active=True
            )

            # Make bed unavailable
            bed.is_available = False
            bed.save()

            messages.success(request, f'✓ ICU Bed {bed.bed_number} at {bed.hospital.name} booked successfully!')
            return redirect('patient_icu_bookings')

        except Exception as e:
            messages.error(request, f'Error booking bed: {str(e)}')
            return redirect('patient_icu_beds')

    context = {
        'bed': bed,
        'hospital': bed.hospital,
    }
    return render(request, 'myapp/patient_book_icu_bed.html', context)


@login_required
def patient_icu_bookings(request):
    """View patient's ICU bookings (both active and discharged)"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('login')

    patient = request.user.patient_profile

    # Get ALL bookings (both active and inactive/discharged)
    all_bookings = ICUBooking.objects.filter(patient=patient).select_related('bed', 'hospital').order_by(
        '-admission_date')

    # Separate active and inactive bookings
    active_bookings_list = all_bookings.filter(is_active=True)
    inactive_bookings_list = all_bookings.filter(is_active=False)

    # Calculate statistics
    active_count = active_bookings_list.count()
    inactive_count = inactive_bookings_list.count()
    total_count = all_bookings.count()

    # Debug print (check console)
    print(f"=== ICU BOOKINGS DEBUG ===")
    print(f"Patient: {patient.full_name} (ID: {patient.id})")
    print(f"Total bookings: {total_count}")
    print(f"Active bookings: {active_count}")
    print(f"Inactive/Discharged bookings: {inactive_count}")

    for booking in all_bookings:
        print(
            f"Booking ID: {booking.id} - Active: {booking.is_active} - Bed: {booking.bed.bed_number if booking.bed else 'No Bed'} - Hospital: {booking.hospital.name if booking.hospital else 'No Hospital'}")

    context = {
        'bookings': all_bookings,  # All bookings
        'active_bookings': active_count,
        'inactive_bookings': inactive_count,  # Discharged/Cancelled bookings
        'total_bookings': total_count,
    }
    return render(request, 'myapp/patient_icu_bookings.html', context)


@login_required
def patient_delete_icu_booking(request, booking_id):
    """Permanently delete a discharged booking record"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied')
        return redirect('login')

    try:
        booking = get_object_or_404(
            ICUBooking,
            id=booking_id,
            patient=request.user.patient_profile,
            is_active=False  # Only allow deleting inactive/discharged bookings
        )

        booking.delete()
        messages.success(request, 'Booking record has been permanently deleted!')

    except Exception as e:
        messages.error(request, f'Error deleting booking: {str(e)}')

    return redirect('patient_icu_bookings')

@login_required
def patient_cancel_icu_booking(request, booking_id):
    """Cancel/Discharge an ICU booking"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied')
        return redirect('login')

    try:
        booking = get_object_or_404(
            ICUBooking,
            id=booking_id,
            patient=request.user.patient_profile
        )

        # Get info for message
        bed_number = booking.bed.bed_number if booking.bed else 'N/A'
        hospital_name = booking.hospital.name if booking.hospital else 'Hospital'

        if booking.is_active:
            # Make bed available again
            if booking.bed:
                booking.bed.is_available = True
                booking.bed.save()

            # Mark booking as inactive (discharged)
            booking.is_active = False
            booking.save()

            messages.success(request,
                             f'✓ ICU Bed {bed_number} at {hospital_name} has been discharged/cancelled successfully!')
        else:
            messages.warning(request, 'This booking is already discharged!')

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('patient_icu_bookings')


@login_required
def patient_profile(request):
    """View and edit patient profile"""
    patient = request.user.patient_profile

    if request.method == 'POST':
        # প্রফাইল আপডেট করুন
        patient.first_name = request.POST.get('first_name')
        patient.last_name = request.POST.get('last_name')
        patient.phone = request.POST.get('phone')
        patient.emergency_contact = request.POST.get('emergency_contact')
        patient.address = request.POST.get('address')
        patient.blood_group = request.POST.get('blood_group')

        # date_of_birth আপডেট করুন
        dob = request.POST.get('date_of_birth')
        if dob:
            try:
                from datetime import datetime
                patient.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                pass

        if request.POST.get('gender'):
            patient.gender = request.POST.get('gender')

        patient.save()

        # User model আপডেট করুন
        user = request.user
        user.first_name = patient.first_name
        user.last_name = patient.last_name
        user.phone = patient.phone
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_profile')

    context = {
        'patient': patient,
    }
    return render(request, 'myapp/patient_profile.html', context)

# ==================== ডাক্তার ভিউস ====================

@login_required
def doctor_dashboard(request):
    """Doctor Dashboard with Notifications and Appointments"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    doctor = request.user.doctor_profile
    today = timezone.now().date()

    # ========== Get Notifications ==========
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:10]

    unread_notification_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    all_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:20]

    # ========== Today's Appointments ==========
    # appointment_time না থাকায় appointment_date ব্যবহার করছি
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date=today,
        status__in=['pending', 'confirmed']
    ).select_related('patient', 'patient__user').order_by('appointment_date')

    today_appointments_count = today_appointments.count()
    today_appointments_list = today_appointments[:10]

    # ========== Upcoming Appointments ==========
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date__gt=today,
        status__in=['pending', 'confirmed']
    ).select_related('patient', 'patient__user').order_by('appointment_date')[:10]

    # ========== Recent Appointments (last 10) ==========
    recent_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient', 'patient__user').order_by('-appointment_date')[:10]

    # ========== Statistics ==========
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    pending_appointments = Appointment.objects.filter(doctor=doctor, status='pending').count()
    confirmed_appointments = Appointment.objects.filter(doctor=doctor, status='confirmed').count()
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='completed').count()
    cancelled_appointments = Appointment.objects.filter(doctor=doctor, status='cancelled').count()

    total_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()

    context = {
        # Doctor Info
        'doctor': doctor,

        # Notifications
        'notifications': notifications,
        'unread_notification_count': unread_notification_count,
        'all_notifications': all_notifications,

        # Today's Appointments
        'today_appointments_count': today_appointments_count,
        'today_appointments': today_appointments_list,

        # Upcoming Appointments
        'upcoming_appointments': upcoming_appointments,

        # Recent Appointments
        'recent_appointments': recent_appointments,

        # Statistics
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_patients': total_patients,

        # Current date/time
        'current_date': today,
        'current_time': timezone.now().time(),
    }
    return render(request, 'myapp/doctor_dashboard.html', context)

# ==================== ইউনিভার্সাল ড্যাশবোর্ড ====================


# views.py

# views.py - dashboard ভিউ

@login_required
def dashboard(request):
    """Universal dashboard redirect based on user type"""
    print("=== DASHBOARD REDIRECT ===")
    print(f"User: {request.user.username}")
    print(f"Is superuser: {request.user.is_superuser}")
    print(f"User type before: {request.user.user_type}")

    # Force fix for superuser
    if request.user.is_superuser and request.user.user_type != 'super_admin':
        print("Fixing user_type for superuser...")
        request.user.user_type = 'super_admin'
        request.user.save()
        print(f"User type after fix: {request.user.user_type}")

    # Now redirect based on user_type
    if request.user.user_type == 'super_admin':
        print("Redirecting to super admin dashboard")
        return redirect('admin_dashboard')

    elif request.user.user_type == 'hospital_admin':
        print("Redirecting to hospital admin dashboard")
        return redirect('hospital_dashboard')

    elif request.user.user_type == 'doctor':
        print("Redirecting to doctor dashboard")
        return redirect('doctor_dashboard')

    elif request.user.user_type == 'patient':
        print("Redirecting to patient dashboard")
        return redirect('patient_dashboard')

    elif request.user.user_type == 'pharmacy_admin':
        print("Redirecting to pharmacy admin dashboard")
        return redirect('pharmacy_dashboard')

    else:
        print("No valid user_type - default to patient dashboard")
        return redirect('patient_dashboard')
# ==================== ইমার্জেন্সি ভিউস ====================

def emergency(request):
    """Emergency request page"""
    # Get all active hospitals
    hospitals = Hospital.objects.filter(is_active=True)

    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        patient_age = request.POST.get('patient_age', '')
        contact_number = request.POST.get('contact_number', '').strip()
        emergency_type = request.POST.get('emergency_type', '')
        location = request.POST.get('location', '').strip()
        priority = request.POST.get('priority', 'medium')
        additional_info = request.POST.get('additional_info', '')
        allergies = request.POST.get('allergies', '')
        hospital_id = request.POST.get('hospital_id', '')

        # Validate hospital selection
        if not hospital_id:
            messages.error(request, 'Please select a hospital!')
            return render(request, 'myapp/emergency.html', {'hospitals': hospitals})

        try:
            hospital = Hospital.objects.get(id=hospital_id, is_active=True)
        except Hospital.DoesNotExist:
            messages.error(request, 'Invalid hospital selection!')
            return render(request, 'myapp/emergency.html', {'hospitals': hospitals})

        errors = []

        if not patient_name:
            errors.append('Patient name is required')
        if not patient_age or not patient_age.isdigit():
            errors.append('Valid age is required')
        if not contact_number:
            errors.append('Contact number is required')
        if not emergency_type:
            errors.append('Emergency type is required')
        if not location:
            errors.append('Location is required')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                emergency = EmergencyRequest.objects.create(
                    patient_name=patient_name,
                    patient_age=int(patient_age),
                    contact_number=contact_number,
                    emergency_type=emergency_type,
                    location=location,
                    priority=priority,
                    additional_info=f"Hospital: {hospital.name}\nAllergies: {allergies or 'None'}\n{additional_info}"
                )
                messages.success(request,
                                 f'🚑 Ambulance {emergency.assigned_ambulance} dispatched from {hospital.name}! Estimated arrival: {emergency.estimated_arrival.strftime("%I:%M %p")}')
                return redirect('emergency_success', request_id=emergency.id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

    context = {
        'hospitals': hospitals,
    }
    return render(request, 'myapp/emergency.html', context)


def emergency_success(request, request_id):
    """Emergency success page"""
    emergency = get_object_or_404(EmergencyRequest, id=request_id)
    return render(request, 'myapp/emergency_success.html', {'emergency': emergency})


# ==================== সাধারণ ভিউস ====================

def contact(request):
    return render(request, 'myapp/contact.html')


def about(request):
    return render(request, 'myapp/about.html')


def faq(request):
    return render(request, 'myapp/faq.html')


# ==================== অতিরিক্ত ডাক্তার ভিউস ====================

@login_required
def doctor_profile(request):
    """Doctor profile view and edit"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('login')

    doctor = request.user.doctor_profile

    if request.method == 'POST':
        doctor.specialization = request.POST.get('specialization')
        doctor.qualification = request.POST.get('qualification')
        doctor.experience_years = request.POST.get('experience_years')
        doctor.consultation_fee = request.POST.get('consultation_fee')
        doctor.bio = request.POST.get('bio')
        doctor.available_from = request.POST.get('available_from')
        doctor.available_to = request.POST.get('available_to')
        doctor.save()

        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('doctor_profile')

    return render(request, 'myapp/doctor_profile.html', {'doctor': doctor})


@login_required
def doctor_appointments(request):
    """View all appointments of the doctor"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    doctor = request.user.doctor_profile

    # Base query - appointment_time নেই, তাই শুধু appointment_date দিয়ে order
    all_appointments = Appointment.objects.filter(doctor=doctor).select_related('patient').order_by('-appointment_date')

    # Total count (before filter)
    total_count = all_appointments.count()

    # Status counts (before filter)
    pending_count = Appointment.objects.filter(doctor=doctor, status='pending').count()
    confirmed_count = Appointment.objects.filter(doctor=doctor, status='confirmed').count()
    completed_count = Appointment.objects.filter(doctor=doctor, status='completed').count()
    cancelled_count = Appointment.objects.filter(doctor=doctor, status='cancelled').count()

    # Apply status filter
    status_filter = request.GET.get('status')
    appointments = all_appointments

    if status_filter and status_filter != 'all':
        appointments = appointments.filter(status=status_filter)

    # Apply search filter
    search_query = request.GET.get('search')
    if search_query:
        appointments = appointments.filter(patient__full_name__icontains=search_query)

    # Apply date filter
    date_filter = request.GET.get('date')
    if date_filter:
        appointments = appointments.filter(appointment_date__date=date_filter)

    context = {
        'appointments': appointments,
        'total': total_count,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'current_status': status_filter,
        'search': search_query if search_query else '',
        'date_filter': date_filter if date_filter else '',
        'status_choices': Appointment.STATUS_CHOICES,
        'doctor': doctor,
    }
    return render(request, 'myapp/doctor_appointments.html', context)

@login_required
def doctor_today_appointments(request):
    """View today's appointments of the doctor"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('login')

    doctor = request.user.doctor_profile
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date=today
    ).select_related('patient').order_by('appointment_date')

    return render(request, 'myapp/doctor_today_appointments.html', {'appointments': appointments})


@login_required
def doctor_update_appointment(request, appointment_id):
    """Doctor update appointment status"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if status in ['pending', 'confirmed', 'completed', 'cancelled']:
            appointment.status = status
            appointment.notes = notes
            appointment.save()

            # পেশন্টকে নোটিফিকেশন পাঠান
            from .utils import send_notification_to_user
            send_notification_to_user(
                user=appointment.patient.user,
                title=f'Appointment {status.title()}',
                message=f'Your appointment with Dr. {doctor.full_name} on {appointment.appointment_date} has been {status}.',
                notification_type='appointment',
                link=f'/patient/appointment/{appointment.id}/'
            )

            messages.success(request, f'Appointment {status} successfully!')
        else:
            messages.error(request, 'Invalid status!')

        return redirect('doctor_appointments')

    context = {
        'appointment': appointment,
        'doctor': doctor,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'myapp/doctor_update_appointment.html', context)

def get_doctor_schedule(request, doctor_id):
    from .models import DoctorSchedule
    from django.http import JsonResponse

    schedules = DoctorSchedule.objects.filter(doctor_id=doctor_id).values('day', 'is_available', 'start_time',
                                                                          'end_time')
    schedule_list = []

    for s in schedules:
        schedule_list.append({
            'day': s['day'],
            'is_available': s['is_available'],
            'start_time': s['start_time'].strftime('%H:%M') if s['start_time'] else '09:00',
            'end_time': s['end_time'].strftime('%H:%M') if s['end_time'] else '17:00',
        })

    return JsonResponse({'schedules': schedule_list})


@login_required
def doctor_patients(request):
    """Doctor's patients list"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    doctor = request.user.doctor_profile

    # যেসব পেশন্ট অ্যাপয়েন্টমেন্ট করেছেন তাদের ইউনিক আইডি বের করুন
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')

    # ইউনিক পেশন্ট আইডি বের করুন
    patient_ids = appointments.values_list('patient_id', flat=True).distinct()

    # পেশন্ট ডিটেইলস নিন
    patients = Patient.objects.filter(id__in=patient_ids, is_active=True).order_by('-created_at')

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q() |
            models.Q(phone__icontains=search_query)
        )

    # Blood group filter
    blood_group = request.GET.get('blood_group', '')
    if blood_group:
        patients = patients.filter(blood_group=blood_group)

    # Active patients count
    active_patients = patients.count()

    # Total appointments count
    total_appointments = appointments.count()

    context = {
        'doctor': doctor,
        'patients': patients,
        'active_patients': active_patients,
        'total_appointments': total_appointments,
        'search': search_query,
        'blood_group': blood_group,
    }
    return render(request, 'myapp/doctor_patients.html', context)

@login_required
def doctor_patient_detail(request, patient_id):
    """View patient details and medical history"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('login')

    doctor = request.user.doctor_profile
    patient = get_object_or_404(Patient, id=patient_id, assigned_doctor=doctor)

    appointments = Appointment.objects.filter(patient=patient, doctor=doctor).order_by('-appointment_date')
    medical_reports = MedicalReport.objects.filter(patient=patient, doctor=doctor).order_by('-created_at')
    test_reports = TestReport.objects.filter(patient=patient, doctor=doctor).order_by('-report_date')

    return render(request, 'myapp/doctor_patient_detail.html', {
        'patient': patient,
        'appointments': appointments,
        'medical_reports': medical_reports,
        'test_reports': test_reports,
    })


@login_required
def doctor_schedule(request):
    """Manage doctor's schedule"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('login')

    doctor = request.user.doctor_profile

    if request.method == 'POST':
        doctor.available_from = request.POST.get('available_from')
        doctor.available_to = request.POST.get('available_to')
        doctor.save()
        messages.success(request, 'Schedule updated successfully!')
        return redirect('doctor_schedule')

    return render(request, 'myapp/doctor_schedule.html', {'doctor': doctor})


@login_required
def hospital_test_reports(request):
    """Hospital admin manage test reports"""
    hospital, is_admin = check_hospital_admin(request.user)
    if not is_admin:
        return redirect('login')

    reports = TestReport.objects.filter(hospital=hospital).select_related('patient', 'doctor').order_by('-report_date')
    patients = Patient.objects.filter(hospital=hospital, is_active=True)
    doctors = Doctor.objects.filter(hospital=hospital, is_available=True)

    selected_patient = None
    patient_id = request.GET.get('patient_id')
    if patient_id:
        try:
            selected_patient = Patient.objects.get(id=patient_id, hospital=hospital)
            reports = reports.filter(patient=selected_patient)
        except:
            pass

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_report':
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
            report_type = request.POST.get('report_type')
            report_title = request.POST.get('report_title')
            findings = request.POST.get('findings')
            test_results = request.POST.get('test_results')
            interpretation = request.POST.get('interpretation')
            recommendations = request.POST.get('recommendations', '')
            test_date = request.POST.get('test_date')
            is_urgent = request.POST.get('is_urgent') == 'on'

            if not patient_id or not doctor_id:
                messages.error(request, 'Please select patient and doctor!')
            else:
                TestReport.objects.create(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    hospital=hospital,
                    report_type=report_type,
                    report_title=report_title,
                    findings=findings,
                    test_results=test_results,
                    interpretation=interpretation,
                    recommendations=recommendations,
                    test_date=test_date,
                    is_urgent=is_urgent,
                    status='completed'
                )
                messages.success(request, 'Test report added successfully!')
                return redirect('hospital_test_reports')

        elif action == 'delete':
            report_id = request.POST.get('report_id')
            report = get_object_or_404(TestReport, id=report_id, hospital=hospital)
            report.delete()
            messages.success(request, 'Report deleted successfully!')

        return redirect('hospital_test_reports')

    context = {
        'reports': reports,
        'hospital': hospital,
        'patients': patients,
        'doctors': doctors,
        'selected_patient': selected_patient,
        'report_types': TestReport.REPORT_TYPES,
    }
    return render(request, 'myapp/hospital_test_reports.html', context)


class Bill:
    PAYMENT_METHOD = None
    objects = None


# myapp/views.py - পেশন্ট বিল ভিউস

# myapp/views.py - পেশন্ট বিল ভিউস

from django.db.models import Sum
from django.utils import timezone
import uuid


@login_required
def patient_bills(request):
    """Patient view all bills"""
    from .models import Bill

    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('login')

    patient = request.user.patient_profile

    # চেক করুন Bill মডেলটি কাজ করছে কিনা
    try:
        bills = Bill.objects.filter(patient=patient).order_by('-created_at')
    except Exception as e:
        print(f"Bill model error: {e}")
        messages.warning(request, 'Billing system is being updated.')
        bills = []

    context = {
        'bills': bills,
        'total_bills': bills.count() if bills else 0,
        'pending_count': bills.filter(status='pending').count() if bills else 0,
        'paid_count': bills.filter(status='paid').count() if bills else 0,
    }
    return render(request, 'myapp/patient_bills.html', context)

@login_required
def patient_bill_detail(request, bill_id):
    """Patient view bill details"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('login')

    patient = request.user.patient_profile
    bill = get_object_or_404(Bill, id=bill_id, patient=patient)

    return render(request, 'myapp/patient_bill_detail.html', {'bill': bill})


@login_required
def patient_pay_bill(request, bill_id):
    """Patient pay a bill"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('login')

    patient = request.user.patient_profile
    bill = get_object_or_404(Bill, id=bill_id, patient=patient, status='pending')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if not payment_method:
            messages.error(request, 'Please select a payment method!')
            return redirect('patient_pay_bill', bill_id=bill_id)

        # Process payment
        bill.status = 'paid'
        bill.payment_method = payment_method
        bill.payment_date = timezone.now()
        bill.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        bill.save()

        messages.success(request, f'Payment successful! Transaction ID: {bill.transaction_id}')
        return redirect('patient_bill_detail', bill_id=bill.id)

    context = {
        'bill': bill,
        'payment_methods': Bill.PAYMENT_METHOD,
    }
    return render(request, 'myapp/patient_pay_bill.html', context)


@login_required
def create_appointment_bill(request, appointment_id):
    """Create bill for an appointment (after appointment is confirmed)"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('login')

    patient = request.user.patient_profile
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)

    # Check if bill already exists
    existing_bill = Bill.objects.filter(appointment=appointment).first()
    if existing_bill:
        messages.info(request, f'Bill already exists for this appointment.')
        return redirect('patient_bill_detail', bill_id=existing_bill.id)

    # Create bill
    bill = Bill.objects.create(
        patient=patient,
        doctor=appointment.doctor,
        appointment=appointment,
        amount=appointment.doctor.consultation_fee,
        discount=0,
        tax=0,
        status='pending',
        description=f"Consultation fee for Dr. {appointment.doctor.full_name} on {appointment.appointment_date.strftime('%Y-%m-%d')}"
    )

    messages.success(request, f'Bill #{bill.bill_number} created successfully!')
    return redirect('patient_pay_bill', bill_id=bill.id)

@login_required
def get_doctors_by_hospital(request):
    """AJAX view to get doctors by hospital"""
    if request.method == 'GET':
        hospital_id = request.GET.get('hospital_id')
        if hospital_id:
            try:
                doctors = Doctor.objects.filter(hospital_id=hospital_id, is_available=True).select_related('user')
                doctors_list = []
                for doctor in doctors:
                    doctors_list.append({
                        'id': doctor.id,
                        'name': doctor.full_name,
                        'specialization': doctor.specialization,
                        'specialization_display': doctor.get_specialization_display(),
                        'fee': str(doctor.consultation_fee),
                        'experience': doctor.experience_years,
                        'qualification': doctor.qualification,
                        'rating': str(doctor.rating),
                    })
                return JsonResponse({'doctors': doctors_list, 'success': True})
            except Exception as e:
                return JsonResponse({'doctors': [], 'success': False, 'error': str(e)})
    return JsonResponse({'doctors': [], 'success': False})

@login_required
def get_beds_by_hospital(request):
    """AJAX view to get ICU beds by hospital"""
    if request.method == 'GET':
        hospital_id = request.GET.get('hospital_id')
        if hospital_id:
            try:
                beds = ICUBed.objects.filter(hospital_id=hospital_id).select_related('hospital')
                beds_list = []
                for bed in beds:
                    beds_list.append({
                        'id': bed.id,
                        'bed_number': bed.bed_number,
                        'bed_type': bed.bed_type,
                        'is_available': bed.is_available,
                        'daily_charge': str(bed.daily_charge),
                        'equipment': bed.equipment,
                    })
                return JsonResponse({'beds': beds_list, 'success': True})
            except Exception as e:
                return JsonResponse({'beds': [], 'success': False, 'error': str(e)})
    return JsonResponse({'beds': [], 'success': False})


# myapp/views.py - ফার্মেসি অ্যাডমিন ভিউস

# ==================== সুপার অ্যাডমিন: ফার্মেসি অ্যাডমিন তৈরি ====================


# myapp/views.py

@login_required
def super_admin_pharmacy_admins(request):
    """Super admin - Manage pharmacies and pharmacy admins"""
    if request.user.user_type != 'super_admin':
        messages.error(request, 'Access denied! Only super admin can access this page.')
        return redirect('dashboard')

    pharmacies = Pharmacy.objects.all().order_by('-created_at')
    pharmacy_admins = PharmacyAdmin.objects.all().select_related('user', 'pharmacy')

    if request.method == 'POST':
        action = request.POST.get('action')
        print(f"=== POST Request Received ===")
        print(f"Action: {action}")
        print(f"POST Data: {request.POST}")

        # ========== Create Pharmacy ==========
        if action == 'create_pharmacy':
            try:
                name = request.POST.get('name')
                code = request.POST.get('code')
                address = request.POST.get('address')
                phone = request.POST.get('phone')
                email = request.POST.get('email')
                delivery_charge = request.POST.get('delivery_charge', 50)
                free_delivery_above = request.POST.get('free_delivery_above', 500)

                if not name or not code:
                    messages.error(request, 'Pharmacy name and code are required!')
                    return redirect('super_admin_pharmacy_admins')

                if Pharmacy.objects.filter(code=code).exists():
                    messages.error(request, f'Pharmacy code "{code}" already exists!')
                    return redirect('super_admin_pharmacy_admins')

                Pharmacy.objects.create(
                    name=name,
                    code=code,
                    address=address,
                    phone=phone,
                    email=email,
                    delivery_charge=delivery_charge,
                    free_delivery_above=free_delivery_above,
                    is_active=True
                )
                messages.success(request, f'✅ Pharmacy "{name}" created successfully!')

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

            return redirect('super_admin_pharmacy_admins')

        # ========== Create Pharmacy Admin ==========
        elif action == 'create_admin':
            try:
                print("=== Creating Pharmacy Admin ===")

                # Get form data
                pharmacy_id = request.POST.get('pharmacy_id')
                first_name = request.POST.get('first_name', '').strip()
                last_name = request.POST.get('last_name', '').strip()
                username = request.POST.get('username', '').strip()
                email = request.POST.get('email', '').strip()
                password = request.POST.get('password', '')
                confirm_password = request.POST.get('confirm_password', '')
                phone = request.POST.get('phone', '').strip()
                designation = request.POST.get('designation', 'Pharmacy Manager')

                print(f"Pharmacy ID: {pharmacy_id}")
                print(f"First Name: {first_name}")
                print(f"Last Name: {last_name}")
                print(f"Username: {username}")
                print(f"Email: {email}")

                # Validation
                if not pharmacy_id:
                    messages.error(request, 'Please select a pharmacy!')
                    return redirect('super_admin_pharmacy_admins')

                if not first_name:
                    messages.error(request, 'First name is required!')
                    return redirect('super_admin_pharmacy_admins')

                if not last_name:
                    messages.error(request, 'Last name is required!')
                    return redirect('super_admin_pharmacy_admins')

                if not username:
                    messages.error(request, 'Username is required!')
                    return redirect('super_admin_pharmacy_admins')

                if not email:
                    messages.error(request, 'Email is required!')
                    return redirect('super_admin_pharmacy_admins')

                if not password:
                    messages.error(request, 'Password is required!')
                    return redirect('super_admin_pharmacy_admins')

                if not confirm_password:
                    messages.error(request, 'Confirm password is required!')
                    return redirect('super_admin_pharmacy_admins')

                if password != confirm_password:
                    messages.error(request, 'Passwords do not match!')
                    return redirect('super_admin_pharmacy_admins')

                if len(password) < 6:
                    messages.error(request, 'Password must be at least 6 characters long!')
                    return redirect('super_admin_pharmacy_admins')

                # Check if username exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, f'Username "{username}" already exists!')
                    return redirect('super_admin_pharmacy_admins')

                # Check if email exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'Email "{email}" already exists!')
                    return redirect('super_admin_pharmacy_admins')

                # Get pharmacy
                pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
                print(f"Pharmacy found: {pharmacy.name}")

                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    user_type='pharmacy_admin'
                )
                print(f"User created: ID={user.id}")

                # Create pharmacy admin
                admin = PharmacyAdmin.objects.create(
                    user=user,
                    pharmacy=pharmacy,
                    phone=phone,
                    designation=designation,
                    is_active=True
                )
                print(f"Pharmacy Admin created: ID={admin.id}")

                messages.success(request, f'✅ Pharmacy Admin "{first_name} {last_name}" created successfully for "{pharmacy.name}"!')

            except Exception as e:
                print(f"Error creating admin: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f'Error: {str(e)}')

            return redirect('super_admin_pharmacy_admins')

        # ========== Toggle Pharmacy ==========
        elif action == 'toggle_pharmacy':
            pharmacy_id = request.POST.get('pharmacy_id')
            pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
            pharmacy.is_active = not pharmacy.is_active
            pharmacy.save()
            status = "activated" if pharmacy.is_active else "deactivated"
            messages.success(request, f'Pharmacy "{pharmacy.name}" {status}!')
            return redirect('super_admin_pharmacy_admins')

        # ========== Delete Pharmacy ==========
        elif action == 'delete_pharmacy':
            pharmacy_id = request.POST.get('pharmacy_id')
            pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
            pharmacy_name = pharmacy.name
            pharmacy.delete()
            messages.success(request, f'Pharmacy "{pharmacy_name}" deleted successfully!')
            return redirect('super_admin_pharmacy_admins')

        # ========== Delete Admin ==========
        elif action == 'delete_admin':
            admin_id = request.POST.get('admin_id')
            admin = get_object_or_404(PharmacyAdmin, id=admin_id)
            admin_name = admin.user.get_full_name()
            admin.user.delete()
            messages.success(request, f'Admin "{admin_name}" deleted successfully!')
            return redirect('super_admin_pharmacy_admins')

        else:
            print(f"Unknown action: {action}")
            messages.error(request, 'Invalid action!')
            return redirect('super_admin_pharmacy_admins')

    context = {
        'pharmacies': pharmacies,
        'pharmacy_admins': pharmacy_admins,
    }
    return render(request, 'myapp/super_admin_pharmacy_admins.html', context)


@login_required
def create_pharmacy_admin(request):
    """Super admin - Create pharmacy admin"""
    # Check if user is super admin
    if request.user.user_type != 'super_admin':
        messages.error(request, 'Access denied! Only super admin can access this page.')
        return redirect('dashboard')

    # Get all active pharmacies
    pharmacies = Pharmacy.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        try:
            print("=== CREATE PHARMACY ADMIN POST ===")
            print(f"POST Data: {request.POST}")

            # Get form data
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            phone = request.POST.get('phone', '')
            pharmacy_id = request.POST.get('pharmacy_id')
            designation = request.POST.get('designation', 'Pharmacy Manager')

            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Pharmacy ID: {pharmacy_id}")
            print(f"First Name: {first_name}")
            print(f"Last Name: {last_name}")

            # Validation
            if not username:
                messages.error(request, 'Username is required!')
                return redirect('create_pharmacy_admin')

            if not email:
                messages.error(request, 'Email is required!')
                return redirect('create_pharmacy_admin')

            if not password:
                messages.error(request, 'Password is required!')
                return redirect('create_pharmacy_admin')

            if not confirm_password:
                messages.error(request, 'Confirm password is required!')
                return redirect('create_pharmacy_admin')

            if password != confirm_password:
                messages.error(request, 'Passwords do not match!')
                return redirect('create_pharmacy_admin')

            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters!')
                return redirect('create_pharmacy_admin')

            # Check if username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists!')
                return redirect('create_pharmacy_admin')

            # Check if email exists
            if User.objects.filter(email=email).exists():
                messages.error(request, f'Email "{email}" already exists!')
                return redirect('create_pharmacy_admin')

            # Check if pharmacy exists
            if not pharmacy_id:
                messages.error(request, 'Please select a pharmacy!')
                return redirect('create_pharmacy_admin')

            pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
            print(f"Pharmacy found: {pharmacy.name}")

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                user_type='pharmacy_admin'
            )
            print(f"User created: ID={user.id}")

            # Create pharmacy admin
            admin = PharmacyAdmin.objects.create(
                user=user,
                pharmacy=pharmacy,
                phone=phone,
                designation=designation,
                is_active=True
            )
            print(f"Pharmacy Admin created: ID={admin.id}")

            messages.success(request,
                             f'✅ Pharmacy Admin "{first_name} {last_name}" created successfully for "{pharmacy.name}"!')
            return redirect('super_admin_pharmacy_admins')

        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error: {str(e)}')
            return redirect('create_pharmacy_admin')

    context = {
        'pharmacies': pharmacies,
    }
    return render(request, 'myapp/create_pharmacy_admin.html', context)


# myapp/views.py - ফার্মেসি অ্যাডমিন ভিউস
@login_required
def super_admin_create_pharmacy_admin(request):
    """Super Admin: Create Pharmacy Admin for a pharmacy"""
    if request.user.user_type != 'super_admin':
        messages.error(request, 'Access denied! Only super admin can access this page.')
        return redirect('dashboard')

    pharmacies = Pharmacy.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        pharmacy_id = request.POST.get('pharmacy_id')
        designation = request.POST.get('designation', 'Pharmacy Manager')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters!')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
        elif not pharmacy_id:
            messages.error(request, 'Please select a pharmacy!')
        else:
            pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)

            # Create user
            admin_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='pharmacy_admin',
                phone=phone
            )

            # Create pharmacy admin profile
            PharmacyAdmin.objects.create(
                user=admin_user,
                pharmacy=pharmacy,
                phone=phone,
                designation=designation,
                is_active=True
            )

            messages.success(request, f'✅ Pharmacy Admin "{username}" created for "{pharmacy.name}"!')
            return redirect('super_admin_pharmacy_admins')

    context = {
        'pharmacies': pharmacies,
    }
    return render(request, 'myapp/create_pharmacy_admin.html', context)




# views.py - pharmacy_dashboard

@login_required
def pharmacy_dashboard(request):
    """Pharmacy admin dashboard"""
    if not hasattr(request.user, 'pharmacy_admin_profile'):
        messages.error(request, 'Access denied!')
        return redirect('dashboard')

    profile = request.user.pharmacy_admin_profile
    pharmacy = profile.pharmacy

    if not pharmacy:
        messages.error(request, 'No pharmacy assigned!')
        return redirect('dashboard')

    # Statistics
    products = PharmacyProduct.objects.filter(pharmacy=pharmacy)
    orders = PharmacyOrder.objects.filter(pharmacy=pharmacy)

    total_products = products.count()
    low_stock = products.filter(stock__lt=20, stock__gt=0).count()
    out_of_stock = products.filter(stock=0).count()
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    total_revenue = orders.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'pharmacy': pharmacy,
        'total_products': total_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'myapp/pharmacy_dashboard.html', context)
# views.py

@login_required
def pharmacy_admin_products(request):
    """Pharmacy admin - Manage products"""
    if not hasattr(request.user, 'pharmacy_admin_profile'):
        messages.error(request, 'Access denied!')
        return redirect('dashboard')

    pharmacy = request.user.pharmacy_admin_profile.pharmacy

    # ✅ সাবধানে প্রোডাক্ট আনুন
    products = PharmacyProduct.objects.filter(pharmacy=pharmacy).order_by('-created_at')

    # ✅ ডাটা ক্লিনিং - নিশ্চিত করুন সব প্রাইস ভ্যালিড
    for product in products:
        if product.price is None:
            product.price = 0
        if product.mrp is None:
            product.mrp = 0
        # Decimal এর জন্য স্ট্রিং কনভার্ট
        try:
            float(product.price)
        except (TypeError, ValueError):
            product.price = 0
            product.save()
        try:
            float(product.mrp)
        except (TypeError, ValueError):
            product.mrp = 0
            product.save()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            try:
                name = request.POST.get('name')
                category = request.POST.get('category')
                price = request.POST.get('price')
                stock = request.POST.get('stock')
                description = request.POST.get('description', '')
                is_active = request.POST.get('is_active') == 'true'

                # ✅ প্রাইস ভ্যালিডেশন
                if not price:
                    price = 0
                else:
                    try:
                        price = float(price)
                    except ValueError:
                        price = 0

                PharmacyProduct.objects.create(
                    pharmacy=pharmacy,
                    name=name,
                    category=category,
                    price=price,
                    stock=int(stock) if stock else 0,
                    description=description,
                    is_active=is_active
                )
                messages.success(request, f'Product "{name}" added successfully!')

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

        elif action == 'edit':
            try:
                product_id = request.POST.get('product_id')
                product = get_object_or_404(PharmacyProduct, id=product_id, pharmacy=pharmacy)

                price = request.POST.get('price')
                if not price:
                    price = 0
                else:
                    try:
                        price = float(price)
                    except ValueError:
                        price = 0

                product.name = request.POST.get('name')
                product.category = request.POST.get('category')
                product.price = price
                product.stock = request.POST.get('stock')
                product.description = request.POST.get('description', '')
                product.is_active = request.POST.get('is_active') == 'true'
                product.save()

                messages.success(request, f'Product "{product.name}" updated successfully!')

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

        elif action == 'delete':
            try:
                product_id = request.POST.get('product_id')
                product = get_object_or_404(PharmacyProduct, id=product_id, pharmacy=pharmacy)
                product_name = product.name
                product.delete()
                messages.success(request, f'Product "{product_name}" deleted successfully!')

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

        return redirect('pharmacy_products')

    total_products = products.count()
    low_stock = products.filter(stock__lt=20, stock__gt=0).count()
    out_of_stock = products.filter(stock=0).count()
    categories = PharmacyProduct.CATEGORY_CHOICES

    context = {
        'products': products,
        'total_products': total_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'categories': categories,
    }
    return render(request, 'myapp/pharmacy_products.html', context)


# views.py - ফার্মেসি অর্ডার লিস্ট

@login_required
def pharmacy_orders(request):
    """Pharmacy admin - View all orders"""
    if not hasattr(request.user, 'pharmacy_admin_profile'):
        messages.error(request, 'Access denied!')
        return redirect('dashboard')

    pharmacy = request.user.pharmacy_admin_profile.pharmacy

    if not pharmacy:
        messages.error(request, 'No pharmacy assigned to your account!')
        return redirect('dashboard')

    orders = PharmacyOrder.objects.filter(pharmacy=pharmacy).order_by('-created_at')

    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    search = request.GET.get('search')
    if search:
        orders = orders.filter(order_number__icontains=search)

    total_orders = orders.count()
    pending_orders = PharmacyOrder.objects.filter(pharmacy=pharmacy, status='pending').count()
    confirmed_orders = PharmacyOrder.objects.filter(pharmacy=pharmacy, status='confirmed').count()
    processing_orders = PharmacyOrder.objects.filter(pharmacy=pharmacy, status='processing').count()
    delivered_orders = PharmacyOrder.objects.filter(pharmacy=pharmacy, status='delivered').count()
    cancelled_orders = PharmacyOrder.objects.filter(pharmacy=pharmacy, status='cancelled').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'processing_orders': processing_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'current_status': status,
        'search': search,
        'pharmacy': pharmacy,
    }
    return render(request, 'myapp/pharmacy_orders.html', context)

@login_required
def pharmacy_order_detail(request, order_id):
    """Pharmacy Admin: View order details"""
    if not hasattr(request.user, 'pharmacy_admin_profile'):
        messages.error(request, 'Access denied!')
        return redirect('dashboard')

    pharmacy_admin = request.user.pharmacy_admin_profile
    order = get_object_or_404(PharmacyOrder, id=order_id, pharmacy=pharmacy_admin.pharmacy)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(PharmacyOrder.STATUS_CHOICES):
            order.status = status
            order.save()
            messages.success(request, f'Order #{order.order_number} updated!')
            return redirect('pharmacy_order_detail', order_id=order.id)

    context = {
        'order': order,
        'items': order.items.all(),
        'status_choices': PharmacyOrder.STATUS_CHOICES,
    }
    return render(request, 'myapp/pharmacy_order_detail.html', context)


# myapp/views.py - পেশন্ট ফার্মেসি ভিউ

# views.py

def pharmacy_products_list(request):
    """Display pharmacy products for patients (public view)"""
    from .models import PharmacyProduct

    print("=" * 60)
    print("PHARMACY PRODUCTS LIST VIEW CALLED")
    print("=" * 60)

    # শুধুমাত্র active এবং stock > 0 products দেখান
    products = PharmacyProduct.objects.filter(is_active=True, stock__gt=0)

    # Debug print
    print(f"Total products found: {products.count()}")

    # প্রতিটি প্রোডাক্টের তথ্য দেখান
    for p in products:
        print(f"  - ID: {p.id}, Name: {p.name}, Category: {p.category}, Price: {p.price}, Stock: {p.stock}")

    # Filtering
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
        print(f"Filtered by category: {category}, New count: {products.count()}")

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
        print(f"Filtered by min_price: {min_price}")
    if max_price:
        products = products.filter(price__lte=max_price)
        print(f"Filtered by max_price: {max_price}")

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'name_asc':
        products = products.order_by('name')
        print("Sorted by name (A-Z)")
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
        print("Sorted by name (Z-A)")
    elif sort_by == 'price_asc':
        products = products.order_by('price')
        print("Sorted by price (Low to High)")
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
        print("Sorted by price (High to Low)")

    # Categories for filter
    categories = []
    category_choices = dict(PharmacyProduct.CATEGORY_CHOICES)
    for cat_code, cat_name in category_choices.items():
        count = products.filter(category=cat_code).count()
        if count > 0:
            categories.append({
                'id': cat_code,
                'name': cat_name,
                'product_count': count
            })
            print(f"Category: {cat_name}, Count: {count}")

    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }

    print(f"Final products count in context: {context['total_products']}")
    print("=" * 60)

    return render(request, 'myapp/pharmacy_products_list.html', context)

@login_required
def pharmacy_add_to_cart(request, product_id):
    """Add product to cart"""
    try:
        product = get_object_or_404(PharmacyProduct, id=product_id, is_active=True)

        if product.stock <= 0:
            messages.error(request, f'{product.name} is out of stock!')
            return redirect('pharmacy_products_list')

        customer, created = PharmacyCustomer.objects.get_or_create(user=request.user)
        cart, cart_created = PharmacyCart.objects.get_or_create(customer=customer)

        cart_item, item_created = PharmacyCartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not item_created:
            quantity = int(request.POST.get('quantity', 1))
            if cart_item.quantity + quantity <= product.stock:
                cart_item.quantity += quantity
                cart_item.save()
                messages.success(request, f'Added {quantity} more {product.name} to cart.')
            else:
                messages.warning(request, f'Cannot add more. Only {product.stock - cart_item.quantity} left.')
        else:
            messages.success(request, f'{product.name} added to cart!')

        return redirect('pharmacy_cart')

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('pharmacy_products_list')

@login_required
def pharmacy_cart(request):
    """Display cart"""
    customer = PharmacyCustomer.objects.filter(user=request.user).first()

    if customer:
        cart = PharmacyCart.objects.filter(customer=customer).first()
        if cart:
            cart_items = cart.items.all().select_related('product')
            subtotal = sum(item.subtotal for item in cart_items)
            total_items = cart.items.count()
            delivery_charge = 50
            total = subtotal + delivery_charge
        else:
            cart_items = []
            subtotal = 0
            total_items = 0
            delivery_charge = 0
            total = 0
    else:
        cart_items = []
        subtotal = 0
        total_items = 0
        delivery_charge = 0
        total = 0

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_items': total_items,
        'delivery_charge': delivery_charge,
        'total': total,
    }
    return render(request, 'myapp/pharmacy_cart.html', context)


def pharmacy_update_cart(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(PharmacyCartItem, id=item_id, cart__customer__user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            if quantity <= cart_item.product.stock:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully!')
            else:
                messages.error(request, f'Only {cart_item.product.stock} items available in stock!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')

    return redirect('pharmacy_cart')


# কার্ট থেকে রিমুভ ভিউ
@login_required
def pharmacy_remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(PharmacyCartItem, id=item_id, cart__customer__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('pharmacy_cart')


# views.py - চেকআউট ভিউ আপডেট করুন

# views.py - চেকআউট ভিউ

# views.py - চেকআউট ভিউ সম্পূর্ণ আপডেট

class Decimal:
    pass


@login_required
def pharmacy_checkout(request):
    """Checkout page - Order summary and payment"""
    from decimal import Decimal  # ফাংশনের ভিতরেও ইম্পোর্ট করতে পারেন

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('patient_products')

    cart_items = CartItem.objects.filter(cart=cart).select_related('product')

    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('patient_products')

    subtotal = sum(item.total_price() for item in cart_items)
    delivery_charge = Decimal('50') if subtotal < Decimal('500') else Decimal('0')
    tax = subtotal * Decimal('0.02')
    grand_total = subtotal + delivery_charge + tax

    if request.method == 'POST':
        try:
            # ফাংশনের ভিতরে Decimal ইম্পোর্ট
            from decimal import Decimal
            import random
            from datetime import datetime

            # Get or create pharmacy customer
            customer, created = PharmacyCustomer.objects.get_or_create(
                user=request.user,
                defaults={
                    'phone': request.POST.get('phone'),
                    'address': request.POST.get('address')
                }
            )

            # Get pharmacy
            pharmacy = Pharmacy.objects.first()
            if not pharmacy:
                pharmacy = Pharmacy.objects.create(
                    name="CareFusion Pharmacy",
                    code="CFP001",
                    address="Dhaka, Bangladesh",
                    phone="01700000000",
                    email="pharmacy@carefusion.com"
                )

            # Generate order number
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

            # Decimal কে float এ কনভার্ট না করে সরাসরি ব্যবহার করুন
            subtotal_decimal = subtotal if isinstance(subtotal, Decimal) else Decimal(str(subtotal))
            delivery_charge_decimal = delivery_charge if isinstance(delivery_charge, Decimal) else Decimal(
                str(delivery_charge))
            grand_total_decimal = grand_total if isinstance(grand_total, Decimal) else Decimal(str(grand_total))

            # Create order
            order = PharmacyOrder.objects.create(
                order_number=order_number,
                customer=customer,
                pharmacy=pharmacy,
                subtotal=subtotal_decimal,
                delivery_charge=delivery_charge_decimal,
                total_amount=grand_total_decimal,
                shipping_address=request.POST.get('address'),
                phone=request.POST.get('phone'),
                payment_method=request.POST.get('payment_method', 'cod'),
                status='pending',
                payment_status='pending'
            )

            # Create order items
            for cart_item in cart_items:
                PharmacyOrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

                # Update stock
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            # Clear cart
            cart_items.delete()

            messages.success(request, f'Order placed successfully! Order ID: {order.order_number}')
            return redirect('pharmacy_order_confirmation', order_id=order.id)

        except Exception as e:
            print(f"Error: {str(e)}")
            messages.error(request, f'Error placing order: {str(e)}')
            return redirect('pharmacy_checkout')

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'tax': tax,
        'total': grand_total,
        'total_items': sum(item.quantity for item in cart_items),
    }
    return render(request, 'myapp/checkout.html', context)


# views.py - এই ভিউটি যোগ করুন

@login_required
def pharmacy_order_confirmation(request, order_id):
    """Order confirmation page"""
    from .models import PharmacyOrder

    customer = PharmacyCustomer.objects.filter(user=request.user).first()

    if not customer:
        messages.error(request, 'Customer not found!')
        return redirect('pharmacy_products_list')

    order = get_object_or_404(PharmacyOrder, id=order_id, customer=customer)
    order_items = order.items.all().select_related('product')

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'myapp/pharmacy_order_confirmation.html', context)


@login_required
def pharmacy_update_order_status(request, order_id):
    """Update order status via POST"""
    if not hasattr(request.user, 'pharmacy_admin_profile'):
        messages.error(request, 'Access denied!')
        return redirect('dashboard')

    if request.method == 'POST':
        order = get_object_or_404(PharmacyOrder, id=order_id)
        new_status = request.POST.get('status')

        if new_status in dict(PharmacyOrder.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.order_number} status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status!')

        return redirect('pharmacy_orders')

    return redirect('pharmacy_orders')


@login_required
def patient_orders(request):
    """Patient - View my pharmacy orders"""
    # প্রথমে PharmacyCustomer চেক করুন
    try:
        customer = PharmacyCustomer.objects.filter(user=request.user).first()
    except Exception as e:
        print(f"Error getting PharmacyCustomer: {e}")
        customer = None

    if not customer:
        messages.info(request, 'No orders found.')
        return render(request, 'myapp/patient_orders.html', {'orders': [], 'current_status': None})

    orders = PharmacyOrder.objects.filter(customer=customer).order_by('-created_at')

    # স্ট্যাটাস ফিল্টার
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    context = {
        'orders': orders,
        'current_status': status,
    }
    return render(request, 'myapp/patient_orders.html', context)


@login_required
def patient_order_detail(request, order_id):
    """Patient - View order details"""
    try:
        customer = PharmacyCustomer.objects.filter(user=request.user).first()
    except Exception:
        customer = None

    if not customer:
        messages.error(request, 'Order not found!')
        return redirect('patient_dashboard')

    order = get_object_or_404(PharmacyOrder, id=order_id, customer=customer)
    order_items = order.items.all().select_related('product')

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'myapp/patient_order_detail.html', context)


@login_required
def patient_cancel_order(request, order_id):
    """Patient - Cancel order"""
    if request.method == 'POST':
        try:
            customer = PharmacyCustomer.objects.filter(user=request.user).first()
            order = get_object_or_404(PharmacyOrder, id=order_id, customer=customer)

            if order.status == 'pending':
                order.status = 'cancelled'
                order.save()
                return JsonResponse({'success': True, 'message': 'Order cancelled successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Cannot cancel this order!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request!'})

# views.py - ডাক্তারের শিডিউল দেখার ভিউ

# views.py - ডাক্তারের শিডিউল দেখার ভিউ

@login_required
def doctor_schedule(request):
    """Doctor - View and manage schedule"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied!')
        return redirect('dashboard')

    doctor = request.user.doctor_profile
    schedules = DoctorSchedule.objects.filter(doctor=doctor).order_by('day')

    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        schedule = get_object_or_404(DoctorSchedule, id=schedule_id, doctor=doctor)

        schedule.is_available = request.POST.get('is_available') == 'on'
        schedule.start_time = request.POST.get('start_time')
        schedule.end_time = request.POST.get('end_time')
        schedule.max_patients = request.POST.get('max_patients')
        schedule.consultation_duration = request.POST.get('consultation_duration')
        schedule.save()

        messages.success(request, 'Schedule updated successfully!')
        return redirect('doctor_schedule')

    context = {
        'schedules': schedules,
        'doctor': doctor,
    }
    return render(request, 'myapp/doctor_schedule.html', context)

# views.py

def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def check_email(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


# views.py

@login_required
def patient_doctor_detail(request, doctor_id):
    """Patient view doctor details"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('login')

    doctor = get_object_or_404(Doctor, id=doctor_id, is_available=True)

    # Get doctor's schedule
    from .models import DoctorSchedule
    schedules = DoctorSchedule.objects.filter(doctor=doctor, is_available=True).order_by('day')

    context = {
        'doctor': doctor,
        'schedules': schedules,
    }
    return render(request, 'myapp/patient_doctor_detail.html', context)


# views.py - add_to_cart ভিউ

# views.py - add_to_cart ভিউ

@login_required
def add_to_cart(request, product_id):
    """Add product to cart and redirect to cart page"""
    if request.method == 'POST':
        try:
            # Get the product
            product = get_object_or_404(PharmacyProduct, id=product_id, is_active=True)
            print(f"Product found: {product.name}, Stock: {product.stock}")

            # Check stock
            if product.stock <= 0:
                message = f'Sorry, {product.name} is out of stock!'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': message})
                messages.error(request, message)
                return redirect(request.META.get('HTTP_REFERER', 'patient_products'))

            # Get or create cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            quantity = int(request.POST.get('quantity', 1))

            # Check if product already in cart
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()

            if cart_item:
                # Update existing cart item
                new_quantity = cart_item.quantity + quantity
                if new_quantity <= product.stock:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    message = f'✅ Updated {product.name} quantity to {cart_item.quantity}'
                else:
                    message = f'⚠️ Only {product.stock} items available!'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': message})
                    messages.warning(request, message)
                    return redirect(request.META.get('HTTP_REFERER', 'patient_products'))
            else:
                # Create new cart item
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                message = f'✅ {product.name} added to cart!'

            # Calculate cart count
            cart_items = CartItem.objects.filter(cart=cart)
            cart_count = sum(item.quantity for item in cart_items)

            # AJAX request handler
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'cart_count': cart_count
                })

            # Normal POST request - redirect to cart page
            messages.success(request, message)
            return redirect('pharmacy_cart')

        except Exception as e:
            print(f"ERROR in add_to_cart: {str(e)}")
            import traceback
            traceback.print_exc()
            error_msg = f'Error: {str(e)}'

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg})

            messages.error(request, error_msg)
            return redirect('patient_products')

    # GET request - redirect to products page
    return redirect('patient_products')



@login_required
def view_cart(request):
    """View shopping cart"""
    from decimal import Decimal

    cart = Cart.objects.filter(user=request.user).first()

    if cart:
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        subtotal = sum(item.total_price() for item in cart_items)

        # Decimal এর সাথে Decimal ব্যবহার করুন
        delivery_charge = Decimal('50') if subtotal < Decimal('500') else Decimal('0')
        tax = subtotal * Decimal('0.02')  # 0.02 কে Decimal এ রূপান্তর করুন
        total = subtotal + delivery_charge + tax
        cart_count = sum(item.quantity for item in cart_items)
    else:
        cart_items = []
        subtotal = Decimal('0')
        delivery_charge = Decimal('0')
        tax = Decimal('0')
        total = Decimal('0')
        cart_count = 0

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'tax': tax,
        'total': total,
        'cart_items_count': cart_count,
    }
    return render(request, 'myapp/pharmacy_cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        # CartItem মডেল ব্যবহার করুন, PharmacyCartItem না
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} removed from cart!')
    except Exception as e:
        messages.error(request, f'Error removing item: {str(e)}')

    return redirect('pharmacy_cart')


@login_required
def update_cart_quantity(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')

    return redirect('pharmacy_cart')

def generate_simple_password():
    """সিম্পল পাসওয়ার্ড জেনারেটর"""
    # 2 uppercase + 2 lowercase + 2 digits
    uppercase = ''.join(random.choices(string.ascii_uppercase, k=2))
    lowercase = ''.join(random.choices(string.ascii_lowercase, k=2))
    digits = ''.join(random.choices(string.digits, k=2))
    return uppercase + lowercase + digits + "@123"


# views.py

@login_required
def doctor_login_info(request, doctor_id):
    """ডাক্তারের লগইন তথ্য দেখানোর জন্য (শুধু হাসপাতাল অ্যাডমিন দেখতে পারবে)"""

    # Check if user is hospital admin
    if not hasattr(request.user, 'hospital_admin_profile'):
        messages.error(request, 'Access denied!')
        return redirect('dashboard')

    doctor = get_object_or_404(Doctor, id=doctor_id)

    context = {
        'doctor': doctor,
        'username': doctor.user.username,
        'email': doctor.user.email,
    }
    return render(request, 'myapp/doctor_login_info.html', context)


@login_required
def doctor_appointment_detail(request, appointment_id):
    """Doctor view appointment details"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['confirmed', 'completed', 'cancelled']:
            appointment.status = status
            appointment.save()
            messages.success(request, f'Appointment status updated to {status}')

            # Send notification to patient
            from .utils import send_notification_to_user
            send_notification_to_user(
                user=appointment.patient.user,
                title=f'Appointment {status.title()}',
                message=f'Your appointment with Dr. {doctor.full_name} on {appointment.appointment_date} has been {status}.',
                notification_type='appointment',
                link=f'/patient/appointment/{appointment.id}/'
            )

            return redirect('doctor_appointment_detail', appointment_id=appointment.id)

    context = {
        'appointment': appointment,
        'doctor': doctor,
    }
    return render(request, 'myapp/doctor_appointment_detail.html', context)


@login_required
def doctor_notifications(request):
    """Doctor notifications page"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    if request.method == 'POST':
        # Mark all as read
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read!')
        return redirect('doctor_notifications')

    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'myapp/doctor_notifications.html', context)


@login_required
def doctor_mark_notification_read(request, notification_id):
    """Mark single notification as read"""
    if not hasattr(request.user, 'doctor_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)

    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect(request.META.get('HTTP_REFERER', 'doctor_dashboard'))


@login_required
def doctor_update_appointment(request, appointment_id):
    """Doctor update appointment status"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if request.method == 'POST':
        status = request.POST.get('status')

        if status in ['pending', 'confirmed', 'completed', 'cancelled']:
            appointment.status = status
            appointment.save()

            # পেশন্টকে নোটিফিকেশন পাঠান
            from .utils import send_notification_to_user
            send_notification_to_user(
                user=appointment.patient.user,
                title=f'Appointment {status.title()}',
                message=f'Your appointment with Dr. {doctor.full_name} on {appointment.appointment_date} has been {status}.',
                notification_type='appointment',
                link=f'/patient/appointment/{appointment.id}/'
            )

            messages.success(request, f'Appointment {status} successfully!')
        else:
            messages.error(request, 'Invalid status!')

        return redirect('doctor_appointments')

    context = {
        'appointment': appointment,
        'doctor': doctor,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'myapp/doctor_update_appointment.html', context)


