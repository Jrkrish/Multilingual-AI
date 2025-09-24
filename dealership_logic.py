"""
Motorcycle Dealership Business Logic Module
Handles dealership-specific operations and integrates with the voice assistant
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class BikeCategory(Enum):
    COMMUTER = "commuter"
    SPORTS = "sports"
    CRUISER = "cruiser"
    ADVENTURE = "adventure"
    SCOOTER = "scooter"

@dataclass
class BikeModel:
    id: str
    name: str
    brand: str
    category: BikeCategory
    price: float
    engine_cc: int
    mileage: float
    features: List[str]
    colors: List[str]
    in_stock: bool
    description: str

@dataclass
class ServicePackage:
    id: str
    name: str
    description: str
    price: float
    duration_hours: int
    services_included: List[str]

@dataclass
class Dealership:
    id: str
    name: str
    address: str
    city: str
    state: str
    phone: str
    latitude: float
    longitude: float
    working_hours: Dict[str, str]

class DealershipManager:
    """
    Manages motorcycle dealership operations including inventory, services, and customer interactions
    """

    def __init__(self):
        self.initialize_bike_inventory()
        self.initialize_service_packages()
        self.initialize_dealerships()
        self.active_bookings = {}
        self.customer_database = {}

    def initialize_bike_inventory(self):
        """Initialize the motorcycle inventory with sample data"""
        self.bike_inventory = [
            BikeModel(
                id="1",
                name="Classic 350",
                brand="Royal Enfield",
                category=BikeCategory.CRUISER,
                price=185000,
                engine_cc=349,
                mileage=35,
                features=["Fuel Injection", "ABS", "Digital Console", "USB Charging"],
                colors=["Black", "Red", "Blue", "Grey"],
                in_stock=True,
                description="The iconic Royal Enfield Classic 350 offers timeless design with modern performance."
            ),
            BikeModel(
                id="2",
                name="Pulsar 220F",
                brand="Bajaj",
                category=BikeCategory.SPORTS,
                price=135000,
                engine_cc=220,
                mileage=38,
                features=["Fuel Injection", "ABS", "LED Headlights", "Digital Meter"],
                colors=["Black", "Red", "Blue"],
                in_stock=True,
                description="The Bajaj Pulsar 220F is a powerful sports bike perfect for enthusiasts."
            ),
            BikeModel(
                id="3",
                name="Activa 6G",
                brand="Honda",
                category=BikeCategory.SCOOTER,
                price=75000,
                engine_cc=109,
                mileage=55,
                features=["LED Headlights", "External Fuel Fill", "Mobile Charging"],
                colors=["Black", "Red", "Blue", "White"],
                in_stock=True,
                description="Honda Activa 6G - India's most loved scooter with modern features."
            ),
            BikeModel(
                id="4",
                name="Dominar 400",
                brand="Bajaj",
                category=BikeCategory.SPORTS,
                price=210000,
                engine_cc=373,
                mileage=27,
                features=["DOHC Engine", "Dual Channel ABS", "Slipper Clutch", "LED Lights"],
                colors=["Black", "Red", "Blue"],
                in_stock=True,
                description="The Bajaj Dominar 400 offers power and style for the modern rider."
            ),
            BikeModel(
                id="5",
                name="Himalayan",
                brand="Royal Enfield",
                category=BikeCategory.ADVENTURE,
                price=220000,
                engine_cc=411,
                mileage=30,
                features=["Long Travel Suspension", "High Ground Clearance", "Tripper Navigation"],
                colors=["Black", "Blue", "White", "Grey"],
                in_stock=False,
                description="Royal Enfield Himalayan - Built for adventure and long-distance touring."
            )
        ]

    def initialize_service_packages(self):
        """Initialize service packages"""
        self.service_packages = [
            ServicePackage(
                id="basic",
                name="Basic Service",
                description="Oil change, filter cleaning, and basic inspection",
                price=800,
                duration_hours=2,
                services_included=["Engine Oil Change", "Oil Filter", "Basic Inspection", "Chain Lubrication"]
            ),
            ServicePackage(
                id="standard",
                name="Standard Service",
                description="Comprehensive maintenance service",
                price=1500,
                duration_hours=4,
                services_included=["Engine Oil Change", "Oil Filter", "Air Filter", "Spark Plugs", "Brake Inspection", "Chain Service"]
            ),
            ServicePackage(
                id="premium",
                name="Premium Service",
                description="Complete maintenance with genuine parts",
                price=2500,
                duration_hours=6,
                services_included=["All Standard Services", "Brake Pads", "Clutch Plates", "Electrical Check", "Performance Tuning"]
            )
        ]

    def initialize_dealerships(self):
        """Initialize dealership locations"""
        self.dealerships = [
            Dealership(
                id="mumbai_main",
                name="EveryLingua Motors - Mumbai Central",
                address="123 MG Road, Mumbai Central",
                city="Mumbai",
                state="Maharashtra",
                phone="+91-9876543210",
                latitude=19.0760,
                longitude=72.8777,
                working_hours={
                    "monday-friday": "9:00 AM - 8:00 PM",
                    "saturday": "9:00 AM - 9:00 PM",
                    "sunday": "10:00 AM - 6:00 PM"
                }
            ),
            Dealership(
                id="delhi_cp",
                name="EveryLingua Motors - Connaught Place",
                address="45 Connaught Place, New Delhi",
                city="Delhi",
                state="Delhi",
                phone="+91-9876543211",
                latitude=28.6139,
                longitude=77.2090,
                working_hours={
                    "monday-friday": "9:00 AM - 8:00 PM",
                    "saturday": "9:00 AM - 9:00 PM",
                    "sunday": "10:00 AM - 6:00 PM"
                }
            )
        ]

    def get_bikes_by_category(self, category: str) -> List[BikeModel]:
        """Get bikes by category"""
        try:
            bike_category = BikeCategory(category.lower())
            return [bike for bike in self.bike_inventory if bike.category == bike_category]
        except ValueError:
            return []

    def search_bikes(self, query: str) -> List[BikeModel]:
        """Search bikes by name, brand, or features"""
        query = query.lower()
        results = []
        for bike in self.bike_inventory:
            if (query in bike.name.lower() or
                query in bike.brand.lower() or
                any(query in feature.lower() for feature in bike.features)):
                results.append(bike)
        return results

    def get_bike_details(self, bike_id: str) -> Optional[BikeModel]:
        """Get detailed information about a specific bike"""
        for bike in self.bike_inventory:
            if bike.id == bike_id:
                return bike
        return None

    def calculate_emi(self, bike_price: float, down_payment: float, tenure_months: int, interest_rate: float = 12.5) -> Dict:
        """Calculate EMI for bike financing"""
        principal = bike_price - down_payment
        monthly_rate = interest_rate / (12 * 100)

        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)

        total_amount = emi * tenure_months
        total_interest = total_amount - principal

        return {
            "monthly_emi": round(emi, 2),
            "total_amount": round(total_amount, 2),
            "total_interest": round(total_interest, 2),
            "principal": principal,
            "down_payment": down_payment
        }

    def book_test_ride(self, bike_id: str, customer_name: str, phone: str, preferred_date: str) -> Dict:
        """Book a test ride for a customer"""
        bike = self.get_bike_details(bike_id)
        if not bike:
            return {"success": False, "message": "Bike not found"}

        if not bike.in_stock:
            return {"success": False, "message": "Bike currently not available for test ride"}

        booking_id = f"TR{random.randint(1000, 9999)}"
        self.active_bookings[booking_id] = {
            "type": "test_ride",
            "bike_id": bike_id,
            "customer_name": customer_name,
            "phone": phone,
            "date": preferred_date,
            "status": "confirmed"
        }

        return {
            "success": True,
            "booking_id": booking_id,
            "message": f"Test ride booked successfully for {bike.name} on {preferred_date}. Booking ID: {booking_id}"
        }

    def book_service(self, bike_model: str, customer_name: str, phone: str, service_type: str, preferred_date: str) -> Dict:
        """Book a service appointment"""
        service_package = None
        for package in self.service_packages:
            if package.id == service_type or package.name.lower() == service_type.lower():
                service_package = package
                break

        if not service_package:
            return {"success": False, "message": "Invalid service type"}

        booking_id = f"SV{random.randint(1000, 9999)}"
        self.active_bookings[booking_id] = {
            "type": "service",
            "bike_model": bike_model,
            "customer_name": customer_name,
            "phone": phone,
            "service_type": service_type,
            "date": preferred_date,
            "status": "confirmed"
        }

        return {
            "success": True,
            "booking_id": booking_id,
            "message": f"Service booked successfully for {bike_model} on {preferred_date}. Booking ID: {booking_id}. Service: {service_package.name} - ₹{service_package.price}"
        }

    def find_nearest_dealer(self, user_latitude: float, user_longitude: float) -> Optional[Dealership]:
        """Find nearest dealership based on user location"""
        nearest_dealer = None
        min_distance = float('inf')

        for dealer in self.dealerships:
            # Simple distance calculation (Haversine formula would be more accurate)
            distance = ((dealer.latitude - user_latitude) ** 2 + (dealer.longitude - user_longitude) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_dealer = dealer

        return nearest_dealer

    def get_dealership_info(self, city: str = None) -> List[Dealership]:
        """Get dealership information by city or all dealerships"""
        if city:
            return [dealer for dealer in self.dealerships if dealer.city.lower() == city.lower()]
        return self.dealerships

    def get_service_packages(self) -> List[ServicePackage]:
        """Get all available service packages"""
        return self.service_packages

    def process_natural_language_query(self, query: str) -> Dict:
        """
        Process natural language queries and return appropriate responses
        This is the main function that handles dealership-specific queries
        """
        query = query.lower().strip()

        # Bike-related queries
        if any(word in query for word in ['bike', 'motorcycle', 'model', 'available']):
            if 'price' in query or 'cost' in query:
                bikes = self.bike_inventory
                response = "Here are our current bike models and prices:\n"
                for bike in bikes:
                    response += f"• {bike.brand} {bike.name}: ₹{bike.price:,}\n"
                return {"type": "bike_prices", "response": response}

            elif 'sports' in query:
                sports_bikes = self.get_bikes_by_category('sports')
                if sports_bikes:
                    response = "Our sports bike collection:\n"
                    for bike in sports_bikes:
                        response += f"• {bike.brand} {bike.name} - ₹{bike.price:,}\n"
                    return {"type": "bike_category", "response": response}
                else:
                    return {"type": "no_results", "response": "No sports bikes available currently."}

            elif 'scooter' in query:
                scooters = self.get_bikes_by_category('scooter')
                if scooters:
                    response = "Our scooter collection:\n"
                    for bike in scooters:
                        response += f"• {bike.brand} {bike.name} - ₹{bike.price:,}\n"
                    return {"type": "bike_category", "response": response}
                else:
                    return {"type": "no_results", "response": "No scooters available currently."}

            else:
                bikes = self.bike_inventory
                response = "Our current motorcycle inventory:\n"
                for bike in bikes:
                    availability = " (In Stock)" if bike.in_stock else " (Out of Stock)"
                    response += f"• {bike.brand} {bike.name} - ₹{bike.price:,}{availability}\n"
                return {"type": "bike_inventory", "response": response}

        # Finance/EMI queries
        elif any(word in query for word in ['emi', 'finance', 'loan', 'installment']):
            # Extract bike name if mentioned
            bike_name = None
            for bike in self.bike_inventory:
                if bike.name.lower() in query:
                    bike_name = bike
                    break

            if bike_name:
                response = f"EMI calculation for {bike_name.brand} {bike_name.name} (₹{bike_name.price:,}):\n"
                response += "• 20% Down Payment (3 years): ₹{:,}/month\n".format(
                    self.calculate_emi(bike_name.price, bike_name.price * 0.2, 36)["monthly_emi"]
                )
                response += "• 30% Down Payment (2 years): ₹{:,}/month\n".format(
                    self.calculate_emi(bike_name.price, bike_name.price * 0.3, 24)["monthly_emi"]
                )
                return {"type": "finance_calculation", "response": response}
            else:
                response = "Please specify which bike model you're interested in for EMI calculation.\n"
                response += "Available models: " + ", ".join([f"{bike.brand} {bike.name}" for bike in self.bike_inventory])
                return {"type": "finance_help", "response": response}

        # Test ride queries
        elif any(word in query for word in ['test ride', 'testride', 'demo']):
            response = "To book a test ride, I need some details:\n"
            response += "• Which bike model are you interested in?\n"
            response += "• Your name and phone number\n"
            response += "• Preferred date and time\n\n"
            response += "Available bikes for test ride:\n"
            for bike in self.bike_inventory:
                if bike.in_stock:
                    response += f"• {bike.brand} {bike.name}\n"
            return {"type": "test_ride_info", "response": response}

        # Service queries
        elif any(word in query for word in ['service', 'maintenance', 'repair']):
            response = "Our service packages:\n"
            for package in self.service_packages:
                response += f"• {package.name}: ₹{package.price} - {package.description}\n"
            response += "\nTo book a service, please provide:\n"
            response += "• Bike model\n"
            response += "• Your name and phone number\n"
            response += "• Preferred service type and date"
            return {"type": "service_info", "response": response}

        # Dealer location queries
        elif any(word in query for word in ['dealer', 'location', 'address', 'nearest']):
            if 'mumbai' in query:
                dealer = self.dealerships[0]
            elif 'delhi' in query:
                dealer = self.dealerships[1]
            else:
                dealer = self.dealerships[0]  # Default to first dealer

            response = f"Nearest Dealership:\n{dealer.name}\n"
            response += f"Address: {dealer.address}, {dealer.city}, {dealer.state}\n"
            response += f"Phone: {dealer.phone}\n"
            response += f"Working Hours: {dealer.working_hours['monday-friday']}"
            return {"type": "dealer_info", "response": response}

        # General greeting or help
        elif any(word in query for word in ['hello', 'hi', 'help', 'what can you do']):
            response = "Hello! I'm your motorcycle dealership assistant. I can help you with:\n"
            response += "• Bike models and prices\n"
            response += "• EMI and finance calculations\n"
            response += "• Test ride bookings\n"
            response += "• Service appointments\n"
            response += "• Dealer locations\n"
            response += "• General motorcycle information\n\n"
            response += "What would you like to know?"
            return {"type": "greeting", "response": response}

        # Default response
        else:
            response = "I can help you with motorcycle information, test rides, service bookings, and financing options. "
            response += "Please let me know what you're looking for!"
            return {"type": "default", "response": response}

# Global dealership manager instance
dealership_manager = DealershipManager()

def get_dealership_response(query: str) -> str:
    """Main function to get response from dealership system using Gemini AI"""
    try:
        # Import Gemini client
        from openai_client import GeminiClient
        import os

        # Get API key from environment
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return "I'm sorry, but I'm unable to process your request right now. Please try again later."

        # Initialize Gemini client
        gemini_client = GeminiClient(api_key)

        # Get current inventory data
        bikes = get_available_bikes()
        services = get_service_packages()
        dealers = get_dealerships()

        # Format data for AI context
        bike_data = "\n".join([
            f"- {bike['brand']} {bike['name']}: ₹{bike['price']:,} ({'In Stock' if bike['in_stock'] else 'Out of Stock'})"
            for bike in bikes
        ])

        service_data = "\n".join([
            f"- {service['name']}: ₹{service['price']} - {service['description']}"
            for service in services
        ])

        dealer_data = "\n".join([
            f"- {dealer['name']}: {dealer['address']}, {dealer['city']} (Phone: {dealer['phone']})"
            for dealer in dealers
        ])

        # Generate AI response with context
        return gemini_client.generate_dealership_response(query, bike_data, service_data, dealer_data)

    except Exception as e:
        print(f"Error in AI response generation: {e}")
        # Fallback to basic response
        return "I'm currently experiencing technical difficulties. Let me help you with basic information about our motorcycles and services. What would you like to know?"

def get_available_bikes() -> List[Dict]:
    """Get list of available bikes for frontend"""
    return [
        {
            "id": bike.id,
            "name": bike.name,
            "brand": bike.brand,
            "price": bike.price,
            "category": bike.category.value,
            "in_stock": bike.in_stock,
            "image": f"{bike.brand.lower()}_{bike.name.lower().replace(' ', '_')}.jpg"
        }
        for bike in dealership_manager.bike_inventory
    ]

def get_service_packages() -> List[Dict]:
    """Get service packages for frontend"""
    return [
        {
            "id": package.id,
            "name": package.name,
            "price": package.price,
            "description": package.description,
            "duration": package.duration_hours
        }
        for package in dealership_manager.service_packages
    ]

def get_dealerships() -> List[Dict]:
    """Get dealership locations for frontend"""
    return [
        {
            "id": dealer.id,
            "name": dealer.name,
            "address": dealer.address,
            "city": dealer.city,
            "phone": dealer.phone,
            "latitude": dealer.latitude,
            "longitude": dealer.longitude
        }
        for dealer in dealership_manager.dealerships
    ]
