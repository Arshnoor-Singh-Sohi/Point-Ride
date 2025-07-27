# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin

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
# CORE VIEWS
# ===================================

def home(request):
    """Renders the home page"""
    return render(request, 'home.html')


# ===================================
# REGISTRATION VIEWS
# ===================================

class TravellerRegistrationView(CreateView):
    """Class-based traveller registration (your version)"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/traveller_registration.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        existing_user = User.objects.filter(username=username).first()
        if existing_user and existing_user.is_driver:
            messages.error(self.request,
                           "An account with this username is already registered as a driver.")
            return self.form_invalid(form)

        user = form.save(commit=False)
        user.is_traveller = True
        user.is_driver = False
        user.save()
        TravellerProfile.objects.create(user=user)
        login(self.request, user)
        messages.success(self.request, "Registration successful.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class DriverRegistrationStep1View(CreateView):
    """Class-based driver registration (your version)"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/driver_registration_step1.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        existing_user = User.objects.filter(username=username).first()
        if existing_user and existing_user.is_traveller:
            messages.error(self.request,
                           "An account with this username is already registered as a traveller.")
            return self.form_invalid(form)

        user = form.save(commit=False)
        user.is_driver = True
        user.is_traveller = False
        user.save()
        DriverProfile.objects.create(user=user, account_status='PENDING')
        login(self.request, user)
        messages.success(self.request, "Driver registration successful.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


def traveller_register(request):
    """Function-based traveller registration (their version)"""
    print_debug("=== TRAVELLER REGISTRATION START ===")

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    print_debug("Form is valid, creating user...")
                    user = form.save(commit=False)
                    user.is_traveller = True
                    user.is_driver = False
                    user.save()

                    DriverProfile.objects.filter(user=user).delete()
                    traveller_profile = TravellerProfile.objects.create(user=user)

                    login(request, user)
                    messages.success(request, f"Welcome {user.full_legal_name}!")
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
    """Function-based driver registration (their version)"""
    print_debug("=== DRIVER REGISTRATION START ===")

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    print_debug("Form is valid, creating driver...")
                    user = form.save(commit=False)
                    user.is_driver = True
                    user.is_traveller = False
                    user.save()

                    TravellerProfile.objects.filter(user=user).delete()
                    driver_profile = DriverProfile.objects.create(
                        user=user,
                        account_status='PENDING',
                        license_number='PENDING_VERIFICATION',
                        vehicle_make='Not Specified',
                        vehicle_model='Not Specified',
                        vehicle_year=2020,
                        vehicle_registration_number=f'TEMP_{user.id}_{user.username}'
                    )

                    login(request, user)
                    messages.success(request, f"Welcome {user.full_legal_name}!")
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
# AUTHENTICATION VIEWS
# ===================================

class CustomLoginView(LoginView):
    """Your class-based login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        role = self.request.POST.get('login_role')
        user = form.get_user()

        if role == 'traveller' and user.is_traveller:
            messages.success(self.request, f"Welcome back, {user.username} (Traveller)!")
            return super().form_valid(form)
        elif role == 'driver' and user.is_driver:
            messages.success(self.request, f"Welcome back, {user.username} (Driver)!")
            return super().form_valid(form)
        else:
            if role == 'traveller' and user.is_driver:
                messages.error(self.request, "You are registered as a driver.")
            elif role == 'driver' and user.is_traveller:
                messages.error(self.request, "You are registered as a traveller.")
            else:
                messages.error(self.request, "Invalid credentials.")
            return self.form_invalid(form)

    def get_success_url(self):
        user = self.request.user
        if user.is_traveller:
            return reverse_lazy('accounts:traveller_dashboard')
        if user.is_driver:
            return reverse_lazy('accounts:driver_dashboard')
        return reverse_lazy('home')

    def form_invalid(self, form):
        if not messages.get_messages(self.request):
            messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Your class-based logout view"""
    next_page = reverse_lazy('home')


def user_login(request):
    """Their function-based login view"""
    print_debug("=== LOGIN ATTEMPT START ===")

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        login_role = request.POST.get('login_role')

        if not login_role:
            messages.error(request, "Please select a role.")
            return render(request, 'accounts/login.html', {'form': form})

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                print_debug(f"User authenticated: {user.username}")
                role_info = get_user_role_info(user)

                if login_role == 'traveller' and user.is_traveller:
                    traveller_profile, created = TravellerProfile.objects.get_or_create(user=user)
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.full_legal_name}!")
                    return redirect('accounts:traveller_dashboard')
                elif login_role == 'driver' and user.is_driver:
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
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.full_legal_name}!")
                    return redirect('accounts:driver_dashboard')
                else:
                    messages.error(request, "Role mismatch.")
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """Their function-based logout view"""
    print_debug(f"User logout: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


# ===================================
# DASHBOARD VIEWS
# ===================================

@login_required
def traveller_dashboard(request):
    """Combined traveller dashboard view"""
    if not request.user.is_traveller:
        return HttpResponseForbidden("Access denied.")

    traveller_profile, created = TravellerProfile.objects.get_or_create(user=request.user)
    context = {
        'user': request.user,
        'profile': traveller_profile
    }
    return render(request, 'accounts/traveller_dashboard.html', context)


@login_required
def driver_dashboard(request):
    """Combined driver dashboard view"""
    if not request.user.is_driver:
        return HttpResponseForbidden("Access denied.")

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
    context = {
        'user': request.user,
        'profile': driver_profile
    }
    return render(request, 'accounts/driver_dashboard.html', context)

class UpdateDriverProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_driver:
            messages.error(request, "You are not authorized to update driver information.")
            return redirect('accounts:edit_profile')

        driver_profile = request.user.driver_profile

        driver_profile.license_number = request.POST.get('license_number')
        driver_profile.license_expiry_date = request.POST.get('license_expiry_date')
        driver_profile.vehicle_make = request.POST.get('vehicle_make')
        driver_profile.vehicle_model = request.POST.get('vehicle_model')
        driver_profile.vehicle_year = request.POST.get('vehicle_year')
        driver_profile.vehicle_registration_number = request.POST.get('vehicle_registration_number')

        driver_profile.save()

        messages.success(request, "Driver profile updated successfully.")
        return redirect('accounts:edit_profile')
# ===================================
# PROFILE VIEWS
# ===================================

class EditProfileView(LoginRequiredMixin, UpdateView):
    """Your edit profile view"""
    model = User
    fields = [
        'full_legal_name',
        'email',
        'phone_number',
        'profile_picture',
        'current_home_address',
        'starting_city',
        'bio',
        'languages_spoken'
    ]
    template_name = 'accounts/edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_driver:
            context['driver_profile'] = self.request.user.driver_profile
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Handle DriverProfile update if driver
        if self.request.user.is_driver:
            driver_profile = self.request.user.driver_profile
            post = self.request.POST
            print(post)
            driver_profile.license_number = post.get('license_number')
            driver_profile.license_expiry_date = post.get('license_expiry_date')
            driver_profile.vehicle_make = post.get('vehicle_make')
            driver_profile.vehicle_model = post.get('vehicle_model')
            driver_profile.vehicle_year = post.get('vehicle_year')
            driver_profile.vehicle_registration_number = post.get('vehicle_registration_number')
            driver_profile.save()

        messages.success(self.request, "Profile updated successfully.")
        return response

    def get_success_url(self):
        if self.request.user.is_driver:
            return reverse_lazy('accounts:driver_dashboard')
        return reverse_lazy('accounts:traveller_dashboard')


@login_required
def profile_view(request):
    """Their profile view"""
    if request.user.is_driver:
        return redirect('accounts:driver_dashboard')
    elif request.user.is_traveller:
        return redirect('accounts:traveller_dashboard')
    else:
        messages.error(request, "Account not set up.")
        return redirect('accounts:login')


# ===================================
# UTILITY VIEWS
# ===================================

def health_check(request):
    """Health check view"""
    return render(request, 'accounts/health_check.html', {
        'status': 'healthy',
        'user_count': User.objects.count(),
        'driver_count': User.objects.filter(is_driver=True).count(),
        'traveller_count': User.objects.filter(is_traveller=True).count(),
    })


# ===================================
# LEGACY COMPATIBILITY
# ===================================

def traveller_registration_view(request):
    return traveller_register(request)


def driver_registration_step1_view(request):
    return driver_register(request)


def custom_login_view(request):
    return user_login(request)


def custom_logout_view(request):
    return user_logout(request)


@login_required
def debug_user_info(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Debug access denied")
    role_info = get_user_role_info(request.user)
    return render(request, 'accounts/debug_user_info.html', {
        'role_info': role_info,
        'user': request.user
    })


def role_required(allowed_roles):
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
                messages.error(request, f"Access denied. Required: {', '.join(allowed_roles)}")
                return redirect('accounts:login')

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


@login_required
def switch_role(request):
    messages.info(request, "Role switching not available.")
    return redirect('accounts:profile_view')