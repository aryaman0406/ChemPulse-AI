from django.db import models

class UploadHistory(models.Model):
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    summary_data = models.JSONField()
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"{self.filename} - {self.upload_date}"
