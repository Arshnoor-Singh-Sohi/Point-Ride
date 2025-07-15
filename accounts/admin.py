# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DriverProfile, TravellerProfile
from .forms import UserRegistrationForm, CustomUserChangeForm # Import your custom forms

# Register your custom User model with the admin site
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom Admin interface for the User model.
    Uses custom forms for adding and changing users.
    """
    add_form = UserRegistrationForm # Form for creating new users in admin
    form = CustomUserChangeForm    # Form for changing existing users in admin
    model = User
    list_display = ['username', 'email', 'full_legal_name', 'is_driver', 'is_traveller', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_legal_name', 'phone_number', 'profile_picture', 'current_home_address', 'starting_city', 'bio', 'languages_spoken', 'is_driver', 'is_traveller')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('full_legal_name', 'phone_number', 'profile_picture', 'current_home_address', 'starting_city', 'bio', 'languages_spoken', 'is_driver', 'is_traveller')}),
    )

# Register other profiles
@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'vehicle_make', 'vehicle_model', 'account_status']
    list_filter = ['account_status']
    search_fields = ['user__username', 'user__full_legal_name', 'license_number', 'vehicle_make', 'vehicle_model']

@admin.register(TravellerProfile)
class TravellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username', 'user__full_legal_name']

