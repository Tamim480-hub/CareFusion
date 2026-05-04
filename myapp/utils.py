# myapp/utils.py

import logging
import secrets
import string
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def generate_random_password(length=8):
    """
    র্যান্ডম পাসওয়ার্ড জেনারেট করুন - secrets module ব্যবহার করে
    """
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def send_notification_to_user(user, title, message, notification_type='system', link=None):
    """
    ইউজারকে ড্যাশবোর্ড নোটিফিকেশন পাঠান
    """
    try:
        from .models import Notification
        notification = Notification.objects.create(
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )
        logger.info(f"Notification sent to {user.username}: {title}")
        return notification
    except Exception as e:
        logger.error(f"Failed to send notification to {user.username}: {str(e)}")
        return None


def send_doctor_welcome_email_and_notification(doctor, password):
    """
    ডাক্তার যোগ করার পর ইমেইল এবং ড্যাশবোর্ড নোটিফিকেশন পাঠান
    """

    # ========== 1. ড্যাশবোর্ড নোটিফিকেশন ==========
    notification_title = "Welcome to CareFusion! 🎉"
    notification_message = f"""Dear Dr. {doctor.full_name},

Your doctor account has been successfully created at {doctor.hospital.name}.

📋 Account Details:
• Username: {doctor.user.username}
• Password: {password}
• Email: {doctor.user.email}
• Specialization: {doctor.get_specialization_display()}
• Consultation Fee: ৳{doctor.consultation_fee}

🔐 Please login using your credentials and change your password for security.

Click below to login to your account."""

    send_notification_to_user(
        user=doctor.user,
        title=notification_title,
        message=notification_message,
        notification_type='doctor_created',
        link='/login/'
    )

    # ========== 2. ইমেইল পাঠান ==========
    return send_doctor_confirmation_email(doctor, doctor.hospital, password)


def send_doctor_confirmation_email(doctor, hospital, password):
    """
    ডাক্তার যোগ করার পর কনফার্মেশন ইমেইল পাঠান
    """
    try:
        subject = f'Welcome to CareFusion - Doctor Account Created'

        context = {
            'doctor_name': doctor.full_name,
            'hospital_name': hospital.name,
            'hospital_address': hospital.address,
            'hospital_phone': hospital.phone,
            'email': doctor.user.email,
            'username': doctor.user.username,
            'password': password,
            'specialization': doctor.get_specialization_display(),
            'consultation_fee': doctor.consultation_fee,
            'experience_years': doctor.experience_years,
            'login_url': 'http://127.0.0.1:8000/login/',
            'current_year': datetime.now().year,
        }

        # HTML ইমেইল কন্টেন্ট
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; background: #f9fafb; }}
                .credentials {{ background: #e0e7ff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: #4f46e5; color: white; text-decoration: none; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; background: #f3f4f6; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🏥 CareFusion</h2>
                    <p>Healthcare Management System</p>
                </div>
                <div class="content">
                    <h3>Dear Dr. {doctor.full_name},</h3>
                    <p>Welcome to <strong>CareFusion</strong>! Your doctor account has been successfully created at <strong>{hospital.name}</strong>.</p>

                    <div class="credentials">
                        <h4>🔐 Your Login Credentials:</h4>
                        <p><strong>Username:</strong> {doctor.user.username}</p>
                        <p><strong>Password:</strong> {password}</p>
                        <p><strong>Email:</strong> {doctor.user.email}</p>
                    </div>

                    <div class="credentials">
                        <h4>📋 Professional Information:</h4>
                        <p><strong>Specialization:</strong> {doctor.get_specialization_display()}</p>
                        <p><strong>Consultation Fee:</strong> ৳{doctor.consultation_fee}</p>
                        <p><strong>Experience:</strong> {doctor.experience_years} years</p>
                    </div>

                    <div class="credentials">
                        <h4>🏥 Hospital Information:</h4>
                        <p><strong>Name:</strong> {hospital.name}</p>
                        <p><strong>Address:</strong> {hospital.address}</p>
                        <p><strong>Phone:</strong> {hospital.phone}</p>
                    </div>

                    <p style="text-align: center;">
                        <a href="http://127.0.0.1:8000/login/" class="btn">🔐 Login to Your Account</a>
                    </p>

                    <p><strong>⚠️ Note:</strong> Please change your password after logging in for security.</p>

                    <p>Best regards,<br>
                    <strong>CareFusion Team</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} CareFusion. All rights reserved.</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [doctor.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Confirmation email sent to {doctor.user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


def send_appointment_confirmation_email(appointment):
    """
    অ্যাপয়েন্টমেন্ট কনফার্মেশনের জন্য ইমেইল
    """
    try:
        subject = f'Appointment Confirmation - CareFusion'

        context = {
            'patient_name': appointment.patient.full_name,
            'doctor_name': appointment.doctor.full_name,
            'hospital_name': appointment.hospital.name if appointment.hospital else appointment.doctor.hospital.name,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'consultation_fee': appointment.doctor.consultation_fee,
            'current_year': datetime.now().year,
        }

        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; }}
                .header {{ background: #4f46e5; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🏥 CareFusion</h2>
                    <p>Appointment Confirmation</p>
                </div>
                <div class="content">
                    <h3>Dear {appointment.patient.full_name},</h3>
                    <p>Your appointment has been <strong>confirmed</strong>.</p>

                    <h4>Appointment Details:</h4>
                    <p><strong>Doctor:</strong> Dr. {appointment.doctor.full_name}</p>
                    <p><strong>Date:</strong> {appointment.appointment_date}</p>
                    <p><strong>Time:</strong> {appointment.appointment_time}</p>
                    <p><strong>Fee:</strong> ৳{appointment.doctor.consultation_fee}</p>

                    <p>Please arrive 15 minutes before your appointment time.</p>

                    <p>Best regards,<br>CareFusion Team</p>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} CareFusion. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_message = strip_tags(html_message)

        recipient_list = [appointment.patient.user.email, appointment.doctor.user.email]

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message,
            fail_silently=True,
        )
        logger.info(f"Appointment email sent to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send appointment email: {str(e)}")
        return False


def get_user_hospital(user):
    """Get the hospital associated with a user"""
    if not user or not user.is_authenticated:
        return None

    if user.is_superuser or user.user_type == 'super_admin':
        return None

    if user.user_type == 'hospital_admin' and hasattr(user, 'hospital_admin_profile'):
        return user.hospital_admin_profile.hospital

    if user.user_type == 'doctor' and hasattr(user, 'doctor_profile'):
        return user.doctor_profile.hospital

    if user.user_type == 'patient' and hasattr(user, 'patient_profile'):
        return user.patient_profile.hospital

    return None


def get_patient_hospital(patient):
    """Get patient's hospital"""
    if not patient:
        return None
    if hasattr(patient, 'hospital') and patient.hospital:
        return patient.hospital
    return None