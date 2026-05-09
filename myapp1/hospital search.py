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