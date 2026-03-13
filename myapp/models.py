from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('pharmacist', 'pharmacist'),
        ('administration', 'administration'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='choice')
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


    class Department(models.Model):
        DEPARTMENT_CHOICES = [
            ('cardiology', 'Cardiology'),
            ('neurology', 'Neurology'),
            ('orthopedics', 'Orthopedics'),
            ('pediatrics', 'Pediatrics'),
            ('general', 'General'),
        ]

        name = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.get_name_display()

        def get_name_display(self):
            pass

