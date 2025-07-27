# rides/urls.py

from django.urls import path
from . import views

app_name = 'rides'

urlpatterns = [
    # Main search and ride listing
    path('', views.home_search, name='home_search'),
    path('search/', views.search_rides, name='search_rides'),
    path('search/<int:pickup_city_id>/<int:dropoff_city_id>/', 
        views.search_rides, name='search_rides_with_cities'),
    
    # Ride management
    path('create/', views.create_ride, name='create_ride'),
    path('ride/<int:ride_id>/', views.ride_detail, name='ride_detail'),
    path('my-rides/', views.my_rides, name='my_rides'),
    
    # Booking management
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    
    # Route and map (this connects to your teammate's work)
    path('map/', views.route_map, name='route_map'),
    
    # Reviews
    path('ride/<int:ride_id>/review/', views.leave_review, name='leave_review'),
    
    # API endpoints
    path('api/cities/', views.api_cities, name='api_cities'),
    path('api/validate-location/', views.api_validate_location, name='api_validate_location'),
]