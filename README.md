# EveryLingua AI - Motorcycle Dealership Voice Assistant

A comprehensive AI-powered voice assistant system for motorcycle dealerships with integrated dealer locator, IVR functionality, and CRM integration.

## Features

### 🚗 **Core Functionality**
- **Voice Assistant**: AI-powered voice interaction using OpenAI GPT
- **Dealer Locator**: Interactive map with Google Maps integration
- **CRM Integration**: Customer management and booking system
- **Human Agent Fallback**: Escalation to human agents for complex queries

### 📞 **Phone & IVR Integration**
- **Automatic Phone Calls**: Direct dialing to service center (+918925329304) and personal number (+919566743579)
- **Real-time IVR**: Voice recognition with Gemini API integration
- **Context-Aware Responses**: Intelligent responses tailored to motorcycle dealership queries

### 🎯 **Key Capabilities**
- Test ride bookings
- Service appointments
- Bike inventory management
- Customer dashboard
- EMI calculations
- Location-based services

## 🚀 Deployment to Render

### Prerequisites
1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push this code to a GitHub repository

### Deployment Steps

#### 1. Connect to Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository containing this code

#### 2. Configure Service
1. **Service Type**: Web Service
2. **Runtime**: Python
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

#### 3. Environment Variables
Set the following environment variables in Render:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Gemini API key | ✅ |
| `EMAIL_SENDER` | Gmail address for notifications | ✅ |
| `EMAIL_PASSWORD` | Gmail app password | ✅ |
| `EMAIL_SMTP_SERVER` | SMTP server (smtp.gmail.com) | ✅ |
| `EMAIL_SMTP_PORT` | SMTP port (587) | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google service account key | ✅ |
| `FLASK_ENV` | Set to 'production' | ✅ |

#### 4. Deploy
1. Click **"Create Web Service"**
2. Wait for the build to complete
3. Your app will be live at the provided URL

### 📱 Access Your App

Once deployed, access these endpoints:

- **Main App**: `https://your-app-name.onrender.com/`
- **Dealer Dashboard**: `https://your-app-name.onrender.com/dealer_dashboard.html`
- **Dealer Locator**: `https://your-app-name.onrender.com/dealer_locator.html`

### 🔧 Local Development

#### Prerequisites
- Python 3.8+
- pip

#### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Run the application:
   ```bash
   python app.py
   ```

#### Environment Variables
Create a `.env` file with:
```env
GEMINI_API_KEY=your_gemini_api_key_here
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
GOOGLE_APPLICATION_CREDENTIALS=path_to_service_account.json
```

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/dealer_dashboard.html` | GET | Dealer dashboard |
| `/dealer_locator.html` | GET | Interactive dealer locator |
| `/api/bikes` | GET | Get available bikes |
| `/api/services` | GET | Get service packages |
| `/api/dealerships` | GET | Get dealership locations |
| `/api/chat` | POST | Chat with voice assistant |
| `/api/test-ride-booking` | POST | Book test ride |
| `/api/service-booking` | POST | Book service |
| `/api/gemini-key` | GET | Get Gemini API key |
| `/health` | GET | Health check |

## 🎮 Usage

### Voice Assistant
1. Open the main application
2. Click the microphone button
3. Speak commands like:
   - "I want to book a test ride"
   - "Show me available bikes"
   - "I need service for my motorcycle"

### Dealer Locator
1. Open `/dealer_locator.html`
2. Click "Call Service Center" to dial +918925329304
3. Use "Voice Control" for IVR interaction
4. Click on map markers for dealership details

### Dashboard
1. Open `/dealer_dashboard.html`
2. Click "Call Service Center" to dial +919566743579
3. Navigate through different sections
4. Use voice control for assistance

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Gemini API for voice recognition
- **Maps**: Google Maps API
- **Database**: SQLite (for development)
- **Deployment**: Render

## 📞 Contact Numbers

- **Service Center**: +918925329304
- **Personal**: +919566743579

## 🔒 Security Notes

- API keys are stored as environment variables
- CORS is enabled for cross-origin requests
- Input validation is implemented
- Error handling is in place

## 📝 License

This project is for demonstration purposes. Please ensure compliance with all API terms of service.

---

**EveryLingua AI** - Transforming motorcycle dealerships with AI-powered voice assistance.
