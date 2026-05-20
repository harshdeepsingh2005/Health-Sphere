"""
HealthSphere AI — Seed Demo Data
=================================
Creates a rich, realistic dataset:
  • 1  superadmin
  • 5  doctors        (with specialisations)
  • 10 nurses
  • 60 patients       (each with profile, vitals, medical records, treatment plans, admissions)

Usage:
    python manage.py seed_demo_data [--flush]

Flags:
    --flush    Delete ALL existing users first (default: True)
"""

import random
from datetime import timedelta, date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User, Role, UserProfile
from clinical_portal.models import MedicalRecord, TreatmentPlan, VitalRecord
from admin_portal.models import AdmissionRecord


# ─── Static data pools ───────────────────────────────────────────────────────

DOCTORS = [
    {"first": "Arjun",    "last": "Mehta",     "email": "arjun.mehta@healthsphere.hospital",    "spec": "Cardiology",        "dept": "Cardiology",       "emp": "DOC-001"},
    {"first": "Priya",    "last": "Sharma",    "email": "priya.sharma@healthsphere.hospital",   "spec": "Neurology",         "dept": "Neurology",        "emp": "DOC-002"},
    {"first": "Rohan",    "last": "Kapoor",    "email": "rohan.kapoor@healthsphere.hospital",   "spec": "Orthopedics",       "dept": "Orthopedics",      "emp": "DOC-003"},
    {"first": "Sneha",    "last": "Joshi",     "email": "sneha.joshi@healthsphere.hospital",    "spec": "Endocrinology",     "dept": "Internal Medicine","emp": "DOC-004"},
    {"first": "Vikram",   "last": "Singh",     "email": "vikram.singh@healthsphere.hospital",   "spec": "Emergency Medicine","dept": "Emergency",        "emp": "DOC-005"},
]

NURSES = [
    {"first": "Anita",    "last": "Pillai",    "email": "anita.pillai@healthsphere.hospital",   "dept": "Cardiology",    "emp": "NRS-001"},
    {"first": "Kiran",    "last": "Rao",       "email": "kiran.rao@healthsphere.hospital",       "dept": "Neurology",     "emp": "NRS-002"},
    {"first": "Sunita",   "last": "Verma",     "email": "sunita.verma@healthsphere.hospital",   "dept": "Orthopedics",   "emp": "NRS-003"},
    {"first": "Megha",    "last": "Nair",      "email": "megha.nair@healthsphere.hospital",      "dept": "ICU",           "emp": "NRS-004"},
    {"first": "Deepa",    "last": "Iyer",      "email": "deepa.iyer@healthsphere.hospital",      "dept": "Emergency",     "emp": "NRS-005"},
    {"first": "Pooja",    "last": "Bhat",      "email": "pooja.bhat@healthsphere.hospital",      "dept": "Emergency",     "emp": "NRS-006"},
    {"first": "Ritu",     "last": "Kulkarni",  "email": "ritu.kulkarni@healthsphere.hospital",  "dept": "Internal Medicine","emp": "NRS-007"},
    {"first": "Priyanka", "last": "Das",       "email": "priyanka.das@healthsphere.hospital",   "dept": "Oncology",      "emp": "NRS-008"},
    {"first": "Smita",    "last": "Ghosh",     "email": "smita.ghosh@healthsphere.hospital",    "dept": "Pediatrics",    "emp": "NRS-009"},
    {"first": "Kavita",   "last": "Mishra",    "email": "kavita.mishra@healthsphere.hospital",  "dept": "ICU",           "emp": "NRS-010"},
]

