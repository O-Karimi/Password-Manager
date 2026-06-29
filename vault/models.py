from django.db import models
from django.contrib.auth.models import User
from .encryption import decrypt_password

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    salt = models.CharField(max_length=255, blank=True, null=True)
    encrypted_vault_key = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credentials")
    website_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    encrypted_password = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.website_name} ({self.username})"