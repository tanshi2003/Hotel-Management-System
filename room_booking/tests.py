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
