from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    User, Doctor, Appointment, ICUBed, ICUBooking, EmergencyRequest,
    Product, Cart, CartItem, Order, OrderItem, Patient, MedicalReport, Hospital
)

User = get_user_model()


# ==================== হেল্পার ফাংশন ====================
def get_user_hospital(user):
    """Get hospital for a user"""
    if user.is_superuser:
        return None
    elif hasattr(user, 'patient_profile') and user.patient_profile.hospital:
        return user.patient_profile.hospital
    elif hasattr(user, 'doctor_profile') and user.doctor_profile.hospital:
        return user.doctor_profile.hospital
    return None


# myapp/views.py - login_view ফাংশনটি আপডেট করুন

# myapp/views.py

# myapp/views.py

def login_view(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email_or_username, password=password)

        if user is None and '@' in email_or_username:
            try:
                users = User.objects.filter(email=email_or_username)
                if users.exists():
                    user_obj = users.first()
                    user = authenticate(request, username=user_obj.username, password=password)
            except:
                pass

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {user.get_full_name() or user.username}!')

            # ইউজার টাইপ অনুযায়ী সঠিক ড্যাশবোর্ডে রিডাইরেক্ট
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'hospital_admin_profile'):
                return redirect('hospital_dashboard')
            elif hasattr(user, 'doctor_profile'):
                return redirect('doctor_dashboard')
            elif hasattr(user, 'patient_profile'):
                return redirect('patient_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid username/email or password')
            return redirect('login')

    return render(request, 'myapp/login.html')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        errors = []

        if not email:
            errors.append('Email is required')
        elif User.objects.filter(username=email).exists():
            errors.append('Email already registered')

        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters')

        if password != confirm_password:
            errors.append('Passwords do not match')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'myapp/signup.html')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name or email.split('@')[0],
                last_name=last_name
            )
            user.phone = phone
            user.user_type = 'patient'
            user.save()

            Patient.objects.create(
                user=user,
                first_name=first_name or email.split('@')[0],
                last_name=last_name,
                phone=phone,
                date_of_birth='1990-01-01',
                gender='male',
                address=''
            )

            login(request, user)
            messages.success(request, f'Welcome {first_name}! Your account has been created.')
            return redirect('patient_dashboard')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')

    return render(request, 'myapp/signup.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ==================== সুপার অ্যাডমিন ভিউস ====================
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Admin access required!')
        return redirect('patient_dashboard')

    context = {
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_beds': ICUBed.objects.count(),
        'available_beds': ICUBed.objects.filter(is_available=True).count(),
        'today_appointments': Appointment.objects.filter(appointment_date__date=timezone.now().date()).count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'emergency_requests': EmergencyRequest.objects.filter(status='pending').count(),
        'recent_patients': Patient.objects.order_by('-created_at')[:10],
        'recent_appointments': Appointment.objects.select_related('doctor', 'patient').order_by('-created_at')[:10],
    }
    return render(request, 'myapp/admin_dashboard.html', context)


@login_required
def admin_manage_patients(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    patients = Patient.objects.all()

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        action = request.POST.get('action')
        patient = get_object_or_404(Patient, id=patient_id)

        if action == 'delete':
            if patient.user:
                patient.user.delete()
            patient.delete()
            messages.success(request, 'Patient deleted successfully!')
        elif action == 'toggle_status':
            patient.is_active = not patient.is_active
            patient.save()
            status = "activated" if patient.is_active else "deactivated"
            messages.success(request, f'Patient {status}!')

    return render(request, 'myapp/admin_manage_patients.html', {'patients': patients})


@login_required
def admin_manage_doctors(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    doctors = Doctor.objects.select_related('user').all()

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        action = request.POST.get('action')
        doctor = get_object_or_404(Doctor, id=doctor_id)

        if action == 'delete':
            user = doctor.user
            doctor.delete()
            user.delete()
            messages.success(request, 'Doctor deleted successfully!')
        elif action == 'toggle_availability':
            doctor.is_available = not doctor.is_available
            doctor.save()
            status = "available" if doctor.is_available else "unavailable"
            messages.success(request, f'Doctor is now {status}!')

    return render(request, 'myapp/admin_manage_doctors.html', {'doctors': doctors})


@login_required
def admin_add_doctor(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name') or ''
        last_name = request.POST.get('last_name') or 'Doctor'
        phone = request.POST.get('phone') or ''
        specialization = request.POST.get('specialization')
        qualification = request.POST.get('qualification') or ''
        experience = request.POST.get('experience') or 0
        fee = request.POST.get('fee') or 0

        if not email or not password:
            messages.error(request, 'Email and password required!')
            return redirect('admin_add_doctor')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('admin_add_doctor')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.phone = phone
        user.user_type = 'doctor'
        user.save()

        Doctor.objects.create(
            user=user,
            specialization=specialization,
            qualification=qualification,
            experience_years=int(experience),
            consultation_fee=float(fee)
        )

        messages.success(request, 'Doctor added successfully!')
        return redirect('admin_manage_doctors')

    return render(request, 'myapp/admin_add_doctor.html', {'specializations': Doctor.SPECIALIZATION_CHOICES})


@login_required
def admin_edit_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)

    if request.method == 'POST':
        doctor.specialization = request.POST.get('specialization')
        doctor.qualification = request.POST.get('qualification')
        doctor.experience_years = request.POST.get('experience')
        doctor.consultation_fee = request.POST.get('fee')
        doctor.save()
        messages.success(request, 'Doctor updated successfully!')
        return redirect('admin_manage_doctors')

    return render(request, 'myapp/admin_edit_doctor.html', {'doctor': doctor})


@login_required
def admin_delete_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    user = doctor.user
    doctor.delete()
    user.delete()
    messages.success(request, 'Doctor deleted successfully!')
    return redirect('admin_manage_doctors')


@login_required
def admin_manage_appointments(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    appointments = Appointment.objects.select_related('patient', 'doctor').all().order_by('-appointment_date')

    if request.method == 'POST':
        apt_id = request.POST.get('appointment_id')
        status = request.POST.get('status')
        appointment = get_object_or_404(Appointment, id=apt_id)
        appointment.status = status
        appointment.save()
        messages.success(request, 'Appointment updated!')

    return render(request, 'myapp/admin_manage_appointments.html', {'appointments': appointments})


# myapp/views.py

@login_required
def admin_manage_beds(request):
    """Manage ICU beds - for super admin and hospital admin"""

    # Check if user is super admin or hospital admin
    if request.user.is_superuser:
        # Super admin sees all beds
        beds = ICUBed.objects.all().order_by('-id')
        hospital = None
    elif hasattr(request.user, 'hospital_admin_profile'):
        # Hospital admin sees only their hospital's beds
        hospital = request.user.hospital_admin_profile.hospital
        beds = ICUBed.objects.filter(hospital=hospital).order_by('-id')
    else:
        messages.error(request, 'Access denied!')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'toggle':
            # Toggle bed availability
            bed_id = request.POST.get('bed_id')
            bed = get_object_or_404(ICUBed, id=bed_id)

            # Check permission for hospital admin
            if not request.user.is_superuser and bed.hospital != hospital:
                messages.error(request, 'Access denied!')
                return redirect('admin_manage_beds')

            bed.is_available = not bed.is_available
            bed.save()
            status = "available" if bed.is_available else "occupied"
            messages.success(request, f'Bed {bed.bed_number} is now {status}!')

        elif action == 'delete':
            # Delete bed
            bed_id = request.POST.get('bed_id')
            bed = get_object_or_404(ICUBed, id=bed_id)

            # Check permission for hospital admin
            if not request.user.is_superuser and bed.hospital != hospital:
                messages.error(request, 'Access denied!')
                return redirect('admin_manage_beds')

            bed.delete()
            messages.success(request, 'Bed deleted successfully!')

    context = {
        'beds': beds,
        'hospital': hospital,
        'is_super_admin': request.user.is_superuser,
    }
    return render(request, 'myapp/admin_manage_beds.html', context)


@login_required
def admin_add_bed(request):
    """Add ICU bed - for super admin and hospital admin"""

    # Check permission
    if request.user.is_superuser:
        hospital = None
        hospitals = Hospital.objects.filter(is_active=True)
    elif hasattr(request.user, 'hospital_admin_profile'):
        hospital = request.user.hospital_admin_profile.hospital
        hospitals = None
    else:
        messages.error(request, 'Access denied!')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        bed_number = request.POST.get('bed_number')
        bed_type = request.POST.get('bed_type')
        daily_charge = request.POST.get('daily_charge')
        equipment = request.POST.get('equipment', '')

        # For hospital admin, automatically assign their hospital
        if hospital:
            ICUBed.objects.create(
                bed_number=bed_number,
                hospital=hospital,
                bed_type=bed_type,
                daily_charge=daily_charge,
                equipment=equipment,
                is_available=True
            )
        else:
            # For super admin, get selected hospital
            hospital_id = request.POST.get('hospital_id')
            selected_hospital = get_object_or_404(Hospital, id=hospital_id) if hospital_id else None
            ICUBed.objects.create(
                bed_number=bed_number,
                hospital=selected_hospital,
                bed_type=bed_type,
                daily_charge=daily_charge,
                equipment=equipment,
                is_available=True
            )

        messages.success(request, 'Bed added successfully!')
        return redirect('admin_manage_beds')

    context = {
        'bed_types': ICUBed.BED_TYPES,
        'hospital': hospital,
        'hospitals': hospitals,
        'is_super_admin': request.user.is_superuser,
    }
    return render(request, 'myapp/admin_add_bed.html', context)


@login_required
def admin_manage_emergencies(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    emergencies = EmergencyRequest.objects.all().order_by('-request_time')

    if request.method == 'POST':
        emergency_id = request.POST.get('emergency_id')
        status = request.POST.get('status')
        emergency = get_object_or_404(EmergencyRequest, id=emergency_id)
        emergency.status = status
        emergency.save()
        messages.success(request, 'Emergency status updated!')

    return render(request, 'myapp/admin_manage_emergencies.html', {'emergencies': emergencies})


@login_required
def admin_products(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    products = Product.objects.all().order_by('-id')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)

        if action == 'delete':
            product.delete()
            messages.success(request, 'Product deleted!')
        elif action == 'toggle':
            product.is_active = not product.is_active
            product.save()
            messages.success(request, 'Product status updated!')

    return render(request, 'myapp/admin_products.html', {'products': products})


@login_required
def admin_add_product(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        if name and price and stock:
            Product.objects.create(
                name=name,
                price=price,
                stock=stock,
                description=description,
                is_active=is_active
            )
            messages.success(request, f'Product "{name}" added successfully!')
            return redirect('admin_products')
        else:
            messages.error(request, 'Please fill all required fields!')

    return render(request, 'myapp/admin_add_product.html')


@login_required
def admin_edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description', '')
        product.is_active = request.POST.get('is_active') == 'on'
        product.save()

        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('admin_products')

    return render(request, 'myapp/admin_edit_product.html', {'product': product})


@login_required
def admin_delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product_name = product.name
    product.delete()
    messages.success(request, f'Product "{product_name}" deleted successfully!')
    return redirect('admin_products')


@login_required
def admin_reports(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    all_patients = Patient.objects.all()
    all_doctors = Doctor.objects.all()
    selected_patient = None
    medical_reports = []
    patient_appointments = []

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        if patient_id:
            try:
                selected_patient = get_object_or_404(Patient, id=patient_id)
                medical_reports = MedicalReport.objects.filter(patient=selected_patient).order_by('-created_at')
                patient_appointments = Appointment.objects.filter(patient=selected_patient.user).order_by(
                    '-appointment_date')
            except:
                pass

    context = {
        'all_patients': all_patients,
        'all_doctors': all_doctors,
        'selected_patient': selected_patient,
        'medical_reports': medical_reports,
        'patient_appointments': patient_appointments,
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_beds': ICUBed.objects.count(),
        'available_beds': ICUBed.objects.filter(is_available=True).count(),
        'monthly_patients': Patient.objects.filter(created_at__month=timezone.now().month).count(),
        'monthly_appointments': Appointment.objects.filter(created_at__month=timezone.now().month).count(),
    }
    return render(request, 'myapp/admin_reports.html', context)


@login_required
def add_medical_report(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor_id')
        report_type = request.POST.get('report_type')
        diagnosis = request.POST.get('diagnosis')
        prescription = request.POST.get('prescription')
        test_results = request.POST.get('test_results')

        try:
            patient = get_object_or_404(Patient, id=patient_id)
            doctor = get_object_or_404(Doctor, id=doctor_id)

            MedicalReport.objects.create(
                patient=patient,
                doctor=doctor,
                report_type=report_type,
                diagnosis=diagnosis,
                prescription=prescription,
                test_results=test_results
            )
            messages.success(request, 'Medical report added successfully!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('admin_reports')

    return redirect('admin_reports')


@staff_member_required
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')

    all_orders = Order.objects.all()
    pending_orders_count = all_orders.filter(status='pending').count()
    confirmed_orders_count = all_orders.filter(status='confirmed').count()
    delivered_orders_count = all_orders.filter(status='delivered').count()
    cancelled_orders_count = all_orders.filter(status='cancelled').count()
    total_orders_count = all_orders.count()

    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            models.Q(order_number__icontains=search) |
            models.Q(user__username__icontains=search) |
            models.Q(user__first_name__icontains=search) |
            models.Q(user__email__icontains=search)
        )

    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status,
        'search': search,
        'total_orders': total_orders_count,
        'pending_orders': pending_orders_count,
        'confirmed_orders': confirmed_orders_count,
        'delivered_orders': delivered_orders_count,
        'cancelled_orders': cancelled_orders_count,
    }
    return render(request, 'myapp/admin_orders.html', context)


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.order_number} status updated to {new_status}!')
            return redirect('admin_order_detail', order_id=order.id)

    context = {
        'order': order,
        'items': order.items.all(),
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'myapp/admin_order_detail.html', context)


# ==================== ডাক্তার ভিউস ====================
# myapp/views.py
@login_required
def patient_dashboard(request):
    """Patient dashboard - only for patient users"""

    # চেক করুন ইউজার পেশন্ট কিনা
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient only area!')
        return redirect('patient_dashboard')  # অথবা 'login'

    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found!')
        return redirect('login')

    hospital = patient.hospital

    upcoming = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).count()

    context = {
        'patient': patient,
        'hospital': hospital,
        'upcoming_appointments': upcoming,
        'total_appointments': Appointment.objects.filter(patient=patient).count(),
        'recent_appointments': Appointment.objects.filter(patient=patient).select_related('doctor').order_by(
            '-appointment_date')[:5],
    }
    return render(request, 'myapp/patient_dashboard.html', context)


# myapp/views.py
@login_required
def doctor_dashboard(request):
    """Doctor dashboard"""

    # চেক করুন ইউজার ডাক্তার কিনা
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor only area!')
        return redirect('login')

    doctor = request.user.doctor_profile  # ← এটা ঠিক করুন (patient_profile না)
    today = timezone.now().date()

    appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date=today
    ).select_related('patient')

    context = {
        'doctor': doctor,
        'today_appointments': appointments,
        'appointment_count': appointments.count(),
        'total_patients': Appointment.objects.filter(doctor=doctor).values('patient').distinct().count(),
    }
    return render(request, 'myapp/doctor_dashboard.html', context)

@login_required
def profile(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.blood_group = request.POST.get('blood_group')
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES.get('profile_picture')
        user.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')

    return render(request, 'myapp/profile.html', {'patient': patient})


# ==================== আপয়েন্টমেন্ট ভিউস ====================
# myapp/views.py

@login_required
def book_appointment(request):
    # পেশন্টের হাসপাতাল পান
    if hasattr(request.user, 'patient_profile'):
        patient = request.user.patient_profile
        hospital = patient.hospital
    else:
        messages.error(request, 'Patient profile not found!')
        return redirect('profile')

    # শুধু ওই হাসপাতালের ডাক্তার দেখান
    if hospital:
        doctors = Doctor.objects.filter(hospital=hospital, is_available=True)
    else:
        messages.error(request, 'You are not assigned to any hospital!')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        symptoms = request.POST.get('symptoms')

        doctor = get_object_or_404(Doctor, id=doctor_id)
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        appointment_datetime = timezone.make_aware(appointment_datetime)

        # অ্যাপয়েন্টমেন্ট তৈরি করুন - হাসপাতাল সেট করতে ভুলবেন না!
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            hospital=hospital,  # ← এটা গুরুত্বপূর্ণ! হাসপিটাল সেট করুন
            appointment_date=appointment_datetime,
            symptoms=symptoms,
            status='pending'
        )

        messages.success(request, f'Appointment booked with Dr. {doctor.full_name}')
        return redirect('my_appointments')

    context = {
        'doctors': doctors,
        'hospital': hospital,
    }
    return render(request, 'myapp/book_appointment.html', context)


# myapp/views.py

@login_required
def my_appointments(request):
    """Show user's appointments based on user type"""

    # চেক করুন ইউজার পেশন্ট কিনা
    if hasattr(request.user, 'patient_profile'):
        # পেশন্টের অ্যাপয়েন্টমেন্ট - শুধু নিজের
        appointments = Appointment.objects.filter(
            patient=request.user.patient_profile
        ).select_related('doctor').order_by('-appointment_date')

        user_type = 'patient'

    elif hasattr(request.user, 'doctor_profile'):
        # ডাক্তারের অ্যাপয়েন্টমেন্ট - শুধু নিজের
        appointments = Appointment.objects.filter(
            doctor=request.user.doctor_profile
        ).select_related('patient').order_by('-appointment_date')

        user_type = 'doctor'

    elif hasattr(request.user, 'hospital_admin_profile'):
        # হাসপাতাল অ্যাডমিন - নিজের হাসপাতালের সব অ্যাপয়েন্টমেন্ট
        hospital = request.user.hospital_admin_profile.hospital
        appointments = Appointment.objects.filter(
            hospital=hospital
        ).select_related('patient', 'doctor').order_by('-appointment_date')

        user_type = 'hospital_admin'

    elif request.user.is_superuser:
        # সুপার অ্যাডমিন - সব অ্যাপয়েন্টমেন্ট
        appointments = Appointment.objects.all().select_related('patient', 'doctor').order_by('-appointment_date')
        user_type = 'super_admin'

    else:
        # অন্য ইউজার - অ্যাক্সেস নাই
        messages.error(request, 'You do not have access to appointments!')
        return redirect('login')

    context = {
        'appointments': appointments,
        'user_type': user_type,
        'appointments_count': appointments.count(),
        'pending_count': appointments.filter(status='pending').count(),
        'confirmed_count': appointments.filter(status='confirmed').count(),
        'completed_count': appointments.filter(status='completed').count(),
        'cancelled_count': appointments.filter(status='cancelled').count(),
    }
    return render(request, 'myapp/my_appointments.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled!')
    return redirect('my_appointments')


# ==================== ডাক্তার লিস্ট ভিউ ====================
def doctor_list(request):
    hospital = None
    if request.user.is_authenticated:
        hospital = get_user_hospital(request.user)

    if hospital:
        doctors = Doctor.objects.filter(hospital=hospital, is_available=True)
    else:
        doctors = Doctor.objects.filter(is_available=True)

    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization=specialization)

    return render(request, 'myapp/doctor_list.html', {
        'doctors': doctors,
        'specializations': Doctor.SPECIALIZATION_CHOICES
    })


# ==================== আইসিইউ ভিউস ====================
# myapp/views.py

# myapp/views.py

@login_required
def icu_beds(request):
    """Show ALL ICU beds from ALL hospitals for patients"""

    # Get all ICU beds from all hospitals
    beds = ICUBed.objects.all().order_by('hospital__name', 'bed_number')

    # Get statistics
    total_beds = beds.count()
    available_beds = beds.filter(is_available=True).count()
    occupied_beds = beds.filter(is_available=False).count()

    # Get unique hospitals for filter
    hospitals = Hospital.objects.filter(icu_beds__isnull=False).distinct()

    context = {
        'beds': beds,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'hospitals': hospitals,
    }
    return render(request, 'myapp/icu_beds.html', context)


# myapp/views.py - আপডেটেড ভার্সন

# myapp/views.py

@login_required
def book_icu_bed(request, bed_id):
    """Book an ICU bed"""
    bed = get_object_or_404(ICUBed, id=bed_id)

    if not bed.is_available:
        messages.error(request, 'Bed not available!')
        return redirect('icu_beds')

    # Get patient profile
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found!')
        return redirect('icu_beds')

    if request.method == 'POST':
        expected_discharge = request.POST.get('expected_discharge')
        condition = request.POST.get('condition')

        # এই তিনটি ফিল্ড বাদ দিন - patient_name, patient_age, contact_number
        ICUBooking.objects.create(
            patient=patient,
            bed=bed,
            hospital=bed.hospital,
            expected_discharge=expected_discharge,
            condition=condition,
            is_active=True
        )

        bed.is_available = False
        bed.save()

        messages.success(request, f'ICU Bed {bed.bed_number} booked successfully!')
        return redirect('icu_beds')

    context = {
        'bed': bed,
    }
    return render(request, 'myapp/book_icu_bed.html', context)

# ==================== ইমার্জেন্সি ভিউস ====================
def emergency(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        patient_age_str = request.POST.get('patient_age', '')
        contact_number = request.POST.get('contact_number', '').strip()
        emergency_type = request.POST.get('emergency_type', '')
        location = request.POST.get('location', '').strip()
        priority = request.POST.get('priority', '')
        additional_info = request.POST.get('additional_info', '').strip()

        errors = []

        if not patient_name:
            errors.append('Patient name is required')
        if not patient_age_str or not patient_age_str.isdigit():
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
            return render(request, 'myapp/emergency.html')

        try:
            emergency = EmergencyRequest.objects.create(
                patient_name=patient_name,
                patient_age=int(patient_age_str),
                contact_number=contact_number,
                emergency_type=emergency_type,
                location=location,
                priority=priority,
                additional_info=additional_info
            )
            messages.success(request, f'🚑 Ambulance {emergency.assigned_ambulance} dispatched!')
            return redirect('emergency_success', request_id=emergency.id)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'myapp/emergency.html')


def emergency_success(request, request_id):
    emergency = get_object_or_404(EmergencyRequest, id=request_id)
    return render(request, 'myapp/emergency_success.html', {'emergency': emergency})


# ==================== কার্ট ভিউস ====================
@login_required
def patient_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()

    context = {
        'cart_items': cart_items,
        'total_items': cart.total_items,
        'total_amount': cart.total_amount,
        'cart': cart,
    }
    return render(request, 'myapp/patient_cart.html', context)


@login_required
def patient_add_to_cart(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock <= 0:
            messages.error(request, f'{product.name} is out of stock!')
            return redirect('patient_products')

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} quantity increased!')
        else:
            messages.success(request, f'{product.name} added to your cart!')

        return redirect('patient_cart')

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('patient_products')


@login_required
def patient_update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0 and quantity <= cart_item.product.stock:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully!')
            elif quantity <= 0:
                cart_item.delete()
                messages.success(request, 'Item removed from cart!')
        except ValueError:
            messages.error(request, 'Invalid quantity!')

    return redirect('patient_cart')


@login_required
def patient_remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from your cart!')
    return redirect('patient_cart')


# ==================== চেকআউট ভিউস ====================
@login_required
def patient_checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.select_related('product').all()

    if not items:
        messages.error(request, 'Your cart is empty!')
        return redirect('patient_cart')

    if request.method == 'POST':
        try:
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"

            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                total_amount=cart.total_amount,
                shipping_address=request.POST.get('address', ''),
                phone=request.POST.get('phone', ''),
                status='pending'
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart.items.all().delete()
            messages.success(request, f'Order placed successfully! Order ID: {order_number}')
            return redirect('patient_orders')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'myapp/patient_checkout.html', {'cart': cart, 'items': items, 'total': cart.total_amount})


@login_required
def patient_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/patient_orders.html', {'orders': orders})


@login_required
def patient_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.order_number} cancelled!')
    else:
        messages.error(request, 'This order cannot be cancelled.')

    return redirect('patient_orders')


# ==================== প্রোডাক্ট ভিউস ====================
@login_required
def patient_products(request):
    hospital = get_user_hospital(request.user)

    if hospital:
        products = Product.objects.filter(is_active=True, stock__gt=0)
    else:
        products = Product.objects.filter(is_active=True, stock__gt=0)

    context = {'products': products}
    return render(request, 'myapp/patient_products.html', context)


# ==================== পেশন্ট স্পেসিফিক ভিউস ====================
@login_required
def patient_doctor_list(request):
    patient = request.user.patient_profile
    hospital = patient.hospital

    if not hospital:
        messages.error(request, 'You are not assigned to any hospital!')
        return redirect('patient_dashboard')

    doctors = Doctor.objects.filter(hospital=hospital, is_available=True)

    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization=specialization)

    context = {
        'doctors': doctors,
        'hospital': hospital,
        'specializations': Doctor.SPECIALIZATION_CHOICES,
    }
    return render(request, 'myapp/patient_doctor_list.html', context)


