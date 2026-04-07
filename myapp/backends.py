# myapp/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailAuthBackend(ModelBackend):
    """
    Custom backend to authenticate users using email instead of username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email (case-insensitive)
            user = User.objects.get(email__iexact=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        return None