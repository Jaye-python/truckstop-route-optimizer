import csv
import math
import json
from pathlib import Path
from typing import List, Dict, Tuple
import os

class FuelOptimizer:
    def __init__(self, cache_path: str):
        """Initialize with geocoded cache file"""
        if not os.path.exists(cache_path):
            raise FileNotFoundError(
                f"Geocoded cache not found at {cache_path}. "
                "Run 'python manage.py geocode_stations' first."
            )
        with open(cache_path, 'r') as f:
            self.stations = json.load(f)
    
    def _distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in miles using Haversine formula"""
        R = 3959  # Earth radius in miles
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def find_optimal_stops(self, route_coords: List[Tuple[float, float]], 
                          total_distance: float, max_range: float = 500) -> Tuple[List[Dict], float]:
        """Find optimal fuel stops along route"""
        if total_distance <= max_range:
            # No stops needed but still calculate cost
            avg_price = sum(s['price'] for s in self.stations) / len(self.stations) if self.stations else 3.5
            gallons_needed = total_distance / 10
            return [], round(gallons_needed * avg_price, 2)
        
        stops = []
        distance_covered = 0
        
        # Calculate cumulative distances along route
        cumulative_distances = [0.0]
        for i in range(1, len(route_coords)):
            dist = self._distance(route_coords[i-1][1], route_coords[i-1][0],
                                route_coords[i][1], route_coords[i][0])
            cumulative_distances.append(cumulative_distances[-1] + dist)
        
        while distance_covered + max_range < total_distance:
            target_distance = distance_covered + max_range
            
            # Find route point near target distance
            target_idx = min(range(len(cumulative_distances)), 
                           key=lambda i: abs(cumulative_distances[i] - target_distance))
            target_lat, target_lon = route_coords[target_idx][1], route_coords[target_idx][0]
            
            # Find cheapest station within 50 miles of target point
            candidates = []
            for station in self.stations:
                dist = self._distance(target_lat, target_lon, station['lat'], station['lon'])
                if dist <= 50:
                    candidates.append((station, dist))
            
            if candidates:
                best_station = min(candidates, key=lambda x: x[0]['price'])[0]
                stops.append(best_station)
                distance_covered = target_distance
            else:
                distance_covered += max_range
        
        # Calculate total fuel cost
        gallons_needed = total_distance / 10  # 10 mpg
        if stops:
            avg_price = sum(s['price'] for s in stops) / len(stops)
        else:
            avg_price = sum(s['price'] for s in self.stations) / len(self.stations) if self.stations else 3.5
        
        total_cost = gallons_needed * avg_price
        
        return stops, round(total_cost, 2)
