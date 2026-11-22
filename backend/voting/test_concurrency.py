"""MySQL/InnoDB integration test. Run against a dedicated MySQL test database."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.db import close_old_connections, connections
from django.test import TransactionTestCase, skipUnlessDBFeature
from accounts.models import User
from elections.models import Election, Position, Candidate
from .models import VoterParticipation, Ballot
from .services import submit_ballot, VoteConflict


class ConcurrentSubmissionTests(TransactionTestCase):
    reset_sequences = True

    def test_two_simultaneous_requests_yield_one_ballot(self):
        if connections['default'].vendor != 'mysql':
            self.skipTest('Concurrency verification requires MySQL/InnoDB.')
        student = User.objects.create_user(
            username='race-student', student_id='RACE-001', password='StrongExample!321')
        election = Election.objects.create(title='Race test', status='OPEN', open_slot=1)
        position = Position.objects.create(election=election, name='President', display_order=1)
        candidate = Candidate.objects.create(position=position, name='Candidate A')
        VoterParticipation.objects.create(election=election, user=student)
        barrier = Barrier(2)
        selections = [{'position_id': position.id, 'candidate_id': candidate.id}]

        def attempt():
            close_old_connections()
            try:
                barrier.wait(timeout=5)
                submit_ballot(election_id=election.id, user=student, selections=selections)
                return 'accepted'
            except VoteConflict:
                return 'duplicate'
            finally:
                connections['default'].close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(attempt) for _ in range(2)]
            outcomes = [f.result(timeout=15) for f in futures]
        self.assertCountEqual(outcomes, ['accepted', 'duplicate'])
        self.assertEqual(Ballot.objects.filter(election=election).count(), 1)
        self.assertTrue(VoterParticipation.objects.get(election=election, user=student).has_voted)
