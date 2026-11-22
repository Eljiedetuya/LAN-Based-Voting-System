from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Election, Position, Candidate
from voting.models import VoterParticipation
from audit.utils import record

def ensure_draft(election):
    if election.status != Election.Status.DRAFT:
        raise ValidationError({'election': 'Election configuration is locked.'})

@transaction.atomic
def open_election(election_id, actor):
    election = Election.objects.select_for_update().get(pk=election_id)
    ensure_draft(election)
    positions = list(Position.objects.filter(election=election))
    if not positions or any(not Candidate.objects.filter(position=p).exists() for p in positions):
        raise ValidationError({'election': 'Every election position needs a candidate.'})
    if not VoterParticipation.objects.filter(election=election).exists():
        raise ValidationError({'election': 'At least one eligible student is required.'})
    if VoterParticipation.objects.filter(election=election).exclude(user__role='STUDENT', user__is_active=True).exists():
        raise ValidationError({'election': 'Eligibility must contain only active student accounts.'})
    if Election.objects.filter(status=Election.Status.OPEN).exclude(pk=election.pk).exists():
        raise ValidationError({'election': 'Another election is already open.'})
    election.status = Election.Status.OPEN
    election.open_slot = 1
    election.opened_at = timezone.now()
    try:
        election.save(update_fields=['status', 'open_slot', 'opened_at'])
    except IntegrityError:
        raise ValidationError({'election': 'Another election is already open.'})
    record(actor, 'ELECTION_OPENED', 'ELECTION', election.id)
    return election

@transaction.atomic
def close_election(election_id, actor):
    election = Election.objects.select_for_update().get(pk=election_id)
    if election.status != Election.Status.OPEN:
        raise ValidationError({'election': 'Only open elections may be closed.'})
    election.status = Election.Status.CLOSED
    election.open_slot = None
    election.closed_at = timezone.now()
    election.save(update_fields=['status', 'open_slot', 'closed_at'])
    record(actor, 'ELECTION_CLOSED', 'ELECTION', election.id)
    return election
