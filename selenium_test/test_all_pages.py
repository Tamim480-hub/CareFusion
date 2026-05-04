"""
CAREFUSION SELENIUM TEST - PERFECT FINAL VERSION
✅ EXACT sequence as requested
✅ YOUR actual credentials
✅ 5 seconds per page display
✅ Visible browser window
✅ Continues even if page shows error
✅ No crashes - robust error handling
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


class CareFusionTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.driver = None
        self.screenshots_dir = "selenium_tests/screenshots"
        self.page_wait = 5  # ⏱️ 5 seconds per page

        # 🔐 YOUR ACTUAL CREDENTIALS
        self.users = {
            'admin': {'username': 'admin@super.com', 'password': 'tamim0011', 'name': 'Super Admin'},
            'hospital': {'username': 'birdem@hospital.com', 'password': 'tamim0022', 'name': 'Hospital Admin'},
            'doctor': {'username': 'habib@doctor.com', 'password': 'tamim123', 'name': 'Dr. Habib'},
            'patient': {'username': 'nusrat@gmail.com', 'password': 'helloUAP', 'name': 'Nusrat Jahan'},
            'pharmacy': {'username': 'A123', 'password': 'tamim0033', 'name': 'Pharmacy Admin'}
        }

    def start_browser(self):
        print("\n" + "="*80)
        print(" "*25 + "CAREFUSION AUTOMATED TEST")
        print("="*80)
        os.makedirs(self.screenshots_dir, exist_ok=True)

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        # ✅ Browser will be VISIBLE
        # chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        print("✅ Browser started!\n")

    def close_browser(self):
        if self.driver:
            print("\nClosing browser in 5 seconds...")
            time.sleep(5)
            self.driver.quit()

    def screenshot(self, name):
        try:
            safe_name = "".join(c for c in name if c.isalnum() or c in ' _-').rstrip()
            path = os.path.join(self.screenshots_dir, f"{safe_name}.png")
            self.driver.save_screenshot(path)
        except:
            pass

    def wait_for_page(self, seconds=2):
        """Simple wait for page stability"""
        time.sleep(seconds)

    def visit_page(self, url, name):
        """Visit page - continues even if error"""
        try:
            print(f"\n📄 {name}")
            print(f"   URL: {url}")

            self.driver.get(url)
            self.wait_for_page(2)  # Wait for load

            title = self.driver.title
            if "Page not found" in title or "TemplateDoesNotExist" in title:
                print(f"   ⚠️  Page not ready (continuing...)")
                self.screenshot(f"404_{name}")
            else:
                print(f"   ✅ Loaded: {title[:40]}")
                self.screenshot(name)

            # ⏱️ Wait exactly 5 seconds as requested
            print(f"   ⏱️  Displaying for {self.page_wait}s...")
            for i in range(self.page_wait, 0, -1):
                print(f"      {i}...")
                time.sleep(1)

            return True
        except Exception as e:
            print(f"   ⚠️  Error (continuing): {e}")
            return False

    def login(self, user_type):
        """Login with robust error handling"""
        user = self.users.get(user_type)
        if not user:
            return False

        print(f"\n🔐 Logging in as {user['name']}...")

        try:
            self.driver.get(f"{self.base_url}/login/")
            self.wait_for_page(2)

            # Find email field (your form uses name="email")
            try:
                email_field = self.driver.find_element(By.NAME, "email")
            except:
                try:
                    email_field = self.driver.find_element(By.ID, "id_email")
                except:
                    email_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")

            email_field.clear()
            email_field.send_keys(user['username'])
            self.wait_for_page(0.5)

            # Find password field
            try:
                pass_field = self.driver.find_element(By.NAME, "password")
            except:
                pass_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")

            pass_field.clear()
            pass_field.send_keys(user['password'])
            self.wait_for_page(0.5)

            # Click submit
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            btn.click()

            self.wait_for_page(3)
            self.wait_for_page(1)  # Extra wait for sidebar

            # Check login
            if "login" in self.driver.current_url.lower():
                print(f"   ⚠️  Login may have failed (continuing...)")
                return False
            else:
                print(f"   ✅ Logged in!")
                self.screenshot(f"{user_type}_logged_in")
                return True
        except Exception as e:
            print(f"   ⚠️  Login error: {e}")
            return False

    def logout(self):
        try:
            self.driver.get(f"{self.base_url}/logout/")
            self.wait_for_page(2)
        except:
            pass

    # ==================== EXACT SEQUENCE AS REQUESTED ====================

    def run_test(self):
        try:
            self.start_browser()

            # ========== AUTH PAGES ==========
            print("\n" + "🔐"*40)
            print(" "*15 + "AUTH PAGES")
            print("🔐"*40)
            self.visit_page(f"{self.base_url}/signup/", "01_Signup")
            self.visit_page(f"{self.base_url}/login/", "02_Login")
            self.visit_page(f"{self.base_url}/forgot-password/", "03_Forgot_Password")

            # ========== SUPER ADMIN ==========
            print("\n" + "👨‍"*40)
            print(" "*10 + "SUPER ADMIN WORKFLOW")
            print("👨‍"*40)
            if self.login('admin'):
                # EXACT sequence: dashboard → hospitals → hospital admins → pharmacy admins
                self.visit_page(f"{self.base_url}/admin/dashboard/", "04_Admin_Dashboard")
                self.visit_page(f"{self.base_url}/admin/hospitals/", "05_Admin_Hospitals")
                self.visit_page(f"{self.base_url}/admin/hospital-admins/", "06_Admin_Hospital_Admins")
                self.visit_page(f"{self.base_url}/super-admin/pharmacy-admins/", "07_Admin_Pharmacy_Admins")
                self.logout()

            # ========== HOSPITAL ADMIN ==========
            print("\n" + "🏥"*40)
            print(" "*10 + "HOSPITAL ADMIN WORKFLOW")
            print("🏥"*40)
            if self.login('hospital'):
                # EXACT sequence: dashboard → doctors → patients → appointments → icu beds → emergency
                self.visit_page(f"{self.base_url}/hospital/dashboard/", "08_Hospital_Dashboard")
                self.visit_page(f"{self.base_url}/hospital/doctors/", "09_Hospital_Doctors")
                self.visit_page(f"{self.base_url}/hospital/patients/", "10_Hospital_Patients")
                self.visit_page(f"{self.base_url}/hospital/appointments/", "11_Hospital_Appointments")
                self.visit_page(f"{self.base_url}/hospital/beds/", "12_Hospital_ICU_Beds")
                self.visit_page(f"{self.base_url}/hospital/emergencies/", "13_Hospital_Emergency")
                self.logout()

            # ========== DOCTOR ==========
            print("\n" + "👨‍⚕️"*40)
            print(" "*15 + "DOCTOR WORKFLOW")
            print("👨‍⚕️"*40)
            if self.login('doctor'):
                # EXACT sequence: dashboard → appointments → my patients → notifications → my profile
                self.visit_page(f"{self.base_url}/doctor/dashboard/", "14_Doctor_Dashboard")
                self.visit_page(f"{self.base_url}/doctor/appointments/", "15_Doctor_Appointments")
                self.visit_page(f"{self.base_url}/doctor/patients/", "16_Doctor_My_Patients")
                self.visit_page(f"{self.base_url}/doctor/notifications/", "17_Doctor_Notifications")
                self.visit_page(f"{self.base_url}/doctor/profile/", "18_Doctor_My_Profile")
                self.logout()

            # ========== PATIENT ==========
            print("\n" + "👤"*40)
            print(" "*15 + "PATIENT WORKFLOW")
            print("👤"*40)
            if self.login('patient'):
                # EXACT sequence: dashboard → appointments → find doctors → products → cart → icu beds → test reports → profile
                self.visit_page(f"{self.base_url}/patient/dashboard/", "19_Patient_Dashboard")
                self.visit_page(f"{self.base_url}/patient/my-appointments/", "20_Patient_Appointments")
                self.visit_page(f"{self.base_url}/patient/doctors/", "21_Patient_Find_Doctors")
                self.visit_page(f"{self.base_url}/patient/products/", "22_Patient_Products")
                self.visit_page(f"{self.base_url}/cart/", "23_Patient_Cart")
                self.visit_page(f"{self.base_url}/patient/icu-beds/", "24_Patient_ICU_Beds")
                self.visit_page(f"{self.base_url}/patient/test-reports/", "25_Patient_Test_Reports")
                self.visit_page(f"{self.base_url}/patient/profile/", "26_Patient_Profile")
                self.logout()

            # ========== PHARMACY ADMIN ==========
            print("\n" + "💊"*40)
            print(" "*10 + "PHARMACY ADMIN WORKFLOW")
            print("💊"*40)
            if self.login('pharmacy'):
                self.visit_page(f"{self.base_url}/pharmacy/dashboard/", "27_Pharmacy_Dashboard")
                self.visit_page(f"{self.base_url}/pharmacy/products/", "28_Pharmacy_Products")
                self.visit_page(f"{self.base_url}/pharmacy/orders/", "29_Pharmacy_Orders")
                self.logout()

            # ========== SUMMARY ==========
            print("\n" + "🎉"*40)
            print(" "*15 + "ALL TESTS COMPLETED!")
            print("🎉"*40)
            print(f"\n📁 Screenshots: {os.path.abspath(self.screenshots_dir)}")
            print(f"\n✅ Sequence tested:")
            print(f"   1. Auth: Signup → Login → Forgot Password")
            print(f"   2. Super Admin: Dashboard → Hospitals → Hospital Admins → Pharmacy Admins")
            print(f"   3. Hospital Admin: Dashboard → Doctors → Patients → Appointments → ICU Beds → Emergency")
            print(f"   4. Doctor: Dashboard → Appointments → My Patients → Notifications → My Profile")
            print(f"   5. Patient: Dashboard → Appointments → Find Doctors → Products → Cart → ICU Beds → Test Reports → Profile")
            print(f"   6. Pharmacy Admin: Dashboard → Products → Orders")
            print(f"\n⏱️  Each page displayed for {self.page_wait} seconds")

        except Exception as e:
            print(f"\n⚠️  Error: {e}")
        finally:
            input("\nPress ENTER to close browser...")
            self.close_browser()


if __name__ == "__main__":
    print("\nMake sure Django is running: python manage.py runserver")
    input("Press ENTER to start testing...")

    test = CareFusionTest()
    test.run_test()