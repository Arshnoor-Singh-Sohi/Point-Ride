# test_location_validation.py
# Run this to test the location validation algorithm

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pointRide.settings')
django.setup()

from rides.views import enhanced_ontario_validation, quick_ontario_check

def test_location_validation():
    """Test the location validation algorithm"""
    
    print("🧪 Testing Location Validation Algorithm")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # Valid Ontario locations
        ("Toronto", "Should find exact match"),
        ("Toronto, Ontario", "Should find Toronto"),
        ("University of Toronto", "Should find nearest city (Toronto)"),
        ("123 King Street, Toronto", "Should validate address in Toronto"),
        ("Ottawa City Hall", "Should find Ottawa"),
        
        # Invalid locations
        ("", "Should reject empty location"),
        ("Montreal, Quebec", "Should reject Quebec location"),
        ("New York, USA", "Should reject US location"),
        ("UnknownCityName", "Should reject unknown location"),
        
        # Edge cases
        ("Tor", "Should suggest Toronto"),
        ("Hamilton ON", "Should find Hamilton"),
    ]
    
    print("\n🔍 Testing Enhanced Ontario Validation:")
    print("-" * 40)
    
    for location, expected in test_cases:
        print(f"\nTesting: '{location}'")
        print(f"Expected: {expected}")
        
        try:
            is_valid, nearest_city, distance, error = enhanced_ontario_validation(location)
            
            if is_valid:
                city_name = nearest_city.name if nearest_city else "None"
                distance_str = f"{distance}km" if distance else "0km"
                print(f"✅ VALID: {city_name} ({distance_str})")
            else:
                print(f"❌ INVALID: {error}")
                
        except Exception as e:
            print(f"🔥 ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🚀 Quick Ontario Check Tests:")
    print("-" * 40)
    
    quick_test_cases = [
        "Toronto",
        "Tor",
        "Ottawa",
        "Quebec",
        "Hamilton",
        "",
    ]
    
    for location in quick_test_cases:
        print(f"\nQuick test: '{location}'")
        try:
            is_valid, suggested_cities, error = quick_ontario_check(location)
            
            if is_valid:
                cities = [c.name for c in suggested_cities[:3]]
                print(f"✅ VALID: Suggestions - {cities}")
            else:
                print(f"❌ INVALID: {error}")
                if suggested_cities:
                    cities = [c.name for c in suggested_cities[:3]]
                    print(f"   Suggestions: {cities}")
                    
        except Exception as e:
            print(f"🔥 ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Location validation algorithm testing complete!")
    print("\n💡 Next steps:")
    print("1. Run: python manage.py runserver")
    print("2. Go to: http://localhost:8000/rides/map/")
    print("3. Test real-time validation by typing addresses")

if __name__ == "__main__":
    test_location_validation()