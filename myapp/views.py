# myapp/views.py
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import UserProfile


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')


        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')

    return render(request, 'myapp/login.html')


def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        request.POST.get('date_of_birth')
        request.POST.get('gender')

        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'myapp/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'myapp/signup.html')


        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )


        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone
        )

        login(request, user)
        return redirect('dashboard')

    return render(request, 'myapp/signup.html')




def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')


def dashboard_view(request=None):
    return render(request, "myapp/dashboard.html")