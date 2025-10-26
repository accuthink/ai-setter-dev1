# Google Calendar Integration Roadmap

## Overview
This document outlines the steps to integrate Google Calendar API for real appointment booking, moving from mock implementations to production-ready calendar management.

---

## Phase 1: Google Calendar API Setup & Authentication

### Step 1.1: Create Google Cloud Project
```bash
# Tasks:
1. Go to Google Cloud Console (console.cloud.google.com)
2. Create new project: "Accuthink AI Appointment Setter"
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download credentials JSON file
```

**Required Credentials:**
- OAuth 2.0 Client ID (for user authorization)
- Service Account (for server-to-server, recommended for business calendars)

### Step 1.2: Choose Authentication Method

**Option A: Service Account (Recommended for Business)**
```
✅ Best for: Business calendars owned by organization
✅ No user interaction needed
✅ Can access shared/delegated calendars
✅ Works with Google Workspace domain delegation

Steps:
1. Create Service Account in Google Cloud
2. Download service account JSON key
3. Share Google Calendar with service account email
4. Grant "Make changes to events" permission
```

**Option B: OAuth 2.0 (For User Calendars)**
```
✅ Best for: Individual user calendars
⚠️ Requires initial authorization flow
⚠️ Needs token refresh handling

Steps:
1. Create OAuth 2.0 Client ID
2. Implement authorization flow
3. Store refresh tokens securely
4. Handle token expiration
```

### Step 1.3: Install Dependencies
```bash
# Add to requirements.txt
google-auth==2.23.3
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.103.0

# Install
pip install google-auth google-auth-oauthlib google-api-python-client
```

### Step 1.4: Environment Configuration
```bash
# Add to .env.local
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
GOOGLE_CALENDAR_TIMEZONE=America/Chicago
```

---

## Phase 2: Calendar Service Implementation

### Step 2.1: Create Calendar Service Module
```
📁 app/services/calendar_service.py
```

**Key Components:**
```python
class GoogleCalendarService:
    def __init__(self):
        """Initialize Google Calendar API client"""
        
    def authenticate(self) -> Resource:
        """Authenticate using service account or OAuth"""
        
    def find_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        buffer_minutes: int = 15
    ) -> List[Dict]:
        """Find available time slots in calendar"""
        
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str],
        description: str = ""
    ) -> Dict:
        """Create calendar event (book appointment)"""
        
    def update_event(
        self,
        event_id: str,
        **kwargs
    ) -> Dict:
        """Update existing event (reschedule)"""
        
    def delete_event(
        self,
        event_id: str
    ) -> bool:
        """Delete event (cancel appointment)"""
        
    def get_event_by_phone(
        self,
        phone_number: str
    ) -> List[Dict]:
        """Find appointments by customer phone number"""
```

### Step 2.2: Implement Authentication
```python
# app/services/calendar_service.py

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self):
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate using service account"""
        creds = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE'),
            scopes=SCOPES
        )
        return build('calendar', 'v3', credentials=creds)
```

### Step 2.3: Implement Find Available Slots
```python
def find_available_slots(
    self,
    start_date: datetime,
    end_date: datetime,
    duration_minutes: int = 60,
    buffer_minutes: int = 15,
    business_hours: dict = None
) -> List[Dict]:
    """
    Find available time slots by checking existing events.
    
    Algorithm:
    1. Get all events in date range
    2. Define business hours (e.g., 9 AM - 5 PM)
    3. Generate potential slots
    4. Filter out slots that conflict with existing events
    5. Add buffer time between appointments
    6. Return list of available slots
    """
    
    if business_hours is None:
        business_hours = {
            'start': '09:00',
            'end': '17:00',
            'days': [0, 1, 2, 3, 4]  # Monday-Friday
        }
    
    # Get existing events
    events_result = self.service.events().list(
        calendarId=self.calendar_id,
        timeMin=start_date.isoformat(),
        timeMax=end_date.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    existing_events = events_result.get('items', [])
    
    # Generate available slots (implement slot generation logic)
    available_slots = self._generate_slots(
        start_date,
        end_date,
        existing_events,
        duration_minutes,
        buffer_minutes,
        business_hours
    )
    
    return available_slots
```

