from datetime import date, timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('hospital_admin', 'Hospital Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username}"


class Hospital(models.Model):
    """Hospital model for multi-hospital system"""
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
    """Each hospital has its own admin"""
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

    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name()}"

    def __str__(self):
        return self.full_name


class Patient(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
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
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                        (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return 0

    def __str__(self):
        return self.full_name


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


# myapp/models.py

class ICUBooking(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='icu_bookings')
    bed = models.ForeignKey(ICUBed, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='icu_bookings', null=True, blank=True)

    # এই ফিল্ডগুলিতে null=True যোগ করুন
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    patient_age = models.IntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)

    admission_date = models.DateTimeField(auto_now_add=True)
    expected_discharge = models.DateField()
    condition = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient_name or self.patient.full_name} - {self.bed.bed_number}"

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


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_amount(self):
        items = self.items.all()
        return sum(item.subtotal for item in items)

    @property
    def total_items(self):
        return self.items.count()

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

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
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


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


@receiver(pre_save, sender=Appointment)
def set_appointment_hospital(sender, instance, **kwargs):
    """Automatically set hospital from doctor before saving"""
    if not instance.hospital and instance.doctor:
        instance.hospital = instance.doctor.hospita