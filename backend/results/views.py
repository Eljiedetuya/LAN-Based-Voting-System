from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from core.permissions import IsAdminOrMonitor
from elections.models import Election, Position, Candidate
from voting.models import Ballot, BallotSelection, VoterParticipation
from .integrity import election_integrity

class ElectionResults(APIView):
    permission_classes = [IsAdminOrMonitor]
    def get(self, request, pk):
        election = get_object_or_404(Election, pk=pk)
        if election.status != Election.Status.CLOSED:
            raise PermissionDenied('Results are available only after the election closes.')
        integrity = election_integrity(election)
        if not integrity['integrity_ok']:
            return Response({'error': {'code': 'reconciliation_failed',
                'detail': 'Election data did not pass integrity checks.'}}, status=409)
        ballots = integrity['anonymous_ballots']
        positions = list(Position.objects.filter(election=election))
        aggregated = dict(Candidate.objects.filter(position__election=election)
            .annotate(total=Count('ballotselection')).values_list('id', 'total'))
        output = []
        for position in positions:
            candidates = Candidate.objects.filter(position=position).order_by('id')
            output.append({'position_id': position.id, 'position': position.name,
                'candidates': [{'id': c.id, 'name': c.name, 'votes': aggregated.get(c.id, 0)} for c in candidates]})
        return Response({'election_id': election.id, 'status': election.status,
                         'accepted_ballots': ballots, 'positions': output})


import csv
from django.http import HttpResponse
from django.utils import timezone

class ElectionReportCSV(APIView):
    """CSV derived exclusively from verified closed-election aggregates."""
    permission_classes = [IsAdminOrMonitor]
    def get(self, request, pk):
        result = ElectionResults().get(request, pk)
        if result.status_code != 200:
            return result
        data = result.data
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="election-{pk}-results.csv"'
        response['Cache-Control'] = 'no-store'
        writer = csv.writer(response)
        writer.writerow(['Election ID', data['election_id']])
        writer.writerow(['Election Status', data['status']])
        writer.writerow(['Accepted Ballots', data['accepted_ballots']])
        writer.writerow(['Generated UTC', timezone.now().isoformat()])
        writer.writerow([])
        writer.writerow(['Position', 'Candidate', 'Votes'])
        for position in data['positions']:
            for candidate in position['candidates']:
                # Avoid spreadsheet formula injection from names or position text.
                def safe(value):
                    value = str(value)
                    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else value
                writer.writerow([safe(position['position']), safe(candidate['name']), candidate['votes']])
        return response