### Step 2.4: Implement Create Event (Book Appointment)
```python
def create_event(
    self,
    customer_name: str,
    customer_phone: str,
    service_name: str,
    start_time: datetime,
    duration_minutes: int = 60,
    notes: str = "",
    send_notifications: bool = True
) -> Dict:
    """Create calendar event for appointment"""
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': f'{service_name} - {customer_name}',
        'description': f'''
Appointment Details:
- Customer: {customer_name}
- Phone: {customer_phone}
- Service: {service_name}
- Notes: {notes}

Booked via AI Assistant
        '''.strip(),
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': os.getenv('GOOGLE_CALENDAR_TIMEZONE', 'UTC'),
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': os.getenv('GOOGLE_CALENDAR_TIMEZONE', 'UTC'),
        },
        'attendees': [
            {'email': f'{customer_phone}@sms.reminder.com'}  # Optional SMS integration
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                {'method': 'popup', 'minutes': 60},        # 1 hour before
            ],
        },
        'extendedProperties': {
            'private': {
                'customer_phone': customer_phone,
                'booked_via': 'ai_assistant',
                'booking_timestamp': datetime.now().isoformat()
            }
        }
    }
    
    # Create event
    created_event = self.service.events().insert(
        calendarId=self.calendar_id,
        body=event,
        sendNotifications=send_notifications
    ).execute()
    
    return {
        'success': True,
        'event_id': created_event['id'],
        'event_link': created_event.get('htmlLink'),
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat()
    }
```

### Step 2.5: Implement Cancel & Reschedule
```python
def cancel_appointment(
    self,
    event_id: str,
    send_notifications: bool = True
) -> Dict:
    """Cancel appointment by deleting event"""
    
    try:
        self.service.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id,
            sendNotifications=send_notifications
        ).execute()
        
        return {'success': True, 'message': 'Appointment cancelled'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def reschedule_appointment(
    self,
    event_id: str,
    new_start_time: datetime,
    duration_minutes: int = 60
) -> Dict:
    """Reschedule appointment to new time"""
    
    # Get existing event
    event = self.service.events().get(
        calendarId=self.calendar_id,
        eventId=event_id
    ).execute()
    
    # Update times
    end_time = new_start_time + timedelta(minutes=duration_minutes)
    event['start']['dateTime'] = new_start_time.isoformat()
    event['end']['dateTime'] = end_time.isoformat()
    
    # Update event
    updated_event = self.service.events().update(
        calendarId=self.calendar_id,
        eventId=event_id,
        body=event,
        sendNotifications=True
    ).execute()
    
    return {
        'success': True,
        'event_id': updated_event['id'],
        'new_start_time': new_start_time.isoformat()
    }

def find_appointments_by_phone(
    self,
    phone_number: str,
    days_ahead: int = 30
) -> List[Dict]:
    """Find customer's appointments by phone number"""
    
    now = datetime.now()
    future = now + timedelta(days=days_ahead)
    
    events = self.service.events().list(
        calendarId=self.calendar_id,
        timeMin=now.isoformat(),
        timeMax=future.isoformat(),
        privateExtendedProperty=f'customer_phone={phone_number}',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events.get('items', [])
```

---

## Phase 3: Update AI Tool Implementations