@login_required
def patient_book_appointment(request, doctor_id):
    patient = request.user.patient_profile
    hospital = patient.hospital

    if not hospital:
        messages.error(request, 'You are not assigned to any hospital!')
        return redirect('patient_dashboard')

    doctor = get_object_or_404(Doctor, id=doctor_id, hospital=hospital, is_available=True)

    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        symptoms = request.POST.get('symptoms', '')

        try:
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            appointment_datetime = timezone.make_aware(appointment_datetime)

            if appointment_datetime < timezone.now():
                messages.error(request, 'Please select a future date and time!')
                return redirect('patient_book_appointment', doctor_id=doctor.id)

            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                appointment_date=appointment_datetime,
                symptoms=symptoms,
                status='pending'
            )

            messages.success(request, f'Appointment booked with {doctor.full_name}!')
            return redirect('patient_my_appointments')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    context = {
        'doctor': doctor,
        'hospital': hospital,
    }
    return render(request, 'myapp/patient_book_appointment.html', context)


@login_required
def patient_my_appointments(request):
    patient = request.user.patient_profile
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    return render(request, 'myapp/patient_my_appointments.html', {'appointments': appointments})


@login_required
def patient_icu_beds(request):
    patient = request.user.patient_profile
    hospital = patient.hospital

    if not hospital:
        messages.error(request, 'You are not assigned to any hospital!')
        return redirect('patient_dashboard')

    beds = ICUBed.objects.filter(hospital=hospital)

    context = {
        'beds': beds,
        'hospital': hospital,
        'available_beds': beds.filter(is_available=True).count(),
        'total_beds': beds.count(),
    }
    return render(request, 'myapp/patient_icu_beds.html', context)


