# myapp/middleware.py
from .utils import get_user_hospital


class HospitalMiddleware:
    """Middleware to add hospital to request"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user_hospital = get_user_hospital(request.user)
        else:
            request.user_hospital = None

        response = self.get_response(request)
        return response