# 60 patients with realistic demographics
PATIENTS_RAW = [
    ("Rahul",      "Gupta",      "M", "1985-03-12", "O+",  "Penicillin",                  "Hypertension, Type 2 Diabetes"),
    ("Sunita",     "Bhatt",      "F", "1972-07-25", "A+",  "Sulfa drugs",                 "Asthma, GERD"),
    ("Aditya",     "Kumar",      "M", "1990-11-08", "B+",  "None",                        "Healthy"),
    ("Meena",      "Patel",      "F", "1968-01-30", "AB-", "Aspirin",                     "Arthritis, Osteoporosis"),
    ("Suresh",     "Reddy",      "M", "1955-06-14", "O-",  "Ibuprofen, Codeine",           "COPD, Heart failure"),
    ("Lakshmi",    "Krishnan",   "F", "1980-09-03", "A-",  "None",                        "Hypothyroidism"),
    ("Vishal",     "Mehta",      "M", "1975-04-22", "B-",  "Latex",                       "Hypertension, CKD Stage 3"),
    ("Nandini",    "Shah",       "F", "1993-12-17", "A+",  "ACE inhibitors",               "PCOS, Anxiety disorder"),
    ("Rajesh",     "Yadav",      "M", "1960-08-05", "O+",  "NSAIDs",                      "Diabetes, Retinopathy"),
    ("Kavya",      "Rao",        "F", "1998-02-28", "B+",  "None",                        "Migraine"),
    ("Deepak",     "Mishra",     "M", "1983-10-11", "AB+", "Penicillin",                  "Epilepsy"),
    ("Preethi",    "Nair",       "F", "1970-05-19", "O+",  "Morphine",                    "Breast cancer (remission)"),
    ("Sanjay",     "Jain",       "M", "1952-03-07", "A+",  "Warfarin interactions",        "Atrial fibrillation, HTN"),
    ("Rekha",      "Singh",      "F", "1987-07-14", "B+",  "None",                        "Lupus"),
    ("Vivek",      "Pillai",     "M", "1978-11-29", "O-",  "Sulfa drugs",                 "Chronic back pain"),
    ("Anjali",     "Sharma",     "F", "1962-04-08", "A-",  "Aspirin",                     "Rheumatoid arthritis, HTN"),
    ("Prakash",    "Iyer",       "M", "1950-09-23", "B+",  "Penicillin, NSAIDs",          "COPD, Type 2 Diabetes, CAD"),
    ("Divya",      "Menon",      "F", "1995-01-16", "AB+", "None",                        "Healthy"),
    ("Gopal",      "Krishnamurthy","M","1966-06-01", "O+", "Codeine",                     "Hypertension, Sleep apnea"),
    ("Usha",       "Verma",      "F", "1958-12-10", "A+",  "Aspirin",                     "Heart failure, CKD Stage 4"),
    ("Harish",     "Bose",       "M", "1988-08-27", "B-",  "None",                        "Type 1 Diabetes"),
    ("Shweta",     "Choudhury",  "F", "1974-03-31", "O+",  "Tetracycline",                "Migraine, PCOS"),
    ("Manoj",      "Tiwari",     "M", "1945-11-03", "A-",  "Morphine, Penicillin",        "Prostate cancer, Diabetes"),
    ("Radha",      "Aggarwal",   "F", "1980-07-19", "AB+", "None",                        "Pregnancy-induced HTN"),
    ("Nitin",      "Desai",      "M", "1992-05-26", "B+",  "NSAIDs",                      "Asthma"),
    ("Poonam",     "Malhotra",   "F", "1965-02-13", "O-",  "Sulfamethoxazole",            "SLE, HTN"),
    ("Arun",       "Pandey",     "M", "1971-10-07", "A+",  "None",                        "Hepatitis C"),
    ("Sarita",     "Gupta",      "F", "1956-04-25", "B+",  "Aspirin, Clopidogrel",        "CAD, Diabetes, Obesity"),
    ("Karthik",    "Rajan",      "M", "1996-09-12", "O+",  "None",                        "Sports injury (ligament tear)"),
    ("Meghna",     "Sinha",      "F", "1984-01-05", "A+",  "Latex",                       "Fibromyalgia, Depression"),
    ("Rajendra",   "Patil",      "M", "1948-07-30", "AB-", "Penicillin",                  "COPD, Pneumonia (recurrent)"),
    ("Smita",      "Joshi",      "F", "1977-03-18", "O+",  "None",                        "Hypothyroidism, Anxiety"),
    ("Venkat",     "Subramaniam","M", "1963-11-21", "B+",  "NSAIDs",                      "Gout, Hypertension"),
    ("Ananya",     "Banerjee",   "F", "1991-06-09", "A-",  "Penicillin",                  "Celiac disease"),
    ("Ramesh",     "Nayak",      "M", "1940-08-15", "O+",  "Multiple — see notes",        "Parkinson's, Hypertension, Diabetes"),
    ("Sudha",      "Pillai",     "F", "1969-12-04", "B-",  "Sulfa drugs",                 "Gallbladder disease, GERD"),
    ("Siddharth",  "Kapoor",     "M", "1999-04-22", "A+",  "None",                        "Anxiety disorder"),
    ("Kavitha",    "Mohan",      "F", "1973-09-16", "AB+", "Aspirin",                     "Type 2 Diabetes, Neuropathy"),
    ("Dilip",      "Saxena",     "M", "1957-02-28", "O-",  "Penicillin, Aspirin",         "Heart failure, Atrial fibrillation"),
    ("Archana",    "Tripathi",   "F", "1982-07-07", "A+",  "None",                        "Endometriosis, Anaemia"),
    ("Santosh",    "Ghosh",      "M", "1976-05-14", "B+",  "NSAIDs, Latex",               "Psoriasis, HTN"),
    ("Leela",      "Rao",        "F", "1961-10-29", "O+",  "Aspirin",                     "CKD Stage 3, Anemia"),
    ("Rohit",      "Chauhan",    "M", "1994-03-03", "A-",  "None",                        "Healthy — pre-op evaluation"),
    ("Geeta",      "Srivastava", "F", "1967-08-20", "AB+", "Tetracycline, Penicillin",    "Rheumatoid arthritis, Osteoporosis"),
    ("Ajit",       "Sawant",     "M", "1953-12-12", "B+",  "Morphine",                    "Lung cancer, COPD"),
    ("Nalini",     "Kumari",     "F", "1986-06-25", "O+",  "None",                        "Polycystic kidney disease"),
    ("Manish",     "Rathore",    "M", "1968-04-10", "A+",  "NSAIDs",                      "Hypertension, Hyperlipidaemia"),
    ("Asha",       "Dwivedi",    "F", "1959-01-23", "B-",  "Aspirin",                     "Stroke (ischaemic), HTN"),
    ("Kiran",      "Hegde",      "M", "1989-09-05", "O+",  "None",                        "Kidney stones"),
    ("Vandana",    "Kulkarni",   "F", "1978-11-18", "A+",  "Penicillin",                  "Thyroid cancer (post-op)"),
    ("Girish",     "Naik",       "M", "1944-07-01", "AB+", "Multiple — see notes",        "Alzheimer's, HTN, T2DM, Cardiac failure"),
    ("Revathi",    "Sundaram",   "F", "1990-02-14", "O-",  "None",                        "IBS, Anxiety"),
    ("Bhuvanesh",  "Kamath",     "M", "1972-05-27", "A-",  "NSAIDs, Penicillin",          "Tuberculosis"),
    ("Hema",       "Lal",        "F", "1964-10-08", "B+",  "Aspirin",                     "Ovarian cyst, PCOS"),
    ("Sunil",      "Bhattacharya","M","1981-03-14", "O+",  "None",                        "Appendicitis (post-op day 2)"),
    ("Jyothi",     "Varma",      "F", "1955-08-30", "A+",  "Latex, Ibuprofen",            "Chronic kidney disease, Dialysis"),
    ("Mohan",      "Pillai",     "M", "1970-06-17", "B+",  "None",                        "Hypertension, Sleep apnoea"),
    ("Sarala",     "Menon",      "F", "1948-12-24", "AB-", "Aspirin, Codeine",            "Osteoarthritis, Heart failure"),
    ("Praveen",    "Tiwari",     "M", "1998-04-06", "O+",  "None",                        "Road traffic accident — fractures"),
    ("Chandra",    "Babu",       "M", "1936-01-10", "A+",  "Multiple — see notes",        "COPD, T2DM, CKD, Cardiac failure — complex geriatric"),
    ("Lakshmi",    "Devi",       "F", "1975-07-22", "B-",  "Sulfa drugs",                 "Gestational diabetes"),
]

