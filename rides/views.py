# rides/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import date, timedelta
from .models import Ride, Booking, City, Route, RideReview
from django.conf import settings

def home_search(request):
    """
    Main search page for finding rides - WORKING VERSION
    """
    # Get recent rides to display
    recent_rides = Ride.objects.filter(
        status='ACTIVE',
        departure_date__gte=date.today()
    ).select_related('pickup_city', 'dropoff_city', 'driver')[:6]
    
    # Get cities for dropdowns
    cities = City.objects.filter(is_active=True).order_by('name')
    
    context = {
        'recent_rides': recent_rides,
        'cities': cities,
        'today': date.today(),
    }
    
    return render(request, 'rides/home_search.html', context)

def search_rides(request):
    """
    Search and display available rides - WORKING VERSION
    """
    rides = Ride.objects.none()
    search_performed = False
    cities = City.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        pickup_city_id = request.POST.get('pickup_city')
        dropoff_city_id = request.POST.get('dropoff_city')
        departure_date = request.POST.get('departure_date')
        
        if pickup_city_id and dropoff_city_id and departure_date:
            try:
                departure_date = date.fromisoformat(departure_date)
                
                rides = Ride.objects.filter(
                    pickup_city_id=pickup_city_id,
                    dropoff_city_id=dropoff_city_id,
                    departure_date=departure_date,
                    status='ACTIVE'
                ).select_related('pickup_city', 'dropoff_city', 'driver').order_by('departure_time')
                
                search_performed = True
                
            except ValueError:
                messages.error(request, "Invalid date format")
    
    context = {
        'rides': rides,
        'cities': cities,
        'search_performed': search_performed,
    }
    
    return render(request, 'rides/search_rides.html', context)

