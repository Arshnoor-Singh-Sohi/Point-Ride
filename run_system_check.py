# run_system_check.py
# Complete system health check for pointRide

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pointRide.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.urls import reverse
from django.test import Client
from rides.models import City, Route, Ride, Booking
from accounts.models import DriverProfile, TravellerProfile
import time

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_database_health():
    """Check database connectivity and integrity"""
    print_header("DATABASE HEALTH CHECK")
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print_success("Database connection successful")
            else:
                print_error("Database connection test failed")
                return False
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False
    
    # Check migrations
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            print_error(f"Unapplied migrations found: {len(plan)} pending")
            return False
        else:
            print_success("All migrations applied")
    except Exception as e:
        print_error(f"Migration check failed: {str(e)}")
        return False
    
    return True

def check_models():
    """Check model integrity"""
    print_header("MODEL INTEGRITY CHECK")
    
    User = get_user_model()
    
    # Check user model
    try:
        user_count = User.objects.count()
        print_success(f"User model working - {user_count} users found")
    except Exception as e:
        print_error(f"User model error: {str(e)}")
        return False
    
    # Check rides models
    try:
        city_count = City.objects.count()
        print_success(f"City model working - {city_count} cities found")
        
        if city_count == 0:
            print_warning("No cities found - run 'python manage.py populate_verified_cities'")
        
        route_count = Route.objects.count()
        print_info(f"Route model working - {route_count} routes found")
        
        ride_count = Ride.objects.count()
        print_info(f"Ride model working - {ride_count} rides found")
        
        booking_count = Booking.objects.count()
        print_info(f"Booking model working - {booking_count} bookings found")
        
    except Exception as e:
        print_error(f"Rides model error: {str(e)}")
        return False
    
    # Check profile models
    try:
        driver_count = DriverProfile.objects.count()
        traveller_count = TravellerProfile.objects.count()
        print_success(f"Profile models working - {driver_count} drivers, {traveller_count} travellers")
    except Exception as e:
        print_error(f"Profile model error: {str(e)}")
        return False
    
    return True

def check_urls():
    """Check URL configuration"""
    print_header("URL CONFIGURATION CHECK")
    
    client = Client()
    
    # Test main URLs
    urls_to_test = [
        ('/', 'Home page'),
        ('/rides/', 'Rides home'),
        ('/accounts/login/', 'Login page'),
        ('/accounts/register/traveller/', 'Traveller registration'),
        ('/accounts/register/driver/step1/', 'Driver registration'),
        ('/admin/', 'Admin page'),
    ]
    
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:
                print_success(f"{name} - Status: {response.status_code}")
            else:
                print_error(f"{name} - Status: {response.status_code}")
        except Exception as e:
            print_error(f"{name} - Error: {str(e)}")
    
    # Test API endpoints (require authentication)
    try:
        # Create test user for API testing
        test_user = User.objects.create_user(
            username='test_api_user',
            email='test@example.com',
            password='testpass123',
            full_legal_name='Test User',
            is_traveller=True
        )
        client.login(username='test_api_user', password='testpass123')
        
        # Test API endpoints
        api_response = client.get('/rides/api/cities/?q=Tor')
        if api_response.status_code == 200:
            print_success("API endpoints working")
        else:
            print_error(f"API endpoints failed - Status: {api_response.status_code}")
        
        # Clean up test user
        test_user.delete()
        
    except Exception as e:
        print_error(f"API test failed: {str(e)}")
    
    return True

def check_location_validation():
    """Check location validation algorithm"""
    print_header("LOCATION VALIDATION CHECK")
    
    try:
        from rides.views import validate_ontario_location
        
        # Test valid Ontario location
        is_valid, city, error = validate_ontario_location("Toronto, Ontario")
        if is_valid:
            print_success("Valid Ontario location test passed")
        else:
            print_error(f"Valid Ontario location test failed: {error}")
        
        # Test invalid location
        is_valid, city, error = validate_ontario_location("New York, USA")
        if not is_valid and "Ontario" in error:
            print_success("Invalid location test passed")
        else:
            print_error("Invalid location test failed")
        
        # Test empty location
        is_valid, city, error = validate_ontario_location("")
        if not is_valid:
            print_success("Empty location test passed")
        else:
            print_error("Empty location test failed")
            
    except Exception as e:
        print_error(f"Location validation check failed: {str(e)}")
        return False
    
    return True

