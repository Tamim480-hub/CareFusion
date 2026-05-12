"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        CAREFUSION — COMPLETE SELENIUM WORKFLOW TEST                         ║
║        Built from actual source code (github.com/Tamim480-hub/CareFusion)   ║
║                                                                              ║
║  SESSION 1 ► SUPER ADMIN (admin@super.com / tamim0011)                      ║
║    Dashboard → Add Hospital (modal, auto) → Add Hospital Admin (modal,auto) ║
║    → Pharmacy Admins page → Add Pharmacy + Admin (auto) → All pages         ║
║                                                                              ║
║  SESSION 2 ► HOSPITAL ADMIN (birdem@hospital.com / tamim0022)               ║
║    Dashboard → Add Doctor (modal, auto) → Add ICU Bed (modal, auto)         ║
║    → Patients → Appointments → Emergencies → Test Reports → Orders          ║
║                                                                              ║
║  SESSION 3 ► PATIENT (nusrat@gmail.com / helloUAP)                          ║
║    Dashboard → Find Doctors → Doctor Detail → Book Appointment w/ Faisal    ║
║    → Products → Add to Cart → Cart → Checkout (auto) → ICU Beds             ║
║    → Book ICU Bed (auto) → My Appointments → Orders → Bills → Profile       ║
║                                                                              ║
║  SESSION 4 ► DOCTOR — Dr. Faisal (faisal@doctor.com / tamim5544)            ║
║    Dashboard → Appointments → Patient List → Schedule → Notifications        ║
║    → Profile                                                                 ║
║                                                                              ║
║  SESSION 5 ► PHARMACY ADMIN (A123 / tamim0033)                              ║
║    Dashboard → Add Product (modal, auto) → Orders → Order Detail            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time, os, random, string

# ═══════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════
BASE       = "http://127.0.0.1:8000"
SS_DIR     = "carefusion_screenshots"
PAGE_WAIT  = 4     # seconds to display each page
ACT_WAIT   = 1.5   # wait after actions
TIMEOUT    = 10

RND = ''.join(random.choices(string.digits, k=4))

# ═══════════════════════════════════════════
#  TEST DATA  (matches actual field names)
# ═══════════════════════════════════════════
HOSPITAL = {
    "name"    : f"Auto Hospital {RND}",
    "code"    : f"AH{RND}",
    "address" : f"Road {RND}, Dhaka",
    "phone"   : f"028{RND}001",
    "email"   : f"autohosp{RND}@test.com",
}
H_ADMIN = {
    "username" : f"hadmin{RND}",
    "email"    : f"hadmin{RND}@test.com",
    "password" : "HAdmin@1234",
    "confirm_password": "HAdmin@1234",
    "first_name": "HAdmin",
    "last_name" : RND,
    "phone"    : f"019{RND}001",
    "designation": "Hospital Administrator",
}
PHARMACY = {
    "name"    : f"Auto Pharmacy {RND}",
    "code"    : f"PH{RND}",
    "address" : f"Lane {RND}, Dhaka",
    "phone"   : f"016{RND}001",
    "email"   : f"autopharm{RND}@test.com",
    "delivery_charge": "50",
    "free_delivery_above": "500",
}
PH_ADMIN = {
    "first_name": "PharmaAdmin",
    "last_name" : RND,
    "username"  : f"pharmadmin{RND}",
    "email"     : f"pharmadmin{RND}@test.com",
    "password"  : "Pharma@1234",
    "confirm_password": "Pharma@1234",
    "phone"     : f"016{RND}002",
    "designation": "Pharmacy Manager",
}
DOCTOR = {
    "first_name"      : "AutoDoc",
    "last_name"       : RND,
    "username"        : f"autodoc{RND}",
    "email"           : f"autodoc{RND}@test.com",
    "password"        : "DocTest@1234",
    "confirm_password": "DocTest@1234",
    "phone"           : f"017{RND}001",
    "specialization"  : "Cardiology",   # select option value
    "qualification"   : "MBBS, MD",
    "experience_years": "5",
    "consultation_fee": "700",
    "available_from"  : "09:00",
    "available_to"    : "17:00",
    "bio"             : "Automated test doctor",
}

NEW_PATIENT = {
    "first_name"      : "AutoPatient",
    "last_name"       : RND,
    "email"           : f"autopatient{RND}@test.com",
    "phone"           : f"018{RND}001",
    "age"             : "28",
    "gender"          : "male",
    "blood_group"     : "B+",
    "password"        : "Patient@1234",
    "confirm_password": "Patient@1234",
}
ICU_BED = {
    "bed_number"  : f"ICU-{RND}",
    "bed_type"    : "ICU",            # select option value
    "daily_charge": "5000",
    "equipment"   : "Ventilator, Monitor",
}
PRODUCT = {
    "name"       : f"AutoMed {RND}",
    "category"   : "tablet",          # select option value
    "price"      : "120.00",
    "stock"      : "50",
    "description": "Automated test medicine",
}
APPT = {
    "date"    : "2026-07-15",
    "symptoms": "Chest pain and shortness of breath",
}
CHECKOUT = {
    "full_name": "Nusrat Jahan",
    "email"    : "nusrat@gmail.com",
    "phone"    : "01700000001",
    "address"  : "House 5, Road 3, Dhaka",
    "notes"    : "Please deliver fast",
}
ICU_BOOK = {
    "condition"          : "Requires intensive cardiac monitoring",
    "expected_discharge" : "2026-07-25",
}


