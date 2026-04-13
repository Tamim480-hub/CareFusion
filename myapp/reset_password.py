# reset_password.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print('✓ Admin password reset to admin123')
except User.DoesNotExist:
    print('Admin user not found, creating new one...')
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@hospital.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('✓ Admin user created with password admin123')

# সব ইউজার দেখান
print('\nAll users:')
for user in User.objects.all():
    print(f'  - {user.username} (superuser: {user.is_superuser})')