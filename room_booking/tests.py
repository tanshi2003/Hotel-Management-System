from datetime import date
from types import SimpleNamespace

from django.test import TestCase

from room_booking.views import calculate_stay_price


class StayPriceTests(TestCase):
    def setUp(self):
        self.room = SimpleNamespace(booking_price=120)

    def test_room_rate_is_multiplied_by_nights(self):
        self.assertEqual(calculate_stay_price(self.room, date(2026, 12, 1), date(2026, 12, 4)), 360)

    def test_add_on_services_are_charged_once_per_stay(self):
        total = calculate_stay_price(
            self.room, date(2026, 12, 1), date(2026, 12, 3),
            cleaning=True, laundry=True, breakfast=True
        )
        self.assertEqual(total, 255.5)

    def test_same_day_checkout_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_stay_price(self.room, date(2026, 12, 1), date(2026, 12, 1))


class BookingLifecyclePolicyTests(TestCase):
    def test_receptionist_and_admin_have_distinct_allowed_targets(self):
        from room_booking.lifecycle import allowed_targets
        self.assertEqual(allowed_targets('requested', 'receptionist'), {'pending', 'confirmed', 'canceled'})
        self.assertEqual(allowed_targets('requested', 'manager'), {'pending', 'confirmed', 'canceled', 'abandoned'})
        self.assertEqual(allowed_targets('confirmed', 'guest'), {'canceled'})
        self.assertEqual(allowed_targets('checked-in', 'guest'), set())

    def test_lifecycle_transition_helper_persists_only_allowed_transition(self):
        from unittest.mock import Mock
        from django.core.exceptions import ValidationError
        from room_booking.lifecycle import transition_booking
        booking = Mock()
        booking.booking_status = 'requested'
        transition_booking(booking, 'confirmed', 'receptionist')
        self.assertEqual(booking.booking_status, 'confirmed')
        booking.save.assert_called_once_with(update_fields=['booking_status'])
        booking.save.reset_mock()
        with self.assertRaises(ValidationError):
            transition_booking(booking, 'abandoned', 'receptionist')
        booking.save.assert_not_called()