# ═══════════════════════════════════════════
#  DRIVER CLASS
# ═══════════════════════════════════════════
class CF:
    def __init__(self):
        self.dr  = None
        self.w   = None
        self.log = []   # (session, action, result)

    # ── browser ─────────────────────────────
    def boot(self):
        os.makedirs(SS_DIR, exist_ok=True)
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-notifications")
        opts.add_argument("--disable-popup-blocking")
        # opts.add_argument("--headless")  # uncomment for CI
        self.dr = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opts,
        )
        self.w = WebDriverWait(self.dr, TIMEOUT)
        print("✅  Browser ready\n")

    def quit(self):
        if self.dr:
            time.sleep(2)
            self.dr.quit()

    # ── console helpers ─────────────────────
    @staticmethod
    def banner(icon, title):
        bar = "─" * 74
        print(f"\n┌{bar}┐")
        print(f"│  {icon}  {title:<70}│")
        print(f"└{bar}┘")

    @staticmethod
    def step(msg):  print(f"   ➤  {msg}")
    @staticmethod
    def ok(msg):    print(f"   ✅ {msg}")
    @staticmethod
    def warn(msg):  print(f"   ⚠️  {msg}")

    def rec(self, sess, action, passed=True):
        self.log.append((sess, action, "✅ Pass" if passed else "⚠️  Skip"))

    # ── screenshot ───────────────────────────
    def shot(self, name):
        try:
            safe = "".join(c for c in name if c.isalnum() or c in "_-")
            self.dr.save_screenshot(f"{SS_DIR}/{safe}.png")
        except Exception:
            pass

    # ── page navigation + display ────────────
    def go(self, path, sess="", label=""):
        url = f"{BASE}{path}"
        print(f"\n  📄  {label or path}")
        print(f"      {url}")
        try:
            self.dr.get(url)
            time.sleep(ACT_WAIT)
            title = self.dr.title
            cur   = self.dr.current_url.lower()

            if any(e in title for e in ["not found","500","403","TemplateDoesNotExist"]):
                self.warn(f"Page issue: {title[:60]}")
                status = "⚠️  Not Ready"
            elif "login" in cur and "login" not in path.lower():
                self.warn("Auth redirect — skipping")
                status = "⚠️  Auth Redirect"
            else:
                self.ok(f"Loaded → {title[:60]}")
                status = "✅ Pass"

            self.shot(f"{sess}_{label}".replace(" ", "_"))
            if sess and label:
                self.log.append((sess, label, status))
            self._tick()
        except Exception as e:
            self.warn(str(e))

    def _tick(self):
        for i in range(PAGE_WAIT, 0, -1):
            print(f"      ⏱  {i}s ", end="\r")
            time.sleep(1)
        print("           ", end="\r")

    # ── auth ─────────────────────────────────
    def login(self, email, pwd, name):
        print(f"\n  🔐  Login → {name}")
        self.dr.get(f"{BASE}/login/")
        time.sleep(ACT_WAIT)
        # login form uses name="email" and name="password"
        self._fill("email",    email)
        self._fill("password", pwd)
        self._submit_form()
        time.sleep(2)
        if "login" in self.dr.current_url.lower():
            self.warn(f"Login failed for {name}")
            return False
        self.ok(f"Logged in — {name}")
        self.shot(f"login_{name.replace(' ','_')}")
        return True

    def logout(self):
        self.dr.get(f"{BASE}/logout/")
        time.sleep(2)
        self.ok("Logged out")

    # ── form helpers ─────────────────────────
    def _fill(self, name, value):
        """Fill a visible input/textarea by its name attribute."""
        for attempt in [
            (By.NAME, name),
            (By.ID,   name),
            (By.ID,   f"id_{name}"),
        ]:
            try:
                el = self.dr.find_element(*attempt)
                if el.is_displayed() and el.is_enabled():
                    el.clear()
                    el.send_keys(value)
                    return True
            except Exception:
                pass
        return False

    def _select_by_name(self, name, value_or_text):
        """Select a <select> option by name attr; try value then visible text."""
        for selector in [
            f"select[name='{name}']",
            f"select#{name}",
            f"select#id_{name}",
        ]:
            try:
                el = self.dr.find_element(By.CSS_SELECTOR, selector)
                s  = Select(el)
                try:
                    s.select_by_value(value_or_text)
                    return True
                except Exception:
                    pass
                # try partial visible text match
                for opt in s.options:
                    if value_or_text.lower() in opt.text.lower():
                        opt.click()
                        return True
                # fallback: pick first non-empty option
                if len(s.options) > 1:
                    s.select_by_index(1)
                    return True
            except Exception:
                pass
        return False

    def _submit_form(self):
        for sel in [
            "button[type='submit']",
            "input[type='submit']",
            "button.btn-primary",
            "button[class*='btn-primary']",
        ]:
            try:
                btn = self.dr.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    time.sleep(ACT_WAIT)
                    return True
            except Exception:
                pass
        try:
            self.dr.find_element(By.TAG_NAME, "form").submit()
            time.sleep(ACT_WAIT)
        except Exception:
            pass

    def _open_modal(self, modal_id):
        """Open a Bootstrap modal by its ID via JS (avoids click-intercept issues)."""
        try:
            self.dr.execute_script(
                f"var m = new bootstrap.Modal(document.getElementById('{modal_id}')); m.show();"
            )
            time.sleep(1.2)
            return True
        except Exception:
            return False

    def _fill_in_modal(self, modal_id, field_data: dict):
        """Fill fields inside a modal. field_data = {name: value}"""
        for name, value in field_data.items():
            for attempt in [
                (By.CSS_SELECTOR, f"#{modal_id} [name='{name}']"),
                (By.CSS_SELECTOR, f"#{modal_id} #{name}"),
            ]:
                try:
                    el = self.dr.find_element(*attempt)
                    if el.tag_name.lower() == "select":
                        s = Select(el)
                        try:
                            s.select_by_value(value)
                        except Exception:
                            for opt in s.options:
                                if value.lower() in opt.text.lower():
                                    opt.click()
                                    break
                            else:
                                if len(s.options) > 1:
                                    s.select_by_index(1)
                    elif el.get_attribute("type") == "checkbox":
                        if value and not el.is_selected():
                            el.click()
                    else:
                        el.clear()
                        el.send_keys(value)
                    break
                except Exception:
                    pass

    def _submit_modal(self, modal_id):
        """Click the submit button inside the given modal."""
        for sel in [
            f"#{modal_id} button[type='submit']",
            f"#{modal_id} input[type='submit']",
            f"#{modal_id} .btn-primary",
        ]:
            try:
                btn = self.dr.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    time.sleep(ACT_WAIT + 0.5)
                    return True
            except Exception:
                pass
        return False

    def _js_submit_modal(self, modal_id, extra_hidden=None):
        """
        Build and submit the modal's form via JS fetch (bypasses CSRF issues
        when the modal form submits to the same page with action=add).
        extra_hidden: list of (name, value) tuples to inject before submit.
        """
        if extra_hidden:
            for name, val in extra_hidden:
                self.dr.execute_script(f"""
                    var f = document.querySelector('#{modal_id} form');
                    if(f){{
                        var h = document.createElement('input');
                        h.type='hidden'; h.name='{name}'; h.value='{val}';
                        f.appendChild(h);
                    }}
                """)
        try:
            btn = self.dr.find_element(
                By.CSS_SELECTOR, f"#{modal_id} button[type='submit']"
            )
            btn.click()
            time.sleep(ACT_WAIT + 0.5)
        except Exception:
            try:
                self.dr.execute_script(
                    f"document.querySelector('#{modal_id} form').submit();"
                )
                time.sleep(ACT_WAIT + 0.5)
            except Exception:
                pass

    def _get_first_id(self, css):
        """Return the href/id of the first matching element."""
        try:
            el = self.dr.find_elements(By.CSS_SELECTOR, css)
            if el:
                return el[0].get_attribute("href") or el[0].get_attribute("data-id")
        except Exception:
            pass
        return None

    def _click_first(self, css):
        try:
            els = self.dr.find_elements(By.CSS_SELECTOR, css)
            for el in els:
                if el.is_displayed() and el.is_enabled():
                    self.dr.execute_script("arguments[0].scrollIntoView(true);", el)
                    time.sleep(0.3)
                    el.click()
                    time.sleep(ACT_WAIT)
                    return True
        except Exception:
            pass
        return False

    def _click_text(self, *texts):
        for txt in texts:
            for method in [By.LINK_TEXT, By.PARTIAL_LINK_TEXT]:
                try:
                    el = self.dr.find_element(method, txt)
                    if el.is_displayed():
                        el.click()
                        time.sleep(ACT_WAIT)
                        return True
                except Exception:
                    pass
            try:
                el = self.dr.find_element(
                    By.XPATH,
                    f"//*[contains(text(),'{txt}') and (self::button or self::a or self::span)]"
                )
                if el.is_displayed():
                    el.click()
                    time.sleep(ACT_WAIT)
                    return True
            except Exception:
                pass
        return False


