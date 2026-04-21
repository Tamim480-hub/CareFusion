# create_hospital.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Hospital, User, HospitalAdminProfile


def create_hospital_and_admin():
    print("=== নতুন হাসপাতাল ও অ্যাডমিন তৈরি করুন ===\n")

    # হাসপাতালের তথ্য নিন
    hospital_name = input("হাসপাতালের নাম: ")
    hospital_code = input("হাসপাতালের কোড (যেমন: CGH001): ")
    hospital_address = input("ঠিকানা: ")
    hospital_phone = input("ফোন নম্বর: ")
    hospital_email = input("ইমেইল: ")

    # হাসপাতাল তৈরি করুন
    hospital = Hospital.objects.create(
        name=hospital_name,
        code=hospital_code,
        address=hospital_address,
        phone=hospital_phone,
        email=hospital_email,
        is_active=True
    )
    print(f"\n✅ হাসপাতাল তৈরি হয়েছে: {hospital.name}")

    # অ্যাডমিন ইউজারের তথ্য নিন
    print("\n--- অ্যাডমিন ইউজারের তথ্য ---")
    username = input("অ্যাডমিন ইউজারনেম: ")
    password = input("পাসওয়ার্ড: ")
    email = input("অ্যাডমিন ইমেইল: ")
    first_name = input("নাম (প্রথম অংশ): ")
    last_name = input("নাম (শেষ অংশ): ")

    # অ্যাডমিন ইউজার তৈরি করুন
    admin_user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        user_type='hospital_admin',  # 'admin' না হয়ে 'hospital_admin'
        first_name=first_name,
        last_name=last_name
    )
    print(f"\n✅ অ্যাডমিন ইউজার তৈরি হয়েছে: {admin_user.username}")

    # হাসপাতাল অ্যাডমিন প্রোফাইল তৈরি করুন (মডেলের নাম HospitalAdminProfile)
    hospital_admin = HospitalAdminProfile.objects.create(
        user=admin_user,
        hospital=hospital,
        designation='Hospital Administrator',
        phone=hospital_phone,
        is_active=True
    )
    print(f"\n✅ হাসপাতাল অ্যাডমিন প্রোফাইল তৈরি হয়েছে!")

    print("\n" + "=" * 50)
    print("🎉 সফলভাবে হাসপাতাল ও অ্যাডমিন তৈরি হয়েছে!")
    print(f"হাসপাতাল: {hospital.name}")
    print(f"হাসপাতাল কোড: {hospital.code}")
    print(f"ঠিকানা: {hospital.address}")
    print(f"ফোন: {hospital.phone}")
    print(f"ইমেইল: {hospital.email}")
    print("-" * 50)
    print(f"অ্যাডমিন ইউজারনেম: {username}")
    print(f"অ্যাডমিন পাসওয়ার্ড: {password}")
    print(f"অ্যাডমিন ইমেইল: {email}")
    print("=" * 50)


def list_all_hospitals():
    """সব হাসপাতালের তালিকা দেখান"""
    hospitals = Hospital.objects.filter(is_active=True)
    print("\n📋 সক্রিয় হাসপাতালের তালিকা:")
    print("-" * 50)
    for h in hospitals:
        admin_count = HospitalAdminProfile.objects.filter(hospital=h).count()
        print(f"🏥 {h.name} ({h.code})")
        print(f"   📍 {h.address}")
        print(f"   📞 {h.phone}")
        print(f"   📧 {h.email}")
        print(f"   👨‍💼 অ্যাডমিন সংখ্যা: {admin_count}")
        print()


if __name__ == '__main__':
    print("=" * 50)
    print("🏥 CARE FUSION HOSPITAL MANAGEMENT SYSTEM")
    print("=" * 50)

    while True:
        print("\nনির্বাচন করুন:")
        print("1. নতুন হাসপাতাল ও অ্যাডমিন তৈরি করুন")
        print("2. সব হাসপাতালের তালিকা দেখুন")
        print("3. প্রস্থান করুন")

        choice = input("\nআপনার পছন্দ (1-3): ")

        if choice == '1':
            create_hospital_and_admin()
        elif choice == '2':
            list_all_hospitals()
        elif choice == '3':
            print("বিদায়! 👋")
            break
        else:
            print("ভুল নির্বাচন! দয়া করে 1, 2 বা 3 চাপুন।")