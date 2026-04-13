# myapp/decorators.py - সম্পূর্ণ নতুন ফাইল

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def login_required_message(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first!')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# অ্যাডমিন চেক করার জন্য শুধু is_superuser ব্যবহার করুন
def admin_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first!')
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, 'Admin access required!')
            return redirect('patient_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper