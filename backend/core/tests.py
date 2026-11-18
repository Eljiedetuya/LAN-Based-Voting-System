from django.test import SimpleTestCase
from django.urls import reverse

class HealthTests(SimpleTestCase):
    def test_health_url_resolves(self):
        self.assertEqual(reverse('health'), '/api/health/')
