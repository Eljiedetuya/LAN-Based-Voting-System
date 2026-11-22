"""Integration tests to run with Django + the local MySQL test database."""
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from elections.models import Election, Position, Candidate
from voting.models import VoterParticipation, Ballot, BallotSelection


class ElectionIntegrityAndReportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(username='report-admin', password='UnrelatedTest123!', role=User.Role.ADMIN, display_name='Admin')
        self.monitor = User.objects.create_user(username='report-monitor', password='UnrelatedTest123!', role=User.Role.MONITOR, display_name='Monitor')
        self.student = User.objects.create_user(username='report-voter', password='UnrelatedTest123!', role=User.Role.STUDENT, student_id='REPORT-001', display_name='Voter')
        self.election = Election.objects.create(title='Report test', status=Election.Status.CLOSED)
        self.position = Position.objects.create(election=self.election, name='President', display_order=1)
        self.candidate = Candidate.objects.create(position=self.position, name='Candidate A')
        self.participation = VoterParticipation.objects.create(election=self.election, user=self.student, has_voted=True)
        self.ballot = Ballot.objects.create(election=self.election)
        BallotSelection.objects.create(ballot=self.ballot, position=self.position, candidate=self.candidate)

    def test_admin_aggregate_integrity(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/monitoring/integrity/{self.election.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['integrity_ok'])
        self.assertNotIn('ballot_id', response.data)
        self.assertNotIn('user_id', response.data)

    def test_monitor_denied_integrity_endpoint(self):
        self.client.force_authenticate(user=self.monitor)
        self.assertEqual(self.client.get(f'/api/monitoring/integrity/{self.election.pk}/').status_code, 403)

    def test_closed_csv_report_contains_aggregates_only(self):
        self.client.force_authenticate(user=self.monitor)
        response = self.client.get(f'/api/reports/{self.election.pk}/csv/')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('Candidate A', body)
        self.assertNotIn('REPORT-001', body)
        self.assertNotIn(str(self.ballot.pk), body)

    def test_open_election_report_rejected(self):
        self.election.status = Election.Status.OPEN
        self.election.save(update_fields=['status'])
        self.client.force_authenticate(user=self.admin_user)
        self.assertEqual(self.client.get(f'/api/reports/{self.election.pk}/csv/').status_code, 403)

    def test_inconsistent_ballot_prevents_report(self):
        self.participation.has_voted = False
        self.participation.save(update_fields=['has_voted'])
        self.client.force_authenticate(user=self.admin_user)
        self.assertEqual(self.client.get(f'/api/reports/{self.election.pk}/csv/').status_code, 409)

    def test_student_denied_results_and_reports(self):
        self.client.force_authenticate(user=self.student)
        self.assertEqual(self.client.get(f'/api/reports/{self.election.pk}/csv/').status_code, 403)
        self.assertEqual(self.client.get(f'/api/results/{self.election.pk}/').status_code, 403)
