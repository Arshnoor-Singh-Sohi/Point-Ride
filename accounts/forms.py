# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    """
    A custom user creation form that uses the custom User model.
    Includes additional fields and basic password validation.
    """
    full_legal_name = forms.CharField(max_length=255, required=True, help_text="As per government ID.")
    phone_number = forms.CharField(max_length=20, required=False, help_text="Optional: e.g., +1234567890")
    current_home_address = forms.CharField(max_length=255, required=True)
    starting_city = forms.CharField(max_length=100, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False, help_text="Tell us about yourself (optional).")
    # Languages spoken will be a multi-select in the UI, but here it's a JSONField.
    # For a simple form, we might not expose it directly or use a CharField for comma-separated values.
    # For now, we'll keep it simple and let the model handle JSONField default.

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', # Inherited from UserCreationForm
            'email',    # Inherited from UserCreationForm
            'full_legal_name',
            'phone_number',
            'current_home_address',
            'starting_city',
            'bio',
            # 'languages_spoken', # Not directly exposed in this simple form for now
        )
        # You can add widgets here for better Bootstrap styling if needed
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'full_legal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Legal Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (optional)'}),
            'current_home_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current Home Address'}),
            'starting_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Starting City'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
        }

    def clean_password2(self):
        """
        Custom validation for password confirmation.
        """
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise ValidationError("Passwords don't match.")
        return password2

    # You can add more custom validation methods here, e.g., clean_phone_number
    # For password strength, Django's UserCreationForm handles some defaults,
    # but for custom rules, you'd override clean_password1 or use validators.
    # Client-side validation will be handled by JavaScript.


class CustomUserChangeForm(UserChangeForm):
    """
    A custom user change form for the admin interface, using the custom User model.
    """
    class Meta(UserChangeForm.Meta):
        model = User
        fields = UserChangeForm.Meta.fields