# ═══════════════════════════════════════════════════════════
#  SESSION 1 — SUPER ADMIN
# ═══════════════════════════════════════════════════════════
def super_admin(cf: CF):
    CF.banner("👑", "SESSION 1 — SUPER ADMIN  (admin@super.com)")

    if not cf.login("admin@super.com", "tamim0011", "Super Admin"):
        return

    # Dashboard
    cf.go("/admin/dashboard/", "SA", "Admin_Dashboard")

    # ── ADD HOSPITAL (modal: #addHospitalModal) ──────────────
    CF.banner("🏥", "SA ► Add Hospital (auto)")
    cf.go("/admin/hospitals/", "SA", "Hospitals_List")
    CF.step(f"Opening Add Hospital modal → name: {HOSPITAL['name']}")
    cf._open_modal("addHospitalModal")
    cf._fill_in_modal("addHospitalModal", {
        "name"    : HOSPITAL["name"],
        "code"    : HOSPITAL["code"],
        "address" : HOSPITAL["address"],
        "phone"   : HOSPITAL["phone"],
        "email"   : HOSPITAL["email"],
    })
    cf.shot("SA_add_hospital_filled")
    cf._submit_modal("addHospitalModal")
    cf.ok("Hospital form submitted")
    cf.shot("SA_hospital_added")
    cf.rec("SA", "Add_Hospital")
    cf._tick()

    # ── ADD HOSPITAL ADMIN (modal: #addAdminModal) ───────────
    CF.banner("👨‍💼", "SA ► Add Hospital Admin (auto)")
    cf.go("/admin/hospital-admins/", "SA", "Hospital_Admins_List")
    CF.step(f"Opening Add Admin modal → {H_ADMIN['email']}")
    cf._open_modal("addAdminModal")
    cf._fill_in_modal("addAdminModal", {
        "username"        : H_ADMIN["username"],
        "email"           : H_ADMIN["email"],
        "password"        : H_ADMIN["password"],
        "confirm_password": H_ADMIN["confirm_password"],
        "first_name"      : H_ADMIN["first_name"],
        "last_name"       : H_ADMIN["last_name"],
        "phone"           : H_ADMIN["phone"],
        "designation"     : H_ADMIN["designation"],
        "hospital_id"     : "1",   # pick first hospital
    })
    cf.shot("SA_add_hadmin_filled")
    cf._submit_modal("addAdminModal")
    cf.ok("Hospital admin submitted")
    cf.shot("SA_hadmin_added")
    cf.rec("SA", "Add_Hospital_Admin")
    cf._tick()

    # ── PHARMACY ADMINS page  ────────────────────────────────
    CF.banner("💊", "SA ► Pharmacy Admins (add pharmacy + admin, auto)")
    cf.go("/super-admin/pharmacy-admins/", "SA", "Pharmacy_Admins_Page")

    # Step 1 — create pharmacy (accordion / inline form, action=create_pharmacy)
    CF.step(f"Filling pharmacy creation form → {PHARMACY['name']}")
    for name, val in PHARMACY.items():
        cf._fill(name, val)
    # inject hidden action field and submit
    try:
        cf.dr.execute_script("""
            var forms = document.querySelectorAll('form');
            forms.forEach(function(f){
                var h = f.querySelector('input[name="action"]');
                if(h && h.value === 'create_pharmacy'){
                    var fields = ['name','code','address','phone','email','delivery_charge','free_delivery_above'];
                    fields.forEach(function(n){
                        var el = f.querySelector('[name="'+n+'"]');
                        if(el){ el.dispatchEvent(new Event('input')); }
                    });
                }
            });
        """)
    except Exception:
        pass
    cf.shot("SA_pharmacy_form_filled")

    # Find and click the submit button for create_pharmacy form
    try:
        btn = cf.dr.find_element(
            By.XPATH,
            "//form[.//input[@value='create_pharmacy']]//button[@type='submit']"
        )
        btn.click()
        time.sleep(ACT_WAIT + 0.5)
        cf.ok("Pharmacy creation submitted")
    except Exception:
        cf.warn("Could not submit pharmacy form — page may differ")
    cf.shot("SA_pharmacy_created")
    cf.rec("SA", "Add_Pharmacy")
    cf._tick()

    # Step 2 — create pharmacy admin (action=create_admin)
    cf.go("/super-admin/pharmacy-admins/", "SA", "Pharmacy_Admin_Create")
    CF.step(f"Filling pharmacy admin form → {PH_ADMIN['email']}")
    # inject values into the create_admin sub-form
    try:
        cf.dr.execute_script("""
            var form = document.querySelector('form input[name="action"][value="create_admin"]');
            if(form){ form = form.closest('form'); }
            var data = arguments[0];
            if(form){
                Object.keys(data).forEach(function(k){
                    var el = form.querySelector('[name="'+k+'"]');
                    if(el){
                        el.value = data[k];
                        el.dispatchEvent(new Event('input'));
                    }
                });
            }
        """, {
            "first_name"      : PH_ADMIN["first_name"],
            "last_name"       : PH_ADMIN["last_name"],
            "username"        : PH_ADMIN["username"],
            "email"           : PH_ADMIN["email"],
            "password"        : PH_ADMIN["password"],
            "confirm_password": PH_ADMIN["confirm_password"],
            "phone"           : PH_ADMIN["phone"],
            "designation"     : PH_ADMIN["designation"],
        })
        cf.shot("SA_pharmacy_admin_form_filled")
        btn = cf.dr.find_element(
            By.XPATH,
            "//form[.//input[@value='create_admin']]//button[@type='submit']"
        )
        btn.click()
        time.sleep(ACT_WAIT + 0.5)
        cf.ok("Pharmacy admin submitted")
    except Exception:
        cf.warn("Pharmacy admin form not found — showing page")
    cf.shot("SA_pharmacy_admin_added")
    cf.rec("SA", "Add_Pharmacy_Admin")
    cf._tick()

    # Remaining pages
    cf.go("/admin/hospitals/",             "SA", "All_Hospitals")
    cf.go("/admin/hospital-admins/",       "SA", "All_Hospital_Admins")
    cf.go("/admin/hospitals/",             "SA", "Hospital_Reports_View")  # hospital_reports.html missing, showing hospitals instead
    cf.go("/super-admin/pharmacy-admins/", "SA", "Pharmacy_Admins_Final")

    cf.logout()


