from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
import logging

from .models import Doctor

# Create logger
logger = logging.getLogger(__name__)


def doctor_search(request):
    """
    Advanced Doctor Search View
    Supports:
    - Search by name or specialization
    - Pagination
    - Safe query handling
    - Logging
    """

    try:
        # Get search query from URL (?q=...)
        query = request.GET.get('q', '').strip()

        # Base queryset (all doctors)
        doctors = Doctor.objects.all()

        # Apply search filter if query exists
        if query:
            doctors = doctors.filter(
                Q(name__icontains=query) |
                Q(specialization__icontains=query)
            )

        # -----------------------------
        # Pagination Section
        # -----------------------------
        page_number = request.GET.get('page', 1)
        paginator = Paginator(doctors, 5)  # 5 doctors per page

        try:
            page_obj = paginator.get_page(page_number)
        except Exception as e:
            logger.error(f"Pagination error: {e}")
            page_obj = paginator.get_page(1)

        # -----------------------------
        # Context Data
        # -----------------------------
        context = {
            'doctors': page_obj,
            'query': query,
            'total_doctors': doctors.count(),
        }

        return render(request, 'doctor_search.html', context)

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Doctor search error: {e}")

        return render(request, 'doctor_search.html', {
            'doctors': [],
            'error': 'Something went wrong. Please try again later.'
        })