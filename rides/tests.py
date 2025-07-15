# rides/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, time, timedelta
from decimal import Decimal
import json

from .models import City, Route, Ride, Booking, RideReview
from .forms import LocationSearchForm, RideSearchForm, RideCreateForm, BookingForm
from accounts.models import DriverProfile, TravellerProfile

User = get_user_model()

class CityModelTest(TestCase):
    """Test City model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.city_data = {
            'name': 'Toronto',
            'province': 'Ontario',
            'country': 'Canada',
            'latitude': Decimal('43.6532'),
            'longitude': Decimal('-79.3832'),
            'is_active': True
        }
    
    def test_city_creation(self):
        """Test creating a city"""
        city = City.objects.create(**self.city_data)
        self.assertEqual(city.name, 'Toronto')
        self.assertEqual(city.province, 'Ontario')
        self.assertEqual(city.country, 'Canada')
        self.assertTrue(city.is_active)
    
    def test_city_str_method(self):
        """Test city string representation"""
        city = City.objects.create(**self.city_data)
        self.assertEqual(str(city), "Toronto, Ontario")
    
    def test_city_unique_constraint(self):
        """Test that city names are unique"""
        City.objects.create(**self.city_data)
        with self.assertRaises(IntegrityError):
            City.objects.create(**self.city_data)
    
    def test_city_ordering(self):
        """Test city ordering"""
        City.objects.create(name='Zulu', province='Ontario', country='Canada')
        City.objects.create(name='Alpha', province='Ontario', country='Canada')
        cities = City.objects.all()
        self.assertEqual(cities[0].name, 'Alpha')
        self.assertEqual(cities[1].name, 'Zulu')

class RideModelTest(TestCase):
    """Test Ride model functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and driver profile
        self.user = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            full_legal_name='Test Driver',
            is_driver=True
        )
        self.driver_profile = DriverProfile.objects.create(
            user=self.user,
            account_status='VERIFIED'
        )
        
        # Create test cities
        self.toronto = City.objects.create(
            name='Toronto',
            province='Ontario',
            country='Canada',
            latitude=43.6532,
            longitude=-79.3832
        )
        self.ottawa = City.objects.create(
            name='Ottawa',
            province='Ontario',
            country='Canada',
            latitude=45.4215,
            longitude=-75.6972
        )
        
        # Create test route
        self.route = Route.objects.create(
            driver=self.user,
            origin_city=self.toronto,
            destination_city=self.ottawa,
            driver_price=Decimal('50.00')
        )
    
    def test_ride_creation(self):
        """Test creating a ride"""
        ride = Ride.objects.create(
            route=self.route,
            driver=self.user,
            departure_date=date.today() + timedelta(days=1),
            departure_time=time(9, 0),
            available_seats=4,
            pickup_location='Union Station',
            pickup_city=self.toronto,
            dropoff_location='Rideau Centre',
            dropoff_city=self.ottawa,
            price_per_seat=Decimal('25.00')
        )
        
        self.assertEqual(ride.driver, self.user)
        self.assertEqual(ride.pickup_city, self.toronto)
        self.assertEqual(ride.dropoff_city, self.ottawa)
        self.assertEqual(ride.status, 'ACTIVE')
    
    def test_ride_available_seats_count(self):
        """Test available seats calculation"""
        ride = Ride.objects.create(
            route=self.route,
            driver=self.user,
            departure_date=date.today() + timedelta(days=1),
            departure_time=time(9, 0),
            available_seats=4,
            pickup_location='Union Station',
            pickup_city=self.toronto,
            dropoff_location='Rideau Centre',
            dropoff_city=self.ottawa,
            price_per_seat=Decimal('25.00')
        )
        
        # Initially all seats available
        self.assertEqual(ride.available_seats_count, 4)
        
        # Create a traveller and booking
        traveller = User.objects.create_user(
            username='testtraveller',
            email='traveller@test.com',
            password='testpass123',
            full_legal_name='Test Traveller',
            is_traveller=True
        )
        
        booking = Booking.objects.create(
            ride=ride,
            traveller=traveller,
            seats_booked=2,
            status='CONFIRMED'
        )
        
        # Should have 2 seats left
        self.assertEqual(ride.available_seats_count, 2)
    
    def test_ride_is_full_property(self):
        """Test is_full property"""
        ride = Ride.objects.create(
            route=self.route,
            driver=self.user,
            departure_date=date.today() + timedelta(days=1),
            departure_time=time(9, 0),
            available_seats=2,
            pickup_location='Union Station',
            pickup_city=self.toronto,
            dropoff_location='Rideau Centre',
            dropoff_city=self.ottawa,
            price_per_seat=Decimal('25.00')
        )
        
        self.assertFalse(ride.is_full)
        
        # Create a traveller and fill all seats
        traveller = User.objects.create_user(
            username='testtraveller',
            email='traveller@test.com',
            password='testpass123',
            full_legal_name='Test Traveller',
            is_traveller=True
        )
        
        booking = Booking.objects.create(
            ride=ride,
            traveller=traveller,
            seats_booked=2,
            status='CONFIRMED'
        )
        
        self.assertTrue(ride.is_full)

