from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credentials")
    website_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.website_name} ({self.username})"