### Step 3.1: Replace Mock Tools in `ai_voice.py`
```python
# app/routers/ai_voice.py

from app.services.calendar_service import GoogleCalendarService

# Initialize calendar service
calendar_service = GoogleCalendarService()

def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool call with REAL Google Calendar integration"""
    
    if tool_name == "find_available_slots":
        service = arguments.get("service_name")
        start_date = datetime.fromisoformat(arguments.get("start_date"))
        end_date = datetime.fromisoformat(arguments.get("end_date"))
        
        # REAL calendar lookup
        slots = calendar_service.find_available_slots(
            start_date=start_date,
            end_date=end_date,
            duration_minutes=60  # Get from service config
        )
        
        return {
            "success": True,
            "slots": slots,
            "message": f"Found {len(slots)} available slots for {service}"
        }
    
    elif tool_name == "book_appointment":
        customer_name = arguments.get("customer_name")
        customer_phone = arguments.get("customer_phone")
        service_name = arguments.get("service_name")
        appointment_datetime = datetime.fromisoformat(arguments.get("appointment_datetime"))
        notes = arguments.get("notes", "")
        
        # REAL calendar booking
        result = calendar_service.create_event(
            customer_name=customer_name,
            customer_phone=customer_phone,
            service_name=service_name,
            start_time=appointment_datetime,
            notes=notes
        )
        
        return result
    
    elif tool_name == "cancel_appointment":
        phone = arguments.get("customer_phone")
        
        # Find appointments by phone
        appointments = calendar_service.find_appointments_by_phone(phone)
        
        if not appointments:
            return {
                "success": False,
                "message": "No upcoming appointments found"
            }
        
        # Cancel the first/next appointment (or handle multiple)
        event_id = appointments[0]['id']
        result = calendar_service.cancel_appointment(event_id)
        
        return result
    
    elif tool_name == "reschedule_appointment":
        phone = arguments.get("customer_phone")
        new_datetime = datetime.fromisoformat(arguments.get("new_datetime"))
        
        # Find and reschedule
        appointments = calendar_service.find_appointments_by_phone(phone)
        
        if not appointments:
            return {
                "success": False,
                "message": "No appointments found to reschedule"
            }
        
        event_id = appointments[0]['id']
        result = calendar_service.reschedule_appointment(
            event_id=event_id,
            new_start_time=new_datetime
        )
        
        return result
    
    return {"success": False, "error": f"Unknown tool: {tool_name}"}
```

---

## Phase 4: Service Configuration & Business Rules

### Step 4.1: Create Service Configuration
```python
# app/services/service_config.py

SERVICE_CATALOG = {
    "consultation": {
        "name": "Consultation",
        "duration_minutes": 30,
        "buffer_minutes": 15,
        "description": "Initial consultation meeting"
    },
    "standard_appointment": {
        "name": "Standard Appointment",
        "duration_minutes": 60,
        "buffer_minutes": 15,
        "description": "Standard service appointment"
    },
    "extended_session": {
        "name": "Extended Session",
        "duration_minutes": 90,
        "buffer_minutes": 30,
        "description": "Extended service session"
    }
}

BUSINESS_HOURS = {
    "timezone": "America/Chicago",
    "hours": {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"},
        "saturday": "closed",
        "sunday": "closed"
    },
    "holidays": [
        "2025-12-25",  # Christmas
        "2025-01-01",  # New Year's
        # Add more holidays
    ],
    "breaks": [
        {"start": "12:00", "end": "13:00"}  # Lunch break
    ]
}
```

### Step 4.2: Implement Business Rules
```python
# app/services/booking_rules.py

class BookingRules:
    """Business rules for appointment booking"""
    
    @staticmethod
    def validate_booking_time(appointment_time: datetime) -> tuple[bool, str]:
        """Validate if booking time is allowed"""
        
        # Must be in future
        if appointment_time < datetime.now():
            return False, "Cannot book appointments in the past"
        
        # Must be within business hours
        day_name = appointment_time.strftime('%A').lower()
        if day_name not in BUSINESS_HOURS['hours']:
            return False, f"We are closed on {day_name.title()}"
        
        hours = BUSINESS_HOURS['hours'][day_name]
        if hours == "closed":
            return False, f"We are closed on {day_name.title()}"
        
        # Check time range
        time_str = appointment_time.strftime('%H:%M')
        if time_str < hours['start'] or time_str >= hours['end']:
            return False, f"Please book between {hours['start']} and {hours['end']}"
        
        # Check minimum advance notice (e.g., 2 hours)
        min_notice = timedelta(hours=2)
        if appointment_time < datetime.now() + min_notice:
            return False, "Please book at least 2 hours in advance"
        
        return True, "Valid"
    
    @staticmethod
    def get_cancellation_policy() -> str:
        """Return cancellation policy text"""
        return "Appointments must be cancelled at least 24 hours in advance"
    
    @staticmethod
    def can_cancel(appointment_time: datetime) -> bool:
        """Check if appointment can still be cancelled"""
        min_notice = timedelta(hours=24)
        return appointment_time > datetime.now() + min_notice
```

