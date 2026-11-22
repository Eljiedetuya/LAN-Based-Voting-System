import uuid
from django.conf import settings
from django.db import models

class VoterParticipation(models.Model):
    election = models.ForeignKey('elections.Election', on_delete=models.PROTECT, related_name='participations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='participations')
    has_voted = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['election', 'user'], name='uniq_election_voter')]
        indexes = [models.Index(fields=['election', 'has_voted'], name='idx_election_voted')]

class Ballot(models.Model):
    # A random identifier, with no identity FK or identifying timestamps.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey('elections.Election', on_delete=models.PROTECT, related_name='ballots')

class BallotSelection(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.PROTECT, related_name='selections')
    position = models.ForeignKey('elections.Position', on_delete=models.PROTECT)
    candidate = models.ForeignKey('elections.Candidate', on_delete=models.PROTECT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['ballot', 'position'], name='uniq_ballot_position')]
        indexes = [models.Index(fields=['candidate', 'position'], name='idx_candidate_position')]
