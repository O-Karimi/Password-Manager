from django.db import models
from django.contrib.auth.models import User
from .encryption import decrypt_password

# Create your models here.

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
    
    def get_decrypted_password(self):
        try:
            return decrypt_password(self.encrypted_password)
        except:
            return "ERROR: Decryption Failed"