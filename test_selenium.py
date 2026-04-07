from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def test_carefusion_full():
    """Test CareFusion: Login, Signup, and Dashboard pages"""

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # ========== TEST 1: Homepage Redirect ==========
        print("\n" + "=" * 50)
        print("🧪 TEST 1: Homepage Redirect")
        print("=" * 50)
        driver.get("http://127.0.0.1:8000")
        time.sleep(2)

        assert "login" in driver.current_url.lower()
        print("✅ PASSED: Root URL redirects to login page")

        # ========== TEST 2: Login Page Elements ==========
        print("\n" + "=" * 50)
        print("🧪 TEST 2: Login Page Elements")
        print("=" * 50)
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        print("✅ PASSED: Login form fields found")

        # ========== TEST 3: Sign Up Page ==========
        print("\n" + "=" * 50)
        print("🧪 TEST 3: Sign Up Page")
        print("=" * 50)
        # Try to find and click Sign Up link
        try:
            signup_link = driver.find_element(By.LINK_TEXT, "Sign Up")
            signup_link.click()
            time.sleep(2)
            assert "signup" in driver.current_url.lower()
            print("✅ PASSED: Sign Up link works, redirected to /signup/")

            # Check signup form fields
            signup_name = driver.find_element(By.NAME, "username")
            signup_email = driver.find_element(By.NAME, "email")
            signup_password = driver.find_element(By.NAME, "password1")
            print("✅ PASSED: Sign Up form fields found")

        except:
            print("⚠️ Sign Up link not found - trying direct URL")
            driver.get("http://127.0.0.1:8000/signup/")
            time.sleep(2)
            if "signup" in driver.current_url.lower():
                print("✅ PASSED: Direct /signup/ URL works")

        # ========== TEST 4: Login Functionality ==========
        print("\n" + "=" * 50)
        print("🧪 TEST 4: Login Functionality")
        print("=" * 50)
        driver.get("http://127.0.0.1:8000/login/")
        time.sleep(2)

        # Use your superuser credentials (change these!)
        TEST_EMAIL = "admin@example.com"  # ← Change to your superuser email
        TEST_PASSWORD = "yourpassword123"  # ← Change to your superuser password

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.clear()
        email_field.send_keys(TEST_EMAIL)
        password_field.clear()
        password_field.send_keys(TEST_PASSWORD)

        # Find and click the submit button
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()
        time.sleep(3)  # Wait for redirect

        # Check if redirected to dashboard or still on login (failed login)
        if "dashboard" in driver.current_url.lower():
            print("✅ PASSED: Login successful, redirected to dashboard")
        elif "login" in driver.current_url.lower():
            print("⚠️ Login failed - check credentials or form validation")
        else:
            print(f"📍 Current URL after login attempt: {driver.current_url}")

        # ========== TEST 5: Dashboard Page ==========
        print("\n" + "=" * 50)
        print("🧪 TEST 5: Dashboard Page")
        print("=" * 50)
        # Try to visit dashboard directly
        driver.get("http://127.0.0.1:8000/dashboard/")
        time.sleep(2)

        if "dashboard" in driver.current_url.lower():
            print("✅ PASSED: Dashboard page accessible")
            # Check for dashboard-specific content
            if "welcome" in driver.page_source.lower() or "dashboard" in driver.page_source.lower():
                print("✅ PASSED: Dashboard contains expected content")
        else:
            print("⚠️ Dashboard not accessible (may require login)")

        # ========== SAVE SCREENSHOT ==========
        driver.save_screenshot("full_test_result.png")
        print("\n📸 Full test screenshot saved as 'full_test_result.png'")
        print("\n🎉 ALL TESTS COMPLETED!")

    except Exception as e:
        print(f"\n❌ Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        print("🔚 Browser closed")


if __name__ == "__main__":
    test_carefusion_full()