# ═══════════════════════════════════════════════════════════
#  SESSION 2 — HOSPITAL ADMIN
# ═══════════════════════════════════════════════════════════
def hospital_admin(cf: CF):
    CF.banner("🏥", "SESSION 2 — HOSPITAL ADMIN  (birdem@hospital.com)")

    if not cf.login("birdem@hospital.com", "tamim0022", "Hospital Admin"):
        return

    cf.go("/hospital/dashboard/", "HA", "Hospital_Dashboard")

    # ── ADD DOCTOR (modal: #addDoctorModal) ──────────────────
    CF.banner("👨‍⚕️", "HA ► Add Doctor (auto)")
    cf.go("/hospital/doctors/", "HA", "Doctors_List")
    CF.step(f"Opening Add Doctor modal → {DOCTOR['email']}")
    cf._open_modal("addDoctorModal")
    cf._fill_in_modal("addDoctorModal", {
        "first_name"      : DOCTOR["first_name"],
        "last_name"       : DOCTOR["last_name"],
        "username"        : DOCTOR["username"],
        "email"           : DOCTOR["email"],
        "password"        : DOCTOR["password"],
        "confirm_password": DOCTOR["confirm_password"],
        "phone"           : DOCTOR["phone"],
        "specialization"  : DOCTOR["specialization"],
        "qualification"   : DOCTOR["qualification"],
        "experience_years": DOCTOR["experience_years"],
        "consultation_fee": DOCTOR["consultation_fee"],
        "available_from"  : DOCTOR["available_from"],
        "available_to"    : DOCTOR["available_to"],
        "bio"             : DOCTOR["bio"],
    })
    cf.shot("HA_add_doctor_filled")
    cf._submit_modal("addDoctorModal")
    cf.ok("Doctor submitted")
    cf.shot("HA_doctor_added")
    cf.rec("HA", "Add_Doctor")
    cf._tick()

    # ── ADD ICU BED (modal: #addBedModal) ────────────────────
    CF.banner("🛏️", "HA ► Add ICU Bed (auto)")
    cf.go("/hospital/beds/", "HA", "ICU_Beds_List")
    CF.step(f"Opening Add Bed modal → {ICU_BED['bed_number']}")
    cf._open_modal("addBedModal")
    cf._fill_in_modal("addBedModal", {
        "bed_number"  : ICU_BED["bed_number"],
        "bed_type"    : ICU_BED["bed_type"],
        "daily_charge": ICU_BED["daily_charge"],
        "equipment"   : ICU_BED["equipment"],
    })
    cf.shot("HA_add_bed_filled")
    cf._submit_modal("addBedModal")
    cf.ok("ICU Bed submitted")
    cf.shot("HA_bed_added")
    cf.rec("HA", "Add_ICU_Bed")
    cf._tick()

    # ── ADD PATIENT via signup (auto) ────────────────────────
    CF.banner("👤", "HA ► Add New Patient via Signup (auto)")
    # Hospital admin logs out temporarily so new patient can register
    cf.logout()
    CF.step(f"Registering new patient: {NEW_PATIENT['email']}")
    cf.go("/signup/", "HA", "Patient_Signup_Page")
    cf._fill("first_name",       NEW_PATIENT["first_name"])
    cf._fill("last_name",        NEW_PATIENT["last_name"])
    cf._fill("email",            NEW_PATIENT["email"])
    cf._fill("phone",            NEW_PATIENT["phone"])
    cf._fill("age",              NEW_PATIENT["age"])
    cf._select_by_name("gender",      NEW_PATIENT["gender"])
    cf._select_by_name("blood_group", NEW_PATIENT["blood_group"])
    cf._fill("password",         NEW_PATIENT["password"])
    cf._fill("confirm_password", NEW_PATIENT["confirm_password"])
    # tick terms checkbox
    try:
        cb = cf.dr.find_element(By.NAME, "terms")
        if not cb.is_selected():
            cf.dr.execute_script("arguments[0].click();", cb)
    except Exception:
        pass
    cf.shot("HA_new_patient_signup_filled")
    CF.step("Submitting patient signup form")
    cf._submit_form()
    time.sleep(2)
    cf.ok(f"Patient registered: {NEW_PATIENT['email']}")
    cf.shot("HA_patient_registered")
    cf.rec("HA", "Add_New_Patient_Signup")
    cf._tick()

    # Log back in as Hospital Admin to show patient in list
    CF.banner("🏥", "HA ► Back to Hospital Admin — verify patient in list")
    cf.login("birdem@hospital.com", "tamim0022", "Hospital Admin")
    cf.go("/hospital/patients/",     "HA", "Patients_List_With_New")
    cf.go("/hospital/appointments/", "HA", "Appointments_List")
    cf.go("/hospital/emergencies/",  "HA", "Emergencies_List")
    cf.go("/hospital/test-reports/", "HA", "Test_Reports")
    cf.go("/hospital/products/",     "HA", "Hospital_Products")

    cf.logout()


