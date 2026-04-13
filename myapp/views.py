from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    User, Doctor, Appointment, ICUBed, ICUBooking, EmergencyRequest,
    Product, Cart, CartItem, Order, OrderItem, Patient, MedicalReport
)

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')

        print(f"=== LOGIN DEBUG ===")
        print(f"Input: {email_or_username}")

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
            print(f"✅ Login successful! User: {user.username}")
            messages.success(request, f'Welcome {user.username}!')

            # user_type চেক না করে শুধু is_superuser চেক করুন
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            print(f"❌ Authentication failed!")
            messages.error(request, 'Invalid username/email or password')

    return render(request, 'myapp/login.html')


# myapp/views.py - signup_view ফাংশনটি এইভাবে আপডেট করুন

# myapp/views.py - সম্পূর্ণ signup_view

def signup_view(request):
    if request.method == 'POST':
        # ডাটা সংগ্রহ
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        # ভ্যালিডেশন
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

        if not first_name:
            first_name = email.split('@')[0] if email else 'User'

        if not last_name:
            last_name = ''

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'myapp/signup.html')

        try:
            # ইউজার তৈরি
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # অতিরিক্ত ফিল্ড সেট
            user.phone = phone
            user.save()

            # পেশেন্ট প্রোফাইল তৈরি
            Patient.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                date_of_birth='1990-01-01',
                gender='male',
                address=''
            )

            # লগইন করুন
            login(request, user)
            messages.success(request, f'Welcome {first_name}! Your account has been created.')
            return redirect('patient_dashboard')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')

    return render(request, 'myapp/signup.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ==================== অ্যাডমিন ভিউস ====================

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
        'recent_appointments': Appointment.objects.select_related('doctor').order_by('-created_at')[:10],
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
            if patient.user:
                patient.user.is_active = not patient.user.is_active
                patient.user.save()
            status = "activated" if patient.user.is_active else "deactivated"
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


@login_required
def admin_manage_beds(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    beds = ICUBed.objects.all()

    if request.method == 'POST':
        bed_id = request.POST.get('bed_id')
        bed = get_object_or_404(ICUBed, id=bed_id)
        bed.is_available = not bed.is_available
        bed.save()
        messages.success(request, 'Bed status updated!')

    return render(request, 'myapp/admin_manage_beds.html', {'beds': beds})


@login_required
def admin_add_bed(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        ICUBed.objects.create(
            bed_number=request.POST.get('bed_number'),
            bed_type=request.POST.get('bed_type'),
            daily_charge=request.POST.get('daily_charge'),
            equipment=request.POST.get('equipment')
        )
        messages.success(request, 'Bed added successfully!')
        return redirect('admin_manage_beds')

    return render(request, 'myapp/admin_add_bed.html', {'bed_types': ICUBed.BED_TYPES})


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

    products = Product.objects.all()

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
        product = Product()
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')

        # ছবি আপলোড হ্যান্ডেল
        if request.FILES.get('product_image'):
            product.image = request.FILES.get('product_image')

        product.save()
        messages.success(request, 'Product added successfully!')
        return redirect('admin_products')

    return render(request, 'myapp/admin_add_product.html')

@login_required
def admin_reports(request):
    if not request.user.is_superuser:
        return redirect('patient_dashboard')

    try:
        all_patients = Patient.objects.all()
    except:
        all_patients = []

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
        'total_patients': Patient.objects.count() if all_patients else 0,
        'total_doctors': Doctor.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_beds': ICUBed.objects.count(),
        'available_beds': ICUBed.objects.filter(is_available=True).count(),
        'monthly_patients': Patient.objects.filter(
            created_at__month=timezone.now().month).count() if all_patients else 0,
        'monthly_appointments': Appointment.objects.filter(created_at__month=timezone.now().month).count(),
    }
    return render(request, 'myapp/admin_reports.html', context)


# myapp/views.py - add_medical_report ভিউ

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

# ==================== ডাক্তার ভিউস ====================

@login_required
def doctor_dashboard(request):
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Doctor profile not found!')
        return redirect('patient_dashboard')

    doctor = request.user.doctor_profile
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


# ==================== পেশেন্ট ভিউস ====================

@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    upcoming = Appointment.objects.filter(
        patient=request.user,
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).count()

    context = {
        'upcoming_appointments': upcoming,
        'total_appointments': Appointment.objects.filter(patient=request.user).count(),
        'recent_appointments': Appointment.objects.filter(patient=request.user).select_related('doctor').order_by(
            '-appointment_date')[:5],
        'patient': patient,
    }
    return render(request, 'myapp/patient_dashboard.html', context)


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

    context = {
        'patient': patient,
    }
    return render(request, 'myapp/profile.html', context)


# ==================== আপয়েন্টমেন্ট ভিউস ====================

@login_required
def book_appointment(request):
    doctors = Doctor.objects.filter(is_available=True)

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        symptoms = request.POST.get('symptoms')

        doctor = get_object_or_404(Doctor, id=doctor_id)
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        appointment_datetime = timezone.make_aware(appointment_datetime)

        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=appointment_datetime,
            symptoms=symptoms
        )

        messages.success(request, 'Appointment booked!')
        return redirect('my_appointments')

    return render(request, 'myapp/book_appointment.html', {'doctors': doctors})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).select_related('doctor').order_by(
        '-appointment_date')
    return render(request, 'myapp/my_appointments.html', {'appointments': appointments})


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
    specialization = request.GET.get('specialization')
    doctors = Doctor.objects.filter(is_available=True)

    if specialization:
        doctors = doctors.filter(specialization=specialization)

    return render(request, 'myapp/doctor_list.html', {
        'doctors': doctors,
        'specializations': Doctor.SPECIALIZATION_CHOICES
    })


