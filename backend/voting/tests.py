from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from elections.models import Election, Position, Candidate
from voting.models import VoterParticipation, Ballot, BallotSelection
from voting.services import submit_ballot, VoteConflict
from rest_framework.exceptions import ValidationError


class VoteIntegrityTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='stu1', student_id='STU-001',
            password='ExampleStrongPass!321', role='STUDENT', display_name='Student One')
        self.other = User.objects.create_user(username='stu2', student_id='STU-002',
            password='ExampleStrongPass!321', role='STUDENT', display_name='Student Two')
        self.monitor = User.objects.create_user(username='monitor', password='ExampleStrongPass!321',
            role='MONITOR', display_name='Monitor')
        self.admin = User.objects.create_user(username='admin', password='ExampleStrongPass!321',
            role='ADMIN', display_name='Administrator')
        self.election = Election.objects.create(title='Council', status='OPEN', open_slot=1)
        # Set required lifecycle timestamp for this test fixture.
        from django.utils import timezone
        self.election.opened_at = timezone.now()
        self.election.save(update_fields=['opened_at'])
        self.position = Position.objects.create(election=self.election, name='President', display_order=1)
        self.candidate = Candidate.objects.create(position=self.position, name='Candidate A')
        self.wrong = Candidate.objects.create(position=self.position, name='Candidate B')
        VoterParticipation.objects.create(user=self.student, election=self.election)
        self.payload = {'selections': [{'position_id': self.position.id, 'candidate_id': self.candidate.id}]}

    def test_success_and_duplicate_rejection(self):
        result = submit_ballot(election_id=self.election.id, user=self.student,
            selections=self.payload['selections'])
        self.assertEqual(result['status'], 'recorded')
        self.assertEqual(Ballot.objects.count(), 1)
        self.assertEqual(BallotSelection.objects.count(), 1)
        self.assertTrue(VoterParticipation.objects.get(user=self.student).has_voted)
        with self.assertRaises(VoteConflict):
            submit_ballot(election_id=self.election.id, user=self.student,
                selections=self.payload['selections'])
        self.assertEqual(Ballot.objects.count(), 1)

    def test_invalid_ballot_rolls_back(self):
        with self.assertRaises(ValidationError):
            submit_ballot(election_id=self.election.id, user=self.student, selections=[])
        self.assertEqual(Ballot.objects.count(), 0)
        self.assertFalse(VoterParticipation.objects.get(user=self.student).has_voted)

    def test_wrong_position_selection_rejected(self):
        another = Position.objects.create(election=self.election, name='Secretary', display_order=2)
        other_candidate = Candidate.objects.create(position=another, name='Secretary X')
        with self.assertRaises(ValidationError):
            submit_ballot(election_id=self.election.id, user=self.student,
                selections=[{'position_id':self.position.id,'candidate_id':other_candidate.id},
                            {'position_id':another.id,'candidate_id':self.candidate.id}])
        self.assertEqual(Ballot.objects.count(), 0)

    def test_student_denied_admin_route(self):
        api = APIClient()
        api.force_authenticate(self.student)
        response = api.get('/api/admin/elections/')
        self.assertEqual(response.status_code, 403)

    def test_monitor_cannot_submit_vote(self):
        api = APIClient()
        api.force_authenticate(self.monitor)
        self.assertEqual(api.post(f'/api/elections/{self.election.id}/submit-vote/', self.payload, format='json').status_code, 403)

    def test_role_cannot_be_supplied_on_student_creation(self):
        api = APIClient()
        api.force_authenticate(self.admin)
        response = api.post('/api/admin/voters/', {'username':'newstudent',
            'student_id':'STU-003', 'display_name':'New Student',
            'password':'ExampleStrongPass!321', 'role':'ADMIN'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.get(username='newstudent').role, 'STUDENT')

    def test_results_hidden_until_closed(self):
        api = APIClient()
        api.force_authenticate(self.admin)
        self.assertEqual(api.get(f'/api/results/{self.election.id}/').status_code, 403)
        submit_ballot(election_id=self.election.id, user=self.student,
                      selections=self.payload['selections'])
        self.election.status='CLOSED'
        self.election.open_slot=None
        from django.utils import timezone
        self.election.closed_at=timezone.now()
        self.election.save()
        response = api.get(f'/api/results/{self.election.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['accepted_ballots'], 1)
        totals = response.data['positions'][0]['candidates']
        self.assertEqual(sum(x['votes'] for x in totals), 1)

    def test_no_identity_field_on_ballot(self):
        names={field.name for field in Ballot._meta.fields}
        self.assertFalse({'user','student_id','participation'} & names)

    def test_monitor_participation_is_aggregate(self):
        api=APIClient()
        api.force_authenticate(self.monitor)
        response=api.get('/api/monitoring/participation/', {'election_id':self.election.id})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['eligible'],1)
        self.assertNotIn('student_id', str(response.data))
