# myapp/tests.py

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse

from .models import (
    Hospital, ICUBed, ICUBooking, Patient, Doctor,
    Medicine
)

User = get_user_model()


class ModelTests(TestCase):
    """Test all models"""

    def setUp(self):
        """Create test data"""
        # Create hospital
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TEST001",
            address="123 Test Street, Dhaka",
            phone="+8801712345678",
            email="test@hospital.com",
            is_active=True
        )

        # Create user and patient
        self.user = User.objects.create_user(
            username='testpatient',
            password='testpass123',
            email='patient@test.com',
            user_type='patient'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            full_name="Test Patient",
            age=35,
            phone="01712345678",
            address="Test Address",
            blood_group="A+"
        )

        # Create doctor user
        self.doctor_user = User.objects.create_user(
            username='testdoctor',
            password='doctorpass123',
            email='doctor@test.com',
            user_type='doctor'
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name="Dr. Test Doctor",
            specialization="Cardiology",
            phone="01812345678",
            license_number="LIC123456",
            is_available=True
        )

        # Create ICU bed
        self.bed = ICUBed.objects.create(
            bed_number="ICU-101",
            bed_type="general",
            daily_charge=Decimal('5000.00'),
            is_available=True,
            hospital=self.hospital,
            equipment="Ventilator, Cardiac Monitor"
        )

    def test_patient_creation(self):
        """Test patient model"""
        self.assertEqual(self.patient.full_name, "Test Patient")
        self.assertEqual(self.patient.age, 35)
        self.assertEqual(self.patient.blood_group, "A+")
        self.assertEqual(str(self.patient), "Test Patient")

    def test_doctor_creation(self):
        """Test doctor model"""
        self.assertEqual(self.doctor.full_name, "Dr. Test Doctor")
        self.assertEqual(self.doctor.specialization, "Cardiology")
        self.assertEqual(self.doctor.is_available, True)
        self.assertEqual(str(self.doctor), "Dr. Dr. Test Doctor")

    def test_hospital_creation(self):
        """Test hospital model"""
        self.assertEqual(self.hospital.name, "Test Hospital")
        self.assertEqual(self.hospital.code, "TEST001")
        self.assertTrue(self.hospital.is_active)

    def test_icu_bed_creation(self):
        """Test ICU bed model"""
        self.assertEqual(self.bed.bed_number, "ICU-101")
        self.assertEqual(self.bed.daily_charge, Decimal('5000.00'))
        self.assertTrue(self.bed.is_available)

    def test_bed_string_representation(self):
        """Test bed string method"""
        expected = f"Bed {self.bed.bed_number} at {self.hospital.name}"
        self.assertEqual(str(self.bed), expected)

    def test_bed_availability_toggle(self):
        """Test bed availability"""
        self.assertTrue(self.bed.is_available)
        self.bed.is_available = False
        self.bed.save()
        self.assertFalse(self.bed.is_available)


class ICUBookingModelTest(TestCase):
    """Test ICU Booking Model"""

    def setUp(self):
        """Create test data"""
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TEST001",
            address="123 Test Street",
            is_active=True
        )

        self.bed = ICUBed.objects.create(
            bed_number="ICU-101",
            bed_type="general",
            daily_charge=Decimal('5000.00'),
            is_available=True,
            hospital=self.hospital
        )

        self.user = User.objects.create_user(
            username='testpatient',
            password='testpass123',
            email='patient@test.com',
            user_type='patient'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            full_name="Test Patient",
            age=35,
            phone="01712345678"
        )

        self.booking = ICUBooking.objects.create(
            patient=self.patient,
            bed=self.bed,
            hospital=self.hospital,
            patient_name=self.patient.full_name,
            patient_age=self.patient.age,
            contact_number=self.patient.phone,
            expected_discharge=date.today() + timedelta(days=5),
            condition="Critical condition, needs ICU care",
            is_active=True,
            admission_date=date.today()
        )

    def test_booking_creation(self):
        """Test booking creation"""
        self.assertEqual(self.booking.patient, self.patient)
        self.assertEqual(self.booking.bed, self.bed)
        self.assertTrue(self.booking.is_active)

    def test_booking_string_representation(self):
        """Test booking string method"""
        expected = f"Booking for {self.patient.full_name} - Bed {self.bed.bed_number}"
        self.assertEqual(str(self.booking), expected)

    def test_booking_cancellation(self):
        """Test booking cancellation"""
        self.booking.is_active = False
        self.booking.save()
        self.assertFalse(self.booking.is_active)

        # Bed should become available
        self.bed.refresh_from_db()
        self.assertTrue(self.bed.is_available)

    def test_booking_dates(self):
        """Test booking dates"""
        self.assertEqual(self.booking.admission_date, date.today())
        self.assertGreater(self.booking.expected_discharge, date.today())