@login_required
def patient_book_icu_bed(request, bed_id):
    patient = request.user.patient_profile
    hospital = patient.hospital

    if not hospital:
        messages.error(request, 'You are not assigned to any hospital!')
        return redirect('patient_dashboard')

    bed = get_object_or_404(ICUBed, id=bed_id, hospital=hospital, is_available=True)

    if request.method == 'POST':
        expected_discharge = request.POST.get('expected_discharge')
        condition = request.POST.get('condition')

        try:
            ICUBooking.objects.create(
                patient=patient,
                bed=bed,
                hospital=hospital,
                expected_discharge=expected_discharge,
                condition=condition,
                is_active=True
            )

            bed.is_available = False
            bed.save()

            messages.success(request, f'ICU Bed {bed.bed_number} booked successfully!')
            return redirect('patient_icu_bookings')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    context = {
        'bed': bed,
        'hospital': hospital,
    }
    return render(request, 'myapp/patient_book_icu_bed.html', context)


@login_required
def patient_icu_bookings(request):
    patient = request.user.patient_profile
    bookings = ICUBooking.objects.filter(patient=patient).order_by('-admission_date')
    return render(request, 'myapp/patient_icu_bookings.html', {'bookings': bookings})


@staff_member_required
def admin_update_order_status(request, order_id):
    """অর্ডারের স্ট্যাটাস আপডেট করুন"""
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.order_number} status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status!')

    return redirect('admin_order_detail', order_id=order_id)


