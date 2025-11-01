"""
Flask web server for the EveryLingua AI Motorcycle Dealership Voice Assistant
Serves the HTML interface and provides API endpoints for dealership operations
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from voice_assistant import VoiceAssistant
from dealership_logic import get_available_bikes, get_service_packages, get_dealerships
from crm_integration import create_test_ride_booking, create_service_booking, get_customer_dashboard
from human_agent_fallback import should_escalate_to_human, escalate_query, get_agent_response, get_agent_dashboard, update_agent_status, resolve_query
from location_service import set_user_location, get_nearest_dealership, process_location_query
from otp_service import send_registration_otp, verify_registration_otp, resend_registration_otp
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global voice assistant instance
voice_assistant = None

@app.route('/')
def index():
    """Serve the main HTML interface"""
    try:
        return app.send_static_file('index.html')
    except:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/dealer_dashboard.html')
def dealer_dashboard():
    """Serve the dealer dashboard HTML interface"""
    try:
        return app.send_static_file('dealer_dashboard.html')
    except:
        with open('dealer_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/dealer_locator.html')
def dealer_locator():
    """Serve the interactive dealer locator HTML interface"""
    try:
        return app.send_static_file('dealer_locator.html')
    except:
        with open('dealer_locator.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/register.html')
def register():
    """Serve the user registration HTML interface"""
    try:
        return app.send_static_file('register.html')
    except:
        with open('register.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/api/bikes')
def get_bikes():
    """Get available bikes"""
    try:
        bikes = get_available_bikes()
        return jsonify({"success": True, "data": bikes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/services')
def get_services():
    """Get service packages"""
    try:
        services = get_service_packages()
        return jsonify({"success": True, "data": services})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealerships')
def get_dealers():
    """Get dealership locations"""
    try:
        dealers = get_dealerships()
        return jsonify({"success": True, "data": dealers})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "error": "No message provided"})

        message = data['message']

        # Get response from dealership logic
        from dealership_logic import get_dealership_response
        response = get_dealership_response(message)

        return jsonify({
            "success": True,
            "response": response,
            "type": "dealership" if "motorcycle" in response.lower() or "bike" in response.lower() else "general"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/bikes/search', methods=['POST'])
def search_bikes():
    """Search bikes by query"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"success": False, "error": "No query provided"})

        query = data['query']
        from dealership_logic import DealershipManager
        manager = DealershipManager()
        bikes = manager.search_bikes(query)

        return jsonify({
            "success": True,
            "data": [
                {
                    "id": bike.id,
                    "name": bike.name,
                    "brand": bike.brand,
                    "price": bike.price,
                    "category": bike.category.value,
                    "in_stock": bike.in_stock
                }
                for bike in bikes
            ]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/bikes/emi', methods=['POST'])
def calculate_bike_emi():
    """Calculate EMI for a specific bike"""
    try:
        data = request.get_json()
        if not data or 'bike_id' not in data:
            return jsonify({"success": False, "error": "No bike_id provided"})

        bike_id = data['bike_id']
        down_payment = data.get('down_payment', 0.2)  # Default 20%
        tenure_months = data.get('tenure_months', 36)  # Default 3 years

        from dealership_logic import DealershipManager
        manager = DealershipManager()
        bike = manager.get_bike_details(bike_id)

        if not bike:
            return jsonify({"success": False, "error": "Bike not found"})

        emi_data = manager.calculate_emi(bike.price, bike.price * down_payment, tenure_months)

        return jsonify({
            "success": True,
            "bike": {
                "id": bike.id,
                "name": bike.name,
                "brand": bike.brand,
                "price": bike.price
            },
            "emi_calculation": emi_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealerships/nearby', methods=['POST'])
def get_nearby_dealerships():
    """Get nearby dealerships based on user location"""
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({"success": False, "error": "Location coordinates required"})

        latitude = data['latitude']
        longitude = data['longitude']

        from dealership_logic import get_dealerships
        from location_service import get_nearest_dealership

        dealers = get_dealerships()
        nearest = get_nearest_dealership(dealers)

        return jsonify({
            "success": True,
            "nearest_dealership": nearest,
            "all_dealerships": dealers
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/voice-command', methods=['POST'])
def voice_command():
    """Handle voice commands from the frontend"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({"success": False, "error": "No command provided"})

        command = data['command']

        # Process the voice command
        response = process_voice_command(command)

        return jsonify({"success": True, "response": response})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/test-ride-booking', methods=['POST'])
def book_test_ride():
    """Book a test ride with CRM integration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        result = create_test_ride_booking(
            customer_name=data.get('name'),
            phone=data.get('phone'),
            bike_model=data.get('bike_model'),
            preferred_date=data.get('date'),
            email=data.get('email', ''),
            city=data.get('city', '')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/service-booking', methods=['POST'])
def book_service():
    """Book a service with CRM integration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        result = create_service_booking(
            customer_name=data.get('name'),
            phone=data.get('phone'),
            bike_model=data.get('bike_model'),
            service_type=data.get('service_type'),
            preferred_date=data.get('date'),
            email=data.get('email', '')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/customer-dashboard/<customer_id>')
def customer_dashboard(customer_id):
    """Get customer dashboard data"""
    try:
        result = get_customer_dashboard(customer_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/location/set', methods=['POST'])
def set_location():
    """Set user location"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        set_user_location(
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            city=data.get('city', ''),
            state=data.get('state', '')
        )

        return jsonify({"success": True, "message": "Location updated"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/location/nearest-dealer')
def nearest_dealer():
    """Get nearest dealership"""
    try:
        from dealership_logic import get_dealerships
        dealers = get_dealerships()
        nearest = get_nearest_dealership(dealers)

        if nearest:
            return jsonify({"success": True, "data": nearest})
        else:
            return jsonify({"success": False, "error": "No dealerships found"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/escalate', methods=['POST'])
def escalate_to_human():
    """Escalate query to human agent"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        result = escalate_query(
            customer_id=data.get('customer_id', 'unknown'),
            query=data.get('query'),
            reason=data.get('reason', 'complex_query'),
            priority=data.get('priority', 1),
            language=data.get('language', 'en')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/response/<query_id>')
def get_human_response(query_id):
    """Get response from human agent"""
    try:
        response = get_agent_response(query_id)
        if response:
            return jsonify({"success": True, "data": response})
        else:
            return jsonify({"success": False, "error": "No response found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/dashboard')
def agent_dashboard():
    """Get human agent dashboard data"""
    try:
        data = get_agent_dashboard()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/status/<agent_id>', methods=['POST'])
def update_agent_status_endpoint(agent_id):
    """Update agent status"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({"success": False, "error": "No status provided"})

        from human_agent_fallback import AgentStatus
        status = AgentStatus(data['status'])

        success = update_agent_status(agent_id, status)
        return jsonify({"success": success})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/resolve/<query_id>', methods=['POST'])
def resolve_human_query(query_id):
    """Resolve query with human agent response"""
    try:
        data = request.get_json()
        if not data or 'response' not in data:
            return jsonify({"success": False, "error": "No response provided"})

        success = resolve_query(query_id, data['response'])
        return jsonify({"success": success})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/gemini-key')
def get_gemini_key():
    """Get Gemini API key for frontend"""
    try:
        # Get API key from environment variables
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            return jsonify({"success": False, "error": "Gemini API key not configured"})

        return jsonify({"success": True, "api_key": gemini_api_key})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/register/send-otp', methods=['POST'])
def send_otp():
    """Send OTP for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        identifier = data.get('identifier')  # email or phone
        method = data.get('method', 'email')  # 'email' or 'sms'

        if not identifier:
            return jsonify({"success": False, "error": "Email or phone number required"})

        # Validate method
        if method not in ['email', 'sms']:
            return jsonify({"success": False, "error": "Invalid verification method"})

        # Send OTP
        success, message = send_registration_otp(identifier, method)

        return jsonify({
            "success": success,
            "message": message,
            "method": method,
            "identifier": identifier
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/register/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        identifier = data.get('identifier')
        otp = data.get('otp')

        if not identifier or not otp:
            return jsonify({"success": False, "error": "Identifier and OTP required"})

        # Verify OTP
        success, message = verify_registration_otp(identifier, otp)

        return jsonify({
            "success": success,
            "message": message,
            "verified": success
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/register/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        identifier = data.get('identifier')
        method = data.get('method', 'email')

        if not identifier:
            return jsonify({"success": False, "error": "Email or phone number required"})

        # Resend OTP
        success, message = resend_registration_otp(identifier, method)

        return jsonify({
            "success": success,
            "message": message,
            "method": method
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def process_voice_command(command: str) -> str:
    """Process a voice command and return appropriate response"""
    from dealership_logic import get_dealership_response

    # Get response from dealership system
    response = get_dealership_response(command)

    return response

def start_voice_assistant():
    """Start the voice assistant in a separate thread"""
    global voice_assistant
    try:
        voice_assistant = VoiceAssistant()
        print("Starting voice assistant...")
        voice_assistant.run()
    except Exception as e:
        print(f"Error starting voice assistant: {e}")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    # Start voice assistant in background thread
    voice_thread = threading.Thread(target=start_voice_assistant, daemon=True)
    voice_thread.start()

    # Get port from environment variable (for Render deployment)
    port = int(os.environ.get('PORT', 5000))

    # Start Flask server
    print("Starting EveryLingua AI Motorcycle Dealership Server...")
    print(f"Web interface available at: http://localhost:{port}")
    print(f"Dealer dashboard available at: http://localhost:{port}/dealer_dashboard.html")
    print("API endpoints:")
    print("  - GET  /api/bikes - Get available bikes")
    print("  - GET  /api/services - Get service packages")
    print("  - GET  /api/dealerships - Get dealership locations")
    print("  - POST /api/chat - Send chat message")
    print("  - POST /api/voice-command - Process voice command")
    print("  - POST /api/test-ride-booking - Book test ride")
    print("  - POST /api/service-booking - Book service")
    print("  - GET  /api/customer-dashboard/<id> - Get customer dashboard")
    print("  - POST /api/location/set - Set user location")
    print("  - GET  /api/location/nearest-dealer - Get nearest dealer")
    print("  - POST /api/human-agent/escalate - Escalate to human agent")
    print("  - GET  /api/human-agent/response/<id> - Get agent response")
    print("  - GET  /api/human-agent/dashboard - Get agent dashboard")
    print("  - POST /api/human-agent/status/<id> - Update agent status")
    print("  - POST /api/human-agent/resolve/<id> - Resolve query")
    print("  - GET  /api/gemini-key - Get Gemini API key")
    print("  - GET  /health - Health check")

    # Use gunicorn for production, but allow debug mode for development
    if os.environ.get('FLASK_ENV') == 'production':
        # Production mode - let gunicorn handle it
        pass
    else:
        # Development mode
        app.run(host='0.0.0.0', port=port, debug=True)
