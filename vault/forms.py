from django import forms
from .models import Credential

class CredentialForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Credential
        fields = ["website_name", "username"]
