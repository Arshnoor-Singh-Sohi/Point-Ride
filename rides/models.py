# rides/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

User = get_user_model()

class City(models.Model):
    """
    Represents cities that pointRide serves in Ontario, Canada
    """
    name = models.CharField(max_length=100, unique=True)
    province = models.CharField(max_length=50, default='Ontario')
    country = models.CharField(max_length=50, default='Canada')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.province}"

class Route(models.Model):
    """
    Represents a route between cities with multiple stops
    """
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    origin_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='origin_routes')
    destination_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='destination_routes')
    
    # Route details
    intermediate_cities = models.JSONField(default=list, blank=True)  # List of city IDs
    total_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Pricing
    suggested_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    driver_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.origin_city} → {self.destination_city} by {self.driver.username}"
    
    def clean(self):
        """Validate that driver price is within acceptable range"""
        if self.suggested_price and self.driver_price:
            max_price = self.suggested_price * 3
            if self.driver_price > max_price:
                raise ValidationError(f"Driver price cannot exceed 3x suggested price (${max_price})")

class Ride(models.Model):
    """
    Represents an actual ride offering by a driver
    """
    RIDE_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('FULL', 'Full'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='rides')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offered_rides')
    
    # Ride details
    departure_date = models.DateField()
    departure_time = models.TimeField()
    available_seats = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    
    # Pickup and drop-off details
    pickup_location = models.CharField(max_length=255)  # Specific address
    pickup_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='pickup_rides')
    dropoff_location = models.CharField(max_length=255)  # Specific address
    dropoff_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='dropoff_rides')
    
    # Additional info
    notes = models.TextField(blank=True, null=True)
    price_per_seat = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=RIDE_STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['departure_date', 'departure_time']
    
    def __str__(self):
        return f"{self.pickup_city} → {self.dropoff_city} on {self.departure_date}"
    
    @property
    def is_full(self):
        """Check if ride is full based on confirmed bookings"""
        confirmed_bookings = self.bookings.filter(status='CONFIRMED').count()
        return confirmed_bookings >= self.available_seats
    
    @property
    def available_seats_count(self):
        """Get number of available seats"""
        confirmed_bookings = self.bookings.filter(status='CONFIRMED').count()
        return self.available_seats - confirmed_bookings

class Booking(models.Model):
    """
    Represents a booking made by a traveller for a specific ride
    """
    BOOKING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='bookings')
    traveller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking details
    seats_booked = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Custom pickup/dropoff if different from ride defaults
    custom_pickup_location = models.CharField(max_length=255, blank=True, null=True)
    custom_dropoff_location = models.CharField(max_length=255, blank=True, null=True)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='PENDING')
    booking_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['ride', 'traveller']  # Prevent duplicate bookings
    
    def __str__(self):
        return f"{self.traveller.username} → {self.ride} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total price and update ride status"""
        if not self.total_price:
            self.total_price = self.ride.price_per_seat * self.seats_booked
        
        super().save(*args, **kwargs)
        
        # Update ride status if full
        if self.ride.is_full and self.ride.status == 'ACTIVE':
            self.ride.status = 'FULL'
            self.ride.save()

class RideReview(models.Model):
    """
    Reviews and ratings for completed rides
    """
    REVIEWER_CHOICES = [
        ('DRIVER', 'Driver'),
        ('TRAVELLER', 'Traveller'),
    ]
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer_type = models.CharField(max_length=20, choices=REVIEWER_CHOICES)
    
    # Review content
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['ride', 'reviewer', 'reviewee']  # Prevent duplicate reviews
    
    def __str__(self):
        return f"{self.reviewer.username} → {self.reviewee.username} ({self.rating}/5)"