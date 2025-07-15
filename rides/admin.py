# rides/admin.py

from django.contrib import admin
from .models import City, Route, Ride, Booking, RideReview

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'province', 'country', 'is_active']
    list_filter = ['province', 'country', 'is_active']
    search_fields = ['name', 'province']
    list_editable = ['is_active']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'province', 'country', 'is_active')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['origin_city', 'destination_city', 'driver', 'driver_price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'origin_city', 'destination_city']
    search_fields = ['driver__username', 'driver__full_legal_name', 'origin_city__name', 'destination_city__name']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Route Information', {
            'fields': ('driver', 'origin_city', 'destination_city', 'intermediate_cities')
        }),
        ('Details', {
            'fields': ('total_distance_km', 'estimated_duration_minutes')
        }),
        ('Pricing', {
            'fields': ('suggested_price', 'driver_price')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at',)

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ['pickup_city', 'dropoff_city', 'driver', 'departure_date', 'departure_time', 'available_seats', 'price_per_seat', 'status']
    list_filter = ['status', 'departure_date', 'pickup_city', 'dropoff_city', 'created_at']
    search_fields = ['driver__username', 'driver__full_legal_name', 'pickup_city__name', 'dropoff_city__name']
    list_editable = ['status']
    ordering = ['-departure_date', '-departure_time']
    date_hierarchy = 'departure_date'
    
    fieldsets = (
        ('Route Information', {
            'fields': ('route', 'driver', 'pickup_city', 'dropoff_city', 'pickup_location', 'dropoff_location')
        }),
        ('Schedule', {
            'fields': ('departure_date', 'departure_time')
        }),
        ('Ride Details', {
            'fields': ('available_seats', 'price_per_seat', 'notes')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('driver', 'pickup_city', 'dropoff_city', 'route')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['ride', 'traveller', 'seats_booked', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'confirmed_at', 'ride__departure_date']
    search_fields = ['traveller__username', 'traveller__full_legal_name', 'ride__pickup_city__name', 'ride__dropoff_city__name']
    list_editable = ['status']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('ride', 'traveller', 'seats_booked', 'total_price')
        }),
        ('Custom Locations', {
            'fields': ('custom_pickup_location', 'custom_dropoff_location'),
            'classes': ('collapse',)
        }),
        ('Status and Notes', {
            'fields': ('status', 'booking_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ride', 'traveller', 'ride__pickup_city', 'ride__dropoff_city')

@admin.register(RideReview)
class RideReviewAdmin(admin.ModelAdmin):
    list_display = ['ride', 'reviewer', 'reviewee', 'rating', 'reviewer_type', 'created_at']
    list_filter = ['rating', 'reviewer_type', 'created_at']
    search_fields = ['reviewer__username', 'reviewee__username', 'ride__pickup_city__name', 'ride__dropoff_city__name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Review Information', {
            'fields': ('ride', 'reviewer', 'reviewee', 'reviewer_type')
        }),
        ('Review Content', {
            'fields': ('rating', 'comment')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ride', 'reviewer', 'reviewee')

# Custom admin site configuration
admin.site.site_header = "pointRide Administration"
admin.site.site_title = "pointRide Admin"
admin.site.index_title = "Welcome to pointRide Administration"