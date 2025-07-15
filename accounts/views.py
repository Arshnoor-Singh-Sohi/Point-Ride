# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

from .models import User, DriverProfile, TravellerProfile
from .forms import UserRegistrationForm # <-- Import the new form here!

@login_required
def traveller_dashboard(request):
    if not request.user.is_traveller:
        return HttpResponseForbidden("You are not authorized to access the traveller dashboard.")
    return render(request, 'accounts/traveller_dashboard.html')

@login_required
def driver_dashboard(request):
    if not request.user.is_driver:
        return HttpResponseForbidden("You are not authorized to access the driver dashboard.")
    return render(request, 'accounts/driver_dashboard.html')

def traveller_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')  # or wherever you want to redirect
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/traveller_login.html', {'form': form})

def traveller_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_traveller = True
            user.is_driver = False
            user.save()
            TravellerProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Registration successful. You're now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/traveller_registration.html', {'form': form})

# Home page view
def home(request):
    """
    Renders the home page of the pointRide application.
    """
    return render(request, 'home.html')

# Traveller Registration View
class TravellerRegistrationView(CreateView):
    """
    Handles the registration process for new traveller users.
    Now uses the custom UserRegistrationForm.
    """
    model = User
    form_class = UserRegistrationForm # <-- Use the custom form here!
    template_name = 'accounts/traveller_registration.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """
        If the form is valid, save the user and create a TravellerProfile.
        Then, log the user in.
        """
        user = form.save(commit=False)
        user.is_traveller = True
        user.is_driver = False # Ensure they are not marked as a driver by default
        user.save()
        TravellerProfile.objects.create(user=user)
        login(self.request, user) # Log the user in immediately after registration
        return super().form_valid(form)

# Driver Registration Step 1 View
class DriverRegistrationStep1View(CreateView):
    """
    Handles the first step of the driver registration process.
    Now uses the custom UserRegistrationForm.
    """
    model = User
    form_class = UserRegistrationForm # <-- Use the custom form here!
    template_name = 'accounts/driver_registration_step1.html'
    success_url = reverse_lazy('home') # Will redirect to step 2 later

    def form_valid(self, form):
        """
        If the form is valid, save the user and create a DriverProfile.
        Set account_status to 'PENDING'.
        """
        user = form.save(commit=False)
        user.is_driver = True
        user.is_traveller = False # Ensure they are not marked as a traveller by default
        user.save()
        # Create a DriverProfile with default status 'PENDING'
        DriverProfile.objects.create(user=user, account_status='PENDING')
        login(self.request, user) # Log the user in immediately after registration
        return super().form_valid(form)

# Custom Login View
class CustomLoginView(LoginView):
    """
    Custom login view to use a specific template and redirect URL.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        role = self.request.POST.get('login_role')
        user = form.get_user()

        if role == 'traveller' and user.is_traveller:
            return super().form_valid(form)
        elif role == 'driver' and user.is_driver:
            return super().form_valid(form)
        else:
            messages.error(self.request, "Selected role does not match your account type.")
            return redirect('accounts:login')

    def get_success_url(self):
        user = self.request.user
        if user.is_traveller:
            return reverse_lazy('accounts:traveller_dashboard')
        if user.is_driver:
            return reverse_lazy('accounts:driver_dashboard')
        return reverse_lazy('home')

# Custom Logout View
class CustomLogoutView(LogoutView):
    """
    Custom logout view to redirect to the home page after logout.
    """
    next_page = reverse_lazy('home')

