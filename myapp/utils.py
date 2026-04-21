# myapp/utils.py


def get_user_hospital(user):
    """Get the hospital associated with a user"""
    if user.is_superuser or user.user_type == 'super_admin':
        return None  # Super admin sees all

    if user.user_type == 'hospital_admin' and hasattr(user, 'hospital_admin'):
        return user.hospital_admin.hospital

    if user.user_type == 'doctor' and hasattr(user, 'doctor_profile'):
        return user.doctor_profile.hospital

    if user.user_type == 'patient' and hasattr(user, 'patient_profile'):
        return user.patient_profile.hospital

    return None


def get_patient_hospital(patient):
    """Get patient's hospital"""
    if patient.hospital:
        return patient.hospital
    return None