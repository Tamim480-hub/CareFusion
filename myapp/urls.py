from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Logout
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Patient Dashboard
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/medical-records/', views.patient_medical_records, name='patient_medical_records'),
    path('patient/bills/', views.patient_bills, name='patient_bills'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),

    # Admin Patient Management
    path('admin/patient/<int:patient_id>/', views.admin_patient_detail, name='admin_patient_detail'),
    path('admin/patient/<int:patient_id>/edit/', views.admin_edit_patient, name='admin_edit_patient'),

    # Extra actions
    path('patient/edit/<int:id>/', views.edit_patient, name='edit_patient'),
    path('patient/delete/<int:id>/', views.delete_patient, name='delete_patient'),
]