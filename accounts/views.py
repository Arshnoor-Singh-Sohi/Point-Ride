# accounts/views.py - COMPLETE ERROR-FREE VERSION

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import User, DriverProfile, TravellerProfile
from .forms import UserRegistrationForm

# ===================================
# UTILITY FUNCTIONS
# ===================================

def print_debug(message):
    """Debug helper function"""
    print(f"🐛 DEBUG: {message}")

def get_user_role_info(user):
    """Get comprehensive user role information"""
    try:
        driver_profile = DriverProfile.objects.filter(user=user).first()
        traveller_profile = TravellerProfile.objects.filter(user=user).first()
        
        return {
            'user': user,
            'is_driver': user.is_driver,
            'is_traveller': user.is_traveller,
            'has_driver_profile': driver_profile is not None,
            'has_traveller_profile': traveller_profile is not None,
            'driver_profile': driver_profile,
            'traveller_profile': traveller_profile
        }
    except Exception as e:
        print_debug(f"Error getting user role info: {e}")
        return None

# ===================================
# HOME PAGE
# ===================================

def home(request):
    """
    Renders the home page of the pointRide application.
    """
    return render(request, 'home.html')

# ===================================
# REGISTRATION VIEWS
# ===================================

def traveller_register(request):
    """
    Handle traveller registration with complete error handling
    """
    print_debug("=== TRAVELLER REGISTRATION START ===")
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():  # Ensure database consistency
                    print_debug("Form is valid, creating user...")
                    
                    # Create user
                    user = form.save(commit=False)
                    user.is_traveller = True
                    user.is_driver = False
                    user.save()
                    
                    print_debug(f"User created: {user.username}")
                    print_debug(f"User flags: driver={user.is_driver}, traveller={user.is_traveller}")
                    
                    # Delete any existing profiles to avoid conflicts
                    DriverProfile.objects.filter(user=user).delete()
                    TravellerProfile.objects.filter(user=user).delete()
                    
                    # Create ONLY traveller profile
                    traveller_profile = TravellerProfile.objects.create(user=user)
                    print_debug(f"TravellerProfile created: {traveller_profile}")
                    
                    # Log the user in
                    login(request, user)
                    print_debug(f"User logged in: {user.username}")
                    
                    messages.success(
                        request, 
                        f"Welcome {user.full_legal_name}! Your traveller account has been created successfully."
                    )
                    return redirect('accounts:traveller_dashboard')
                    
            except Exception as e:
                print_debug(f"Registration error: {e}")
                messages.error(request, f"Registration failed: {str(e)}")
                
        else:
            print_debug(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
        print_debug("Displaying traveller registration form")

    return render(request, 'accounts/traveller_registration.html', {'form': form})

def driver_register(request):
    """
    Handle driver registration with complete error handling
    """
    print_debug("=== DRIVER REGISTRATION START ===")
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():  # Ensure database consistency
                    print_debug("Form is valid, creating driver...")
                    
                    # Create user
                    user = form.save(commit=False)
                    user.is_driver = True
                    user.is_traveller = False
                    user.save()
                    
                    print_debug(f"User created: {user.username}")
                    print_debug(f"User flags: driver={user.is_driver}, traveller={user.is_traveller}")
                    
                    # Delete any existing profiles to avoid conflicts
                    DriverProfile.objects.filter(user=user).delete()
                    TravellerProfile.objects.filter(user=user).delete()
                    
                    # Create ONLY driver profile with safe defaults
                    driver_profile = DriverProfile.objects.create(
                        user=user,
                        account_status='PENDING',
                        license_number='PENDING_VERIFICATION',
                        vehicle_make='Not Specified',
                        vehicle_model='Not Specified',
                        vehicle_year=2020,  # Default year
                        vehicle_registration_number=f'TEMP_{user.id}_{user.username}'
                    )
                    print_debug(f"DriverProfile created: {driver_profile}")
                    
                    # Log the user in
                    login(request, user)
                    print_debug(f"User logged in: {user.username}")
                    
                    messages.success(
                        request, 
                        f"Welcome {user.full_legal_name}! Your driver account has been created. Please complete your profile verification."
                    )
                    return redirect('accounts:driver_dashboard')
                    
            except Exception as e:
                print_debug(f"Registration error: {e}")
                messages.error(request, f"Registration failed: {str(e)}")
                
        else:
            print_debug(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
        print_debug("Displaying driver registration form")

    return render(request, 'accounts/driver_registration_step1.html', {'form': form})

# ===================================
# LOGIN / LOGOUT VIEWS
# ===================================

def user_login(request):
    """
    Handle user login with role validation
    """
    print_debug("=== LOGIN ATTEMPT START ===")
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        login_role = request.POST.get('login_role')
        
        print_debug(f"Login role selected: {login_role}")
        
        if not login_role:
            messages.error(request, "Please select whether you're logging in as a Driver or Traveller.")
            return render(request, 'accounts/login.html', {'form': form})
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            print_debug(f"Login attempt for username: {username}")
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                print_debug(f"User authenticated: {user.username}")
                
                # Get user role info
                role_info = get_user_role_info(user)
                if role_info:
                    print_debug(f"User role info: driver={role_info['is_driver']}, traveller={role_info['is_traveller']}")
                    print_debug(f"Profile info: driver_profile={role_info['has_driver_profile']}, traveller_profile={role_info['has_traveller_profile']}")
                
                # Validate role selection
                if login_role == 'traveller':
                    if user.is_traveller:
                        # Ensure traveller profile exists
                        traveller_profile, created = TravellerProfile.objects.get_or_create(user=user)
                        if created:
                            print_debug("Created missing traveller profile")
                        
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.full_legal_name}!")
                        print_debug("Redirecting to traveller dashboard")
                        return redirect('accounts:traveller_dashboard')
                    else:
                        messages.error(request, "Your account is not registered as a Traveller. Please select 'Driver' or create a new Traveller account.")
                        
                elif login_role == 'driver':
                    if user.is_driver:
                        # Ensure driver profile exists
                        driver_profile, created = DriverProfile.objects.get_or_create(
                            user=user,
                            defaults={
                                'account_status': 'PENDING',
                                'license_number': 'PENDING_VERIFICATION',
                                'vehicle_make': 'Not Specified',
                                'vehicle_model': 'Not Specified',
                                'vehicle_year': 2020,
                                'vehicle_registration_number': f'TEMP_{user.id}_{user.username}'
                            }
                        )
                        if created:
                            print_debug("Created missing driver profile")
                        
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.full_legal_name}!")
                        print_debug("Redirecting to driver dashboard")
                        return redirect('accounts:driver_dashboard')
                    else:
                        messages.error(request, "Your account is not registered as a Driver. Please select 'Traveller' or create a new Driver account.")
                else:
                    messages.error(request, "Invalid role selection. Please select Driver or Traveller.")
            else:
                print_debug("Authentication failed")
                messages.error(request, "Invalid username or password. Please try again.")
        else:
            print_debug(f"Form validation errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = AuthenticationForm()
        print_debug("Displaying login form")

    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    """
    Handle user logout
    """
    print_debug(f"User logout: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

# ===================================
# DASHBOARD VIEWS
# ===================================

@login_required
def traveller_dashboard(request):
    """
    Traveller dashboard with role verification
    """
    print_debug(f"Traveller dashboard access attempt: {request.user.username}")
    
    # Strict role checking
    if not request.user.is_traveller:
        messages.error(request, "Access denied. You need a Traveller account to access this page.")
        return redirect('accounts:login')
    
    # Ensure traveller profile exists
    traveller_profile, created = TravellerProfile.objects.get_or_create(user=request.user)
    if created:
        print_debug("Created missing traveller profile for dashboard access")
    
    context = {
        'user': request.user,
        'profile': traveller_profile
    }
    
    return render(request, 'accounts/traveller_dashboard.html', context)

@login_required
def driver_dashboard(request):
    """
    Driver dashboard with role verification
    """
    print_debug(f"Driver dashboard access attempt: {request.user.username}")
    
    # Strict role checking
    if not request.user.is_driver:
        messages.error(request, "Access denied. You need a Driver account to access this page.")
        return redirect('accounts:login')
    
    # Ensure driver profile exists
    driver_profile, created = DriverProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'account_status': 'PENDING',
            'license_number': 'PENDING_VERIFICATION',
            'vehicle_make': 'Not Specified',
            'vehicle_model': 'Not Specified',
            'vehicle_year': 2020,
            'vehicle_registration_number': f'TEMP_{request.user.id}_{request.user.username}'
        }
    )
    if created:
        print_debug("Created missing driver profile for dashboard access")
    
    context = {
        'user': request.user,
        'profile': driver_profile
    }
    
    return render(request, 'accounts/driver_dashboard.html', context)

