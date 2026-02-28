import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import RouteRequestSerializer, RouteResponseSerializer
from .fuel_optimizer import FuelOptimizer
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Initialize fuel optimizer once
cache_path = Path(settings.BASE_DIR) / 'fuel-prices-for-be-assessment_geocoded.json'
fuel_optimizer = None
try:
    fuel_optimizer = FuelOptimizer(str(cache_path))
    logger.info(f"Loaded {len(fuel_optimizer.stations)} fuel stations")
except FileNotFoundError as e:
    logger.warning(f"Fuel optimizer not ready: {e}")
    logger.warning("Run 'python manage.py geocode_stations' to initialize")
except Exception as e:
    logger.error(f"Failed to initialize fuel optimizer: {e}")

class OptimalRouteView(APIView):
    @extend_schema(
        request=RouteRequestSerializer,
        responses={200: RouteResponseSerializer},
        description="Calculate optimal fuel stops along a route between two US locations",
        examples=[
            OpenApiExample(
                'Short Route',
                value={'start': 'Los Angeles, CA', 'finish': 'San Francisco, CA'},
                request_only=True,
            ),
            OpenApiExample(
                'Cross-Country Route',
                value={'start': 'New York, NY', 'finish': 'Los Angeles, CA'},
                request_only=True,
            ),
        ]
    )
    def post(self, request):
        if not fuel_optimizer:
            return Response(
                {'error': 'Fuel optimizer not initialized. Run: python manage.py geocode_stations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        start = validated_data.get('start')
        finish = validated_data.get('finish')
        
        if not start or not finish:
            return Response({'error': 'start and finish are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get route from OpenRouteService
        try:
            route_data = self._get_route(start, finish)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Route error: {e}")
            return Response({'error': 'Failed to get route'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Extract route coordinates and distance
        coordinates = route_data['features'][0]['geometry']['coordinates']
        distance_meters = route_data['features'][0]['properties']['segments'][0]['distance']
        distance_miles = distance_meters * 0.000621371
        
        # Find optimal fuel stops
        fuel_stops, total_cost = fuel_optimizer.find_optimal_stops(
            coordinates, distance_miles, max_range=500
        )
        
        response_data = {
            'route_geometry': route_data['features'][0]['geometry'],
            'distance_miles': round(distance_miles, 2),
            'fuel_stops': fuel_stops,
            'total_fuel_cost': total_cost,
            'total_gallons': round(distance_miles / 10, 2)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_route(self, start: str, finish: str):
        """Get route from OpenRouteService API"""
        api_key = getattr(settings, 'OPENROUTE_API_KEY', None)
        if not api_key:
            raise ValueError("OPENROUTE_API_KEY not configured in .env file")
        
        # Geocode start and finish
        start_coords = self._geocode(start)
        finish_coords = self._geocode(finish)
        
        # Get route
        url = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        body = {
            'coordinates': [start_coords, finish_coords]
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def _geocode(self, location: str):
        """Geocode location to coordinates"""
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="fuel_route_planner", timeout=10)
        try:
            geo = geolocator.geocode(f"{location}, USA")
            if not geo:
                raise ValueError(f"Could not geocode location: {location}")
            return [geo.longitude, geo.latitude]
        except Exception as e:
            raise ValueError(f"Geocoding failed for {location}: {e}")



class RouteFormView(APIView):
    """Simple form view for route planning"""
    def get(self, request):
        return render(request, 'route_form.html')
