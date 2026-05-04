# myapp/models.py

from datetime import date, timedelta, datetime
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# ==================== User Model ====================
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('hospital_admin', 'Hospital Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('pharmacy_admin', 'Pharmacy Admin'),
        ('pharmacy_customer', 'Pharmacy Customer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username}"


# ==================== Hospital Models ====================
class Hospital(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='hospital_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class HospitalAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_admin_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='admins')
    designation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'hospital']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.hospital.name}"


# ==================== Doctor Models ====================
class Doctor(models.Model):
    SPECIALIZATION_CHOICES = (
        ('cardiologist', 'Cardiologist'),
        ('dermatologist', 'Dermatologist'),
        ('neurologist', 'Neurologist'),
        ('pediatrician', 'Pediatrician'),
        ('orthopedic', 'Orthopedic'),
        ('gynecologist', 'Gynecologist'),
        ('psychiatrist', 'Psychiatrist'),
        ('ent', 'ENT Specialist'),
        ('general_physician', 'General Physician'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors', null=True, blank=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    available_from = models.TimeField(default='09:00')
    available_to = models.TimeField(default='17:00')
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    default_start_time = models.TimeField(default='09:00')
    default_end_time = models.TimeField(default='17:00')
    default_consultation_duration = models.IntegerField(default=30)
    default_max_patients = models.IntegerField(default=20)

    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name()}"

    def __str__(self):
        return self.full_name


class DoctorSchedule(models.Model):
    WEEKDAYS = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=20, choices=WEEKDAYS)
    is_available = models.BooleanField(default=True)
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='17:00')
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    max_patients = models.IntegerField(default=20)
    consultation_duration = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['doctor', 'day']
        ordering = ['day']

    def __str__(self):
        return f"{self.doctor.full_name} - {self.get_day_display()}"


# ==================== Patient Models ====================
class Patient(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    phone = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if not self.date_of_birth:
            return 0
        try:
            if isinstance(self.date_of_birth, str):
                from datetime import datetime
                dob = datetime.strptime(self.date_of_birth, '%Y-%m-%d').date()
            else:
                dob = self.date_of_birth
            today = date.today()
            age = today.year - dob.year
            if (today.month, today.day) < (dob.month, dob.day):
                age -= 1
            return age if age >= 0 else 0
        except Exception:
            return 0

    def __str__(self):
        return self.full_name


# ==================== Appointment Models ====================
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    appointment_date = models.DateTimeField()
    symptoms = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.doctor.full_name}"


# ==================== ICU Models ====================
class ICUBed(models.Model):
    BED_TYPES = (
        ('general', 'General ICU'),
        ('cardiac', 'Cardiac ICU'),
        ('pediatric', 'Pediatric ICU'),
        ('neonatal', 'Neonatal ICU'),
    )

    bed_number = models.CharField(max_length=10)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='icu_beds', null=True, blank=True)
    bed_type = models.CharField(max_length=20, choices=BED_TYPES, default='general')
    is_available = models.BooleanField(default=True)
    equipment = models.TextField(blank=True)
    daily_charge = models.DecimalField(max_digits=10, decimal_places=2, default=5000)

    class Meta:
        unique_together = ['bed_number', 'hospital']

    def __str__(self):
        return f"Bed {self.bed_number} - {self.hospital.name if self.hospital else 'No Hospital'}"


class ICUBooking(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='icu_bookings')
    bed = models.ForeignKey(ICUBed, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='icu_bookings', null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    patient_age = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    admission_date = models.DateTimeField(auto_now_add=True)
    expected_discharge = models.DateField()
    condition = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient_name or self.patient.full_name} - {self.bed.bed_number}"


# ==================== Emergency Models ====================
class EmergencyRequest(models.Model):
    PRIORITY_CHOICES = (
        ('critical', 'Critical - Immediate'),
        ('high', 'High - 5 mins'),
        ('medium', 'Medium - 10 mins'),
        ('low', 'Low - 15 mins'),
    )

    patient_name = models.CharField(max_length=100)
    patient_age = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    emergency_type = models.CharField(max_length=100)
    location = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    additional_info = models.TextField(blank=True)
    request_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    assigned_ambulance = models.CharField(max_length=50, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.assigned_ambulance:
            count = EmergencyRequest.objects.count()
            self.assigned_ambulance = f'AMB-{count + 1:04d}'
        if not self.estimated_arrival:
            self.estimated_arrival = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Emergency - {self.patient_name}"


# ==================== Hospital Product Models ====================
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==================== Cart & Order Models ====================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('PharmacyProduct', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ==================== Medical Report Models ====================
class MedicalReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    report_type = models.CharField(max_length=100)
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True)
    test_results = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.first_name} - {self.report_type} - {self.created_at.date()}"


