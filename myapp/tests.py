# myapp/tests.py - আরও ভালো সমাধান
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.test import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

User = get_user_model()


class LoginSeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(service=service)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        """প্রতিটি টেস্টের আগে টেস্ট ডাটা তৈরি করুন"""
        # টেস্ট ইউজার তৈরি
        self.user = User.objects.create_user(
            username='testuser123',
            email='testuser@example.com',
            password='TestPassword123',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()

        # Django Test Client (অপশনাল)
        self.client = Client()

    def test_successful_login_redirects_to_dashboard(self):
        """সফল লগইন ড্যাশবোর্ডে রিডাইরেক্ট করে কিনা টেস্ট"""

        # লগইন পেজে যান
        self.selenium.get(f'{self.live_server_url}/login/')

        # ফর্ম এলিমেন্ট খুঁজুন
        username_field = self.selenium.find_element(By.NAME, "email")
        password_field = self.selenium.find_element(By.NAME, "password")

        # ইউজারনেম এবং পাসওয়ার্ড দিন
        username_field.send_keys("testuser123")
        password_field.send_keys("TestPassword123")

        # ফর্ম সাবমিট করুন
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # পেজ লোড হওয়ার জন্য অপেক্ষা করুন
        WebDriverWait(self.selenium, 5).until(
            EC.url_contains('/patient/dashboard/')
        )

        # ভেরিফাই করুন
        self.assertIn('/patient/dashboard/', self.selenium.current_url)

        # ড্যাশবোর্ডে স্বাগতম বার্তা আছে কিনা চেক করুন
        welcome_text = self.selenium.find_element(By.TAG_NAME, "body").text
        self.assertIn("Welcome", welcome_text)

    def test_invalid_login_shows_error(self):
        """ভুল পাসওয়ার্ড দিলে এরর মেসেজ দেখায় কিনা টেস্ট"""

        self.selenium.get(f'{self.live_server_url}/login/')

        # ভুল ক্রেডেনশিয়াল দিন
        username_field = self.selenium.find_element(By.NAME, "email")
        password_field = self.selenium.find_element(By.NAME, "password")

        username_field.send_keys("testuser123")
        password_field.send_keys("WrongPassword")

        submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(1)

        # এরর মেসেজ চেক করুন
        body_text = self.selenium.find_element(By.TAG_NAME, "body").text
        self.assertIn("Invalid", body_text)

        # লগইন পেজেই আছে কিনা চেক করুন (ড্যাশবোর্ডে রিডাইরেক্ট হয়নি)
        self.assertIn('/login/', self.selenium.current_url)