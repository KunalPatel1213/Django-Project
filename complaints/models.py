from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    name = models.CharField(max_length=100, verbose_name="शिकायतकर्ता का नाम")
    location = models.CharField(max_length=100, verbose_name="स्थान")
    issue = models.TextField(verbose_name="समस्या का विवरण")
    photo = models.ImageField(upload_to='complaints/photos/', verbose_name="फोटो")
    qr_code = models.ImageField(upload_to='complaints/qrcodes/', blank=True, null=True, verbose_name="QR कोड")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="दर्ज करने का समय")

    def __str__(self):
        return f"{self.name} - {self.location}"

# ✅ प्रधान के लिए AdminProfile model
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    village_name = models.CharField(max_length=100, verbose_name="गाँव का नाम")

    def __str__(self):
        return f"{self.user.username} ({self.village_name})"