from django.test import TestCase
from django.contrib.auth.hashers import check_password
from rest_framework.test import APIClient
from .models import User

class AccountTests(TestCase):
    def test_password_hashed(self):
        user=User.objects.create_user(username='account', password='StrongExample!321',
            role='STUDENT', student_id='S-10')
        self.assertNotEqual(user.password, 'StrongExample!321')
        self.assertTrue(check_password('StrongExample!321', user.password))

    def test_anonymous_not_allowed_to_read_account(self):
        api=APIClient()
        self.assertIn(api.get('/api/auth/me/').status_code, (401,403))
