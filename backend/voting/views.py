from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from core.permissions import IsStudent
from elections.models import Election
from .models import VoterParticipation
from .services import submit_ballot

class MyVotingStatus(APIView):
    permission_classes = [IsStudent]
    def get(self, request, pk):
        election = get_object_or_404(Election, pk=pk)
        row = VoterParticipation.objects.filter(election=election, user=request.user).first()
        return Response({'election_id': election.id, 'election_status': election.status,
            'eligible': row is not None, 'has_voted': row.has_voted if row else False})

class SubmitVote(APIView):
    permission_classes = [IsStudent]
    def post(self, request, pk):
        if not isinstance(request.data, dict) or set(request.data) != {'selections'}:
            raise ValidationError({'selections': 'Submit only the selections field.'})
        result = submit_ballot(election_id=pk, user=request.user,
                               selections=request.data['selections'])
        return Response(result, status=201)
