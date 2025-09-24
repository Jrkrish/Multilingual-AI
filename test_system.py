#!/usr/bin/env python3
"""
Test script for EveryLingua AI Motorcycle Dealership Voice Assistant
Tests core functionality including dealership logic, location services, and API endpoints
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

def test_dealership_logic():
    """Test dealership business logic"""
    print("🧪 Testing Dealership Logic...")

    try:
        from dealership_logic import (
            get_dealership_response,
            get_available_bikes,
            get_service_packages,
            get_dealerships,
            DealershipManager
        )

        # Test bike inventory
        bikes = get_available_bikes()
        assert len(bikes) > 0, "No bikes found in inventory"
        print(f"✅ Found {len(bikes)} bikes in inventory")

        # Test service packages
        services = get_service_packages()
        assert len(services) > 0, "No service packages found"
        print(f"✅ Found {len(services)} service packages")

        # Test dealerships
        dealers = get_dealerships()
        assert len(dealers) > 0, "No dealerships found"
        print(f"✅ Found {len(dealers)} dealerships")

        # Test natural language processing
        test_queries = [
            "show me bikes",
            "what are the prices",
            "sports bikes",
            "calculate EMI for classic 350",
            "test ride booking",
            "service packages",
            "nearest dealer"
        ]

        for query in test_queries:
            response = get_dealership_response(query)
            assert response, f"No response for query: {query}"
            print(f"✅ Query '{query}' -> Response generated")

        print("✅ Dealership logic tests passed!\n")

    except Exception as e:
        print(f"❌ Dealership logic test failed: {e}\n")
        return False

    return True

def test_location_services():
    """Test location services"""
    print("🧪 Testing Location Services...")

    try:
        from location_service import (
            LocationService,
            set_user_location,
            get_nearest_dealership,
            process_location_query
        )
        from dealership_logic import get_dealerships

        # Test location service
        location_service = LocationService()

        # Set mock location
        set_user_location(19.0760, 72.8777, "Mumbai", "Maharashtra")

        # Test distance calculation
        distance = location_service.calculate_distance(19.0760, 72.8777, 28.6139, 77.2090)
        assert distance > 0, "Distance calculation failed"
        print(f"✅ Distance calculation: Mumbai to Delhi = {distance:.2f} km")

        # Test nearest dealership
        dealers = get_dealerships()
        nearest = get_nearest_dealership(dealers)
        assert nearest is not None, "Nearest dealership not found"
        dealer = nearest['dealership']
        dealer_name = dealer.get('name') if isinstance(dealer, dict) else dealer.name
        print(f"✅ Nearest dealership found: {dealer_name}")

        # Test location queries
        location_queries = [
            "nearest dealer",
            "find dealer near me",
            "directions to showroom"
        ]

        for query in location_queries:
            response = process_location_query(query, dealers)
            assert "response" in response, f"No response for location query: {query}"
            print(f"✅ Location query '{query}' -> Response generated")

        print("✅ Location services tests passed!\n")

    except Exception as e:
        print(f"❌ Location services test failed: {e}\n")
        return False

    return True

def test_voice_assistant():
    """Test voice assistant initialization"""
    print("🧪 Testing Voice Assistant...")

    try:
        # Set environment variable for testing
        import os
        os.environ['GEMINI_API_KEY'] = 'test_key_for_initialization'

        from voice_assistant import VoiceAssistant

        # Test initialization
        assistant = VoiceAssistant()
        assert assistant is not None, "Voice assistant initialization failed"
        print("✅ Voice assistant initialized successfully")

        # Test dealership response method
        response = assistant.get_dealership_response("show me bikes")
        assert response, "No response from dealership logic"
        print("✅ Dealership response method working")

        print("✅ Voice assistant tests passed!\n")

    except Exception as e:
        print(f"❌ Voice assistant test failed: {e}\n")
        return False

    return True

def test_api_endpoints():
    """Test Flask API endpoints"""
    print("🧪 Testing API Endpoints...")

    try:
        # Import here to avoid issues if Flask not installed
        from app import app
        from dealership_logic import get_available_bikes, get_service_packages, get_dealerships

        # Test with Flask test client
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            assert response.status_code == 200, "Health endpoint failed"
            data = json.loads(response.data)
            assert data['status'] == 'healthy', "Health check failed"
            print("✅ Health endpoint working")

            # Test bikes endpoint
            response = client.get('/api/bikes')
            assert response.status_code == 200, "Bikes endpoint failed"
            data = json.loads(response.data)
            assert data['success'] == True, "Bikes API failed"
            assert len(data['data']) > 0, "No bikes returned"
            print("✅ Bikes API endpoint working")

            # Test services endpoint
            response = client.get('/api/services')
            assert response.status_code == 200, "Services endpoint failed"
            data = json.loads(response.data)
            assert data['success'] == True, "Services API failed"
            print("✅ Services API endpoint working")

            # Test dealerships endpoint
            response = client.get('/api/dealerships')
            assert response.status_code == 200, "Dealerships endpoint failed"
            data = json.loads(response.data)
            assert data['success'] == True, "Dealerships API failed"
            print("✅ Dealerships API endpoint working")

            # Test chat endpoint
            response = client.post('/api/chat', json={'message': 'show me bikes'})
            assert response.status_code == 200, "Chat endpoint failed"
            data = json.loads(response.data)
            assert data['success'] == True, "Chat API failed"
            assert 'response' in data, "No response in chat data"
            print("✅ Chat API endpoint working")

        print("✅ API endpoints tests passed!\n")

    except Exception as e:
        print(f"❌ API endpoints test failed: {e}\n")
        return False

    return True

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("🧪 Testing Dependencies...")

    required_modules = [
        'flask',
        'flask_cors',
        'speech_recognition',
        'google.generativeai',
        'google.cloud.texttospeech',
        'deep_translator',
        'pygame'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)

    if missing_modules:
        print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt\n")
        return False

    print("✅ All dependencies are installed!\n")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting EveryLingua AI System Tests\n")
    print("=" * 50)

    tests = [
        ("Dependencies", test_dependencies),
        ("Dealership Logic", test_dealership_logic),
        ("Location Services", test_location_services),
        ("Voice Assistant", test_voice_assistant),
        ("API Endpoints", test_api_endpoints)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if test_func():
            passed += 1

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        print("\nTo start the system:")
        print("1. Set your GEMINI_API_KEY in .env file")
        print("2. Run: python app.py")
        print("3. Open: http://localhost:5000")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