DIAGNOSIS_TITLES = [
    "Hypertensive Crisis", "Diabetic Ketoacidosis", "Acute Myocardial Infarction",
    "Pneumonia — Community Acquired", "Acute Ischaemic Stroke", "Sepsis — Urinary Source",
    "Asthma Exacerbation", "COPD Exacerbation", "Acute Appendicitis",
    "Compression Fracture — L2", "Bilateral Pulmonary Embolism", "Atrial Fibrillation — RVR",
    "Decompensated Heart Failure", "Acute Renal Failure", "Hepatic Encephalopathy",
    "Hypoglycaemic Episode", "Cellulitis — Lower Limb", "Urinary Tract Infection",
]

TREATMENT_TITLES = [
    "Antihypertensive Regimen",    "Insulin Optimisation Protocol",   "Post-MI Cardiac Rehab",
    "Pulmonary Physiotherapy",     "Stroke Rehabilitation",           "IV Antibiotic Course",
    "Bronchodilator Management",   "Chronic Pain Management",         "Dialysis Schedule",
    "Chemotherapy Cycle 3",        "Nutritional Support Plan",        "DVT Prophylaxis",
    "Glycaemic Management",        "Wound Care Protocol",             "Physical Therapy — Hip",
]

MEDICATIONS = [
    "Amlodipine 5 mg OD", "Metformin 1000 mg BD", "Atorvastatin 40 mg OD",
    "Ramipril 5 mg OD", "Aspirin 75 mg OD", "Pantoprazole 40 mg OD",
    "Insulin Glargine 20 U nocte", "Salbutamol inhaler PRN", "Furosemide 40 mg OD",
    "Carvedilol 6.25 mg BD", "Warfarin — INR-guided", "Clopidogrel 75 mg OD",
    "Lisinopril 10 mg OD", "Omeprazole 20 mg OD", "Levothyroxine 50 mcg OD",
    "Prednisolone 10 mg OD", "Morphine SR 30 mg BD", "Tramadol 50 mg TDS PRN",
    "Methotrexate 15 mg weekly", "Hydroxychloroquine 200 mg BD",
]

