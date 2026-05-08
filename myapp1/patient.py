from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ==========================================
# Patient Model (Advanced Version)
# ==========================================

class Patient(models.Model):

    # -------------------------
    # BASIC RELATION
    # -------------------------
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )

    # -------------------------
    # PERSONAL INFORMATION
    # -------------------------
    age = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(120)
        ]
    )

    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ]
    )

    phone = models.CharField(
        max_length=20,
        unique=True
    )

    emergency_contact = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    address = models.TextField()

    city = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=50,
        default="Bangladesh"
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # -------------------------
    # MEDICAL INFORMATION
    # -------------------------
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        choices=[
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
        ]
    )

    allergies = models.TextField(
        blank=True,
        null=True
    )

    chronic_diseases = models.TextField(
        blank=True,
        null=True
    )

    current_medications = models.TextField(
        blank=True,
        null=True
    )

    # -------------------------
    # PROFILE DATA
    # -------------------------
    profile_picture = models.ImageField(
        upload_to='patients/',
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    # -------------------------
    # SYSTEM FIELDS
    # -------------------------
    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    last_visit = models.DateTimeField(
        blank=True,
        null=True
    )

    # -------------------------
    # META OPTIONS
    # -------------------------
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    # -------------------------
    # STRING REPRESENTATION
    # -------------------------
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.phone})"

    # -------------------------
    # FULL NAME METHOD
    # -------------------------
    def full_name(self):
        return self.user.get_full_name()

    # -------------------------
    # AGE CHECKER
    # -------------------------
    def is_adult(self):
        return self.age >= 18

    # -------------------------
    # UPDATE LAST VISIT
    # -------------------------
    def update_last_visit(self):
        self.last_visit = timezone.now()
        self.save()

    # -------------------------
    # BLOOD GROUP CHECK
    # -------------------------
    def has_blood_group(self):
        return self.blood_group is not None

    # -------------------------
    # PROFILE COMPLETENESS SCORE
    # -------------------------
    def profile_completion_score(self):

        score = 0

        if self.phone:
            score += 20
        if self.address:
            score += 20
        if self.blood_group:
            score += 20
        if self.profile_picture:
            score += 20
        if self.emergency_contact:
            score += 20

        return score

    # -------------------------
    # SAVE OVERRIDE
    # -------------------------
    def save(self, *args, **kwargs):

        # Auto-capitalize gender
        if self.gender:
            self.gender = self.gender.capitalize()

        super().save(*args, **kwargs)