@login_required
def create_ride(request):
    """
    Create a new ride (drivers only) - ENHANCED VERSION
    """
    if not request.user.is_driver:
        return HttpResponseForbidden("Only drivers can create rides")
    
    cities = City.objects.filter(is_active=True).order_by('name')
    
    # Create the context once and reuse it - this ensures consistency
    context = {
        'cities': cities,
        'today': date.today(),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    
    if request.method == 'POST':
        pickup_city_id = request.POST.get('pickup_city')
        dropoff_city_id = request.POST.get('dropoff_city')
        pickup_location = request.POST.get('pickup_location')
        dropoff_location = request.POST.get('dropoff_location')
        departure_date = request.POST.get('departure_date')
        departure_time = request.POST.get('departure_time')
        available_seats = request.POST.get('available_seats')
        price_per_seat = request.POST.get('price_per_seat')
        notes = request.POST.get('notes', '')
        
        # Basic validation
        if not all([pickup_city_id, dropoff_city_id, pickup_location, dropoff_location, 
                   departure_date, departure_time, available_seats, price_per_seat]):
            messages.error(request, "Please fill in all required fields")
            return render(request, 'rides/create_ride.html', context)  # Now consistent!
        
        if pickup_city_id == dropoff_city_id:
            messages.error(request, "Pickup and drop-off cities must be different")
            return render(request, 'rides/create_ride.html', context)  # Now consistent!
        
        try:
            pickup_city = City.objects.get(id=pickup_city_id)
            dropoff_city = City.objects.get(id=dropoff_city_id)
            departure_date = date.fromisoformat(departure_date)
            
            # Create or get route
            route, created = Route.objects.get_or_create(
                driver=request.user,
                origin_city=pickup_city,
                destination_city=dropoff_city,
                defaults={'driver_price': float(price_per_seat)}
            )
            
            # Create ride
            ride = Ride.objects.create(
                route=route,
                driver=request.user,
                pickup_city=pickup_city,
                dropoff_city=dropoff_city,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                departure_date=departure_date,
                departure_time=departure_time,
                available_seats=int(available_seats),
                price_per_seat=float(price_per_seat),
                notes=notes
            )
            
            messages.success(request, f'Ride created successfully! {pickup_city.name} → {dropoff_city.name} on {departure_date}')
            return redirect('rides:ride_detail', ride_id=ride.id)
            
        except (ValueError, City.DoesNotExist) as e:
            messages.error(request, f"Error creating ride: {str(e)}")
            return render(request, 'rides/create_ride.html', context)  # Now consistent!
    
    # GET request - now this includes the API key too!
    return render(request, 'rides/create_ride.html', context)


def ride_detail(request, ride_id):
    """
    Display ride details and booking form - ENHANCED VERSION
    """
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Check if user can book
    can_book = (
        request.user.is_authenticated and 
        request.user.is_traveller and 
        request.user != ride.driver and
        ride.status == 'ACTIVE' and
        ride.available_seats_count > 0
    )
    
    # Check existing booking
    existing_booking = None
    if request.user.is_authenticated:
        existing_booking = Booking.objects.filter(
            ride=ride, 
            traveller=request.user,
            status__in=['PENDING', 'CONFIRMED']
        ).first()
    
    # Handle booking
    if request.method == 'POST' and can_book and not existing_booking:
        seats_booked = request.POST.get('seats_booked')
        booking_notes = request.POST.get('booking_notes', '')
        
        try:
            seats_booked = int(seats_booked)
            if seats_booked > ride.available_seats_count:
                messages.error(request, f"Only {ride.available_seats_count} seats available")
            else:
                booking = Booking.objects.create(
                    ride=ride,
                    traveller=request.user,
                    seats_booked=seats_booked,
                    total_price=seats_booked * ride.price_per_seat,
                    booking_notes=booking_notes
                )
                messages.success(request, 'Booking request sent successfully! The driver will review your request.')
                return redirect('rides:booking_detail', booking_id=booking.id)
                
        except ValueError:
            messages.error(request, "Invalid number of seats")
    
    context = {
        'ride': ride,
        'can_book': can_book,
        'existing_booking': existing_booking,
        'available_seats_range': range(1, min(5, ride.available_seats_count + 1))
    }
    
    return render(request, 'rides/ride_detail.html', context)

@login_required
def booking_detail(request, booking_id):
    """
    Display booking details - ENHANCED VERSION with better seat tracking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if request.user != booking.traveller and request.user != booking.ride.driver:
        return HttpResponseForbidden("You don't have permission to view this booking")
    
    # Handle booking actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm' and request.user == booking.ride.driver and booking.status == 'PENDING':
            # Check if there are enough seats available (using fixed calculation)
            current_available = booking.ride.available_seats_count
            if booking.seats_booked <= current_available:
                booking.status = 'CONFIRMED'
                booking.confirmed_at = timezone.now()
                booking.save()
                
                # Check if ride is now full (using fixed calculation)
                if booking.ride.available_seats_count <= 0:
                    booking.ride.status = 'FULL'
                    booking.ride.save()
                
                messages.success(request, f'Booking confirmed for {booking.traveller.full_legal_name}! {booking.seats_booked} seat(s) booked.')
            else:
                messages.error(request, f'Not enough seats available! Only {current_available} seats left.')
                
        elif action == 'reject' and request.user == booking.ride.driver and booking.status == 'PENDING':
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, 'Booking rejected!')
            
        elif action == 'cancel' and request.user == booking.traveller and booking.status == 'PENDING':
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, 'Booking cancelled!')
        
        return redirect('rides:booking_detail', booking_id=booking.id)
    
    return render(request, 'rides/booking_detail.html', {'booking': booking})

@login_required
def my_rides(request):
    """
    Display user's rides - ENHANCED VERSION
    """
    if request.user.is_driver:
        # Get driver's rides with proper seat calculations
        rides = Ride.objects.filter(driver=request.user).select_related(
            'pickup_city', 'dropoff_city'
        ).prefetch_related('bookings').order_by('-departure_date')
        
        # Get pending bookings for driver's rides
        pending_bookings = Booking.objects.filter(
            ride__driver=request.user,
            status='PENDING'
        ).select_related('ride', 'traveller', 'ride__pickup_city', 'ride__dropoff_city').order_by('-created_at')
        
        return render(request, 'rides/my_rides_driver.html', {
            'rides': rides,
            'pending_bookings': pending_bookings
        })
    else:
        # Traveller bookings
        bookings = Booking.objects.filter(traveller=request.user).select_related(
            'ride', 'ride__pickup_city', 'ride__dropoff_city', 'ride__driver'
        ).order_by('-created_at')
        
        return render(request, 'rides/my_rides_traveller.html', {'bookings': bookings})

@login_required  
def route_map(request):
    """
    Enhanced visual route selection interface - SIMPLIFIED VERSION
    Now includes secure API key handling for Google Maps
    """
    if not request.user.is_driver:
        return HttpResponseForbidden("Only drivers can access route planning")
    
    cities = City.objects.filter(is_active=True).order_by('name')
    user_routes = Route.objects.filter(driver=request.user).select_related('origin_city', 'destination_city')
    
    # Note: Route creation is now handled directly in create_ride view
    # This view focuses on visualization and planning
    
    # Pass the Google Maps API key from settings to the template
    # This is the key addition - we're securely passing the API key through context
    context = {
        'cities': cities,
        'user_routes': user_routes,
        'today': date.today(),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,  # Add API key to context
    }
    
    return render(request, 'rides/route_map.html', context)

@login_required
def leave_review(request, ride_id):
    """
    Leave a review - SIMPLE VERSION
    """
    ride = get_object_or_404(Ride, id=ride_id)
    messages.info(request, "Review system coming soon!")
    return redirect('rides:ride_detail', ride_id=ride.id)

# API endpoints
@login_required
def api_cities(request):
    """
    API endpoint to get cities for autocomplete
    """
    query = request.GET.get('q', '')
    cities = City.objects.filter(
        name__icontains=query,
        is_active=True
    )[:10]
    
    data = [{'id': city.id, 'name': city.name} for city in cities]
    return JsonResponse(data, safe=False)

@login_required
def api_validate_location(request):
    """
    API endpoint for location validation - ENHANCED VERSION
    """
    location = request.GET.get('location', '')
    
    # Basic Ontario validation
    ontario_keywords = ['ontario', 'on', 'canada', 'ca']
    is_ontario = any(keyword in location.lower() for keyword in ontario_keywords)
    
    # Find nearest city
    nearest_city = None
    if location:
        city_match = City.objects.filter(
            name__icontains=location.split(',')[0].strip(),
            is_active=True
        ).first()
        if city_match:
            nearest_city = city_match.name
    
    return JsonResponse({
        'is_valid': is_ontario,
        'nearest_city': nearest_city,
        'error': None if is_ontario else 'Location must be in Ontario, Canada'
    })