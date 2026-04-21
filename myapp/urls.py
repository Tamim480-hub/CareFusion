from django.urls import path
from . import views

urlpatterns = [
    # ==================== Auth URLs ====================
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # ==================== Super Admin URLs ====================
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/patients/', views.admin_manage_patients, name='admin_manage_patients'),
    path('dashboard/doctors/', views.admin_manage_doctors, name='admin_manage_doctors'),
    path('dashboard/doctors/add/', views.admin_add_doctor, name='admin_add_doctor'),
    path('dashboard/doctors/edit/<int:id>/', views.admin_edit_doctor, name='admin_edit_doctor'),
    path('dashboard/doctors/delete/<int:id>/', views.admin_delete_doctor, name='admin_delete_doctor'),
    path('dashboard/appointments/', views.admin_manage_appointments, name='admin_manage_appointments'),
    path('dashboard/beds/', views.admin_manage_beds, name='admin_manage_beds'),
    path('dashboard/beds/add/', views.admin_add_bed, name='admin_add_bed'),
    path('dashboard/emergencies/', views.admin_manage_emergencies, name='admin_manage_emergencies'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/products/add/', views.admin_add_product, name='admin_add_product'),
    path('dashboard/products/edit/<int:id>/', views.admin_edit_product, name='admin_edit_product'),
    path('dashboard/products/delete/<int:id>/', views.admin_delete_product, name='admin_delete_product'),
    path('dashboard/reports/', views.admin_reports, name='admin_reports'),

    # ==================== Admin Order URLs ====================
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/update/<int:order_id>/', views.admin_update_order_status, name='admin_update_order_status'),

    # ==================== Reports URLs ====================
    path('reports/', views.admin_reports, name='reports'),
    path('reports/add/', views.add_medical_report, name='add_medical_report'),

    # ==================== Doctor URLs ====================
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),

    # ==================== Hospital Admin URLs ====================
    path('hospital/dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('hospital/patients/', views.hospital_manage_patients, name='hospital_patients'),
    path('hospital/doctors/', views.hospital_manage_doctors, name='hospital_doctors'),
    path('hospital/appointments/', views.hospital_manage_appointments, name='hospital_appointments'),
    path('hospital/beds/', views.hospital_manage_beds, name='hospital_beds'),

    # ==================== Patient URLs ====================
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('profile/', views.profile, name='profile'),

    # ==================== Patient Doctor URLs ====================
    path('patient/doctors/', views.patient_doctor_list, name='patient_doctor_list'),

    # ==================== Appointment URLs ====================
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/my/', views.my_appointments, name='my_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('patient/appointment/book/<int:doctor_id>/', views.patient_book_appointment, name='patient_book_appointment'),
    path('patient/appointments/', views.patient_my_appointments, name='patient_my_appointments'),

    # ==================== ICU URLs ====================
    path('icu/beds/', views.icu_beds, name='icu_beds'),
    path('icu/book/<int:bed_id>/', views.book_icu_bed, name='book_icu_bed'),
    path('patient/icu/beds/', views.patient_icu_beds, name='patient_icu_beds'),
    path('patient/icu/book/<int:bed_id>/', views.patient_book_icu_bed, name='patient_book_icu_bed'),
    path('patient/icu/bookings/', views.patient_icu_bookings, name='patient_icu_bookings'),

    # ==================== Emergency URLs ====================
    path('emergency/', views.emergency, name='emergency'),
    path('emergency/success/<int:request_id>/', views.emergency_success, name='emergency_success'),

    # ==================== Patient Products URLs ====================
    path('patient/products/', views.patient_products, name='patient_products'),

    # ==================== Patient Cart URLs ====================
    path('patient/cart/', views.patient_cart, name='patient_cart'),
    path('patient/cart/add/<int:product_id>/', views.patient_add_to_cart, name='patient_add_to_cart'),
    path('patient/cart/update/<int:item_id>/', views.patient_update_cart, name='patient_update_cart'),
    path('patient/cart/remove/<int:item_id>/', views.patient_remove_from_cart, name='patient_remove_from_cart'),

    # ==================== Patient Checkout & Orders URLs ====================
    path('patient/checkout/', views.patient_checkout, name='patient_checkout'),
    path('patient/orders/', views.patient_orders, name='patient_orders'),
    path('patient/orders/cancel/<int:order_id>/', views.patient_cancel_order, name='patient_cancel_order'),
    path('patient/orders/review/<int:order_id>/', views.patient_submit_review, name='patient_submit_review'),

    # ==================== General Cart URLs (Optional) ====================
    path('general/cart/', views.cart_view, name='cart'),
    path('general/cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('general/cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('general/cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('general/cart/checkout/', views.checkout, name='checkout'),
    path('general/orders/', views.my_orders, name='my_orders'),

    # ==================== Universal Dashboard Redirect ====================
    path('dashboard/redirect/', views.dashboard, name='dashboard'),
]