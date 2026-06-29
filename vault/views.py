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

@login_required
def dashboard(request):
    overwrite_warning = False
    pending_data = None

    if request.method == "POST":
        form = CredentialForm(request.POST)
        if form.is_valid():
            website = form.cleaned_data["website_name"]
            username = form.cleaned_data["username"]
            new_password = form.cleaned_data["password"]

            existing_cred = Credential.objects.filter(
                user=request.user,
                website_name=website,
                username=username
            ).first()

            is_confirmed = request.POST.get("confirm_overwrite") == "True"

            if existing_cred and not is_confirmed:
                overwrite_warning = True
                pending_data = form.cleaned_data
            else:
                if existing_cred and is_confirmed:
                    existing_cred.password = new_password
                    existing_cred.save()
                    messages.success(request, f"Password for {website} updated successfully!")
                else:
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
        "credentials": user_credentials,
        "overwrite_warning": overwrite_warning,
        "pending_data": pending_data,
    }

    return render(request, "vault/dashboard.html", context)