from django.shortcuts import render
from django.db import models
from django.urls import path


# =========================================================
# 🏥 MODEL SECTION (Hospital Data Structure)
# =========================================================

class Hospital(models.Model):

    # -----------------------------------------
    # Basic Information
    # -----------------------------------------

    name = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=20
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    # -----------------------------------------
    # String Representation
    # -----------------------------------------

    def __str__(self):
        return self.name
# =========================================================
# 🔍 VIEW SECTION (SEARCH LOGIC)
# =========================================================

def search_hospital(request):

    # -----------------------------------------
    # STEP 1: GET SEARCH QUERY FROM USER
    # -----------------------------------------

    query = request.GET.get('q')

    # -----------------------------------------
    # STEP 2: GET ALL HOSPITALS
    # -----------------------------------------

    hospitals = Hospital.objects.all()

    # -----------------------------------------
    # STEP 3: CHECK IF USER SEARCHED ANYTHING
    # -----------------------------------------

    if query:

        # -------------------------------------
        # SEARCH BY NAME
        # -------------------------------------

        name_results = Hospital.objects.filter(
            name__icontains=query
        )

        # -------------------------------------
        # SEARCH BY LOCATION
        # -------------------------------------

        location_results = Hospital.objects.filter(
            location__icontains=query
        )

        # -------------------------------------
        # MERGE BOTH RESULTS
        # -------------------------------------

        hospitals = name_results | location_results

    # -----------------------------------------
    # STEP 4: COUNT RESULTS
    # -----------------------------------------

    total_results = hospitals.count()

    # -----------------------------------------
    # STEP 5: EMPTY RESULT CHECK
    # -----------------------------------------

    if query and total_results == 0:

        message = "No hospitals found matching your search."

    else:

        message = ""

    # -----------------------------------------
    # STEP 6: CONTEXT DATA
    # -----------------------------------------

    context = {

        # data
        'hospitals': hospitals,

        # search input
        'query': query,

        # extra info
        'total_results': total_results,

        'message': message

    }

    # -----------------------------------------
    # STEP 7: RETURN TEMPLATE
    # -----------------------------------------

    return render(
        request,
        'search_hospital.html',
        context
    )


# =========================================================
# 🌐 URL SECTION (ROUTING)
# =========================================================

urlpatterns = [

    path(
        'search-hospital/',
        search_hospital,
        name='search_hospital'
    ),

]


# =========================================================
# 📝 OPTIONAL TEMPLATE (for understanding)
# =========================================================

"""
search_hospital.html

------------------------------------------

<form method="GET">

    <input type="text"
           name="q"
           placeholder="Search hospital..."
           value="{{ query }}">

    <button type="submit">
        Search
    </button>

</form>

------------------------------------------

{% if message %}
    <p style="color:red;">
        {{ message }}
    </p>
{% endif %}

------------------------------------------

{% for hospital in hospitals %}

    <div style="border:1px solid #ccc; padding:10px; margin:10px;">

        <h3>{{ hospital.name }}</h3>

        <p>Location: {{ hospital.location }}</p>

        <p>Phone: {{ hospital.phone }}</p>

        <p>{{ hospital.description }}</p>

    </div>

{% endfor %}

------------------------------------------
"""