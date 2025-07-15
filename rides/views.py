# rides/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date, timedelta
from .models import Ride, Booking, City, Route, RideReview
from .forms import (
    LocationSearchForm, RideSearchForm, RideCreateForm, 
    BookingForm, RideReviewForm, RouteCreateForm
)

# City validation algorithm as mentioned in requirements
def validate_ontario_location(location_string):
    """
    Algorithm to validate if location is in Ontario, Canada
    Returns: (is_valid, nearest_city, error_message)
    """
    if not location_string:
        return False, None, "Location cannot be empty"
    
    # Basic validation - check if it contains Ontario-related keywords
    ontario_keywords = ['ontario', 'on', 'canada', 'toronto', 'ottawa', 'hamilton', 'mississauga']
    location_lower = location_string.lower()
    
    # Check if location is in another country/province
    international_keywords = ['usa', 'united states', 'quebec', 'alberta', 'bc', 'british columbia']
    if any(keyword in location_lower for keyword in international_keywords):
        return False, None, "We currently only provide service in Ontario, Canada."
    
    # Try to find nearest city from our served cities
    cities = City.objects.filter(is_active=True)
    nearest_city = None
    
    for city in cities:
        if city.name.lower() in location_lower:
            nearest_city = city
            break
    
    if not nearest_city:
        # If no exact match, suggest list of cities we serve
        served_cities = list(cities.values_list('name', flat=True))
        return False, None, f"We don't serve that location yet. We serve: {', '.join(served_cities[:10])}"
    
    return True, nearest_city, None

def home_search(request):
    """
    Main search page for finding rides
    """
    form = LocationSearchForm()
    recent_rides = Ride.objects.filter(
        status='ACTIVE',
        departure_date__gte=date.today()
    ).order_by('departure_date', 'departure_time')[:6]
    
    if request.method == 'POST':
        form = LocationSearchForm(request.POST)
        if form.is_valid():
            pickup = form.cleaned_data['pickup_location']
            dropoff = form.cleaned_data['dropoff_location']
            
            # Validate locations using our algorithm
            pickup_valid, pickup_city, pickup_error = validate_ontario_location(pickup)
            dropoff_valid, dropoff_city, dropoff_error = validate_ontario_location(dropoff)
            
            if not pickup_valid:
                messages.error(request, f"Pickup location: {pickup_error}")
                return render(request, 'rides/home_search.html', {'form': form, 'recent_rides': recent_rides})
            
            if not dropoff_valid:
                messages.error(request, f"Drop-off location: {dropoff_error}")
                return render(request, 'rides/home_search.html', {'form': form, 'recent_rides': recent_rides})
            
            # If valid, redirect to ride search with cities
            return redirect('rides:search_rides_with_cities', 
                          pickup_city_id=pickup_city.id, 
                          dropoff_city_id=dropoff_city.id)
    
    return render(request, 'rides/home_search.html', {
        'form': form,
        'recent_rides': recent_rides
    })

def search_rides(request, pickup_city_id=None, dropoff_city_id=None):
    """
    Search and display available rides
    """
    form = RideSearchForm()
    rides = Ride.objects.none()
    
    # Pre-fill form if cities provided
    if pickup_city_id and dropoff_city_id:
        try:
            pickup_city = City.objects.get(id=pickup_city_id)
            dropoff_city = City.objects.get(id=dropoff_city_id)
            form.fields['pickup_city'].initial = pickup_city
            form.fields['dropoff_city'].initial = dropoff_city
        except City.DoesNotExist:
            messages.error(request, "Invalid city selection")
    
    if request.method == 'POST':
        form = RideSearchForm(request.POST)
        if form.is_valid():
            pickup_city = form.cleaned_data['pickup_city']
            dropoff_city = form.cleaned_data['dropoff_city']
            departure_date = form.cleaned_data['departure_date']
            passengers = form.cleaned_data['passengers']
            
            # Search for rides
            rides = Ride.objects.filter(
                pickup_city=pickup_city,
                dropoff_city=dropoff_city,
                departure_date=departure_date,
                status='ACTIVE'
            ).annotate(
                booked_seats=Count('bookings', filter=Q(bookings__status='CONFIRMED'))
            ).filter(
                available_seats__gt=passengers - 1  # Ensure enough seats
            ).order_by('departure_time')
    
    # Pagination
    paginator = Paginator(rides, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'rides/search_rides.html', {
        'form': form,
        'rides': page_obj,
        'search_performed': request.method == 'POST'
    })

@login_required
def create_ride(request):
    """
    Create a new ride (drivers only)
    """
    if not request.user.is_driver:
        return HttpResponseForbidden("Only drivers can create rides")
    
    if request.method == 'POST':
        form = RideCreateForm(request.POST, user=request.user)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            
            # Create or get route
            route, created = Route.objects.get_or_create(
                driver=request.user,
                origin_city=ride.pickup_city,
                destination_city=ride.dropoff_city,
                defaults={'driver_price': ride.price_per_seat}
            )
            ride.route = route
            ride.save()
            
            messages.success(request, 'Ride created successfully!')
            return redirect('rides:ride_detail', ride_id=ride.id)
    else:
        form = RideCreateForm(user=request.user)
    
    return render(request, 'rides/create_ride.html', {'form': form})