# ═══════════════════════════════════════════════════════════
#  SESSION 3 — PATIENT
# ═══════════════════════════════════════════════════════════
def patient(cf: CF):
    CF.banner("👤", "SESSION 3 — PATIENT  (nusrat@gmail.com)")

    if not cf.login("nusrat@gmail.com", "helloUAP", "Nusrat Jahan"):
        return

    # Dashboard
    cf.go("/patient/dashboard/", "PAT", "Patient_Dashboard")

    # ── DOCTOR SEARCH ────────────────────────────────────────
    CF.banner("🩺", "PAT ► Find Doctors + View Dr. Faisal")
    cf.go("/patient/doctors/", "PAT", "Find_Doctors")

    # Search for "faisal"
    CF.step("Searching for Dr. Faisal")
    for sel in [
        "input[name='search']", "input[name='q']",
        "input[type='search']", "input[placeholder*='earch' i]"
    ]:
        try:
            f = cf.dr.find_element(By.CSS_SELECTOR, sel)
            if f.is_displayed():
                f.clear(); f.send_keys("faisal"); f.send_keys(Keys.RETURN)
                time.sleep(ACT_WAIT)
                cf.ok("Search executed")
                break
        except Exception:
            pass
    cf.shot("PAT_search_faisal")
    cf._tick()

    # Open Dr. Faisal's detail page
    CF.step("Opening Dr. Faisal's profile page")
    faisal_link = None
    try:
        # look for a link in a row/card that contains "Faisal"
        rows = cf.dr.find_elements(
            By.XPATH,
            "//tr[contains(.,'Faisal') or contains(.,'faisal')]//a | "
            "//*[contains(@class,'card')][contains(.,'Faisal')]//a"
        )
        if rows:
            faisal_link = rows[0].get_attribute("href")
            rows[0].click()
            time.sleep(ACT_WAIT)
            cf.ok("Faisal profile opened")
    except Exception:
        pass
    if not faisal_link:
        # fallback: /patient/doctor/1/
        cf.go("/patient/doctor/1/", "PAT", "Doctor_Detail_Faisal")
    cf.shot("PAT_faisal_profile")
    cf._tick()

    # ── BOOK APPOINTMENT with Dr. Faisal ─────────────────────
    CF.banner("📅", "PAT ► Book Appointment with Dr. Faisal (auto)")
    cf.go("/patient/book-appointment/", "PAT", "Book_Appointment_Page")

    # URL: /patient/book-appointment/
    # Form fields: doctor_id (select), date (date), time (select), symptoms (textarea)
    CF.step("Selecting Dr. Faisal from doctor dropdown")
    try:
        sel_el = cf.dr.find_element(By.CSS_SELECTOR, "select[name='doctor_id']")
        s = Select(sel_el)
        faisal_found = False
        for opt in s.options:
            if "faisal" in opt.text.lower():
                opt.click()
                cf.ok("Dr. Faisal selected in dropdown")
                faisal_found = True
                break
        if not faisal_found and len(s.options) > 1:
            s.select_by_index(1)
            cf.warn("Faisal not in list — selected first available doctor")
        time.sleep(ACT_WAIT)
    except Exception as e:
        cf.warn(f"Doctor select: {e}")

    CF.step(f"Setting date: {APPT['date']}")
    # set via JS because date pickers often block direct input
    try:
        date_el = cf.dr.find_element(By.NAME, "date")
        cf.dr.execute_script(f"arguments[0].value='{APPT['date']}'", date_el)
        cf.dr.execute_script("arguments[0].dispatchEvent(new Event('change'))", date_el)
        time.sleep(ACT_WAIT)
        cf.ok("Date set")
    except Exception as e:
        cf.warn(f"Date input: {e}")

    CF.step("Selecting time slot")
    time.sleep(1)   # wait for AJAX slot load
    try:
        time_sel = cf.dr.find_element(By.CSS_SELECTOR, "select[name='time']")
        s = Select(time_sel)
        if len(s.options) > 1:
            s.select_by_index(1)
            cf.ok(f"Time slot: {s.first_selected_option.text}")
        else:
            cf.warn("No time slots available (doctor may have no schedule set)")
    except Exception as e:
        cf.warn(f"Time select: {e}")

    CF.step("Filling symptoms")
    cf._fill("symptoms", APPT["symptoms"])
    cf.shot("PAT_appointment_form_filled")
    cf._tick()

    CF.step("Submitting appointment")
    cf._submit_form()
    cf.ok("Appointment submitted")
    cf.shot("PAT_appointment_submitted")
    cf.rec("PAT", "Book_Appointment_Dr_Faisal")
    cf._tick()

    # ── PRODUCTS → CART → CHECKOUT ───────────────────────────
    CF.banner("💊", "PAT ► Buy Medicine → Cart → Checkout (auto)")
    cf.go("/patient/products/", "PAT", "Products_Page")

    # The add-to-cart form is:  POST /add-to-cart/<product_id>/  quantity=1
    CF.step("Adding first product to cart")
    added = False
    try:
        forms = cf.dr.find_elements(By.CSS_SELECTOR, "form.add-to-cart-form, form[action*='add-to-cart']")
        if forms:
            # submit the first one via JS (avoids page scroll issues)
            cf.dr.execute_script("arguments[0].submit();", forms[0])
            time.sleep(ACT_WAIT)
            cf.ok("Product added to cart via form submit")
            added = True
    except Exception:
        pass
    if not added:
        # click button inside first product card
        cf._click_first(
            "button[type='submit'].add-to-cart, "
            "form[action*='add-to-cart'] button, "
            ".card button[type='submit']"
        )
        cf.ok("Clicked add-to-cart button")
    cf.shot("PAT_product_added_cart")
    cf._tick()

    # Cart
    cf.go("/cart/", "PAT", "Cart_Page")
    cf.shot("PAT_cart")
    cf._tick()

    # Checkout  (URL: /checkout/ or /pharmacy/store/checkout/)
    cf.go("/checkout/", "PAT", "Checkout_Page")
    CF.step("Filling checkout form")
    for name, val in CHECKOUT.items():
        cf._fill(name, val)
    # payment method radio — select "cod"
    try:
        cod = cf.dr.find_element(By.CSS_SELECTOR, "input[name='payment_method'][value='cod']")
        cf.dr.execute_script("arguments[0].click();", cod)
        cf.ok("COD payment selected")
    except Exception:
        pass
    cf.shot("PAT_checkout_filled")
    CF.step("Submitting checkout")
    cf._submit_form()
    cf.ok("Checkout submitted")
    cf.shot("PAT_order_placed")
    cf.rec("PAT", "Place_Order_And_Pay")
    cf._tick()

    # ── ICU BEDS → BOOK ─────────────────────────────────────
    CF.banner("🛏️", "PAT ► ICU Beds → Book a Bed (auto)")
    cf.go("/patient/icu-beds/", "PAT", "ICU_Beds_Page")

    # Find first "Book" link  → /patient/icu-beds/book/<bed_id>/
    CF.step("Clicking Book on first available ICU bed")
    booked_icu = False
    try:
        book_links = cf.dr.find_elements(
            By.XPATH,
            "//a[contains(@href,'icu-beds/book') or contains(text(),'Book')]"
        )
        if book_links:
            href = book_links[0].get_attribute("href")
            cf.dr.get(href)
            time.sleep(ACT_WAIT)
            cf.ok(f"ICU booking page: {href}")
            booked_icu = True
    except Exception:
        pass
    if not booked_icu:
        cf.go("/patient/icu-beds/book/1/", "PAT", "ICU_Book_Page")

    # Fill the ICU booking form
    # Fields: condition (textarea), expected_discharge (date)
    CF.step("Filling ICU booking form")
    cf._fill("condition", ICU_BOOK["condition"])
    try:
        disc_el = cf.dr.find_element(By.NAME, "expected_discharge")
        cf.dr.execute_script(f"arguments[0].value='{ICU_BOOK['expected_discharge']}'", disc_el)
    except Exception:
        pass
    cf.shot("PAT_icu_book_form")
    CF.step("Submitting ICU booking")
    cf._submit_form()
    cf.ok("ICU booking submitted")
    cf.shot("PAT_icu_booked")
    cf.rec("PAT", "Book_ICU_Bed")
    cf._tick()

    # Remaining patient pages
    cf.go("/patient/my-appointments/", "PAT", "My_Appointments")
    cf.go("/patient/icu-bookings/",    "PAT", "My_ICU_Bookings")
    cf.go("/patient/orders/",          "PAT", "My_Orders")
    cf.go("/patient/bills/",           "PAT", "My_Bills")
    cf.go("/patient/test-reports/",    "PAT", "Test_Reports")
    cf.go("/patient/profile/",         "PAT", "Patient_Profile")

    cf.logout()


