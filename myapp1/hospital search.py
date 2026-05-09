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