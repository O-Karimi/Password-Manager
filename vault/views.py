from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from .models import Credential
from .forms import CredentialForm

from .encryption import encrypt_password

from django.http import JsonResponse

from .utils import generate_advanced_password

from django.shortcuts import render, redirect, get_object_or_404

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
                    existing_cred.encrypted_password = encrypt_password(new_password)
                    existing_cred.save()
                    messages.success(request, f"Password for {website} updated successfully!")
                else:
                    credential = form.save(commit=False)
                    credential.user = request.user
                    credential.encrypted_password = encrypt_password(new_password)
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

@login_required
def generate_password_api(request):
    
    length = int(request.GET.get('length', 16))
    use_upper = request.GET.get('use_upper', 'true') == 'true'
    use_lower = request.GET.get('use_lower', 'true') == 'true'
    use_numbers = request.GET.get('use_numbers', 'true') == 'true'
    use_symbols = request.GET.get('use_symbols', 'true') == 'true'
    custom_symbols = request.GET.get('custom_symbols', '')
    exclude_ambiguous = request.GET.get('exclude_ambiguous', 'false') == 'true'
    
    is_passphrase = request.GET.get('is_passphrase', 'false') == 'true'
    word_count = int(request.GET.get('word_count', 4))
    separator = request.GET.get('separator', '-')

    new_password = generate_advanced_password(
        length=length, use_upper=use_upper, use_lower=use_lower, 
        use_numbers=use_numbers, use_symbols=use_symbols, 
        custom_symbols=custom_symbols, exclude_ambiguous=exclude_ambiguous,
        is_passphrase=is_passphrase, word_count=word_count, separator=separator
    )
    
    return JsonResponse({'password': new_password})

@login_required
def delete_credential(request, pk):
    """Securely deletes a credential after verifying ownership."""
    # Ensure the credential exists AND belongs to the currently logged-in user
    credential = get_object_or_404(Credential, pk=pk, user=request.user)

    # Only allow deletion via POST request for security
    if request.method == 'POST':
        website = credential.website_name
        credential.delete()
        messages.success(request, f'Password for {website} was permanently deleted.')
    
    return redirect('dashboard')