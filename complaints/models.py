from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
import random
import string
import os

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'रिपोर्ट दर्ज हुई'),
        ('verified', 'सत्यापित'),
        ('resolved', 'हल हुई'),
        ('feedback', 'फीडबैक'),
        ('performance', 'प्रदर्शन'),
        ('escalation', 'एस्केलेशन'),
        ('dashboard', 'डैशबोर्ड'),
    ]
    
    FEEDBACK_CHOICES = [
        ('happy', '🙂'),
        ('neutral', '😐'),
        ('angry', '😡'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, verbose_name="शिकायतकर्ता का नाम")
    location = models.CharField(max_length=100, verbose_name="स्थान")
    issue = models.TextField(verbose_name="समस्या का विवरण")
    photo = models.ImageField(upload_to='complaints/photos/', verbose_name="फोटो")
    qr_code = models.ImageField(upload_to='complaints/qrcodes/', blank=True, null=True, verbose_name="QR कोड")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="दर्ज करने का समय")
    
    # New fields for complaint tracking
    complaint_id = models.CharField(max_length=20, unique=True, blank=True, verbose_name="शिकायत आईडी")
    description = models.TextField(verbose_name="विवरण", blank=True)
    voice_note = models.FileField(upload_to='complaints/voice_notes/', null=True, blank=True, verbose_name="वॉइस नोट")
    
    # Status Tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='submitted',
        verbose_name="स्थिति"
    )
    feedback = models.CharField(
        max_length=10, 
        choices=FEEDBACK_CHOICES, 
        null=True, 
        blank=True,
        verbose_name="फीडबैक"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name="बनाने की तारीख")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="सत्यापित की तारीख")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="हल होने की तारीख")
    
    # Staff Information
    assigned_staff = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="निर्धारित स्टाफ"
    )
    escalated_to = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="एस्केलेट किया गया"
    )
    
    # Performance Metrics
    sla_breached = models.BooleanField(default=False, verbose_name="SLA उल्लंघन")
    trust_badge = models.BooleanField(default=False, verbose_name="ट्रस्ट बैज")

    class Meta:
        verbose_name = "शिकायत"
        verbose_name_plural = "शिकायतें"
        ordering = ['-created_at']

    def generate_complaint_id(self):
        """शिकायत आईडी जनरेट करें"""
        date_str = timezone.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"CMP{date_str}{random_str}"

    def generate_qr_code(self):
        """QR कोड जनरेट करें"""
        if self.complaint_id:
            qr_data = f"Complaint ID: {self.complaint_id}\nName: {self.name}\nLocation: {self.location}\nIssue: {self.issue[:50]}..."
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            # Ensure the file name is unique
            filename = f'qrcode_{self.complaint_id}_{timezone.now().strftime("%H%M%S")}.png'
            
            self.qr_code.save(
                filename,
                File(buffer),
                save=False
            )

    def save(self, *args, **kwargs):
        # Generate complaint ID if not exists
        if not self.complaint_id:
            self.complaint_id = self.generate_complaint_id()
        
        # Set description from issue if description is empty
        if not self.description and self.issue:
            self.description = self.issue
        
        # Generate QR code if complaint_id exists and qr_code is not generated
        if self.complaint_id and not self.qr_code:
            self.generate_qr_code()
        
        # Update timestamps based on status
        if self.status == 'verified' and not self.verified_at:
            self.verified_at = timezone.now()
        elif self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)

    def get_status_display_hindi(self):
        """हिंदी में स्थिति दिखाएं"""
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.status, self.status)

    def get_feedback_display_emoji(self):
        """इमोजी में फीडबैक दिखाएं"""
        feedback_dict = dict(self.FEEDBACK_CHOICES)
        return feedback_dict.get(self.feedback, '')

    # Admin में image preview के लिए methods
    def photo_preview(self):
        if self.photo:
            return f'<a href="{self.photo.url}" target="_blank"><img src="{self.photo.url}" width="100" height="100" style="object-fit: cover; border-radius: 8px;" /></a>'
        return "No Photo"
    photo_preview.allow_tags = True
    photo_preview.short_description = "फोटो प्रिव्यू"

    def qr_code_preview(self):
        if self.qr_code:
            return f'<a href="{self.qr_code.url}" target="_blank"><img src="{self.qr_code.url}" width="100" height="100" style="object-fit: cover; border-radius: 8px;" /></a>'
        return "No QR Code"
    qr_code_preview.allow_tags = True
    qr_code_preview.short_description = "QR कोड प्रिव्यू"

    def __str__(self):
        return f"{self.name} - {self.location} - {self.complaint_id}"

# ✅ प्रधान के लिए AdminProfile model
class AdminProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="उपयोगकर्ता"
    )
    village_name = models.CharField(
        max_length=100, 
        verbose_name="गाँव का नाम"
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name="फोन नंबर"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="सक्रिय है"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="बनाने की तारीख"
    )

    class Meta:
        verbose_name = "प्रशासन प्रोफाइल"
        verbose_name_plural = "प्रशासन प्रोफाइल"

    def __str__(self):
        return f"{self.user.username} ({self.village_name})"

# ✅ शिकायत ट्रैकिंग के लिए अतिरिक्त मॉडल
class ComplaintTracking(models.Model):
    complaint = models.ForeignKey(
        Complaint, 
        on_delete=models.CASCADE,
        related_name='tracking_records',
        verbose_name="शिकायत"
    )
    status = models.CharField(
        max_length=20, 
        choices=Complaint.STATUS_CHOICES,
        verbose_name="स्थिति"
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name="नोट्स"
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="अपडेट किया गया"
    )
    updated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="अपडेट की तारीख"
    )

    class Meta:
        verbose_name = "शिकायत ट्रैकिंग"
        verbose_name_plural = "शिकायत ट्रैकिंग"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.complaint.complaint_id} - {self.status}"

# ✅ स्टाफ मेम्बर के लिए मॉडल
class StaffMember(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="उपयोगकर्ता"
    )
    admin_profile = models.ForeignKey(
        AdminProfile, 
        on_delete=models.CASCADE,
        related_name='staff_members',
        verbose_name="प्रशासन प्रोफाइल"
    )
    designation = models.CharField(
        max_length=100,
        verbose_name="पदनाम"
    )
    phone_number = models.CharField(
        max_length=15,
        verbose_name="फोन नंबर"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="सक्रिय है"
    )

    class Meta:
        verbose_name = "स्टाफ सदस्य"
        verbose_name_plural = "स्टाफ सदस्य"

    def __str__(self):
        # Use username if full name is not available
        full_name = self.user.get_full_name()
        if not full_name:
            full_name = self.user.username
        return f"{full_name} - {self.designation}"