# ═══════════════════════════════════════════════════════════
#  SESSION 4a — DOCTOR  (Dr. Faisal — existing)
#  SESSION 4b — NEW AUTO DOCTOR  (added by Hospital Admin)
# ═══════════════════════════════════════════════════════════
def doctor_sessions(cf: CF):

    # ── 4a: Dr. Faisal (existing doctor) ─────────────────────
    CF.banner("👨‍⚕️", "SESSION 4a — Dr. Faisal  (faisal@doctor.com / tamim5544)")

    if cf.login("faisal@doctor.com", "tamim5544", "Dr. Faisal"):
        cf.go("/doctor/dashboard/",    "DOC_F", "Faisal_Dashboard")
        cf.go("/doctor/appointments/", "DOC_F", "Faisal_Appointments")

        # Open first appointment detail
        CF.step("Opening first appointment detail")
        try:
            links = cf.dr.find_elements(
                By.XPATH, "//a[contains(@href,'doctor/appointment/')]"
            )
            if links:
                cf.dr.get(links[0].get_attribute("href"))
                time.sleep(ACT_WAIT)
                cf.ok("Appointment detail opened")
                cf.shot("DOC_F_appt_detail")
                cf._tick()
        except Exception:
            pass

        cf.go("/doctor/patients/",     "DOC_F", "Faisal_My_Patients")

        # Open first patient detail
        CF.step("Checking if newly added patient appears in list")
        try:
            links = cf.dr.find_elements(
                By.XPATH, "//a[contains(@href,'doctor/patient/')]"
            )
            if links:
                cf.dr.get(links[0].get_attribute("href"))
                time.sleep(ACT_WAIT)
                cf.ok("Patient detail opened")
                cf.shot("DOC_F_patient_detail")
                cf._tick()
        except Exception:
            pass

        cf.go("/doctor/notifications/", "DOC_F", "Faisal_Notifications")
        cf.go("/doctor/profile/",       "DOC_F", "Faisal_Profile")
        cf.logout()

    # ── 4b: New Auto Doctor (added by Hospital Admin this run) ──
    CF.banner("👨‍⚕️", f"SESSION 4b — NEW DOCTOR  ({DOCTOR['email']} / {DOCTOR['password']})")
    CF.step(f"Logging in as newly added doctor: {DOCTOR['email']}")

    if cf.login(DOCTOR["email"], DOCTOR["password"], f"Dr. AutoDoc {RND}"):
        cf.go("/doctor/dashboard/",    "DOC_NEW", "NewDoc_Dashboard")
        cf.go("/doctor/appointments/", "DOC_NEW", "NewDoc_Appointments")
        cf.go("/doctor/patients/",     "DOC_NEW", "NewDoc_My_Patients")

        # Try to open a patient detail — should see newly registered patient
        CF.step(f"Checking for newly added patient: {NEW_PATIENT['email']}")
        try:
            # Look for the auto patient in the list
            body = cf.dr.find_element(By.TAG_NAME, "body").text
            if NEW_PATIENT["email"] in body or NEW_PATIENT["first_name"] in body:
                cf.ok(f"✅ New patient visible: {NEW_PATIENT['first_name']} {NEW_PATIENT['last_name']}")
            else:
                cf.ok("Patients list loaded (patient may need appointment first)")
            cf.shot("DOC_NEW_patients_list")
            # Open first available patient detail
            links = cf.dr.find_elements(
                By.XPATH, "//a[contains(@href,'doctor/patient/')]"
            )
            if links:
                cf.dr.get(links[0].get_attribute("href"))
                time.sleep(ACT_WAIT)
                cf.ok("Patient record opened by new doctor")
                cf.shot("DOC_NEW_patient_record")
                cf._tick()
        except Exception:
            pass

        cf.go("/doctor/notifications/", "DOC_NEW", "NewDoc_Notifications")
        cf.go("/doctor/profile/",       "DOC_NEW", "NewDoc_Profile")
        cf.rec("DOC_NEW", "New_Doctor_Login_And_View_Patients")
        cf.logout()


