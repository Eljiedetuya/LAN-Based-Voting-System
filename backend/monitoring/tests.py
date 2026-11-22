"""Contract/security tests for the Phase 10 read-only election picker endpoint."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User
from elections.models import Election

class MonitorElectionListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.election = Election.objects.create(title='Integration test election')
        self.monitor = User.objects.create_user(username='monitor-test', password='TestPass123!Unrelated', role=User.Role.MONITOR, display_name='Monitor')
        self.student = User.objects.create_user(username='student-test', password='TestPass123!Unrelated', role=User.Role.STUDENT, student_id='TEST-001', display_name='Student')

    def test_monitor_can_see_only_basic_election_metadata(self):
        self.client.force_authenticate(user=self.monitor)
        response = self.client.get('/api/monitoring/elections/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(set(response.data[0]), {'id', 'title', 'status'})

    def test_student_cannot_view_monitor_election_list(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/monitoring/elections/')
        self.assertEqual(response.status_code, 403)
