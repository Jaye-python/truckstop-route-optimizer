from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import csv
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

class Command(BaseCommand):
    help = 'Pre-geocode fuel stations for faster API startup'

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / 'fuel-prices-for-be-assessment.csv'
        cache_path = str(csv_path).replace('.csv', '_geocoded.json')
        
        self.stdout.write('Geocoding fuel stations...')
        
        geolocator = Nominatim(user_agent="fuel_optimizer")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        
        stations = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            seen = {}
            
            for row in reader:
                key = (row['City'], row['State'])
                price = float(row['Retail Price'])
                
                if key not in seen or price < seen[key]['price']:
                    seen[key] = {
                        'name': row['Truckstop Name'],
                        'address': row['Address'],
                        'city': row['City'],
                        'state': row['State'],
                        'price': price
                    }
            
            self.stdout.write(f'Found {len(seen)} unique cities to geocode...')
            
            for key, station in seen.items():
                location = f"{station['city']}, {station['state']}, USA"
                try:
                    geo = geocode(location)
                    if geo:
                        station['lat'] = geo.latitude
                        station['lon'] = geo.longitude
                        stations.append(station)
                        self.stdout.write(f'Geocoded: {location}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed: {location} - {e}'))
        
        with open(cache_path, 'w') as f:
            json.dump(stations, f)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully geocoded {len(stations)} stations to {cache_path}'))
