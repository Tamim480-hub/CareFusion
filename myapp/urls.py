# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Admin URLs
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

    # Reports URLs
    path('dashboard/reports/', views.admin_reports, name='admin_reports'),
    path('reports/', views.admin_reports, name='reports'),
    path('reports/add/', views.add_medical_report, name='add_medical_report'),  # ← এই লাইনটি যোগ করুন

    # Doctor URLs
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    # Patient URLs
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('profile/', views.profile, name='profile'),

    # Appointment URLs
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/my/', views.my_appointments, name='my_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),

    # Doctor List
    path('doctors/', views.doctor_list, name='doctor_list'),

    # ICU URLs
    path('icu/beds/', views.icu_beds, name='icu_beds'),
    path('icu/book/<int:bed_id>/', views.book_icu_bed, name='book_icu_bed'),

    # Emergency URLs
    path('emergency/', views.emergency, name='emergency'),
    path('emergency/success/<int:request_id>/', views.emergency_success, name='emergency_success'),

    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
# myapp/urls.py - এই লাইনটি যোগ করুন

    path('reports/add/', views.add_medical_report, name='add_medical_report'),
    # Orders
    path('orders/', views.my_orders, name='my_orders'),
]