def ride_detail(request, ride_id):
    """
    Display ride details and booking form
    """
    ride = get_object_or_404(Ride, id=ride_id)
    can_book = (
        request.user.is_authenticated and 
        request.user.is_traveller and 
        request.user != ride.driver and
        ride.status == 'ACTIVE' and
        ride.available_seats_count > 0
    )
    
    # Check if user already booked this ride
    existing_booking = None
    if request.user.is_authenticated:
        existing_booking = Booking.objects.filter(
            ride=ride, 
            traveller=request.user,
            status__in=['PENDING', 'CONFIRMED']
        ).first()
    
    booking_form = None
    if can_book and not existing_booking:
        booking_form = BookingForm(ride=ride)
        
        if request.method == 'POST' and 'book_ride' in request.POST:
            booking_form = BookingForm(request.POST, ride=ride)
            if booking_form.is_valid():
                booking = booking_form.save(commit=False)
                booking.ride = ride
                booking.traveller = request.user
                booking.save()
                
                messages.success(request, 'Booking request sent successfully!')
                return redirect('rides:booking_detail', booking_id=booking.id)
    
    return render(request, 'rides/ride_detail.html', {
        'ride': ride,
        'booking_form': booking_form,
        'can_book': can_book,
        'existing_booking': existing_booking
    })

@login_required
def booking_detail(request, booking_id):
    """
    Display booking details
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if request.user != booking.traveller and request.user != booking.ride.driver:
        return HttpResponseForbidden("You don't have permission to view this booking")
    
    # Handle booking actions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm' and request.user == booking.ride.driver:
            booking.status = 'CONFIRMED'
            booking.confirmed_at = timezone.now()
            booking.save()
            messages.success(request, 'Booking confirmed!')
            
        elif action == 'cancel':
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, 'Booking cancelled!')
        
        return redirect('rides:booking_detail', booking_id=booking.id)
    
    return render(request, 'rides/booking_detail.html', {'booking': booking})

@login_required
def my_rides(request):
    """
    Display user's rides (different view for drivers vs travelers)
    """
    if request.user.is_driver:
        # Show rides created by driver
        rides = Ride.objects.filter(driver=request.user).order_by('-departure_date')
        bookings = Booking.objects.filter(ride__driver=request.user).order_by('-created_at')
        
        return render(request, 'rides/my_rides_driver.html', {
            'rides': rides,
            'bookings': bookings
        })
    else:
        # Show bookings made by traveller
        bookings = Booking.objects.filter(traveller=request.user).order_by('-created_at')
        
        return render(request, 'rides/my_rides_traveller.html', {
            'bookings': bookings
        })

@login_required  
def route_map(request):
    """
    Visual route selection interface (the map your teammate worked on)
    This is at /accounts/maps as mentioned
    """
    if not request.user.is_driver:
        return HttpResponseForbidden("Only drivers can create routes")
    
    cities = City.objects.filter(is_active=True)
    user_routes = Route.objects.filter(driver=request.user)
    
    if request.method == 'POST':
        form = RouteCreateForm(request.POST, user=request.user)
        if form.is_valid():
            route = form.save(commit=False)
            route.driver = request.user
            route.save()
            
            messages.success(request, 'Route created successfully!')
            return redirect('rides:route_map')
    else:
        form = RouteCreateForm(user=request.user)
    
    return render(request, 'rides/route_map.html', {
        'cities': cities,
        'user_routes': user_routes,
        'form': form
    })

@login_required
def leave_review(request, ride_id):
    """
    Leave a review for a completed ride
    """
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Determine if user can review
    can_review = False
    reviewee = None
    reviewer_type = None
    
    if request.user == ride.driver:
        # Driver reviewing travellers
        can_review = True
        reviewer_type = 'DRIVER'
    elif Booking.objects.filter(ride=ride, traveller=request.user, status='CONFIRMED').exists():
        # Traveller reviewing driver
        can_review = True
        reviewee = ride.driver
        reviewer_type = 'TRAVELLER'
    
    if not can_review:
        return HttpResponseForbidden("You cannot review this ride")
    
    if request.method == 'POST':
        form = RideReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ride = ride
            review.reviewer = request.user
            review.reviewee = reviewee
            review.reviewer_type = reviewer_type
            review.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('rides:ride_detail', ride_id=ride.id)
    else:
        form = RideReviewForm()
    
    return render(request, 'rides/leave_review.html', {
        'form': form,
        'ride': ride,
        'reviewee': reviewee
    })

# API endpoints for AJAX requests
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
    API endpoint to validate locations using our algorithm
    """
    location = request.GET.get('location', '')
    is_valid, nearest_city, error = validate_ontario_location(location)
    
    return JsonResponse({
        'is_valid': is_valid,
        'nearest_city': nearest_city.name if nearest_city else None,
        'error': error
    })