# ==================== আইসিইউ ভিউস ====================

@login_required
def icu_beds(request):
    beds = ICUBed.objects.all()
    return render(request, 'myapp/icu_beds.html', {'beds': beds})


@login_required
def book_icu_bed(request, bed_id):
    bed = get_object_or_404(ICUBed, id=bed_id)

    if not bed.is_available:
        messages.error(request, 'Bed not available!')
        return redirect('icu_beds')

    if request.method == 'POST':
        ICUBooking.objects.create(
            patient=request.user,
            bed=bed,
            patient_name=request.POST.get('patient_name'),
            patient_age=request.POST.get('patient_age'),
            contact_number=request.POST.get('contact_number'),
            expected_discharge=request.POST.get('expected_discharge'),
            condition=request.POST.get('condition')
        )
        bed.is_available = False
        bed.save()
        messages.success(request, 'Bed booked successfully!')
        return redirect('icu_beds')

    return render(request, 'myapp/book_icu_bed.html', {'bed': bed})


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

        if not patient_age_str:
            errors.append('Patient age is required')
        elif not patient_age_str.isdigit():
            errors.append('Patient age must be a number')
        elif int(patient_age_str) < 0 or int(patient_age_str) > 150:
            errors.append('Please enter a valid age (0-150)')

        if not contact_number:
            errors.append('Contact number is required')

        if not emergency_type:
            errors.append('Emergency type is required')

        if not location:
            errors.append('Location is required')

        if not priority:
            errors.append('Priority is required')

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

            success_msg = f'🚑 Ambulance {emergency.assigned_ambulance} dispatched! '
            success_msg += f'Estimated arrival: {emergency.estimated_arrival.strftime("%I:%M %p")}'
            messages.success(request, success_msg)

            return redirect('emergency_success', request_id=emergency.id)

        except Exception as e:
            messages.error(request, f'Error creating emergency request: {str(e)}')
            return render(request, 'myapp/emergency.html')

    return render(request, 'myapp/emergency.html')


def emergency_success(request, request_id):
    emergency = get_object_or_404(EmergencyRequest, id=request_id)
    return render(request, 'myapp/emergency_success.html', {'emergency': emergency})


# ==================== কার্ট ভিউস ====================

# myapp/views.py - ডিবাগ সংস্করণ

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    print(f"Cart ID: {cart.id}")
    print(f"Items count: {items.count()}")
    for item in items:
        print(f"Item: {item.product.name}, Quantity: {item.quantity}")

    context = {
        'cart': cart,
        'items': items,
        'total': cart.total_amount,
    }
    return render(request, 'myapp/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    print(f"Product: {product.name}")
    print(f"Cart ID: {cart.id}")

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        print(f"Updated quantity: {cart_item.quantity}")
    else:
        print("Created new cart item")

    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('cart')



@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed!')

    return redirect('cart')


@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)

    if request.method == 'POST':
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"

        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=cart.total_amount,
            shipping_address=request.POST.get('address'),
            phone=request.POST.get('phone')
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()
        messages.success(request, f'Order placed! Order ID: {order_number}')
        return redirect('my_orders')

    return render(request, 'myapp/checkout.html', {'cart': cart})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/my_orders.html', {'orders': orders})


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