class BookingModelTest(TestCase):
    """Test Booking model functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create driver
        self.driver = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            full_legal_name='Test Driver',
            is_driver=True
        )
        
        # Create traveller
        self.traveller = User.objects.create_user(
            username='testtraveller',
            email='traveller@test.com',
            password='testpass123',
            full_legal_name='Test Traveller',
            is_traveller=True
        )
        
        # Create cities
        self.toronto = City.objects.create(name='Toronto', province='Ontario', country='Canada')
        self.ottawa = City.objects.create(name='Ottawa', province='Ontario', country='Canada')
        
        # Create route
        self.route = Route.objects.create(
            driver=self.driver,
            origin_city=self.toronto,
            destination_city=self.ottawa,
            driver_price=Decimal('50.00')
        )
        
        # Create ride
        self.ride = Ride.objects.create(
            route=self.route,
            driver=self.driver,
            departure_date=date.today() + timedelta(days=1),
            departure_time=time(9, 0),
            available_seats=4,
            pickup_location='Union Station',
            pickup_city=self.toronto,
            dropoff_location='Rideau Centre',
            dropoff_city=self.ottawa,
            price_per_seat=Decimal('25.00')
        )
    
    def test_booking_creation(self):
        """Test creating a booking"""
        booking = Booking.objects.create(
            ride=self.ride,
            traveller=self.traveller,
            seats_booked=2
        )
        
        self.assertEqual(booking.ride, self.ride)
        self.assertEqual(booking.traveller, self.traveller)
        self.assertEqual(booking.seats_booked, 2)
        self.assertEqual(booking.status, 'PENDING')
        self.assertEqual(booking.total_price, Decimal('50.00'))  # 2 seats * $25
    
    def test_booking_auto_price_calculation(self):
        """Test automatic price calculation"""
        booking = Booking.objects.create(
            ride=self.ride,
            traveller=self.traveller,
            seats_booked=3
        )
        
        # Should automatically calculate total price
        self.assertEqual(booking.total_price, Decimal('75.00'))  # 3 seats * $25
    
    def test_booking_unique_constraint(self):
        """Test that user can't book the same ride twice"""
        Booking.objects.create(
            ride=self.ride,
            traveller=self.traveller,
            seats_booked=1
        )
        
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                ride=self.ride,
                traveller=self.traveller,
                seats_booked=1
            )

class LocationValidationTest(TestCase):
    """Test location validation algorithm"""
    
    def setUp(self):
        """Set up test data"""
        from rides.views import validate_ontario_location
        self.validate_func = validate_ontario_location
        
        # Create test cities
        City.objects.create(name='Toronto', province='Ontario', country='Canada')
        City.objects.create(name='Ottawa', province='Ontario', country='Canada')
    
    def test_valid_ontario_location(self):
        """Test valid Ontario location"""
        is_valid, city, error = self.validate_func('Toronto, Ontario')
        self.assertTrue(is_valid)
        self.assertEqual(city.name, 'Toronto')
        self.assertIsNone(error)
    
    def test_invalid_empty_location(self):
        """Test empty location"""
        is_valid, city, error = self.validate_func('')
        self.assertFalse(is_valid)
        self.assertIsNone(city)
        self.assertEqual(error, "Location cannot be empty")
    
    def test_invalid_international_location(self):
        """Test international location"""
        is_valid, city, error = self.validate_func('New York, USA')
        self.assertFalse(is_valid)
        self.assertIsNone(city)
        self.assertEqual(error, "We currently only provide service in Ontario, Canada.")
    
    def test_unserved_location(self):
        """Test location not in served cities"""
        is_valid, city, error = self.validate_func('UnknownCity, Ontario')
        self.assertFalse(is_valid)
        self.assertIsNone(city)
        self.assertIn("We don't serve that location yet", error)

