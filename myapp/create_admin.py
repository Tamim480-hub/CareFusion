# create_admin.py - প্রকল্পের রুট ফোল্ডারে (যেখানে manage.py আছে)
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from myapp.models import UserProfile

User = get_user_model()


def create_admin():
    email = 'admin@hospital.com'
    password = 'Admin@123456'

    # চেক করুন ইউজার আছে কিনা
    if not User.objects.filter(username=email).exists():
        admin_user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name='Super',
            last_name='Admin',
            user_type='admin',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        print(f'✓ Admin user created successfully!')
    else:
        admin_user = User.objects.get(username=email)
        admin_user.set_password(password)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.user_type = 'admin'
        admin_user.save()
        print(f'✓ Admin user updated successfully!')

    # প্রোফাইল তৈরি বা আপডেট করুন
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'role': 'admin',
            'phone': '01700000000',
            'address': 'Admin Office'
        }
    )

    if not created:
        profile.role = 'admin'
        profile.save()

    print(f'\n{"=" * 40}')
    print(f'Login Credentials:')
    print(f'Email: {email}')
    print(f'Password: {password}')
    print(f'{"=" * 40}')


if __name__ == '__main__':
    create_admin()