# ==================== রিভিউ ভিউ ====================
@login_required
def patient_submit_review(request, order_id):
    """Submit a review for a delivered order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')

        if rating and review_text:
            messages.success(request, 'Thank you for your review!')
        else:
            messages.error(request, 'Please provide both rating and review.')

    return redirect('patient_orders')


# ==================== জেনারেল কার্ট ভিউস (URL রেফারেন্সের জন্য) ====================
@login_required
def cart_view(request):
    """General cart view"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()

    context = {
        'cart_items': cart_items,
        'total_items': cart.total_items,
        'total_amount': cart.total_amount,
        'cart': cart,
    }
    return render(request, 'myapp/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if product.stock <= 0:
        messages.error(request, f'{product.name} is out of stock!')
        return redirect('patient_products')

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'{product.name} quantity increased!')
    else:
        messages.success(request, f'{product.name} added to your cart!')

    return redirect('cart_view')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from your cart!')
    return redirect('cart_view')


@login_required
def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0 and quantity <= cart_item.product.stock:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated!')
            elif quantity <= 0:
                cart_item.delete()
                messages.success(request, 'Item removed!')
        except ValueError:
            messages.error(request, 'Invalid quantity!')

    return redirect('cart_view')


@login_required
def checkout(request):
    """Process checkout"""
    cart = Cart.objects.get(user=request.user)
    items = cart.items.select_related('product').all()

    if not items:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart_view')

    if request.method == 'POST':
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"

        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=cart.total_amount,
            shipping_address=request.POST.get('address', ''),
            phone=request.POST.get('phone', ''),
            status='pending'
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()
        messages.success(request, f'Order placed! Order ID: {order_number}')
        return redirect('my_orders')

    context = {
        'cart': cart,
        'items': items,
        'total': cart.total_amount,
    }
    return render(request, 'myapp/checkout.html', context)