---

## Phase 5: Error Handling & Resilience

### Step 5.1: Implement Error Handling
```python
# app/services/calendar_service.py

from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class CalendarServiceError(Exception):
    """Custom exception for calendar service errors"""
    pass

def create_event(self, **kwargs):
    """Create event with error handling"""
    try:
        # ... event creation code ...
        return result
        
    except HttpError as e:
        error_code = e.resp.status
        
        if error_code == 409:
            # Conflict - time slot already booked
            logger.error("Time slot conflict")
            return {
                'success': False,
                'error': 'This time slot is no longer available'
            }
        
        elif error_code == 403:
            # Permission denied
            logger.error("Calendar permission denied")
            return {
                'success': False,
                'error': 'Calendar access error. Please contact support.'
            }
        
        elif error_code == 404:
            # Calendar not found
            logger.error("Calendar not found")
            return {
                'success': False,
                'error': 'Calendar configuration error'
            }
        
        else:
            logger.error(f"Calendar API error: {e}")
            return {
                'success': False,
                'error': 'Unable to book appointment. Please try again.'
            }
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'success': False,
            'error': 'An unexpected error occurred'
        }
```

### Step 5.2: Implement Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def _api_call_with_retry(self, func, *args, **kwargs):
    """Wrapper for API calls with retry logic"""
    return func(*args, **kwargs)
```

---

## Phase 6: Testing

### Step 6.1: Unit Tests
```python
# tests/test_calendar_service.py

import pytest
from datetime import datetime, timedelta
from app.services.calendar_service import GoogleCalendarService

@pytest.fixture
def calendar_service():
    return GoogleCalendarService()

def test_find_available_slots(calendar_service):
    """Test finding available time slots"""
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=7)
    
    slots = calendar_service.find_available_slots(start_date, end_date)
    
    assert isinstance(slots, list)
    assert len(slots) > 0
    assert 'datetime' in slots[0]

def test_create_appointment(calendar_service):
    """Test creating appointment"""
    appointment_time = datetime.now() + timedelta(days=2, hours=10)
    
    result = calendar_service.create_event(
        customer_name="Test User",
        customer_phone="+15551234567",
        service_name="Consultation",
        start_time=appointment_time
    )
    
    assert result['success'] == True
    assert 'event_id' in result
    
    # Cleanup
    calendar_service.cancel_appointment(result['event_id'])
```

### Step 6.2: Integration Tests
```bash
# scripts/test-calendar-integration.sh

#!/bin/bash
# Test real calendar integration

echo "Testing Google Calendar Integration..."

# Test 1: Find available slots
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "What times are available next Tuesday?"}
    ]
  }'

# Test 2: Book appointment
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Book appointment for John Doe, 555-1234, consultation, next Tuesday 2pm"}
    ]
  }'
```

---

## Phase 7: Enhanced Features

### Step 7.1: SMS Confirmations (Telnyx SMS API)
```python
# app/services/notification_service.py

import httpx
from app.core.config import settings

class NotificationService:
    def send_sms_confirmation(
        self,
        to_phone: str,
        appointment_details: dict
    ):
        """Send SMS confirmation via Telnyx"""
        
        message = f"""
Appointment Confirmed!

Date: {appointment_details['date']}
Time: {appointment_details['time']}
Service: {appointment_details['service']}
Location: {settings.BUSINESS_NAME}

Reply CANCEL to cancel
        """.strip()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.telnyx.com/v2/messages",
                headers={
                    "Authorization": f"Bearer {settings.TELNYX_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": settings.TELNYX_PHONE_NUMBER,
                    "to": to_phone,
                    "text": message
                }
            )
        
        return response.json()
```

### Step 7.2: Email Confirmations
```python
# Using SendGrid or similar
def send_email_confirmation(
    self,
    to_email: str,
    appointment_details: dict
):
    """Send email confirmation with calendar invite"""
    # Implement email sending with .ics attachment
    pass
```

### Step 7.3: Reminder System
```python
# app/services/reminder_service.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler

