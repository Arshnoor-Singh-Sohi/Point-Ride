# rides/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, time
from .models import Ride, Booking, City, Route, RideReview

class LocationSearchForm(forms.Form):
    """
    Form for searching pickup and drop-off locations
    This is what your teammate worked on at /accounts/maps
    """
    pickup_location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter pickup location...',
            'autocomplete': 'off',
            'id': 'pickup-input'
        }),
        help_text="Start typing your pickup location"
    )
    
    dropoff_location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter drop-off location...',
            'autocomplete': 'off',
            'id': 'dropoff-input'
        }),
        help_text="Start typing your drop-off location"
    )
    
    def clean_pickup_location(self):
        """Validate pickup location is in Ontario, Canada"""
        pickup = self.cleaned_data.get('pickup_location')
        if pickup:
            # This would integrate with your teammate's map validation
            # For now, basic validation
            if not pickup.strip():
                raise ValidationError("Pickup location cannot be empty")
        return pickup
    
    def clean_dropoff_location(self):
        """Validate drop-off location is in Ontario, Canada"""
        dropoff = self.cleaned_data.get('dropoff_location')
        if dropoff:
            if not dropoff.strip():
                raise ValidationError("Drop-off location cannot be empty")
        return dropoff
    
    def clean(self):
        """Validate that pickup and drop-off are different"""
        cleaned_data = super().clean()
        pickup = cleaned_data.get('pickup_location')
        dropoff = cleaned_data.get('dropoff_location')
        
        if pickup and dropoff and pickup.lower() == dropoff.lower():
            raise ValidationError("Pickup and drop-off locations must be different")
        
        return cleaned_data

class RideSearchForm(forms.Form):
    """
    Form for travelers to search for available rides
    """
    pickup_city = forms.ModelChoiceField(
        queryset=City.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select pickup city"
    )
    
    dropoff_city = forms.ModelChoiceField(
        queryset=City.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select drop-off city"
    )
    
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        }),
        initial=date.today
    )
    
    passengers = forms.IntegerField(
        min_value=1,
        max_value=4,
        initial=1,
        widget=forms.Select(
            choices=[(i, f"{i} passenger{'s' if i > 1 else ''}") for i in range(1, 5)],
            attrs={'class': 'form-control'}
        )
    )
    
    def clean_departure_date(self):
        """Ensure departure date is not in the past"""
        departure_date = self.cleaned_data.get('departure_date')
        if departure_date and departure_date < date.today():
            raise ValidationError("Departure date cannot be in the past")
        return departure_date

class RideCreateForm(forms.ModelForm):
    """
    Form for drivers to create new rides
    """
    class Meta:
        model = Ride
        fields = [
            'pickup_location', 'pickup_city', 'dropoff_location', 'dropoff_city',
            'departure_date', 'departure_time', 'available_seats', 'price_per_seat', 'notes'
        ]
        widgets = {
            'pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Specific pickup address'
            }),
            'pickup_city': forms.Select(attrs={'class': 'form-control'}),
            'dropoff_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Specific drop-off address'
            }),
            'dropoff_city': forms.Select(attrs={'class': 'form-control'}),
            'departure_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'available_seats': forms.Select(
                choices=[(i, f"{i} seat{'s' if i > 1 else ''}") for i in range(1, 9)],
                attrs={'class': 'form-control'}
            ),
            'price_per_seat': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional information for passengers (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter cities to active ones
        self.fields['pickup_city'].queryset = City.objects.filter(is_active=True)
        self.fields['dropoff_city'].queryset = City.objects.filter(is_active=True)
        
        # Set minimum date to today
        self.fields['departure_date'].widget.attrs['min'] = date.today().isoformat()
    
    def clean_departure_date(self):
        """Validate departure date"""
        departure_date = self.cleaned_data.get('departure_date')
        if departure_date and departure_date < date.today():
            raise ValidationError("Departure date cannot be in the past")
        return departure_date
    
    def clean_price_per_seat(self):
        """Validate price is reasonable"""
        price = self.cleaned_data.get('price_per_seat')
        if price and price < 0:
            raise ValidationError("Price cannot be negative")
        if price and price > 1000:
            raise ValidationError("Price seems too high. Please contact support for high-value rides.")
        return price
    
    def clean(self):
        """Validate pickup and drop-off are different"""
        cleaned_data = super().clean()
        pickup_city = cleaned_data.get('pickup_city')
        dropoff_city = cleaned_data.get('dropoff_city')
        
        if pickup_city and dropoff_city and pickup_city == dropoff_city:
            raise ValidationError("Pickup and drop-off cities must be different")
        
        return cleaned_data

class BookingForm(forms.ModelForm):
    """
    Form for travelers to book a ride
    """
    class Meta:
        model = Booking
        fields = ['seats_booked', 'custom_pickup_location', 'custom_dropoff_location', 'booking_notes']
        widgets = {
            'seats_booked': forms.Select(
                choices=[(i, f"{i} seat{'s' if i > 1 else ''}") for i in range(1, 5)],
                attrs={'class': 'form-control'}
            ),
            'custom_pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Custom pickup location (optional)'
            }),
            'custom_dropoff_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Custom drop-off location (optional)'
            }),
            'booking_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests or notes (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.ride = kwargs.pop('ride', None)
        super().__init__(*args, **kwargs)
        
        # Set max seats based on available seats
        if self.ride:
            max_seats = min(4, self.ride.available_seats_count)
            self.fields['seats_booked'].widget.choices = [
                (i, f"{i} seat{'s' if i > 1 else ''}") for i in range(1, max_seats + 1)
            ]
    
    def clean_seats_booked(self):
        """Validate seats availability"""
        seats = self.cleaned_data.get('seats_booked')
        if self.ride and seats:
            if seats > self.ride.available_seats_count:
                raise ValidationError(f"Only {self.ride.available_seats_count} seats available")
        return seats

class RideReviewForm(forms.ModelForm):
    """
    Form for reviewing rides after completion
    """
    class Meta:
        model = RideReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience (optional)'
            })
        }
    
    def clean_rating(self):
        """Validate rating is within range"""
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise ValidationError("Rating must be between 1 and 5")
        return rating

class RouteCreateForm(forms.ModelForm):
    """
    Form for creating routes (for the visual map interface)
    """
    class Meta:
        model = Route
        fields = ['origin_city', 'destination_city', 'driver_price']
        widgets = {
            'origin_city': forms.Select(attrs={'class': 'form-control'}),
            'destination_city': forms.Select(attrs={'class': 'form-control'}),
            'driver_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['origin_city'].queryset = City.objects.filter(is_active=True)
        self.fields['destination_city'].queryset = City.objects.filter(is_active=True)
    
    def clean(self):
        """Validate route cities are different"""
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin_city')
        destination = cleaned_data.get('destination_city')
        
        if origin and destination and origin == destination:
            raise ValidationError("Origin and destination cities must be different")
        
        return cleaned_data