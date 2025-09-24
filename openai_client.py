from pathlib import Path
import google.generativeai as genai
from google.cloud import texttospeech
import os

class GeminiClient:
    """
    A client for interacting with Google's Gemini API for conversational AI and text-to-speech functionalities.
    """
    def __init__(self, api_key=None):
        # Use provided API key or get from environment
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Try to get API key from environment
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                raise ValueError("Gemini API key not provided and not found in environment variables")

        # Use Gemini 2.5 Pro model as requested
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Initialize TTS client with credentials
        try:
            self.tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Warning: Could not initialize TTS client: {e}")
            self.tts_client = None

    def chat_with_gemini(self, prompt, context=None):
        """Generate response using Gemini AI with optional context"""
        try:
            if context:
                full_prompt = f"{context}\n\nUser Query: {prompt}"
            else:
                full_prompt = prompt

            response = self.model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error in Gemini chat: {e}")
            return f"I apologize, but I'm having trouble processing your request right now. Please try again later."

    def text_to_speech(self, text, language_code="en-US"):
        """Convert text to speech with specified language"""
        if not self.tts_client:
            print("TTS client not available")
            return None

        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            filename = Path(__file__).parent / "output_speech.mp3"
            with open(str(filename), "wb") as f:
                f.write(response.audio_content)
            return str(filename)
        except Exception as e:
            print(f"Error in TTS: {e}")
            return None

    def generate_dealership_response(self, query, bike_data=None, service_data=None, dealer_data=None):
        """Generate intelligent dealership response using Gemini AI"""
        context = f"""
You are an AI assistant for EveryLingua Motors, a motorcycle dealership.
You have access to the following information:

BIKE INVENTORY:
{bike_data if bike_data else 'No bike data available'}

SERVICE PACKAGES:
{service_data if service_data else 'No service data available'}

DEALERSHIP LOCATIONS:
{dealer_data if dealer_data else 'No dealer data available'}

Please provide helpful, accurate responses about:
- Available motorcycle models and prices
- EMI and financing options
- Test ride bookings
- Service appointments
- Dealership locations
- General motorcycle information

Be conversational, friendly, and professional. If you don't have specific information, provide general guidance and offer to connect the customer with a human representative.
"""

        return self.chat_with_gemini(query, context)
