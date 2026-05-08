from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Doctor


def search_doctor(request):

    # =====================================
    # Get Search Parameters
    # =====================================

    query = request.GET.get('q', '').strip()

    specialization = request.GET.get(
        'specialization',
        ''
    ).strip()

    page_number = request.GET.get('page')

    # =====================================
    # Start QuerySet
    # =====================================

    doctors = Doctor.objects.select_related(
        'user'
    ).all().order_by(
        'user__first_name'
    )

    # =====================================
    # Search by Name or Specialization
    # =====================================

    if query:

        doctors = doctors.filter(

            Q(user__first_name__icontains=query) |

            Q(user__last_name__icontains=query) |

            Q(user__username__icontains=query) |

            Q(specialization__icontains=query)

        )

    # =====================================
    # Filter by Exact Specialization
    # =====================================

    if specialization:

        doctors = doctors.filter(
            specialization__iexact=specialization
        )

    # =====================================
    # Total Count
    # =====================================

    total_doctors = doctors.count()

    # =====================================
    # Pagination
    # =====================================

    paginator = Paginator(
        doctors,
        5
    )

    page_obj = paginator.get_page(
        page_number
    )

    # =====================================
    # Empty Search Message
    # =====================================

    if query and total_doctors == 0:

        messages.warning(
            request,
            "No doctors found matching your search."
        )

    # =====================================
    # Specialization List
    # =====================================

    specializations = Doctor.objects.values_list(
        'specialization',
        flat=True
    ).distinct()

    # =====================================
    # Context Data
    # =====================================

    context = {

        'page_obj': page_obj,

        'doctors': page_obj,

        'query': query,

        'specialization': specialization,

        'specializations': specializations,

        'total_doctors': total_doctors,

    }

    # =====================================
    # Render Template
    # =====================================

    return render(

        request,

        'search_doctor.html',

        context

    )