@login_required
def my_orders(request):
    """Display user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/my_orders.html', {'orders': orders})


# myapp/views.py


# myapp/views.py

@login_required
def hospital_dashboard(request):
    """Hospital Admin Dashboard - shows only their hospital's data"""

    # Check if user is hospital admin
    if not hasattr(request.user, 'hospital_admin_profile'):
        messages.error(request, 'Access denied. Hospital Admin only area!')
        return redirect('login')  # ← এখানে 'login' এ রিডাইরেক্ট করুন

    # Get hospital admin profile and hospital
    try:
        admin_profile = request.user.hospital_admin_profile
        hospital = admin_profile.hospital
    except:
        messages.error(request, 'Hospital admin profile not found!')
        return redirect('login')

    if not hospital:
        messages.error(request, 'No hospital assigned to this admin!')
        return redirect('login')

    # Get statistics for this hospital only
    doctors_count = Doctor.objects.filter(hospital=hospital).count()
    patients_count = Patient.objects.filter(hospital=hospital).count()
    appointments_count = Appointment.objects.filter(hospital=hospital).count()
    beds_count = ICUBed.objects.filter(hospital=hospital).count()
    available_beds = ICUBed.objects.filter(hospital=hospital, is_available=True).count()
    products_count = Product.objects.filter(hospital=hospital, is_active=True).count()

    # Get recent data
    recent_patients = Patient.objects.filter(hospital=hospital).order_by('-created_at')[:5]
    recent_appointments = Appointment.objects.filter(hospital=hospital).select_related('patient', 'doctor').order_by('-created_at')[:5]

    # Get today's appointments
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        hospital=hospital,
        appointment_date__date=today
    ).count()

    # Get pending appointments
    pending_appointments = Appointment.objects.filter(
        hospital=hospital,
        status='pending'
    ).count()

    context = {
        'hospital': hospital,
        'doctors_count': doctors_count,
        'patients_count': patients_count,
        'appointments_count': appointments_count,
        'beds_count': beds_count,
        'available_beds': available_beds,
        'products_count': products_count,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'myapp/hospital_dashboard.html', context)

