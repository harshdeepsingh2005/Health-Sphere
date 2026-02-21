"""
Django management command to seed appointment and doctor schedule data.
Usage: python manage.py seed_appointments [--clear]
"""
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from appointments.models import Appointment, AppointmentType, DoctorSchedule
from users.models import User, Role


class Command(BaseCommand):
    help = 'Seed doctor schedules and appointments with realistic demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing appointment and schedule data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Appointment.objects.all().delete()
            DoctorSchedule.objects.all().delete()
            self.stdout.write('  Done.')

        doctors  = list(User.objects.filter(role__name=Role.DOCTOR).order_by('id'))
        patients = list(User.objects.filter(role__name=Role.PATIENT).order_by('id'))

        if not doctors:
            self.stdout.write(self.style.ERROR('No doctors found. Run seed_data first.'))
            return
        if not patients:
            self.stdout.write(self.style.ERROR('No patients found. Run seed_data first.'))
            return

        apt_types = {a.name: a for a in AppointmentType.objects.all()}
        if not apt_types:
            self.stdout.write(self.style.ERROR('No AppointmentTypes found. Check appointments app.'))
            return

        # ── Doctor Schedules ─────────────────────────────────────
        self.stdout.write('\nCreating doctor schedules...')
        sched_count = 0

        weekday_configs = [
            # Mon–Fri  09:00–17:00 with 13:00–14:00 break
            {'days': range(0, 5),
             'start': datetime.time(9, 0), 'end': datetime.time(17, 0),
             'break_s': datetime.time(13, 0), 'break_e': datetime.time(14, 0),
             'max': 12},
            # Saturday 09:00–13:00 no break
            {'days': [5],
             'start': datetime.time(9, 0), 'end': datetime.time(13, 0),
             'break_s': None, 'break_e': None,
             'max': 6},
        ]

        for i, doctor in enumerate(doctors):
            # Alternate: some doctors don't work Saturdays
            configs = weekday_configs if i % 3 != 0 else weekday_configs[:1]
            for cfg in configs:
                for day in cfg['days']:
                    _, created = DoctorSchedule.objects.get_or_create(
                        doctor=doctor,
                        day_of_week=day,
                        defaults={
                            'start_time': cfg['start'],
                            'end_time': cfg['end'],
                            'break_start_time': cfg['break_s'],
                            'break_end_time': cfg['break_e'],
                            'max_appointments': cfg['max'],
                            'is_active': True,
                        }
                    )
                    if created:
                        sched_count += 1

        self.stdout.write(f'  {sched_count} schedule slots across {len(doctors)} doctors')

        # ── Appointments ─────────────────────────────────────────
        self.stdout.write('\nCreating appointments...')

        today = timezone.now().date()

        time_slots = [
            datetime.time(9, 0),  datetime.time(9, 30),
            datetime.time(10, 0), datetime.time(10, 30),
            datetime.time(11, 0), datetime.time(11, 30),
            datetime.time(14, 0), datetime.time(14, 30),
            datetime.time(15, 0), datetime.time(15, 30),
            datetime.time(16, 0), datetime.time(16, 30),
        ]

        type_cycle = [
            'routine_checkup', 'follow_up', 'consultation',
            'specialist', 'routine_checkup', 'telemedicine',
            'follow_up', 'consultation', 'emergency',
            'follow_up', 'routine_checkup', 'specialist',
        ]

        reasons = [
            "Routine blood pressure check and medication review",
            "Follow-up after chest pain episode last month",
            "Annual physical examination",
            "Persistent headaches for the past 2 weeks",
            "Knee pain and difficulty walking up stairs",
            "Diabetes management and HbA1c review",
            "Pre-operative consultation – elective knee replacement",
            "Chest congestion and shortness of breath",
            "Fever, chills, and body aches for 3 days",
            "Post-discharge follow-up after hospitalization",
            "Skin rash spreading on arms and legs",
            "Lower back pain radiating to left leg",
            "Anxiety, low mood, and sleep disturbance",
            "Eye strain and blurred vision – screen fatigue",
            "Telemedicine – routine medication refill",
            "Specialist referral – cardiac evaluation",
            "Abdominal pain – upper right quadrant",
            "Chronic fatigue and unexplained weight loss",
            "Ear pain and hearing difficulty",
            "Vaccination and travel medicine consultation",
        ]

        apt_count = 0
        i = 0
        batch = []

        # 3 weeks past + today + 3 weeks future = ~6 weeks of data
        for week_offset in range(-3, 4):
            for day_offset in range(7):
                appt_date = today + datetime.timedelta(weeks=week_offset, days=day_offset)
                if appt_date.weekday() >= 5:   # skip weekends
                    continue

                slots_today = 4 if week_offset == 0 else 3

                for slot_idx in range(slots_today):
                    patient = patients[i % len(patients)]
                    doctor  = doctors[i % len(doctors)]
                    type_name = type_cycle[i % len(type_cycle)]
                    apt_type  = apt_types.get(type_name) or list(apt_types.values())[0]
                    appt_time = time_slots[(slot_idx + i) % len(time_slots)]
                    reason    = reasons[i % len(reasons)]

                    # Status logic based on date
                    if appt_date < today:
                        sc = ['completed', 'completed', 'completed', 'cancelled', 'completed']
                        status = sc[i % len(sc)]
                    elif appt_date == today:
                        status = 'in_progress' if slot_idx == 0 else 'confirmed'
                    else:
                        sc = ['confirmed', 'confirmed', 'requested', 'confirmed']
                        status = sc[i % len(sc)]

                    doctor_notes = ''
                    if status == 'completed':
                        notes_pool = [
                            "Patient reviewed. Medications adjusted. Follow-up in 4 weeks.",
                            "Vitals stable. Lab results reviewed. Continue current treatment.",
                            "Condition improving. Physiotherapy recommended.",
                            "Referred to specialist. Urgency: routine.",
                            "Patient counselled on lifestyle modifications and diet.",
                        ]
                        doctor_notes = notes_pool[i % len(notes_pool)]

                    batch.append(Appointment(
                        patient=patient,
                        doctor=doctor,
                        appointment_type=apt_type,
                        scheduled_date=appt_date,
                        scheduled_time=appt_time,
                        duration_minutes=apt_type.duration_minutes or 30,
                        status=status,
                        reason=reason,
                        doctor_notes=doctor_notes,
                        notes='',
                    ))
                    apt_count += 1
                    i += 1

        # bulk_create skips individual save()/full_clean() — safe for seeding historical data
        Appointment.objects.bulk_create(batch, batch_size=100)
        self.stdout.write(f'  {apt_count} appointments created')


        # ── Summary ───────────────────────────────────────────────
        from django.db.models import Count
        self.stdout.write('\n✓ Appointment data seeded:')
        self.stdout.write(f'  {DoctorSchedule.objects.count()} doctor schedule slots')
        self.stdout.write(f'  {Appointment.objects.count()} appointments total')
        for status, count in (
            Appointment.objects.values('status')
            .annotate(c=Count('id'))
            .values_list('status', 'c')
        ):
            self.stdout.write(f'    {status}: {count}')
