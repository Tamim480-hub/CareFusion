from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Sum

from .models import (
    User, Doctor, Patient, Appointment, ICUBed, ICUBooking,
    EmergencyRequest, Product, Cart, CartItem, Order, OrderItem,
    MedicalReport, Department, UserProfile, Hospital, HospitalAdminProfile
)


# ==================== Order Item Inline ====================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ==================== Custom User Admin ====================
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_active')
    list_filter = ('user_type', 'is_active')
    search_fields = ('username', 'email', 'phone')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'address', 'profile_picture', 'date_of_birth', 'blood_group'),
        }),
    )


# Register User
admin.site.register(User, CustomUserAdmin)


# ==================== Hospital Admin ====================
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'email')


@admin.register(HospitalAdminProfile)
class HospitalAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital', 'designation', 'is_active')
    list_filter = ('hospital', 'is_active')
    search_fields = ('user__username', 'user__email', 'hospital__name')
    raw_id_fields = ('user', 'hospital')


# ==================== Doctor Admin ====================
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'hospital', 'specialization', 'consultation_fee', 'is_available')
    list_filter = ('specialization', 'is_available', 'hospital')
    search_fields = ('user__username', 'user__email', 'specialization')
    raw_id_fields = ('user', 'hospital')

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Doctor Name'


# ==================== Patient Admin ====================
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'hospital', 'phone', 'is_active')
    list_filter = ('is_active', 'gender', 'hospital')
    search_fields = ('first_name', 'last_name', 'phone', 'user__username')
    raw_id_fields = ('user', 'assigned_doctor', 'hospital')

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Patient Name'


# ==================== Appointment Admin ====================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient_name', 'get_doctor_name', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date', 'hospital')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__username')
    raw_id_fields = ('patient', 'doctor', 'hospital')

    def get_patient_name(self, obj):
        return obj.patient.full_name
    get_patient_name.short_description = 'Patient Name'

    def get_doctor_name(self, obj):
        return obj.doctor.full_name
    get_doctor_name.short_description = 'Doctor Name'


# ==================== ICUBed Admin ====================
@admin.register(ICUBed)
class ICUBedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'hospital', 'bed_type', 'is_available', 'daily_charge')
    list_filter = ('bed_type', 'is_available', 'hospital')
    search_fields = ('bed_number',)


# ==================== ICUBooking Admin ====================
@admin.register(ICUBooking)
class ICUBookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'bed', 'hospital', 'admission_date', 'is_active')
    list_filter = ('is_active', 'admission_date')
    search_fields = ('patient__first_name', 'patient__last_name')
    raw_id_fields = ('patient', 'bed', 'hospital')


# ==================== EmergencyRequest Admin ====================
@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'priority', 'status', 'request_time')
    list_filter = ('priority', 'status')
    search_fields = ('patient_name', 'contact_number')


# ==================== Product Admin ====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'total_sold', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

    def total_sold(self, obj):
        total = OrderItem.objects.filter(product=obj).aggregate(total=Sum('quantity'))['total'] or 0
        return total
    total_sold.short_description = 'Total Sold'

from .models import Pharmacy, PharmacyAdmin, PharmacyProduct, PharmacyOrder, PharmacyOrderItem

admin.site.register(Pharmacy)
admin.site.register(PharmacyAdmin)
admin.site.register(PharmacyProduct)
admin.site.register(PharmacyOrder)
admin.site.register(PharmacyOrderItem)

# ==================== Cart Admin ====================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_amount', 'created_at')
    search_fields = ('user__username',)

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Total Items'

    def total_amount(self, obj):
        return f'৳{obj.total_amount}'
    total_amount.short_description = 'Total Amount'


# ==================== CartItem Admin ====================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'subtotal')
    search_fields = ('cart__user__username', 'product__name')

    def subtotal(self, obj):
        return f'৳{obj.subtotal}'
    subtotal.short_description = 'Subtotal'


# ==================== Order Admin ====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    actions = ['mark_as_confirmed', 'mark_as_delivered']

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} orders marked as confirmed!')
    mark_as_confirmed.short_description = 'Mark selected orders as Confirmed'

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f'{queryset.count()} orders marked as delivered!')
    mark_as_delivered.short_description = 'Mark selected orders as Delivered'


# ==================== OrderItem Admin ====================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__order_number', 'product__name')


# ==================== MedicalReport Admin ====================
@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'report_type', 'created_at')
    list_filter = ('report_type',)
    search_fields = ('patient__first_name', 'report_type')
    raw_id_fields = ('patient', 'doctor')


# ==================== Department Admin ====================
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


# ==================== UserProfile Admin ====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username',)