# myapp/views.py
@login_required
def dashboard(request):
    """Universal dashboard redirect based on user type"""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'hospital_admin_profile'):
        return redirect('hospital_dashboard')
    elif hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_dashboard')
    elif hasattr(request.user, 'patient_profile'):
        return redirect('patient_dashboard')
    else:
        return redirect('patient_dashboard')


# myapp/views.py - Hospital Admin specific views

@login_required
def hospital_manage_patients(request):
    """Hospital Admin: Manage patients of their hospital only"""
    if not hasattr(request.user, 'hospital_admin_profile'):
        return redirect('login')

    hospital = request.user.hospital_admin_profile.hospital
    patients = Patient.objects.filter(hospital=hospital)

    if request.method == 'POST':
        action = request.POST.get('action')
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id, hospital=hospital)

        if action == 'delete':
            if patient.user:
                patient.user.delete()
            patient.delete()
            messages.success(request, 'Patient deleted successfully!')
        elif action == 'toggle':
            patient.is_active = not patient.is_active
            patient.save()
            status = "activated" if patient.is_active else "deactivated"
            messages.success(request, f'Patient {status}!')

    context = {
        'patients': patients,
        'hospital': hospital,
    }
    return render(request, 'myapp/hospital_patients.html', context)


@login_required
def hospital_manage_doctors(request):
    """Hospital Admin: Manage doctors of their hospital only"""

    # Check if user is hospital admin
    if not hasattr(request.user, 'hospital_admin_profile'):
        messages.error(request, 'Access denied. Hospital Admin only!')
        return redirect('login')

    # Get hospital
    hospital = request.user.hospital_admin_profile.hospital

    # Get doctors for this hospital only
    doctors = Doctor.objects.filter(hospital=hospital).select_related('user')

    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            # Add new doctor
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            specialization = request.POST.get('specialization')
            qualification = request.POST.get('qualification')
            experience = request.POST.get('experience')
            fee = request.POST.get('fee')

            if not email or not password:
                messages.error(request, 'Email and password required!')
            elif User.objects.filter(username=email).exists():
                messages.error(request, 'Email already exists!')
            else:
                # Create user
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    user_type='doctor'
                )
                # Create doctor profile
                Doctor.objects.create(
                    user=user,
                    hospital=hospital,
                    specialization=specialization,
                    qualification=qualification,
                    experience_years=int(experience) if experience else 0,
                    consultation_fee=float(fee) if fee else 500,
                    is_available=True
                )
                messages.success(request, f'Doctor {first_name} {last_name} added successfully!')

        elif action == 'edit':
            # Edit doctor
            doctor_id = request.POST.get('doctor_id')
            doctor = get_object_or_404(Doctor, id=doctor_id, hospital=hospital)
            doctor.specialization = request.POST.get('specialization')
            doctor.qualification = request.POST.get('qualification')
            doctor.experience_years = request.POST.get('experience')
            doctor.consultation_fee = request.POST.get('fee')
            doctor.save()
            messages.success(request, 'Doctor updated successfully!')

        elif action == 'delete':
            # Delete doctor
            doctor_id = request.POST.get('doctor_id')
            doctor = get_object_or_404(Doctor, id=doctor_id, hospital=hospital)
            user = doctor.user
            doctor.delete()
            user.delete()
            messages.success(request, 'Doctor deleted successfully!')

        elif action == 'toggle':
            # Toggle doctor availability
            doctor_id = request.POST.get('doctor_id')
            doctor = get_object_or_404(Doctor, id=doctor_id, hospital=hospital)
            doctor.is_available = not doctor.is_available
            doctor.save()
            status = "available" if doctor.is_available else "unavailable"
            messages.success(request, f'Doctor is now {status}!')

    context = {
        'doctors': doctors,
        'hospital': hospital,
        'specializations': Doctor.SPECIALIZATION_CHOICES,
    }
    return render(request, 'myapp/hospital_doctors.html', context)