class RideViewTest(TestCase):
    """Test ride views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.driver = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            full_legal_name='Test Driver',
            is_driver=True
        )
        
        self.traveller = User.objects.create_user(
            username='testtraveller',
            email='traveller@test.com',
            password='testpass123',
            full_legal_name='Test Traveller',
            is_traveller=True
        )
        
        # Create cities
        self.toronto = City.objects.create(name='Toronto', province='Ontario', country='Canada')
        self.ottawa = City.objects.create(name='Ottawa', province='Ontario', country='Canada')
    
    def test_home_search_view(self):
        """Test home search view"""
        response = self.client.get(reverse('rides:home_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Where do you want to go?')
    
    def test_search_rides_view(self):
        """Test search rides view"""
        response = self.client.get(reverse('rides:search_rides'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Results')
    
    def test_create_ride_view_requires_login(self):
        """Test create ride view requires login"""
        response = self.client.get(reverse('rides:create_ride'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_ride_view_driver_only(self):
        """Test create ride view is for drivers only"""
        self.client.login(username='testtraveller', password='testpass123')
        response = self.client.get(reverse('rides:create_ride'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_create_ride_view_success(self):
        """Test successful ride creation"""
        self.client.login(username='testdriver', password='testpass123')
        response = self.client.get(reverse('rides:create_ride'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Ride')

class APIEndpointTest(TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            full_legal_name='Test User',
            is_traveller=True
        )
        
        # Create cities
        City.objects.create(name='Toronto', province='Ontario', country='Canada')
        City.objects.create(name='Ottawa', province='Ontario', country='Canada')
        City.objects.create(name='Hamilton', province='Ontario', country='Canada')
    
    def test_api_cities_endpoint(self):
        """Test cities API endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('rides:api_cities'), {'q': 'Tor'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Toronto')
    
    def test_api_validate_location_endpoint(self):
        """Test location validation API endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('rides:api_validate_location'), 
            {'location': 'Toronto, Ontario'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['is_valid'])
        self.assertEqual(data['nearest_city'], 'Toronto')

class FormTest(TestCase):
    """Test forms"""
    
    def setUp(self):
        """Set up test data"""
        self.toronto = City.objects.create(name='Toronto', province='Ontario', country='Canada')
        self.ottawa = City.objects.create(name='Ottawa', province='Ontario', country='Canada')
    
    def test_location_search_form_valid(self):
        """Test valid location search form"""
        form_data = {
            'pickup_location': 'Toronto, Ontario',
            'dropoff_location': 'Ottawa, Ontario'
        }
        form = LocationSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_location_search_form_same_locations(self):
        """Test location search form with same pickup and dropoff"""
        form_data = {
            'pickup_location': 'Toronto, Ontario',
            'dropoff_location': 'Toronto, Ontario'
        }
        form = LocationSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Pickup and drop-off locations must be different', str(form.errors))
    
    def test_ride_search_form_valid(self):
        """Test valid ride search form"""
        form_data = {
            'pickup_city': self.toronto.id,
            'dropoff_city': self.ottawa.id,
            'departure_date': date.today() + timedelta(days=1),
            'passengers': 2
        }
        form = RideSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_ride_search_form_past_date(self):
        """Test ride search form with past date"""
        form_data = {
            'pickup_city': self.toronto.id,
            'dropoff_city': self.ottawa.id,
            'departure_date': date.today() - timedelta(days=1),
            'passengers': 2
        }
        form = RideSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Departure date cannot be in the past', str(form.errors))

class IntegrationTest(TestCase):
    """Integration tests for complete user workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create driver
        self.driver = User.objects.create_user(
            username='testdriver',
            email='driver@test.com',
            password='testpass123',
            full_legal_name='Test Driver',
            is_driver=True
        )
        DriverProfile.objects.create(user=self.driver, account_status='VERIFIED')
        
        # Create traveller
        self.traveller = User.objects.create_user(
            username='testtraveller',
            email='traveller@test.com',
            password='testpass123',
            full_legal_name='Test Traveller',
            is_traveller=True
        )
        TravellerProfile.objects.create(user=self.traveller)
        
        # Create cities
        self.toronto = City.objects.create(name='Toronto', province='Ontario', country='Canada')
        self.ottawa = City.objects.create(name='Ottawa', province='Ontario', country='Canada')
    
    def test_complete_booking_workflow(self):
        """Test complete booking workflow from driver creating ride to traveller booking"""
        
        # 1. Driver logs in and creates a ride
        self.client.login(username='testdriver', password='testpass123')
        
        ride_data = {
            'pickup_city': self.toronto.id,
            'dropoff_city': self.ottawa.id,
            'pickup_location': 'Union Station',
            'dropoff_location': 'Rideau Centre',
            'departure_date': date.today() + timedelta(days=1),
            'departure_time': '09:00',
            'available_seats': 4,
            'price_per_seat': '25.00',
            'notes': 'Test ride'
        }
        
        response = self.client.post(reverse('rides:create_ride'), ride_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Verify ride was created
        ride = Ride.objects.get(driver=self.driver)
        self.assertEqual(ride.pickup_city, self.toronto)
        self.assertEqual(ride.dropoff_city, self.ottawa)
        
        # 2. Traveller logs in and searches for rides
        self.client.login(username='testtraveller', password='testpass123')
        
        search_data = {
            'pickup_city': self.toronto.id,
            'dropoff_city': self.ottawa.id,
            'departure_date': date.today() + timedelta(days=1),
            'passengers': 2
        }
        
        response = self.client.post(reverse('rides:search_rides'), search_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Driver')
        
        # 3. Traveller books the ride
        booking_data = {
            'book_ride': True,
            'seats_booked': 2,
            'booking_notes': 'Test booking'
        }
        
        response = self.client.post(
            reverse('rides:ride_detail', kwargs={'ride_id': ride.id}), 
            booking_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful booking
        
        # Verify booking was created
        booking = Booking.objects.get(traveller=self.traveller, ride=ride)
        self.assertEqual(booking.seats_booked, 2)
        self.assertEqual(booking.status, 'PENDING')
        self.assertEqual(booking.total_price, Decimal('50.00'))
        
        # 4. Driver confirms the booking
        self.client.login(username='testdriver', password='testpass123')
        
        response = self.client.post(
            reverse('rides:booking_detail', kwargs={'booking_id': booking.id}),
            {'action': 'confirm'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify booking was confirmed
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertIsNotNone(booking.confirmed_at)

# Performance Tests
class PerformanceTest(TestCase):
    """Performance tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create multiple cities
        cities = []
        for i in range(50):
            city = City.objects.create(
                name=f'City{i}',
                province='Ontario',
                country='Canada',
                latitude=43.0 + i * 0.1,
                longitude=-79.0 + i * 0.1
            )
            cities.append(city)
        
        # Create multiple users
        for i in range(20):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='testpass123',
                full_legal_name=f'User {i}',
                is_driver=i % 2 == 0,
                is_traveller=i % 2 == 1
            )
    
    def test_city_search_performance(self):
        """Test city search performance"""
        import time
        
        start_time = time.time()
        
        # Simulate multiple searches
        for i in range(100):
            City.objects.filter(name__icontains=f'City{i % 10}')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 1 second
        self.assertLess(execution_time, 1.0)

# Run specific test categories
def run_model_tests():
    """Run model tests specifically"""
    from django.test.utils import get_runner
    from django.conf import settings
    import sys
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    test_labels = [
        'rides.tests.CityModelTest',
        'rides.tests.RideModelTest',
        'rides.tests.BookingModelTest',
    ]
    
    failures = test_runner.run_tests(test_labels)
    if failures:
        sys.exit(bool(failures))

def run_view_tests():
    """Run view tests specifically"""
    from django.test.utils import get_runner
    from django.conf import settings
    import sys
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    test_labels = [
        'rides.tests.RideViewTest',
        'rides.tests.APIEndpointTest',
    ]
    
    failures = test_runner.run_tests(test_labels)
    if failures:
        sys.exit(bool(failures))

def run_integration_tests():
    """Run integration tests specifically"""
    from django.test.utils import get_runner
    from django.conf import settings
    import sys
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    test_labels = [
        'rides.tests.IntegrationTest',
    ]
    
    failures = test_runner.run_tests(test_labels)
    if failures:
        sys.exit(bool(failures))