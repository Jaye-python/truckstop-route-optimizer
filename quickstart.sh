#!/bin/bash
# Quick Start Script

echo "🚀 Fuel-Optimized Route Planner - Quick Start"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OpenRouteService API key"
    echo "   Get one free at: https://openrouteservice.org/dev/#/signup"
    echo ""
    read -p "Press Enter after adding your API key to .env..."
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# Check if geocoded cache exists
if [ ! -f fuel-prices-for-be-assessment_geocoded.json ]; then
    echo "🌍 Geocoding fuel stations (first time only, ~10-15 minutes)..."
    python manage.py geocode_stations
else
    echo "✅ Geocoded stations cache found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  python manage.py runserver"
echo ""
echo "Then test the API:"
echo "  python test_api.py"
echo ""
echo "Or open demo.html in your browser for interactive map"
