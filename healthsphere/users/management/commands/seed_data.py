"""
HealthSphere AI - Sample Data Seeder
=====================================

Management command to populate the database with realistic sample data
for all models in the HealthSphere AI platform.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear   # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import date, time, timedelta
import random
import uuid


class Command(BaseCommand):
    help = "Seeds the database with realistic sample data for HealthSphere AI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seeded data before creating new data",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.clear_data()

        self.stdout.write(self.style.NOTICE("🌱 Starting HealthSphere AI data seeding..."))

        with transaction.atomic():
            self.seed_roles()
            self.seed_users()
            self.seed_appointment_types()
            self.seed_medication_database()
            self.seed_pharmacies()
            self.seed_patient_profiles()
            self.seed_doctor_schedules()
            self.seed_vital_records()
            self.seed_medical_records()
            self.seed_treatment_plans()
            self.seed_appointments()
            self.seed_prescriptions()
            self.seed_health_metrics()
            self.seed_analytics()

        self.stdout.write(self.style.SUCCESS("\n✅ Sample data seeding complete!"))
        self.stdout.write(self.style.SUCCESS("   Login credentials: password = 'HealthSphere123!'"))

    # ------------------------------------------------------------------ #
    #  CLEAR                                                               #
    # ------------------------------------------------------------------ #
    def clear_data(self):
        self.stdout.write(self.style.WARNING("⚠️  Clearing existing sample data..."))
        from users.models import User, Role
        from appointments.models import Appointment, AppointmentType, DoctorSchedule
        from clinical_portal.models import MedicalRecord, TreatmentPlan, VitalRecord
        from prescriptions.models import (
            MedicationDatabase, Pharmacy, Prescription, DrugInteraction,
        )
        from patient_portal.models import HealthMetric, PatientProfile
        from analytics.models import (
            PredictiveModel, PatientFlowPrediction, ClinicalOutcomePrediction, AnalyticsReport,
        )

        Appointment.objects.all().delete()
        Prescription.objects.all().delete()
        MedicalRecord.objects.all().delete()
        TreatmentPlan.objects.all().delete()
        VitalRecord.objects.all().delete()
        HealthMetric.objects.all().delete()
        PatientProfile.objects.all().delete()
        DoctorSchedule.objects.all().delete()
        ClinicalOutcomePrediction.objects.all().delete()
        PatientFlowPrediction.objects.all().delete()
        AnalyticsReport.objects.all().delete()
        PredictiveModel.objects.all().delete()
        DrugInteraction.objects.all().delete()
        Prescription.objects.all().delete()
        Pharmacy.objects.all().delete()
        MedicationDatabase.objects.all().delete()
        AppointmentType.objects.all().delete()
        User.objects.filter(username__startswith="sample_").delete()
        self.stdout.write(self.style.WARNING("   Cleared.\n"))

    # ------------------------------------------------------------------ #
    #  ROLES                                                               #
    # ------------------------------------------------------------------ #
    def seed_roles(self):
        from users.models import Role
        roles_data = [
            ("admin",   "Hospital administrators with full system access"),
            ("doctor",  "Licensed medical doctors with clinical access"),
            ("nurse",   "Nursing staff with patient care access"),
            ("patient", "Registered patients with self-service access"),
        ]
        self.roles = {}
        for name, desc in roles_data:
            role, _ = Role.objects.get_or_create(name=name, defaults={"description": desc})
            self.roles[name] = role
        self.stdout.write(f"  ✓ Roles: {len(self.roles)}")

    # ------------------------------------------------------------------ #
    #  USERS                                                               #
    # ------------------------------------------------------------------ #
    def seed_users(self):
        from users.models import User, UserProfile

        PASSWORD = "HealthSphere123!"

        # --- Admins ---
        admins_data = [
            ("sample_admin1", "admin1@healthsphere.ai", "Alexandra", "Morgan"),
            ("sample_admin2", "admin2@healthsphere.ai", "Benjamin", "Crawford"),
        ]

        # --- Doctors ---
        doctors_data = [
            ("sample_dr_patel",    "dr.patel@healthsphere.ai",    "Ananya",    "Patel",    "Cardiology",      "EMP001"),
            ("sample_dr_chen",     "dr.chen@healthsphere.ai",     "Michael",   "Chen",     "Neurology",       "EMP002"),
            ("sample_dr_johnson",  "dr.johnson@healthsphere.ai",  "Sarah",     "Johnson",  "General Medicine","EMP003"),
            ("sample_dr_garcia",   "dr.garcia@healthsphere.ai",   "Carlos",    "Garcia",   "Orthopedics",     "EMP004"),
            ("sample_dr_kim",      "dr.kim@healthsphere.ai",      "Ji-Young",  "Kim",      "Oncology",        "EMP005"),
            ("sample_dr_patel2",   "dr.patel2@healthsphere.ai",   "Raj",       "Patel",    "Pediatrics",      "EMP006"),
        ]

        # --- Nurses ---
        nurses_data = [
            ("sample_nurse_adams",   "nurse.adams@healthsphere.ai",   "Emily",   "Adams",   "Cardiology",  "NRS001"),
            ("sample_nurse_brooks",  "nurse.brooks@healthsphere.ai",  "James",   "Brooks",  "Emergency",   "NRS002"),
            ("sample_nurse_cooper",  "nurse.cooper@healthsphere.ai",  "Linda",   "Cooper",  "Oncology",    "NRS003"),
        ]

        # --- Patients ---
        patients_data = [
            ("sample_pt_smith",    "patient.smith@email.com",    "John",    "Smith",    date(1985, 4, 12),  "555-0101"),
            ("sample_pt_jones",    "patient.jones@email.com",    "Maria",   "Jones",    date(1972, 8, 23),  "555-0102"),
            ("sample_pt_wilson",   "patient.wilson@email.com",   "Robert",  "Wilson",   date(1990, 1, 5),   "555-0103"),
            ("sample_pt_taylor",   "patient.taylor@email.com",   "Emma",    "Taylor",   date(1968, 11, 17), "555-0104"),
            ("sample_pt_anderson", "patient.anderson@email.com", "David",   "Anderson", date(2001, 6, 30),  "555-0105"),
            ("sample_pt_thomas",   "patient.thomas@email.com",   "Sophia",  "Thomas",   date(1955, 3, 8),   "555-0106"),
            ("sample_pt_jackson",  "patient.jackson@email.com",  "Oliver",  "Jackson",  date(1978, 9, 14),  "555-0107"),
            ("sample_pt_white",    "patient.white@email.com",    "Ava",     "White",    date(2010, 12, 20), "555-0108"),
            ("sample_pt_harris",   "patient.harris@email.com",   "Liam",    "Harris",   date(1965, 7, 3),   "555-0109"),
            ("sample_pt_martin",   "patient.martin@email.com",   "Nora",    "Martin",   date(1993, 2, 28),  "555-0110"),
        ]

        self.admins, self.doctors, self.nurses, self.patients = [], [], [], []

        for uname, email, first, last in admins_data:
            u, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(email=email, first_name=first, last_name=last,
                              role=self.roles["admin"], is_verified=True,
                              phone="555-0001", address="123 Hospital Drive, Springfield"),
            )
            if created:
                u.set_password(PASSWORD)
                u.save()
            UserProfile.objects.get_or_create(user=u, defaults={"department": "Administration"})
            self.admins.append(u)

        for uname, email, first, last, spec, emp_id in doctors_data:
            u, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(email=email, first_name=first, last_name=last,
                              role=self.roles["doctor"], is_verified=True,
                              phone=f"555-{random.randint(1000,9999)}",
                              address="456 Medical Center Blvd, Springfield"),
            )
            if created:
                u.set_password(PASSWORD)
                u.save()
            UserProfile.objects.get_or_create(
                user=u,
                defaults={"employee_id": emp_id, "department": spec, "specialization": spec},
            )
            self.doctors.append(u)

        for uname, email, first, last, dept, emp_id in nurses_data:
            u, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(email=email, first_name=first, last_name=last,
                              role=self.roles["nurse"], is_verified=True,
                              phone=f"555-{random.randint(1000,9999)}",
                              address="789 Nursing Ave, Springfield"),
            )
            if created:
                u.set_password(PASSWORD)
                u.save()
            UserProfile.objects.get_or_create(
                user=u,
                defaults={"employee_id": emp_id, "department": dept},
            )
            self.nurses.append(u)

        for uname, email, first, last, dob, phone in patients_data:
            u, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(email=email, first_name=first, last_name=last,
                              role=self.roles["patient"], is_verified=True,
                              date_of_birth=dob, phone=phone,
                              address=f"{random.randint(1,999)} Main St, Springfield"),
            )
            if created:
                u.set_password(PASSWORD)
                u.save()
            blood_types = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
            UserProfile.objects.get_or_create(
                user=u,
                defaults={
                    "blood_type": random.choice(blood_types),
                    "emergency_contact_name": f"Contact for {first}",
                    "emergency_contact_phone": f"555-{random.randint(1000,9999)}",
                    "allergies": random.choice(["", "Penicillin", "Sulfa drugs", "Latex", "None known"]),
                },
            )
            self.patients.append(u)

        self.stdout.write(f"  ✓ Users: {len(self.admins)} admins, {len(self.doctors)} doctors, "
                         f"{len(self.nurses)} nurses, {len(self.patients)} patients")

    # ------------------------------------------------------------------ #
    #  APPOINTMENT TYPES                                                   #
    # ------------------------------------------------------------------ #
    def seed_appointment_types(self):
        from appointments.models import AppointmentType
        types_data = [
            ("consultation",    "Initial or follow-up consultation with a doctor",       30, "#4361ee"),
            ("follow_up",       "Follow-up visit after treatment or procedure",          20, "#7209b7"),
            ("emergency",       "Emergency medical consultation",                        60, "#dc3545"),
            ("telemedicine",    "Remote video consultation",                             30, "#06d6a0"),
            ("routine_checkup", "Annual physical exam and wellness check",               45, "#118ab2"),
            ("specialist",      "Specialist referral visit",                             45, "#e9c46a"),
        ]
        self.appt_types = {}
        for name, desc, dur, color in types_data:
            at, _ = AppointmentType.objects.get_or_create(
                name=name,
                defaults={"description": desc, "duration_minutes": dur, "color_code": color},
            )
            self.appt_types[name] = at
        self.stdout.write(f"  ✓ Appointment types: {len(self.appt_types)}")

    # ------------------------------------------------------------------ #
    #  MEDICATION DATABASE                                                 #
    # ------------------------------------------------------------------ #
    def seed_medication_database(self):
        from prescriptions.models import MedicationDatabase
        meds_data = [
            # (ndc_code, generic_name, brand_name, strength, dosage_form, drug_class, route, fda_approved, requires_rx)
            ("00071-0155-23", "Lisinopril",       "Prinivil",   "10mg",   "tablet", "antihypertensive", "oral", True, True),
            ("00071-0156-23", "Lisinopril",       "Prinivil",   "20mg",   "tablet", "antihypertensive", "oral", True, True),
            ("00003-0892-23", "Metformin",        "Glucophage", "500mg",  "tablet", "antidiabetic",     "oral", True, True),
            ("00003-0893-23", "Metformin",        "Glucophage", "1000mg", "tablet", "antidiabetic",     "oral", True, True),
            ("00093-0734-01", "Atorvastatin",     "Lipitor",    "20mg",   "tablet", "other",            "oral", True, True),
            ("00093-0735-01", "Atorvastatin",     "Lipitor",    "40mg",   "tablet", "other",            "oral", True, True),
            ("00054-0018-25", "Metoprolol",       "Lopressor",  "25mg",   "tablet", "antihypertensive", "oral", True, True),
            ("00054-0019-25", "Metoprolol",       "Lopressor",  "50mg",   "tablet", "antihypertensive", "oral", True, True),
            ("00006-0012-31", "Omeprazole",       "Prilosec",   "20mg",   "capsule","other",            "oral", True, False),
            ("00006-0013-31", "Omeprazole",       "Prilosec",   "40mg",   "capsule","other",            "oral", True, True),
            ("00069-0305-41", "Amoxicillin",      "Amoxil",     "500mg",  "capsule","antibiotic",       "oral", True, True),
            ("00069-0306-41", "Amoxicillin",      "Amoxil",     "875mg",  "tablet", "antibiotic",       "oral", True, True),
            ("00085-1101-01", "Sertraline",       "Zoloft",     "50mg",   "tablet", "antidepressant",   "oral", True, True),
            ("00085-1102-01", "Sertraline",       "Zoloft",     "100mg",  "tablet", "antidepressant",   "oral", True, True),
            ("00074-3777-60", "Levothyroxine",    "Synthroid",  "50mcg",  "tablet", "other",            "oral", True, True),
            ("00074-3778-60", "Levothyroxine",    "Synthroid",  "100mcg", "tablet", "other",            "oral", True, True),
            ("00006-0135-28", "Amlodipine",       "Norvasc",    "5mg",    "tablet", "antihypertensive", "oral", True, True),
            ("00006-0136-28", "Amlodipine",       "Norvasc",    "10mg",   "tablet", "antihypertensive", "oral", True, True),
            ("00054-0443-25", "Prednisone",       "Deltasone",  "5mg",    "tablet", "steroid",          "oral", True, True),
            ("00054-0444-25", "Prednisone",       "Deltasone",  "20mg",   "tablet", "steroid",          "oral", True, True),
            ("00781-1712-92", "Albuterol",        "ProAir HFA", "90mcg",  "inhaler","bronchodilator",   "inhalation", True, True),
            ("51672-4098-2",  "Ibuprofen",        "Advil",      "200mg",  "tablet", "analgesic",        "oral", True, False),
            ("00904-5898-61", "Acetaminophen",    "Tylenol",    "500mg",  "tablet", "analgesic",        "oral", True, False),
            ("00378-0023-91", "Warfarin",         "Coumadin",   "5mg",    "tablet", "anticoagulant",    "oral", True, True),
            ("00093-0322-01", "Cetirizine",       "Zyrtec",     "10mg",   "tablet", "antihistamine",    "oral", True, False),
            ("00006-0742-44", "Pantoprazole",     "Protonix",   "40mg",   "tablet", "other",            "oral", True, True),
            ("00781-5077-01", "Hydrochlorothiazide","HydroDIURIL","25mg",  "tablet", "diuretic",        "oral", True, True),
            ("51079-0940-20", "Gabapentin",       "Neurontin",  "300mg",  "capsule","analgesic",        "oral", True, True),
            ("00003-0147-23", "Losartan",         "Cozaar",     "50mg",   "tablet", "antihypertensive", "oral", True, True),
            ("00006-0117-54", "Vitamin D3",       "D-Vita",     "1000IU", "tablet", "vitamin",          "oral", True, False),
        ]
        self.medications = []
        for row in meds_data:
            ndc, generic, brand, strength, form, drug_class, route, fda, rx = row
            med, _ = MedicationDatabase.objects.get_or_create(
                ndc_code=ndc,
                defaults=dict(
                    generic_name=generic, brand_name=brand, strength=strength,
                    dosage_form=form, drug_class=drug_class, route_of_administration=route,
                    fda_approved=fda, requires_prescription=rx,
                    otc_available=not rx, is_active=True,
                ),
            )
            self.medications.append(med)
        self.stdout.write(f"  ✓ Medications: {len(self.medications)}")

    # ------------------------------------------------------------------ #
    #  PHARMACIES                                                          #
    # ------------------------------------------------------------------ #
    def seed_pharmacies(self):
        from prescriptions.models import Pharmacy
        pharmacies_data = [
            ("CareRx Pharmacy",        "retail",      "1234567", "555-7001", "101 Main St",         "Springfield",  "IL", "62701"),
            ("MedPlus Drugstore",       "retail",      "2345678", "555-7002", "202 Oak Ave",          "Springfield",  "IL", "62702"),
            ("HealthSphere Hospital Rx","hospital",    "3456789", "555-7003", "1 Hospital Dr",        "Springfield",  "IL", "62703"),
            ("QuickFill Mail Order",    "mail_order",  "4567890", "555-7004", "300 Commerce Blvd",    "Chicago",      "IL", "60601"),
            ("Specialty Meds Plus",     "specialty",   "5678901", "555-7005", "400 Medical Park",     "Decatur",      "IL", "62521"),
        ]
        self.pharmacies = []
        for name, ptype, ncpdp, phone, addr, city, state, zipcode in pharmacies_data:
            ph, _ = Pharmacy.objects.get_or_create(
                ncpdp_id=ncpdp,
                defaults=dict(
                    name=name, pharmacy_type=ptype, phone=phone,
                    address_line_1=addr, city=city, state=state, zip_code=zipcode,
                    accepts_electronic_prescriptions=True, is_active=True,
                    is_preferred_network=ptype in ("retail", "hospital"),
                ),
            )
            self.pharmacies.append(ph)
        self.stdout.write(f"  ✓ Pharmacies: {len(self.pharmacies)}")

    # ------------------------------------------------------------------ #
    #  PATIENT PROFILES                                                    #
    # ------------------------------------------------------------------ #
    def seed_patient_profiles(self):
        from patient_portal.models import PatientProfile
        insurance_types = ["private", "public", "medicare", "medicaid", "none"]
        ins_providers = ["BlueCross BlueShield", "Aetna", "Cigna", "UnitedHealth", "Humana", ""]
        mrn_counter = 100001
        self.patient_profiles = []
        for i, patient in enumerate(self.patients):
            pp, _ = PatientProfile.objects.get_or_create(
                user=patient,
                defaults=dict(
                    primary_doctor=self.doctors[i % len(self.doctors)],
                    medical_record_number=f"MRN-{mrn_counter + i}",
                    insurance_type=insurance_types[i % len(insurance_types)],
                    insurance_provider=ins_providers[i % len(ins_providers)],
                    insurance_policy_number=f"POL-{random.randint(100000, 999999)}",
                    preferred_pharmacy=str(self.pharmacies[i % len(self.pharmacies)].name),
                    communication_preference=random.choice(["email", "phone", "sms", "portal"]),
                    consent_to_research=random.choice([True, False]),
                ),
            )
            self.patient_profiles.append(pp)
        self.stdout.write(f"  ✓ Patient profiles: {len(self.patient_profiles)}")

    # ------------------------------------------------------------------ #
    #  DOCTOR SCHEDULES                                                    #
    # ------------------------------------------------------------------ #
    def seed_doctor_schedules(self):
        from appointments.models import DoctorSchedule
        count = 0
        for doctor in self.doctors:
            # Each doctor works Mon-Fri
            for day in range(5):
                _, created = DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    day_of_week=day,
                    defaults=dict(
                        start_time=time(8, 0),
                        end_time=time(17, 0),
                        break_start_time=time(12, 0),
                        break_end_time=time(13, 0),
                        is_active=True,
                        max_appointments=20,
                    ),
                )
                if created:
                    count += 1
        self.stdout.write(f"  ✓ Doctor schedules: {count}")

    # ------------------------------------------------------------------ #
    #  VITAL RECORDS                                                       #
    # ------------------------------------------------------------------ #
    def seed_vital_records(self):
        from clinical_portal.models import VitalRecord
        count = 0
        now = timezone.now()
        for patient in self.patients:
            nurse = random.choice(self.nurses)
            # 6 vital readings per patient over the last 3 months
            for i in range(6):
                days_ago = random.randint(1, 90)
                VitalRecord.objects.create(
                    patient=patient,
                    recorded_by=nurse,
                    temperature=round(random.uniform(36.0, 37.8), 1),
                    blood_pressure_systolic=random.randint(108, 145),
                    blood_pressure_diastolic=random.randint(65, 95),
                    heart_rate=random.randint(58, 100),
                    respiratory_rate=random.randint(14, 20),
                    oxygen_saturation=random.randint(95, 100),
                    weight=round(random.uniform(50, 110), 2),
                    height=round(random.uniform(150, 195), 2),
                    blood_glucose=random.randint(70, 140),
                    pain_level=random.randint(0, 4),
                    notes="Routine vital signs recording.",
                    recorded_at=now - timedelta(days=days_ago),
                )
                count += 1
        self.stdout.write(f"  ✓ Vital records: {count}")

    # ------------------------------------------------------------------ #
    #  MEDICAL RECORDS                                                     #
    # ------------------------------------------------------------------ #
    def seed_medical_records(self):
        from clinical_portal.models import MedicalRecord
        records_data = [
            ("consultation", "Initial Cardiology Consultation",
             "Patient presented with chest tightness and shortness of breath. "
             "ECG performed; mild ST changes noted. Referred for stress echocardiogram.", "medium", "I25.10"),
            ("diagnosis", "Type 2 Diabetes Mellitus Diagnosis",
             "HbA1c: 7.8%. Fasting glucose: 145 mg/dL. Diagnosed with T2DM. "
             "Started on Metformin 500 mg twice daily. Diet and lifestyle counselling provided.", "medium", "E11.9"),
            ("lab_result", "Comprehensive Metabolic Panel",
             "Na: 138, K: 4.1, Cl: 102, CO2: 24, BUN: 18, Creatinine: 1.0, "
             "Glucose: 128, ALT: 32, AST: 28. Results within normal range.", "low", ""),
            ("progress", "Follow-up: Hypertension Management",
             "BP today: 132/84 mmHg. Patient tolerating Lisinopril well. "
             "No adverse effects reported. Continue current medication regimen.", "low", "I10"),
            ("imaging", "Chest X-Ray Report",
             "No acute cardiopulmonary process. Lungs clear bilaterally. "
             "Heart size normal. No pleural effusion or pneumothorax.", "low", ""),
            ("procedure", "Knee Arthroscopy Note",
             "Arthroscopic partial meniscectomy performed on right knee. "
             "Meniscal tear confirmed and trimmed. Patient tolerated procedure well.", "high", "M23.200"),
            ("diagnosis", "Major Depressive Disorder",
             "Patient meets DSM-5 criteria for MDD. PHQ-9 score: 16. "
             "Started Sertraline 50 mg daily. Referral to psychology provided.", "medium", "F32.1"),
            ("consultation", "Oncology Consultation – Breast Mass",
             "Palpable 1.5 cm mass in the left upper outer quadrant. "
             "Biopsy scheduled. Pending pathology results.", "high", "N63"),
            ("lab_result", "Thyroid Function Test",
             "TSH: 6.8 mIU/L (↑ High). Free T4: 0.9 ng/dL. "
             "Consistent with subclinical hypothyroidism. Started Levothyroxine 50 mcg.", "medium", "E03.9"),
            ("discharge", "Discharge Summary – Pneumonia",
             "Patient admitted 5 days ago with community-acquired pneumonia. "
             "Treated with IV antibiotics. Improved clinically. Discharged on oral Amoxicillin.", "high", "J18.9"),
        ]
        count = 0
        for i, patient in enumerate(self.patients):
            doctor = self.doctors[i % len(self.doctors)]
            rec_type, title, desc, severity, icd = records_data[i % len(records_data)]
            MedicalRecord.objects.create(
                patient=patient,
                created_by=doctor,
                record_type=rec_type,
                title=title,
                description=desc,
                severity=severity,
                diagnosis_code=icd,
                ai_risk_score=round(random.uniform(5, 75), 1),
                ai_recommendations="Continue monitoring. Follow-up in 4 weeks.",
                record_date=timezone.now() - timedelta(days=random.randint(5, 120)),
            )
            count += 1
        self.stdout.write(f"  ✓ Medical records: {count}")

    # ------------------------------------------------------------------ #
    #  TREATMENT PLANS                                                     #
    # ------------------------------------------------------------------ #
    def seed_treatment_plans(self):
        from clinical_portal.models import TreatmentPlan
        plans_data = [
            ("Hypertension Management Plan",
             "Comprehensive 6-month plan for blood pressure control.",
             "Essential Hypertension (I10)",
             "Lisinopril 10 mg daily; Amlodipine 5 mg daily",
             "Monthly BP checks; renal function at 3 months",
             "DASH diet; reduce sodium to <2g/day; 30 min aerobic exercise 5x/week",
             "Follow-up in 4 weeks; adjust medications if BP consistently >140/90",
             "active", 180),
            ("Type 2 Diabetes Management",
             "12-month diabetes management with lifestyle modification.",
             "Type 2 Diabetes Mellitus (E11.9)",
             "Metformin 500 mg twice daily with meals",
             "HbA1c every 3 months; annual foot exam; annual eye exam",
             "Low-carbohydrate diet; weight loss 5-10%; daily blood glucose monitoring",
             "Endocrinology referral at 3 months if HbA1c not at goal (<7%)",
             "active", 365),
            ("Post-Operative Knee Rehabilitation",
             "8-week rehabilitation following arthroscopic knee surgery.",
             "Medial Meniscal Tear (M23.200)",
             "Ibuprofen 400 mg as needed for pain; Ice 20 min QID",
             "Physiotherapy 3x/week; Range of motion exercises daily",
             "Rest, Ice, Compression, Elevation; avoid high-impact activities for 6 weeks",
             "Orthopaedic follow-up at 2 weeks; physiotherapy progress review at 4 weeks",
             "active", 56),
            ("Depression Treatment Plan",
             "Evidence-based treatment for Major Depressive Disorder.",
             "Major Depressive Disorder (F32.1)",
             "Sertraline 50 mg daily; titrate to 100 mg at week 4 if tolerated",
             "Weekly mood diary; PHQ-9 monthly",
             "Regular sleep schedule; daily physical activity; social engagement",
             "Psychiatry review at 4 weeks; crisis line info provided",
             "active", 180),
            ("Hypothyroid Management",
             "Long-term thyroid hormone replacement therapy.",
             "Subclinical Hypothyroidism (E03.9)",
             "Levothyroxine 50 mcg daily on empty stomach",
             "TSH at 6 weeks; then annually; take medication consistently",
             "Take medication at same time daily; avoid calcium/iron supplements within 4h",
             "Endocrinology follow-up in 6 weeks",
             "active", 365),
        ]
        count = 0
        for i, patient in enumerate(self.patients[:5]):
            doctor = self.doctors[i % len(self.doctors)]
            title, desc, diag, meds, procs, lifestyle, fu, status, duration = plans_data[i]
            start = date.today() - timedelta(days=random.randint(10, 60))
            TreatmentPlan.objects.create(
                patient=patient,
                created_by=doctor,
                title=title,
                description=desc,
                diagnosis=diag,
                medications=meds,
                procedures=procs,
                lifestyle_recommendations=lifestyle,
                follow_up_instructions=fu,
                status=status,
                start_date=start,
                end_date=start + timedelta(days=duration),
                next_review_date=start + timedelta(days=28),
            )
            count += 1
        self.stdout.write(f"  ✓ Treatment plans: {count}")

    # ------------------------------------------------------------------ #
    #  APPOINTMENTS                                                        #
    # ------------------------------------------------------------------ #
    def seed_appointments(self):
        from appointments.models import Appointment
        count = 0
        today = date.today()

        statuses_past = ["completed", "completed", "completed", "no_show", "cancelled"]
        statuses_future = ["confirmed", "confirmed", "requested", "requested"]

        past_appt_ids = []

        def _next_weekday(d):
            """Return d if weekday, else advance to Monday."""
            while d.weekday() >= 5:
                d += timedelta(days=1)
            return d

        # --- Past appointments: create with a near-future date, then update ---
        temp_future = _next_weekday(today + timedelta(days=7))
        for patient in self.patients:
            for _ in range(random.randint(3, 5)):
                doctor = random.choice(self.doctors)
                appt_type = random.choice(list(self.appt_types.values()))
                hour = random.randint(9, 16)
                appt_time = time(hour, random.choice([0, 30]))
                try:
                    appt = Appointment.objects.create(
                        patient=patient,
                        doctor=doctor,
                        appointment_type=appt_type,
                        scheduled_date=temp_future,  # valid future date
                        scheduled_time=appt_time,
                        duration_minutes=appt_type.duration_minutes,
                        status="confirmed",  # valid status at creation
                        reason=random.choice([
                            "Routine checkup and medication review",
                            "Follow-up for hypertension management",
                            "Chest pain evaluation",
                            "Diabetes monitoring and HbA1c review",
                            "Annual physical examination",
                        ]),
                        notes="Patient arrived on time. No acute distress.",
                        doctor_notes="Assessment completed. Medications adjusted.",
                        is_telemedicine=appt_type.name == "telemedicine",
                    )
                    past_appt_ids.append((
                        appt.pk,
                        today - timedelta(days=random.randint(1, 90)),
                        random.choice(statuses_past),
                    ))
                    count += 1
                except Exception:
                    pass

        # Now bulk-update past appointments to their real past dates
        for pk, past_date, status in past_appt_ids:
            past_date = _next_weekday(past_date)
            Appointment.objects.filter(pk=pk).update(
                scheduled_date=past_date,
                status=status,
            )

        # --- Future appointments ---
        for patient in self.patients:
            for _ in range(random.randint(1, 3)):
                doctor = random.choice(self.doctors)
                appt_type = random.choice(list(self.appt_types.values()))
                days_ahead = random.randint(3, 45)
                appt_date = _next_weekday(today + timedelta(days=days_ahead))
                hour = random.randint(9, 16)
                appt_time = time(hour, random.choice([0, 30]))
                try:
                    Appointment.objects.create(
                        patient=patient,
                        doctor=doctor,
                        appointment_type=appt_type,
                        scheduled_date=appt_date,
                        scheduled_time=appt_time,
                        duration_minutes=appt_type.duration_minutes,
                        status=random.choice(statuses_future),
                        reason=random.choice([
                            "Follow-up consultation",
                            "Quarterly diabetes review",
                            "Blood pressure monitoring",
                            "Annual wellness checkup",
                            "Specialist referral",
                        ]),
                        is_telemedicine=appt_type.name == "telemedicine",
                        send_reminder=True,
                    )
                    count += 1
                except Exception:
                    pass

        self.stdout.write(f"  ✓ Appointments: {count}")

    # ------------------------------------------------------------------ #
    #  PRESCRIPTIONS                                                       #
    # ------------------------------------------------------------------ #
    def seed_prescriptions(self):
        from prescriptions.models import Prescription
        count = 0
        now = timezone.now()

        common_prescriptions = [
            # (med_index, dosage, qty, days_supply, refills, diag_code, diag_desc, indication, status)
            (0, "Take 1 tablet once daily in the morning",                    30,  30, 5, "I10",   "Hypertension",             "Blood pressure control",             "filled"),
            (2, "Take 1 tablet twice daily with meals",                       60,  30, 5, "E11.9", "Type 2 Diabetes",          "Glycemic control",                   "filled"),
            (4, "Take 1 tablet once daily at bedtime",                        30,  30, 5, "E78.5", "Hyperlipidemia",           "Cholesterol management",             "filled"),
            (6, "Take 1 tablet twice daily",                                  60,  30, 5, "I10",   "Hypertension",             "Heart rate and BP control",          "filled"),
            (8, "Take 1 capsule once daily before breakfast",                 30,  30, 2, "K21.0", "GERD",                     "Acid suppression",                   "filled"),
            (10,"Take 1 capsule three times daily with food",                 21,   7, 0, "J06.9", "Upper respiratory tract inf","Bacterial infection treatment",      "filled"),
            (12,"Take 1 tablet once daily in the morning",                    30,  30, 3, "F32.1", "Major Depressive Disorder","Depression management",              "filled"),
            (14,"Take 1 tablet once daily on empty stomach",                  30,  30, 5, "E03.9", "Hypothyroidism",           "Thyroid hormone replacement",        "filled"),
            (16,"Take 1 tablet once daily",                                   30,  30, 5, "I10",   "Hypertension",             "Calcium channel blockade for BP",    "transmitted"),
            (20,"2 puffs inhaled every 4-6 hours as needed for shortness of breath", 1, 30, 2, "J45.30","Asthma","Bronchospasm relief",                 "approved"),
        ]

        for i, patient in enumerate(self.patients):
            doctor = self.doctors[i % len(self.doctors)]
            rx_info = common_prescriptions[i % len(common_prescriptions)]
            med_idx, dosage, qty, days, refills, icd, icd_desc, indication, status = rx_info
            med = self.medications[med_idx]
            pharmacy = self.pharmacies[i % len(self.pharmacies)]
            rx_num = f"RX{random.randint(1000000, 9999999)}"
            effective = now - timedelta(days=random.randint(1, 60))
            try:
                Prescription.objects.create(
                    patient=patient,
                    prescriber=doctor,
                    medication=med,
                    dosage_instructions=dosage,
                    quantity=qty,
                    days_supply=days,
                    refills_authorized=refills,
                    refills_used=random.randint(0, min(refills, 2)),
                    diagnosis_code=icd,
                    diagnosis_description=icd_desc,
                    indication=indication,
                    status=status,
                    priority="routine",
                    effective_date=effective,
                    expiration_date=effective + timedelta(days=365),
                    rx_number=rx_num,
                    pharmacy=pharmacy,
                    allergy_checked=True,
                    interaction_checked=True,
                    duplicate_therapy_checked=True,
                    electronically_signed=True,
                    signature_timestamp=effective,
                    patient_instructions=f"Take as directed. Contact us if you experience side effects.",
                )
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipping prescription: {e}"))

        self.stdout.write(f"  ✓ Prescriptions: {count}")

    # ------------------------------------------------------------------ #
    #  HEALTH METRICS (Patient self-reported)                             #
    # ------------------------------------------------------------------ #
    def seed_health_metrics(self):
        from patient_portal.models import HealthMetric
        count = 0
        now = timezone.now()

        metrics_config = [
            ("weight",         70.0,  110.0, None,  None,  "kg"),
            ("heart_rate",     60.0,  100.0, None,  None,  "bpm"),
            ("blood_glucose",  80.0,  150.0, None,  None,  "mg/dL"),
            ("temperature",    36.2,  37.5,  None,  None,  "°C"),
            ("steps",          3000,  12000, None,  None,  "steps"),
            ("sleep_hours",    5.0,   9.0,   None,  None,  "hours"),
            ("blood_pressure", 110.0, 140.0, 65.0,  95.0,  "mmHg"),
            ("mood",           4.0,   9.0,   None,  None,  "1-10"),
            ("water_intake",   1.0,   3.5,   None,  None,  "L"),
            ("exercise_minutes",15.0, 90.0,  None,  None,  "min"),
        ]

        for patient in self.patients:
            # 30 days of data for a few metrics
            for metric_type, val_min, val_max, sec_min, sec_max, unit in metrics_config[:5]:
                for days_ago in range(0, 30, 3):
                    value = round(random.uniform(val_min, val_max), 2)
                    secondary = round(random.uniform(sec_min, sec_max), 2) if sec_min else None
                    HealthMetric.objects.create(
                        patient=patient,
                        metric_type=metric_type,
                        value=value,
                        secondary_value=secondary,
                        unit=unit,
                        source=random.choice(["manual", "device"]),
                        recorded_at=now - timedelta(days=days_ago),
                    )
                    count += 1

        self.stdout.write(f"  ✓ Health metrics: {count}")

    # ------------------------------------------------------------------ #
    #  ANALYTICS                                                           #
    # ------------------------------------------------------------------ #
    def seed_analytics(self):
        from analytics.models import (
            PredictiveModel, PatientFlowPrediction,
            ClinicalOutcomePrediction, AnalyticsReport,
        )
        now = timezone.now()
        admin = self.admins[0]

        # --- Predictive Models ---
        models_data = [
            ("Patient Flow Predictor v2",      "patient_flow",       "random_forest",      "2.0.0", 0.89, 0.87, 0.91, 0.89),
            ("Readmission Risk Model",         "readmission_risk",   "gradient_boosting",  "1.3.0", 0.84, 0.82, 0.85, 0.83),
            ("Bed Occupancy Forecaster",       "bed_occupancy",      "time_series",        "1.1.0", 0.91, 0.90, 0.92, 0.91),
            ("Clinical Outcome Predictor",     "clinical_outcome",   "neural_network",     "3.0.0", 0.86, 0.85, 0.87, 0.86),
            ("Length of Stay Model",           "length_of_stay",     "ensemble",           "1.0.0", 0.79, 0.78, 0.80, 0.79),
            ("Staff Optimization Engine",      "staff_optimization", "clustering",         "1.2.0", 0.88, 0.87, 0.90, 0.88),
        ]
        self.pred_models = []
        for name, mtype, algo, ver, acc, prec, rec, f1 in models_data:
            pm, _ = PredictiveModel.objects.get_or_create(
                name=name, version=ver,
                defaults=dict(
                    model_type=mtype, algorithm=algo,
                    accuracy=acc, precision=prec, recall=rec, f1_score=f1,
                    is_active=True, is_production_ready=True,
                    description=f"Production-ready {mtype.replace('_', ' ')} model.",
                    created_by=admin,
                    parameters={"n_estimators": 200, "max_depth": 10, "learning_rate": 0.05},
                    training_data_summary={"records": random.randint(50000, 200000), "features": random.randint(40, 120)},
                ),
            )
            self.pred_models.append(pm)
        self.stdout.write(f"  ✓ Predictive models: {len(self.pred_models)}")

        # --- Patient Flow Predictions ---
        departments = ["emergency", "icu", "general_ward", "surgery", "cardiology", "outpatient"]
        horizons = ["24_hours", "48_hours", "7_days"]
        flow_count = 0
        flow_model = self.pred_models[0]
        for dept in departments:
            for h in horizons:
                for day_offset in range(-7, 8):
                    target = now + timedelta(days=day_offset)
                    occupancy = random.randint(20, 60)
                    util = round(occupancy / 60, 2)
                    PatientFlowPrediction.objects.create(
                        model=flow_model,
                        prediction_date=now,
                        prediction_horizon=h,
                        target_date=target,
                        department=dept,
                        predicted_admissions=random.randint(5, 30),
                        predicted_discharges=random.randint(5, 25),
                        predicted_bed_occupancy=occupancy,
                        predicted_capacity_utilization=util,
                        confidence_score=round(random.uniform(0.80, 0.96), 2),
                        predicted_staff_needed={"doctors": random.randint(3, 10), "nurses": random.randint(5, 20)},
                    )
                    flow_count += 1
        self.stdout.write(f"  ✓ Patient flow predictions: {flow_count}")

        # --- Clinical Outcome Predictions ---
        outcome_model = self.pred_models[3]
        risk_levels = ["low", "low", "moderate", "high", "critical"]
        outcome_types = ["readmission_risk", "mortality_risk", "complication_risk", "length_of_stay"]
        outcome_count = 0
        for patient in self.patients:
            for outcome_type in outcome_types[:2]:
                risk_level = random.choice(risk_levels)
                risk_score_map = {"low": (0.0, 0.25), "moderate": (0.25, 0.55), "high": (0.55, 0.75), "critical": (0.75, 1.0)}
                lo, hi = risk_score_map[risk_level]
                ClinicalOutcomePrediction.objects.create(
                    model=outcome_model,
                    patient=patient,
                    outcome_type=outcome_type,
                    risk_level=risk_level,
                    risk_score=round(random.uniform(lo, hi), 3),
                    prediction_horizon_days=30,
                    confidence_score=round(random.uniform(0.78, 0.95), 2),
                    risk_factors=["Age > 65", "Hypertension", "Diabetes"] if risk_level in ("high", "critical") else ["Mild hypertension"],
                    protective_factors=["Regular exercise", "Medication adherence"],
                    recommended_interventions=["Increase monitoring frequency", "Schedule follow-up within 2 weeks"],
                    explanation=f"Patient has {risk_level} risk of {outcome_type.replace('_', ' ')}.",
                )
                outcome_count += 1
        self.stdout.write(f"  ✓ Clinical outcome predictions: {outcome_count}")

        # --- Analytics Reports ---
        report_types = [
            ("Monthly Patient Flow Report", "patient_flow", "monthly"),
            ("Weekly Resource Utilization", "resource_utilization", "weekly"),
            ("Quality Metrics Dashboard",   "quality_metrics",      "daily"),
            ("Financial Performance Q1",    "financial_analytics",  "quarterly"),
            ("Operational KPIs – February", "operational_kpis",     "monthly"),
        ]
        for name, rtype, freq in report_types:
            period_end = now
            period_start = now - timedelta(days=30 if freq == "monthly" else 7 if freq == "weekly" else 1)
            AnalyticsReport.objects.create(
                name=name,
                report_type=rtype,
                frequency=freq,
                report_date=now,
                period_start=period_start,
                period_end=period_end,
                generated_by=admin,
                status="completed",
                is_scheduled=freq != "ad_hoc",
                data={
                    "total_patients": random.randint(200, 500),
                    "total_appointments": random.randint(500, 1500),
                    "avg_wait_time_min": random.randint(10, 45),
                    "bed_occupancy_rate": round(random.uniform(0.65, 0.92), 2),
                    "patient_satisfaction": round(random.uniform(4.1, 4.9), 1),
                    "readmission_rate": round(random.uniform(0.05, 0.12), 3),
                },
                kpis={
                    "appointments_completed": random.randint(300, 800),
                    "new_patients": random.randint(30, 150),
                    "prescriptions_issued": random.randint(200, 600),
                    "avg_los_days": round(random.uniform(2.5, 5.0), 1),
                },
            )
        self.stdout.write(f"  ✓ Analytics reports: {len(report_types)}")
