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
