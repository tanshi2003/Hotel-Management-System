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
