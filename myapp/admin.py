# myapp/admin.py - UserProfile বাদ দিয়ে
from django.contrib import admin
from .models import Doctor, Appointment, ICUBed, ICUBooking, EmergencyRequest, Product, Cart, Order


# ডাক্তার অ্যাডমিন
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'consultation_fee', 'is_available')
    list_filter = ('specialization', 'is_available')
    search_fields = ('user__first_name', 'user__last_name')

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Doctor Name'


# আপয়েন্টমেন্ট অ্যাডমিন
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient_name', 'get_doctor_name', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__first_name')

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()
    get_patient_name.short_description = 'Patient Name'

    def get_doctor_name(self, obj):
        return obj.doctor.full_name
    get_doctor_name.short_description = 'Doctor Name'


# আইসিইউ বেড অ্যাডমিন
@admin.register(ICUBed)
class ICUBedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'bed_type', 'is_available', 'daily_charge')
    list_filter = ('bed_type', 'is_available')
    search_fields = ('bed_number',)


# আইসিইউ বুকিং অ্যাডমিন
@admin.register(ICUBooking)
class ICUBookingAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'bed', 'admission_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('patient_name', 'contact_number')


# ইমার্জেন্সি অ্যাডমিন
@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'priority', 'status', 'request_time')
    list_filter = ('priority', 'status')
    search_fields = ('patient_name', 'contact_number')


# প্রোডাক্ট অ্যাডমিন
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


# কার্ট অ্যাডমিন
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)


# অর্ডার অ্যাডমিন
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email')