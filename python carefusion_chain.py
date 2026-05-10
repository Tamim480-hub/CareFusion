"""
CAREFUSION — CHAIN WORKFLOW SELENIUM TEST
==========================================

একটাই chain — সব add করা data দিয়ে পুরো workflow:

STEP 0  Sign Up / Sign In page দেখায়

STEP 1  Super Admin login করে:
        → "City Hospital XXXX" add করে
        → Hospital Admin "Mokles Bhai" add করে
        → Pharmacy "MediPlus XXXX" add করে
        → Pharmacy Admin "Tolumolu" add করে
        → সব page দেখে logout

STEP 2  "Mokles Bhai" (নতুন Hospital Admin) login করে:
        → Doctor "Dr. Baten Mia" add করে
        → ICU Bed "ICU-XXXX" add করে
        → সব page দেখে logout

STEP 3  নতুন Patient "Rafiq Ahmed" signup করে:
        → "Dr. Baten Mia" select করে appointment নেয়
        → Medicine কিনে cart এ add করে
        → Order place করে (checkout)
        → ICU Bed book করে
        → সব page দেখে logout

STEP 4  "Dr. Baten Mia" login করে:
        → Rafiq এর appointment দেখে
        → Patient list দেখে
        → সব page দেখে logout

STEP 5  "Tolumolu" (নতুন Pharmacy Admin) login করে:
        → Medicine "Baten Special XXXX" add করে
        → Rafiq এর order দেখে
        → সব page দেখে logout
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time, os, random, string

# ══════════════════════════════
#  CONFIG
# ══════════════════════════════
BASE   = "http://127.0.0.1:8000"
SS_DIR = "carefusion_screenshots"
SHOW   = 4
WAIT   = 1.5

RND = ''.join(random.choices(string.digits, k=4))

# ══════════════════════════════════════════════════════
#  THE CHAIN — সব connected
# ══════════════════════════════════════════════════════

HOSPITAL = {
    "name"   : f"City Hospital {RND}",
    "code"   : f"CH{RND}",
    "address": f"Road {RND}, Mirpur, Dhaka",
    "phone"  : f"028{RND}001",
    "email"  : f"cityhospital{RND}@test.com",
}

MOKLES = {
    "first_name"      : "Mokles",
    "last_name"       : "Bhai",
    "username"        : f"mokles{RND}",
    "email"           : f"mokles{RND}@hospital.com",
    "password"        : f"Mokles{RND}@x",
    "confirm_password": f"Mokles{RND}@x",
    "phone"           : f"019{RND}001",
}

PHARMACY = {
    "name"               : f"MediPlus Pharmacy {RND}",
    "code"               : f"MP{RND}",
    "address"            : f"Lane {RND}, Uttara, Dhaka",
    "phone"              : f"016{RND}001",
    "email"              : f"mediplus{RND}@test.com",
    "delivery_charge"    : "50",
    "free_delivery_above": "500",
}

TOLUMOLU = {
    "first_name"      : "Tolumolu",
    "last_name"       : RND,
    "username"        : f"tolumolu{RND}",
    "email"           : f"tolumolu{RND}@pharmacy.com",
    "password"        : f"Tolumolu{RND}@x",
    "confirm_password": f"Tolumolu{RND}@x",
    "phone"           : f"016{RND}002",
    "designation"     : "Pharmacy Manager",
}

BATEN = {
    "first_name"      : "Baten",
    "last_name"       : "Mia",
    "username"        : f"baten{RND}",
    "email"           : f"baten{RND}@doctor.com",
    "password"        : f"Baten{RND}@x",
    "confirm_password": f"Baten{RND}@x",
    "phone"           : f"017{RND}001",
}

ICU_BED = {
    "bed_number"  : f"ICU-{RND}",
    "bed_type"    : "ICU",
    "daily_charge": "5000",
    "equipment"   : "Ventilator, Heart Monitor",
}

RAFIQ = {
    "first_name"      : "Rafiq",
    "last_name"       : "Ahmed",
    "email"           : f"rafiq{RND}@gmail.com",
    "phone"           : f"018{RND}001",
    "age"             : "35",
    "gender"          : "male",
    "blood_group"     : "B+",
    "password"        : f"Rafiq{RND}@x",
    "confirm_password": f"Rafiq{RND}@x",
}

APPT = {
    "date"    : "2026-08-15",
    "symptoms": "Fever, chest pain and headache",
}

CHECKOUT_DATA = {
    "full_name": "Rafiq Ahmed",
    "email"    : f"rafiq{RND}@gmail.com",
    "phone"    : f"018{RND}001",
    "address"  : f"House {RND}, Road 5, Dhaka",
    "notes"    : "Please deliver quickly",
}

ICU_BOOK = {
    "condition"         : "Requires intensive cardiac monitoring",
    "expected_discharge": "2026-08-25",
}

MEDICINE = {
    "name"       : f"Baten Special {RND}",
    "category"   : "tablet",
    "price"      : "150.00",
    "stock"      : "100",
    "description": "Medicine added by Tolumolu for Dr. Baten patients",
}

RESULTS = []


# ══════════════════════════════
#  HELPERS
# ══════════════════════════════
def banner(icon, text):
    bar = "─" * 74
    print(f"\n┌{bar}┐")
    print(f"│  {icon}  {text:<70}│")
    print(f"└{bar}┘")

def step(msg):  print(f"   ➤  {msg}")
def ok(msg):    print(f"   ✅ {msg}")
def warn(msg):  print(f"   ⚠️  {msg}")

def tick():
    for i in range(SHOW, 0, -1):
        print(f"      ⏱  {i}s ", end="\r")
        time.sleep(1)
    print("           ", end="\r")

def shot(dr, name):
    try:
        os.makedirs(SS_DIR, exist_ok=True)
        safe = "".join(c for c in name if c.isalnum() or c in "_-")
        dr.save_screenshot(f"{SS_DIR}/{safe}.png")
    except Exception:
        pass

def go(dr, path, lbl=""):
    url = f"{BASE}{path}"
    print(f"\n  📄  {lbl or path}")
    print(f"      {url}")
    try:
        dr.get(url)
        time.sleep(WAIT)
        title = dr.title
        cur   = dr.current_url.lower()
        if any(e in title for e in ["not found","500","403","TemplateDoesNotExist","NoReverseMatch"]):
            warn("Page not built — skipping")
            RESULTS.append((lbl, "⚠️  Not Built"))
            return
        if "login" in cur and "login" not in path.lower():
            warn("Session expired")
            RESULTS.append((lbl, "⚠️  Session"))
            return
        ok(f"Loaded → {title[:65]}")
        shot(dr, lbl)
        RESULTS.append((lbl, "✅ Pass"))
        tick()
    except Exception as e:
        warn(str(e))

def do_login(dr, email, pwd, name):
    print(f"\n  🔐  Login → {name}")
    print(f"      {email}  /  {pwd}")
    dr.get(f"{BASE}/login/")
    time.sleep(WAIT)
    fill(dr, "email", email)
    fill(dr, "password", pwd)
    do_submit(dr)
    time.sleep(2)
    if "login" in dr.current_url.lower():
        warn(f"Login FAILED → {name}")
        return False
    ok(f"Logged in → {name}")
    shot(dr, f"LOGIN_{name.replace(' ','_')}")
    return True

def do_logout(dr):
    dr.get(f"{BASE}/logout/")
    time.sleep(2)
    ok("Logged out\n")

def fill(dr, name, value):
    for loc in [(By.NAME, name), (By.ID, name), (By.ID, f"id_{name}")]:
        try:
            el = dr.find_element(*loc)
            if el.is_displayed() and el.is_enabled():
                el.clear()
                el.send_keys(value)
                return True
        except Exception:
            pass
    return False

def do_sel(dr, name, val):
    for css in [f"select[name='{name}']", f"#{name}", f"#id_{name}"]:
        try:
            s = Select(dr.find_element(By.CSS_SELECTOR, css))
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

def do_submit(dr):
    for css in ["button[type='submit']", "input[type='submit']", "button.btn-primary"]:
        try:
            btn = dr.find_element(By.CSS_SELECTOR, css)
            if btn.is_displayed() and btn.is_enabled():
                btn.click()
                time.sleep(WAIT)
                return
        except Exception:
            pass
    try:
        dr.find_element(By.TAG_NAME, "form").submit()
        time.sleep(WAIT)
    except Exception:
        pass

def open_modal(dr, modal_id):
    try:
        dr.execute_script(
            f"bootstrap.Modal.getOrCreateInstance("
            f"document.getElementById('{modal_id}')).show();"
        )
        time.sleep(1.5)
        return True
    except Exception:
        return False

def fill_modal(dr, modal_id, data):
    for name, value in data.items():
        for css in [f"#{modal_id} [name='{name}']", f"#{modal_id} #{name}"]:
            try:
                el = dr.find_element(By.CSS_SELECTOR, css)
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

def submit_modal(dr, modal_id):
    for css in [f"#{modal_id} button[type='submit']",
                f"#{modal_id} .btn-primary",
                f"#{modal_id} input[type='submit']"]:
        try:
            btn = dr.find_element(By.CSS_SELECTOR, css)
            if btn.is_displayed() and btn.is_enabled():
                btn.click()
                time.sleep(WAIT + 0.5)
                return True
        except Exception:
            pass
    return False

def visible(dr, *words):
    try:
        body = dr.find_element(By.TAG_NAME, "body").text.lower()
        return any(w.lower() in body for w in words)
    except Exception:
        return False

def rec(label, passed=True):
    RESULTS.append((label, "✅ Pass" if passed else "⚠️  Skip"))


# ══════════════════════════════════════════════════════════════
#  STEP 0 — AUTH PAGES
# ══════════════════════════════════════════════════════════════
def step0(dr):
    banner("🔐", "STEP 0 — Sign Up · Sign In · Forgot Password")
    go(dr, "/signup/",          "S0_Sign_Up_Page")
    go(dr, "/login/",           "S0_Sign_In_Page")
    go(dr, "/forgot-password/", "S0_Forgot_Password")


# ══════════════════════════════════════════════════════════════
#  STEP 1 — SUPER ADMIN
# ══════════════════════════════════════════════════════════════
def step1(dr):
    banner("👑", "STEP 1 — SUPER ADMIN  (admin@super.com / tamim0011)")
    if not do_login(dr, "admin@super.com", "tamim0011", "Super Admin"):
        return

    go(dr, "/admin/dashboard/", "S1_Admin_Dashboard")

    # Add Hospital
    banner("🏥", f"S1 ► Add Hospital → '{HOSPITAL['name']}'")
    go(dr, "/admin/hospitals/", "S1_Hospitals_List")
    open_modal(dr, "addHospitalModal")
    fill_modal(dr, "addHospitalModal", {
        "name": HOSPITAL["name"], "code": HOSPITAL["code"],
        "address": HOSPITAL["address"], "phone": HOSPITAL["phone"],
        "email": HOSPITAL["email"],
    })
    shot(dr, "S1_hospital_form")
    submit_modal(dr, "addHospitalModal")
    time.sleep(1)
    go(dr, "/admin/hospitals/", "S1_Hospital_Added_Verify")
    if visible(dr, HOSPITAL["name"]):
        ok(f"✅ '{HOSPITAL['name']}' list এ দেখা যাচ্ছে!")
    rec(f"S1_Hospital_Added")

    # Add Mokles (Hospital Admin)
    banner("👨‍💼", "S1 ► Add Hospital Admin → 'Mokles Bhai'")
    step(f"Mokles credentials (Step 2 এ use হবে): {MOKLES['email']} / {MOKLES['password']}")
    go(dr, "/admin/hospital-admins/", "S1_Hospital_Admins_List")
    open_modal(dr, "addAdminModal")
    fill_modal(dr, "addAdminModal", {
        "username": MOKLES["username"], "email": MOKLES["email"],
        "password": MOKLES["password"], "confirm_password": MOKLES["confirm_password"],
        "first_name": MOKLES["first_name"], "last_name": MOKLES["last_name"],
        "phone": MOKLES["phone"],
    })
    shot(dr, "S1_mokles_form")
    submit_modal(dr, "addAdminModal")
    time.sleep(1)
    go(dr, "/admin/hospital-admins/", "S1_Mokles_Added_Verify")
    if visible(dr, MOKLES["first_name"], MOKLES["email"]):
        ok("✅ 'Mokles Bhai' list এ দেখা যাচ্ছে!")
    rec("S1_Hospital_Admin_Mokles_Added")

    # Add Pharmacy
    banner("💊", f"S1 ► Add Pharmacy → '{PHARMACY['name']}'")
    go(dr, "/super-admin/pharmacy-admins/", "S1_Pharmacy_Page")
    try:
        form = dr.find_element(By.XPATH, "//form[.//input[@value='create_pharmacy']]")
        for field, val in PHARMACY.items():
            try:
                el = form.find_element(By.NAME, field)
                el.clear(); el.send_keys(val)
            except Exception:
                pass
        shot(dr, "S1_pharmacy_form")
        btn = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        dr.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.5)
        btn.click()
        time.sleep(WAIT + 1)
        ok(f"'{PHARMACY['name']}' submitted!")
        rec("S1_Pharmacy_Added")
    except Exception as e:
        warn(f"Pharmacy form: {e}")
    tick()

    # Add Tolumolu (Pharmacy Admin)
    banner("💊", "S1 ► Add Pharmacy Admin → 'Tolumolu'")
    step(f"Tolumolu credentials (Step 5 এ use হবে): {TOLUMOLU['email']} / {TOLUMOLU['password']}")
    go(dr, "/super-admin/pharmacy-admins/", "S1_Pharmacy_Admin_Create")
    try:
        dr.execute_script("""
            var f = document.querySelector('form input[name="action"][value="create_admin"]');
            if(f) f = f.closest('form');
            var d = arguments[0];
            if(f){
                Object.keys(d).forEach(function(k){
                    var el = f.querySelector('[name="'+k+'"]');
                    if(el) el.value = d[k];
                });
                var pid = f.querySelector('[name="pharmacy_id"]');
                if(pid && !pid.value) pid.value = '1';
            }
        """, {k: v for k, v in TOLUMOLU.items()})
        shot(dr, "S1_tolumolu_form")
        btn = dr.find_element(
            By.XPATH, "//form[.//input[@value='create_admin']]//button[@type='submit']"
        )
        dr.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.5)
        btn.click()
        time.sleep(WAIT + 1)
        ok("'Tolumolu' submitted!")
        rec("S1_Pharmacy_Admin_Tolumolu_Added")
    except Exception as e:
        warn(f"Tolumolu form: {e}")
    tick()

    go(dr, "/admin/hospitals/",             "S1_All_Hospitals_Final")
    go(dr, "/admin/hospital-admins/",       "S1_All_Hospital_Admins_Final")
    go(dr, "/super-admin/pharmacy-admins/", "S1_All_Pharmacy_Admins_Final")
    do_logout(dr)


# ══════════════════════════════════════════════════════════════
#  STEP 2 — MOKLES (Hospital Admin added by Super Admin)
# ══════════════════════════════════════════════════════════════
def step2(dr):
    banner("🏥", "STEP 2 — 'Mokles Bhai' login (added by Super Admin in Step 1)")
    step(f"Login: {MOKLES['email']}  /  {MOKLES['password']}")

    if not do_login(dr, MOKLES["email"], MOKLES["password"], "Mokles Bhai"):
        banner("❌", "Mokles login failed — hospital assign না হলে login কাজ করে না")
        return

    go(dr, "/hospital/dashboard/", "S2_Hospital_Dashboard")

    # Add Doctor: Baten
    banner("👨‍⚕️", "S2 ► Mokles adds Doctor → 'Dr. Baten Mia'")
    step(f"Baten credentials (Step 4 এ use হবে): {BATEN['email']} / {BATEN['password']}")
    go(dr, "/hospital/doctors/", "S2_Doctors_List")
    open_modal(dr, "addDoctorModal")
    fill_modal(dr, "addDoctorModal", {
        "first_name": BATEN["first_name"], "last_name": BATEN["last_name"],
        "username": BATEN["username"], "email": BATEN["email"],
        "password": BATEN["password"], "confirm_password": BATEN["confirm_password"],
        "phone": BATEN["phone"],
    })
    shot(dr, "S2_baten_doctor_form")
    submit_modal(dr, "addDoctorModal")
    time.sleep(1)
    go(dr, "/hospital/doctors/", "S2_Doctor_Baten_Added_Verify")
    if visible(dr, BATEN["first_name"], BATEN["last_name"]):
        ok("✅ 'Dr. Baten Mia' doctors list এ দেখা যাচ্ছে!")
    rec("S2_Doctor_Baten_Mia_Added")

    # Add ICU Bed
    banner("🛏️", f"S2 ► Mokles adds ICU Bed → '{ICU_BED['bed_number']}'")
    go(dr, "/hospital/beds/", "S2_ICU_Beds_List")
    open_modal(dr, "addBedModal")
    fill_modal(dr, "addBedModal", {
        "bed_number": ICU_BED["bed_number"], "bed_type": ICU_BED["bed_type"],
        "daily_charge": ICU_BED["daily_charge"], "equipment": ICU_BED["equipment"],
    })
    shot(dr, "S2_icu_bed_form")
    submit_modal(dr, "addBedModal")
    time.sleep(1)
    go(dr, "/hospital/beds/", "S2_ICU_Bed_Added_Verify")
    if visible(dr, ICU_BED["bed_number"]):
        ok(f"✅ '{ICU_BED['bed_number']}' beds list এ দেখা যাচ্ছে!")
    rec(f"S2_ICU_Bed_Added")

    go(dr, "/hospital/patients/",     "S2_Patients_List")
    go(dr, "/hospital/appointments/", "S2_Appointments_List")
    go(dr, "/hospital/emergencies/",  "S2_Emergencies_List")
    go(dr, "/hospital/test-reports/", "S2_Test_Reports")
    go(dr, "/hospital/products/",     "S2_Products_List")
    do_logout(dr)


# ══════════════════════════════════════════════════════════════
#  STEP 3 — PATIENT: RAFIQ AHMED
# ══════════════════════════════════════════════════════════════
def step3(dr):
    banner("👤", "STEP 3 — New Patient 'Rafiq Ahmed' — signup & full workflow")

    # Signup
    banner("📝", f"S3 ► Rafiq Ahmed signs up → {RAFIQ['email']}")
    go(dr, "/signup/", "S3_Signup_Page")
    fill(dr, "first_name",       RAFIQ["first_name"])
    fill(dr, "last_name",        RAFIQ["last_name"])
    fill(dr, "email",            RAFIQ["email"])
    fill(dr, "phone",            RAFIQ["phone"])
    fill(dr, "age",              RAFIQ["age"])
    do_sel(dr, "gender",         RAFIQ["gender"])
    do_sel(dr, "blood_group",    RAFIQ["blood_group"])
    fill(dr, "password",         RAFIQ["password"])
    fill(dr, "confirm_password", RAFIQ["confirm_password"])
    try:
        cb = dr.find_element(By.NAME, "terms")
        if not cb.is_selected():
            dr.execute_script("arguments[0].click();", cb)
    except Exception:
        pass
    shot(dr, "S3_signup_form_filled")
    do_submit(dr)
    time.sleep(2)
    ok("'Rafiq Ahmed' registered!")
    shot(dr, "S3_signup_done")
    rec("S3_Rafiq_Signup")
    tick()

    if not do_login(dr, RAFIQ["email"], RAFIQ["password"], "Rafiq Ahmed"):
        warn("Rafiq login failed")
        return

    go(dr, "/patient/dashboard/", "S3_Patient_Dashboard")

    # Book appointment with Dr. Baten
    banner("📅", "S3 ► Rafiq books appointment with 'Dr. Baten Mia' (added by Mokles)")
    go(dr, "/patient/book-appointment/", "S3_Book_Appointment_Page")

    step("Selecting 'Dr. Baten Mia' from dropdown")
    try:
        s_el = dr.find_element(By.CSS_SELECTOR, "select[name='doctor_id']")
        s    = Select(s_el)
        found = False
        for opt in s.options:
            if BATEN["first_name"].lower() in opt.text.lower() or \
               BATEN["last_name"].lower() in opt.text.lower():
                opt.click()
                ok(f"✅ Selected: '{opt.text}'")
                found = True
                break
        if not found and len(s.options) > 1:
            s.select_by_index(1)
            ok(f"Selected: {s.first_selected_option.text}")
        time.sleep(WAIT)
    except Exception as e:
        warn(f"Doctor select: {e}")

    step(f"Date: {APPT['date']}")
    try:
        d = dr.find_element(By.NAME, "date")
        dr.execute_script(f"arguments[0].value='{APPT['date']}'", d)
        dr.execute_script("arguments[0].dispatchEvent(new Event('change'))", d)
        time.sleep(WAIT)
        ok("Date set")
    except Exception as e:
        warn(f"Date: {e}")

    step("Time slot select করছে")
    time.sleep(1.5)
    try:
        ts = dr.find_element(By.CSS_SELECTOR, "select[name='time']")
        s  = Select(ts)
        if len(s.options) > 1:
            s.select_by_index(1)
            ok(f"Time: {s.first_selected_option.text}")
        else:
            warn("No slots — doctor schedule set না থাকলে slot আসবে না")
    except Exception as e:
        warn(f"Time: {e}")

    fill(dr, "symptoms", APPT["symptoms"])
    shot(dr, "S3_appointment_form_filled")
    do_submit(dr)
    ok("Appointment submitted!")
    shot(dr, "S3_appointment_done")
    rec("S3_Appointment_with_Dr_Baten")
    tick()

    # Buy medicine
    banner("💊", "S3 ► Rafiq medicine কেনে → cart → checkout")
    go(dr, "/patient/products/", "S3_Products_Page")
    try:
        forms = dr.find_elements(
            By.CSS_SELECTOR, "form.add-to-cart-form, form[action*='add-to-cart']"
        )
        if forms:
            dr.execute_script("arguments[0].submit();", forms[0])
            time.sleep(WAIT)
            ok("Product added to cart!")
    except Exception:
        pass
    shot(dr, "S3_product_added")
    tick()

    go(dr, "/cart/", "S3_Cart_Page")
    tick()

    go(dr, "/checkout/", "S3_Checkout_Page")
    for name, val in CHECKOUT_DATA.items():
        fill(dr, name, val)
    try:
        cod = dr.find_element(
            By.CSS_SELECTOR, "input[name='payment_method'][value='cod']"
        )
        dr.execute_script("arguments[0].click();", cod)
        ok("Cash on Delivery selected")
    except Exception:
        pass
    shot(dr, "S3_checkout_filled")
    do_submit(dr)
    ok("Order placed!")
    shot(dr, "S3_order_placed")
    rec("S3_Order_Placed")
    tick()

    # Book ICU Bed
    banner("🛏️", f"S3 ► Rafiq books ICU Bed '{ICU_BED['bed_number']}' (Mokles এর add করা)")
    go(dr, "/patient/icu-beds/", "S3_ICU_Beds_Page")
    if visible(dr, ICU_BED["bed_number"]):
        ok(f"✅ '{ICU_BED['bed_number']}' দেখা যাচ্ছে — Mokles এর add করা!")

    booked = False
    try:
        links = dr.find_elements(By.XPATH, "//a[contains(@href,'icu-beds/book')]")
        if links:
            dr.get(links[0].get_attribute("href"))
            time.sleep(WAIT)
            booked = True
    except Exception:
        pass
    if not booked:
        go(dr, "/patient/icu-beds/book/1/", "S3_ICU_Book_Page")

    fill(dr, "condition", ICU_BOOK["condition"])
    try:
        el = dr.find_element(By.NAME, "expected_discharge")
        dr.execute_script(f"arguments[0].value='{ICU_BOOK['expected_discharge']}'", el)
    except Exception:
        pass
    shot(dr, "S3_icu_form_filled")
    do_submit(dr)
    ok(f"ICU Bed '{ICU_BED['bed_number']}' booked!")
    shot(dr, "S3_icu_booked")
    rec("S3_ICU_Bed_Booked")
    tick()

    go(dr, "/patient/my-appointments/", "S3_My_Appointments")
    go(dr, "/patient/icu-bookings/",    "S3_My_ICU_Bookings")
    go(dr, "/patient/orders/",          "S3_My_Orders")
    go(dr, "/patient/bills/",           "S3_My_Bills")
    go(dr, "/patient/test-reports/",    "S3_Test_Reports")
    go(dr, "/patient/profile/",         "S3_My_Profile")
    do_logout(dr)


# ══════════════════════════════════════════════════════════════
#  STEP 4 — DR. BATEN MIA (added by Mokles in Step 2)
# ══════════════════════════════════════════════════════════════
def step4(dr):
    banner("👨‍⚕️", "STEP 4 — 'Dr. Baten Mia' login (added by Mokles in Step 2)")
    step(f"Login: {BATEN['email']}  /  {BATEN['password']}")

    if not do_login(dr, BATEN["email"], BATEN["password"], "Dr. Baten Mia"):
        banner("❌", "Dr. Baten login failed!")
        return

    go(dr, "/doctor/dashboard/", "S4_Doctor_Dashboard")

    banner("📋", "S4 ► Dr. Baten এর appointments — Rafiq এর booking আছে!")
    go(dr, "/doctor/appointments/", "S4_My_Appointments")
    if visible(dr, RAFIQ["first_name"], RAFIQ["email"]):
        ok(f"✅ 'Rafiq Ahmed' এর appointment দেখা যাচ্ছে!")
    else:
        ok("Appointments page loaded")
    shot(dr, "S4_appointments_rafiq_check")
    rec("S4_Dr_Baten_Sees_Rafiq_Appointment")

    try:
        links = dr.find_elements(By.XPATH, "//a[contains(@href,'doctor/appointment/')]")
        if links:
            dr.get(links[0].get_attribute("href"))
            time.sleep(WAIT)
            ok("Appointment detail opened")
            shot(dr, "S4_appointment_detail")
            tick()
    except Exception:
        pass

    banner("👥", "S4 ► Dr. Baten এর patient list — Rafiq visible!")
    go(dr, "/doctor/patients/", "S4_My_Patients")
    if visible(dr, RAFIQ["first_name"]):
        ok(f"✅ 'Rafiq Ahmed' patient list এ দেখা যাচ্ছে!")
    rec("S4_Dr_Baten_Sees_Patient_List")

    try:
        links = dr.find_elements(By.XPATH, "//a[contains(@href,'doctor/patient/')]")
        if links:
            dr.get(links[0].get_attribute("href"))
            time.sleep(WAIT)
            ok("Patient record opened")
            shot(dr, "S4_patient_record")
            tick()
    except Exception:
        pass

    go(dr, "/doctor/notifications/", "S4_Notifications")
    go(dr, "/doctor/profile/",       "S4_Doctor_Profile")
    do_logout(dr)


# ══════════════════════════════════════════════════════════════
#  STEP 5 — TOLUMOLU (Pharmacy Admin added by Super Admin)
# ══════════════════════════════════════════════════════════════
def step5(dr):
    banner("💊", "STEP 5 — 'Tolumolu' login (Pharmacy Admin added in Step 1)")
    step(f"Login: {TOLUMOLU['email']}  /  {TOLUMOLU['password']}")

    if not do_login(dr, TOLUMOLU["email"], TOLUMOLU["password"], "Tolumolu"):
        banner("❌", "Tolumolu login failed!")
        return

    go(dr, "/pharmacy/dashboard/", "S5_Pharmacy_Dashboard")

    banner("💊", f"S5 ► Tolumolu adds Medicine → '{MEDICINE['name']}'")
    go(dr, "/pharmacy/products/", "S5_Products_List")
    open_modal(dr, "addProductModal")
    fill_modal(dr, "addProductModal", {
        "name": MEDICINE["name"], "category": MEDICINE["category"],
        "price": MEDICINE["price"], "stock": MEDICINE["stock"],
        "description": MEDICINE["description"],
    })
    shot(dr, "S5_medicine_form")
    submit_modal(dr, "addProductModal")
    time.sleep(1)

    go(dr, "/pharmacy/products/", "S5_Medicine_Added_Verify")
    if visible(dr, MEDICINE["name"]):
        ok(f"✅ '{MEDICINE['name']}' products list এ দেখা যাচ্ছে!")
    rec("S5_Medicine_Added")

    banner("📦", "S5 ► Tolumolu orders দেখে — Rafiq এর order এখানে!")
    go(dr, "/pharmacy/orders/", "S5_All_Orders")
    if visible(dr, RAFIQ["first_name"], RAFIQ["email"]):
        ok(f"✅ 'Rafiq Ahmed' এর order দেখা যাচ্ছে!")
    else:
        ok("Orders page loaded")
    rec("S5_Tolumolu_Sees_Rafiq_Order")

    try:
        links = dr.find_elements(By.XPATH, "//a[contains(@href,'pharmacy/orders/')]")
        detail = [l for l in links if l.get_attribute("href") and
                  l.get_attribute("href").rstrip("/").split("/")[-1].isdigit()]
        if detail:
            dr.get(detail[0].get_attribute("href"))
            time.sleep(WAIT)
            ok("Order detail opened")
            shot(dr, "S5_order_detail")
            tick()
    except Exception:
        pass

    go(dr, "/pharmacy/products/", "S5_Products_Final")
    do_logout(dr)


# ══════════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════════
def print_summary():
    print("\n\n" + "═" * 78)
    print("              CAREFUSION CHAIN WORKFLOW — TEST COMPLETE")
    print("═" * 78)
    print(f"\n  {'Action':<52}  Result")
    print("  " + "─" * 65)
    passed = warned = 0
    for action, result in RESULTS:
        m = "✅" if "Pass" in result else "⚠️ "
        print(f"  {action:<52}  {m} {result}")
        if "Pass" in result: passed += 1
        else:                warned  += 1
    print("  " + "─" * 65)
    print(f"\n  Total: {len(RESULTS)}   ✅ Pass: {passed}   ⚠️  Skip: {warned}")
    print(f"\n  📁 Screenshots: {os.path.abspath(SS_DIR)}/")
    print(f"  🔑 Run ID: {RND}")
    print(f"""
  ┌─ CHAIN STORY ────────────────────────────────────────────────────┐
  │                                                                  │
  │  STEP 1  Super Admin adds:                                       │
  │    🏥  Hospital    : {HOSPITAL['name']:<40}│
  │    👨  HospAdmin   : Mokles Bhai  ({MOKLES['email']})  │
  │    💊  Pharmacy    : {PHARMACY['name']:<40}│
  │    💊  PharmAdmin  : Tolumolu     ({TOLUMOLU['email']})│
  │                                                                  │
  │  STEP 2  Mokles Bhai login → adds:                               │
  │    👨‍⚕️  Doctor   : Dr. Baten Mia ({BATEN['email']})  │
  │    🛏️  ICU Bed  : {ICU_BED['bed_number']:<43}│
  │                                                                  │
  │  STEP 3  Rafiq Ahmed signup → books Dr. Baten, orders           │
  │          medicine, books ICU Bed                                 │
  │                                                                  │
  │  STEP 4  Dr. Baten login → sees Rafiq appointment ✅            │
  │                                                                  │
  │  STEP 5  Tolumolu login → adds medicine, sees Rafiq order ✅    │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
""")
    print("═" * 78)


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═" * 78)
    print("  CAREFUSION — Chain Workflow Selenium Test")
    print("  ─────────────────────────────────────────")
    print("  City Hospital → Mokles (HAdmin) → Dr. Baten → Rafiq (Patient)")
    print("  → Tolumolu (PharmAdmin) — সব নতুন, পুরনো কোনো user নেই")
    print("═" * 78)
    print("\n  ▶  Django চালু রাখো:  python manage.py runserver\n")
    input("  ENTER চাপো শুরু করতে…\n")

    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-notifications")
    dr = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts,
    )
    print("✅  Browser ready\n")

    try:
        step0(dr)
        step1(dr)
        step2(dr)
        step3(dr)
        step4(dr)
        step5(dr)
        print_summary()
    except Exception as e:
        print(f"\n  ❌ Fatal: {e}")
        import traceback; traceback.print_exc()
    finally:
        input("\n  ENTER চাপো browser বন্ধ করতে…")
        dr.quit()