WARDS = ["General", "ICU", "Cardiology", "Neurology", "Orthopaedics", "Oncology", "Emergency", "HDU"]
ROOMS  = [f"{r}{n}" for r in ["A","B","C","D"] for n in range(101,116)]

RECORD_TYPES = ["consultation", "diagnosis", "lab_result", "imaging", "procedure", "progress", "discharge", "other"]
SEVERITIES   = ["low", "medium", "high", "critical"]


def rnd_date_offset(days_back_min: int, days_back_max: int) -> datetime:
    offset = random.randint(days_back_min, days_back_max)
    return timezone.now() - timedelta(days=offset)


def rnd_vitals() -> dict:
    return {
        "heart_rate":              random.randint(58, 108),
        "blood_pressure_systolic": random.randint(100, 175),
        "blood_pressure_diastolic":random.randint(60, 105),
        "temperature":             round(random.uniform(36.1, 38.7), 1),
        "oxygen_saturation":       random.randint(88, 100),
        "respiratory_rate":        random.randint(12, 26),
        "weight":                  round(random.uniform(48, 115), 1),
        "height":                  random.randint(148, 192),
    }


class Command(BaseCommand):
    help = "Seed 1 admin + 5 doctors + 10 nurses + 60 patients with full demo data"

    def add_arguments(self, parser):
        parser.add_argument("--no-flush", action="store_true", help="Skip deleting existing users")

    def handle(self, *args, **options):
        if not options["no_flush"]:
            self.stdout.write(self.style.WARNING("⚠  Deleting all existing users…"))
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓  All users deleted"))

        # ── Roles ──────────────────────────────────────────────────────────────
        def role(name):
            r, _ = Role.objects.get_or_create(name=name)
            return r

        admin_role   = role(Role.ADMIN)
        doctor_role  = role(Role.DOCTOR)
        nurse_role   = role(Role.NURSE)
        patient_role = role(Role.PATIENT)

        PASSWORD = "HealthSphere@2025"

        # ── 1. Admin ───────────────────────────────────────────────────────────
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@healthsphere.hospital",
            password=PASSWORD,
            first_name="System",
            last_name="Administrator",
            role=admin_role,
        )
        admin.phone = "+91 98100 00001"
        admin.save()
        UserProfile.objects.get_or_create(user=admin, defaults={"employee_id": "ADM-000", "department": "Administration"})
        self.stdout.write(self.style.SUCCESS(f"  ✓ Admin: admin / {PASSWORD}"))

        # ── 2. Doctors ─────────────────────────────────────────────────────────
        doctors = []
        for d in DOCTORS:
            uname = d["first"].lower() + "." + d["last"].lower()
            u = User.objects.create_user(
                username=uname,
                email=d["email"],
                password=PASSWORD,
                first_name=d["first"],
                last_name=d["last"],
                role=doctor_role,
                date_of_birth=date(random.randint(1968, 1985), random.randint(1,12), random.randint(1,28)),
                phone=f"+91 98{random.randint(100,999)} {random.randint(10000,99999)}",
            )
            UserProfile.objects.get_or_create(user=u, defaults={
                "employee_id":    d["emp"],
                "department":     d["dept"],
                "specialization": d["spec"],
            })
            doctors.append(u)
            self.stdout.write(f"  ✓ Doctor: {uname}")

        # ── 3. Nurses ──────────────────────────────────────────────────────────
        for n in NURSES:
            uname = n["first"].lower() + "." + n["last"].lower()
            u = User.objects.create_user(
                username=uname,
                email=n["email"],
                password=PASSWORD,
                first_name=n["first"],
                last_name=n["last"],
                role=nurse_role,
                date_of_birth=date(random.randint(1975, 1998), random.randint(1,12), random.randint(1,28)),
                phone=f"+91 97{random.randint(100,999)} {random.randint(10000,99999)}",
            )
            UserProfile.objects.get_or_create(user=u, defaults={
                "employee_id": n["emp"],
                "department":  n["dept"],
            })
            self.stdout.write(f"  ✓ Nurse : {uname}")

        # ── 4. Patients ────────────────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("\n  Creating 60 patients with full data…"))

        # Decide which 30 of 60 will be currently admitted
        patient_indices = list(range(60))
        admitted_indices = set(random.sample(patient_indices, 30))

        for idx, (fn, ln, gender, dob_str, bt, allergy, history) in enumerate(PATIENTS_RAW):
            uname = f"{fn.lower().replace(' ','')}.{ln.lower().replace(' ','')}"
            # suffix for uniqueness if name duplicates (e.g. two Lakshmi)
            if User.objects.filter(username=uname).exists():
                uname = f"{uname}{idx}"

            dob = date.fromisoformat(dob_str)
            phone = f"+91 {random.randint(70,99)}{random.randint(100,999)} {random.randint(10000,99999)}"
            emergency_name = f"{random.choice(['Sita','Ravi','Ashok','Meena','Suresh','Priya'])} {ln}"
            emergency_phone = f"+91 9{random.randint(0,9)}{random.randint(100,999)} {random.randint(10000,99999)}"

            patient = User.objects.create_user(
                username=uname,
                email=f"{uname}@patient.healthsphere.demo",
                password=PASSWORD,
                first_name=fn,
                last_name=ln,
                role=patient_role,
                date_of_birth=dob,
                phone=phone,
            )
            UserProfile.objects.get_or_create(user=patient, defaults={
                "blood_type":              bt,
                "allergies":               allergy,
                "medical_notes":           history,
                "emergency_contact_name":  emergency_name,
                "emergency_contact_phone": emergency_phone,
            })

            doctor = random.choice(doctors)

            # ── Vitals (2-4 readings per patient) ────────────────────────────
            for v_offset in range(random.randint(2, 4)):
                v     = rnd_vitals()
                nurse_user = User.objects.filter(role__name=Role.NURSE).order_by("?").first()
                VitalRecord.objects.create(
                    patient                   = patient,
                    recorded_by               = nurse_user,
                    recorded_at               = rnd_date_offset(v_offset * 7, v_offset * 7 + 6),
                    heart_rate                = v["heart_rate"],
                    blood_pressure_systolic   = v["blood_pressure_systolic"],
                    blood_pressure_diastolic  = v["blood_pressure_diastolic"],
                    temperature               = v["temperature"],
                    oxygen_saturation         = v["oxygen_saturation"],
                    respiratory_rate          = v["respiratory_rate"],
                    weight                    = v["weight"],
                    height                    = v["height"],
                    notes                     = f"Routine vitals observation #{v_offset+1}",
                )

            # ── Medical Records (3-6 per patient) ────────────────────────────
            diagnoses_used = random.sample(DIAGNOSIS_TITLES, k=min(3, len(DIAGNOSIS_TITLES)))
            for r_i, dx in enumerate(diagnoses_used):
                sev = random.choice(SEVERITIES)
                MedicalRecord.objects.create(
                    patient         = patient,
                    created_by      = doctor,
                    record_type     = random.choice(RECORD_TYPES),
                    title           = dx,
                    description     = (
                        f"Patient {fn} {ln} presented with {dx.lower()}. "
                        f"Background history: {history}. "
                        f"Medication context: {random.choice(MEDICATIONS)}. "
                        f"Patient was reviewed by {doctor.get_full_name()} and managed accordingly. "
                        f"Observation confirmed via clinical assessment and relevant investigations."
                    ),
                    severity        = sev,
                    diagnosis_code  = f"ICD-{random.randint(10, 99)}.{random.randint(0,9)}",
                    record_date     = rnd_date_offset(r_i * 30, r_i * 30 + 29),
                    is_confidential = (r_i == 0 and random.random() < 0.15),
                )

            # ── Treatment Plans (1-2 per patient) ────────────────────────────
            for t_i in range(random.randint(1, 2)):
                t_title = random.choice(TREATMENT_TITLES)
                start   = rnd_date_offset(90, 120).date()
                end     = start + timedelta(days=random.randint(30, 180))
                status  = "active" if t_i == 0 else random.choice(["completed", "active"])
                meds    = random.sample(MEDICATIONS, k=random.randint(2, 4))
                TreatmentPlan.objects.create(
                    patient          = patient,
                    created_by       = doctor,
                    title            = t_title,
                    diagnosis        = diagnoses_used[0] if diagnoses_used else "General management",
                    description      = (
                        f"Treatment plan for {fn} {ln}: {t_title}. "
                        f"Primary diagnosis: {diagnoses_used[0] if diagnoses_used else history}. "
                        f"Medications prescribed: {', '.join(meds)}. "
                        f"Goals: stabilise {diagnoses_used[0].lower() if diagnoses_used else 'condition'}, reduce hospitalisations, improve quality of life. "
                        f"Patient counselled on compliance, lifestyle modifications, and follow-up schedule."
                    ),
                    medications      = "\n".join(meds),
                    lifestyle_recommendations = "Low-sodium diet, regular moderate exercise, smoking cessation, weight management, medication compliance.",
                    follow_up_instructions    = f"Follow up with Dr. {doctor.get_full_name()} in 4 weeks. Monthly blood work required.",
                    start_date       = start,
                    end_date         = end,
                    status           = status,
                    next_review_date = start + timedelta(days=30),
                )

            # ── Admission (admitted or past) ──────────────────────────────────
            admission_type = random.choice(["emergency", "scheduled", "observation"])
            adm_start      = rnd_date_offset(3, 25)

            if idx in admitted_indices:
                # Currently admitted
                AdmissionRecord.objects.create(
                    patient           = patient,
                    attending_doctor  = doctor,
                    admission_type    = admission_type,
                    admission_date    = adm_start,
                    status            = "admitted",
                    ward              = random.choice(WARDS),
                    room_number       = random.choice(ROOMS),
                    bed_number        = str(random.randint(1, 6)),
                    diagnosis         = diagnoses_used[0] if diagnoses_used else history,
                    notes             = f"Patient under observation. Attending: Dr. {doctor.get_full_name()}. Allergies: {allergy}.",
                )
            else:
                # Discharged — past admission
                adm_end = adm_start + timedelta(days=random.randint(2, 12))
                AdmissionRecord.objects.create(
                    patient           = patient,
                    attending_doctor  = doctor,
                    admission_type    = admission_type,
                    admission_date    = adm_start,
                    discharge_date    = adm_end,
                    status            = "discharged",
                    ward              = random.choice(WARDS),
                    room_number       = random.choice(ROOMS),
                    bed_number        = str(random.randint(1, 6)),
                    diagnosis         = diagnoses_used[0] if diagnoses_used else history,
                    notes             = f"Discharged in stable condition. Follow-up in 4 weeks.",
                )

            if (idx + 1) % 10 == 0:
                self.stdout.write(f"    … {idx+1}/60 patients created")

        # ── Summary ────────────────────────────────────────────────────────────
        self.stdout.write("\n" + "─" * 56)
        self.stdout.write(self.style.SUCCESS(
            f"✅  Seed complete!\n"
            f"    Users:            {User.objects.count()}\n"
            f"    Patients:         {User.objects.filter(role__name=Role.PATIENT).count()}\n"
            f"    Medical records:  {MedicalRecord.objects.count()}\n"
            f"    Treatment plans:  {TreatmentPlan.objects.count()}\n"
            f"    Vital records:    {VitalRecord.objects.count()}\n"
            f"    Admissions:       {AdmissionRecord.objects.count()}\n"
            f"─────────────────────────────────────────────────────────\n"
            f"    All passwords: {PASSWORD}"
        ))
