from django.test import TestCase
from user_profile.models import Person, Account

# Create your tests here.


class RegistrationIntegrityTests(TestCase):
    def test_registration_creates_person_and_hashed_account_together(self):
        response = self.client.post('/hms/user/registration/', {
            'name': 'Test Guest',
            'email': 'newguest@example.com',
            'phone': '1234567890',
            'password': 'strong-test-password',
        })
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(email='newguest@example.com')
        account = Account.objects.get(email='newguest@example.com')
        self.assertEqual(person.account_type, 'guest')
        self.assertTrue(account.is_guest)
        self.assertEqual(account.person_id, person.id)
        self.assertTrue(account.check_password('strong-test-password'))

    def test_duplicate_email_is_rejected_without_creating_second_person(self):
        person = Person.objects.create(name='Existing', email='existing@example.com', phone='1234567890', account_type='guest')
        Account.objects.create_user(email='existing@example.com', password='old-password', is_guest=True, person=person)
        response = self.client.post('/hms/user/registration/', {
            'name': 'Duplicate Guest',
            'email': 'existing@example.com',
            'phone': '9876543210',
            'password': 'new-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Person.objects.filter(email='existing@example.com').count(), 1)
        self.assertEqual(Account.objects.filter(email='existing@example.com').count(), 1)

class LoginNormalizationTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            name='Login Guest', email='login-guest@example.com',
            phone='1234567890', account_type='guest',
        )
        Account.objects.create_user(
            email='login-guest@example.com', password='test-login-password',
            is_guest=True, person=self.person,
        )

    def test_login_accepts_mixed_case_email(self):
        response = self.client.post('/hms/user/login/', {
            'email': 'LOGIN-GUEST@EXAMPLE.COM',
            'password': 'test-login-password',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_user_manager_normalizes_email(self):
        account = Account.objects.create_user(
            email='  MixedCase@Example.com  ', password='test-password', is_guest=True,
        )
        self.assertEqual(account.email, 'mixedcase@example.com')