# ===================================
# PROFILE MANAGEMENT VIEWS
# ===================================

@login_required
def profile_view(request):
    """
    Generic profile view that redirects to appropriate dashboard
    """
    if request.user.is_driver:
        return redirect('accounts:driver_dashboard')
    elif request.user.is_traveller:
        return redirect('accounts:traveller_dashboard')
    else:
        messages.error(request, "Your account needs to be set up. Please register as either a Driver or Traveller.")
        return redirect('accounts:login')

@login_required
def switch_role(request):
    """
    Allow users to switch roles (if needed in the future)
    Currently not implemented - users should have single roles
    """
    messages.info(request, "Role switching is not currently available. Please contact support if you need to change your account type.")
    return redirect('accounts:profile_view')

# ===================================
# ERROR HANDLING VIEWS
# ===================================

def role_required(allowed_roles):
    """
    Decorator to ensure user has required role
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            user_roles = []
            if request.user.is_driver:
                user_roles.append('driver')
            if request.user.is_traveller:
                user_roles.append('traveller')
            
            if not any(role in allowed_roles for role in user_roles):
                messages.error(request, f"Access denied. This page requires: {', '.join(allowed_roles)}")
                return redirect('accounts:login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# ===================================
# LEGACY VIEW COMPATIBILITY
# ===================================

# These are kept for backward compatibility with any existing URLs

def traveller_registration_view(request):
    """Legacy compatibility for class-based view"""
    return traveller_register(request)

def driver_registration_step1_view(request):
    """Legacy compatibility for class-based view"""
    return driver_register(request)

def custom_login_view(request):
    """Legacy compatibility for class-based view"""
    return user_login(request)

def custom_logout_view(request):
    """Legacy compatibility for class-based view"""
    return user_logout(request)

# ===================================
# DEBUG AND TESTING HELPERS
# ===================================

@login_required
def debug_user_info(request):
    """
    Debug view to check user information (remove in production)
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("Debug access denied")
    
    role_info = get_user_role_info(request.user)
    
    context = {
        'role_info': role_info,
        'user': request.user
    }
    
    return render(request, 'accounts/debug_user_info.html', context)

def health_check(request):
    """
    Simple health check view
    """
    return render(request, 'accounts/health_check.html', {
        'status': 'healthy',
        'user_count': User.objects.count(),
        'driver_count': User.objects.filter(is_driver=True).count(),
        'traveller_count': User.objects.filter(is_traveller=True).count(),
    })