class ReminderService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
    
    def schedule_reminder(
        self,
        appointment_time: datetime,
        customer_phone: str,
        service_name: str
    ):
        """Schedule reminder 24 hours before appointment"""
        
        reminder_time = appointment_time - timedelta(hours=24)
        
        self.scheduler.add_job(
            self._send_reminder,
            'date',
            run_date=reminder_time,
            args=[customer_phone, appointment_time, service_name]
        )
    
    async def _send_reminder(self, phone, time, service):
        """Send reminder via SMS or voice call"""
        # Implement reminder logic
        pass
```

### Step 7.4: Multiple Staff/Resource Calendars
```python
# Support for multiple calendars (different staff members)

STAFF_CALENDARS = {
    "sarah": "sarah@accuthink.com.calendar.google.com",
    "mike": "mike@accuthink.com.calendar.google.com",
    "alex": "alex@accuthink.com.calendar.google.com"
}

def find_available_slots_multi_staff(
    self,
    start_date: datetime,
    end_date: datetime,
    staff_preference: str = None
):
    """Find available slots across multiple staff calendars"""
    
    if staff_preference and staff_preference in STAFF_CALENDARS:
        calendars = [STAFF_CALENDARS[staff_preference]]
    else:
        calendars = list(STAFF_CALENDARS.values())
    
    all_slots = []
    for calendar_id in calendars:
        slots = self.find_available_slots(
            start_date, end_date, calendar_id=calendar_id
        )
        all_slots.extend(slots)
    
    return sorted(all_slots, key=lambda x: x['datetime'])
```

---

## Phase 8: Deployment & Monitoring

### Step 8.1: Environment Setup
```bash
# Production .env
GOOGLE_CALENDAR_ID=production-calendar@group.calendar.google.com
GOOGLE_SERVICE_ACCOUNT_FILE=/app/secrets/service-account.json
GOOGLE_CALENDAR_TIMEZONE=America/Chicago

# Enable calendar features
CALENDAR_INTEGRATION_ENABLED=true
SEND_SMS_CONFIRMATIONS=true
SEND_EMAIL_CONFIRMATIONS=true
```

### Step 8.2: Monitoring & Logging
```python
# Log all calendar operations
logger.info(f"📅 Appointment booked: {customer_name} at {appointment_time}")
logger.info(f"📅 Appointment cancelled: event_id={event_id}")
logger.error(f"❌ Calendar API error: {error}")

# Track metrics
- Bookings per day
- Cancellation rate
- API error rate
- Average slot availability
```

### Step 8.3: Rate Limiting
```python
# Implement rate limiting for calendar API calls
from slowapi import Limiter

limiter = Limiter(key_func=lambda: "global")

@limiter.limit("100/hour")
def find_available_slots(...):
    # Prevents excessive API calls
    pass
```

---

## Summary Timeline

| Phase | Duration | Complexity | Priority |
|-------|----------|------------|----------|
| 1. API Setup | 1-2 days | Low | High |
| 2. Calendar Service | 3-5 days | Medium | High |
| 3. Tool Integration | 2-3 days | Medium | High |
| 4. Business Rules | 2-3 days | Low | Medium |
| 5. Error Handling | 1-2 days | Medium | High |
| 6. Testing | 2-3 days | Medium | High |
| 7. Enhanced Features | 5-7 days | High | Low |
| 8. Deployment | 1-2 days | Medium | High |

**Total Estimated Time**: 3-4 weeks for full implementation

---

## Quick Start (Minimum Viable Product)

If you want to start quickly with basic functionality:

1. **Week 1**: Phase 1-2 (Setup + Basic Calendar Service)
2. **Week 2**: Phase 3 + 5 (Tool Integration + Error Handling)
3. **Week 3**: Phase 6 + 8 (Testing + Deployment)
4. **Week 4+**: Phase 4 + 7 (Business Rules + Enhanced Features)

---

## Next Immediate Action

Start with **Phase 1.1-1.3**:
```bash
# 1. Go to Google Cloud Console
# 2. Create project
# 3. Enable Calendar API
# 4. Create service account
# 5. Download credentials
# 6. Share calendar with service account
# 7. Test connection

# Then run:
pip install google-auth google-api-python-client
python scripts/test-calendar-connection.py
```

Would you like me to create the initial calendar service implementation file to get started?
