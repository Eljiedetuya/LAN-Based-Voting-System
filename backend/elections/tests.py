from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from accounts.models import User
from elections.models import Election, Position, Candidate
from elections.services import open_election, close_election
from voting.models import VoterParticipation

class ElectionLifecycleTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='administrator', password='ExampleStrongPass!321', role='ADMIN')
        self.student = User.objects.create_user(username='student1', student_id='STU-10', password='ExampleStrongPass!321')
        self.election = Election.objects.create(title='Election')
        self.position = Position.objects.create(election=self.election, name='President', display_order=1)
        Candidate.objects.create(position=self.position, name='Candidate')
        VoterParticipation.objects.create(election=self.election, user=self.student)

    def test_open_then_close(self):
        self.assertEqual(open_election(self.election.id, self.admin).status, Election.Status.OPEN)
        self.assertEqual(close_election(self.election.id, self.admin).status, Election.Status.CLOSED)
        with self.assertRaises(ValidationError):
            open_election(self.election.id, self.admin)

    def test_only_one_open_election(self):
        open_election(self.election.id, self.admin)
        another = Election.objects.create(title='Another')
        Position.objects.create(election=another, name='President', display_order=1)
        Candidate.objects.create(position=Position.objects.get(election=another), name='Other')
        VoterParticipation.objects.create(election=another, user=self.student)
        with self.assertRaises(ValidationError):
            open_election(another.id, self.admin)
