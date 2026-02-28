from rest_framework import renderers
from django.template.loader import render_to_string

class HTMLMapRenderer(renderers.BaseRenderer):
    media_type = 'text/html'
    format = 'map'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data or 'route_geometry' not in data:
            return '<html><body><h1>No route data available</h1></body></html>'
        
        if not renderer_context:
            renderer_context = {}
        
        request = renderer_context.get('request')
        request_data = request.data if request else {}
        
        coordinates = data['route_geometry']['coordinates']
        context = {
            'start': request_data.get('start', 'Start'),
            'finish': request_data.get('finish', 'Finish'),
            'route_coords': [[c[1], c[0]] for c in coordinates],
            'distance_miles': data['distance_miles'],
            'fuel_stops': data['fuel_stops'],
            'total_fuel_cost': data['total_fuel_cost'],
            'total_gallons': data['total_gallons']
        }
        return render_to_string('route_map.html', context)
