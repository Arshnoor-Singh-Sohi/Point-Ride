# test_complete_system.py
# Complete system verification after fixing views

import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pointRide.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import DriverProfile, TravellerProfile

def clean_test_users():
    """Clean up any existing test users"""
    User = get_user_model()
    test_usernames = [
        'test_traveller_final', 'test_driver_final', 
        'demo_traveller', 'demo_driver'
    ]
    
    for username in test_usernames:
        User.objects.filter(username=username).delete()
    
    print("✅ Cleaned up existing test users")

def test_registration():
    """Test registration for both user types"""
    client = Client()
    
    print("\n📝 TESTING REGISTRATION")
    print("=" * 40)
    
    # Test Traveller Registration
    print("\n1. Testing Traveller Registration...")
    traveller_data = {
        'username': 'test_traveller_final',
        'email': 'traveller@final.test',
        'password1': 'testpass123!',
        'password2': 'testpass123!',
        'full_legal_name': 'Final Test Traveller',
        'current_home_address': '123 Final Test St',
        'starting_city': 'Toronto',
        'bio': 'Final test traveller account'
    }
    
    response = client.post('/accounts/register/traveller/', traveller_data, follow=True)
    
    if response.status_code == 200:
        # Check if user was created
        User = get_user_model()
        try:
            user = User.objects.get(username='test_traveller_final')
            print(f"✅ Traveller user created: {user.username}")
            print(f"   is_traveller: {user.is_traveller}")
            print(f"   is_driver: {user.is_driver}")
            
            # Check profile
            profile = TravellerProfile.objects.filter(user=user).first()
            if profile:
                print("✅ TravellerProfile created")
            else:
                print("❌ TravellerProfile NOT created")
                
        except User.DoesNotExist:
            print("❌ Traveller user NOT created")
    else:
        print(f"❌ Traveller registration failed: {response.status_code}")
    
    # Test Driver Registration
    print("\n2. Testing Driver Registration...")
    driver_data = {
        'username': 'test_driver_final',
        'email': 'driver@final.test',
        'password1': 'testpass123!',
        'password2': 'testpass123!',
        'full_legal_name': 'Final Test Driver',
        'current_home_address': '456 Final Test Ave',
        'starting_city': 'Ottawa',
        'bio': 'Final test driver account'
    }
    
    response = client.post('/accounts/register/driver/step1/', driver_data, follow=True)
    
    if response.status_code == 200:
        # Check if user was created
        try:
            user = User.objects.get(username='test_driver_final')
            print(f"✅ Driver user created: {user.username}")
            print(f"   is_traveller: {user.is_traveller}")
            print(f"   is_driver: {user.is_driver}")
            
            # Check profile
            profile = DriverProfile.objects.filter(user=user).first()
            if profile:
                print(f"✅ DriverProfile created (status: {profile.account_status})")
            else:
                print("❌ DriverProfile NOT created")
                
        except User.DoesNotExist:
            print("❌ Driver user NOT created")
    else:
        print(f"❌ Driver registration failed: {response.status_code}")

def test_login():
    """Test login functionality"""
    client = Client()
    
    print("\n🔐 TESTING LOGIN SYSTEM")
    print("=" * 40)
    
    # Test Traveller Login
    print("\n1. Testing Traveller Login...")
    login_data = {
        'username': 'test_traveller_final',
        'password': 'testpass123!',
        'login_role': 'traveller'
    }
    
    response = client.post('/accounts/login/', login_data, follow=True)
    
    if response.status_code == 200 and 'dashboard' in response.request['PATH_INFO']:
        print("✅ Traveller login successful")
    else:
        print(f"❌ Traveller login failed: {response.status_code}")
        print(f"   Redirected to: {response.request['PATH_INFO']}")
    
    client.logout()
    
    # Test Driver Login
    print("\n2. Testing Driver Login...")
    login_data = {
        'username': 'test_driver_final',
        'password': 'testpass123!',
        'login_role': 'driver'
    }
    
    response = client.post('/accounts/login/', login_data, follow=True)
    
    if response.status_code == 200 and 'dashboard' in response.request['PATH_INFO']:
        print("✅ Driver login successful")
    else:
        print(f"❌ Driver login failed: {response.status_code}")
        print(f"   Redirected to: {response.request['PATH_INFO']}")

def test_role_validation():
    """Test role validation in login"""
    client = Client()
    
    print("\n🛡️ TESTING ROLE VALIDATION")
    print("=" * 40)
    
    # Test traveller trying to login as driver (should fail)
    print("\n1. Testing role mismatch (traveller as driver)...")
    login_data = {
        'username': 'test_traveller_final',
        'password': 'testpass123!',
        'login_role': 'driver'  # Wrong role
    }
    
    response = client.post('/accounts/login/', login_data)
    
    if response.status_code == 200 and 'login' in response.request['PATH_INFO']:
        print("✅ Role validation working (traveller rejected as driver)")
    else:
        print("⚠️ Role validation may not be working")
    
    # Test driver trying to login as traveller (should fail)
    print("\n2. Testing role mismatch (driver as traveller)...")
    login_data = {
        'username': 'test_driver_final',
        'password': 'testpass123!',
        'login_role': 'traveller'  # Wrong role
    }
    
    response = client.post('/accounts/login/', login_data)
    
    if response.status_code == 200 and 'login' in response.request['PATH_INFO']:
        print("✅ Role validation working (driver rejected as traveller)")
    else:
        print("⚠️ Role validation may not be working")

