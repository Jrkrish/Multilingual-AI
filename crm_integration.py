"""
CRM Integration Module for Motorcycle Dealership
Handles customer relationship management, booking tracking, and customer communication
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class CustomerStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    BOOKED_TEST_RIDE = "booked_test_ride"
    BOOKED_SERVICE = "booked_service"
    PURCHASED = "purchased"
    INACTIVE = "inactive"

class CommunicationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    WHATSAPP = "whatsapp"

@dataclass
class Customer:
    id: str
    name: str
    phone: str
    email: str = ""
    city: str = ""
    preferred_bikes: List[str] = None
    status: CustomerStatus = CustomerStatus.NEW
    created_date: str = ""
    last_contact: str = ""
    notes: str = ""

    def __post_init__(self):
        if self.preferred_bikes is None:
            self.preferred_bikes = []
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.last_contact:
            self.last_contact = self.created_date

@dataclass
class Booking:
    id: str
    customer_id: str
    type: str  # "test_ride", "service", "purchase"
    bike_model: str = ""
    service_type: str = ""
    date: str = ""
    status: str = "confirmed"  # confirmed, completed, cancelled
    notes: str = ""
    created_date: str = ""

@dataclass
class Communication:
    id: str
    customer_id: str
    type: CommunicationType
    subject: str = ""
    message: str = ""
    sent_date: str = ""
    status: str = "sent"  # sent, delivered, failed

class CRMManager:
    """
    Manages customer relationships, bookings, and communications
    """

    def __init__(self, db_path: str = "dealership_crm.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                city TEXT,
                preferred_bikes TEXT,
                status TEXT,
                created_date TEXT,
                last_contact TEXT,
                notes TEXT
            )
        ''')

        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                type TEXT,
                bike_model TEXT,
                service_type TEXT,
                date TEXT,
                status TEXT,
                notes TEXT,
                created_date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        # Communications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communications (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                type TEXT,
                subject TEXT,
                message TEXT,
                sent_date TEXT,
                status TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_customer(self, customer: Customer) -> bool:
        """Add a new customer to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO customers (id, name, phone, email, city, preferred_bikes,
                                    status, created_date, last_contact, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer.id, customer.name, customer.phone, customer.email, customer.city,
                  json.dumps(customer.preferred_bikes), customer.status.value,
                  customer.created_date, customer.last_contact, customer.notes))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding customer: {e}")
            return False

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return Customer(
                    id=row[0],
                    name=row[1],
                    phone=row[2],
                    email=row[3],
                    city=row[4],
                    preferred_bikes=json.loads(row[5]) if row[5] else [],
                    status=CustomerStatus(row[6]),
                    created_date=row[7],
                    last_contact=row[8],
                    notes=row[9]
                )
            return None
        except Exception as e:
            print(f"Error getting customer: {e}")
            return None

    def update_customer_status(self, customer_id: str, status: CustomerStatus) -> bool:
        """Update customer status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE customers SET status = ?, last_contact = ?
                WHERE id = ?
            ''', (status.value, datetime.now().isoformat(), customer_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating customer status: {e}")
            return False

    def add_booking(self, booking: Booking) -> bool:
        """Add a new booking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO bookings (id, customer_id, type, bike_model, service_type,
                                   date, status, notes, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (booking.id, booking.customer_id, booking.type, booking.bike_model,
                  booking.service_type, booking.date, booking.status, booking.notes,
                  booking.created_date))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding booking: {e}")
            return False

    def get_customer_bookings(self, customer_id: str) -> List[Booking]:
        """Get all bookings for a customer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM bookings WHERE customer_id = ?", (customer_id,))
            rows = cursor.fetchall()
            conn.close()

            bookings = []
            for row in rows:
                bookings.append(Booking(
                    id=row[0],
                    customer_id=row[1],
                    type=row[2],
                    bike_model=row[3],
                    service_type=row[4],
                    date=row[5],
                    status=row[6],
                    notes=row[7],
                    created_date=row[8]
                ))
            return bookings
        except Exception as e:
            print(f"Error getting customer bookings: {e}")
            return []

    def add_communication(self, communication: Communication) -> bool:
        """Add a communication record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO communications (id, customer_id, type, subject, message,
                                          sent_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (communication.id, communication.customer_id, communication.type.value,
                  communication.subject, communication.message, communication.sent_date,
                  communication.status))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding communication: {e}")
            return False

    def send_email(self, to_email: str, subject: str, message: str, customer_id: str = None) -> bool:
        """Send email to customer"""
        try:
            # Email configuration (you would configure this with your SMTP settings)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            sender_email = os.getenv('SENDER_EMAIL', 'noreply@everylingua.com')
            sender_password = os.getenv('SENDER_PASSWORD', '')

            if not sender_password:
                print("Email not configured - would send email to:", to_email)
                return True

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)
            server.quit()

            # Log communication
            if customer_id:
                comm = Communication(
                    id=f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    customer_id=customer_id,
                    type=CommunicationType.EMAIL,
                    subject=subject,
                    message=message,
                    sent_date=datetime.now().isoformat()
                )
                self.add_communication(comm)

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_sms(self, phone: str, message: str, customer_id: str = None) -> bool:
        """Send SMS to customer"""
        try:
            # SMS configuration (you would integrate with an SMS service)
            sms_api_key = os.getenv('SMS_API_KEY', '')

            if not sms_api_key:
                print(f"SMS not configured - would send SMS to {phone}: {message}")
                return True

            # Here you would integrate with your SMS provider
            # For now, just log the communication
            if customer_id:
                comm = Communication(
                    id=f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    customer_id=customer_id,
                    type=CommunicationType.SMS,
                    message=message,
                    sent_date=datetime.now().isoformat()
                )
                self.add_communication(comm)

            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def create_test_ride_booking(self, customer_name: str, phone: str, bike_model: str,
                                preferred_date: str, email: str = "", city: str = "") -> Dict:
        """Create a test ride booking with CRM integration"""
        try:
            # Create or get customer
            customer_id = f"cust_{phone}_{datetime.now().strftime('%Y%m%d')}"

            customer = Customer(
                id=customer_id,
                name=customer_name,
                phone=phone,
                email=email,
                city=city,
                preferred_bikes=[bike_model],
                status=CustomerStatus.BOOKED_TEST_RIDE
            )

            if not self.add_customer(customer):
                return {"success": False, "message": "Failed to create customer record"}

            # Create booking
            booking_id = f"TR{datetime.now().strftime('%Y%m%d%H%M')}"
            booking = Booking(
                id=booking_id,
                customer_id=customer_id,
                type="test_ride",
                bike_model=bike_model,
                date=preferred_date,
                created_date=datetime.now().isoformat()
            )

            if not self.add_booking(booking):
                return {"success": False, "message": "Failed to create booking"}

            # Send confirmation
            confirmation_message = f"""
Dear {customer_name},

Your test ride for {bike_model} has been booked successfully!

Booking Details:
- Date: {preferred_date}
- Booking ID: {booking_id}
- Dealership: EveryLingua Motors

Please bring a valid driving license and arrive 15 minutes before the scheduled time.

For any changes, please contact us at +91-9876543210

Best regards,
EveryLingua Motors Team
"""

            self.send_email(email or f"{phone}@sms.everylingua.com", f"Test Ride Confirmation - {booking_id}", confirmation_message, customer_id)
            self.send_sms(phone, f"Test ride booked for {bike_model} on {preferred_date}. Booking ID: {booking_id}", customer_id)

            return {
                "success": True,
                "booking_id": booking_id,
                "message": f"Test ride booked successfully! Booking ID: {booking_id}"
            }

        except Exception as e:
            print(f"Error creating test ride booking: {e}")
            return {"success": False, "message": "Failed to create booking"}

    def create_service_booking(self, customer_name: str, phone: str, bike_model: str,
                             service_type: str, preferred_date: str, email: str = "") -> Dict:
        """Create a service booking with CRM integration"""
        try:
            # Create or get customer
            customer_id = f"cust_{phone}_{datetime.now().strftime('%Y%m%d')}"

            customer = Customer(
                id=customer_id,
                name=customer_name,
                phone=phone,
                email=email,
                preferred_bikes=[bike_model],
                status=CustomerStatus.BOOKED_SERVICE
            )

            if not self.add_customer(customer):
                return {"success": False, "message": "Failed to create customer record"}

            # Create booking
            booking_id = f"SV{datetime.now().strftime('%Y%m%d%H%M')}"
            booking = Booking(
                id=booking_id,
                customer_id=customer_id,
                type="service",
                bike_model=bike_model,
                service_type=service_type,
                date=preferred_date,
                created_date=datetime.now().isoformat()
            )

            if not self.add_booking(booking):
                return {"success": False, "message": "Failed to create booking"}

            # Send confirmation
            confirmation_message = f"""
Dear {customer_name},

Your service appointment has been booked successfully!

Booking Details:
- Bike: {bike_model}
- Service: {service_type}
- Date: {preferred_date}
- Booking ID: {booking_id}

Please arrive at the scheduled time with your bike and service book.

For any changes, please contact us at +91-9876543210

Best regards,
EveryLingua Motors Team
"""

            self.send_email(email or f"{phone}@sms.everylingua.com", f"Service Booking Confirmation - {booking_id}", confirmation_message, customer_id)
            self.send_sms(phone, f"Service booked for {bike_model} on {preferred_date}. Booking ID: {booking_id}", customer_id)

            return {
                "success": True,
                "booking_id": booking_id,
                "message": f"Service booked successfully! Booking ID: {booking_id}"
            }

        except Exception as e:
            print(f"Error creating service booking: {e}")
            return {"success": False, "message": "Failed to create booking"}

    def get_customer_dashboard_data(self, customer_id: str) -> Dict:
        """Get customer dashboard data"""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return {"success": False, "message": "Customer not found"}

            bookings = self.get_customer_bookings(customer_id)

            return {
                "success": True,
                "customer": {
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "status": customer.status.value,
                    "preferred_bikes": customer.preferred_bikes
                },
                "bookings": [
                    {
                        "id": booking.id,
                        "type": booking.type,
                        "bike_model": booking.bike_model,
                        "service_type": booking.service_type,
                        "date": booking.date,
                        "status": booking.status
                    }
                    for booking in bookings
                ]
            }
        except Exception as e:
            print(f"Error getting customer dashboard data: {e}")
            return {"success": False, "message": "Failed to get dashboard data"}

# Global CRM manager instance
crm_manager = CRMManager()

def create_test_ride_booking(customer_name: str, phone: str, bike_model: str,
                           preferred_date: str, email: str = "", city: str = "") -> Dict:
    """Create test ride booking with CRM integration"""
    return crm_manager.create_test_ride_booking(customer_name, phone, bike_model, preferred_date, email, city)

def create_service_booking(customer_name: str, phone: str, bike_model: str,
                         service_type: str, preferred_date: str, email: str = "") -> Dict:
    """Create service booking with CRM integration"""
    return crm_manager.create_service_booking(customer_name, phone, bike_model, service_type, preferred_date, email)

def get_customer_dashboard(customer_id: str) -> Dict:
    """Get customer dashboard data"""
    return crm_manager.get_customer_dashboard_data(customer_id)
