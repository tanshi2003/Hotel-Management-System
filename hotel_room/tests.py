import json
from datetime import date

from django.test import TestCase

# Create your tests here.


class RoomAvailabilityLifecycleTests(TestCase):
    def setUp(self):
        from user_profile.models import Person
        from hotel_room.models import Hotel, Room
        from room_booking.models import Booking, BookingHistory
        self.hotel = Hotel.objects.create(name='Test Hotel')
        self.room = Room.objects.create(
            hotel=self.hotel, room_number='A101', style='standard', booking_price=100,
        )
        self.person = Person.objects.create(
            name='Availability Guest', email='availability@example.com',
            phone='1234567890', account_type='guest',
        )
        self.booking = Booking.objects.create(
            reservation_number='R-AVAIL-001', person=self.person, booking_status='confirmed',
        )
        BookingHistory.objects.create(
            reservation_number=self.booking, room=self.room, person=self.person,
            check_in=date(2026, 12, 10), check_out=date(2026, 12, 12),
            total_price=200,
        )

    def availability(self, payload):
        return self.client.post(
            '/hms/rooms/details/availability',
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_active_booking_blocks_overlapping_dates(self):
        response = self.availability({
            'roomNumber': 'A101', 'checkInDate': '2026-12-11', 'checkOutDate': '2026-12-13',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_available'])

    def test_checkout_boundary_is_available(self):
        response = self.availability({
            'roomNumber': 'A101', 'checkInDate': '2026-12-12', 'checkOutDate': '2026-12-14',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_available'])

    def test_canceled_booking_does_not_block_room(self):
        self.booking.booking_status = 'canceled'
        self.booking.save(update_fields=['booking_status'])
        response = self.availability({
            'roomNumber': 'A101', 'checkInDate': '2026-12-11', 'checkOutDate': '2026-12-13',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_available'])

    def test_non_string_date_payload_returns_400_not_server_error(self):
        response = self.availability({
            'roomNumber': 'A101', 'checkInDate': 20261211, 'checkOutDate': '2026-12-13',
        })
        self.assertEqual(response.status_code, 400)

    def test_json_array_payload_returns_400(self):
        response = self.client.post(
            '/hms/rooms/details/availability',
            data=json.dumps(['not', 'an', 'object']),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
