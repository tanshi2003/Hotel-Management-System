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
        self.account = Account.objects.create_user(
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
        self.assertEqual(self.client.session['_auth_user_id'], str(self.account.pk))

    def test_user_manager_normalizes_email(self):
        account = Account.objects.create_user(
            email='  MixedCase@Example.com  ', password='test-password', is_guest=True,
        )
        self.assertEqual(account.email, 'mixedcase@example.com')


class ProfileUpdateConsistencyTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            name='Profile Guest', email='profile-guest@example.com',
            phone='1111111111', account_type='guest',
        )
        self.account = Account.objects.create_user(
            email=self.person.email, password='profile-password',
            is_guest=True, person=self.person,
        )
        self.client.force_login(self.account)

    def profile_payload(self, **overrides):
        payload = {
            'name': 'Updated Profile Guest',
            'email': self.person.email,
            'phone': '2222222222',
            'account_type': 'guest',
            'city': 'Delhi',
            'country': 'India',
            'zip_code': '110001',
        }
        payload.update(overrides)
        return payload

    def test_profile_and_new_address_are_saved_together(self):
        response = self.client.post('/hms/user/profile/', self.profile_payload())
        self.assertEqual(response.status_code, 302)
        self.person.refresh_from_db()
        self.assertEqual(self.person.name, 'Updated Profile Guest')
        self.assertEqual(self.person.phone, '2222222222')
        address = self.person.address
        self.assertEqual(address.city, 'Delhi')
        self.assertEqual(address.country, 'India')
        self.assertEqual(address.zip_code, 110001)

    def test_existing_address_is_updated_with_profile(self):
        from user_profile.models import Address
        Address.objects.create(city='Old City', country='India', zip_code=100000, person=self.person)
        response = self.client.post('/hms/user/profile/', self.profile_payload(city='Mumbai', zip_code='400001'))
        self.assertEqual(response.status_code, 302)
        self.person.refresh_from_db()
        self.assertEqual(self.person.name, 'Updated Profile Guest')
        self.assertEqual(self.person.address.city, 'Mumbai')
        self.assertEqual(self.person.address.zip_code, 400001)

    def test_address_save_failure_rolls_back_profile_update(self):
        from unittest.mock import patch
        from django.db import IntegrityError
        with patch('user_profile.views.Address.save', side_effect=IntegrityError('forced test failure')):
            response = self.client.post('/hms/user/profile/', self.profile_payload(name='Should Roll Back'))
        self.assertEqual(response.status_code, 200)
        self.person.refresh_from_db()
        self.assertEqual(self.person.name, 'Profile Guest')
        self.assertEqual(self.person.phone, '1111111111')
        self.assertFalse(hasattr(self.person, 'address'))
