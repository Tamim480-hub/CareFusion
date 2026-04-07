from django.contrib import admin
from .models import UserProfile, Patient, Doctor, Department, Appointment, Bill, MedicalRecord


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'department', 'assigned_doctor', 'is_active', 'created_at', 'user')
    list_filter = ('is_active', 'department', 'assigned_doctor')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialization', 'license_number', 'is_available', 'created_at')
    list_filter = ('is_available', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization', 'license_number')
    readonly_fields = ('created_at',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status', 'created_at')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__username')
    readonly_fields = ('created_at',)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'description', 'amount', 'paid', 'created_at')
    list_filter = ('paid', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'description')
    readonly_fields = ('created_at',)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'created_at')
    list_filter = ('created_at', 'doctor')
    search_fields = ('patient__first_name', 'patient__last_name', 'diagnosis')
    readonly_fields = ('created_at',)