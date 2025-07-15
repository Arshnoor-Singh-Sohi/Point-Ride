# rides/management/commands/populate_cities.py

from django.core.management.base import BaseCommand
from rides.models import City

class Command(BaseCommand):
    help = 'Populate initial cities data for Ontario, Canada'

    def handle(self, *args, **options):
        # Ontario cities with approximate coordinates
        ontario_cities = [
            {'name': 'Toronto', 'latitude': 43.6532, 'longitude': -79.3832},
            {'name': 'Ottawa', 'latitude': 45.4215, 'longitude': -75.6972},
            {'name': 'Mississauga', 'latitude': 43.5890, 'longitude': -79.6441},
            {'name': 'Hamilton', 'latitude': 43.2557, 'longitude': -79.8711},
            {'name': 'Brampton', 'latitude': 43.7315, 'longitude': -79.7624},
            {'name': 'London', 'latitude': 42.9849, 'longitude': -81.2453},
            {'name': 'Markham', 'latitude': 43.8561, 'longitude': -79.3370},
            {'name': 'Vaughan', 'latitude': 43.8563, 'longitude': -79.5085},
            {'name': 'Kitchener', 'latitude': 43.4643, 'longitude': -80.5204},
            {'name': 'Windsor', 'latitude': 42.3149, 'longitude': -83.0364},
            {'name': 'Richmond Hill', 'latitude': 43.8828, 'longitude': -79.4403},
            {'name': 'Oakville', 'latitude': 43.4675, 'longitude': -79.6877},
            {'name': 'Burlington', 'latitude': 43.3255, 'longitude': -79.7990},
            {'name': 'Oshawa', 'latitude': 43.8971, 'longitude': -78.8658},
            {'name': 'Barrie', 'latitude': 44.3894, 'longitude': -79.6903},
            {'name': 'Guelph', 'latitude': 43.5448, 'longitude': -80.2482},
            {'name': 'Kingston', 'latitude': 44.2312, 'longitude': -76.4860},
            {'name': 'Cambridge', 'latitude': 43.3616, 'longitude': -80.3144},
            {'name': 'Waterloo', 'latitude': 43.4643, 'longitude': -80.5204},
            {'name': 'Sudbury', 'latitude': 46.4917, 'longitude': -80.9930},
            {'name': 'Thunder Bay', 'latitude': 48.3809, 'longitude': -89.2477},
            {'name': 'St. Catharines', 'latitude': 43.1594, 'longitude': -79.2469},
            {'name': 'Sault Ste. Marie', 'latitude': 46.5197, 'longitude': -84.3456},
            {'name': 'Sarnia', 'latitude': 42.9994, 'longitude': -82.4066},
            {'name': 'Peterborough', 'latitude': 44.3106, 'longitude': -78.3197},
            {'name': 'Niagara Falls', 'latitude': 43.0962, 'longitude': -79.0377},
            {'name': 'North Bay', 'latitude': 46.3091, 'longitude': -79.4608},
            {'name': 'Welland', 'latitude': 42.9918, 'longitude': -79.2648},
            {'name': 'Brantford', 'latitude': 43.1394, 'longitude': -80.2644},
            {'name': 'Timmins', 'latitude': 48.4758, 'longitude': -81.3304},
            {'name': 'Chatham', 'latitude': 42.4048, 'longitude': -82.1910},
            {'name': 'Belleville', 'latitude': 44.1628, 'longitude': -77.3832},
            {'name': 'Cornwall', 'latitude': 45.0212, 'longitude': -74.7307},
            {'name': 'Orillia', 'latitude': 44.6084, 'longitude': -79.4197},
            {'name': 'Stratford', 'latitude': 43.3701, 'longitude': -80.9821},
        ]

        created_count = 0
        updated_count = 0

        for city_data in ontario_cities:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                defaults={
                    'province': 'Ontario',
                    'country': 'Canada',
                    'latitude': city_data['latitude'],
                    'longitude': city_data['longitude'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created city: {city.name}')
                )
            else:
                # Update coordinates if they don't exist
                if not city.latitude or not city.longitude:
                    city.latitude = city_data['latitude']
                    city.longitude = city_data['longitude']
                    city.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated coordinates for: {city.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully populated cities database:\n'
                f'- Created: {created_count} cities\n'
                f'- Updated: {updated_count} cities\n'
                f'- Total Ontario cities: {City.objects.filter(province="Ontario").count()}'
            )
        )