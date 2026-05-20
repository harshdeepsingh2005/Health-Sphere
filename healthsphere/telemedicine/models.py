"""
HealthSphere AI - Telemedicine Models
====================================

Models for virtual consultations, video conferencing, and remote patient monitoring.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid
import json

User = get_user_model()


class TelemedicineSession(models.Model):
    """
    Virtual consultation session between patient and healthcare provider.
    """
    
    SESSION_TYPES = [
        ('video_consultation', 'Video Consultation'),
        ('phone_consultation', 'Phone Consultation'),
        ('chat_consultation', 'Chat Consultation'),
        ('remote_monitoring', 'Remote Monitoring'),
        ('follow_up', 'Follow-up Session'),
        ('emergency_consult', 'Emergency Consultation'),
    ]
    
    SESSION_STATUS = [
        ('scheduled', 'Scheduled'),
        ('waiting', 'Waiting Room'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('technical_issues', 'Technical Issues'),
    ]
    
    RECORDING_STATUS = [
        ('not_recorded', 'Not Recorded'),
        ('recording', 'Recording in Progress'),
        ('recorded', 'Recorded'),
        ('processing', 'Processing'),
        ('failed', 'Recording Failed'),
    ]
    
    # Core session information
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='video_consultation')
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='scheduled')
    
    # Participants
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_telemedicine_sessions')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_telemedicine_sessions')
    additional_participants = models.ManyToManyField(
        User, blank=True, related_name='telemedicine_participants',
        help_text="Other healthcare providers, interpreters, or family members"
    )
    
    # Appointment integration
    appointment = models.OneToOneField(
        'appointments.Appointment', on_delete=models.CASCADE,
        related_name='telemedicine_session', null=True, blank=True
    )
    
    # Session timing
    scheduled_start_time = models.DateTimeField()
    scheduled_end_time = models.DateTimeField()
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Technical details
    platform = models.CharField(
        max_length=50, default='webrtc',
        choices=[
            ('webrtc', 'WebRTC'),
            ('zoom', 'Zoom'),
            ('teams', 'Microsoft Teams'),
            ('webex', 'Cisco Webex'),
            ('phone', 'Phone Call'),
            ('custom', 'Custom Platform'),
        ]
    )
    room_url = models.URLField(blank=True, help_text="Virtual room/meeting URL")
    room_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    # Recording and documentation
    recording_status = models.CharField(max_length=20, choices=RECORDING_STATUS, default='not_recorded')
    recording_consent = models.BooleanField(default=False, help_text="Patient consent for recording")
    recording_url = models.URLField(blank=True)
    recording_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Recording duration in seconds")
    
    # Clinical information
    chief_complaint = models.TextField(blank=True, help_text="Main reason for consultation")
    consultation_notes = models.TextField(blank=True, help_text="Clinical notes from consultation")
    diagnosis = models.TextField(blank=True, help_text="Diagnosis or assessment")
    treatment_plan = models.TextField(blank=True, help_text="Treatment recommendations")
    prescriptions_issued = models.ManyToManyField(
        'prescriptions.Prescription', blank=True,
        related_name='telemedicine_sessions'
    )
    
    # Technical quality metrics
    connection_quality = models.CharField(
        max_length=20, blank=True,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('failed', 'Connection Failed'),
        ]
    )
    technical_issues = models.TextField(blank=True, help_text="Any technical problems encountered")
    
    # Billing and insurance
    billing_code = models.CharField(max_length=20, blank=True, help_text="CPT code for telemedicine visit")
    insurance_approved = models.BooleanField(default=False)
    copay_collected = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Satisfaction and quality
    patient_satisfaction_score = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Patient satisfaction rating (1-5)"
    )
    provider_satisfaction_score = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Provider satisfaction rating (1-5)"
    )
    
    # Administrative
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='created_telemedicine_sessions'
    )
    
    class Meta:
        db_table = 'telemedicine_session'
        ordering = ['-scheduled_start_time']
        indexes = [
            models.Index(fields=['patient', 'scheduled_start_time']),
            models.Index(fields=['provider', 'scheduled_start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Telemedicine {self.get_session_type_display()} - {self.patient.get_full_name()} with {self.provider.get_full_name()}"
    
    @property
    def is_active(self):
        """Check if session is currently active."""
        return self.status == 'in_progress'
    
    @property
    def can_start(self):
        """Check if session can be started."""
        return (
            self.status in ['scheduled', 'waiting'] and
            timezone.now() >= self.scheduled_start_time - timedelta(minutes=15) and
            timezone.now() <= self.scheduled_end_time
        )
    
    @property
    def is_overdue(self):
        """Check if session is overdue to start."""
        return (
            self.status == 'scheduled' and
            timezone.now() > self.scheduled_start_time + timedelta(minutes=15)
        )
    
    def start_session(self):
        """Start the telemedicine session."""
        self.status = 'in_progress'
        self.actual_start_time = timezone.now()
        self.save(update_fields=['status', 'actual_start_time'])
    
    def end_session(self):
        """End the telemedicine session."""
        if self.status == 'in_progress':
            self.status = 'completed'
            self.actual_end_time = timezone.now()
            if self.actual_start_time:
                duration = self.actual_end_time - self.actual_start_time
                self.duration_minutes = int(duration.total_seconds() / 60)
            self.save(update_fields=['status', 'actual_end_time', 'duration_minutes'])


class VirtualWaitingRoom(models.Model):
    """
    Virtual waiting room for patients before telemedicine sessions.
    """
    
    session = models.OneToOneField(TelemedicineSession, on_delete=models.CASCADE, related_name='waiting_room')
    patient_joined_at = models.DateTimeField(null=True, blank=True)
    provider_notified_at = models.DateTimeField(null=True, blank=True)
    estimated_wait_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Estimated wait time in minutes"
    )
    
    # Patient engagement while waiting
    educational_content_viewed = models.JSONField(default=list, blank=True)
    forms_completed = models.JSONField(default=list, blank=True)
    vital_signs_submitted = models.JSONField(default=dict, blank=True)
    
    # Technical check results
    camera_test_passed = models.BooleanField(default=False)
    microphone_test_passed = models.BooleanField(default=False)
    speaker_test_passed = models.BooleanField(default=False)
    connection_test_passed = models.BooleanField(default=False)
    browser_compatibility = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'telemedicine_virtual_waiting_room'
    
    def __str__(self):
        return f"Waiting Room - {self.session}"
    
    @property
    def wait_time_minutes(self):
        """Calculate current wait time in minutes."""
        if self.patient_joined_at:
            wait_time = timezone.now() - self.patient_joined_at
            return int(wait_time.total_seconds() / 60)
        return 0


class TelemedicineMessage(models.Model):
    """
    Chat messages during telemedicine sessions.
    """
    
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File Attachment'),
        ('system', 'System Message'),
        ('prescription', 'Prescription'),
        ('vital_signs', 'Vital Signs'),
    ]
    
    session = models.ForeignKey(TelemedicineSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telemedicine_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Message content
    content = models.TextField(help_text="Message text content")
    attachment_url = models.URLField(blank=True, help_text="URL to attached file or image")
    attachment_type = models.CharField(max_length=50, blank=True)
    attachment_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    
    # Message metadata
    sent_at = models.DateTimeField(auto_now_add=True)
    read_by_recipient = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Clinical relevance
    is_clinical_note = models.BooleanField(default=False)
    is_confidential = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'telemedicine_message'
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['session', 'sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.get_full_name()} at {self.sent_at}"
    
    def mark_as_read(self):
        """Mark message as read by recipient."""
        self.read_by_recipient = True
        self.read_at = timezone.now()
        self.save(update_fields=['read_by_recipient', 'read_at'])


class RemoteMonitoringDevice(models.Model):
    """
    Remote monitoring devices connected to telemedicine platform.
    """
    
    DEVICE_TYPES = [
        ('blood_pressure', 'Blood Pressure Monitor'),
        ('glucose_meter', 'Glucose Meter'),
        ('pulse_oximeter', 'Pulse Oximeter'),
        ('thermometer', 'Digital Thermometer'),
        ('weight_scale', 'Digital Scale'),
        ('ecg_monitor', 'ECG Monitor'),
        ('spirometer', 'Spirometer'),
        ('heart_rate_monitor', 'Heart Rate Monitor'),
        ('activity_tracker', 'Activity Tracker'),
        ('medication_dispenser', 'Smart Pill Dispenser'),
    ]
    
    CONNECTIVITY_TYPES = [
        ('bluetooth', 'Bluetooth'),
        ('wifi', 'WiFi'),
        ('cellular', 'Cellular'),
        ('usb', 'USB'),
        ('manual', 'Manual Entry'),
    ]
    
    device_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monitoring_devices')
    
    # Device information
    device_type = models.CharField(max_length=30, choices=DEVICE_TYPES)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    
    # Connectivity
    connectivity_type = models.CharField(max_length=20, choices=CONNECTIVITY_TYPES)
    mac_address = models.CharField(max_length=17, blank=True, help_text="MAC address for network devices")
    last_connection = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Configuration
    measurement_frequency = models.CharField(
        max_length=20, default='daily',
        choices=[
            ('hourly', 'Every Hour'),
            ('daily', 'Daily'),
            ('twice_daily', 'Twice Daily'),
            ('weekly', 'Weekly'),
            ('on_demand', 'On Demand'),
            ('continuous', 'Continuous'),
        ]
    )
    alert_thresholds = models.JSONField(default=dict, blank=True)
    
    # Status
    battery_level = models.PositiveIntegerField(null=True, blank=True, help_text="Battery percentage")
    signal_strength = models.PositiveIntegerField(null=True, blank=True, help_text="Signal strength percentage")
    last_calibration = models.DateTimeField(null=True, blank=True)
    next_calibration_due = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'telemedicine_remote_monitoring_device'
        unique_together = ['patient', 'device_type', 'serial_number']
        indexes = [
            models.Index(fields=['patient', 'device_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_device_type_display()} - {self.patient.get_full_name()}"
    
    @property
    def needs_calibration(self):
        """Check if device needs calibration."""
        if self.next_calibration_due:
            return timezone.now() >= self.next_calibration_due
        return False
    
    @property
    def is_online(self):
        """Check if device is currently online."""
        if self.last_connection:
            offline_threshold = timezone.now() - timedelta(hours=1)
            return self.last_connection >= offline_threshold
        return False
