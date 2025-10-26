"""Google Calendar integration service for appointment booking.

This module provides real calendar integration replacing the mock
implementations in ai_voice.py.

Setup:
1. Create Google Cloud project and enable Calendar API
2. Create Service Account and download JSON credentials
3. Share Google Calendar with service account email
4. Set GOOGLE_CALENDAR_ID and GOOGLE_SERVICE_ACCOUNT_FILE in .env
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """Service for managing appointments via Google Calendar API."""

    def __init__(
        self,
        calendar_id: Optional[str] = None,
        service_account_file: Optional[str] = None,
        timezone: str = "UTC"
    ):
        """Initialize Google Calendar service.

        Parameters
        ----------
        calendar_id : str, optional
            Google Calendar ID. Defaults to env variable GOOGLE_CALENDAR_ID
        service_account_file : str, optional
            Path to service account JSON. Defaults to env variable
        timezone : str
            Timezone for calendar operations
        """
        self.calendar_id = calendar_id or os.getenv('GOOGLE_CALENDAR_ID')
        self.service_account_file = (
            service_account_file or 
            os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        )
        self.timezone = timezone or os.getenv('GOOGLE_CALENDAR_TIMEZONE', 'UTC')
        
        if not self.calendar_id:
            raise ValueError("GOOGLE_CALENDAR_ID environment variable not set")
        
        if not self.service_account_file:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable not set")
        
        self.service = self._authenticate()
        logger.info(f"✅ Google Calendar service initialized for {self.calendar_id}")

    def _authenticate(self):
        """Authenticate with Google Calendar API using service account.

        Returns
        -------
        Resource
            Authenticated Google Calendar API service
        """
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=SCOPES
            )
            service = build('calendar', 'v3', credentials=creds)
            logger.info("✅ Successfully authenticated with Google Calendar API")
            return service
        except Exception as e:
            logger.error(f"❌ Failed to authenticate with Google Calendar: {e}")
            raise

    def find_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        buffer_minutes: int = 15,
        business_hours: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Find available appointment slots in the calendar.

        Parameters
        ----------
        start_date : datetime
            Start of search range
        end_date : datetime
            End of search range
        duration_minutes : int
            Duration of appointment in minutes
        buffer_minutes : int
            Buffer time between appointments
        business_hours : dict, optional
            Business hours configuration

        Returns
        -------
        List[Dict]
            List of available time slots with datetime and display info
        """
        if business_hours is None:
            business_hours = {
                'start': '09:00',
                'end': '17:00',
                'days': [0, 1, 2, 3, 4]  # Monday-Friday (0=Monday)
            }

        try:
            # Get existing events in date range
            logger.info(f"🔍 Searching for available slots from {start_date} to {end_date}")
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            existing_events = events_result.get('items', [])
            logger.info(f"📅 Found {len(existing_events)} existing events")

            # Generate potential time slots
            available_slots = self._generate_available_slots(
                start_date,
                end_date,
                existing_events,
                duration_minutes,
                buffer_minutes,
                business_hours
            )

            logger.info(f"✅ Found {len(available_slots)} available slots")
            return available_slots

        except HttpError as e:
            logger.error(f"❌ Calendar API error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error finding slots: {e}")
            return []

    def _generate_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        existing_events: List[Dict],
        duration_minutes: int,
        buffer_minutes: int,
        business_hours: Dict
    ) -> List[Dict[str, Any]]:
        """Generate list of available time slots.

        This is a simplified implementation. In production, you'd want more
        sophisticated slot generation considering holidays, breaks, etc.
        """
        available_slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            # Check if this day is a business day
            if current_date.weekday() not in business_hours['days']:
                current_date += timedelta(days=1)
                continue

            # Parse business hours for this day
            start_hour, start_min = map(int, business_hours['start'].split(':'))
            end_hour, end_min = map(int, business_hours['end'].split(':'))

            day_start = datetime.combine(
                current_date,
                datetime.min.time().replace(hour=start_hour, minute=start_min)
            )
            day_end = datetime.combine(
                current_date,
                datetime.min.time().replace(hour=end_hour, minute=end_min)
            )

            # Generate slots for this day
            current_slot = day_start
            while current_slot + timedelta(minutes=duration_minutes) <= day_end:
                slot_end = current_slot + timedelta(minutes=duration_minutes)

                # Check if slot conflicts with existing events
                is_available = True
                for event in existing_events:
                    event_start = datetime.fromisoformat(
                        event['start'].get('dateTime', event['start'].get('date'))
                    )
                    event_end = datetime.fromisoformat(
                        event['end'].get('dateTime', event['end'].get('date'))
                    )

                    # Check for overlap (with buffer)
                    if not (slot_end <= event_start or current_slot >= event_end):
                        is_available = False
                        break

                if is_available and current_slot > datetime.now():
                    available_slots.append({
                        'datetime': current_slot.isoformat(),
                        'display': current_slot.strftime('%A, %B %d at %I:%M %p'),
                        'date': current_slot.strftime('%Y-%m-%d'),
                        'time': current_slot.strftime('%I:%M %p')
                    })

                # Move to next slot (including buffer)
                current_slot += timedelta(minutes=duration_minutes + buffer_minutes)

            current_date += timedelta(days=1)

        return available_slots

    def create_event(
        self,
        customer_name: str,
        customer_phone: str,
        service_name: str,
        start_time: datetime,
        duration_minutes: int = 60,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Create a calendar event (book appointment).

        Parameters
        ----------
        customer_name : str
            Customer's full name
        customer_phone : str
            Customer's phone number
        service_name : str
            Name of service being booked
        start_time : datetime
            Appointment start time
        duration_minutes : int
            Duration in minutes
        notes : str
            Additional notes

        Returns
        -------
        Dict
            Result with success status, event_id, and details
        """
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)

            event = {
                'summary': f'{service_name} - {customer_name}',
                'description': f'''
Appointment Details:
- Customer: {customer_name}
- Phone: {customer_phone}
- Service: {service_name}
- Notes: {notes}

Booked via AI Assistant on {datetime.now().strftime('%Y-%m-%d at %I:%M %p')}
                '''.strip(),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': self.timezone,
                },
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

            logger.info(f"📅 Creating appointment for {customer_name} at {start_time}")
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendNotifications=True
            ).execute()

            logger.info(f"✅ Appointment created: {created_event['id']}")

            return {
                'success': True,
                'event_id': created_event['id'],
                'event_link': created_event.get('htmlLink'),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'message': f"Successfully booked {service_name} for {customer_name} on {start_time.strftime('%A, %B %d at %I:%M %p')}"
            }

        except HttpError as e:
            error_code = e.resp.status
            logger.error(f"❌ Calendar API error {error_code}: {e}")
            
            if error_code == 409:
                return {
                    'success': False,
                    'error': 'This time slot is no longer available. Please choose another time.'
                }
            elif error_code == 403:
                return {
                    'success': False,
                    'error': 'Calendar access error. Please contact support.'
                }
            else:
                return {
                    'success': False,
                    'error': 'Unable to book appointment. Please try again.'
                }

        except Exception as e:
            logger.error(f"❌ Unexpected error creating event: {e}")
            return {
                'success': False,
                'error': 'An unexpected error occurred while booking.'
            }

    def find_appointments_by_phone(
        self,
        phone_number: str,
        days_ahead: int = 30
    ) -> List[Dict]:
        """Find customer appointments by phone number.

        Parameters
        ----------
        phone_number : str
            Customer's phone number
        days_ahead : int
            How many days ahead to search

        Returns
        -------
        List[Dict]
            List of appointment events
        """
        try:
            now = datetime.now()
            future = now + timedelta(days=days_ahead)

            logger.info(f"🔍 Searching for appointments for {phone_number}")

            events = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now.isoformat(),
                timeMax=future.isoformat(),
                privateExtendedProperty=f'customer_phone={phone_number}',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            appointments = events.get('items', [])
            logger.info(f"📅 Found {len(appointments)} appointments for {phone_number}")

            return appointments

        except Exception as e:
            logger.error(f"❌ Error finding appointments: {e}")
            return []

    def cancel_appointment(
        self,
        event_id: str,
        send_notifications: bool = True
    ) -> Dict[str, Any]:
        """Cancel an appointment by deleting the calendar event.

        Parameters
        ----------
        event_id : str
            Google Calendar event ID
        send_notifications : bool
            Whether to send cancellation notifications

        Returns
        -------
        Dict
            Result with success status and message
        """
        try:
            logger.info(f"🗑️ Cancelling appointment: {event_id}")

            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendNotifications=send_notifications
            ).execute()

            logger.info(f"✅ Appointment cancelled: {event_id}")

            return {
                'success': True,
                'message': 'Appointment has been cancelled successfully'
            }

        except HttpError as e:
            logger.error(f"❌ Error cancelling appointment: {e}")
            return {
                'success': False,
                'error': 'Unable to cancel appointment. Please contact support.'
            }

    def reschedule_appointment(
        self,
        event_id: str,
        new_start_time: datetime,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """Reschedule an appointment to a new time.

        Parameters
        ----------
        event_id : str
            Google Calendar event ID
        new_start_time : datetime
            New start time for appointment
        duration_minutes : int
            Duration in minutes

        Returns
        -------
        Dict
            Result with success status and new details
        """
        try:
            logger.info(f"📅 Rescheduling appointment {event_id} to {new_start_time}")

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

            logger.info(f"✅ Appointment rescheduled: {event_id}")

            return {
                'success': True,
                'event_id': updated_event['id'],
                'new_start_time': new_start_time.isoformat(),
                'message': f"Appointment rescheduled to {new_start_time.strftime('%A, %B %d at %I:%M %p')}"
            }

        except HttpError as e:
            logger.error(f"❌ Error rescheduling appointment: {e}")
            return {
                'success': False,
                'error': 'Unable to reschedule appointment. Please try again.'
            }


# TODO: Add these when ready
# - Business hours validation
# - Holiday checking
# - Multiple calendar support (different staff)
# - Conflict detection with better algorithms
# - Waitlist management
# - Recurring appointments
