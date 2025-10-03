from django.db import models

class Complaint(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    issue = models.TextField()
    photo = models.ImageField(upload_to='complaint_photos/')
    qr_code = models.ImageField(upload_to='complaint_qrcodes/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.location}"