# myapp/views.py

@login_required
def hospital_manage_appointments(request):
    """Hospital Admin: Manage appointments of their hospital only"""

    # Check if user is hospital admin
    if not hasattr(request.user, 'hospital_admin_profile'):
        messages.error(request, 'Access denied. Hospital Admin only!')
        return redirect('login')

    # Get hospital
    hospital = request.user.hospital_admin_profile.hospital

    # Get all appointments for this hospital
    appointments = Appointment.objects.filter(hospital=hospital).select_related('patient', 'doctor').order_by(
        '-appointment_date')

    # Get statistics
    total_appointments = appointments.count()
    pending_appointments = appointments.filter(status='pending').count()
    confirmed_appointments = appointments.filter(status='confirmed').count()
    completed_appointments = appointments.filter(status='completed').count()
    cancelled_appointments = appointments.filter(status='cancelled').count()

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    # Search by patient name
    search = request.GET.get('search')
    if search:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(doctor__user__first_name__icontains=search) |
            Q(doctor__user__last_name__icontains=search)
        )

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')

        appointment = get_object_or_404(Appointment, id=appointment_id, hospital=hospital)
        appointment.status = new_status
        appointment.save()

        messages.success(request, f'Appointment #{appointment.id} status updated to {new_status}!')
        return redirect('hospital_appointments')

    context = {
        'hospital': hospital,
        'appointments': appointments,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'current_status': status_filter,
        'search': search,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'myapp/hospital_appointments.html', context)


