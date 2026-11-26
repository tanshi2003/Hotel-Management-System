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

class BookingCreationConsistencyTests(TestCase):
    def setUp(self):
        from user_profile.models import Person, Account
        from hotel_room.models import Hotel, Room
        from room_booking.models import WishList
        self.hotel = Hotel.objects.create(name='Booking Test Hotel')
        self.room1 = Room.objects.create(hotel=self.hotel, room_number='B201', style='standard', booking_price=100)
        self.room2 = Room.objects.create(hotel=self.hotel, room_number='B202', style='delux', booking_price=150)
        self.person = Person.objects.create(name='Booking Guest', email='booking@example.com', phone='1234567890', account_type='guest')
        self.user = Account.objects.create_user(email='booking@example.com', password='test-password', person=self.person, is_guest=True)
        self.client.force_login(self.user)
        self.wishlist_model = WishList
        self.booking_endpoint = '/hms/room-booking/book-now/'

    def add_wishlist(self, room, checkin=date(2026, 12, 10), checkout=date(2026, 12, 12), cleaning=False):
        return self.wishlist_model.objects.create(
            person=self.person, room=room, check_in=checkin, check_out=checkout,
            room_cleaning=cleaning, total_price=99999,
        )

    def book(self, ids):
        import json
        return self.client.post(self.booking_endpoint, data=json.dumps({'itemId': ids}), content_type='application/json')

    def test_overlapping_wishlist_items_for_same_room_rejected_without_partial_writes(self):
        from room_booking.models import Booking, BookingHistory
        first = self.add_wishlist(self.room1)
        second = self.add_wishlist(self.room1, date(2026, 12, 11), date(2026, 12, 13))
        response = self.book([first.pk, second.pk])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)
        self.assertEqual(BookingHistory.objects.count(), 0)
        self.assertEqual(self.wishlist_model.objects.filter(person=self.person).count(), 2)

    def test_successful_booking_creates_consistent_booking_history_and_recalculates_prices(self):
        from room_booking.models import Booking, BookingHistory
        first = self.add_wishlist(self.room1, cleaning=True)
        second = self.add_wishlist(self.room2)
        response = self.book([str(first.pk), second.pk])
        self.assertEqual(response.status_code, 201)
        booking = Booking.objects.get(reservation_number=response.json()['reservationNumber'])
        self.assertEqual(booking.booking_status, 'requested')
        self.assertSetEqual(set(booking.rooms.values_list('pk', flat=True)), {self.room1.pk, self.room2.pk})
        histories = list(BookingHistory.objects.filter(reservation_number=booking).order_by('room_id'))
        self.assertEqual(len(histories), 2)
        self.assertEqual({history.room_id for history in histories}, {self.room1.pk, self.room2.pk})
        self.assertTrue(all(history.person_id == self.person.pk for history in histories))
        self.assertEqual({history.total_price for history in histories}, {205, 300})
        self.assertFalse(self.wishlist_model.objects.filter(person=self.person).exists())

    def test_invalid_wishlist_ids_are_rejected_without_creating_booking(self):
        from room_booking.models import Booking
        for bad_ids in ([True], [1.5], [-1], ['not-an-id']):
            with self.subTest(bad_ids=bad_ids):
                response = self.book(bad_ids)
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)
    def test_existing_active_booking_conflict_returns_409_and_preserves_wishlist(self):
        from room_booking.models import Booking, BookingHistory
        existing = Booking.objects.create(
            reservation_number='R-EXISTING-001', person=self.person, booking_status='confirmed',
        )
        BookingHistory.objects.create(
            reservation_number=existing, room=self.room1, person=self.person,
            check_in=date(2026, 12, 10), check_out=date(2026, 12, 12), total_price=200,
        )
        item = self.add_wishlist(self.room1)
        response = self.book([item.pk])
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(BookingHistory.objects.count(), 1)
        self.assertTrue(self.wishlist_model.objects.filter(pk=item.pk).exists())
    def test_non_object_booking_payload_returns_400(self):
        import json
        from room_booking.models import Booking
        response = self.client.post(
            self.booking_endpoint, data=json.dumps(['not', 'an', 'object']),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)