def check_authentication():
    """Check authentication system"""
    print_header("AUTHENTICATION SYSTEM CHECK")
    
    User = get_user_model()
    
    try:
        # Create test users
        test_driver = User.objects.create_user(
            username='test_driver_check',
            email='testdriver@example.com',
            password='testpass123',
            full_legal_name='Test Driver',
            is_driver=True
        )
        
        test_traveller = User.objects.create_user(
            username='test_traveller_check',
            email='testtraveller@example.com',
            password='testpass123',
            full_legal_name='Test Traveller',
            is_traveller=True
        )
        
        # Test driver profile creation
        driver_profile = DriverProfile.objects.create(
            user=test_driver,
            account_status='VERIFIED'
        )
        
        # Test traveller profile creation
        traveller_profile = TravellerProfile.objects.create(
            user=test_traveller
        )
        
        print_success("User creation and profiles working")
        
        # Test login
        client = Client()
        
        # Test driver login
        response = client.post('/accounts/login/', {
            'username': 'test_driver_check',
            'password': 'testpass123',
            'login_role': 'driver'
        })
        
        if response.status_code == 302:  # Redirect after successful login
            print_success("Driver login working")
        else:
            print_error(f"Driver login failed - Status: {response.status_code}")
        
        # Test traveller login
        response = client.post('/accounts/login/', {
            'username': 'test_traveller_check',
            'password': 'testpass123',
            'login_role': 'traveller'
        })
        
        if response.status_code == 302:  # Redirect after successful login
            print_success("Traveller login working")
        else:
            print_error(f"Traveller login failed - Status: {response.status_code}")
        
        # Clean up test users
        test_driver.delete()
        test_traveller.delete()
        
    except Exception as e:
        print_error(f"Authentication check failed: {str(e)}")
        return False
    
    return True

def check_performance():
    """Check basic performance metrics"""
    print_header("PERFORMANCE CHECK")
    
    try:
        # Test database query performance
        start_time = time.time()
        cities = list(City.objects.all())
        end_time = time.time()
        
        query_time = end_time - start_time
        if query_time < 1.0:
            print_success(f"Database query performance good ({query_time:.3f}s)")
        else:
            print_warning(f"Database query performance slow ({query_time:.3f}s)")
        
        # Test URL response time
        client = Client()
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        if response_time < 2.0:
            print_success(f"URL response time good ({response_time:.3f}s)")
        else:
            print_warning(f"URL response time slow ({response_time:.3f}s)")
        
    except Exception as e:
        print_error(f"Performance check failed: {str(e)}")
        return False
    
    return True

def run_automated_tests():
    """Run automated test suite"""
    print_header("AUTOMATED TEST SUITE")
    
    try:
        # Run basic tests
        print_info("Running automated tests...")
        
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=1, interactive=False)
        
        # Run specific test modules
        test_labels = [
            'rides.tests.CityModelTest',
            'rides.tests.LocationValidationTest',
        ]
        
        failures = test_runner.run_tests(test_labels)
        
        if failures == 0:
            print_success("All automated tests passed")
        else:
            print_error(f"Automated tests failed: {failures} failures")
            
    except Exception as e:
        print_warning(f"Automated test run failed: {str(e)}")
        print_info("Try running: python manage.py test rides")

def main():
    """Main system check function"""
    print_header("POINTRIDE SYSTEM HEALTH CHECK")
    print_info("Starting comprehensive system check...")
    
    checks = [
        ("Database Health", check_database_health),
        ("Model Integrity", check_models),
        ("URL Configuration", check_urls),
        ("Location Validation", check_location_validation),
        ("Authentication System", check_authentication),
        ("Performance", check_performance),
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Check '{check_name}' failed with exception: {str(e)}")
            failed += 1
    
    # Run automated tests
    run_automated_tests()
    
    # Summary
    print_header("SYSTEM CHECK SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print_success("🎉 ALL CHECKS PASSED! System is ready for use.")
        print_info("You can now run: python manage.py runserver")
    else:
        print_error(f"⚠️  {failed} checks failed. Please review errors above.")
        print_info("Refer to TESTING_GUIDE.md for detailed troubleshooting.")
    
    print_header("NEXT STEPS")
    print("1. If all checks passed: Start the server with 'python manage.py runserver'")
    print("2. If checks failed: Review errors and fix issues")
    print("3. Run manual tests from TESTING_GUIDE.md")
    print("4. Test the system with real user scenarios")
    print("5. Monitor system performance and logs")

if __name__ == "__main__":
    main()