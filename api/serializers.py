from rest_framework import serializers

class RouteRequestSerializer(serializers.Serializer):
    start = serializers.CharField(max_length=200, help_text="Start location in USA")
    finish = serializers.CharField(max_length=200, help_text="Finish location in USA")

class FuelStopSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    price = serializers.FloatField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()

class RouteResponseSerializer(serializers.Serializer):
    route_geometry = serializers.JSONField()
    distance_miles = serializers.FloatField()
    fuel_stops = FuelStopSerializer(many=True)
    total_fuel_cost = serializers.FloatField()
    total_gallons = serializers.FloatField()
