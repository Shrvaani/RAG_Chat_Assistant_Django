from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .forms import UserRegistrationForm
from .models import UserProfile
from services.supabase_service import SupabaseService

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user in Supabase (optional)
            try:
                supabase_service = SupabaseService()
                if supabase_service.enabled:
                    supabase_user = supabase_service.create_user(
                        user_id=str(user.id),
                        username=user.username,
                        email=user.email
                    )
                    # Link Django user to Supabase user only if Supabase user was created successfully
                    if supabase_user and 'id' in supabase_user:
                        profile = UserProfile.objects.get(user=user)
                        profile.supabase_user_id = supabase_user['id']
                        profile.save()
                        print(f"Successfully linked Django user {user.id} to Supabase user {supabase_user['id']}")
                    else:
                        print("Supabase user creation failed, but Django user was created successfully")
                        messages.warning(request, 'User created but Supabase sync failed: Unable to create user in Supabase')
                else:
                    print("Supabase is not enabled, skipping user sync")
            except Exception as e:
                # If Supabase fails, still create the user
                print(f"Supabase sync error: {e}")
                messages.warning(request, f'User created but Supabase sync failed: {str(e)}')
            
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('chat:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('chat:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    """User profile view"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

