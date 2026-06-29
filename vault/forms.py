from django import forms
from .models import Credential

class CredentialForm(forms.ModelForm):
    class Meta:
        model = Credential
        fields = ["website_name", "username", "password"]
        widgets = {
            "password": forms.PasswordInput()
        }