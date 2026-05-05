from django.contrib.auth import get_user_model
User = get_user_model()

admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@hospital.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True,
    }
)

