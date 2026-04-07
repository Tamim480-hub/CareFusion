from django.shortcuts import redirect
from django.urls import path
from . import views

def home_redirect(request):
    return redirect('login')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]