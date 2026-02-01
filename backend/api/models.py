from django.db import models

class UploadHistory(models.Model):
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    summary_data = models.JSONField()
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"{self.filename} - {self.upload_date}"


class ThresholdSettings(models.Model):
    """Configurable thresholds for anomaly detection"""
    name = models.CharField(max_length=50, default="default", unique=True)
    pressure_warning = models.FloatField(default=70.0)
    pressure_critical = models.FloatField(default=80.0)
    temperature_warning = models.FloatField(default=130.0)
    temperature_critical = models.FloatField(default=150.0)
    flowrate_min = models.FloatField(default=10.0)
    flowrate_max = models.FloatField(default=200.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thresholds: P>{self.pressure_critical}, T>{self.temperature_critical}"

    class Meta:
        verbose_name_plural = "Threshold Settings"


class EquipmentHistory(models.Model):
    """Historical tracking of equipment parameters over time"""
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    pressure = models.FloatField()
    temperature = models.FloatField()
    flowrate = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    upload_session = models.ForeignKey(UploadHistory, on_delete=models.CASCADE, related_name='equipment_records', null=True)

    def __str__(self):
        return f"{self.equipment_name} - {self.recorded_at}"

    class Meta:
        verbose_name_plural = "Equipment Histories"
        ordering = ['-recorded_at']


class AlertSettings(models.Model):
    """Email alert configuration for critical equipment notifications"""
    ALERT_FREQUENCY_CHOICES = [
        ('immediate', 'Immediate'),
        ('hourly', 'Hourly Digest'),
        ('daily', 'Daily Digest'),
    ]
    
    email_enabled = models.BooleanField(default=True)
    email_address = models.EmailField(blank=True, null=True)
    alert_on_critical = models.BooleanField(default=True)
    alert_on_warning = models.BooleanField(default=False)
    alert_on_maintenance_due = models.BooleanField(default=True)
    alert_frequency = models.CharField(max_length=20, choices=ALERT_FREQUENCY_CHOICES, default='immediate')
    maintenance_reminder_days = models.IntegerField(default=3)  # Days before maintenance to remind
    last_alert_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alert Settings - {'Enabled' if self.email_enabled else 'Disabled'}"

    class Meta:
        verbose_name_plural = "Alert Settings"


class AlertLog(models.Model):
    """Log of all sent alerts"""
    ALERT_TYPE_CHOICES = [
        ('critical', 'Critical Alert'),
        ('warning', 'Warning Alert'),
        ('maintenance', 'Maintenance Reminder'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    equipment_name = models.CharField(max_length=255)
    message = models.TextField()
    sent_to = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    was_successful = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.alert_type} - {self.equipment_name} - {self.sent_at}"

    class Meta:
        ordering = ['-sent_at']


class MaintenanceSchedule(models.Model):
    """Scheduled maintenance for equipment"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    assigned_to = models.CharField(max_length=255, blank=True)
    estimated_duration = models.IntegerField(default=60, help_text="Duration in minutes")
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.equipment_name} - {self.scheduled_date}"

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
        verbose_name_plural = "Maintenance Schedules"
