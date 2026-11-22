from django.db import connection
from django.db.models import Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsAdminOrMonitor
from elections.models import Election
from voting.models import VoterParticipation

class ParticipationSummary(APIView):
    permission_classes = [IsAdminOrMonitor]
    def get(self, request):
        election_id = request.query_params.get('election_id')
        if not election_id or not election_id.isdecimal():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'election_id': 'A valid election ID is required.'})
        election = get_object_or_404(Election, pk=election_id)
        counts = VoterParticipation.objects.filter(election=election).aggregate(
            eligible=Count('id'), recorded=Count('id', filter=Q(has_voted=True)))
        total = counts['eligible']
        recorded = counts['recorded']
        return Response({'election_id': election.id, 'election_status': election.status,
            'eligible': total, 'recorded': recorded, 'remaining': total-recorded,
            'turnout_percent': round(100*recorded/total, 2) if total else None,
            'updated_at': timezone.now().isoformat()})

class SystemHealth(APIView):
    permission_classes = [IsAdminOrMonitor]
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            database = 'healthy'
        except Exception:
            database = 'unavailable'
        return Response({'application': 'healthy', 'database': database,
                         'checked_at': timezone.now().isoformat()})


class MonitorElectionList(APIView):
    """Minimal election metadata for monitor pickers; no admin management data."""
    permission_classes = [IsAdminOrMonitor]
    def get(self, request):
        return Response(list(Election.objects.order_by('-id').values('id', 'title', 'status')))


from core.permissions import IsAdmin
from results.integrity import election_integrity

class ElectionIntegritySummary(APIView):
    """Admin-only aggregate check; no candidate tally or ballot identity."""
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        election = get_object_or_404(Election, pk=pk)
        return Response(election_integrity(election))
