"""
Location Services Module for Motorcycle Dealership
Handles GPS coordinates, location-based queries, and nearest dealership finder
"""

import math
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dealership_logic import Dealership
import os

@dataclass
class UserLocation:
    """Represents user's current location"""
    latitude: float
    longitude: float
    city: str = ""
    state: str = ""
    address: str = ""

class LocationService:
    """
    Service for handling location-based operations
    """

    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0

    def __init__(self):
        self.user_location = None

    def set_user_location(self, latitude: float, longitude: float, city: str = "", state: str = ""):
        """Set user's current location"""
        self.user_location = UserLocation(
            latitude=latitude,
            longitude=longitude,
            city=city,
            state=state
        )

    def get_user_location(self) -> Optional[UserLocation]:
        """Get user's current location"""
        return self.user_location

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        # Convert to radians
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return self.EARTH_RADIUS_KM * c

    def find_nearest_dealership(self, dealerships: List, user_lat: float, user_lon: float) -> Optional[Dict]:
        """Find nearest dealership to user's location"""
        if not dealerships:
            return None

        nearest = None
        min_distance = float('inf')

        for dealer in dealerships:
            # Handle both dictionary and object formats
            if isinstance(dealer, dict):
                dealer_lat = dealer.get('latitude')
                dealer_lon = dealer.get('longitude')
            else:
                dealer_lat = dealer.latitude
                dealer_lon = dealer.longitude

            if dealer_lat is not None and dealer_lon is not None:
                distance = self.calculate_distance(user_lat, user_lon, dealer_lat, dealer_lon)
                if distance < min_distance:
                    min_distance = distance
                    nearest = dealer

        if nearest:
            return {
                "dealership": nearest,
                "distance_km": round(min_distance, 2),
                "distance_miles": round(min_distance * 0.621371, 2)
            }

        return None

    def get_location_info(self, latitude: float, longitude: float) -> Dict:
        """Get location information using Google Maps Geocoding API"""
        try:
            # Get Google Maps API key from environment
            google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

            if google_maps_api_key:
                # Use Google Maps Geocoding API
                geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={google_maps_api_key}"

                response = requests.get(geocoding_url, timeout=5)
                data = response.json()

                if data.get('status') == 'OK' and data.get('results'):
                    result = data['results'][0]
                    address_components = result.get('address_components', [])

                    # Extract city and state
                    city = "Unknown"
                    state = "Unknown"

                    for component in address_components:
                        if 'locality' in component.get('types', []):
                            city = component.get('long_name', 'Unknown')
                        elif 'administrative_area_level_1' in component.get('types', []):
                            state = component.get('long_name', 'Unknown')

                    return {
                        "city": city,
                        "state": state,
                        "region": "India",
                        "timezone": "Asia/Kolkata",
                        "full_address": result.get('formatted_address', 'Unknown')
                    }

            # Fallback to mock data if API fails or no key
            return self.get_mock_location_info(latitude, longitude)

        except Exception as e:
            print(f"Error getting location info: {e}")
            return self.get_mock_location_info(latitude, longitude)

    def get_mock_location_info(self, latitude: float, longitude: float) -> Dict:
        """Get mock location information for testing"""
        # Mumbai coordinates check
        if 19.0 <= latitude <= 19.2 and 72.8 <= longitude <= 73.0:
            return {
                "city": "Mumbai",
                "state": "Maharashtra",
                "region": "Western India",
                "timezone": "Asia/Kolkata",
                "full_address": "Mumbai, Maharashtra, India"
            }
        # Delhi coordinates check
        elif 28.5 <= latitude <= 28.7 and 77.1 <= longitude <= 77.3:
            return {
                "city": "Delhi",
                "state": "Delhi",
                "region": "Northern India",
                "timezone": "Asia/Kolkata",
                "full_address": "New Delhi, Delhi, India"
            }
        else:
            return {
                "city": "Unknown",
                "state": "Unknown",
                "region": "India",
                "timezone": "Asia/Kolkata",
                "full_address": "Unknown Location"
            }

    def get_nearby_dealerships_google_maps(self, latitude: float, longitude: float, radius: int = 50000) -> List[Dict]:
        """Get nearby dealerships using Google Places API"""
        try:
            google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

            if google_maps_api_key:
                # Search for motorcycle dealerships nearby
                places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    'location': f'{latitude},{longitude}',
                    'radius': radius,  # 50km radius
                    'type': 'car_dealer',  # Closest category for motorcycle dealers
                    'keyword': 'motorcycle OR bike OR two wheeler',
                    'key': google_maps_api_key
                }

                response = requests.get(places_url, params=params, timeout=10)
                data = response.json()

                if data.get('status') == 'OK':
                    nearby_places = []
                    for place in data.get('results', []):
                        # Filter for motorcycle-related places
                        name = place.get('name', '').lower()
                        if any(keyword in name for keyword in ['motorcycle', 'bike', 'honda', 'yamaha', 'suzuki', 'bajaj', 'hero', 'tvs', 'royal enfield']):
                            nearby_places.append({
                                'name': place.get('name', 'Unknown'),
                                'address': place.get('vicinity', 'Unknown'),
                                'latitude': place['geometry']['location']['lat'],
                                'longitude': place['geometry']['location']['lng'],
                                'rating': place.get('rating', 0),
                                'distance': self.calculate_distance(latitude, longitude,
                                                                  place['geometry']['location']['lat'],
                                                                  place['geometry']['location']['lng'])
                            })

                    return nearby_places[:5]  # Return top 5 results

            return []  # Return empty list if API fails

        except Exception as e:
            print(f"Error getting nearby dealerships: {e}")
            return []

    def format_distance(self, distance_km: float) -> str:
        """Format distance for user-friendly display"""
        if distance_km < 1:
            return f"{int(distance_km * 1000)} meters"
        elif distance_km < 10:
            return f"{distance_km:.1f} km"
        else:
            return f"{int(distance_km)} km"

    def get_directions_url(self, from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> str:
        """Generate Google Maps directions URL"""
        return f"https://www.google.com/maps/dir/{from_lat},{from_lon}/{to_lat},{to_lon}"

    def process_location_query(self, query: str, dealerships: List[Dealership]) -> Dict:
        """Process location-based queries"""
        query = query.lower().strip()

        # Check if user location is available
        if not self.user_location:
            return {
                "type": "location_needed",
                "response": "I need your location to find the nearest dealership. Please enable location services or provide your city name."
            }

        # Find nearest dealership
        nearest_info = self.find_nearest_dealership(
            dealerships,
            self.user_location.latitude,
            self.user_location.longitude
        )

        if not nearest_info:
            return {
                "type": "no_dealers",
                "response": "Sorry, I couldn't find any dealerships in your area."
            }

        dealer = nearest_info["dealership"]
        distance = nearest_info["distance_km"]

        # Handle different types of location queries
        if any(word in query for word in ['nearest', 'closest', 'near me']):
            # Handle both dictionary and object formats
            if isinstance(dealer, dict):
                dealer_name = dealer.get('name', 'Unknown')
                dealer_city = dealer.get('city', 'Unknown')
                dealer_state = dealer.get('state', 'Unknown')
                dealer_address = dealer.get('address', 'Unknown')
                dealer_phone = dealer.get('phone', 'Unknown')
                dealer_hours = dealer.get('working_hours', {}).get('monday-friday', '9:00 AM - 8:00 PM')
                dealer_lat = dealer.get('latitude')
                dealer_lon = dealer.get('longitude')
            else:
                dealer_name = dealer.name
                dealer_city = dealer.city
                dealer_state = dealer.state
                dealer_address = dealer.address
                dealer_phone = dealer.phone
                dealer_hours = dealer.working_hours.get('monday-friday', '9:00 AM - 8:00 PM')
                dealer_lat = dealer.latitude
                dealer_lon = dealer.longitude

            response = f"The nearest dealership is {dealer_name} in {dealer_city}, {dealer_state}.\n"
            response += f"It's approximately {self.format_distance(distance)} away from your location.\n"
            response += f"Address: {dealer_address}\n"
            response += f"Phone: {dealer_phone}\n"
            response += f"Working Hours: {dealer_hours}"

            return {
                "type": "nearest_dealer",
                "response": response,
                "dealership": dealer,
                "distance": distance,
                "directions_url": self.get_directions_url(
                    self.user_location.latitude, self.user_location.longitude,
                    dealer_lat, dealer_lon
                )
            }

        elif any(word in query for word in ['directions', 'how to reach', 'navigate']):
            # Handle both dictionary and object formats
            if isinstance(dealer, dict):
                dealer_name = dealer.get('name', 'Unknown')
                dealer_address = dealer.get('address', 'Unknown')
                dealer_city = dealer.get('city', 'Unknown')
                dealer_lat = dealer.get('latitude')
                dealer_lon = dealer.get('longitude')
            else:
                dealer_name = dealer.name
                dealer_address = dealer.address
                dealer_city = dealer.city
                dealer_lat = dealer.latitude
                dealer_lon = dealer.longitude

            response = f"Here are directions to {dealer_name}:\n"
            response += f"From your location to: {dealer_address}, {dealer_city}\n"
            response += f"Distance: {self.format_distance(distance)}"

            return {
                "type": "directions",
                "response": response,
                "directions_url": self.get_directions_url(
                    self.user_location.latitude, self.user_location.longitude,
                    dealer_lat, dealer_lon
                )
            }

        elif any(word in query for word in ['hours', 'timing', 'open']):
            # Handle both dictionary and object formats
            if isinstance(dealer, dict):
                dealer_name = dealer.get('name', 'Unknown')
                dealer_hours = dealer.get('working_hours', {})
            else:
                dealer_name = dealer.name
                dealer_hours = dealer.working_hours

            response = f"{dealer_name} working hours:\n"
            for day_range, hours in dealer_hours.items():
                response += f"• {day_range.title()}: {hours}\n"

            return {
                "type": "hours",
                "response": response
            }

        else:
            # General location info
            location_info = self.get_location_info(self.user_location.latitude, self.user_location.longitude)

            # Handle both dictionary and object formats
            if isinstance(dealer, dict):
                dealer_name = dealer.get('name', 'Unknown')
            else:
                dealer_name = dealer.name

            response = f"You're currently in {location_info['city']}, {location_info['state']}.\n"
            response += f"The nearest dealership is {dealer_name}, about {self.format_distance(distance)} away."

            return {
                "type": "location_info",
                "response": response,
                "location": location_info
            }

    def get_mock_location(self, city: str) -> Optional[UserLocation]:
        """Get mock location for testing purposes"""
        mock_locations = {
            "mumbai": UserLocation(19.0760, 72.8777, "Mumbai", "Maharashtra"),
            "delhi": UserLocation(28.6139, 77.2090, "Delhi", "Delhi"),
            "bangalore": UserLocation(12.9716, 77.5946, "Bangalore", "Karnataka"),
            "chennai": UserLocation(13.0827, 80.2707, "Chennai", "Tamil Nadu"),
            "kolkata": UserLocation(22.5726, 88.3639, "Kolkata", "West Bengal"),
            "pune": UserLocation(18.5204, 73.8567, "Pune", "Maharashtra"),
            "hyderabad": UserLocation(17.3850, 78.4867, "Hyderabad", "Telangana"),
            "ahmedabad": UserLocation(23.0225, 72.5714, "Ahmedabad", "Gujarat")
        }

        return mock_locations.get(city.lower())

# Global location service instance
location_service = LocationService()

def set_user_location(latitude: float, longitude: float, city: str = "", state: str = ""):
    """Set user's location"""
    location_service.set_user_location(latitude, longitude, city, state)

def get_nearest_dealership(dealerships: List[Dealership]) -> Optional[Dict]:
    """Get nearest dealership to user's location"""
    if not location_service.get_user_location():
        return None

    user_loc = location_service.get_user_location()
    return location_service.find_nearest_dealership(dealerships, user_loc.latitude, user_loc.longitude)

def process_location_query(query: str, dealerships: List[Dealership]) -> Dict:
    """Process location-based queries"""
    return location_service.process_location_query(query, dealerships)

def get_location_info(latitude: float, longitude: float) -> Dict:
    """Get location information"""
    return location_service.get_location_info(latitude, longitude)