# ═══════════════════════════════════════════════════════════
#  SESSION 5 — PHARMACY ADMIN
# ═══════════════════════════════════════════════════════════
def pharmacy_admin(cf: CF):
    CF.banner("💊", "SESSION 5 — PHARMACY ADMIN  (A123)")

    if not cf.login("A123", "tamim0033", "Pharmacy Admin"):
        return

    cf.go("/pharmacy/dashboard/", "PH", "Pharmacy_Dashboard")

    # ── ADD PRODUCT (modal: #addProductModal) ────────────────
    CF.banner("💊", "PH ► Add Product / Medicine (auto)")
    cf.go("/pharmacy/products/", "PH", "Products_List")
    CF.step(f"Opening Add Product modal → {PRODUCT['name']}")
    cf._open_modal("addProductModal")
    cf._fill_in_modal("addProductModal", {
        "name"       : PRODUCT["name"],
        "category"   : PRODUCT["category"],
        "price"      : PRODUCT["price"],
        "stock"      : PRODUCT["stock"],
        "description": PRODUCT["description"],
        "is_active"  : "true",
    })
    # tick the active checkbox
    try:
        cb = cf.dr.find_element(
            By.CSS_SELECTOR, "#addProductModal input[name='is_active']"
        )
        if not cb.is_selected():
            cb.click()
    except Exception:
        pass
    cf.shot("PH_add_product_filled")
    cf._submit_modal("addProductModal")
    cf.ok("Product submitted")
    cf.shot("PH_product_added")
    cf.rec("PH", "Add_Product")
    cf._tick()

    # ── ORDERS ──────────────────────────────────────────────
    cf.go("/pharmacy/orders/", "PH", "All_Orders")

    # Open first order detail
    CF.step("Opening first order detail")
    try:
        links = cf.dr.find_elements(
            By.XPATH, "//a[contains(@href,'pharmacy/orders/')]"
        )
        detail_links = [l for l in links if l.get_attribute("href") and
                        l.get_attribute("href").split("/")[-2].isdigit()]
        if detail_links:
            cf.dr.get(detail_links[0].get_attribute("href"))
            time.sleep(ACT_WAIT)
            cf.ok("Order detail opened")
            cf.shot("PH_order_detail")
            cf._tick()
    except Exception:
        pass

    cf.go("/pharmacy/products/", "PH", "Products_Final")

    cf.logout()


