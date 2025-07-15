# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
import json


class User(AbstractUser):
    full_legal_name = models.CharField(max_length=255, blank=False, null=False)

    phone_number = models.CharField(max_length=20, blank=True, null=True)

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    current_home_address = models.CharField(max_length=255, blank=False, null=False)

    starting_city = models.CharField(max_length=100, blank=False, null=False)

    bio = models.TextField(blank=True, null=True)

    languages_spoken = models.JSONField(default=list, blank=True, null=True)

    is_driver = models.BooleanField(default=False)
    is_traveller = models.BooleanField(default=True)  # Default to traveller

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.username


# Driver Profile Model
# Contains information specific to drivers, linked one-to-one with the custom User model.
class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')

    # Driving License details (e.g., license number, expiry date, class)
    license_number = models.CharField(max_length=50, blank=False, null=True)
    license_expiry_date = models.DateField(blank=False, null=True)
    license_class = models.CharField(max_length=20, blank=True, null=True)  # e.g., 'G', 'Class 5'

    # Vehicle Information
    vehicle_make = models.CharField(max_length=100, blank=False, null=True)
    vehicle_model = models.CharField(max_length=100, blank=False, null=True)
    vehicle_year = models.IntegerField(blank=False, null=True)
    vehicle_registration_number = models.CharField(max_length=50, unique=True, blank=False, null=True)

    # Vehicle photos (e.g., front, back, interior). Stored as a JSON string of paths.
    # In a production app, this might be a separate model for multiple images.
    vehicle_photos = models.JSONField(default=list, blank=True, null=True)  # Stores list of photo URLs/paths

    # Weekly schedule interface / availability. Stored as JSON.
    # Example: {'Monday': '9am-5pm', 'Tuesday': 'off'}
    availability = models.JSONField(default=dict, blank=True, null=True)

    # Account status: 'Pending Verification', 'Verified', 'Rejected'
    account_status = models.CharField(
        max_length=30,
        choices=[
            ('PENDING', 'Pending Verification'),
            ('VERIFIED', 'Verified'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )

    def __str__(self):
        return f"Driver Profile for {self.user.username}"


# Traveller Profile Model
# Contains information specific to travellers, linked one-to-one with the custom User model.
class TravellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='traveller_profile')

    # Any specific fields for travellers can be added here.
    # For now, it might be simple, but can expand later (e.g., preferred payment methods, ride history).

    def __str__(self):
        return f"Traveller Profile for {self.user.username}"

