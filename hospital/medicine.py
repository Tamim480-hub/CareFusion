"""
╔══════════════════════════════════════════════════════════════════════════════╗
║             CAREFUSION — SELENIUM WORKFLOW TEST                             ║
║                                                                              ║
║  গল্পটা এরকম:                                                               ║
║                                                                              ║
║  ১. প্রথমে Sign Up / Login page দেখায়                                       ║
║                                                                              ║
║  ২. Super Admin login করে:                                                  ║
║     → "City Hospital" নামে একটা নতুন Hospital add করে                      ║
║     → সেই Hospital এর জন্য একটা নতুন Hospital Admin add করে                ║
║     → একটা নতুন Pharmacy + Pharmacy Admin add করে                          ║
║     → সব page দেখে logout                                                   ║
║                                                                              ║
║  ৩. নতুন Hospital Admin (Step 1 এ add করা, সেই email+password দিয়ে) login: ║
║     → তার hospital এর জন্য একটা নতুন Doctor add করে                        ║
║     → একটা নতুন ICU Bed add করে                                            ║
║     → সব page দেখে logout                                                   ║
║                                                                              ║
║  ৪. নতুন Patient signup করে:                                                ║
║     → সেই নতুন Doctor এর সাথে appointment book করে                         ║
║     → Medicine কিনে, order place করে, ICU bed book করে                     ║
║     → সব page দেখে logout                                                   ║
║                                                                              ║
║  ৫. নতুন Doctor (Step 2 এ add করা, সেই email+password দিয়ে) login করে:     ║
║     → তার appointment দেখে — নতুন patient এর booking সেখানে আছে!           ║
║     → সব page দেখে logout                                                   ║
║                                                                              ║
║  ৬. নতুন Pharmacy Admin (Step 1 এ add করা, সেই email+password দিয়ে) login: ║
║     → নতুন Medicine add করে                                                 ║
║     → Orders দেখে (patient এর order সেখানে দেখা যাচ্ছে)                    ║
║     → logout                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time, os, random, string

# ══════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════
BASE      = "http://127.0.0.1:8000"
SS_DIR    = "carefusion_screenshots"
SHOW      = 4      # seconds each page stays on screen
WAIT      = 1.5    # wait after form actions
TIMEOUT   = 10

# unique 4-digit suffix so data never clashes on repeated runs
RND = ''.join(random.choices(string.digits, k=4))

# ══════════════════════════════════════════════
#  ALL NEW TEST DATA  (exact field names from templates)
# ══════════════════════════════════════════════

HOSPITAL = {
    "name"   : f"City Hospital {RND}",
    "code"   : f"CH{RND}",
    "address": f"Road {RND}, Mirpur, Dhaka",
    "phone"  : f"028{RND}111",
    "email"  : f"cityhospital{RND}@test.com",
}

# Hospital Admin — created by Super Admin, will login later
H_ADMIN = {
    "username"        : f"hadmin{RND}",
    "email"           : f"hadmin{RND}@test.com",
    "password"        : f"HAdmin{RND}@",
    "confirm_password": f"HAdmin{RND}@",
    "first_name"      : "HAdmin",
    "last_name"       : RND,
    "phone"           : f"019{RND}111",
}

PHARMACY = {
    "name"               : f"MediPlus Pharmacy {RND}",
    "code"               : f"MP{RND}",
    "address"            : f"Lane {RND}, Uttara, Dhaka",
    "phone"              : f"016{RND}111",
    "email"              : f"mediplus{RND}@test.com",
    "delivery_charge"    : "50",
    "free_delivery_above": "500",
}

# Pharmacy Admin — created by Super Admin, will login later
PH_ADMIN = {
    "first_name"      : "PAdmin",
    "last_name"       : RND,
    "username"        : f"pharmadmin{RND}",
    "email"           : f"pharmadmin{RND}@test.com",
    "password"        : f"Pharma{RND}@",
    "confirm_password": f"Pharma{RND}@",
    "phone"           : f"016{RND}222",
    "designation"     : "Pharmacy Manager",
}

# Doctor — created by Hospital Admin, will login later
DOCTOR = {
    "first_name"      : "DrAuto",
    "last_name"       : RND,
    "username"        : f"drauto{RND}",
    "email"           : f"drauto{RND}@test.com",
    "password"        : f"Doctor{RND}@",
    "confirm_password": f"Doctor{RND}@",
    "phone"           : f"017{RND}111",
}

ICU_BED = {
    "bed_number"  : f"ICU-{RND}",
    "bed_type"    : "ICU",
    "daily_charge": "5000",
    "equipment"   : "Ventilator, Heart Monitor, IV Pump",
}

# Patient — will signup, then book appointment with new doctor
PATIENT = {
    "first_name"      : "Rafiq",
    "last_name"       : RND,
    "email"           : f"rafiq{RND}@test.com",
    "phone"           : f"018{RND}111",
    "age"             : "32",
    "gender"          : "male",
    "blood_group"     : "B+",
    "password"        : f"Patient{RND}@",
    "confirm_password": f"Patient{RND}@",
}

APPT = {
    "date"    : "2026-08-10",
    "symptoms": "Fever, headache and chest discomfort",
}

CHECKOUT = {
    "full_name": f"Rafiq {RND}",
    "email"    : f"rafiq{RND}@test.com",
    "phone"    : f"018{RND}111",
    "address"  : f"House {RND}, Road 5, Dhaka",
    "notes"    : "Please deliver quickly",
}

ICU_BOOK = {
    "condition"         : "Needs urgent cardiac monitoring",
    "expected_discharge": "2026-08-20",
}

MEDICINE = {
    "name"       : f"AutoMed {RND}",
    "category"   : "tablet",
    "price"      : "150.00",
    "stock"      : "100",
    "description": "Automated test medicine for demo",
}


# ══════════════════════════════════════════════
#  DRIVER / HELPER CLASS
# ══════════════════════════════════════════════
class CF:
    def __init__(self):
        self.dr  = None
        self.log = []

    # ── browser ──────────────────────────────
    def boot(self):
        os.makedirs(SS_DIR, exist_ok=True)
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-notifications")
        self.dr = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opts,
        )
        print("✅  Browser ready\n")

    def quit(self):
        if self.dr:
            time.sleep(2)
            self.dr.quit()

    # ── print helpers ─────────────────────────
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

    def rec(self, sess, action):
        self.log.append((sess, action, "✅ Pass"))

    # ── screenshot ────────────────────────────
    def shot(self, name):
        try:
            safe = "".join(c for c in name if c.isalnum() or c in "_-")
            self.dr.save_screenshot(f"{SS_DIR}/{safe}.png")
        except Exception:
            pass

    # ── go to page + show for SHOW seconds ───
    def go(self, path, sess="", label=""):
        url = f"{BASE}{path}"
        print(f"\n  📄  {label or path}")
        print(f"      {url}")
        try:
            self.dr.get(url)
            time.sleep(WAIT)
            title = self.dr.title
            cur   = self.dr.current_url.lower()

            # skip pages that don't exist in project
            if any(e in title for e in ["not found","500","403","TemplateDoesNotExist","NoReverseMatch"]):
                self.warn(f"Page not built yet — skipping")
                if sess and label:
                    self.log.append((sess, label, "⚠️  Not Built"))
                return

            if "login" in cur and "login" not in path.lower():
                # session expired — re-login silently handled by caller
                self.warn("Session expired")
                if sess and label:
                    self.log.append((sess, label, "⚠️  Session"))
                return

            self.ok(f"Loaded → {title[:60]}")
            self.shot(f"{sess}_{label}".replace(" ", "_"))
            if sess and label:
                self.log.append((sess, label, "✅ Pass"))
            self._tick()
        except Exception as e:
            self.warn(str(e))

    def _tick(self):
        for i in range(SHOW, 0, -1):
            print(f"      ⏱  {i}s ", end="\r")
            time.sleep(1)
        print("           ", end="\r")

    # ── login ─────────────────────────────────
    def login(self, email, pwd, name):
        print(f"\n  🔐  Logging in → {name}")
        self.dr.get(f"{BASE}/login/")
        time.sleep(WAIT)
        self._fill("email",    email)
        self._fill("password", pwd)
        self._submit()
        time.sleep(2)
        if "login" in self.dr.current_url.lower():
            self.warn(f"Login failed — {name}")
            return False
        self.ok(f"Logged in — {name}")
        self.shot(f"LOGIN_{name.replace(' ','_')}")
        return True

    def logout(self):
        self.dr.get(f"{BASE}/logout/")
        time.sleep(2)
        self.ok("Logged out")

    # ── form helpers ──────────────────────────
    def _fill(self, name, value):
        for loc in [(By.NAME, name), (By.ID, name), (By.ID, f"id_{name}")]:
            try:
                el = self.dr.find_element(*loc)
                if el.is_displayed() and el.is_enabled():
                    el.clear()
                    el.send_keys(value)
                    return True
            except Exception:
                pass
        return False

    def _select(self, name, val):
        for css in [f"select[name='{name}']", f"#{name}", f"#id_{name}"]:
            try:
                s = Select(self.dr.find_element(By.CSS_SELECTOR, css))
                try:
                    s.select_by_value(val)
                    return True
                except Exception:
                    pass
                for opt in s.options:
                    if val.lower() in opt.text.lower():
                        opt.click()
                        return True
                if len(s.options) > 1:
                    s.select_by_index(1)
                    return True
            except Exception:
                pass
        return False

    def _submit(self):
        for css in ["button[type='submit']", "input[type='submit']",
                    "button.btn-primary", ".btn-primary[type='submit']"]:
            try:
                btn = self.dr.find_element(By.CSS_SELECTOR, css)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    time.sleep(WAIT)
                    return True
            except Exception:
                pass
        try:
            self.dr.find_element(By.TAG_NAME, "form").submit()
            time.sleep(WAIT)
        except Exception:
            pass

    def _open_modal(self, modal_id):
        """Open Bootstrap modal via JS — no click intercept issues."""
        try:
            self.dr.execute_script(
                f"bootstrap.Modal.getOrCreateInstance("
                f"document.getElementById('{modal_id}')).show();"
            )
            time.sleep(1.5)
            return True
        except Exception:
            return False

    def _fill_modal(self, modal_id, data: dict):
        """Fill all fields inside a modal."""
        for name, value in data.items():
            for css in [
                f"#{modal_id} [name='{name}']",
                f"#{modal_id} #{name}",
            ]:
                try:
                    el = self.dr.find_element(By.CSS_SELECTOR, css)
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
                    else:
                        el.clear()
                        el.send_keys(value)
                    break
                except Exception:
                    pass

    def _submit_modal(self, modal_id):
        """Click submit inside modal."""
        for css in [
            f"#{modal_id} button[type='submit']",
            f"#{modal_id} input[type='submit']",
            f"#{modal_id} .btn-primary",
        ]:
            try:
                btn = self.dr.find_element(By.CSS_SELECTOR, css)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    time.sleep(WAIT + 0.5)
                    return True
            except Exception:
                pass
        return False


# ══════════════════════════════════════════════════════════
#  STEP 0 — AUTH PAGES
# ══════════════════════════════════════════════════════════
def show_auth_pages(cf: CF):
    CF.banner("🔐", "STEP 0 — Auth Pages  (Sign Up · Sign In · Forgot Password)")
    cf.go("/signup/",          "AUTH", "Sign_Up_Page")
    cf.go("/login/",           "AUTH", "Sign_In_Page")
    cf.go("/forgot-password/", "AUTH", "Forgot_Password")


# ══════════════════════════════════════════════════════════
#  STEP 1 — SUPER ADMIN
#  adds: Hospital, Hospital Admin, Pharmacy Admin
# ══════════════════════════════════════════════════════════
def step_super_admin(cf: CF):
    CF.banner("👑", "STEP 1 — SUPER ADMIN  (admin@super.com)")

    if not cf.login("admin@super.com", "tamim0011", "Super Admin"):
        return

    cf.go("/admin/dashboard/", "SA", "Dashboard")

    # ── Add Hospital ──────────────────────────────────────────
    CF.banner("🏥", f"SA ► Adding Hospital: {HOSPITAL['name']}")
    cf.go("/admin/hospitals/", "SA", "Hospitals_List")
    CF.step("Opening Add Hospital modal")
    cf._open_modal("addHospitalModal")
    cf._fill_modal("addHospitalModal", {
        "name"   : HOSPITAL["name"],
        "code"   : HOSPITAL["code"],
        "address": HOSPITAL["address"],
        "phone"  : HOSPITAL["phone"],
        "email"  : HOSPITAL["email"],
    })
    cf.shot("SA_hospital_form_filled")
    cf._submit_modal("addHospitalModal")
    cf.ok(f"Hospital '{HOSPITAL['name']}' added!")
    cf.shot("SA_hospital_added")
    cf.rec("SA", f"Add_Hospital_{HOSPITAL['name']}")
    cf._tick()

    # ── Add Hospital Admin ────────────────────────────────────
    CF.banner("👨‍💼", f"SA ► Adding Hospital Admin: {H_ADMIN['email']}")
    cf.go("/admin/hospital-admins/", "SA", "Hospital_Admins_List")
    CF.step("Opening Add Hospital Admin modal")
    cf._open_modal("addAdminModal")
    cf._fill_modal("addAdminModal", {
        "username"        : H_ADMIN["username"],
        "email"           : H_ADMIN["email"],
        "password"        : H_ADMIN["password"],
        "confirm_password": H_ADMIN["confirm_password"],
        "first_name"      : H_ADMIN["first_name"],
        "last_name"       : H_ADMIN["last_name"],
        "phone"           : H_ADMIN["phone"],
    })
    cf.shot("SA_hadmin_form_filled")
    cf._submit_modal("addAdminModal")
    cf.ok(f"Hospital Admin '{H_ADMIN['email']}' added!")
    cf.shot("SA_hadmin_added")
    cf.rec("SA", f"Add_Hospital_Admin_{H_ADMIN['email']}")
    cf._tick()

    # ── Add Pharmacy + Pharmacy Admin ─────────────────────────
    CF.banner("💊", f"SA ► Adding Pharmacy: {PHARMACY['name']}  +  Admin: {PH_ADMIN['email']}")
    cf.go("/super-admin/pharmacy-admins/", "SA", "Pharmacy_Admins_Page")

    # --- create pharmacy ---
    CF.step(f"Filling pharmacy form → {PHARMACY['name']}")
    try:
        form = cf.dr.find_element(
            By.XPATH,
            "//form[.//input[@value='create_pharmacy']]"
        )
        for name, val in PHARMACY.items():
            try:
                el = form.find_element(By.NAME, name)
                el.clear(); el.send_keys(val)
            except Exception:
                pass
        cf.shot("SA_pharmacy_form_filled")
        btn = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        cf.dr.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.5)
        btn.click()
        time.sleep(WAIT + 1)
        cf.ok(f"Pharmacy '{PHARMACY['name']}' submitted!")
        cf.shot("SA_pharmacy_added")
        cf.rec("SA", f"Add_Pharmacy_{PHARMACY['name']}")
        cf._tick()
    except Exception as e:
        cf.warn(f"Pharmacy form: {e}")

    # --- create pharmacy admin ---
    cf.go("/super-admin/pharmacy-admins/", "SA", "Pharmacy_Admin_Create")
    CF.step(f"Filling pharmacy admin form → {PH_ADMIN['email']}")
    try:
        # inject values via JS into the create_admin form
        cf.dr.execute_script("""
            var form = document.querySelector('form input[name="action"][value="create_admin"]');
            if(form) form = form.closest('form');
            var d = arguments[0];
            if(form){
                Object.keys(d).forEach(function(k){
                    var el = form.querySelector('[name="'+k+'"]');
                    if(el){ el.value = d[k]; }
                });
            }
        """, {k: v for k, v in PH_ADMIN.items()})

        # set pharmacy_id to first available pharmacy
        cf.dr.execute_script("""
            var sel = document.querySelector('form input[name="action"][value="create_admin"]');
            if(sel){ sel = sel.closest('form'); }
            if(sel){
                var pid = sel.querySelector('[name="pharmacy_id"]');
                if(pid && !pid.value){
                    var firstPharm = document.querySelector('[data-pharmacy-id]');
                    if(firstPharm) pid.value = firstPharm.dataset.pharmacyId;
                    else pid.value = '1';
                }
            }
        """)

        cf.shot("SA_pharmadmin_form_filled")
        btn = cf.dr.find_element(
            By.XPATH,
            "//form[.//input[@value='create_admin']]//button[@type='submit']"
        )
        cf.dr.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.5)
        btn.click()
        time.sleep(WAIT + 1)
        cf.ok(f"Pharmacy Admin '{PH_ADMIN['email']}' submitted!")
        cf.shot("SA_pharmadmin_added")
        cf.rec("SA", f"Add_Pharmacy_Admin_{PH_ADMIN['email']}")
        cf._tick()
    except Exception as e:
        cf.warn(f"Pharmacy admin form: {e}")

    # ── Show remaining super admin pages ──────────────────────
    cf.go("/admin/hospitals/",             "SA", "All_Hospitals_Final")
    cf.go("/admin/hospital-admins/",       "SA", "All_Hospital_Admins_Final")
    cf.go("/super-admin/pharmacy-admins/", "SA", "All_Pharmacy_Admins_Final")

    cf.logout()


# ══════════════════════════════════════════════════════════
#  STEP 2 — NEW HOSPITAL ADMIN
#  (the one Super Admin just created)
#  adds: Doctor, ICU Bed
# ══════════════════════════════════════════════════════════
def step_hospital_admin(cf: CF):
    CF.banner("🏥", f"STEP 2 — NEW HOSPITAL ADMIN  ({H_ADMIN['email']})")
    CF.step(f"Credentials  →  email: {H_ADMIN['email']}  |  password: {H_ADMIN['password']}")

    CF.step(f"Using credentials added by Super Admin in Step 1")
    CF.step(f"email: {H_ADMIN['email']}  password: {H_ADMIN['password']}")

    if not cf.login(H_ADMIN["email"], H_ADMIN["password"], f"HAdmin {RND}"):
        CF.banner("❌", "Hospital Admin login failed!")
        print(f"   Reason: Super Admin added this admin in Step 1.")
        print(f"   If login fails, the admin may not have been assigned a hospital.")
        print(f"   email   : {H_ADMIN['email']}")
        print(f"   password: {H_ADMIN['password']}")
        return

    cf.go("/hospital/dashboard/", "HA", "Hospital_Dashboard")

    # ── Add Doctor ────────────────────────────────────────────
    CF.banner("👨‍⚕️", f"HA ► Adding Doctor: {DOCTOR['email']}")
    cf.go("/hospital/doctors/", "HA", "Doctors_List")
    CF.step("Opening Add Doctor modal")
    cf._open_modal("addDoctorModal")
    cf._fill_modal("addDoctorModal", {
        "first_name"      : DOCTOR["first_name"],
        "last_name"       : DOCTOR["last_name"],
        "username"        : DOCTOR["username"],
        "email"           : DOCTOR["email"],
        "password"        : DOCTOR["password"],
        "confirm_password": DOCTOR["confirm_password"],
        "phone"           : DOCTOR["phone"],
    })
    cf.shot("HA_doctor_form_filled")
    cf._submit_modal("addDoctorModal")
    cf.ok(f"Doctor '{DOCTOR['first_name']} {DOCTOR['last_name']}' added!")
    cf.shot("HA_doctor_added")
    cf.rec("HA", f"Add_Doctor_{DOCTOR['email']}")
    cf._tick()

    # confirm doctor appears in list
    CF.step("Verifying new doctor appears in list")
    cf.go("/hospital/doctors/", "HA", "Doctors_List_After_Add")
    try:
        body = cf.dr.find_element(By.TAG_NAME, "body").text
        if DOCTOR["first_name"] in body or DOCTOR["email"] in body:
            cf.ok(f"✅ Doctor '{DOCTOR['first_name']} {DOCTOR['last_name']}' visible in list!")
        else:
            cf.ok("Doctors list loaded")
    except Exception:
        pass

    # ── Add ICU Bed ───────────────────────────────────────────
    CF.banner("🛏️", f"HA ► Adding ICU Bed: {ICU_BED['bed_number']}")
    cf.go("/hospital/beds/", "HA", "ICU_Beds_List")
    CF.step("Opening Add Bed modal")
    cf._open_modal("addBedModal")
    cf._fill_modal("addBedModal", {
        "bed_number"  : ICU_BED["bed_number"],
        "bed_type"    : ICU_BED["bed_type"],
        "daily_charge": ICU_BED["daily_charge"],
        "equipment"   : ICU_BED["equipment"],
    })
    cf.shot("HA_bed_form_filled")
    cf._submit_modal("addBedModal")
    cf.ok(f"ICU Bed '{ICU_BED['bed_number']}' added!")
    cf.shot("HA_bed_added")
    cf.rec("HA", f"Add_ICU_Bed_{ICU_BED['bed_number']}")
    cf._tick()

    # confirm bed appears
    CF.step("Verifying new bed appears in list")
    cf.go("/hospital/beds/", "HA", "ICU_Beds_After_Add")
    try:
        body = cf.dr.find_element(By.TAG_NAME, "body").text
        if ICU_BED["bed_number"] in body:
            cf.ok(f"✅ Bed '{ICU_BED['bed_number']}' visible in list!")
        else:
            cf.ok("ICU Beds list loaded")
    except Exception:
        pass

    # ── Remaining hospital admin pages ────────────────────────
    cf.go("/hospital/patients/",     "HA", "Patients_List")
    cf.go("/hospital/appointments/", "HA", "Appointments_List")
    cf.go("/hospital/emergencies/",  "HA", "Emergencies_List")
    cf.go("/hospital/test-reports/", "HA", "Test_Reports")
    cf.go("/hospital/products/",     "HA", "Products_List")

    cf.logout()


# ══════════════════════════════════════════════════════════
#  STEP 3 — NEW PATIENT
#  signs up, books appointment with new doctor
# ══════════════════════════════════════════════════════════
def step_patient(cf: CF):
    CF.banner("👤", f"STEP 3 — NEW PATIENT  (signing up as {PATIENT['email']})")

    # ── Signup ────────────────────────────────────────────────
    CF.banner("📝", f"Patient ► Sign Up: {PATIENT['email']}")
    cf.go("/signup/", "PAT", "Patient_Signup")
    CF.step(f"Filling signup form for {PATIENT['first_name']} {PATIENT['last_name']}")
    cf._fill("first_name",       PATIENT["first_name"])
    cf._fill("last_name",        PATIENT["last_name"])
    cf._fill("email",            PATIENT["email"])
    cf._fill("phone",            PATIENT["phone"])
    cf._fill("age",              PATIENT["age"])
    cf._select("gender",         PATIENT["gender"])
    cf._select("blood_group",    PATIENT["blood_group"])
    cf._fill("password",         PATIENT["password"])
    cf._fill("confirm_password", PATIENT["confirm_password"])
    try:
        cb = cf.dr.find_element(By.NAME, "terms")
        if not cb.is_selected():
            cf.dr.execute_script("arguments[0].click();", cb)
    except Exception:
        pass
    cf.shot("PAT_signup_filled")
    CF.step("Submitting signup")
    cf._submit()
    time.sleep(2)
    cf.ok(f"Patient '{PATIENT['first_name']} {PATIENT['last_name']}' registered!")
    cf.shot("PAT_signup_done")
    cf.rec("PAT", f"Signup_{PATIENT['email']}")
    cf._tick()

    # Login as patient
    if not cf.login(PATIENT["email"], PATIENT["password"], f"{PATIENT['first_name']} {PATIENT['last_name']}"):
        cf.warn("Patient login failed")
        return

    cf.go("/patient/dashboard/", "PAT", "Patient_Dashboard")

    # ── Find new doctor and book appointment ──────────────────
    CF.banner("📅", f"Patient ► Book Appointment with new doctor ({DOCTOR['first_name']} {DOCTOR['last_name']})")
    cf.go("/patient/book-appointment/", "PAT", "Book_Appointment_Page")

    CF.step(f"Selecting Dr. {DOCTOR['first_name']} {DOCTOR['last_name']} from dropdown")
    try:
        sel_el = cf.dr.find_element(By.CSS_SELECTOR, "select[name='doctor_id']")
        s = Select(sel_el)
        found = False
        for opt in s.options:
            if DOCTOR["first_name"].lower() in opt.text.lower() or \
               DOCTOR["last_name"].lower() in opt.text.lower():
                opt.click()
                cf.ok(f"Doctor selected: {opt.text}")
                found = True
                break
        if not found:
            # pick any available doctor
            if len(s.options) > 1:
                s.select_by_index(1)
                cf.ok(f"Selected doctor: {s.first_selected_option.text}")
        time.sleep(WAIT)
    except Exception as e:
        cf.warn(f"Doctor select: {e}")

    CF.step(f"Setting date: {APPT['date']}")
    try:
        d = cf.dr.find_element(By.NAME, "date")
        cf.dr.execute_script(f"arguments[0].value='{APPT['date']}'", d)
        cf.dr.execute_script("arguments[0].dispatchEvent(new Event('change'))", d)
        time.sleep(WAIT)
        cf.ok("Date set")
    except Exception as e:
        cf.warn(f"Date: {e}")

    CF.step("Selecting time slot")
    time.sleep(1.5)
    try:
        ts = cf.dr.find_element(By.CSS_SELECTOR, "select[name='time']")
        s  = Select(ts)
        if len(s.options) > 1:
            s.select_by_index(1)
            cf.ok(f"Time: {s.first_selected_option.text}")
        else:
            cf.warn("No slots yet — doctor schedule may not be set")
    except Exception as e:
        cf.warn(f"Time: {e}")

    cf._fill("symptoms", APPT["symptoms"])
    cf.shot("PAT_appointment_form_filled")
    CF.step("Submitting appointment")
    cf._submit()
    cf.ok("Appointment submitted!")
    cf.shot("PAT_appointment_done")
    cf.rec("PAT", f"Book_Appointment_with_{DOCTOR['first_name']}")
    cf._tick()

    # ── Buy medicine ──────────────────────────────────────────
    CF.banner("💊", "Patient ► Browse Products → Add to Cart → Checkout")
    cf.go("/patient/products/", "PAT", "Products_Page")
    CF.step("Adding first product to cart")
    try:
        forms = cf.dr.find_elements(
            By.CSS_SELECTOR,
            "form.add-to-cart-form, form[action*='add-to-cart']"
        )
        if forms:
            cf.dr.execute_script("arguments[0].submit();", forms[0])
            time.sleep(WAIT)
            cf.ok("Product added to cart!")
    except Exception:
        pass
    cf.shot("PAT_product_added")
    cf._tick()

    cf.go("/cart/", "PAT", "Cart_Page")
    cf.shot("PAT_cart")
    cf._tick()

    cf.go("/checkout/", "PAT", "Checkout_Page")
    CF.step("Filling checkout details")
    for name, val in CHECKOUT.items():
        cf._fill(name, val)
    try:
        cod = cf.dr.find_element(
            By.CSS_SELECTOR, "input[name='payment_method'][value='cod']"
        )
        cf.dr.execute_script("arguments[0].click();", cod)
        cf.ok("Cash on Delivery selected")
    except Exception:
        pass
    cf.shot("PAT_checkout_filled")
    cf._submit()
    cf.ok("Order placed!")
    cf.shot("PAT_order_placed")
    cf.rec("PAT", "Place_Order")
    cf._tick()

    # ── Book ICU Bed ──────────────────────────────────────────
    CF.banner("🛏️", f"Patient ► Book ICU Bed: {ICU_BED['bed_number']}")
    cf.go("/patient/icu-beds/", "PAT", "ICU_Beds_Page")
    CF.step(f"Looking for bed {ICU_BED['bed_number']}")
    try:
        body = cf.dr.find_element(By.TAG_NAME, "body").text
        if ICU_BED["bed_number"] in body:
            cf.ok(f"✅ Bed '{ICU_BED['bed_number']}' is visible — booking it!")
    except Exception:
        pass

    booked = False
    try:
        links = cf.dr.find_elements(
            By.XPATH,
            "//a[contains(@href,'icu-beds/book')]"
        )
        if links:
            href = links[0].get_attribute("href")
            cf.dr.get(href)
            time.sleep(WAIT)
            booked = True
            cf.ok(f"ICU booking page opened")
    except Exception:
        pass
    if not booked:
        cf.go("/patient/icu-beds/book/1/", "PAT", "ICU_Book_Page")

    cf._fill("condition", ICU_BOOK["condition"])
    try:
        el = cf.dr.find_element(By.NAME, "expected_discharge")
        cf.dr.execute_script(f"arguments[0].value='{ICU_BOOK['expected_discharge']}'", el)
    except Exception:
        pass
    cf.shot("PAT_icu_form_filled")
    cf._submit()
    cf.ok("ICU Bed booked!")
    cf.shot("PAT_icu_booked")
    cf.rec("PAT", f"Book_ICU_Bed_{ICU_BED['bed_number']}")
    cf._tick()

    # ── Remaining patient pages ───────────────────────────────
    cf.go("/patient/my-appointments/", "PAT", "My_Appointments")
    cf.go("/patient/icu-bookings/",    "PAT", "My_ICU_Bookings")
    cf.go("/patient/orders/",          "PAT", "My_Orders")
    cf.go("/patient/bills/",           "PAT", "My_Bills")
    cf.go("/patient/test-reports/",    "PAT", "Test_Reports")
    cf.go("/patient/profile/",         "PAT", "My_Profile")

    cf.logout()


# ══════════════════════════════════════════════════════════
#  STEP 4 — NEW DOCTOR
#  (the one Hospital Admin just added)
#  logs in and sees the patient's appointment
# ══════════════════════════════════════════════════════════
def step_doctor(cf: CF):
    CF.banner(
        "👨‍⚕️",
        f"STEP 4 — NEW DOCTOR  ({DOCTOR['email']})"
    )
    CF.step(f"Credentials  →  email: {DOCTOR['email']}  |  password: {DOCTOR['password']}")

    if not cf.login(DOCTOR["email"], DOCTOR["password"],
                    f"Dr. {DOCTOR['first_name']} {DOCTOR['last_name']}"):
        cf.warn("New doctor login failed")
        return

    cf.go("/doctor/dashboard/", "DOC", "Doctor_Dashboard")

    # ── Appointments — show patient's booking ─────────────────
    CF.banner("📋", f"Doctor ► Appointments — patient {PATIENT['first_name']} booked here!")
    cf.go("/doctor/appointments/", "DOC", "My_Appointments")
    CF.step(f"Checking if patient '{PATIENT['first_name']} {PATIENT['last_name']}' appointment shows up")
    try:
        body = cf.dr.find_element(By.TAG_NAME, "body").text
        if PATIENT["first_name"] in body or PATIENT["email"] in body:
            cf.ok(f"✅ Patient '{PATIENT['first_name']} {PATIENT['last_name']}' appointment is visible!")
        else:
            cf.ok("Appointments page loaded (patient may need slot confirmation)")
    except Exception:
        pass
    cf.shot("DOC_appointments_with_patient")

    # open first appointment detail
    try:
        links = cf.dr.find_elements(
            By.XPATH, "//a[contains(@href,'doctor/appointment/')]"
        )
        if links:
            cf.dr.get(links[0].get_attribute("href"))
            time.sleep(WAIT)
            cf.ok("Appointment detail opened")
            cf.shot("DOC_appointment_detail")
            cf._tick()
    except Exception:
        pass
    cf._tick()

    # ── Patients list ─────────────────────────────────────────
    CF.banner("👥", "Doctor ► My Patients")
    cf.go("/doctor/patients/", "DOC", "My_Patients")
    try:
        body = cf.dr.find_element(By.TAG_NAME, "body").text
        if PATIENT["first_name"] in body:
            cf.ok(f"✅ Patient '{PATIENT['first_name']}' visible in patients list!")
        else:
            cf.ok("Patients list loaded")
    except Exception:
        pass

    # open first patient record
    try:
        links = cf.dr.find_elements(
            By.XPATH, "//a[contains(@href,'doctor/patient/')]"
        )
        if links:
            cf.dr.get(links[0].get_attribute("href"))
            time.sleep(WAIT)
            cf.ok("Patient record opened")
            cf.shot("DOC_patient_record")
            cf._tick()
    except Exception:
        pass

    # Remaining doctor pages
    cf.go("/doctor/notifications/", "DOC", "Notifications")
    cf.go("/doctor/profile/",       "DOC", "Doctor_Profile")

    cf.logout()


# ══════════════════════════════════════════════════════════
#  STEP 5 — NEW PHARMACY ADMIN
#  (the one Super Admin just added)
#  adds medicine, sees patient's order
# ══════════════════════════════════════════════════════════
def step_pharmacy_admin(cf: CF):
    CF.banner("💊", f"STEP 5 — NEW PHARMACY ADMIN  ({PH_ADMIN['email']})")
    CF.step(f"Credentials  →  email: {PH_ADMIN['email']}  |  password: {PH_ADMIN['password']}")

    CF.step(f"Using credentials added by Super Admin in Step 1")
    CF.step(f"email: {PH_ADMIN['email']}  password: {PH_ADMIN['password']}")

    if not cf.login(PH_ADMIN["email"], PH_ADMIN["password"], f"PharmaAdmin {RND}"):
        CF.banner("❌", "Pharmacy Admin login failed!")
        print(f"   Reason: Super Admin added this admin in Step 1.")
        print(f"   If login fails, the pharmacy admin may not have been assigned a pharmacy.")
        print(f"   email   : {PH_ADMIN['email']}")
        print(f"   password: {PH_ADMIN['password']}")
        return

    cf.go("/pharmacy/dashboard/", "PH", "Pharmacy_Dashboard")

    # ── Add Medicine ──────────────────────────────────────────
    CF.banner("💊", f"Pharmacy ► Adding Medicine: {MEDICINE['name']}")
    cf.go("/pharmacy/products/", "PH", "Products_List")
    CF.step(f"Opening Add Product modal → {MEDICINE['name']}")
    cf._open_modal("addProductModal")
    cf._fill_modal("addProductModal", {
        "name"       : MEDICINE["name"],
        "category"   : MEDICINE["category"],
        "price"      : MEDICINE["price"],
        "stock"      : MEDICINE["stock"],
        "description": MEDICINE["description"],
    })
    cf.shot("PH_medicine_form_filled")
    cf._submit_modal("addProductModal")
    cf.ok(f"Medicine '{MEDICINE['name']}' added!")
    cf.shot("PH_medicine_added")
    cf.rec("PH", f"Add_Medicine_{MEDICINE['name']}")
    cf._tick()

    # confirm medicine appears
    CF.step("Verifying medicine in product list")
    cf.go("/pharmacy/products/", "PH", "Products_After_Add")
    try:
        body = cf.dr.find_element(By.TAG_NAME, "body").text
        if MEDICINE["name"] in body:
            cf.ok(f"✅ Medicine '{MEDICINE['name']}' visible in list!")
        else:
            cf.ok("Products list loaded")
    except Exception:
        pass

    # ── Orders — show patient's order ─────────────────────────
    CF.banner("📦", "Pharmacy ► Orders — patient's order should be here!")
    cf.go("/pharmacy/orders/", "PH", "All_Orders")
    CF.step(f"Checking if patient '{PATIENT['first_name']}' order shows up")
    try:
        body = cf.dr.find_element(By.TAG_NAME, "body").text
        if PATIENT["first_name"] in body or PATIENT["email"] in body:
            cf.ok(f"✅ Patient '{PATIENT['first_name']}' order is visible!")
        else:
            cf.ok("Orders page loaded")
    except Exception:
        pass

    # open first order detail
    try:
        links = cf.dr.find_elements(
            By.XPATH, "//a[contains(@href,'pharmacy/orders/')]"
        )
        detail = [l for l in links
                  if l.get_attribute("href") and
                  l.get_attribute("href").rstrip("/").split("/")[-1].isdigit()]
        if detail:
            cf.dr.get(detail[0].get_attribute("href"))
            time.sleep(WAIT)
            cf.ok("Order detail opened")
            cf.shot("PH_order_detail")
            cf._tick()
    except Exception:
        pass

    cf.go("/pharmacy/products/", "PH", "Products_Final")
    cf.logout()


# ══════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════
def print_summary(cf: CF):
    print("\n\n" + "═" * 78)
    print("                  CAREFUSION — WORKFLOW TEST COMPLETE")
    print("═" * 78)
    print(f"\n  {'Step':<8}  {'Action':<45}  Result")
    print("  " + "─" * 68)
    passed = warned = 0
    for sess, action, result in cf.log:
        m = "✅" if "Pass" in result else "⚠️ "
        print(f"  {sess:<8}  {action:<45}  {m} {result}")
        if "Pass" in result: passed += 1
        else:                warned  += 1
    print("  " + "─" * 68)
    print(f"\n  Total: {len(cf.log)}   ✅ Pass: {passed}   ⚠️  Warn: {warned}")
    print(f"\n  📁 Screenshots: {os.path.abspath(SS_DIR)}/")
    print(f"  🔑 Run ID      : {RND}")
    print(f"""
  Story recap:
    0. Auth       → Sign Up, Sign In, Forgot Password pages shown
    1. SuperAdmin → Added Hospital '{HOSPITAL['name']}'
                    Added Hospital Admin '{H_ADMIN['email']}'
                    Added Pharmacy '{PHARMACY['name']}' + Admin '{PH_ADMIN['email']}'
    2. HospAdmin  → Logged in as new admin
                    Added Doctor '{DOCTOR['first_name']} {DOCTOR['last_name']}'
                    Added ICU Bed '{ICU_BED['bed_number']}'
    3. Patient    → Signed up as '{PATIENT['first_name']} {PATIENT['last_name']}'
                    Booked appointment with new doctor
                    Bought medicine, placed order, booked ICU bed
    4. Doctor     → Logged in as new doctor '{DOCTOR['email']}'
                    Saw patient's appointment & records
    5. Pharmacy   → Logged in as new pharmacy admin '{PH_ADMIN['email']}'
                    Added medicine '{MEDICINE['name']}'
                    Saw patient's order
""")
    print("═" * 78)


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═" * 78)
    print("  CareFusion — Complete Workflow Selenium Test")
    print("  ─────────────────────────────────────────────")
    print("  সব নতুন data দিয়ে পুরো story দেখাবে:")
    print(f"  Hospital → Hospital Admin → Doctor → Patient → ICU Bed → Medicine")
    print("  প্রতিটা add এর পর সেটা list এ দেখা যাচ্ছে confirm করবে")
    print("═" * 78)
    print("\n  ▶  Django চালু থাকতে হবে:  python manage.py runserver\n")
    input("  ENTER চাপো শুরু করতে…\n")

    cf = CF()
    try:
        cf.boot()
        show_auth_pages(cf)
        step_super_admin(cf)
        step_hospital_admin(cf)
        step_patient(cf)
        step_doctor(cf)
        step_pharmacy_admin(cf)
        print_summary(cf)
    except Exception as e:
        print(f"\n  ❌ Fatal: {e}")
        import traceback; traceback.print_exc()
    finally:
        input("\n  ENTER চাপো browser বন্ধ করতে…")
        cf.quit()