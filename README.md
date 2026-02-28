# Fuel-Optimized Route Planner API

Django REST API that calculates optimal fuel stops along a route based on cost and vehicle range.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a free OpenRouteService API key:
   - Visit https://openrouteservice.org/dev/#/signup
   - Sign up for a free account
   - Copy your API key

3. Create `.env` file:
```bash
cp .env.example .env
```
Then edit `.env` and add your API key:
```
OPENROUTE_API_KEY=your_actual_api_key_here
```

4. Pre-geocode fuel stations (first time only):
```bash
python manage.py geocode_stations
```
This creates a cache file for fast API startup.

5. Run migrations:
```bash
python manage.py migrate
```

6. Start server:
```bash
python manage.py runserver
```

## API Usage

### Web Interface (Easiest)
Simply visit: **http://localhost:8000/api/**

Enter your start and finish locations, click "Plan Route & Show Map" to see:
- Interactive map with the route drawn
- Fuel stop markers with prices
- Total distance, fuel cost, and gallons needed

### API Endpoint
`POST /api/route/`

**Get JSON response:**
```bash
curl -X POST http://localhost:8000/api/route/ \
  -H "Content-Type: application/json" \
  -d '{"start": "Los Angeles, CA", "finish": "New York, NY"}'
```

**Get HTML map view:**
```bash
curl -X POST "http://localhost:8000/api/route/?format=map" \
  -H "Content-Type: application/json" \
  -d '{"start": "Los Angeles, CA", "finish": "New York, NY"}'
```

**In Postman:**
1. Set method to POST
2. URL: `http://localhost:8000/api/route/?format=map`
3. Body (raw JSON): `{"start": "Los Angeles, CA", "finish": "New York, NY"}`
4. Click Send - the map will display in the response preview

Or visit in browser: `http://localhost:8000/api/route/?format=map` (POST form data)

### Request Body
```json
{
    "start": "Los Angeles, CA",
    "finish": "New York, NY"
}
```

### JSON Response
```json
{
    "route_geometry": {
        "type": "LineString",
        "coordinates": [[lon, lat], ...]
    },
    "distance_miles": 2789.45,
    "fuel_stops": [
        {
            "name": "PILOT TRAVEL CENTER",
            "address": "I-40, EXIT 280",
            "city": "Oklahoma City",
            "state": "OK",
            "price": 3.30,
            "lat": 35.4676,
            "lon": -97.5164
        }
    ],
    "total_fuel_cost": 975.31,
    "total_gallons": 278.95
}
```

## Features

- Single API call to OpenRouteService for routing
- Optimal fuel stops based on:
  - 500-mile vehicle range
  - Cheapest fuel prices within 50 miles of refuel point
- Returns GeoJSON route geometry for map display
- Calculates total fuel cost at 10 MPG

## Example Request

```bash
curl -X POST http://localhost:8000/api/route/ \
  -H "Content-Type: application/json" \
  -d '{"start": "San Francisco, CA", "finish": "Miami, FL"}'
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Demo Page

Open `demo.html` in your browser to use the interactive map interface:
1. Make sure the server is running
2. Open `demo.html` in a web browser
3. Enter start and finish locations
4. Click "Plan Route" to see the route and fuel stops on the map