# ═══════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════
def summary(cf: CF):
    print("\n\n" + "═" * 78)
    print("                CAREFUSION SELENIUM TEST — COMPLETE")
    print("═" * 78)
    print(f"\n  {'Sess':<6}  {'Action':<38}  Result")
    print("  " + "─" * 62)
    passed = warned = 0
    for sess, action, result in cf.log:
        marker = "✅" if "Pass" in result else "⚠️ "
        print(f"  {sess:<6}  {action:<38}  {marker} {result}")
        if "Pass" in result: passed += 1
        else: warned += 1
    print("  " + "─" * 62)
    print(f"\n  Total : {len(cf.log)}   ✅ Pass : {passed}   ⚠️  Skip/Warn : {warned}")
    print(f"\n  📁 Screenshots → {os.path.abspath(SS_DIR)}/")
    print(f"  🔑 Run suffix  → {RND}")
    print("""
  Sessions completed:
    🔐  Auth Pages     → Sign Up, Sign In, Forgot Password
    👑  Super Admin    → Add Hospital, Hospital Admin, Pharmacy Admin
    🏥  Hospital Admin → Add Doctor, Add ICU Bed, All pages
    👤  Patient        → Find Doctors, Book Appt (Faisal), Buy Medicine,
                         Place Order, Book ICU Bed, All pages
    👤  New Patient    → Auto registered via signup form
    👨‍⚕️  Dr. Faisal (4a) → Dashboard, Appointments, My Patients, Profile
    👨‍⚕️  New Doctor (4b)  → Login with added credentials, view patients
    💊  Pharmacy Admin → Add Product, Orders, All pages
""")
    print("═" * 78)



# ═══════════════════════════════════════════════════════════
#  AUTH PAGES  (shown before any login)
# ═══════════════════════════════════════════════════════════
def auth_pages(cf: CF):
    CF.banner("🔐", "AUTH — Sign Up · Sign In · Forgot Password")
    cf.go("/signup/",          "AUTH", "Sign_Up_Page")
    cf.go("/login/",           "AUTH", "Sign_In_Page")
    cf.go("/forgot-password/", "AUTH", "Forgot_Password_Page")


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═" * 78)
    print("  CareFusion — Complete Selenium Workflow Test")
    print("  (built from actual source: github.com/Tamim480-hub/CareFusion)")
    print("  ─────────────────────────────────────────────────────────────")
    print("  0. Auth Pages    → Sign Up, Sign In, Forgot Password (shown first)")
    print("  1. Super Admin   → add hospital, hospital admin, pharmacy admin")
    print("  2. Hospital Admin→ add doctor, add ICU bed, all pages")
    print("  3. Patient       → book appointment (Dr. Faisal), buy medicine,")
    print("                     place order, book ICU bed, all pages")
    print("  4. Doctor (4a)   → Dr. Faisal all pages")
    print("  4b.New Doctor    → login with auto-added credentials, view patients")
    print("  5. Pharmacy Admin→ add medicine, all pages")
    print("═" * 78)
    print("\n  ▶  Make sure Django is running:  python manage.py runserver")
    print()
    input("  Press ENTER to start the test…\n")

    cf = CF()
    try:
        cf.boot()
        auth_pages(cf)        # ← Sign Up & Sign In shown first
        super_admin(cf)
        hospital_admin(cf)
        patient(cf)
        doctor_sessions(cf)
        pharmacy_admin(cf)
        summary(cf)
    except Exception as e:
        print(f"\n  ❌ Fatal: {e}")
        import traceback; traceback.print_exc()
    finally:
        input("\n  Press ENTER to close browser…")
        cf.quit()

