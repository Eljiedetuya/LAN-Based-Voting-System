import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from elections.models import Election, Position, Candidate
from .models import VoterParticipation, Ballot, BallotSelection

class VoteConflict(ValidationError):
    status_code = 409
    default_code = 'vote_conflict'

@transaction.atomic
def submit_ballot(*, election_id, user, selections):
    # Lock order is always election -> eligibility; closing election follows same order.
    election = get_object_or_404(Election.objects.select_for_update(), pk=election_id)
    if election.status != Election.Status.OPEN:
        raise VoteConflict('Election is not open.')
    participation = VoterParticipation.objects.select_for_update().filter(
        election=election, user=user).first()
    if participation is None:
        raise VoteConflict('Not eligible for this election.')
    if participation.has_voted:
        raise VoteConflict('Vote already recorded for this election.')
    if not isinstance(selections, list):
        raise ValidationError({'selections': 'Expected an array of selections.'})
    positions = list(Position.objects.filter(election=election).order_by('id'))
    if not positions or len(selections) != len(positions):
        raise ValidationError({'selections': 'Select exactly one candidate for every position.'})
    mapping = {}
    for item in selections:
        if not isinstance(item, dict) or set(item) != {'position_id', 'candidate_id'}:
            raise ValidationError({'selections': 'Each selection needs position_id and candidate_id.'})
        position_id, candidate_id = item['position_id'], item['candidate_id']
        if type(position_id) is not int or type(candidate_id) is not int or position_id in mapping:
            raise ValidationError({'selections': 'Invalid or repeated position selection.'})
        mapping[position_id] = candidate_id
    if set(mapping) != {p.id for p in positions}:
        raise ValidationError({'selections': 'Ballot positions are incomplete or invalid.'})
    valid_pairs = set(Candidate.objects.filter(position__election=election,
        position_id__in=mapping.keys(), pk__in=mapping.values()).values_list('position_id', 'id'))
    if set(mapping.items()) != valid_pairs:
        raise ValidationError({'selections': 'One or more candidates are invalid for their positions.'})
    # The random ID is never returned and never logged alongside voter identity.
    ballot = Ballot.objects.create(id=uuid.uuid4(), election=election)
    BallotSelection.objects.bulk_create([
        BallotSelection(ballot=ballot, position_id=pid, candidate_id=cid)
        for pid, cid in mapping.items()
    ])
    updated = VoterParticipation.objects.filter(pk=participation.pk, has_voted=False).update(has_voted=True)
    if updated != 1:
        raise VoteConflict('Vote already recorded for this election.')
    return {'status': 'recorded', 'election_id': election.id, 'has_voted': True}
