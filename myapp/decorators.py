# myapp/decorators.py - Role-Based Access Control
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile

def admin_required(view_func):
    """Decorator to restrict access to Admin users only"""
    @wraps(view_func)
    def _wrapper_view(request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'admin' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Access denied. Admin privileges required.')
                return redirect('patient_dashboard')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('login')
    return _wrapper_view


def patient_required(view_func):
    """Decorator to restrict access to Patient users only"""
    @wraps(view_func)
    def _wrapper_view(request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'patient':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Access denied. Patient account required.')
                return redirect('dashboard')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('login')
    return _wrapper_view


def doctor_required(view_func):
    """Decorator to restrict access to Doctor users only"""
    @wraps(view_func)
    def _wrapper_view(request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'doctor':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Access denied. Doctor account required.')
                return redirect('login')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('login')
    return _wrapper_view