class PatientViewsTest(TestCase):
    """Test Patient Views"""

    def setUp(self):
        """Setup test data"""
        # Create hospital
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TEST001",
            address="123 Test Street",
            is_active=True
        )

        # Create beds
        self.bed1 = ICUBed.objects.create(
            bed_number="ICU-101",
            bed_type="general",
            daily_charge=Decimal('5000.00'),
            is_available=True,
            hospital=self.hospital
        )

        self.bed2 = ICUBed.objects.create(
            bed_number="ICU-102",
            bed_type="cardiac",
            daily_charge=Decimal('7500.00'),
            is_available=False,
            hospital=self.hospital
        )

        # Create patient user
        self.user = User.objects.create_user(
            username='testpatient',
            password='testpass123',
            email='patient@test.com',
            user_type='patient'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            full_name="Test Patient",
            age=35,
            phone="01712345678",
            address="Test Address"
        )

        self.client = Client()
        self.client.login(username='testpatient', password='testpass123')

    def test_patient_dashboard_access(self):
        """Test patient dashboard loads"""
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_icu_beds_page_access(self):
        """Test ICU beds page loads correctly"""
        response = self.client.get(reverse('patient_icu_beds'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/patient_icu_beds.html')

    def test_icu_beds_context(self):
        """Test context data in ICU beds page"""
        response = self.client.get(reverse('patient_icu_beds'))
        self.assertIn('hospitals', response.context)
        self.assertGreaterEqual(len(response.context['hospitals']), 1)

    def test_get_beds_by_hospital_api(self):
        """Test AJAX endpoint for getting beds"""
        response = self.client.get(
            reverse('get_beds_by_hospital'),
            {'hospital_id': self.hospital.id}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['beds']), 2)

    def test_book_icu_bed_view(self):
        """Test booking an ICU bed"""
        response = self.client.post(
            reverse('patient_book_icu_bed', args=[self.bed1.id]),
            {
                'condition': 'Patient needs urgent ICU care',
                'expected_discharge': (date.today() + timedelta(days=7)).isoformat()
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check if booking created
        booking_exists = ICUBooking.objects.filter(
            patient=self.patient,
            bed=self.bed1
        ).exists()
        self.assertTrue(booking_exists)

        # Bed should be unavailable
        self.bed1.refresh_from_db()
        self.assertFalse(self.bed1.is_available)

    def test_icu_bookings_view(self):
        """Test viewing bookings"""
        # Create a booking
        ICUBooking.objects.create(
            patient=self.patient,
            bed=self.bed1,
            hospital=self.hospital,
            patient_name=self.patient.full_name,
            patient_age=self.patient.age,
            contact_number=self.patient.phone,
            condition="Test condition",
            is_active=True,
            admission_date=date.today()
        )

        response = self.client.get(reverse('patient_icu_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertEqual(response.context['active_bookings'], 1)

    def test_cancel_booking(self):
        """Test cancelling a booking"""
        # Create a booking
        booking = ICUBooking.objects.create(
            patient=self.patient,
            bed=self.bed1,
            hospital=self.hospital,
            patient_name=self.patient.full_name,
            patient_age=self.patient.age,
            contact_number=self.patient.phone,
            condition="Test condition",
            is_active=True,
            admission_date=date.today()
        )

        # Cancel booking
        response = self.client.post(
            reverse('patient_cancel_icu_booking', args=[booking.id]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check booking is inactive
        booking.refresh_from_db()
        self.assertFalse(booking.is_active)

        # Bed should be available
        self.bed1.refresh_from_db()
        self.assertTrue(self.bed1.is_available)

    def test_patient_profile_view(self):
        """Test patient profile view"""
        response = self.client.get(reverse('patient_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('patient', response.context)


class DoctorViewsTest(TestCase):
    """Test Doctor Views"""

    def setUp(self):
        """Setup doctor test data"""
        # Create doctor user
        self.doctor_user = User.objects.create_user(
            username='testdoctor',
            password='doctorpass123',
            email='doctor@test.com',
            user_type='doctor'
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name="Dr. Test Doctor",
            specialization="Cardiology",
            phone="01812345678",
            license_number="LIC123456",
            is_available=True
        )

        # Create patient
        self.patient_user = User.objects.create_user(
            username='testpatient',
            password='patientpass123',
            email='patient@test.com',
            user_type='patient'
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name="Test Patient",
            age=35,
            phone="01712345678"
        )

        # Create hospital
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TEST001",
            is_active=True
        )

        self.client = Client()
        self.client.login(username='testdoctor', password='doctorpass123')

    def test_doctor_dashboard_access(self):
        """Test doctor dashboard loads"""
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_doctor_patients_list(self):
        """Test doctor patients list"""
        response = self.client.get(reverse('doctor_patients'))
        self.assertEqual(response.status_code, 200)

    def test_doctor_appointments(self):
        """Test doctor appointments view"""
        response = self.client.get(reverse('doctor_appointments'))
        self.assertEqual(response.status_code, 200)


class AuthenticationTest(TestCase):
    """Test Authentication"""

    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            user_type='patient'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            full_name="Test User",
            age=30,
            phone="01712345678"
        )

        self.client = Client()

    def test_login_page_loads(self):
        """Test login page loads"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_successful_login(self):
        """Test successful login"""
        response = self.client.post(
            reverse('login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('patient_dashboard'), status_code=302, target_status_code=200)

    def test_invalid_login(self):
        """Test invalid login"""
        response = self.client.post(
            reverse('login'),
            {
                'username': 'testuser',
                'password': 'wrongpassword'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)

    def test_logout(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access(self):
        """Test unauthorized access redirects to login"""
        self.client.logout()
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class APITest(TestCase):
    """Test API endpoints"""

    def setUp(self):
        """Setup API test data"""
        self.hospital = Hospital.objects.create(
            name="API Test Hospital",
            code="APITEST",
            is_active=True
        )

        self.bed = ICUBed.objects.create(
            bed_number="API-101",
            bed_type="general",
            daily_charge=Decimal('5000.00'),
            is_available=True,
            hospital=self.hospital
        )

        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123',
            user_type='patient'
        )

        Patient.objects.create(
            user=self.user,
            full_name="API Patient",
            age=30,
            phone="01912345678"
        )

        self.client = Client()
        self.client.login(username='apiuser', password='apipass123')

    def test_get_beds_api(self):
        """Test get beds API"""
        response = self.client.get(
            reverse('get_beds_by_hospital'),
            {'hospital_id': self.hospital.id}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['beds']), 0)

        # Check bed data structure
        first_bed = data['beds'][0]
        self.assertIn('id', first_bed)
        self.assertIn('bed_number', first_bed)
        self.assertIn('daily_charge', first_bed)
        self.assertIn('is_available', first_bed)

    def test_invalid_hospital_api(self):
        """Test API with invalid hospital ID"""
        response = self.client.get(
            reverse('get_beds_by_hospital'),
            {'hospital_id': 99999}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['beds']), 0)

    def test_api_without_login(self):
        """Test API without authentication"""
        self.client.logout()
        response = self.client.get(
            reverse('get_beds_by_hospital'),
            {'hospital_id': self.hospital.id}
        )

        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class EdgeCaseTest(TestCase):
    """Test Edge Cases"""

    def setUp(self):
        """Setup edge case test data"""
        self.hospital = Hospital.objects.create(
            name="Edge Test Hospital",
            code="EDGETEST",
            is_active=True
        )

        self.user = User.objects.create_user(
            username='edgeuser',
            password='edgepass123',
            user_type='patient'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            full_name="Edge Patient",
            age=25,
            phone="01812345678"
        )

        self.client = Client()
        self.client.login(username='edgeuser', password='edgepass123')

    def test_book_without_condition(self):
        """Test booking without providing condition"""
        bed = ICUBed.objects.create(
            bed_number="EDGE-101",
            bed_type="general",
            daily_charge=Decimal('5000.00'),
            is_available=True,
            hospital=self.hospital
        )

        response = self.client.post(
            reverse('patient_book_icu_bed', args=[bed.id]),
            {
                'condition': '',  # Empty condition
                'expected_discharge': ''
            },
            follow=True
        )

        # Should show error (status 200 with error message)
        self.assertEqual(response.status_code, 200)

        # Booking should not be created
        booking_exists = ICUBooking.objects.filter(bed=bed).exists()
        self.assertFalse(booking_exists)

    def test_cancel_nonexistent_booking(self):
        """Test cancelling a booking that doesn't exist"""
        response = self.client.post(
            reverse('patient_cancel_icu_booking', args=[99999]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)

    def test_book_unavailable_bed(self):
        """Test booking a bed that is already occupied"""
        bed = ICUBed.objects.create(
            bed_number="EDGE-102",
            bed_type="cardiac",
            daily_charge=Decimal('7500.00'),
            is_available=False,  # Already occupied
            hospital=self.hospital
        )

        response = self.client.post(
            reverse('patient_book_icu_bed', args=[bed.id]),
            {
                'condition': 'Patient needs ICU',
                'expected_discharge': (date.today() + timedelta(days=5)).isoformat()
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Booking should not be created
        booking_exists = ICUBooking.objects.filter(bed=bed).exists()
        self.assertFalse(booking_exists)

    def test_double_booking_prevention(self):
        """Test that same bed cannot be booked twice"""
        bed = ICUBed.objects.create(
            bed_number="EDGE-103",
            bed_type="general",
            daily_charge=Decimal('5000.00'),
            is_available=True,
            hospital=self.hospital
        )

        # First booking
        booking1 = ICUBooking.objects.create(
            patient=self.patient,
            bed=bed,
            hospital=self.hospital,
            patient_name=self.patient.full_name,
            patient_age=self.patient.age,
            contact_number=self.patient.phone,
            condition="First booking",
            is_active=True,
            admission_date=date.today()
        )

        # Make bed unavailable
        bed.is_available = False
        bed.save()

        # Try second booking
        response = self.client.post(
            reverse('patient_book_icu_bed', args=[bed.id]),
            {
                'condition': 'Second booking attempt',
                'expected_discharge': (date.today() + timedelta(days=5)).isoformat()
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Should still have only one booking
        booking_count = ICUBooking.objects.filter(bed=bed).count()
        self.assertEqual(booking_count, 1)


class HospitalAdminTest(TestCase):
    """Test Hospital Admin Views"""

    def setUp(self):
        """Setup hospital admin test data"""
        # Create hospital admin user
        self.admin_user = User.objects.create_user(
            username='hospitaladmin',
            password='adminpass123',
            email='admin@hospital.com',
            user_type='hospital_admin'
        )

        # Create hospital
        self.hospital = Hospital.objects.create(
            name="Admin Hospital",
            code="ADMIN001",
            admin=self.admin_user,
            is_active=True
        )

        self.client = Client()
        self.client.login(username='hospitaladmin', password='adminpass123')

    def test_hospital_admin_dashboard(self):
        """Test hospital admin dashboard access"""
        response = self.client.get(reverse('hospital_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_manage_icu_beds(self):
        """Test ICU bed management"""
        response = self.client.get(reverse('hospital_icu_beds'))
        self.assertEqual(response.status_code, 200)


class SuperAdminTest(TestCase):
    """Test Super Admin Views"""

    def setUp(self):
        """Setup super admin test data"""
        self.super_user = User.objects.create_superuser(
            username='superadmin',
            password='superpass123',
            email='admin@supers.com'
        )

        self.client = Client()
        self.client.login(username='superadmin', password='superpass123')

    def test_admin_panel_access(self):
        """Test Django admin panel access"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_super_admin_dashboard(self):
        """Test super admin dashboard"""
        response = self.client.get(reverse('superadmin_dashboard'))
        self.assertEqual(response.status_code, 200)


class PharmacyTest(TestCase):
    """Test Pharmacy Views"""

    def setUp(self):
        """Setup pharmacy test data"""
        self.pharmacy_user = User.objects.create_user(
            username='pharmacy',
            password='pharmacy123',
            email='pharmacy@test.com',
            user_type='pharmacy'
        )

        self.client = Client()
        self.client.login(username='pharmacy', password='pharmacy123')

    def test_pharmacy_dashboard(self):
        """Test pharmacy dashboard access"""
        response = self.client.get(reverse('pharmacy_dashboard'))
        self.assertEqual(response.status_code, 200)


class PerformanceTest(TestCase):
    """Performance Tests"""

    def setUp(self):
        """Setup performance test data"""
        self.hospital = Hospital.objects.create(
            name="Performance Hospital",
            code="PERFTEST",
            is_active=True
        )

        # Create 20 beds
        for i in range(1, 21):
            ICUBed.objects.create(
                bed_number=f"PERF-{i:03d}",
                bed_type="general",
                daily_charge=Decimal('5000.00'),
                is_available=(i % 2 == 0),
                hospital=self.hospital
            )

        self.user = User.objects.create_user(
            username='perfuser',
            password='perfpass123',
            user_type='patient'
        )

        Patient.objects.create(
            user=self.user,
            full_name="Performance Patient",
            age=45,
            phone="01612345678"
        )

        self.client = Client()
        self.client.login(username='perfuser', password='perfpass123')

    def test_api_response_time(self):
        """Test API response time"""
        import time

        start_time = time.time()
        response = self.client.get(
            reverse('get_beds_by_hospital'),
            {'hospital_id': self.hospital.id}
        )
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        response_time = end_time - start_time

        # API should respond within 2 seconds
        self.assertLess(response_time, 2)
        print(f"API response time: {response_time:.3f} seconds")

    def test_page_load_time(self):
        """Test page load time"""
        import time

        start_time = time.time()
        response = self.client.get(reverse('patient_icu_beds'))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time

        # Page should load within 3 seconds
        self.assertLess(load_time, 3)
        print(f"Page load time: {load_time:.3f} seconds")