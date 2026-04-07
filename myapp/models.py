from django.contrib.auth.models import User
from django.db import models


# =============================================================================
# 🔹 User Profile Model
# =============================================================================
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_patient(self):
        return self.role == 'patient'


# =============================================================================
# 🔹 Department Model
# =============================================================================
class Department(models.Model):
    DEPARTMENT_CHOICES = [
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('general', 'General Medicine'),
        ('emergency', 'Emergency'),
        ('radiology', 'Radiology'),
        ('pharmacy', 'Pharmacy'),
    ]

    code = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    floor = models.CharField(max_length=20, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    head_doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# =============================================================================
# 🔹 Doctor Model
# =============================================================================
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"


# =============================================================================
# 🔹 Patient Model
# =============================================================================
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    phone = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15)
    address = models.TextField()
    blood_group = models.CharField(max_length=5, blank=True)
    assigned_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


# =============================================================================
# 🔹 Bed Model
# =============================================================================
class Bed(models.Model):
    BED_TYPE_CHOICES = [
        ('general', 'General Ward'),
        ('icu', 'ICU'),
        ('ccu', 'CCU'),
        ('private', 'Private Room'),
        ('semi_private', 'Semi Private'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('reserved', 'Reserved'),
    ]

    bed_number = models.CharField(max_length=10, unique=True)
    bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    floor = models.CharField(max_length=10)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='beds')
    current_patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_bed'
    )
    occupied_since = models.DateTimeField(blank=True, null=True)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    has_monitor = models.BooleanField(default=False)
    has_oxygen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bed {self.bed_number} - {self.get_status_display()}"


# =============================================================================
# 🔹 Appointment Model
# =============================================================================
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.doctor}"


# =============================================================================
# 🔹 Bill Model
# =============================================================================
class Bill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.patient} - ৳{self.amount}"


# =============================================================================
# 🔹 Medical Record Model
# =============================================================================
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='medical_records')
    diagnosis = models.TextField()
    treatment = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record #{self.id} - {self.patient}"