def test_dashboard_access():
    """Test dashboard access and permissions"""
    client = Client()
    
    print("\n🏠 TESTING DASHBOARD ACCESS")
    print("=" * 40)
    
    # Login as traveller and test dashboard access
    print("\n1. Testing traveller dashboard access...")
    client.login(username='test_traveller_final', password='testpass123!')
    
    response = client.get('/accounts/dashboard/traveller/')
    if response.status_code == 200:
        print("✅ Traveller dashboard accessible")
    else:
        print(f"❌ Traveller dashboard failed: {response.status_code}")
    
    # Test driver dashboard access (should be denied)
    response = client.get('/accounts/dashboard/driver/')
    if response.status_code == 302 or response.status_code == 403:
        print("✅ Driver dashboard properly blocked for traveller")
    else:
        print("⚠️ Driver dashboard not properly protected")
    
    client.logout()
    
    # Login as driver and test dashboard access
    print("\n2. Testing driver dashboard access...")
    client.login(username='test_driver_final', password='testpass123!')
    
    response = client.get('/accounts/dashboard/driver/')
    if response.status_code == 200:
        print("✅ Driver dashboard accessible")
    else:
        print(f"❌ Driver dashboard failed: {response.status_code}")
    
    # Test traveller dashboard access (should be denied)
    response = client.get('/accounts/dashboard/traveller/')
    if response.status_code == 302 or response.status_code == 403:
        print("✅ Traveller dashboard properly blocked for driver")
    else:
        print("⚠️ Traveller dashboard not properly protected")

def test_profile_consistency():
    """Test profile consistency"""
    User = get_user_model()
    
    print("\n📊 TESTING PROFILE CONSISTENCY")
    print("=" * 40)
    
    # Check all test users
    test_users = User.objects.filter(
        username__in=['test_traveller_final', 'test_driver_final']
    )
    
    for user in test_users:
        print(f"\n👤 User: {user.username}")
        print(f"   Flags: driver={user.is_driver}, traveller={user.is_traveller}")
        
        driver_profiles = DriverProfile.objects.filter(user=user).count()
        traveller_profiles = TravellerProfile.objects.filter(user=user).count()
        
        print(f"   Profiles: driver={driver_profiles}, traveller={traveller_profiles}")
        
        # Check consistency
        if user.is_driver and not user.is_traveller:
            if driver_profiles == 1 and traveller_profiles == 0:
                print("   ✅ CONSISTENT: Driver user with driver profile only")
            else:
                print("   ❌ INCONSISTENT: Driver user has wrong profiles")
        elif user.is_traveller and not user.is_driver:
            if traveller_profiles == 1 and driver_profiles == 0:
                print("   ✅ CONSISTENT: Traveller user with traveller profile only")
            else:
                print("   ❌ INCONSISTENT: Traveller user has wrong profiles")
        else:
            print("   ❌ INCONSISTENT: User has multiple or no roles")

def generate_summary():
    """Generate final test summary"""
    User = get_user_model()
    
    print("\n📈 FINAL TEST SUMMARY")
    print("=" * 50)
    
    total_users = User.objects.count()
    drivers = User.objects.filter(is_driver=True).count()
    travellers = User.objects.filter(is_traveller=True).count()
    both_roles = User.objects.filter(is_driver=True, is_traveller=True).count()
    
    driver_profiles = DriverProfile.objects.count()
    traveller_profiles = TravellerProfile.objects.count()
    
    print(f"👥 Total Users: {total_users}")
    print(f"🚗 Drivers: {drivers}")
    print(f"✈️ Travellers: {travellers}")
    print(f"⚠️ Dual Role Users: {both_roles}")
    print(f"📝 Driver Profiles: {driver_profiles}")
    print(f"📝 Traveller Profiles: {traveller_profiles}")
    
    # Health indicators
    print(f"\n🏥 SYSTEM HEALTH:")
    if both_roles == 0:
        print("✅ No users with conflicting roles")
    else:
        print("❌ Users with conflicting roles found")
    
    if drivers == driver_profiles and travellers == traveller_profiles:
        print("✅ Profile counts match user flags")
    else:
        print("❌ Profile counts don't match user flags")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. If all tests passed: System is ready for use")
    print("2. Test with manual browser testing")
    print("3. Run: python manage.py runserver")
    print("4. Visit: http://localhost:8000/accounts/health/")

def main():
    """Run complete system test"""
    print("🚀 COMPLETE SYSTEM TEST - FIXED VIEWS")
    print("=" * 60)
    
    try:
        clean_test_users()
        test_registration()
        test_login()
        test_role_validation()
        test_dashboard_access()
        test_profile_consistency()
        generate_summary()
        
        print("\n🎉 TESTING COMPLETED!")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()