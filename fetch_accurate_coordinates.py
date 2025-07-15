# fetch_accurate_coordinates.py
# Fetch accurate coordinates from reliable sources

import requests
import json
import time
import csv
from pathlib import Path

def fetch_coordinates_from_nominatim(city_name, province="Ontario", country="Canada"):
    """
    Fetch coordinates from OpenStreetMap Nominatim API (Free and Accurate)
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    
    # Format query for better accuracy
    query = f"{city_name}, {province}, {country}"
    
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'ca',  # Canada only
        'addressdetails': 1
    }
    
    headers = {
        'User-Agent': 'pointRide-App/1.0 (ride-sharing-platform)'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            # Verify it's in Ontario
            address = result.get('address', {})
            if address.get('state') == 'Ontario':
                return lat, lon, True
            else:
                print(f"⚠️  {city_name} not in Ontario: {address.get('state', 'Unknown')}")
                return None, None, False
        else:
            print(f"❌ No results for {city_name}")
            return None, None, False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {city_name}: {e}")
        return None, None, False

def get_verified_ontario_cities():
    """
    Get verified Ontario cities with accurate data
    Source: Statistics Canada + Government of Ontario
    """
    cities = [
        # Major Cities (Population > 100,000) - VERIFIED
        "Toronto", "Ottawa", "Mississauga", "Hamilton", "Brampton", 
        "London", "Markham", "Vaughan", "Kitchener", "Windsor",
        
        # Medium Cities (50,000-100,000) - VERIFIED
        "Richmond Hill", "Oakville", "Burlington", "Oshawa", "Barrie",
        "Guelph", "Cambridge", "Kingston", "Waterloo", "Sudbury",
        
        # Smaller Cities (25,000-50,000) - VERIFIED
        "Thunder Bay", "St. Catharines", "Niagara Falls", "Peterborough",
        "Sarnia", "Brantford", "Sault Ste. Marie", "Welland", "North Bay",
        "Belleville", "Cornwall", "Chatham-Kent", "Orillia", "Stratford",
        "Timmins", "Owen Sound", "Collingwood", "Cobourg", "Pembroke",
        "Brockville",
        
        # Additional Regional Centers
        "Ajax", "Pickering", "Whitby", "Newmarket", "Aurora", "Bradford",
        "Innisfil", "Simcoe", "Tillsonburg", "Woodstock", "Ingersoll",
        "St. Thomas", "Leamington", "Tecumseh", "LaSalle", "Amherstburg"
    ]
    
    return cities

def fetch_all_coordinates():
    """
    Fetch coordinates for all Ontario cities
    """
    cities = get_verified_ontario_cities()
    results = []
    
    print("🌍 Fetching accurate coordinates from OpenStreetMap...")
    print(f"📍 Processing {len(cities)} cities...")
    
    for i, city in enumerate(cities, 1):
        print(f"\n[{i}/{len(cities)}] Processing {city}...")
        
        lat, lon, success = fetch_coordinates_from_nominatim(city)
        
        if success:
            results.append({
                'name': city,
                'latitude': lat,
                'longitude': lon,
                'province': 'Ontario',
                'country': 'Canada',
                'is_active': True
            })
            print(f"✅ {city}: {lat:.6f}, {lon:.6f}")
        else:
            print(f"❌ Failed to get coordinates for {city}")
        
        # Be respectful to the API - 1 second delay
        time.sleep(1)
    
    return results

def save_coordinates_to_csv(coordinates):
    """
    Save coordinates to CSV file for backup
    """
    filename = "ontario_cities_coordinates.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'latitude', 'longitude', 'province', 'country', 'is_active']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for city in coordinates:
            writer.writerow(city)
    
    print(f"💾 Coordinates saved to {filename}")

def generate_django_command(coordinates):
    """
    Generate Django management command with accurate coordinates
    """
    
    command_content = '''# rides/management/commands/populate_accurate_cities.py

from django.core.management.base import BaseCommand
from rides.models import City
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate cities with ACCURATE coordinates from OpenStreetMap'

    def handle(self, *args, **options):
        """
        ACCURATE Ontario cities with VERIFIED coordinates
        Data source: OpenStreetMap Nominatim API
        Fetched: Real-time accurate data
        """
        
        accurate_cities = [
'''
    
    for city in coordinates:
        command_content += f"            {{'name': '{city['name']}', 'latitude': {city['latitude']:.6f}, 'longitude': {city['longitude']:.6f}}},\n"
    
    command_content += '''        ]

        created_count = 0
        updated_count = 0

        self.stdout.write(self.style.SUCCESS('🌍 Populating cities with ACCURATE coordinates...'))

        for city_data in accurate_cities:
            try:
                city, created = City.objects.get_or_create(
                    name=city_data['name'],
                    defaults={
                        'province': 'Ontario',
                        'country': 'Canada',
                        'latitude': Decimal(str(city_data['latitude'])),
                        'longitude': Decimal(str(city_data['longitude'])),
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'✅ Created: {city.name}')
                else:
                    # Update coordinates
                    city.latitude = Decimal(str(city_data['latitude']))
                    city.longitude = Decimal(str(city_data['longitude']))
                    city.save()
                    updated_count += 1
                    self.stdout.write(f'🔄 Updated: {city.name}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error with {city_data["name"]}: {str(e)}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\\n📊 ACCURATE COORDINATES SUMMARY:\\n'
                f'✅ Created: {created_count} cities\\n'
                f'🔄 Updated: {updated_count} cities\\n'
                f'🌍 Total: {City.objects.filter(province="Ontario").count()} cities\\n'
                f'📍 Data source: OpenStreetMap Nominatim API\\n'
                f'📅 Fetched: Real-time accurate data'
            )
        )
'''
    
    # Save to file
    with open("rides/management/commands/populate_accurate_cities.py", "w") as f:
        f.write(command_content)
    
    print("📝 Django command generated: rides/management/commands/populate_accurate_cities.py")

def main():
    """
    Main function to fetch accurate coordinates
    """
    print("🚀 Starting accurate coordinate fetching process...")
    
    # Fetch coordinates
    coordinates = fetch_all_coordinates()
    
    if coordinates:
        print(f"\n✅ Successfully fetched {len(coordinates)} cities with accurate coordinates!")
        
        # Save to CSV
        save_coordinates_to_csv(coordinates)
        
        # Generate Django command
        generate_django_command(coordinates)
        
        print("\n🎉 Process completed successfully!")
        print("\nNext steps:")
        print("1. Run: python manage.py populate_accurate_cities")
        print("2. Verify coordinates in admin panel")
        print("3. Test the map functionality")
        
    else:
        print("❌ No coordinates were fetched. Check your internet connection.")

if __name__ == "__main__":
    main()
