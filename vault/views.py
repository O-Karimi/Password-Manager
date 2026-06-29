from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from .models import Credential
from .forms import CredentialForm

# Create your views here.

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if( form.is_valid()):
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect("login")
    else:
        form = UserCreationForm()
        
    return render(request, 'vault/register.html', {"form": form}) 

def dashboard(request):
    if request.method == "POST":
        form = CredentialForm(request.POST)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.user = request.user
            credential.save()
            messages.success(request, f"Password for {credential.website_name} added to vault!")
            return redirect("dashboard")
    else:
        form = CredentialForm()

    user_credentials = Credential.objects.filter(user=request.user)

    context = {
        "form": form,
        "credentials": user_credentials
    }

    return render(request, "vault/dashboard.html", context)