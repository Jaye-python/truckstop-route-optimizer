#!/usr/bin/env python3
"""Test script for the route API"""
import requests
import json

def test_route_api():
    url = 'http://localhost:8000/api/route/'
    
    test_cases = [
        {
            'name': 'Short route (no fuel stops needed)',
            'data': {'start': 'Los Angeles, CA', 'finish': 'San Francisco, CA'}
        },
        {
            'name': 'Long route (multiple fuel stops)',
            'data': {'start': 'New York, NY', 'finish': 'Los Angeles, CA'}
        },
        {
            'name': 'Medium route',
            'data': {'start': 'Chicago, IL', 'finish': 'Miami, FL'}
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test['name']}")
        print(f"{'='*60}")
        print(f"Request: {test['data']}")
        
        try:
            response = requests.post(url, json=test['data'])
            response.raise_for_status()
            
            result = response.json()
            print(f"\nDistance: {result['distance_miles']} miles")
            print(f"Total Gallons: {result['total_gallons']}")
            print(f"Total Fuel Cost: ${result['total_fuel_cost']}")
            print(f"Number of Fuel Stops: {len(result['fuel_stops'])}")
            
            if result['fuel_stops']:
                print("\nFuel Stops:")
                for i, stop in enumerate(result['fuel_stops'], 1):
                    print(f"  {i}. {stop['name']} - {stop['city']}, {stop['state']}")
                    print(f"     Price: ${stop['price']}/gal")
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")

if __name__ == '__main__':
    print("Testing Route API")
    print("Make sure the server is running: python manage.py runserver")
    input("Press Enter to continue...")
    test_route_api()
