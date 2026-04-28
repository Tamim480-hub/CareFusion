# myapp/urls.py - সম্পূর্ণ সঠিক ফাইল

from django.urls import path
from . import views

urlpatterns = [
    # ==================== Auth URLs ====================
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # ==================== Super Admin URLs ====================
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/hospitals/', views.admin_manage_hospitals, name='admin_manage_hospitals'),
    path('admin/hospitals/<int:hospital_id>/', views.admin_hospital_detail, name='admin_hospital_detail'),
    path('admin/hospital-admins/', views.admin_manage_hospital_admins, name='admin_manage_hospital_admins'),
    path('admin/hospital-reports/', views.admin_hospital_reports, name='admin_hospital_reports'),

    # ==================== Super Admin - Pharmacy Management ====================
    path('super-admin/pharmacy-admins/', views.super_admin_pharmacy_admins, name='super_admin_pharmacy_admins'),
    path('super-admin/create-pharmacy-admin/', views.create_pharmacy_admin, name='create_pharmacy_admin'),

    # ==================== Hospital Admin URLs ====================
    path('hospital/dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('hospital/profile/', views.hospital_profile, name='hospital_profile'),
    path('hospital/doctors/', views.hospital_doctors, name='hospital_doctors'),
    path('hospital/patients/', views.hospital_patients, name='hospital_patients'),
    path('hospital/appointments/', views.hospital_appointments, name='hospital_appointments'),
    path('hospital/beds/', views.hospital_beds, name='hospital_beds'),
    path('hospital/products/', views.hospital_products, name='hospital_products'),
    path('hospital/orders/', views.hospital_orders, name='hospital_orders'),
    path('hospital/orders/<int:order_id>/', views.hospital_order_detail, name='hospital_order_detail'),
    path('hospital/test-reports/', views.hospital_test_reports, name='hospital_test_reports'),
    path('hospital/emergencies/', views.hospital_emergencies, name='hospital_emergencies'),

    # ==================== Patient URLs ====================
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),
    path('patient/book-appointment/', views.patient_book_appointment, name='patient_book_appointment'),
    path('patient/my-appointments/', views.patient_my_appointments, name='patient_my_appointments'),
    path('patient/cancel-appointment/<int:appointment_id>/', views.patient_cancel_appointment,
         name='patient_cancel_appointment'),
    path('patient/doctors/', views.patient_doctors, name='patient_doctors'),
    path('patient/test-reports/', views.patient_test_reports, name='patient_test_reports'),
    path('patient/test-report/<int:report_id>/', views.patient_test_report_detail, name='patient_test_report_detail'),
    path('patient/icu-beds/', views.patient_icu_beds, name='patient_icu_beds'),
    path('patient/icu-beds/book/<int:bed_id>/', views.patient_book_icu_bed, name='patient_book_icu_bed'),
    path('patient/icu-bookings/', views.patient_icu_bookings, name='patient_icu_bookings'),
    path('patient/icu-booking/cancel/<int:booking_id>/', views.patient_cancel_icu_booking,
         name='patient_cancel_icu_booking'),

    # Patient Bills URLs
    path('patient/bills/', views.patient_bills, name='patient_bills'),
    path('patient/bill/<int:bill_id>/', views.patient_bill_detail, name='patient_bill_detail'),
    path('patient/bill/pay/<int:bill_id>/', views.patient_pay_bill, name='patient_pay_bill'),
    path('appointment/bill/create/<int:appointment_id>/', views.create_appointment_bill,
         name='create_appointment_bill'),

    # ==================== Doctor URLs ====================
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/appointments/today/', views.doctor_today_appointments, name='doctor_today_appointments'),
    path('doctor/appointments/update/<int:appointment_id>/', views.doctor_update_appointment,
         name='doctor_update_appointment'),
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    path('doctor/patient/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/schedule/', views.doctor_schedule, name='doctor_schedule'),

    # ==================== Public URLs ====================
    path('emergency/', views.emergency, name='emergency'),
    path('emergency/success/<int:request_id>/', views.emergency_success, name='emergency_success'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),

    # ==================== Universal Dashboard Redirect ====================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ==================== AJAX URLs ====================
    path('get-doctors-by-hospital/', views.get_doctors_by_hospital, name='get_doctors_by_hospital'),
    path('get-beds-by-hospital/', views.get_beds_by_hospital, name='get_beds_by_hospital'),
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),

    # ==================== Pharmacy Admin URLs ====================
    path('pharmacy/dashboard/', views.pharmacy_dashboard, name='pharmacy_dashboard'),
    path('pharmacy/products/', views.pharmacy_admin_products, name='pharmacy_products'),
    path('pharmacy/orders/', views.pharmacy_orders, name='pharmacy_orders'),
    path('pharmacy/orders/<int:order_id>/', views.pharmacy_order_detail, name='pharmacy_order_detail'),
    path('pharmacy/update-order-status/<int:order_id>/', views.pharmacy_update_order_status,
         name='pharmacy_update_order_status'),

    # ==================== Pharmacy Customer URLs (Patient Pharmacy) ====================
    path('pharmacy/store/', views.pharmacy_products_list, name='pharmacy_products_list'),
    path('pharmacy/store/add-to-cart/<int:product_id>/', views.pharmacy_add_to_cart, name='pharmacy_add_to_cart'),
    path('pharmacy/store/cart/', views.pharmacy_cart, name='pharmacy_cart'),
    path('pharmacy/store/cart/update/<int:item_id>/', views.pharmacy_update_cart, name='pharmacy_update_cart'),
    path('pharmacy/store/cart/remove/<int:item_id>/', views.pharmacy_remove_from_cart,
         name='pharmacy_remove_from_cart'),
    path('pharmacy/store/checkout/', views.pharmacy_checkout, name='pharmacy_checkout'),
    path('pharmacy/order-confirmation/<int:order_id>/', views.pharmacy_order_confirmation,
         name='pharmacy_order_confirmation'),

    # Patient products (alias for pharmacy store)
    path('patient/products/', views.pharmacy_products_list, name='patient_products'),

    # ==================== Patient Pharmacy Orders URLs ====================
    path('patient/orders/', views.patient_orders, name='patient_orders'),
    path('patient/order/<int:order_id>/', views.patient_order_detail, name='patient_order_detail'),
    path('patient/cancel-order/<int:order_id>/', views.patient_cancel_order, name='patient_cancel_order'),

    # ==================== Patient Doctor Detail ====================
    path('patient/doctor/<int:doctor_id>/', views.patient_doctor_detail, name='patient_doctor_detail'),
    path('get-doctor-schedule/<int:doctor_id>/', views.get_doctor_schedule, name='get_doctor_schedule'),
    path('patient/delete-icu-booking/<int:booking_id>/', views.patient_delete_icu_booking,
         name='patient_delete_icu_booking'),
]