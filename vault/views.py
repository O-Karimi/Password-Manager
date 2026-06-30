from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from .models import Credential, UserProfile
from .forms import CredentialForm

from .encryption import encrypt_password, generate_user_keys, unlock_vault_key, decrypt_password

from django.http import JsonResponse

from .utils import generate_advanced_password

from django.contrib.auth import login, authenticate

from django.contrib.auth import update_session_auth_hash
from .encryption import rekey_vault

import csv
from django.http import HttpResponse

# Create your views here.

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if( form.is_valid()):
            user = form.save()

            raw_password = request.POST.get('password1') or request.POST.get('password')
            if not raw_password:
                messages.error(request, "Error capturing password from form. Please try again.")
                return redirect('register')

            salt, encrypted_key = generate_user_keys( raw_password)

            UserProfile.objects.create(
                user=user,
                salt=salt.decode("utf-8"),
                encrypted_vault_key = encrypted_key.decode("utf-8")
            )

            messages.success(request, "Account created successfully!")
            return redirect("login")
    else:
        form = UserCreationForm()
        
    return render(request, 'vault/register.html', {"form": form}) 

def custom_login(request):
    """Custom login view to intercept the password and unlock the vault key."""
    if request.method == 'POST':
        username = request.POST.get('username')
        raw_password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=raw_password)
        
        if user is not None:
            login(request, user)
            
            try:
                profile = user.profile
                vault_key = unlock_vault_key(
                    raw_password, 
                    profile.salt.encode('utf-8'), 
                    profile.encrypted_vault_key.encode('utf-8')
                )
                request.session['vault_key'] = vault_key.decode('utf-8')
                return redirect('dashboard')
            except Exception:
                messages.error(request, 'Cryptographic error: Unable to unlock vault.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    else:
        form = AuthenticationForm()
        
    return render(request, 'vault/login.html', {'form': form})

@login_required
def dashboard(request):
    vault_key = request.session.get("vault_key")

    if not vault_key:
        messages.error(request, "Secure session expired. Please log in again.")
        return redirect("login")

    overwrite_warning = False
    pending_data = None

    if request.method == "POST":
        from .forms import CredentialForm
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
                encrypted_pass = encrypt_password(new_password, vault_key)

                if existing_cred and is_confirmed:
                    existing_cred.encrypted_password = encrypted_pass
                    existing_cred.save()
                    messages.success(request, f"Password for {website} updated successfully!")
                else:
                    credential = form.save(commit=False)
                    credential.user = request.user
                    credential.encrypted_password = encrypted_pass
                    credential.save()
                    messages.success(request, f"Password for {credential.website_name} added to vault!")
                return redirect("dashboard")
    else:
        from .forms import CredentialForm
        form = CredentialForm()

    raw_credentials = Credential.objects.filter(user=request.user)

    decrypted_credentials = []

    for c in raw_credentials:
        try:
            dec = decrypt_password(c.encrypted_password, vault_key)
        except Exception:
            dec = "ERROR: Decryption Failed"
        
        decrypted_credentials.append({
            "id":c.id,
            "website_name": c.website_name,
            "username": c.username,
            "decrypted_password": dec
        })

    context = {
        "form": form,
        "credentials": decrypted_credentials,
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

@login_required
def profile(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('profile')

        if not request.user.check_password(old_password):
            messages.error(request, 'Incorrect current password.')
            return redirect('profile')

        try:
            user_profile = request.user.profile
            new_salt, new_encrypted_key = rekey_vault(
                old_password, 
                new_password, 
                user_profile.salt.encode('utf-8'), 
                user_profile.encrypted_vault_key.encode('utf-8')
            )

            user_profile.salt = new_salt.decode('utf-8')
            user_profile.encrypted_vault_key = new_encrypted_key.decode('utf-8')
            user_profile.save()

            request.user.set_password(new_password)
            request.user.save()

            update_session_auth_hash(request, request.user)

            messages.success(request, 'Master password updated securely!')
            return redirect('dashboard')
            
        except Exception:
            messages.error(request, 'Cryptographic error during password change.')
            return redirect('profile')

    return render(request, 'vault/profile.html')

@login_required
def export_passwords(request):
    vault_key = request.session.get('vault_key')
    
    if not vault_key:
        messages.error(request, 'Secure session expired. Please log in again to export data.')
        return redirect('login')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_secure_vault.csv"'

    writer = csv.writer(response)
    
    writer.writerow(['Website', 'Username', 'Password'])

    credentials = Credential.objects.filter(user=request.user)
    for c in credentials:
        try:
            plain_password = decrypt_password(c.encrypted_password, vault_key)
        except Exception:
            plain_password = "ERROR: Decryption Failed"
            
        writer.writerow([c.website_name, c.username, plain_password])

    return response

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'vault/home.html')