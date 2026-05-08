from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Patient


@login_required
def patient_profile(request):

    # =====================================================
    # STEP 1: GET LOGGED-IN USER PATIENT DATA
    # =====================================================

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    # =====================================================
    # STEP 2: BASIC INFORMATION
    # =====================================================

    full_name = patient.user.get_full_name()
    username = patient.user.username
    email = patient.user.email

    age = patient.age
    gender = patient.gender
    phone = patient.phone
    address = patient.address

    blood_group = patient.blood_group

    # =====================================================
    # STEP 3: AGE CHECK
    # =====================================================

    if age >= 18:
        is_adult = True
        age_status = "Adult"
    else:
        is_adult = False
        age_status = "Minor"

    # =====================================================
    # STEP 4: BLOOD GROUP CHECK
    # =====================================================

    if blood_group:
        has_blood_group = True
        blood_status = "Available"
    else:
        has_blood_group = False
        blood_status = "Not Provided"

    # =====================================================
    # STEP 5: PHONE CHECK
    # =====================================================

    if phone:
        phone_status = "Available"
    else:
        phone_status = "Not Available"

    # =====================================================
    # STEP 6: ADDRESS CHECK
    # =====================================================

    if address:
        address_status = "Available"
    else:
        address_status = "Not Available"

    # =====================================================
    # STEP 7: PROFILE COMPLETION SCORE (SIMPLE)
    # =====================================================

    score = 0

    if phone:
        score = score + 25

    if address:
        score = score + 25

    if blood_group:
        score = score + 25

    if age:
        score = score + 25

    # =====================================================
    # STEP 8: PROFILE STATUS
    # =====================================================

    if score == 100:
        profile_status = "Complete"
    elif score >= 50:
        profile_status = "Half Complete"
    else:
        profile_status = "Incomplete"

    # =====================================================
    # STEP 9: PROFILE PICTURE CHECK
    # =====================================================

    if patient.profile_picture:
        has_image = True
    else:
        has_image = False

    # =====================================================
    # STEP 10: LAST VISIT (OPTIONAL SIMPLE)
    # =====================================================

    last_visit = patient.last_visit

    # =====================================================
    # STEP 11: CONTEXT DATA FOR TEMPLATE
    # =====================================================

    context = {

        # user info
        'patient': patient,
        'full_name': full_name,
        'username': username,
        'email': email,

        # personal info
        'age': age,
        'gender': gender,
        'phone': phone,
        'address': address,

        # status info
        'is_adult': is_adult,
        'age_status': age_status,

        # medical info
        'blood_group': blood_group,
        'has_blood_group': has_blood_group,
        'blood_status': blood_status,

        # contact status
        'phone_status': phone_status,
        'address_status': address_status,

        # profile score
        'profile_score': score,
        'profile_status': profile_status,

        # image
        'has_image': has_image,

        # system info
        'last_visit': last_visit,

    }

    # =====================================================
    # STEP 12: RETURN RESPONSE
    # =====================================================

    return render(
        request,
        'patient_profile.html',
        context
    )