"""Aggregate-only integrity checks: never return individual ballots or choices."""
from django.db.models import Count, F
from elections.models import Position
from voting.models import Ballot, BallotSelection, VoterParticipation


def election_integrity(election):
    """Detect ballot count, completeness and candidate association errors.

    Does not prove cryptographic anonymity or one-to-one ballot origin. This
    assumes election configuration is frozen after opening.
    """
    positions = list(Position.objects.filter(election=election).values_list('id', flat=True))
    expected = set(positions)
    ballots = Ballot.objects.filter(election=election).count()
    recorded = VoterParticipation.objects.filter(election=election, has_voted=True).count()
    issues = []
    if ballots != recorded:
        issues.append('participation_ballot_count_mismatch')
    if ballots and not positions:
        issues.append('no_configured_positions')
    choice_rows = BallotSelection.objects.filter(ballot__election=election)
    if choice_rows.count() != ballots * len(positions):
        issues.append('selection_count_mismatch')
    # Check each ballot independently; a total count alone misses a swapped position.
    counts = choice_rows.values('ballot_id').annotate(total=Count('id'))
    if any(item['total'] != len(positions) for item in counts.iterator()):
        issues.append('incomplete_ballot')
    if choice_rows.exclude(position__election=election).exists() or choice_rows.exclude(candidate__position_id=F('position_id')).exists():
        issues.append('invalid_choice_association')
    if choice_rows.exclude(candidate__position__election=election).exists():
        issues.append('cross_election_candidate')
    # Missing individual positions with a valid total (e.g. a repeated position)
    # are prevented by the unique (ballot, position) DB constraint.
    return {
        'election_id': election.pk, 'election_status': election.status,
        'eligible': VoterParticipation.objects.filter(election=election).count(),
        'recorded': recorded, 'anonymous_ballots': ballots,
        'configured_positions': len(expected),
        'integrity_ok': not issues, 'issue_codes': sorted(set(issues)),
    }