class TestReport(models.Model):
    REPORT_TYPES = (
        ('blood_test', 'Blood Test'),
        ('x_ray', 'X-Ray'),
        ('mri', 'MRI'),
        ('ct_scan', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('urine_test', 'Urine Test'),
        ('stool_test', 'Stool Test'),
        ('ecg', 'ECG'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='test_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_reports')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='test_reports', null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='other')
    report_title = models.CharField(max_length=200, blank=True)
    report_date = models.DateField(auto_now_add=True)
    test_date = models.DateField(null=True, blank=True)
    findings = models.TextField(blank=True)
    normal_range = models.TextField(blank=True)
    test_results = models.TextField(blank=True)
    interpretation = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    report_file = models.FileField(upload_to='test_reports/', null=True, blank=True)
    report_image = models.ImageField(upload_to='test_reports/images/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.patient.full_name} - {self.get_report_type_display()} - {self.report_date}"


# ==================== Bill Models ====================
class Bill(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_METHOD = (
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Banking'),
        ('mobile', 'Mobile Banking'),
        ('insurance', 'Insurance'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bills')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='bills')
    bill_number = models.CharField(max_length=50, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.patient.id}"
        self.total_amount = float(self.amount) - float(self.discount) + float(self.tax)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill #{self.bill_number} - {self.patient.full_name}"


# ==================== Department Models ====================
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ==================== Pharmacy Models ====================
class Pharmacy(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='pharmacy_logos/', null=True, blank=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    free_delivery_above = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PharmacyAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacy_admin_profile')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='admins', null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    designation = models.CharField(max_length=100, default='Pharmacy Manager')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.pharmacy.name if self.pharmacy else 'No Pharmacy'}"


class PharmacyProduct(models.Model):
    CATEGORY_CHOICES = (
        ('medicine', 'Medicine'),
        ('equipment', 'Medical Equipment'),
        ('supplement', 'Health Supplement'),
        ('personal_care', 'Personal Care'),
        ('baby_care', 'Baby Care'),
        ('ayurvedic', 'Ayurvedic'),
        ('homeopathy', 'Homeopathy'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='medicine')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='pharmacy_products/', null=True, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    requires_prescription = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='products', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def selling_price(self):
        return self.price - (self.price * self.discount_percent / 100)

    def __str__(self):
        return self.name


class PharmacyCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacy_customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class PharmacyCart(models.Model):
    customer = models.OneToOneField(PharmacyCustomer, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_items(self):
        return self.items.count()

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Cart - {self.customer.user.username if self.customer else 'No Customer'}"


class PharmacyCartItem(models.Model):
    cart = models.ForeignKey(PharmacyCart, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    product = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.product.selling_price * self.quantity if self.product else 0

    def __str__(self):
        return f"{self.product.name if self.product else 'No Product'} x {self.quantity}"


class PharmacyPrescription(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )

    prescription_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(PharmacyCustomer, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    image = models.ImageField(upload_to='prescriptions/')
    doctor_name = models.CharField(max_length=200, blank=True)
    doctor_registration = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(PharmacyAdmin, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.prescription_number:
            import random
            self.prescription_number = f"RX-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"RX-{self.prescription_number}"


class PharmacyOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('mobile', 'Mobile Banking'),
    )

    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(PharmacyCustomer, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    prescription = models.ForeignKey(PharmacyPrescription, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, default='pending')
    shipping_address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"PH-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number}"


class PharmacyOrderItem(models.Model):
    order = models.ForeignKey(PharmacyOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ==================== Medical Prescription ====================
class MedicalPrescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_prescriptions')
    date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField()
    medicines = models.TextField(help_text="Medicine names with dosage")
    instructions = models.TextField(blank=True)
    next_visit_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.full_name} on {self.date}"


# ==================== Notification Model ====================
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('doctor_created', 'Doctor Account Created'),
        ('appointment', 'New Appointment'),
        ('schedule', 'Schedule Update'),
        ('patient', 'Patient Message'),
        ('system', 'System Alert'),
        ('reminder', 'Reminder'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"