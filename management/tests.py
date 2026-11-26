from django.test import TestCase
from user_profile.models import Account


class ManagementAccessTests(TestCase):
    def setUp(self):
        self.guest = Account.objects.create_user(email='guest@example.com', password='test-password', is_guest=True)
        self.receptionist = Account.objects.create_user(email='reception@example.com', password='test-password', is_receptionist=True)

    def test_anonymous_users_are_redirected_to_login(self):
        response = self.client.get('/hms/management/')
        self.assertEqual(response.status_code, 302)

    def test_guest_cannot_access_management_page(self):
        self.client.force_login(self.guest)
        response = self.client.get('/hms/management/')
        self.assertEqual(response.status_code, 403)

    def test_receptionist_can_access_management_page(self):
        self.client.force_login(self.receptionist)
        response = self.client.get('/hms/management/')
        self.assertEqual(response.status_code, 200)


class BookingStatusTransitionTests(TestCase):
    def setUp(self):
        from user_profile.models import Person
        from room_booking.models import Booking
        self.person = Person.objects.create(name='Lifecycle Guest', email='life@example.com', phone='123', account_type='guest')
        self.guest = Account.objects.create_user(email='life@example.com', password='pw', is_guest=True, person=self.person)
        self.receptionist = Account.objects.create_user(email='life-reception@example.com', password='pw', is_receptionist=True)
        self.manager = Account.objects.create_user(email='life-manager@example.com', password='pw', is_manager=True)
        self.booking = Booking.objects.create(person=self.person, reservation_number='R-LIFECYCLE-1', booking_status='requested')

    def status_post(self, status):
        import json
        return self.client.post(
            f'/hms/management/booking/{self.booking.reservation_number}/status/',
            data=json.dumps({'status': status}), content_type='application/json',
    )

    def test_guest_cannot_use_staff_transition_endpoint(self):
        self.client.force_login(self.guest)
        self.assertEqual(self.status_post('confirmed').status_code, 403)

    def test_receptionist_can_confirm_requested_booking(self):
        self.client.force_login(self.receptionist)
        response = self.status_post('confirmed')
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.booking_status, 'confirmed')

    def test_receptionist_cannot_mark_booking_abandoned(self):
        self.client.force_login(self.receptionist)
        response = self.status_post('abandoned')
        self.assertEqual(response.status_code, 409)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.booking_status, 'requested')

    def test_manager_can_mark_booking_abandoned(self):
        self.client.force_login(self.manager)
        response = self.status_post('abandoned')
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.booking_status, 'abandoned')

    def test_checked_out_booking_cannot_be_cancelled(self):
        self.booking.booking_status = 'checked-out'
        self.booking.save(update_fields=['booking_status'])
        self.client.force_login(self.manager)
        self.assertEqual(self.status_post('canceled').status_code, 409)

    def test_transition_endpoint_rejects_invalid_json_shape(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            f'/hms/management/booking/{self.booking.reservation_number}/status/',
            data='[]', content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class GuestCancellationTests(TestCase):
    def setUp(self):
        from user_profile.models import Person
        from room_booking.models import Booking
        self.person = Person.objects.create(name='Cancel Guest', email='cancel@example.com', phone='123', account_type='guest')
        self.guest = Account.objects.create_user(email='cancel@example.com', password='pw', is_guest=True, person=self.person)
        self.other_person = Person.objects.create(name='Other Guest', email='other@example.com', phone='123', account_type='guest')
        self.other_guest = Account.objects.create_user(email='other@example.com', password='pw', is_guest=True, person=self.other_person)
        self.booking = Booking.objects.create(person=self.person, reservation_number='R-CANCEL-1', booking_status='confirmed')

    def cancel(self):
        return self.client.post(f'/hms/room-booking/booking/{self.booking.reservation_number}/cancel/')

    def test_guest_can_cancel_own_confirmed_booking(self):
        self.client.force_login(self.guest)
        response = self.cancel()
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.booking_status, 'canceled')

    def test_guest_cannot_cancel_another_guest_booking(self):
        self.client.force_login(self.other_guest)
        self.assertEqual(self.cancel().status_code, 404)

    def test_guest_cannot_cancel_after_checkin(self):
        self.booking.booking_status = 'checked-in'
        self.booking.save(update_fields=['booking_status'])
        self.client.force_login(self.guest)
        self.assertEqual(self.cancel().status_code, 409)
