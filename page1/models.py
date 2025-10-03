from django.db import models
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError

class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('road', 'Road Issue'),
        ('water', 'Water Supply'),
        ('electricity', 'Electricity'),
        ('sanitation', 'Sanitation'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
    ]

    FEEDBACK_CHOICES = [
        ('happy', '🙂 Happy'),
        ('neutral', '😐 Neutral'),
        ('angry', '😡 Angry'),
    ]

    villager_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    photo = models.ImageField(upload_to='complaint_photos/%Y/%m/%d/', blank=True, null=True)
    voice_note = models.FileField(upload_to='complaint_voice/%Y/%m/%d/', blank=True, null=True)
    qr_code = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.CharField(max_length=20, choices=FEEDBACK_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    escalated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'

    def __str__(self):
        return f"{self.villager_name} - {self.category} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = f"COMP_{uuid.uuid4().hex[:10].upper()}"
        
        # Status change timestamps
        if self.status == 'verified' and not self.verified_at:
            self.verified_at = timezone.now()
        elif self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status == 'escalated' and not self.escalated_at:
            self.escalated_at = timezone.now()
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('complaint_detail', kwargs={'pk': self.pk})

    @property
    def days_since_created(self):
        return (timezone.now() - self.created_at).days

    @property
    def get_status_color(self):
        status_colors = {
            'pending': 'warning',
            'verified': 'info',
            'resolved': 'success',
            'escalated': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

    def clean(self):
        # Validation for status timestamps
        if self.status == 'verified' and not self.verified_at:
            self.verified_at = timezone.now()
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        if self.status == 'escalated' and not self.escalated_at:
            self.escalated_at = timezone.now()