@login_required
def hospital_manage_beds(request):
    """Hospital Admin: Manage ICU beds of their hospital only"""
    if not hasattr(request.user, 'hospital_admin_profile'):
        return redirect('login')

    hospital = request.user.hospital_admin_profile.hospital
    beds = ICUBed.objects.filter(hospital=hospital)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            ICUBed.objects.create(
                bed_number=request.POST.get('bed_number'),
                hospital=hospital,
                bed_type=request.POST.get('bed_type'),
                daily_charge=request.POST.get('daily_charge'),
                equipment=request.POST.get('equipment'),
                is_available=True
            )
            messages.success(request, 'ICU Bed added successfully!')

        elif action == 'toggle':
            bed_id = request.POST.get('bed_id')
            bed = get_object_or_404(ICUBed, id=bed_id, hospital=hospital)
            bed.is_available = not bed.is_available
            bed.save()
            status = "available" if bed.is_available else "occupied"
            messages.success(request, f'Bed {bed.bed_number} is now {status}!')

        elif action == 'delete':
            bed_id = request.POST.get('bed_id')
            bed = get_object_or_404(ICUBed, id=bed_id, hospital=hospital)
            bed.delete()
            messages.success(request, 'Bed deleted successfully!')

    context = {
        'beds': beds,
        'hospital': hospital,
    }
    return render(request, 'myapp/hospital_beds.html', context)