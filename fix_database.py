# fix_database.py
# Run this script to fix database integrity issues

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pointRide.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from accounts.models import TravellerProfile, DriverProfile

def fix_database():
    """Fix database integrity issues"""
    print("🔧 Fixing database integrity issues...")
    
    # Method 1: Clean up orphaned profiles
    print("\n1. Cleaning up orphaned profiles...")
    
    User = get_user_model()
    
    # Find orphaned traveller profiles
    orphaned_traveller_profiles = []
    for profile in TravellerProfile.objects.all():
        try:
            if not User.objects.filter(id=profile.user_id).exists():
                orphaned_traveller_profiles.append(profile)
        except:
            orphaned_traveller_profiles.append(profile)
    
    if orphaned_traveller_profiles:
        print(f"   Found {len(orphaned_traveller_profiles)} orphaned traveller profiles")
        for profile in orphaned_traveller_profiles:
            print(f"   Deleting orphaned TravellerProfile (ID: {profile.id}, User ID: {profile.user_id})")
            profile.delete()
    
    # Find orphaned driver profiles
    orphaned_driver_profiles = []
    for profile in DriverProfile.objects.all():
        try:
            if not User.objects.filter(id=profile.user_id).exists():
                orphaned_driver_profiles.append(profile)
        except:
            orphaned_driver_profiles.append(profile)
    
    if orphaned_driver_profiles:
        print(f"   Found {len(orphaned_driver_profiles)} orphaned driver profiles")
        for profile in orphaned_driver_profiles:
            print(f"   Deleting orphaned DriverProfile (ID: {profile.id}, User ID: {profile.user_id})")
            profile.delete()
    
    print("✅ Database cleanup completed!")
    
    # Method 2: Reset migrations if needed
    print("\n2. Checking migration status...")
    
    with connection.cursor() as cursor:
        # Check if django_migrations table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='django_migrations'
        """)
        
        if cursor.fetchone():
            print("   Migrations table exists - checking for rides app...")
            cursor.execute("""
                SELECT * FROM django_migrations 
                WHERE app = 'rides'
            """)
            
            rides_migrations = cursor.fetchall()
            if rides_migrations:
                print(f"   Found {len(rides_migrations)} rides migrations")
            else:
                print("   No rides migrations found")
        else:
            print("   No migrations table found")
    
    print("\n🎉 Database is ready for migration!")

if __name__ == "__main__":
    fix_database()