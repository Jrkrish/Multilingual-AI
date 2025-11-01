"""
OTP Service for user registration verification
Handles email and SMS OTP generation and verification
"""

import smtplib
import random
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class OTPService:
    def __init__(self):
        self.otp_storage = {}  # In production, use Redis or database
        self.otp_expiry_minutes = 5
        
        # Email configuration
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', 587))

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))

    def store_otp(self, identifier, otp, method='email'):
        """Store OTP with expiration time"""
        expiry_time = datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
        self.otp_storage[identifier] = {
            'otp': otp,
            'expiry': expiry_time,
            'method': method,
            'attempts': 0
        }

    def send_email_otp(self, email, otp):
        """Send OTP via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = email
            msg['Subject'] = "EveryLingua AI - Registration OTP"

            body = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #3b82f6;">Welcome to EveryLingua AI!</h2>
                    <p>Thank you for registering with us. Please use the following OTP to verify your email address:</p>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #1f2937; font-size: 32px; letter-spacing: 4px; margin: 0;">{otp}</h1>
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>This OTP is valid for {self.otp_expiry_minutes} minutes only</li>
                        <li>Do not share this OTP with anyone</li>
                        <li>If you didn't request this OTP, please ignore this email</li>
                    </ul>
                    
                    <p>Best regards,<br>EveryLingua AI Team</p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 12px; color: #6b7280;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            server.send_message(msg)
            server.quit()

            return True, "OTP sent successfully to your email"

        except Exception as e:
            print(f"Email sending error: {e}")
            return False, f"Failed to send email: {str(e)}"

    def send_sms_otp(self, phone, otp):
        """Send OTP via SMS (Mock implementation)"""
        # In production, integrate with SMS service like Twilio, AWS SNS, etc.
        try:
            # Mock SMS sending
            print(f"SMS OTP: {otp} sent to {phone}")
            
            # Store in a file for demonstration (remove in production)
            with open('sms_log.txt', 'a') as f:
                f.write(f"{datetime.now()}: SMS OTP {otp} sent to {phone}\n")
            
            return True, "OTP sent successfully to your phone"
            
        except Exception as e:
            print(f"SMS sending error: {e}")
            return False, f"Failed to send SMS: {str(e)}"

    def verify_otp(self, identifier, provided_otp):
        """Verify the provided OTP"""
        if identifier not in self.otp_storage:
            return False, "OTP not found or expired"

        stored_data = self.otp_storage[identifier]
        
        # Check if OTP is expired
        if datetime.now() > stored_data['expiry']:
            del self.otp_storage[identifier]
            return False, "OTP has expired. Please request a new one"

        # Check attempt limit
        if stored_data['attempts'] >= 3:
            del self.otp_storage[identifier]
            return False, "Too many failed attempts. Please request a new OTP"

        # Verify OTP
        if stored_data['otp'] == provided_otp:
            del self.otp_storage[identifier]
            return True, "OTP verified successfully"
        else:
            stored_data['attempts'] += 1
            return False, f"Invalid OTP. {3 - stored_data['attempts']} attempts remaining"

    def resend_otp(self, identifier, method='email'):
        """Resend OTP to the same identifier"""
        if identifier not in self.otp_storage:
            return False, "No pending OTP found. Please start registration again"

        # Generate new OTP
        new_otp = self.generate_otp()
        
        # Update stored OTP
        self.store_otp(identifier, new_otp, method)

        # Send based on method
        if method == 'email':
            return self.send_email_otp(identifier, new_otp)
        elif method == 'sms':
            return self.send_sms_otp(identifier, new_otp)
        else:
            return False, "Invalid method"

# Global OTP service instance
otp_service = OTPService()

def send_registration_otp(identifier, method='email'):
    """Send OTP for user registration"""
    otp = otp_service.generate_otp()
    otp_service.store_otp(identifier, otp, method)

    if method == 'email':
        return otp_service.send_email_otp(identifier, otp)
    elif method == 'sms':
        return otp_service.send_sms_otp(identifier, otp)
    else:
        return False, "Invalid verification method"

def verify_registration_otp(identifier, otp):
    """Verify OTP for user registration"""
    return otp_service.verify_otp(identifier, otp)

def resend_registration_otp(identifier, method='email'):
    """Resend OTP for user registration"""
    return otp_service.resend_otp(identifier, method)
